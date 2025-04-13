import os
import inspect
import re
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship, backref
from typing import Dict, Type, Any, Optional, List, Set, Tuple, Union
from enum import Enum
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
        # Convert CamelCase to snake_case for table name
        self.table_name = ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')
        self.sa_model = None
        self.references = {}  # Store references to this entity from other models

# Define common entities for normalization based on the models in the codebase
COMMON_ENTITIES = [
    EntityDefinition("DocumentClassification", ["model_name"]),
    EntityDefinition("Customer", ["name", "customer_name", "client_name", "client", "licensee", "counterparty"]),
    EntityDefinition("Employee", ["employee_name", "staff_name", "personnel_name", "employee"]),
    EntityDefinition("Company", ["company_name", "organization_name", "org_name", "corporate_name", "employer", "licensor", "company"]),
    EntityDefinition("Product", ["product_name", "item_name", "service_name", "product", "service_covered"]),
    EntityDefinition("Contract", ["contract_id", "agreement_id", "document_id"]),
    EntityDefinition("Jurisdiction", ["governing_law", "governing_law_jurisdiction", "jurisdiction"]),
    # New entities based on model analysis
    EntityDefinition("Vendor", ["vendor", "supplier", "provider", "service_provider"]),
    EntityDefinition("Location", ["location", "office_location", "address", "site", "locations"]),
    EntityDefinition("Department", ["department", "division", "business_unit", "team"]),
    EntityDefinition("Position", ["position", "job_title", "title", "role"]),
    EntityDefinition("Document", ["document", "file", "document_id", "file_path"]),
    EntityDefinition("PaymentTerm", ["payment_term", "payment_terms", "payment_frequency"]),
    EntityDefinition("Industry", ["industry", "sector", "business_sector", "market_segment"]),
    EntityDefinition("Currency", ["currency", "currency_code"]),
    EntityDefinition("BankAccount", ["bank_account", "account_number", "banking_details"]),
    EntityDefinition("TaxAuthority", ["tax_authority", "tax_jurisdiction", "taxing_entity"]),
]

def identify_entity_fields(pydantic_model: Type[BaseModel]) -> Dict[str, List[str]]:
    """
    Identify fields in a Pydantic model that should be normalized to common entities.
    
    Returns a dict mapping entity names to lists of field names.
    """
    entity_fields = {}
    
    # Check if model has fields attribute (some older Pydantic versions use __fields__)
    model_fields = getattr(pydantic_model, "model_fields", None)
    if model_fields is None:
        model_fields = getattr(pydantic_model, "__fields__", {})
    
    for field_name, field_info in model_fields.items():
        # Skip fields that are complex objects which shouldn't be normalized
        if hasattr(field_info, "annotation"):
            python_type = field_info.annotation
            # Skip list and dict fields, as they typically aren't direct entity references
            if "List" in str(python_type) or "Dict" in str(python_type):
                continue
            
            # Skip enum types
            if "Enum" in str(python_type) or isinstance(python_type, type) and issubclass(python_type, Enum):
                continue
                
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
                    # Avoid false positives - make sure it's truly related
                    # For example, "customer_name_label" shouldn't match if just "name" is an identifier
                    if len(identifier) > 4 or identifier == field_name or field_name.startswith(identifier + "_") or field_name.endswith("_" + identifier):
                        if entity.name not in entity_fields:
                            entity_fields[entity.name] = []
                        entity_fields[entity.name].append(field_name)
                        break
    
    return entity_fields

def create_entity_models(base=Base):
    """Create SQLAlchemy models for common entities with additional metadata."""
    entity_models = {}
    
    for entity in COMMON_ENTITIES:
        columns = {
            "__tablename__": entity.table_name,
            "id": sa.Column(sa.Integer, primary_key=True),
            # All entities have a name column that stores the primary name
            "name": sa.Column(sa.String, unique=True, nullable=False),
            # Add common metadata fields
            "created_at": sa.Column(sa.DateTime, default=datetime.utcnow),
            "updated_at": sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
            "description": sa.Column(sa.String, nullable=True),
            "metadata_": sa.Column(sa.JSON, nullable=True),  # Use metadata_ to avoid SQLAlchemy reserved keyword
        }
        
        # Add entity-specific columns based on the entity type
        if entity.name == "Customer":
            columns.update({
                "contact_email": sa.Column(sa.String, nullable=True),
                "contact_phone": sa.Column(sa.String, nullable=True),
                "is_active": sa.Column(sa.Boolean, default=True),
            })
        elif entity.name == "Employee":
            columns.update({
                "title": sa.Column(sa.String, nullable=True),
                "department": sa.Column(sa.String, nullable=True),
                "hire_date": sa.Column(sa.Date, nullable=True),
            })
        elif entity.name == "Company":
            columns.update({
                "website": sa.Column(sa.String, nullable=True),
                "industry": sa.Column(sa.String, nullable=True),
                "incorporated_date": sa.Column(sa.Date, nullable=True),
            })
        elif entity.name == "Product":
            columns.update({
                "version": sa.Column(sa.String, nullable=True),
                "product_type": sa.Column(sa.String, nullable=True),
                "is_active": sa.Column(sa.Boolean, default=True),
            })
        elif entity.name == "Contract":
            columns.update({
                "effective_date": sa.Column(sa.Date, nullable=True),
                "expiration_date": sa.Column(sa.Date, nullable=True),
                "contract_type": sa.Column(sa.String, nullable=True),
            })
        elif entity.name == "Jurisdiction":
            columns.update({
                "country": sa.Column(sa.String, nullable=True),
                "region": sa.Column(sa.String, nullable=True),  # State/Province
                "is_international": sa.Column(sa.Boolean, nullable=True),
            })
        
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
        "created_at": sa.Column(sa.DateTime, default=datetime.utcnow),
        "updated_at": sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    }
    
    # Identify entity fields for normalization
    entity_fields = identify_entity_fields(pydantic_model)
    
    # Track relationships to add after model creation
    relationships = {}
    
    # Check if model has fields attribute (some older Pydantic versions use __fields__)
    model_fields = getattr(pydantic_model, "model_fields", None)
    if model_fields is None:
        model_fields = getattr(pydantic_model, "__fields__", {})
    
    # Process the Pydantic model fields and convert to SQLAlchemy columns
    for field_name, field_info in model_fields.items():
        # Skip the 'analyzed_at' field from the DiligentizerModel base class since we have created_at
        if field_name == 'analyzed_at':
            continue
            
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
                if entity_name in [e.name for e in COMMON_ENTITIES]:
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
        
        # Get field type
        if hasattr(field_info, "annotation"):
            python_type = field_info.annotation
        else:
            python_type = field_info.type_
        
        # Handle nested Pydantic models (from the specific models we've seen)
        if hasattr(python_type, "__origin__") and python_type.__origin__ is list:
            # For List[BaseModel] types 
            if hasattr(python_type, "__args__") and len(python_type.__args__) > 0:
                arg_type = python_type.__args__[0]
                if isinstance(arg_type, type) and issubclass(arg_type, BaseModel):
                    column = sa.Column(column_name, sa.JSON)
                else:
                    column = sa.Column(column_name, sa.JSON)
            else:
                column = sa.Column(column_name, sa.JSON)
        
        # Handle enums (which are common in the models we've seen)
        elif isinstance(python_type, type) and issubclass(python_type, Enum):
            # Store enum as string
            column = sa.Column(column_name, sa.String)
        
        # Handle optional types
        elif hasattr(python_type, "__origin__") and python_type.__origin__ is Union:
            # For Optional[X] which is Union[X, None]
            if hasattr(python_type, "__args__") and type(None) in python_type.__args__:
                # Get the non-None type
                non_none_types = [t for t in python_type.__args__ if t is not type(None)]
                if non_none_types:
                    actual_type = non_none_types[0]
                    # Recurse to handle the actual type, but make nullable
                    if actual_type == str:
                        column = sa.Column(column_name, sa.String, nullable=True)
                    elif actual_type == int:
                        column = sa.Column(column_name, sa.Integer, nullable=True)
                    elif actual_type == float:
                        column = sa.Column(column_name, sa.Float, nullable=True)
                    elif actual_type == bool:
                        column = sa.Column(column_name, sa.Boolean, nullable=True)
                    elif actual_type == dict or "Dict" in str(actual_type):
                        column = sa.Column(column_name, sa.JSON, nullable=True)
                    elif actual_type == list or "List" in str(actual_type):
                        column = sa.Column(column_name, sa.JSON, nullable=True)
                    elif actual_type == date or actual_type == datetime:
                        column = sa.Column(column_name, sa.DateTime, nullable=True)
                    elif isinstance(actual_type, type) and issubclass(actual_type, Enum):
                        column = sa.Column(column_name, sa.String, nullable=True)
                    elif isinstance(actual_type, type) and issubclass(actual_type, BaseModel):
                        column = sa.Column(column_name, sa.JSON, nullable=True)
                    else:
                        column = sa.Column(column_name, sa.JSON, nullable=True)
                else:
                    column = sa.Column(column_name, sa.JSON, nullable=True)
            else:
                # Regular union type
                column = sa.Column(column_name, sa.JSON)
        
        # Handle date and datetime types which are common in the models
        elif python_type == date:
            column = sa.Column(column_name, sa.Date)
        elif python_type == datetime:
            column = sa.Column(column_name, sa.DateTime)
        
        # Handle nested Pydantic models
        elif isinstance(python_type, type) and issubclass(python_type, BaseModel):
            column = sa.Column(column_name, sa.JSON)
        
        # Regular primitive types
        elif python_type == str:
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
        # Find the entity model by table name
        entity_model_name = None
        for entity in COMMON_ENTITIES:
            if entity.table_name == target_table:
                entity_model_name = f"{entity.name}Table"
                break
        
        # If not found, fall back to the old method
        if not entity_model_name:
            class_name_parts = target_table.split('_')
            entity_model_name = ''.join(part.capitalize() for part in class_name_parts) + 'Table'
        
        # Handle more complex relationship names (deal with potential conflicts)
        if rel_name == '':
            rel_name = target_table
            
        # Remove any trailing underscores
        rel_name = rel_name.rstrip('_')
        
        # Create the relationship with a more specific backref name to avoid conflicts
        # Include both table name and relationship name for uniqueness
        setattr(model_class, rel_name, relationship(
            entity_model_name,
            foreign_keys=[getattr(model_class, fk_column)],
            backref=backref(
                f"{table_name}_{rel_name}_collection", 
                lazy='dynamic',
                cascade="all, delete-orphan"
            )
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

def get_or_create_entity(session, entity_model, entity_name, extra_fields=None, update_existing=True):
    """
    Get an existing entity instance or create a new one.
    
    Args:
        session: SQLAlchemy session
        entity_model: The entity model class
        entity_name: The name of the entity
        extra_fields: Optional dict of additional fields to set on newly created entities
        update_existing: Whether to update existing entities with extra_fields
        
    Returns:
        Entity instance
    """
    if not entity_name:
        return None
        
    # Strip whitespace and check if empty
    if isinstance(entity_name, str):
        entity_name = entity_name.strip()
        if not entity_name:
            return None
    
    # Query for existing entity
    instance = session.query(entity_model).filter_by(name=entity_name).first()
    
    if instance:
        # Update existing entity with any new information if requested
        if update_existing and extra_fields:
            updated = False
            for key, value in extra_fields.items():
                if value is not None and hasattr(instance, key):
                    current_value = getattr(instance, key)
                    # Only update if the field is currently None or empty
                    if current_value is None or (isinstance(current_value, str) and not current_value.strip()):
                        setattr(instance, key, value)
                        updated = True
            
            if updated:
                session.flush()  # Update without committing the transaction
    else:
        # Create a new entity with the provided name
        fields = {'name': entity_name}
        
        # Add any extra fields provided
        if extra_fields:
            fields.update({k: v for k, v in extra_fields.items() if v is not None})
            
        instance = entity_model(**fields)
        session.add(instance)
        session.flush()  # This will assign an ID without committing the transaction
        
        # Log the creation to help with debugging
        print(f"Created new entity: {entity_model.__name__} - {entity_name}")
    
    # Ensure the entity has a valid ID
    if not instance.id:
        session.flush()
        
    return instance

def extract_entity_data(pydantic_instance, entity_name, field_name, value):
    """
    Extract relevant data for an entity from a pydantic model.
    
    Args:
        pydantic_instance: The pydantic model instance
        entity_name: The name of the entity (e.g., 'Company', 'Customer')
        field_name: The name of the field referencing the entity
        value: The current field value
        
    Returns:
        Dict of extra fields to set on the entity
    """
    extra_fields = {}
    full_model_data = pydantic_instance.model_dump() if hasattr(pydantic_instance, "model_dump") else pydantic_instance.dict()
    
    # First extract data from metadata if available
    if hasattr(pydantic_instance, "metadata") and getattr(pydantic_instance, "metadata", None):
        metadata = pydantic_instance.metadata
        if isinstance(metadata, dict):
            # Common metadata fields for different entity types
            if entity_name == "Company":
                extra_fields.update({
                    "website": metadata.get("company_website") or metadata.get("website"),
                    "industry": metadata.get("industry") or metadata.get("sector"),
                    "description": metadata.get("company_description") or metadata.get("description"),
                })
            elif entity_name == "Customer":
                extra_fields.update({
                    "contact_email": metadata.get("customer_email") or metadata.get("contact_email"),
                    "contact_phone": metadata.get("customer_phone") or metadata.get("contact_phone"),
                    "description": metadata.get("customer_description") or metadata.get("description"),
                })
            elif entity_name == "Product":
                extra_fields.update({
                    "version": metadata.get("product_version") or metadata.get("version"),
                    "product_type": metadata.get("product_type") or metadata.get("type"),
                    "description": metadata.get("product_description") or metadata.get("description"),
                })
    
    # Look for entity-specific fields in the model data
    # Naming patterns commonly used for entity properties
    if entity_name == "Company":
        # Look for company-related fields
        website_keys = [f"{field_name}_website", "company_website", "website", "url"]
        for key in website_keys:
            if key in full_model_data and full_model_data[key]:
                extra_fields["website"] = full_model_data[key]
                break
                
        industry_keys = [f"{field_name}_industry", "company_industry", "industry", "sector", "field"]
        for key in industry_keys:
            if key in full_model_data and full_model_data[key]:
                extra_fields["industry"] = full_model_data[key]
                break
    
    elif entity_name == "Customer":
        # Look for customer-related fields
        email_keys = [f"{field_name}_email", "customer_email", "client_email", "contact_email", "email"]
        for key in email_keys:
            if key in full_model_data and full_model_data[key]:
                extra_fields["contact_email"] = full_model_data[key]
                break
                
        phone_keys = [f"{field_name}_phone", "customer_phone", "client_phone", "contact_phone", "phone"]
        for key in phone_keys:
            if key in full_model_data and full_model_data[key]:
                extra_fields["contact_phone"] = full_model_data[key]
                break
    
    elif entity_name == "Contract":
        # Look for contract-related fields
        date_keys = ["effective_date", "start_date", "execution_date", "agreement_date"]
        for key in date_keys:
            if key in full_model_data and full_model_data[key]:
                extra_fields["effective_date"] = full_model_data[key]
                break
                
        exp_date_keys = ["expiration_date", "end_date", "termination_date"]
        for key in exp_date_keys:
            if key in full_model_data and full_model_data[key]:
                extra_fields["expiration_date"] = full_model_data[key]
                break
                
        type_keys = ["contract_type", "agreement_type", "document_type"]
        for key in type_keys:
            if key in full_model_data and full_model_data[key]:
                extra_fields["contract_type"] = full_model_data[key]
                break
    
    # Extract description if available
    if "description" in full_model_data and full_model_data["description"] and "description" not in extra_fields:
        extra_fields["description"] = full_model_data["description"]
        
    return extra_fields

def pydantic_to_sqlalchemy(pydantic_instance, sa_model_class, session: Session, sa_models=None):
    """
    Convert a Pydantic model instance to a SQLAlchemy model instance and save it.
    Handles nested models, entity normalization, and complex types.
    
    Args:
        pydantic_instance: Pydantic model instance to convert
        sa_model_class: SQLAlchemy model class to convert to
        session: SQLAlchemy session
        sa_models: Dictionary of all SQLAlchemy model classes
    """
    # Identify entity fields for potential normalization
    entity_fields = identify_entity_fields(type(pydantic_instance))
    
    # Create a dict with SQLAlchemy attribute names
    data = {}
    
    # Track entities created/updated during this operation to ensure they're committed
    created_entities = []
    
    # Get model fields based on Pydantic version
    model_fields = getattr(pydantic_instance.__class__, "model_fields", None)
    if model_fields is None:
        model_fields = getattr(pydantic_instance.__class__, "__fields__", {})
    
    for field_name in model_fields:
        # Skip analyzed_at as we use created_at and updated_at
        if field_name == 'analyzed_at':
            continue
            
        value = getattr(pydantic_instance, field_name)
        
        # Skip None values for optional fields
        if value is None:
            continue
            
        # Check if this field should be normalized
        normalized = False
        for entity_name, fields in entity_fields.items():
            if field_name in fields:
                # Find the corresponding entity model from sa_models
                entity_model = None
                if sa_models:
                    entity_model = sa_models.get(entity_name)
                
                if entity_model and value:
                    # Don't try to normalize boolean values or numbers
                    if isinstance(value, (bool, int, float)):
                        break
                    
                    # Extract all relevant entity data
                    extra_fields = extract_entity_data(pydantic_instance, entity_name, field_name, value)
                    
                    # Get or create the entity with the extracted data
                    entity_instance = get_or_create_entity(session, entity_model, value, extra_fields, update_existing=True)
                    
                    if entity_instance:
                        # Set the foreign key value
                        fk_field = f"{field_name}_id"
                        data[fk_field] = entity_instance.id
                        # Add to list of entities to ensure they're committed
                        created_entities.append(entity_instance)
                        normalized = True
                    break
        
        if normalized:
            continue
            
        # Handle SQLAlchemy reserved keywords
        if field_name == 'metadata':
            attr_name = 'metadata_'
        else:
            attr_name = field_name
        
        # Handle different value types
        if isinstance(value, Enum):
            # For enum values, store the string value
            value = value.value
        elif isinstance(value, BaseModel):
            # Convert nested Pydantic models to dictionaries
            value = value.model_dump() if hasattr(value, "model_dump") else value.dict()
        elif isinstance(value, list):
            # Handle lists of Pydantic models
            if value and isinstance(value[0], BaseModel):
                value = [
                    (item.model_dump() if hasattr(item, "model_dump") else item.dict())
                    for item in value
                ]
        elif isinstance(value, dict):
            # For dictionaries, check each value for Pydantic models
            for k, v in list(value.items()):
                if isinstance(v, BaseModel):
                    value[k] = v.model_dump() if hasattr(v, "model_dump") else v.dict()
                elif isinstance(v, Enum):
                    value[k] = v.value
        
        # Recursively serialize datetime objects
        value = serialize_for_db(value)
        
        data[attr_name] = value
    
    try:
        # Create the SQLAlchemy model instance
        sa_instance = sa_model_class(**data)
        session.add(sa_instance)
        
        # Make sure all created entities are in the session
        for entity in created_entities:
            if entity not in session:
                session.add(entity)
        
        # Flush but don't commit yet - let the caller commit
        session.flush()
        return sa_instance
    except Exception as e:
        session.rollback()
        # If there was an error related to relationships, try to debug it
        if "'bool' object has no attribute '_sa_instance_state'" in str(e):
            # Create a new dict excluding boolean values that might be confused as relationship objects
            fixed_data = {k: v for k, v in data.items() if not isinstance(v, bool)}
            
            # Try again with fixed data
            sa_instance = sa_model_class(**fixed_data)
            session.add(sa_instance)
            
            # Make sure all created entities are in the session
            for entity in created_entities:
                if entity not in session:
                    session.add(entity)
                    
            session.flush()
            return sa_instance
        else:
            # Re-raise the original exception if it's not the specific one we're handling
            raise

def setup_database(db_path: str, model_classes: List[Type[BaseModel]]):
    """Set up the database with tables for all models."""
    engine = create_engine(db_path)
    sa_models = create_tables(engine, model_classes)
    Session = sessionmaker(bind=engine)
    
    return engine, Session, sa_models

from models import ModelEncoder

def save_model_to_db(model_instance: BaseModel, sa_models: Dict, session: Session):
    """Save a model instance to the database."""
    model_class_name = model_instance.__class__.__name__
    sa_model_class = sa_models.get(model_class_name)
    
    if not sa_model_class:
        raise ValueError(f"No SQLAlchemy model found for {model_class_name}")
    
    try:
        # Begin a transaction
        session.begin_nested()
        
        result = pydantic_to_sqlalchemy(model_instance, sa_model_class, session, sa_models)
        
        # Ensure changes are committed
        session.commit()
        return result
    except TypeError as e:
        session.rollback()
        if "not JSON serializable" in str(e):
            # Fallback: Use JSON serialization with custom encoder as a last resort
            session.begin_nested()
            model_dict = json.loads(json.dumps(model_instance.model_dump(), cls=ModelEncoder))
            model_instance = type(model_instance).model_validate(model_dict)
            result = pydantic_to_sqlalchemy(model_instance, sa_model_class, session, sa_models)
            session.commit()
            return result
        raise
    except Exception as e:
        session.rollback()
        raise
