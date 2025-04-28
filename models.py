from typing import List, Dict, Optional, Any, Union, Literal
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationInfo
import re
import os
import uuid
from bson import ObjectId
import bcrypt  # Add bcrypt for password hashing


def parse_date(date_string: str) -> datetime:
    """
    Parse a date string in multiple possible formats.

    Tries multiple date formats and returns a datetime object.
    If no format matches, raises ValueError.
    """
    if not date_string:
        raise ValueError("Date string cannot be empty")

    # Check if we have date and time components
    has_time = False
    if " " in date_string and (":" in date_string.split(" ", 1)[1]):
        has_time = True

    # Formats with time components
    datetime_formats = [
        "%d/%m/%Y %H:%M",  # 31/12/2023 14:30
        "%d/%m/%Y %H:%M:%S",  # 31/12/2023 14:30:45
        "%Y-%m-%d %H:%M",  # 2023-12-31 14:30
        "%Y-%m-%d %H:%M:%S",  # 2023-12-31 14:30:45
        "%m/%d/%Y %H:%M",  # 12/31/2023 14:30
        "%m/%d/%Y %H:%M:%S",  # 12/31/2023 14:30:45
        "%d-%m-%Y %H:%M",  # 31-12-2023 14:30
        "%d-%m-%Y %H:%M:%S",  # 31-12-2023 14:30:45
        "%d.%m.%Y %H:%M",  # 31.12.2023 14:30
        "%d.%m.%Y %H:%M:%S",  # 31.12.2023 14:30:45
        "%d %b %Y %H:%M",  # 31 Dec 2023 14:30
        "%d %B %Y %H:%M",  # 31 December 2023 14:30
        "%b %d, %Y %H:%M",  # Dec 31, 2023 14:30
        "%B %d, %Y %H:%M",  # December 31, 2023 14:30
    ]

    # Date-only formats
    date_formats = [
        "%d/%m/%Y",  # 31/12/2023
        "%Y-%m-%d",  # 2023-12-31
        "%m/%d/%Y",  # 12/31/2023
        "%d-%m-%Y",  # 31-12-2023
        "%Y/%m/%d",  # 2023/12/31
        "%d.%m.%Y",  # 31.12.2023
        "%Y.%m.%d",  # 2023.12.31
        "%d %b %Y",  # 31 Dec 2023
        "%d %B %Y",  # 31 December 2023
        "%b %d, %Y",  # Dec 31, 2023
        "%B %d, %Y",  # December 31, 2023
    ]

    # Try formats based on whether time component is present
    formats_to_try = datetime_formats + date_formats if has_time else date_formats

    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f"Could not parse date string: {date_string}")


class PyObjectId(ObjectId):
    """Custom type for handling MongoDB ObjectId."""

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def validate(cls, value):
        if isinstance(value, ObjectId):
            return value
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)


class FileType(str, Enum):
    """Tipos de arquivo suportados."""

    IMAGE = "image"
    PDF = "pdf"


class TravelMethod(str, Enum):
    """Métodos de viagem suportados."""

    PLANE = "plane"
    BUS = "bus"
    CAR = "car"
    PET_TRANSPORT = "petTransport"
    OTHER = "other"


class TravelStatus(str, Enum):
    """Status possíveis para viagens."""

    UPCOMING = "upcoming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PetSpecies(str, Enum):
    """Espécies de animais suportadas."""

    CANINE = "canine"
    FELINE = "feline"
    BIRD = "bird"
    RODENT = "rodent"
    OTHER = "other"


class Gender(str, Enum):
    """Gêneros suportados."""

    MALE = "male"
    FEMALE = "female"


class DocumentType(str, Enum):
    """Tipos de documentos comuns."""

    # Documentos de pet
    VACCINATION_CARD = "vaccinationCard"
    MICROCHIP_CERTIFICATE = "microchipCertificate"
    RABIES_SEROLOGY = "rabiesSerologyReport"
    LEISHMANIASIS_SEROLOGY = "leishmaniasisSerologyReport"
    IMPORT_PERMIT = "importPermit"
    PET_PASSPORT = "petPassport"
    CVI = "cvi"
    EXPORT_AUTHORIZATION = "exportAuthorization"
    ARRIVAL_NOTICE = "arrivalNotice"
    ENDORSED_CVI = "endorsedCvi"
    AWB_CARGO = "awbCargo"
    PET_FACILITIES = "petFacilities"

    # Documentos humanos
    IDENTITY_DOCUMENT = "identityDocument"
    CVI_ISSUANCE_AUTHORIZATION = "cviIssuanceAuthorization"
    PASSPORT = "passport"
    TRAVEL_TICKET = "travelTicket"
    TRAVEL_AUTHORIZATION = "travelAuthorization"
    CAR_DOCUMENT = "carDocument"
    ADDRESS_PROOF = "addressProof"

    # Outros
    PET_PHOTO = "petPhoto"
    OTHER = "other"


class EntityType(str, Enum):
    """Tipos de entidades para referência."""

    USER = "user"
    PET = "pet"
    TRAVEL = "travel"
    DOCUMENT = "document"


# Base models with core fields
class MongoBaseModel(BaseModel):
    """Base model with MongoDB ID and common fields."""

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat(),
        },
    }

    def model_dump(self, **kwargs):
        """Override model_dump method to handle ObjectId."""
        data = super().model_dump(**kwargs)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data


class Address(MongoBaseModel):
    """Modelo para endereço."""

    entity_type: EntityType  # A que entidade pertence (user, travel)
    entity_id: PyObjectId  # ID da entidade correspondente
    lat: Optional[str] = None
    lng: Optional[str] = None
    formatted: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    address_type: str = "residential"  # residential, delivery, destination

    @classmethod
    def from_dict(
        cls,
        address_data: Dict[str, Any],
        entity_type: EntityType,
        entity_id: PyObjectId,
        address_type: str = "residential",
    ) -> "Address":
        """Cria um endereço a partir de um dicionário."""
        if not address_data:
            return None

        return cls(
            entity_type=entity_type,
            entity_id=entity_id,
            lat=address_data.get("lat"),
            lng=address_data.get("lng"),
            formatted=address_data.get("formatted"),
            city=address_data.get("cidade") or address_data.get("city"),
            state=address_data.get("estado") or address_data.get("state"),
            zip_code=address_data.get("cep") or address_data.get("zip_code"),
            address_type=address_type,
        )


class Document(MongoBaseModel):
    """Modelo unificado para todos os tipos de documentos."""

    entity_type: EntityType  # user, pet, travel
    entity_id: (
        PyObjectId  # ID da entidade a que pertence (para viagem, sempre o viagem_id)
    )
    document_type: DocumentType  # Tipo específico do documento
    filename: str  # Nome original do arquivo
    path: str  # Caminho de armazenamento (local or firebase blob name)
    file_type: FileType  # Tipo do arquivo (imagem ou PDF)
    size: int  # Tamanho em bytes
    description: Optional[str] = None  # Descrição opcional

    # Firebase Storage fields
    firebase_path: Optional[str] = (
        None  # Full Firebase Storage path (gs://bucket-name/path)
    )
    public_url: Optional[str] = None  # Public URL for the file
    storage_type: str = "local"  # 'local' or 'firebase'
    # Novo: subpasta para organização (ex: 'passport', 'pets/{pet_id}/vaccinationCard')
    firebase_subfolder: Optional[str] = None

    # NOVO: Referência explícita ao pet (para documentos de pet em viagem)
    pet_id: Optional[PyObjectId] = None

    @classmethod
    def create_document(
        cls,
        file_path: str,
        entity_type: EntityType,
        entity_id: PyObjectId,
        document_type: DocumentType,
        file_type: Optional[FileType] = None,
        description: Optional[str] = None,
        firebase_path: Optional[str] = None,
        public_url: Optional[str] = None,
        storage_type: str = "local",
        firebase_subfolder: Optional[str] = None,
        pet_id: Optional[PyObjectId] = None,
    ) -> "Document":
        """Cria um documento a partir de um arquivo."""

        # Extrair o nome do arquivo do caminho
        filename = os.path.basename(file_path)

        # Inferir o tipo do arquivo pela extensão se não for fornecido
        if file_type is None:
            extension = os.path.splitext(filename)[1].lower()
            if extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
                file_type = FileType.IMAGE
            elif extension == ".pdf":
                file_type = FileType.PDF
            else:
                raise ValueError(f"Tipo de arquivo não suportado: {extension}")

        # Obter tamanho do arquivo (se existir)
        size = 0
        try:
            if os.path.exists(file_path) and storage_type == "local":
                size = os.path.getsize(file_path)
        except:
            pass  # Ignora erros ao obter tamanho do arquivo

        # Criar e retornar o documento
        return cls(
            entity_type=entity_type,
            entity_id=entity_id,
            document_type=document_type,
            filename=filename,
            path=file_path,
            file_type=file_type,
            size=size,
            description=description,
            firebase_path=firebase_path,
            public_url=public_url,
            storage_type=storage_type,
            firebase_subfolder=firebase_subfolder,
            pet_id=pet_id,
        )


class Pet(MongoBaseModel):
    """Modelo para pets."""

    owner_id: PyObjectId  # Referência ao usuário proprietário
    name: str
    species: PetSpecies
    breed: str
    gender: Gender
    birth_date: datetime
    microchip: Optional[str] = None
    weight: Optional[str] = None
    fur_color: Optional[str] = None
    photo_id: Optional[PyObjectId] = None  # Referência ao documento de foto

    @classmethod
    def from_dict(cls, pet_data: Dict[str, Any], owner_id: PyObjectId) -> "Pet":
        """Cria um pet a partir de um dicionário."""
        # Converte a data de nascimento para datetime usando função robusta
        birth_date = parse_date(pet_data.get("birth_date"))

        return cls(
            owner_id=owner_id,
            name=pet_data.get("name"),
            species=pet_data.get("species"),
            breed=pet_data.get("breed"),
            gender=pet_data.get("gender"),
            birth_date=birth_date,
            microchip=pet_data.get("microchip"),
            weight=pet_data.get("weight"),
            fur_color=pet_data.get("fur_color"),
        )


class User(MongoBaseModel):
    """Modelo para usuário."""

    username: str
    owner_name: str
    email: str
    contact_number: str
    has_cpf: bool
    cpf: Optional[str] = None
    passport_number: Optional[str] = None
    has_special_needs: bool
    special_needs_details: Optional[str] = None
    how_did_you_know: Optional[str] = None
    residential_address_id: Optional[PyObjectId] = None
    delivery_address_id: Optional[PyObjectId] = None
    last_access: datetime = Field(default_factory=datetime.now)
    pet_ids: List[PyObjectId] = Field(default_factory=list)
    document_ids: Dict[str, PyObjectId] = Field(default_factory=dict)
    password_hash: str  # Store hashed password, not plain text

    @classmethod
    def from_form_data(cls, form_data: Dict[str, Any]) -> "User":
        """Cria um usuário a partir de dados de formulário."""
        password = form_data["password"]
        password_hash = cls.hash_password(password)
        return cls(
            username=form_data.get("username"),
            owner_name=form_data["owner_name"],
            email=form_data["email"],
            contact_number=form_data["contact_number"],
            has_cpf=form_data.get("hasCpf") == "yes",
            cpf=form_data.get("cpf") if form_data.get("hasCpf") == "yes" else None,
            passport_number=(
                form_data.get("passport_number")
                if form_data.get("hasCpf") == "no"
                else None
            ),
            has_special_needs=form_data.get("hasSpecialNeeds") == "yes",
            special_needs_details=(
                form_data.get("special_needs_details")
                if form_data.get("hasSpecialNeeds") == "yes"
                else None
            ),
            how_did_you_know=form_data.get("how_did_you_know"),
            password_hash=password_hash,
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """Verify a stored password against one provided by user."""
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )


class Travel(MongoBaseModel):
    """Modelo para viagens."""

    user_id: PyObjectId  # Referência ao usuário proprietário
    username: str  # Nome de usuário (duplicado para facilitar consultas)
    status: TravelStatus = TravelStatus.UPCOMING

    # Localizações
    origin: str
    destination: str
    destination_address_id: Optional[PyObjectId] = (
        None  # Referência ao endereço de destino
    )
    border_city: Optional[str] = None

    # Detalhes da viagem
    travel_method: TravelMethod
    vehicle_plate: Optional[str] = None
    ticket_document_id: Optional[PyObjectId] = (
        None  # Referência ao documento da passagem
    )
    ticket_date: Optional[datetime] = None
    estimated_date: Optional[str] = None

    # Referências
    pet_ids: List[PyObjectId] = Field(default_factory=list)  # Referências aos pets
    document_ids: Dict[str, PyObjectId] = Field(
        default_factory=dict
    )  # {tipo_documento: id_documento}

    # Documentos obrigatórios
    required_documents: Dict[str, Any] = Field(
        default_factory=lambda: {
            "human_docs": [],
            # pet_docs: Dict[str, List[str]] where key is pet_id (as str), value is list of required doc types for that pet
            "pet_docs": {},
        }
    )

    @classmethod
    def from_form_data(
        cls, form_data: Dict[str, Any], user_id: PyObjectId, username: str
    ) -> "Travel":
        """Cria uma viagem a partir de dados de formulário."""
        # Converte a data/hora da passagem para datetime
        ticket_date = None
        if form_data.get("travelTicketDate"):
            try:
                ticket_date = parse_date(form_data["travelTicketDate"])
            except ValueError:
                # Falha silenciosa mantendo None
                pass

        return cls(
            user_id=user_id,
            username=username,
            origin=form_data["origin"],
            destination=form_data["destination"],
            ticket_date=ticket_date,
            estimated_date=form_data.get("estimatedDate"),
            travel_method=form_data["travelMethod"],
            border_city=form_data.get("borderCity"),
            vehicle_plate=form_data.get("vehiclePlate"),
            pet_ids=(
                form_data.getlist("travelingPets")
                if hasattr(form_data, "getlist")
                else form_data.get("travelingPets", [])
            ),
            status=TravelStatus.UPCOMING,
        )


class AdminUserView(BaseModel):
    """Modelo para visualização de usuário no admin."""

    owner_name: str
    username: str
    registration_date: datetime
    last_access: datetime
    pets_count: int = 0
    travels_count: int = 0


# Funções auxiliares para migração e interoperabilidade
def create_file_document(
    file_path: str,
    entity_type: EntityType,
    entity_id: PyObjectId,
    document_type: DocumentType,
    file_type: Optional[FileType] = None,
) -> Document:
    """Função para compatibilidade com código legado."""
    return Document.create_document(
        file_path=file_path,
        entity_type=entity_type,
        entity_id=entity_id,
        document_type=document_type,
        file_type=file_type,
    )


# Frontend validation schemas
# These schemas are used for frontend validation only and don't affect database models
class FrontendValidation:
    """Provides validation rules for frontend forms without restricting backend models."""

    @staticmethod
    def validate_microchip(microchip: Optional[str]) -> dict:
        """Valida o formato do microchip."""
        result = {"valid": True, "message": ""}
        if microchip is not None and not re.match(
            r"^[0-9]{1,15}$", microchip.replace(".", "")
        ):
            result["valid"] = False
            result["message"] = "Microchip deve conter até 15 dígitos."
        return result

    @staticmethod
    def validate_cpf(cpf: Optional[str], has_cpf: bool) -> dict:
        """Valida o CPF."""
        result = {"valid": True, "message": ""}

        if has_cpf and not cpf:
            result["valid"] = False
            result["message"] = "CPF é obrigatório."
            return result

        if cpf is not None:
            # Remove pontuação
            cpf_clean = cpf.replace(".", "").replace("-", "")
            if not re.match(r"^\d{11}$", cpf_clean):
                result["valid"] = False
                result["message"] = "CPF deve conter 11 dígitos."

        return result

    @staticmethod
    def validate_passport(passport: Optional[str], has_cpf: bool) -> dict:
        """Valida o passaporte."""
        result = {"valid": True, "message": ""}

        if not has_cpf and not passport:
            result["valid"] = False
            result["message"] = "Número do passaporte é obrigatório."
            return result

        if passport is not None and not re.match(r"^[A-Z0-9]{8,9}$", passport):
            result["valid"] = False
            result["message"] = (
                "Passaporte deve conter 8-9 caracteres alfanuméricos (A-Z, 0-9)."
            )

        return result

    @staticmethod
    def validate_special_needs_details(
        details: Optional[str], has_special_needs: bool
    ) -> dict:
        """Valida os detalhes de necessidades especiais."""
        result = {"valid": True, "message": ""}

        if has_special_needs and not details:
            result["valid"] = False
            result["message"] = "Detalhes de necessidades especiais são obrigatórios."

        return result

    @staticmethod
    def validate_vehicle_plate(plate: Optional[str], travel_method: str) -> dict:
        """Valida a placa do veículo."""
        result = {"valid": True, "message": ""}

        if travel_method == "car" and not plate:
            result["valid"] = False
            result["message"] = "Placa do veículo é obrigatória para viagens de carro."
            return result

        if plate is not None and len(plate) > 7:
            result["valid"] = False
            result["message"] = "Placa do veículo deve ter no máximo 7 caracteres."

        return result

    @staticmethod
    def validate_user_form(form_data: Dict[str, Any]) -> Dict[str, dict]:
        """Validates all user form fields at once and returns validation results."""
        results = {}

        has_cpf = form_data.get("hasCpf") == "yes"
        has_special_needs = form_data.get("hasSpecialNeeds") == "yes"

        results["cpf"] = FrontendValidation.validate_cpf(form_data.get("cpf"), has_cpf)
        results["passport"] = FrontendValidation.validate_passport(
            form_data.get("passport_number"), has_cpf
        )
        results["special_needs"] = FrontendValidation.validate_special_needs_details(
            form_data.get("special_needs_details"), has_special_needs
        )

        return results

    @staticmethod
    def validate_pet_form(form_data: Dict[str, Any]) -> Dict[str, dict]:
        """Validates all pet form fields at once and returns validation results."""
        results = {}

        results["microchip"] = FrontendValidation.validate_microchip(
            form_data.get("microchip")
        )

        return results

    @staticmethod
    def validate_travel_form(form_data: Dict[str, Any]) -> Dict[str, dict]:
        """Validates all travel form fields at once and returns validation results."""
        results = {}

        travel_method = form_data.get("travelMethod")
        results["vehicle_plate"] = FrontendValidation.validate_vehicle_plate(
            form_data.get("vehiclePlate"), travel_method
        )

        return results
