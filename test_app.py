import pytest
from app import app  # Your Flask app instance
import io  # For simulating file uploads
import os  # For secret key if needed
from unittest.mock import patch, MagicMock, call
from bson import ObjectId
from datetime import datetime
import re  # For microchip cleaning check


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF if you use Flask-WTF
    # It's good practice to use a specific test secret key
    # or ensure your app.config['SECRET_KEY'] is set appropriately for tests
    # For example, from an environment variable or a test config
    app.config["SECRET_KEY"] = os.getenv(
        "TEST_SECRET_KEY", "test_secret_key_for_pytest_12345"
    )
    app.config["UPLOAD_FOLDER"] = (
        "static/uploads"  # Ensure it's set, even if we mock os ops
    )

    with app.test_client() as client:
        # Ensure an application context is active for session operations
        with app.app_context():
            # Simulate admin login for the session
            with client.session_transaction() as sess:
                sess["admin_logged_in"] = True
        yield client


# Helper to compare Pydantic models or dicts, being careful about ObjectId and datetime
def assert_obj_equiv(obj1, obj2, ignore_keys=None):
    if ignore_keys is None:
        ignore_keys = []

    d1 = obj1.__dict__ if hasattr(obj1, "__dict__") else obj1
    d2 = obj2.__dict__ if hasattr(obj2, "__dict__") else obj2

    # Filter out ignored keys before comparing lengths or iterating
    filtered_d1_keys = {k for k in d1 if k not in ignore_keys}
    filtered_d2_keys = {k for k in d2 if k not in ignore_keys}

    assert len(filtered_d1_keys) == len(filtered_d2_keys), (
        f"Different number of non-ignored keys: {len(filtered_d1_keys)} vs {len(filtered_d2_keys)}.\n"
        f"Keys1: {filtered_d1_keys}, Keys2: {filtered_d2_keys}"
    )

    for key in filtered_d1_keys:
        assert (
            key in filtered_d2_keys
        ), f"Key {key} not in second object's non-ignored keys"
        val1 = d1[key]
        val2 = d2[key]
        if isinstance(val1, ObjectId) or isinstance(val2, ObjectId):
            assert str(val1) == str(
                val2
            ), f"ObjectId mismatch for key {key}: {str(val1)} vs {str(val2)}"
        elif isinstance(val1, datetime) and isinstance(val2, datetime):
            assert isinstance(val1, datetime) and isinstance(
                val2, datetime
            ), f"Type mismatch or non-datetime for key {key}"
        elif isinstance(val1, list) and isinstance(val2, list):
            assert len(val1) == len(val2), f"List length mismatch for key {key}"
            # More sophisticated list comparison might be needed depending on content
            for item1, item2 in zip(val1, val2):
                assert_obj_equiv(
                    item1, item2, ignore_keys
                )  # Recursive call for nested objects
        elif isinstance(val1, dict) and isinstance(val2, dict):
            assert_obj_equiv(val1, val2, ignore_keys)  # Recursive call for nested dicts
        elif isinstance(val1, float) and isinstance(val2, float):
            assert (
                abs(val1 - val2) < 1e-9
            ), f"Float mismatch for key {key}: {val1} vs {val2}"
        else:
            assert val1 == val2, f"Value mismatch for key {key}: {val1} vs {val2}"


# Base form data generator reflecting cadastro_usuario_novo.html structure
def get_default_valid_form_data():
    return {
        "pet_count": "1",
        "owner_name": "Milena Grazielle Rodovalho Mendonca",
        "password": "mila1234",
        "email": "milenagrarodo@gmail.com",
        "contact_number": "+14161234567",  # Example valid phone number after JS processing
        "full_phone_with_code": "+14161234567",  # Assume JS populates this
        "hasCpf": "no",  # Defaulting to passport as in original scenario
        "cpf": "",
        "passport_number": "F0899684",
        "residential_address": "2908 Hwy 7 #1308, Concord, ON L4K 0K5, Canadá",
        "endereco_residential_lat": "43.7961219",
        "endereco_residential_lng": "-79.5204803",
        "endereco_residential_formatted": "2908 Hwy 7 #1308, Concord, ON L4K 0K5, Canadá",
        "endereco_residential_cidade": "Vaughan",
        "endereco_residential_estado": "ON",
        "endereco_residential_cep": "L4K 0K5",
        # Delivery address included as per original payload
        "delivery_address": "Rua Engenheiro Moacyr Parahyba, 385 - apto 101 - Iputinga, Recife - PE, 50800-320, Brazil",
        "endereco_delivery_lat": "-8.0349703",
        "endereco_delivery_lng": "-34.9391845",
        "endereco_delivery_formatted": "Rua Engenheiro Moacyr Parahyba, 385 - apto 101 - Iputinga, Recife - PE, 50800-320, Brasil",
        "endereco_delivery_cidade": "",
        "endereco_delivery_estado": "PE",
        "endereco_delivery_cep": "50800-320",
        "hasSpecialNeeds": "no",
        "special_needs_details": "",
        "how_did_you_know": "instagram",  # Value from the dropdown
        "pets[0][name]": "Mila",
        "pets[0][species]": "canine",
        "pets[0][breed]": "Poodle",
        "pets[0][gender]": "male",
        "pets[0][birth_date]": "01/06/2023",
        "pets[0][weight]": "3.8",
        "pets[0][microchip]": "952.000.001.491.276",
        "pets[0][fur_color]": "Apricot (avermelhada)",
        "pets[0][photo]": (io.BytesIO(b"fake_photo_content_mila"), "mila.jpg"),
    }


# Test scenarios
scenarios = [
    ("valid_passport_one_pet_with_photo", {}, 200, None),
    (
        "valid_cpf_one_pet_no_photo",
        {
            "hasCpf": "yes",
            "cpf": "123.456.789-00",
            "passport_number": "",
            "pets[0][photo]": (io.BytesIO(b""), ""),
        },
        200,
        None,
    ),
    ("valid_no_pets", {"pet_count": "0"}, 200, None),
    (
        "missing_owner_name",
        {"owner_name": ""},
        400,
        "Owner name ('owner_name') is required and cannot be empty",
    ),
    (
        "missing_password",
        {"password": ""},
        400,
        "Password ('password') is required and cannot be empty",
    ),
    (
        "invalid_pet_microchip_too_long",
        {"pets[0][microchip]": "1234567890123456"},
        400,
        "microchip '1234567890123456' is invalid",
    ),
]


@pytest.mark.parametrize(
    "test_name, overrides, expected_status, expected_error_key", scenarios
)
@patch("app.os.path.getsize")
@patch("app.os.remove")
@patch("app.os.path.exists")
@patch("app.upload_file_to_firebase")
@patch("app.pets_db")
@patch("app.documents_db")
@patch("app.addresses_db")
@patch("app.users_db")
def test_criar_usuario_form_scenarios(
    mock_users_db_instance,
    mock_addresses_db_instance,
    mock_documents_db_instance,
    mock_pets_db_instance,
    mock_upload_firebase_func,
    mock_os_path_exists,
    mock_os_remove,
    mock_os_getsize,
    client,
    test_name,
    overrides,
    expected_status,
    expected_error_key,
):
    form_data = get_default_valid_form_data()
    form_data.update(overrides)

    # Clean up pet data if pet_count is "0"
    if form_data.get("pet_count") == "0":
        pet_keys_to_remove = [k for k in form_data if k.startswith("pets[")]
        for key_to_remove in pet_keys_to_remove:
            del form_data[key_to_remove]

    # --- Mock Setup ---
    mock_user_id = ObjectId()
    mock_pets_db_instance.create_pet.return_value = ObjectId()  # General pet_id
    mock_documents_db_instance.create_document.return_value = ObjectId()
    mock_users_db_instance.create_user.return_value = mock_user_id
    mock_addresses_db_instance.create_address.side_effect = [
        ObjectId(),
        ObjectId(),
    ]  # For res and deliv
    mock_pets_db_instance.update_pet.return_value = 1
    mock_upload_firebase_func.return_value = {
        "blob_name": "mock_user/pets/mock_photo.jpg",
        "firebase_path": "firebase_storage_path/mock_photo.jpg",
        "public_url": "http://mockurl.com/photo.jpg",
    }
    mock_os_path_exists.return_value = True
    mock_os_getsize.return_value = 12345
    mock_os_remove.return_value = None

    # --- Make the POST request ---
    response = client.post(
        "/criar_usuario", data=form_data, content_type="multipart/form-data"
    )

    # --- Assertions ---
    assert (
        response.status_code == expected_status
    ), f"Test '{test_name}': Status code mismatch. Response: {response.get_data(as_text=True)}"
    json_data = response.get_json()

    if expected_status == 200:
        assert (
            json_data is not None
        ), f"Test '{test_name}': Response was not JSON for a 200 status."
        assert (
            json_data.get("message") == "Usuário criado com sucesso"
        ), f"Test '{test_name}': Success message mismatch."
        assert (
            "username" in json_data
        ), f"Test '{test_name}': Username missing in success response."
        generated_username = json_data["username"]

        # Assert User Creation Call
        mock_users_db_instance.create_user.assert_called_once()
        # ... (detailed assertions for user, address, pet, doc, firebase calls for happy paths)
        # Example for user:
        args_user_call = mock_users_db_instance.create_user.call_args[0][0]
        assert args_user_call.owner_name == form_data["owner_name"]
        if form_data.get("hasCpf") == "yes":
            assert args_user_call.cpf == form_data["cpf"]
            assert args_user_call.passport_number is None
        else:
            assert args_user_call.passport_number == form_data["passport_number"]
            assert args_user_call.cpf is None

        # Assert Address Creation (called for residential, and for delivery if delivery_address is present)
        expected_address_calls = 1
        if form_data.get("delivery_address"):
            expected_address_calls = 2
        assert (
            mock_addresses_db_instance.create_address.call_count
            == expected_address_calls
        )

        if (
            form_data.get("pet_count") != "0"
            and form_data.get("pets[0][photo]")
            and form_data["pets[0][photo]"][1]
        ):  # Photo has a filename
            mock_upload_firebase_func.assert_called_once()
            mock_documents_db_instance.create_document.assert_called_once()
            mock_pets_db_instance.update_pet.assert_called_once()
        elif form_data.get("pet_count") != "0":  # Pet exists but no photo
            mock_upload_firebase_func.assert_not_called()
            mock_documents_db_instance.create_document.assert_not_called()
            mock_pets_db_instance.update_pet.assert_not_called()
        else:  # No pets
            mock_pets_db_instance.create_pet.assert_not_called()
            mock_upload_firebase_func.assert_not_called()
            mock_documents_db_instance.create_document.assert_not_called()
            mock_pets_db_instance.update_pet.assert_not_called()

    else:  # Error cases (e.g. 400)
        assert (
            json_data is not None
        ), f"Test '{test_name}': Error response was not JSON."
        assert (
            "error" in json_data
        ), f"Test '{test_name}': 'error' key missing in error response."
        if (
            expected_error_key
        ):  # Not all 400s might have a specific snippet we check here yet
            assert (
                expected_error_key.lower() in json_data["error"].lower()
            ), f"Test '{test_name}': Expected error snippet '{expected_error_key}' not found in '{json_data['error']}'."
