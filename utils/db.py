import os
import inspect
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict, Type, Any, Optional, List
import json
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

def create_sqlalchemy_model_from_pydantic(pydantic_model: Type[BaseModel], base=Base):
    """Dynamically create a SQLAlchemy model from a Pydantic model."""
    model_name = f"{pydantic_model.__name__}Table"
    table_name = get_table_name(pydantic_model)
    
    # Define the columns
    columns = {
        "__tablename__": table_name,
        "id": sa.Column(sa.Integer, primary_key=True),
    }
    
    # Process the Pydantic model fields and convert to SQLAlchemy columns
    for field_name, field_info in pydantic_model.model_fields.items():
        # Skip complex nested models for now, store as JSON
        column_name = field_name
        
        # Handle SQLAlchemy reserved keywords (like 'metadata')
        if column_name == 'metadata':
            attr_name = 'metadata_'
        else:
            attr_name = column_name
        
        # Choose column type based on the Python type
        # This is a simplification - more complex mappings would be needed for a production system
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
    
    # Create and return the new SQLAlchemy model class
    return type(model_name, (base,), columns)

def create_tables(engine, pydantic_models):
    """Create tables for all specified Pydantic models."""
    # Create SQLAlchemy models from Pydantic models
    sa_models = {}
    for model_class in pydantic_models:
        sa_model = create_sqlalchemy_model_from_pydantic(model_class)
        sa_models[model_class.__name__] = sa_model
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    return sa_models

def pydantic_to_sqlalchemy(pydantic_instance, sa_model_class, session: Session):
    """Convert a Pydantic model instance to a SQLAlchemy model instance and save it."""
    # Create a dict with SQLAlchemy attribute names
    data = {}
    for field_name in pydantic_instance.model_fields:
        value = getattr(pydantic_instance, field_name)
        
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

def save_model_to_db(model_instance: BaseModel, sa_models: Dict, session: Session):
    """Save a model instance to the database."""
    model_class_name = model_instance.__class__.__name__
    sa_model_class = sa_models.get(model_class_name)
    
    if not sa_model_class:
        raise ValueError(f"No SQLAlchemy model found for {model_class_name}")
    
    return pydantic_to_sqlalchemy(model_instance, sa_model_class, session)
