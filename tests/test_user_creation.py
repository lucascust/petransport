import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import mongomock
import json
from bson import ObjectId
from datetime import datetime
from io import BytesIO

# Add the parent directory to sys.path to import app and other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database_operations import UsersDB, PetsDB, AddressesDB, DocumentsDB
from models import (
    User,
    Pet,
    Address,
    EntityType,
    PetSpecies,
    Gender,
    DocumentType,
    FileType,
)


class TestUserCreation(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test_secret_key"
        self.app.config["UPLOAD_FOLDER"] = "tests/test_files/uploads"

        # Ensure the upload folder exists
        os.makedirs(self.app.config["UPLOAD_FOLDER"], exist_ok=True)

        # Mock MongoDB client
        self.mongo_patcher = patch("app.client")
        self.mock_mongo = self.mongo_patcher.start()

        # Set up mongomock for testing
        self.mock_db = mongomock.MongoClient().db
        self.mock_mongo.__getitem__.return_value = self.mock_db

        # Mock database classes
        self.users_db_patcher = patch("app.users_db")
        self.pets_db_patcher = patch("app.pets_db")
        self.addresses_db_patcher = patch("app.addresses_db")
        self.documents_db_patcher = patch("app.documents_db")

        self.mock_users_db = self.users_db_patcher.start()
        self.mock_pets_db = self.pets_db_patcher.start()
        self.mock_addresses_db = self.addresses_db_patcher.start()
        self.mock_documents_db = self.documents_db_patcher.start()

        # Configure mocks
        self.mock_users_db.create_user.return_value = ObjectId(
            "507f1f77bcf86cd799439011"
        )
        self.mock_pets_db.create_pet.return_value = ObjectId("507f1f77bcf86cd799439012")
        self.mock_addresses_db.create_address.return_value = ObjectId(
            "507f1f77bcf86cd799439013"
        )
        self.mock_documents_db.create_document.return_value = ObjectId(
            "507f1f77bcf86cd799439014"
        )

        # Create test client
        self.client = self.app.test_client()

        # Set up admin session for testing
        with self.client.session_transaction() as session:
            session["admin_logged_in"] = True

    def tearDown(self):
        """Clean up after each test."""
        # Stop patchers
        self.mongo_patcher.stop()
        self.users_db_patcher.stop()
        self.pets_db_patcher.stop()
        self.addresses_db_patcher.stop()
        self.documents_db_patcher.stop()

        # Clean up test files
        for file in os.listdir(self.app.config["UPLOAD_FOLDER"]):
            file_path = os.path.join(self.app.config["UPLOAD_FOLDER"], file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def test_user_creation_endpoint_get(self):
        """Test the GET method for the user creation page."""
        response = self.client.get("/cadastro_usuario_novo")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"owner_registration", response.data
        )  # Check if the page contains relevant content

    def test_user_creation_post_basic(self):
        """Test basic user creation without pets or delivery address."""
        # Create a basic user with minimal information
        data = {
            "owner_name": "John Doe",
            "email": "john.doe@example.com",
            "contact_number": "+551199999999",
            "hasCpf": "yes",
            "cpf": "123.456.789-00",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "google",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Paulista, 1000, São Paulo, SP",
            "endereco_residential_cidade": "São Paulo",
            "endereco_residential_estado": "SP",
            "endereco_residential_cep": "01310-100",
            "pet_count": "0",
        }

        response = self.client.post("/criar_usuario", data=data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["message"], "Usuário criado com sucesso")
        self.assertIn("username", response_data)

        # Verify the correct functions were called
        self.mock_users_db.create_user.assert_called_once()
        self.mock_addresses_db.create_address.assert_called_once()
        self.assertEqual(self.mock_pets_db.create_pet.call_count, 0)

    def test_user_creation_with_pets(self):
        """Test user creation with pets."""
        # Create a user with one pet
        data = {
            "owner_name": "Jane Smith",
            "email": "jane.smith@example.com",
            "contact_number": "+551188888888",
            "hasCpf": "yes",
            "cpf": "987.654.321-00",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "instagram",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Rua Augusta, 500, São Paulo, SP",
            "endereco_residential_cidade": "São Paulo",
            "endereco_residential_estado": "SP",
            "endereco_residential_cep": "01304-000",
            "pet_count": "1",
            "pets[0][name]": "Rex",
            "pets[0][species]": "canine",
            "pets[0][breed]": "Golden Retriever",
            "pets[0][gender]": "male",
            "pets[0][birth_date]": "01/01/2020",
            "pets[0][weight]": "25",
            "pets[0][microchip]": "123456789012345",
        }

        # Create pet photo file
        pet_photo = (BytesIO(b"fake image content"), "pet.jpg")
        data["pets[0][photo]"] = pet_photo

        response = self.client.post(
            "/criar_usuario", data=data, content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data["message"], "Usuário criado com sucesso")

        # Verify the correct functions were called
        self.mock_users_db.create_user.assert_called_once()
        self.mock_addresses_db.create_address.assert_called_once()
        self.mock_pets_db.create_pet.assert_called_once()
        self.mock_documents_db.create_document.assert_called_once()

    def test_user_creation_with_delivery_address(self):
        """Test user creation with both residential and delivery addresses."""
        # Create a user with multiple addresses
        data = {
            "owner_name": "Alice Johnson",
            "email": "alice.johnson@example.com",
            "contact_number": "+551177777777",
            "hasCpf": "yes",
            "cpf": "111.222.333-44",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "facebook",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Rua Oscar Freire, 200, São Paulo, SP",
            "endereco_residential_cidade": "São Paulo",
            "endereco_residential_estado": "SP",
            "endereco_residential_cep": "01426-000",
            "delivery_address": "yes",
            "endereco_delivery_lat": "-23.561729",
            "endereco_delivery_lng": "-46.655874",
            "endereco_delivery_formatted": "Av. Rebouças, 1000, São Paulo, SP",
            "endereco_delivery_cidade": "São Paulo",
            "endereco_delivery_estado": "SP",
            "endereco_delivery_cep": "05402-000",
            "pet_count": "0",
        }

        response = self.client.post("/criar_usuario", data=data)
        self.assertEqual(response.status_code, 200)

        # Verify the addresses were saved
        self.assertEqual(self.mock_addresses_db.create_address.call_count, 2)

    def test_user_creation_with_special_needs(self):
        """Test user creation with special needs."""
        data = {
            "owner_name": "Robert Brown",
            "email": "robert.brown@example.com",
            "contact_number": "+551166666666",
            "hasCpf": "yes",
            "cpf": "555.666.777-88",
            "hasSpecialNeeds": "yes",
            "special_needs_details": "Wheelchair user",
            "how_did_you_know": "recommendation",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Brigadeiro Faria Lima, 3000, São Paulo, SP",
            "endereco_residential_cidade": "São Paulo",
            "endereco_residential_estado": "SP",
            "endereco_residential_cep": "01451-000",
            "pet_count": "0",
        }

        response = self.client.post("/criar_usuario", data=data)
        self.assertEqual(response.status_code, 200)

        # Verify user with special needs was saved correctly
        user_data = self.mock_users_db.create_user.call_args[0][0]
        self.assertTrue(user_data.has_special_needs)
        self.assertEqual(user_data.special_needs_details, "Wheelchair user")

    def test_user_creation_with_passport(self):
        """Test user creation with passport instead of CPF."""
        data = {
            "owner_name": "Maria Silva",
            "email": "maria.silva@example.com",
            "contact_number": "+551155555555",
            "hasCpf": "no",
            "passport_number": "AB123456",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "other",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Rua da Consolação, 500, São Paulo, SP",
            "endereco_residential_cidade": "São Paulo",
            "endereco_residential_estado": "SP",
            "endereco_residential_cep": "01301-000",
            "pet_count": "0",
        }

        response = self.client.post("/criar_usuario", data=data)
        self.assertEqual(response.status_code, 200)

        # Verify user with passport was saved correctly
        user_data = self.mock_users_db.create_user.call_args[0][0]
        self.assertFalse(user_data.has_cpf)
        self.assertEqual(user_data.passport_number, "AB123456")

    def test_user_creation_full(self):
        """Test comprehensive user creation with all fields."""
        # Create a user with multiple pets, special needs, and delivery address
        data = {
            "owner_name": "Carlos Eduardo",
            "email": "carlos.eduardo@example.com",
            "contact_number": "+551144444444",
            "hasCpf": "yes",
            "cpf": "999.888.777-66",
            "hasSpecialNeeds": "yes",
            "special_needs_details": "Visual impairment",
            "how_did_you_know": "youtube",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Paulista, 2000, São Paulo, SP",
            "endereco_residential_cidade": "São Paulo",
            "endereco_residential_estado": "SP",
            "endereco_residential_cep": "01310-200",
            "delivery_address": "yes",
            "endereco_delivery_lat": "-23.561729",
            "endereco_delivery_lng": "-46.655874",
            "endereco_delivery_formatted": "Av. Rebouças, 2000, São Paulo, SP",
            "endereco_delivery_cidade": "São Paulo",
            "endereco_delivery_estado": "SP",
            "endereco_delivery_cep": "05402-200",
            "pet_count": "2",
            "pets[0][name]": "Luna",
            "pets[0][species]": "canine",
            "pets[0][breed]": "Labrador",
            "pets[0][gender]": "female",
            "pets[0][birth_date]": "01/01/2019",
            "pets[0][weight]": "22",
            "pets[0][microchip]": "111222333444555",
            "pets[1][name]": "Felix",
            "pets[1][species]": "feline",
            "pets[1][breed]": "Siamese",
            "pets[1][gender]": "male",
            "pets[1][birth_date]": "15/05/2020",
            "pets[1][weight]": "4.5",
            "pets[1][microchip]": "555444333222111",
        }

        # Create pet photo files
        pet_photo1 = (BytesIO(b"fake image content 1"), "pet1.jpg")
        pet_photo2 = (BytesIO(b"fake image content 2"), "pet2.jpg")
        data["pets[0][photo]"] = pet_photo1
        data["pets[1][photo]"] = pet_photo2

        response = self.client.post(
            "/criar_usuario", data=data, content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)

        # Verify all data was saved correctly
        self.mock_users_db.create_user.assert_called_once()
        self.assertEqual(self.mock_addresses_db.create_address.call_count, 2)
        self.assertEqual(self.mock_pets_db.create_pet.call_count, 2)
        self.assertEqual(self.mock_documents_db.create_document.call_count, 2)

    def test_reading_user_data(self):
        """Test reading user data after creation."""
        # Mock user data for retrieval
        mock_user = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "carlosEduardo",
            "owner_name": "Carlos Eduardo",
            "email": "carlos.eduardo@example.com",
            "contact_number": "+551144444444",
            "has_cpf": True,
            "cpf": "999.888.777-66",
            "has_special_needs": True,
            "special_needs_details": "Visual impairment",
            "how_did_you_know": "youtube",
            "registration_date": datetime.now(),
            "last_access": datetime.now(),
        }

        # Mock retrieving the user
        self.mock_users_db.get_user_by_username.return_value = mock_user

        # Mock admin session
        with self.client.session_transaction() as session:
            session["admin_logged_in"] = True

        # Test fetching user data
        response = self.client.get("/api/usuario/carlosEduardo")
        self.assertEqual(response.status_code, 200)

        # Verify user data was retrieved correctly
        self.mock_users_db.get_user_by_username.assert_called_once_with("carlosEduardo")

        # Parse response data
        response_data = json.loads(response.data)
        self.assertEqual(response_data["owner_name"], "Carlos Eduardo")
        self.assertEqual(response_data["email"], "carlos.eduardo@example.com")
        self.assertTrue(response_data["has_cpf"])
        self.assertTrue(response_data["has_special_needs"])

    def test_validation_missing_required_fields(self):
        """Test validation for missing required fields."""
        # Missing owner_name and email
        data = {
            "contact_number": "+551199999999",
            "hasCpf": "yes",
            "cpf": "123.456.789-00",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "google",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Paulista, 1000, São Paulo, SP",
            "pet_count": "0",
        }

        response = self.client.post("/criar_usuario", data=data)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertIn("Campos obrigatórios ausentes", response_data["error"])

    def test_validation_invalid_email(self):
        """Test validation for invalid email format."""
        data = {
            "owner_name": "John Doe",
            "email": "invalid-email",  # Invalid email format
            "contact_number": "+551199999999",
            "hasCpf": "yes",
            "cpf": "123.456.789-00",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "google",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Paulista, 1000, São Paulo, SP",
            "pet_count": "0",
        }

        response = self.client.post("/criar_usuario", data=data)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertIn("formato de email inválido", response_data["error"].lower())

    def test_validation_invalid_cpf(self):
        """Test validation for invalid CPF format."""
        data = {
            "owner_name": "John Doe",
            "email": "john.doe@example.com",
            "contact_number": "+551199999999",
            "hasCpf": "yes",
            "cpf": "123456",  # Invalid CPF format
            "hasSpecialNeeds": "no",
            "how_did_you_know": "google",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Paulista, 1000, São Paulo, SP",
            "pet_count": "0",
        }

        response = self.client.post("/criar_usuario", data=data)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertIn("cpf inválido", response_data["error"].lower())

    def test_pet_creation_validation(self):
        """Test validation for pet creation with missing fields."""
        data = {
            "owner_name": "John Doe",
            "email": "john.doe@example.com",
            "contact_number": "+551199999999",
            "hasCpf": "yes",
            "cpf": "123.456.789-00",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "google",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Paulista, 1000, São Paulo, SP",
            "pet_count": "1",
            # Missing required pet fields
            "pets[0][species]": "canine",
            "pets[0][gender]": "male",
            # Name is missing
        }

        response = self.client.post("/criar_usuario", data=data)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertIn("campos do pet ausentes", response_data["error"].lower())

    def test_multiple_pets_with_different_species(self):
        """Test creating a user with multiple pets of different species."""
        data = {
            "owner_name": "Pedro Santos",
            "email": "pedro.santos@example.com",
            "contact_number": "+551133333333",
            "hasCpf": "yes",
            "cpf": "444.555.666-77",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "instagram",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Rua Augusta, 800, São Paulo, SP",
            "endereco_residential_cidade": "São Paulo",
            "endereco_residential_estado": "SP",
            "endereco_residential_cep": "01305-000",
            "pet_count": "3",
            "pets[0][name]": "Rex",
            "pets[0][species]": "canine",
            "pets[0][breed]": "Golden Retriever",
            "pets[0][gender]": "male",
            "pets[0][birth_date]": "01/01/2020",
            "pets[0][weight]": "25",
            "pets[0][microchip]": "123456789012345",
            "pets[1][name]": "Luna",
            "pets[1][species]": "feline",
            "pets[1][breed]": "Maine Coon",
            "pets[1][gender]": "female",
            "pets[1][birth_date]": "15/03/2019",
            "pets[1][weight]": "6.5",
            "pets[1][microchip]": "987654321012345",
            "pets[2][name]": "Paco",
            "pets[2][species]": "bird",
            "pets[2][breed]": "Parrot",
            "pets[2][gender]": "male",
            "pets[2][birth_date]": "10/06/2021",
            "pets[2][weight]": "0.4",
            "pets[2][microchip]": "",  # Empty microchip
        }

        # Create pet photo files
        pet_photo1 = (BytesIO(b"fake image content 1"), "pet1.jpg")
        pet_photo2 = (BytesIO(b"fake image content 2"), "pet2.jpg")
        pet_photo3 = (BytesIO(b"fake image content 3"), "pet3.jpg")
        data["pets[0][photo]"] = pet_photo1
        data["pets[1][photo]"] = pet_photo2
        data["pets[2][photo]"] = pet_photo3

        response = self.client.post(
            "/criar_usuario", data=data, content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)

        # Verify all pets were created
        self.assertEqual(self.mock_pets_db.create_pet.call_count, 3)
        self.assertEqual(self.mock_documents_db.create_document.call_count, 3)

        # Verify pet species were correctly saved
        pet1_data = self.mock_pets_db.create_pet.call_args_list[0][0][0]
        pet2_data = self.mock_pets_db.create_pet.call_args_list[1][0][0]
        pet3_data = self.mock_pets_db.create_pet.call_args_list[2][0][0]

        self.assertEqual(pet1_data.species, PetSpecies.CANINE)
        self.assertEqual(pet2_data.species, PetSpecies.FELINE)
        self.assertEqual(pet3_data.species, PetSpecies.BIRD)

    def test_update_existing_user(self):
        """Test updating an existing user."""
        # First create a user
        self.mock_users_db.get_user_by_username.return_value = None  # Not found
        self.mock_users_db.create_user.return_value = ObjectId(
            "507f1f77bcf86cd799439011"
        )

        data = {
            "owner_name": "John Doe",
            "email": "john.doe@example.com",
            "contact_number": "+551199999999",
            "hasCpf": "yes",
            "cpf": "123.456.789-00",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "google",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Paulista, 1000, São Paulo, SP",
            "pet_count": "0",
        }

        self.client.post("/criar_usuario", data=data)

        # Now update the user
        self.mock_users_db.get_user_by_id.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "johnDoe",
            "owner_name": "John Doe",
            "email": "john.doe@example.com",
            "contact_number": "+551199999999",
            "has_cpf": True,
            "cpf": "123.456.789-00",
            "has_special_needs": False,
            "how_did_you_know": "google",
            "registration_date": datetime.now(),
            "last_access": datetime.now(),
        }

        update_data = {
            "owner_name": "John Doe Updated",
            "email": "john.updated@example.com",
            "contact_number": "+551188888888",
            "hasSpecialNeeds": "yes",
            "special_needs_details": "Hearing impairment",
        }

        response = self.client.put(
            "/api/usuario/507f1f77bcf86cd799439011",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.mock_users_db.update_user.assert_called_once()

        # Check that the updated data was passed correctly
        updated_user = self.mock_users_db.update_user.call_args[0][1]
        self.assertEqual(updated_user.owner_name, "John Doe Updated")
        self.assertEqual(updated_user.email, "john.updated@example.com")
        self.assertEqual(updated_user.contact_number, "+551188888888")
        self.assertTrue(updated_user.has_special_needs)
        self.assertEqual(updated_user.special_needs_details, "Hearing impairment")

    def test_add_pet_to_existing_user(self):
        """Test adding a new pet to an existing user."""
        # Mock existing user
        self.mock_users_db.get_user_by_id.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "johnDoe",
            "owner_name": "John Doe",
            "email": "john.doe@example.com",
            "pets": [],  # No pets initially
        }

        # Data for adding a new pet
        data = {
            "name": "Buddy",
            "species": "canine",
            "breed": "Beagle",
            "gender": "male",
            "birth_date": "10/05/2021",
            "weight": "12.5",
            "microchip": "666777888999000",
        }

        # Create pet photo file
        pet_photo = (BytesIO(b"fake image content"), "buddy.jpg")
        data["photo"] = pet_photo

        response = self.client.post(
            "/api/usuario/507f1f77bcf86cd799439011/pet",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 201)
        self.mock_pets_db.create_pet.assert_called_once()
        self.mock_documents_db.create_document.assert_called_once()

        # Verify pet data was saved correctly
        pet_data = self.mock_pets_db.create_pet.call_args[0][0]
        self.assertEqual(pet_data.name, "Buddy")
        self.assertEqual(pet_data.species, PetSpecies.CANINE)
        self.assertEqual(pet_data.breed, "Beagle")
        self.assertEqual(pet_data.gender, Gender.MALE)

    def test_delete_user(self):
        """Test deleting a user and all related data."""
        # Mock existing user
        user_id = ObjectId("507f1f77bcf86cd799439011")
        self.mock_users_db.get_user_by_id.return_value = {
            "_id": user_id,
            "username": "johnDoe",
            "owner_name": "John Doe",
            "email": "john.doe@example.com",
            "pets": [ObjectId("507f1f77bcf86cd799439012")],
            "addresses": [ObjectId("507f1f77bcf86cd799439013")],
        }

        response = self.client.delete(f"/api/usuario/{user_id}")

        self.assertEqual(response.status_code, 200)

        # Verify all database delete operations were called
        self.mock_users_db.delete_user.assert_called_once_with(user_id)
        self.mock_pets_db.delete_pet.assert_called_once()
        self.mock_addresses_db.delete_address.assert_called_once()

        # If documents associated with pets are also deleted
        self.mock_documents_db.delete_documents_by_entity.assert_called_once()

    def test_database_error_handling(self):
        """Test error handling when database operations fail."""
        # Set up database operation to raise an exception
        self.mock_users_db.create_user.side_effect = Exception(
            "Database connection error"
        )

        data = {
            "owner_name": "John Doe",
            "email": "john.doe@example.com",
            "contact_number": "+551199999999",
            "hasCpf": "yes",
            "cpf": "123.456.789-00",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "google",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Paulista, 1000, São Paulo, SP",
            "pet_count": "0",
        }

        response = self.client.post("/criar_usuario", data=data)

        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertIn("falha ao criar usuário", response_data["error"].lower())

    def test_address_validation(self):
        """Test validation for address fields."""
        data = {
            "owner_name": "John Doe",
            "email": "john.doe@example.com",
            "contact_number": "+551199999999",
            "hasCpf": "yes",
            "cpf": "123.456.789-00",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "google",
            # Missing residential address coordinates
            "endereco_residential_formatted": "Av. Paulista, 1000, São Paulo, SP",
            "pet_count": "0",
        }

        response = self.client.post("/criar_usuario", data=data)

        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn("error", response_data)
        self.assertIn("endereço residencial incompleto", response_data["error"].lower())

    def test_user_username_generation(self):
        """Test username generation for new users."""
        data = {
            "owner_name": "José da Silva",  # Name with special characters
            "email": "jose.silva@example.com",
            "contact_number": "+551199999999",
            "hasCpf": "yes",
            "cpf": "123.456.789-00",
            "hasSpecialNeeds": "no",
            "how_did_you_know": "google",
            "endereco_residential_lat": "-23.550520",
            "endereco_residential_lng": "-46.633308",
            "endereco_residential_formatted": "Av. Paulista, 1000, São Paulo, SP",
            "endereco_residential_cidade": "São Paulo",
            "endereco_residential_estado": "SP",
            "endereco_residential_cep": "01310-100",
            "pet_count": "0",
        }

        # Username generation logic
        def create_user_side_effect(user_data):
            # Check if the username is properly normalized
            self.assertIn("joseDaSilva", user_data.username)
            return ObjectId("507f1f77bcf86cd799439011")

        self.mock_users_db.create_user.side_effect = create_user_side_effect

        response = self.client.post("/criar_usuario", data=data)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
