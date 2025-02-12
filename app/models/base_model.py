# app/models/base_model.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

# Define a naming convention for database constraints
# This helps create consistent and predictable constraint names across your database
convention = {
    "ix": "ix_%(column_0_label)s",      # Index naming
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # Unique constraint naming
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check constraint naming
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # Foreign key naming
    "pk": "pk_%(table_name)s"  # Primary key naming
}

# Create metadata with the defined naming convention
# This ensures consistent naming across all database objects
metadata = MetaData(naming_convention=convention)

# Create the declarative base with the custom metadata
# This will be the base class for all SQLAlchemy models in the application
Base = declarative_base(metadata=metadata)

# Optional: Add a base method for serialization if needed
def to_dict(self):
    """
    Convert SQLAlchemy model instance to a dictionary.
    This method can be used as a base for serialization across models.
    """
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Attach the to_dict method to the Base class
Base.to_dict = to_dict