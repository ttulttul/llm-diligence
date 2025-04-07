import os
import inspect
import re
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship, backref
from typing import Dict, Type, Any, Optional, List, Set, Tuple
import json
from datetime import datetime, date
from pydantic import BaseModel

# Create the declarative base class
Base = declarative_base()

def create_engine(db_path: str):
    """Create a SQLAlchemy engine for the specified database."""
    # Create the database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    # Create the SQLAlchemy engine
    engine = sa.create_engine(f"sqlite:///{db_path}")
    return engine

def get_table_name(model_class):
    """Generate a table name from a model class."""
    # Convert CamelCase to snake_case
    name = model_class.__name__
    snake_case = ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
    return snake_case

# Entity definitions for normalization
class EntityDefinition:
    """Defines a common entity that should be normalized across tables."""
    def __init__(self, name, identifier_fields):
        self.name = name
        self.identifier_fields = identifier_fields
        self.table_name = f"{name.lower()}"
        self.sa_model = None
        self.references = {}  # Store references to this entity from other models

# Define common entities for normalization
COMMON_ENTITIES = [
    EntityDefinition("Customer", ["name", "customer_name", "client_name", "client"]),
    EntityDefinition("Employee", ["employee_name", "staff_name", "personnel_name"]),
    EntityDefinition("Company", ["company_name", "organization_name", "org_name", "corporate_name"]),
    EntityDefinition("Product", ["product_name", "item_name", "service_name"]),
]

def identify_entity_fields(pydantic_model: Type[BaseModel]) -> Dict[str, List[str]]:
    """
    Identify fields in a Pydantic model that should be normalized to common entities.
    
    Returns a dict mapping entity names to lists of field names.
    """
    entity_fields = {}
    
    for field_name, field_info in pydantic_model.model_fields.items():
        # Check if this field matches any common entity
        for entity in COMMON_ENTITIES:
            # Simple case: field name exactly matches one of the identifier fields
            if field_name in entity.identifier_fields:
                if entity.name not in entity_fields:
                    entity_fields[entity.name] = []
                entity_fields[entity.name].append(field_name)
                continue
                
            # Pattern-based case: field name contains one of the identifiers
            # For example "primary_customer_name" should match "customer_name"
            for identifier in entity.identifier_fields:
                if identifier in field_name:
                    if entity.name not in entity_fields:
                        entity_fields[entity.name] = []
                    entity_fields[entity.name].append(field_name)
                    break
    
    return entity_fields

def create_entity_models(base=Base):
    """Create SQLAlchemy models for common entities."""
    entity_models = {}
    
    for entity in COMMON_ENTITIES:
        columns = {
            "__tablename__": entity.table_name,
            "id": sa.Column(sa.Integer, primary_key=True),
            # All entities have a name column that stores the primary name
            "name": sa.Column(sa.String, unique=True, nullable=False),
            # Add created_at for tracking
            "created_at": sa.Column(sa.DateTime, default=datetime.utcnow),
        }
        
        # Create the SQLAlchemy model for this entity
        model_name = f"{entity.name}Table"
        entity.sa_model = type(model_name, (base,), columns)
        entity_models[entity.name] = entity.sa_model
    
    return entity_models

def create_sqlalchemy_model_from_pydantic(pydantic_model: Type[BaseModel], base=Base, entity_models=None):
    """Dynamically create a SQLAlchemy model from a Pydantic model with normalization."""
    model_name = f"{pydantic_model.__name__}Table"
    table_name = get_table_name(pydantic_model)
    
    # Define the columns
    columns = {
        "__tablename__": table_name,
        "id": sa.Column(sa.Integer, primary_key=True),
    }
    
    # Identify entity fields for normalization
    entity_fields = identify_entity_fields(pydantic_model)
    
    # Track relationships to add after model creation
    relationships = {}
    
    # Process the Pydantic model fields and convert to SQLAlchemy columns
    for field_name, field_info in pydantic_model.model_fields.items():
        # Check if this field should be normalized
        normalized = False
        
        for entity_name, fields in entity_fields.items():
            if field_name in fields and entity_models and entity_name in entity_models:
                # This field should be normalized - create a foreign key instead
                entity_model = entity_models[entity_name]
                fk_column_name = f"{field_name}_id"
                
                # Create foreign key column
                columns[fk_column_name] = sa.Column(
                    sa.Integer, 
                    sa.ForeignKey(f"{entity_model.__tablename__}.id"),
                    nullable=True
                )
                
                # Define relationship
                relationship_name = field_name.replace("_name", "").replace("name", "")
                if not relationship_name:
                    relationship_name = entity_name.lower()
                
                # Store relationship to be added after model creation
                relationships[relationship_name] = (entity_model.__tablename__, fk_column_name)
                
                # Record this reference in the entity for potential back-references
                if entity_name in COMMON_ENTITIES:
                    for entity in COMMON_ENTITIES:
                        if entity.name == entity_name:
                            if pydantic_model.__name__ not in entity.references:
                                entity.references[pydantic_model.__name__] = []
                            entity.references[pydantic_model.__name__].append(fk_column_name)
                
                normalized = True
                break
        
        if normalized:
            continue
            
        # Regular field processing for non-normalized fields
        column_name = field_name
        
        # Handle SQLAlchemy reserved keywords (like 'metadata')
        if column_name == 'metadata':
            attr_name = 'metadata_'
        else:
            attr_name = column_name
        
        # Choose column type based on the Python type
        python_type = field_info.annotation
        if python_type == str:
            column = sa.Column(column_name, sa.String)
        elif python_type == int:
            column = sa.Column(column_name, sa.Integer)
        elif python_type == float:
            column = sa.Column(column_name, sa.Float)
        elif python_type == bool:
            column = sa.Column(column_name, sa.Boolean)
        elif python_type == dict or "Dict" in str(python_type):
            column = sa.Column(column_name, sa.JSON)
        elif python_type == list or "List" in str(python_type):
            column = sa.Column(column_name, sa.JSON)
        else:
            # For other types, store as JSON
            column = sa.Column(column_name, sa.JSON)
        
        columns[attr_name] = column
    
    # Create the new SQLAlchemy model class
    model_class = type(model_name, (base,), columns)
    
    # Add relationships
    for rel_name, (target_table, fk_column) in relationships.items():
        setattr(model_class, rel_name, relationship(
            target_table.replace("_", "").capitalize() + "Table",
            foreign_keys=[getattr(model_class, fk_column)]
        ))
    
    return model_class

def create_tables(engine, pydantic_models):
    """Create tables for all specified Pydantic models."""
    # First create models for common entities
    entity_models = create_entity_models()
    
    # Create SQLAlchemy models from Pydantic models
    sa_models = {}
    for model_class in pydantic_models:
        sa_model = create_sqlalchemy_model_from_pydantic(model_class, entity_models=entity_models)
        sa_models[model_class.__name__] = sa_model
    
    # Add all entity models to the sa_models dict
    for entity_name, entity_model in entity_models.items():
        sa_models[entity_name] = entity_model
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    return sa_models

def serialize_for_db(obj):
    """Recursively convert datetime and date objects to ISO format strings."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_for_db(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_db(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(serialize_for_db(item) for item in obj)
    elif isinstance(obj, set):
        return {serialize_for_db(item) for item in obj}
    else:
        return obj

def get_or_create_entity(session, entity_model, entity_name):
    """Get an existing entity instance or create a new one."""
    instance = session.query(entity_model).filter_by(name=entity_name).first()
    if not instance:
        instance = entity_model(name=entity_name)
        session.add(instance)
        session.flush()  # This will assign an ID without committing the transaction
    return instance

def pydantic_to_sqlalchemy(pydantic_instance, sa_model_class, session: Session):
    """Convert a Pydantic model instance to a SQLAlchemy model instance and save it."""
    # Identify entity fields for potential normalization
    entity_fields = identify_entity_fields(type(pydantic_instance))
    
    # Create a dict with SQLAlchemy attribute names
    data = {}
    for field_name in pydantic_instance.model_fields:
        value = getattr(pydantic_instance, field_name)
        
        # Check if this field should be normalized
        normalized = False
        for entity_name, fields in entity_fields.items():
            if field_name in fields:
                # Find the corresponding entity model
                entity_model = None
                for model_name, model_class in session.registry._class_registry.items():
                    if model_name == f"{entity_name}Table":
                        entity_model = model_class
                        break
                
                if entity_model and value:
                    # Get or create the entity
                    entity_instance = get_or_create_entity(session, entity_model, value)
                    
                    # Set the foreign key value
                    fk_field = f"{field_name}_id"
                    data[fk_field] = entity_instance.id
                    normalized = True
                    break
        
        if normalized:
            continue
            
        # Handle SQLAlchemy reserved keywords
        if field_name == 'metadata':
            attr_name = 'metadata_'
        else:
            attr_name = field_name
        
        # Convert nested Pydantic models to dictionaries
        if isinstance(value, BaseModel):
            value = value.model_dump()
        elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
            value = [item.model_dump() for item in value]
        
        # Recursively serialize datetime objects
        value = serialize_for_db(value)
        
        data[attr_name] = value
    
    # Create and save the SQLAlchemy model instance
    sa_instance = sa_model_class(**data)
    session.add(sa_instance)
    session.commit()
    
    return sa_instance

def setup_database(db_path: str, model_classes: List[Type[BaseModel]]):
    """Set up the database with tables for all models."""
    engine = create_engine(db_path)
    sa_models = create_tables(engine, model_classes)
    Session = sessionmaker(bind=engine)
    
    return engine, Session, sa_models

# Custom JSON encoder that can handle datetime and date objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def save_model_to_db(model_instance: BaseModel, sa_models: Dict, session: Session):
    """Save a model instance to the database."""
    model_class_name = model_instance.__class__.__name__
    sa_model_class = sa_models.get(model_class_name)
    
    if not sa_model_class:
        raise ValueError(f"No SQLAlchemy model found for {model_class_name}")
    
    try:
        return pydantic_to_sqlalchemy(model_instance, sa_model_class, session)
    except TypeError as e:
        if "not JSON serializable" in str(e):
            # Fallback: Use JSON serialization with custom encoder as a last resort
            model_dict = json.loads(json.dumps(model_instance.model_dump(), cls=DateTimeEncoder))
            model_instance = type(model_instance).model_validate(model_dict)
            return pydantic_to_sqlalchemy(model_instance, sa_model_class, session)
        raise
