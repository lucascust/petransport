"""
Database operations module for the petransport application.
Handles CRUD operations for all collections using the new data model.
"""

import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Union
from bson import ObjectId
from pymongo import MongoClient
import models
from models import (
    User,
    Pet,
    Travel,
    Document,
    Address,
    EntityType,
    DocumentType,
    TravelStatus,
    FileType,
)


# MongoDB Setup
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client["petransport"]


class DBOperations:
    """Base class for database operations."""

    def __init__(self, collection_name):
        self.collection = db[collection_name]

    def insert_one(self, model):
        """Insert a document into the collection."""
        doc_dict = model.model_dump(by_alias=True)
        result = self.collection.insert_one(doc_dict)
        return result.inserted_id

    def find_one(self, filter_dict):
        """Find a single document in the collection."""
        return self.collection.find_one(filter_dict)

    def find(self, filter_dict=None, sort=None, limit=None):
        """Find multiple documents in the collection."""
        cursor = self.collection.find(filter_dict or {})
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def update_one(self, filter_dict, update_dict):
        """Update a single document in the collection."""
        result = self.collection.update_one(filter_dict, update_dict)
        return result.modified_count

    def delete_one(self, filter_dict):
        """Delete a single document from the collection."""
        result = self.collection.delete_one(filter_dict)
        return result.deleted_count

    def count(self, filter_dict=None):
        """Count documents in the collection."""
        return self.collection.count_documents(filter_dict or {})


class UsersDB(DBOperations):
    """Operations for the users collection."""

    def __init__(self):
        super().__init__("users")

    def create_user(self, user: User) -> ObjectId:
        """Create a new user."""
        user_id = self.insert_one(user)
        return user_id

    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Get a user by username."""
        return self.find_one({"username": username})

    def get_user_by_id(self, user_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Get a user by ID."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return self.find_one({"_id": user_id})

    def update_user(
        self, user_id: Union[str, ObjectId], update_data: Dict[str, Any]
    ) -> int:
        """Update a user."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        # Set updated_at timestamp
        update_data["updated_at"] = datetime.now()

        return self.update_one({"_id": user_id}, {"$set": update_data})

    def add_pet_to_user(self, user_id: Union[str, ObjectId], pet_id: ObjectId) -> int:
        """Add a pet to a user's pets list."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        return self.update_one(
            {"_id": user_id},
            {"$push": {"pet_ids": pet_id}, "$set": {"updated_at": datetime.now()}},
        )

    def update_user_last_access(self, user_id: Union[str, ObjectId]) -> int:
        """Update the last access time for a user."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        return self.update_one(
            {"_id": user_id}, {"$set": {"last_access": datetime.now()}}
        )

    def list_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all users with basic info for admin display."""
        pipeline = [
            {
                "$lookup": {
                    "from": "travels",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "travels",
                }
            },
            {
                "$project": {
                    "owner_name": 1,
                    "username": 1,
                    "email": 1,
                    "created_at": 1,
                    "last_access": 1,
                    "pet_ids": 1,  # Return pet_ids instead of full pet objects
                    "travels_count": {"$size": "$travels"},
                }
            },
            {"$sort": {"created_at": -1}},
            {"$limit": limit},
        ]

        return list(self.collection.aggregate(pipeline))


class PetsDB(DBOperations):
    """Operations for the pets collection."""

    def __init__(self):
        super().__init__("pets")

    def create_pet(self, pet: Pet) -> ObjectId:
        """Create a new pet."""
        pet_id = self.insert_one(pet)

        # Add pet to user's pet list
        users_db = UsersDB()
        users_db.add_pet_to_user(pet.owner_id, pet_id)

        return pet_id

    def get_pet_by_id(self, pet_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Get a pet by ID."""
        if isinstance(pet_id, str):
            pet_id = ObjectId(pet_id)
        return self.find_one({"_id": pet_id})

    def get_pets_by_owner(self, owner_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        """Get all pets for a specific owner."""
        if isinstance(owner_id, str):
            owner_id = ObjectId(owner_id)
        return self.find({"owner_id": owner_id})

    def update_pet(
        self, pet_id: Union[str, ObjectId], update_data: Dict[str, Any]
    ) -> int:
        """Update a pet."""
        if isinstance(pet_id, str):
            pet_id = ObjectId(pet_id)

        # Set updated_at timestamp
        update_data["updated_at"] = datetime.now()

        return self.update_one({"_id": pet_id}, {"$set": update_data})

    def add_document_to_pet(
        self, pet_id: Union[str, ObjectId], doc_type: str, doc_id: ObjectId
    ) -> int:
        """Add a document to a pet."""
        if isinstance(pet_id, str):
            pet_id = ObjectId(pet_id)

        return self.update_one(
            {"_id": pet_id},
            {
                "$set": {
                    f"document_ids.{doc_type}": doc_id,
                    "updated_at": datetime.now(),
                }
            },
        )

    def get_pet_with_documents(self, pet_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Get a pet with its documents."""
        if isinstance(pet_id, str):
            pet_id = ObjectId(pet_id)

        pipeline = [
            {"$match": {"_id": pet_id}},
            {
                "$lookup": {
                    "from": "documents",
                    "let": {"pet_id": "$_id", "doc_ids": "$document_ids"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$entity_type", "pet"]},
                                        {"$eq": ["$entity_id", "$$pet_id"]},
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "documents",
                }
            },
        ]

        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None


class TravelsDB(DBOperations):
    """Operations for the travels collection."""

    def __init__(self):
        super().__init__("travels")

    def create_travel(self, travel: Travel) -> ObjectId:
        """Create a new travel."""
        travel_id = self.insert_one(travel)
        return travel_id

    def get_travel_by_id(self, travel_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Get a travel by ID."""
        if isinstance(travel_id, str):
            travel_id = ObjectId(travel_id)
        return self.find_one({"_id": travel_id})

    def get_travels_by_user(
        self, user_id: Union[str, ObjectId]
    ) -> List[Dict[str, Any]]:
        """Get all travels for a specific user."""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return self.find({"user_id": user_id}, sort=[("created_at", -1)])

    def get_travels_by_owner(
        self, user_id: Union[str, ObjectId]
    ) -> List[Dict[str, Any]]:
        """Get all travels for a specific user by owner id."""
        if isinstance(user_id, str):
            user_id_obj = ObjectId(user_id)
        else:
            user_id_obj = user_id

        # Buscar tanto pelo ObjectId quanto pela versão string do ID para compatibilidade
        user_id_str = str(user_id_obj)

        # Combinar resultados de ambas as consultas
        travels = self.find(
            {"$or": [{"user_id": user_id_obj}, {"user_id": user_id_str}]},
            sort=[("created_at", -1)],
        )

        # Debug para verificar se a viagem específica foi encontrada
        travel_id_str = "67fb7c9618768dd784992340"
        try:
            travel = self.get_travel_by_id(travel_id_str)
            if travel:
                travel_user_id = travel.get("user_id")
                print(
                    f"DEBUG: Viagem específica {travel_id_str} - user_id: {travel_user_id} (tipo: {type(travel_user_id)})"
                )
                print(
                    f"DEBUG: Comparando com user_id_obj: {user_id_obj} e user_id_str: {user_id_str}"
                )
        except Exception as e:
            print(f"DEBUG ERROR in get_travels_by_owner: {str(e)}")

        return travels

    def update_travel(
        self, travel_id: Union[str, ObjectId], update_data: Dict[str, Any]
    ) -> int:
        """Update a travel."""
        if isinstance(travel_id, str):
            travel_id = ObjectId(travel_id)

        # Set updated_at timestamp
        update_data["updated_at"] = datetime.now()

        result = self.update_one({"_id": travel_id}, {"$set": update_data})
        return result

    def update_travel_status(
        self, travel_id: Union[str, ObjectId], status: TravelStatus
    ) -> int:
        """Update the status of a travel."""
        if isinstance(travel_id, str):
            travel_id = ObjectId(travel_id)

        result = self.update_one(
            {"_id": travel_id},
            {"$set": {"status": status.value, "updated_at": datetime.now()}},
        )
        return result

    def add_document_to_travel(
        self, travel_id: Union[str, ObjectId], doc_type: str, doc_id: ObjectId
    ) -> int:
        """Add a document to a travel."""
        if isinstance(travel_id, str):
            travel_id = ObjectId(travel_id)

        return self.update_one(
            {"_id": travel_id},
            {
                "$set": {
                    f"document_ids.{doc_type}": doc_id,
                    "updated_at": datetime.now(),
                }
            },
        )

    def get_travel_with_details(
        self, travel_id: Union[str, ObjectId]
    ) -> Dict[str, Any]:
        """Get a travel with full details (pets, documents, address, etc)."""
        if isinstance(travel_id, str):
            travel_id = ObjectId(travel_id)

        pipeline = [
            {"$match": {"_id": travel_id}},
            # Lookup pets
            {
                "$lookup": {
                    "from": "pets",
                    "localField": "pet_ids",
                    "foreignField": "_id",
                    "as": "pets",
                }
            },
            # Lookup destination address
            {
                "$lookup": {
                    "from": "addresses",
                    "let": {"addr_id": "$destination_address_id"},
                    "pipeline": [{"$match": {"$expr": {"$eq": ["$_id", "$$addr_id"]}}}],
                    "as": "destination_address",
                }
            },
            # Lookup travel documents
            {
                "$lookup": {
                    "from": "documents",
                    "let": {"travel_id": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$entity_type", "travel"]},
                                        {"$eq": ["$entity_id", "$$travel_id"]},
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "documents",
                }
            },
            # Unwind destination_address array to single object or null
            {
                "$addFields": {
                    "destination_address": {"$arrayElemAt": ["$destination_address", 0]}
                }
            },
        ]

        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else None

    def add_pet_to_travel(
        self, travel_id: Union[str, ObjectId], pet_id: Union[str, ObjectId]
    ) -> int:
        """Add a pet to a travel."""
        if isinstance(travel_id, str):
            travel_id = ObjectId(travel_id)
        if isinstance(pet_id, str):
            pet_id = ObjectId(pet_id)

        return self.update_one(
            {"_id": travel_id},
            {"$push": {"pet_ids": pet_id}, "$set": {"updated_at": datetime.now()}},
        )

    def get_pets_in_travel(
        self, travel_id: Union[str, ObjectId]
    ) -> List[Dict[str, Any]]:
        """Get all pets in a travel."""
        if isinstance(travel_id, str):
            travel_id = ObjectId(travel_id)

        travel = self.get_travel_by_id(travel_id)
        if not travel or "pet_ids" not in travel:
            return []

        # Fetch each pet from the pets collection
        pets_db = PetsDB()
        pets = []
        for pet_id in travel["pet_ids"]:
            pet = pets_db.get_pet_by_id(pet_id)
            if pet:
                # Get photo if exists
                if "photo_id" in pet and pet["photo_id"]:
                    docs_db = DocumentsDB()
                    photo_doc = docs_db.get_document_by_id(pet["photo_id"])
                    if photo_doc:
                        pet["photo"] = {"path": photo_doc["path"]}
                pets.append(pet)

        return pets


class DocumentsDB(DBOperations):
    """Operations for the documents collection."""

    def __init__(self):
        super().__init__("documents")

    def create_document(self, document: Document) -> ObjectId:
        """Create a new document."""
        document_id = self.insert_one(document)

        # Add document reference to the appropriate entity
        if document.entity_type == EntityType.PET:
            pets_db = PetsDB()
            pets_db.add_document_to_pet(
                document.entity_id, document.document_type.value, document_id
            )
        elif document.entity_type == EntityType.TRAVEL:
            travels_db = TravelsDB()
            travels_db.add_document_to_travel(
                document.entity_id, document.document_type.value, document_id
            )

        return document_id

    def get_document_by_id(self, document_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Get a document by ID."""
        if isinstance(document_id, str):
            document_id = ObjectId(document_id)
        return self.find_one({"_id": document_id})

    def get_entity_documents(
        self, entity_type: EntityType, entity_id: Union[str, ObjectId]
    ) -> List[Dict[str, Any]]:
        """Get all documents for a specific entity."""
        if isinstance(entity_id, str):
            entity_id = ObjectId(entity_id)
        return self.find({"entity_type": entity_type.value, "entity_id": entity_id})

    def delete_document(self, document_id: Union[str, ObjectId]) -> int:
        """Delete a document."""
        if isinstance(document_id, str):
            document_id = ObjectId(document_id)

        # Get document details before deletion
        document = self.get_document_by_id(document_id)
        if not document:
            return 0

        # Remove document reference from entity
        if document["entity_type"] == EntityType.PET.value:
            pets_db = PetsDB()
            pets_db.update_one(
                {"_id": document["entity_id"]},
                {"$unset": {f"document_ids.{document['document_type']}": ""}},
            )
        elif document["entity_type"] == EntityType.TRAVEL.value:
            travels_db = TravelsDB()
            travels_db.update_one(
                {"_id": document["entity_id"]},
                {"$unset": {f"document_ids.{document['document_type']}": ""}},
            )

        # Delete the document
        return self.delete_one({"_id": document_id})

    def update_document(
        self, document_id: Union[str, ObjectId], update_data: Dict[str, Any]
    ) -> int:
        """Update a document."""
        if isinstance(document_id, str):
            document_id = ObjectId(document_id)

        # Set updated_at timestamp if not already included
        if "updated_at" not in update_data:
            update_data["updated_at"] = datetime.now()

        return self.update_one({"_id": document_id}, {"$set": update_data})

    def get_documents_by_entity(
        self, entity_type: EntityType, entity_id: Union[str, ObjectId]
    ) -> List[Dict[str, Any]]:
        """Get all documents for a specific entity by its entity type and ID."""
        if isinstance(entity_id, str):
            entity_id = ObjectId(entity_id)

        return self.find(
            {"entity_type": entity_type.value, "entity_id": entity_id},
            sort=[("created_at", -1)],
        )

    def find_documents_by_type(
        self,
        entity_type: EntityType,
        entity_id: Union[str, ObjectId],
        document_type: str,
    ) -> List[Dict[str, Any]]:
        """
        Find documents for a specific entity by document type.

        Args:
            entity_type: The type of entity (TRAVEL, PET, USER)
            entity_id: The ID of the entity
            document_type: The specific document type to search for

        Returns:
            List of matching documents
        """
        if isinstance(entity_id, str):
            entity_id = ObjectId(entity_id)

        return self.find(
            {
                "entity_type": entity_type.value,
                "entity_id": entity_id,
                "document_type": document_type,
            },
            sort=[("created_at", -1)],
        )


class AddressesDB(DBOperations):
    """Operations for the addresses collection."""

    def __init__(self):
        super().__init__("addresses")

    def create_address(self, address: Address) -> ObjectId:
        """Create a new address."""
        address_id = self.insert_one(address)

        # Update the entity with the new address ID
        if address.entity_type == EntityType.USER:
            users_db = UsersDB()
            if address.address_type == "residential":
                users_db.update_one(
                    {"_id": address.entity_id},
                    {"$set": {"residential_address_id": address_id}},
                )
            elif address.address_type == "delivery":
                users_db.update_one(
                    {"_id": address.entity_id},
                    {"$set": {"delivery_address_id": address_id}},
                )
        elif address.entity_type == EntityType.TRAVEL:
            travels_db = TravelsDB()
            travels_db.update_one(
                {"_id": address.entity_id},
                {"$set": {"destination_address_id": address_id}},
            )

        return address_id

    def get_address_by_id(self, address_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Get an address by ID."""
        if isinstance(address_id, str):
            address_id = ObjectId(address_id)
        return self.find_one({"_id": address_id})

    def get_entity_addresses(
        self, entity_type: EntityType, entity_id: Union[str, ObjectId]
    ) -> List[Dict[str, Any]]:
        """Get all addresses for a specific entity."""
        if isinstance(entity_id, str):
            entity_id = ObjectId(entity_id)
        return self.find({"entity_type": entity_type.value, "entity_id": entity_id})

    def update_address(
        self, address_id: Union[str, ObjectId], update_data: Dict[str, Any]
    ) -> int:
        """Update an address."""
        if isinstance(address_id, str):
            address_id = ObjectId(address_id)

        # Set updated_at timestamp
        update_data["updated_at"] = datetime.now()

        return self.update_one({"_id": address_id}, {"$set": update_data})


# Create instances of DB operation classes for convenience
users_db = UsersDB()
pets_db = PetsDB()
travels_db = TravelsDB()
documents_db = DocumentsDB()
addresses_db = AddressesDB()
