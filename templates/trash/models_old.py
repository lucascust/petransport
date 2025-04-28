from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, constr, field_validator, ValidationInfo
import re
import os
import uuid


class FileType(Enum):
    """Tipos de arquivo suportados."""

    IMAGE = "image"
    PDF = "pdf"


def create_file_document(
    file_path: str, file_type: Optional[FileType] = None
) -> "FileDocument":
    """
    Cria uma instância de FileDocument a partir do caminho do arquivo.

    Args:
        file_path: Caminho do arquivo
        file_type: Tipo do arquivo (opcional, será inferido pela extensão se não fornecido)

    Returns:
        FileDocument: Objeto FileDocument preenchido
    """
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

    # Gerar ID único
    file_id = str(uuid.uuid4())

    # Obter tamanho do arquivo (se existir)
    size = 0
    try:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
    except:
        pass  # Ignora erros ao obter tamanho do arquivo

    # Criar e retornar o documento
    return FileDocument(
        file_id=file_id,
        filename=filename,
        path=file_path,
        file_type=file_type,
        size=size,
        uploaded_at=datetime.now(),
    )


class FileDocument(BaseModel):
    """Modelo para arquivos (imagens e PDFs)."""

    file_id: str = Field(description="Identificador único do arquivo")
    filename: str = Field(description="Nome original do arquivo")
    path: str = Field(description="Caminho de armazenamento do arquivo")
    file_type: FileType = Field(description="Tipo do arquivo (imagem ou PDF)")
    size: int = Field(description="Tamanho do arquivo em bytes")
    uploaded_at: datetime = Field(
        default_factory=datetime.now, description="Data de upload"
    )

    @field_validator("file_type")
    def validate_file_type(cls, v):
        """Valida o tipo de arquivo."""
        if v not in [FileType.IMAGE, FileType.PDF]:
            raise ValueError("Tipo de arquivo deve ser imagem ou PDF.")
        return v


class Address(BaseModel):
    """Modelo para endereço."""

    lat: Optional[str] = None
    lng: Optional[str] = None
    formatted: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

    @classmethod
    def from_dict(cls, address_data: Dict[str, Any], prefix: str = "") -> "Address":
        """
        Cria um endereço a partir de um dicionário.

        Args:
            address_data: Dicionário com dados do endereço
            prefix: Prefixo dos campos (ex: 'endereco_residential_', 'endereco_delivery_')

        Returns:
            Address: Objeto Address preenchido
        """
        if not address_data:
            return None

        field_map = {
            "lat": f"{prefix}lat",
            "lng": f"{prefix}lng",
            "formatted": f"{prefix}formatted",
            "city": f"{prefix}cidade",
            "state": f"{prefix}estado",
            "zip_code": f"{prefix}cep",
        }

        address_kwargs = {}
        for attr, key in field_map.items():
            if key in address_data:
                address_kwargs[attr] = address_data[key]

        return cls(**address_kwargs)


class Pet(BaseModel):
    """Modelo para pet."""

    name: str
    species: str
    breed: str
    gender: str
    birth_date: datetime
    microchip: Optional[str] = None
    weight: Optional[str] = None
    photo: Optional[FileDocument] = None

    @field_validator("microchip")
    def validate_microchip(cls, v, info: ValidationInfo):
        """Valida o formato do microchip."""
        if v is not None and not re.match(r"^[0-9]{1,15}$", v.replace(".", "")):
            raise ValueError("Microchip deve conter até 15 dígitos.")
        return v

    @field_validator("gender")
    def validate_gender(cls, v, info: ValidationInfo):
        """Valida o gênero do pet."""
        if v not in ["male", "female"]:
            raise ValueError('Gênero deve ser "male" ou "female".')
        return v

    @field_validator("species")
    def validate_species(cls, v, info: ValidationInfo):
        """Valida a espécie do pet."""
        valid_species = ["canine", "feline", "bird", "rodent", "other"]
        if v not in valid_species:
            raise ValueError(
                f'Espécie deve ser uma das seguintes: {", ".join(valid_species)}.'
            )
        return v

    @classmethod
    def from_dict(cls, pet_data: Dict[str, Any]) -> "Pet":
        """
        Cria um pet a partir de um dicionário.

        Args:
            pet_data: Dicionário com dados do pet

        Returns:
            Pet: Objeto Pet preenchido
        """
        # Converte a data de nascimento para datetime
        birth_date = datetime.strptime(pet_data.get("birth_date"), "%d/%m/%Y")

        # Converter foto para FileDocument se presente
        photo = None
        if pet_data.get("photo"):
            photo = create_file_document(pet_data.get("photo"))

        return cls(
            name=pet_data.get("name"),
            species=pet_data.get("species"),
            breed=pet_data.get("breed"),
            gender=pet_data.get("gender"),
            birth_date=birth_date,
            microchip=pet_data.get("microchip"),
            weight=pet_data.get("weight"),
            photo=photo,
        )

    def update_photo(self, photo_path: str) -> None:
        """
        Atualiza a foto do pet.

        Args:
            photo_path: Caminho da nova foto
        """
        self.photo = create_file_document(photo_path, FileType.IMAGE)


class PetDocument(BaseModel):
    """Modelo para documentos de pets."""

    vaccinationCard: Optional[FileDocument] = None
    microchipCertificate: Optional[FileDocument] = None
    rabiesSerologyReport: Optional[FileDocument] = None
    leishmaniasisSerologyReport: Optional[FileDocument] = None
    importPermit: Optional[FileDocument] = None
    petPassport: Optional[FileDocument] = None
    cvi: Optional[FileDocument] = None
    importAuthorization: Optional[FileDocument] = None
    arrivalNotice: Optional[FileDocument] = None
    endorsedCvi: Optional[FileDocument] = None
    awbCargo: Optional[FileDocument] = None
    petFacilities: Optional[FileDocument] = None
    otherPetDocuments: Optional[List[FileDocument]] = None

    @classmethod
    def from_form_data(cls, form_data: Dict[str, Any]) -> "PetDocument":
        """
        Cria um objeto PetDocument a partir de dados de formulário.

        Args:
            form_data: Dicionário com caminhos de arquivos

        Returns:
            PetDocument: Objeto PetDocument preenchido
        """
        document_fields = {
            "vaccinationCard",
            "microchipCertificate",
            "rabiesSerologyReport",
            "leishmaniasisSerologyReport",
            "importPermit",
            "petPassport",
            "cvi",
            "importAuthorization",
            "arrivalNotice",
            "endorsedCvi",
            "awbCargo",
            "petFacilities",
        }

        document_kwargs = {}

        # Processa os campos individuais
        for field in document_fields:
            if field in form_data and form_data[field]:
                document_kwargs[field] = create_file_document(form_data[field])

        # Processa a lista de outros documentos
        if "otherPetDocuments" in form_data and form_data["otherPetDocuments"]:
            document_kwargs["otherPetDocuments"] = [
                create_file_document(doc) for doc in form_data["otherPetDocuments"]
            ]

        return cls(**document_kwargs)


class HumanDocument(BaseModel):
    """Modelo para documentos humanos."""

    identityDocument: Optional[FileDocument] = None
    cviIssuanceAuthorization: Optional[FileDocument] = None
    passport: Optional[FileDocument] = None
    travelTicket: Optional[FileDocument] = None
    travelAuthorization: Optional[FileDocument] = None
    carDocument: Optional[FileDocument] = None
    addressProof: Optional[FileDocument] = None
    otherHumanDocuments: Optional[List[FileDocument]] = None

    @classmethod
    def from_form_data(cls, form_data: Dict[str, Any]) -> "HumanDocument":
        """
        Cria um objeto HumanDocument a partir de dados de formulário.

        Args:
            form_data: Dicionário com caminhos de arquivos

        Returns:
            HumanDocument: Objeto HumanDocument preenchido
        """
        document_fields = {
            "identityDocument",
            "cviIssuanceAuthorization",
            "passport",
            "travelTicket",
            "travelAuthorization",
            "carDocument",
            "addressProof",
        }

        document_kwargs = {}

        # Processa os campos individuais
        for field in document_fields:
            if field in form_data and form_data[field]:
                document_kwargs[field] = create_file_document(form_data[field])

        # Processa a lista de outros documentos
        if "otherHumanDocuments" in form_data and form_data["otherHumanDocuments"]:
            document_kwargs["otherHumanDocuments"] = [
                create_file_document(doc) for doc in form_data["otherHumanDocuments"]
            ]

        return cls(**document_kwargs)


class Travel(BaseModel):
    """Modelo para viagens na coleção independente."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    origin: str
    destination: str
    travelTicketFile: Optional[FileDocument] = None
    travelTicketDate: Optional[datetime] = None
    estimatedDate: Optional[str] = None
    travelingPets: List[str] = []
    destinationAddress: Optional[Address] = None
    travelMethod: str
    borderCity: Optional[str] = None
    vehiclePlate: Optional[str] = None
    status: str = "upcoming"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    required_documents: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "pet_docs": ["vaccinationCard", "microchipCertificate"],
            "human_docs": ["passport", "identityDocument"],
        }
    )
    # Novo campo para armazenar documentos de pet
    pet_documents: Dict[str, Dict[str, FileDocument]] = Field(
        default_factory=dict
    )  # {pet_id: {doc_type: FileDocument}}
    # Novo campo para armazenar documentos humanos
    human_documents: Dict[str, FileDocument] = Field(
        default_factory=dict
    )  # {doc_type: FileDocument}
    history: List[Dict[str, Any]] = Field(
        default_factory=lambda: [
            {
                "type": "status_change",
                "description": "Viagem criada",
                "date": datetime.now(),
            }
        ]
    )

    @field_validator("travelMethod")
    def validate_travel_method(cls, v, info: ValidationInfo):
        """Valida o método de viagem."""
        valid_methods = ["plane", "bus", "car", "petTransport", "other"]
        if v not in valid_methods:
            raise ValueError(
                f'Método de viagem deve ser um dos seguintes: {", ".join(valid_methods)}.'
            )
        return v

    @field_validator("vehiclePlate")
    def validate_vehicle_plate(cls, v, info: ValidationInfo):
        """Valida a placa do veículo quando o método de viagem é carro."""
        if info.data.get("travelMethod") == "car" and not v:
            raise ValueError(
                "Placa do veículo é obrigatória quando o método de viagem é carro."
            )

        if v is not None and len(v) > 7:
            raise ValueError("Placa do veículo deve ter no máximo 7 caracteres.")
        return v

    @field_validator("status")
    def validate_status(cls, v, info: ValidationInfo):
        """Valida o status da viagem."""
        valid_status = ["upcoming", "in_progress", "completed", "cancelled"]
        if v not in valid_status:
            raise ValueError(
                f'Status deve ser um dos seguintes: {", ".join(valid_status)}.'
            )
        return v

    @classmethod
    def from_travel_data(
        cls, travel_data: Dict[str, Any], user_id: str, username: str
    ) -> "Travel":
        """
        Cria um objeto Travel a partir de dados de viagem e informações do usuário.

        Args:
            travel_data: Dicionário com dados da viagem do formato antigo
            user_id: ID do usuário
            username: Nome de usuário

        Returns:
            Travel: Objeto Travel preenchido
        """
        # Preserva o ID existente se estiver presente
        travel_id = travel_data.get("id", str(uuid.uuid4()))

        # Cria um novo objeto Travel com os dados existentes
        return cls(
            id=travel_id,
            user_id=user_id,
            username=username,
            origin=travel_data.get("origin", ""),
            destination=travel_data.get("destination", ""),
            travelTicketFile=travel_data.get("travelTicketFile"),
            travelTicketDate=travel_data.get("travelTicketDate"),
            estimatedDate=travel_data.get("estimatedDate"),
            travelingPets=travel_data.get("travelingPets", []),
            destinationAddress=travel_data.get("destinationAddress"),
            travelMethod=travel_data.get("travelMethod", "other"),
            borderCity=travel_data.get("borderCity"),
            vehiclePlate=travel_data.get("vehiclePlate"),
            status=travel_data.get("status", "upcoming"),
            created_at=travel_data.get("created_at", datetime.now()),
            updated_at=travel_data.get("updated_at"),
            required_documents=travel_data.get(
                "required_documents",
                {
                    "pet_docs": ["vaccinationCard", "microchipCertificate"],
                    "human_docs": ["passport", "identityDocument"],
                },
            ),
            pet_documents=travel_data.get("pet_documents", {}),
            human_documents=travel_data.get("human_documents", {}),
            history=travel_data.get(
                "history",
                [
                    {
                        "type": "status_change",
                        "description": "Viagem criada",
                        "date": datetime.now(),
                    }
                ],
            ),
        )

    @classmethod
    def from_form_data(
        cls, form_data: Dict[str, Any], user_id: str, username: str
    ) -> "Travel":
        """
        Cria um objeto Travel a partir de dados de formulário.

        Args:
            form_data: Dicionário com dados de viagem do formulário
            user_id: ID do usuário
            username: Nome de usuário

        Returns:
            Travel: Objeto Travel preenchido
        """
        # Converte a data/hora da passagem para datetime
        ticket_date = None
        if form_data.get("travelTicketDate"):
            try:
                ticket_date = datetime.strptime(
                    form_data["travelTicketDate"], "%d/%m/%Y %H:%M"
                )
            except:
                # Tenta formato sem hora
                try:
                    ticket_date = datetime.strptime(
                        form_data["travelTicketDate"], "%d/%m/%Y"
                    )
                except:
                    pass

        # Processa o endereço de destino
        dest_addr = None
        if form_data.get("destinationAddress"):
            dest_addr = Address(formatted=form_data.get("destinationAddress"))
        elif form_data.get("destinationAddress_formatted"):
            dest_addr = Address.from_dict(form_data["destinationAddress"])

        # Processa o arquivo da passagem
        ticket_file = None
        if (
            "travelTicketFile" in form_data
            and hasattr(form_data["travelTicketFile"], "filename")
            and form_data["travelTicketFile"].filename
        ):
            file = form_data["travelTicketFile"]
            filename = os.path.basename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"{timestamp}_{filename}"

            ticket_file = FileDocument(
                file_id=str(uuid.uuid4()),
                filename=filename,
                path=file_path,
                file_type=(
                    FileType.PDF
                    if filename.lower().endswith(".pdf")
                    else FileType.IMAGE
                ),
                size=getattr(file, "content_length", 0),
                uploaded_at=datetime.now(),
            )
        elif form_data.get("travelTicketFile"):
            # Handle case where it's a simple file path (used in tests)
            ticket_file = create_file_document(form_data["travelTicketFile"])

        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            username=username,
            origin=form_data["origin"],
            destination=form_data["destination"],
            travelTicketFile=ticket_file,
            travelTicketDate=ticket_date,
            estimatedDate=form_data.get("estimatedDate"),
            travelingPets=(
                form_data.getlist("travelingPets")
                if hasattr(form_data, "getlist")
                else form_data.get("travelingPets", [])
            ),
            destinationAddress=dest_addr,
            travelMethod=form_data["travelMethod"],
            borderCity=form_data.get("borderCity"),
            vehiclePlate=form_data.get("vehiclePlate"),
            created_at=datetime.now(),
            status="upcoming",
            history=[
                {
                    "type": "status_change",
                    "description": "Viagem criada",
                    "date": datetime.now(),
                }
            ],
        )

    def add_pet_document(
        self, pet_id: str, doc_type: str, file_doc: FileDocument
    ) -> None:
        """
        Adiciona ou atualiza um documento de pet à viagem.

        Args:
            pet_id: ID do pet
            doc_type: Tipo de documento
            file_doc: Objeto FileDocument
        """
        if pet_id not in self.pet_documents:
            self.pet_documents[pet_id] = {}

        self.pet_documents[pet_id][doc_type] = file_doc

        # Adiciona um evento ao histórico
        self.history.append(
            {
                "type": "document_upload",
                "description": f"Documento '{doc_type}' enviado para o pet",
                "date": datetime.now(),
            }
        )

        # Atualiza a data de modificação
        self.updated_at = datetime.now()

    def add_human_document(self, doc_type: str, file_doc: FileDocument) -> None:
        """
        Adiciona ou atualiza um documento humano à viagem.

        Args:
            doc_type: Tipo de documento
            file_doc: Objeto FileDocument
        """
        self.human_documents[doc_type] = file_doc

        # Adiciona um evento ao histórico
        self.history.append(
            {
                "type": "document_upload",
                "description": f"Documento '{doc_type}' do responsável enviado",
                "date": datetime.now(),
            }
        )

        # Atualiza a data de modificação
        self.updated_at = datetime.now()

    def get_pet_document(self, pet_id: str, doc_type: str) -> Optional[FileDocument]:
        """
        Obtém um documento de pet específico.

        Args:
            pet_id: ID do pet
            doc_type: Tipo de documento

        Returns:
            FileDocument ou None se não existir
        """
        if pet_id in self.pet_documents and doc_type in self.pet_documents[pet_id]:
            return self.pet_documents[pet_id][doc_type]
        return None

    def get_human_document(self, doc_type: str) -> Optional[FileDocument]:
        """
        Obtém um documento humano específico.

        Args:
            doc_type: Tipo de documento

        Returns:
            FileDocument ou None se não existir
        """
        return self.human_documents.get(doc_type)


class User(BaseModel):
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
    residential_address: Address
    delivery_address: Optional[Address] = None
    registration_date: datetime = Field(default_factory=datetime.now)
    last_access: datetime = Field(default_factory=datetime.now)
    allowed_pages: List[str] = Field(
        default_factory=lambda: ["page1", "page2", "page3", "page4"]
    )
    pets: List[Pet] = []
    # Campos para documentos
    pet_documents: Dict[str, Dict[str, FileDocument]] = Field(default_factory=dict)
    human_documents: Dict[str, FileDocument] = Field(default_factory=dict)
    travel_ids: List[str] = Field(default_factory=list)  # Lista de IDs de viagens

    @field_validator("cpf")
    def validate_cpf(cls, v, info: ValidationInfo):
        """Valida o CPF se has_cpf for True."""
        if info.data.get("has_cpf") and not v:
            raise ValueError("CPF é obrigatório quando has_cpf é True.")

        if v is not None:
            # Remove pontuação
            cpf_clean = v.replace(".", "").replace("-", "")
            if not re.match(r"^\d{11}$", cpf_clean):
                raise ValueError("CPF deve conter 11 dígitos.")
        return v

    @field_validator("passport_number")
    def validate_passport(cls, v, info: ValidationInfo):
        """Valida o passaporte se has_cpf for False."""
        if not info.data.get("has_cpf") and not v:
            raise ValueError(
                "Número do passaporte é obrigatório quando has_cpf é False."
            )

        if v is not None and not re.match(r"^[A-Z0-9]{8,9}$", v):
            raise ValueError(
                "Passaporte deve conter 8-9 caracteres alfanuméricos (A-Z, 0-9)."
            )
        return v

    @field_validator("special_needs_details")
    def validate_special_needs_details(cls, v, info: ValidationInfo):
        """Valida os detalhes de necessidades especiais se has_special_needs for True."""
        if info.data.get("has_special_needs") and not v:
            raise ValueError(
                "Detalhes de necessidades especiais são obrigatórios quando has_special_needs é True."
            )
        return v

    @classmethod
    def from_form_data(cls, form_data: Dict[str, Any]) -> "User":
        """
        Cria um usuário a partir de dados de formulário.

        Args:
            form_data: Dicionário com dados do usuário

        Returns:
            User: Objeto User preenchido
        """
        # Processa os endereços
        residential_addr = Address.from_dict(
            form_data["residential_address"], prefix="endereco_residential_"
        )

        delivery_addr = None
        if form_data.get("delivery_address"):
            delivery_addr = Address.from_dict(
                form_data["delivery_address"], prefix="endereco_delivery_"
            )

        # Processa os pets
        pets_list = []
        for pet_data in form_data.get("pets", []):
            pets_list.append(Pet.from_dict(pet_data))

        # Retorna o usuário completo
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
            residential_address=residential_addr,
            delivery_address=delivery_addr,
            registration_date=datetime.now(),
            last_access=datetime.now(),
            pets=pets_list,
            pet_documents={},  # Inicializa vazio, será preenchido posteriormente
            human_documents={},  # Inicializa vazio, será preenchido posteriormente
            travel_ids=[],  # Inicializa vazio, será preenchido posteriormente
        )


class AdminUserView(BaseModel):
    """Modelo para visualização de usuário no admin."""

    owner_name: str
    username: str
    registration_date: datetime
    last_access: datetime
    pets: List[Pet] = []
