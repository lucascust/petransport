"""
Helper module for converting between MongoDB documents and Pydantic models.
This provides convenience functions to convert between BSON documents and our Pydantic models.
"""

from typing import Dict, List, Any, Optional, Union, Type, TypeVar
from bson import ObjectId
import models
from models import (
    User,
    Pet,
    Travel,
    Document,
    Address,
    Event,
    EntityType,
    EventType,
    DocumentType,
    TravelStatus,
    FileType,
)
from datetime import datetime, timezone, timedelta

T = TypeVar("T", User, Pet, Travel, Document, Address, Event)


def doc_to_model(document: Dict[str, Any], model_class: Type[T]) -> T:
    """
    Convert a MongoDB document to a Pydantic model.

    Args:
        document: MongoDB document dictionary
        model_class: The Pydantic model class

    Returns:
        An instance of the specified model class
    """
    if not document:
        return None

    # MongoDB returns _id, but Pydantic models use id
    if "_id" in document and "id" not in document:
        document["id"] = document.pop("_id")

    return model_class(**document)


def model_to_doc(model: T) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a MongoDB document.

    Args:
        model: Pydantic model instance

    Returns:
        Dictionary ready for MongoDB insertion
    """
    # Get dict representation with alias support (for _id)
    doc = model.model_dump(by_alias=True)

    # Remove None values
    return {k: v for k, v in doc.items() if v is not None}


def user_from_doc(document: Dict[str, Any]) -> User:
    """Convert a user document to a User model."""
    return doc_to_model(document, User)


def pet_from_doc(document: Dict[str, Any]) -> Pet:
    """Convert a pet document to a Pet model."""
    return doc_to_model(document, Pet)


def travel_from_doc(document: Dict[str, Any]) -> Travel:
    """Convert a travel document to a Travel model."""
    return doc_to_model(document, Travel)


def document_from_doc(document: Dict[str, Any]) -> Document:
    """Convert a file document to a Document model."""
    return doc_to_model(document, Document)


def address_from_doc(document: Dict[str, Any]) -> Address:
    """Convert an address document to an Address model."""
    return doc_to_model(document, Address)


def event_from_doc(document: Dict[str, Any]) -> Event:
    """Convert an event document to an Event model."""
    return doc_to_model(document, Event)


def handle_object_id(obj_id: Union[str, ObjectId]) -> ObjectId:
    """Convert a string ID to ObjectId if needed."""
    if isinstance(obj_id, str):
        return ObjectId(obj_id)
    return obj_id
