from typing import Dict, Any, Optional, List, Callable, Union
import json
import os
from pathlib import Path
import logging


class TranslationManager:
    """
    Gerencia traduções para o sistema, carregando de arquivos JSON.
    Permite acessar traduções para modelos, formulários e mensagens.
    """

    def __init__(self, translations_dir: str = "translations"):
        """
        Inicializa o gerenciador de traduções.

        Args:
            translations_dir: Diretório onde os arquivos de tradução estão localizados
        """
        self.translations_dir = translations_dir
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.available_languages = []
        self.default_lang = "pt"
        self._load_translations()

    def _load_translations(self) -> None:
        """Carrega todas as traduções disponíveis dos arquivos JSON."""
        base_dir = Path(self.translations_dir)

        # Cria o diretório de traduções se não existir
        if not base_dir.exists():
            os.makedirs(base_dir, exist_ok=True)

            # Se o diretório precisou ser criado, gere arquivos padrão
            self._create_default_translations()

        # Carrega cada arquivo de tradução (.json)
        for lang_file in base_dir.glob("*.json"):
            lang_code = lang_file.stem  # Extrai o código do idioma do nome do arquivo

            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self.translations[lang_code] = json.load(f)
                    self.available_languages.append(lang_code)
            except Exception as e:
                print(f"Erro ao carregar traduções para {lang_code}: {str(e)}")
                # Cria uma tradução vazia para esse idioma
                self.translations[lang_code] = {}

        # Se nenhum arquivo de tradução foi encontrado, criar o padrão
        if not self.translations:
            self._create_default_translations()
            self._load_translations()  # Recarrega após criar

    def _create_default_translations(self) -> None:
        """Cria arquivos de tradução padrão se não existirem."""
        base_dir = Path(self.translations_dir)

        # Estrutura básica de traduções
        default_translations = {
            "pt": self._get_default_pt_translations(),
            "en": self._get_default_en_translations(),
        }

        # Cria um arquivo para cada idioma
        for lang, translations in default_translations.items():
            file_path = base_dir / f"{lang}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)

    def _get_default_pt_translations(self) -> Dict[str, Any]:
        """Retorna traduções padrão em português."""
        return {
            "models": {
                "Pet": {
                    "fields": {
                        "name": "Nome do Pet",
                        "species": "Espécie",
                        "breed": "Raça",
                        "gender": "Sexo",
                        "birth_date": "Data de Nascimento",
                        "microchip": "Código do Microchip",
                        "weight": "Peso do Animal (kg)",
                        "photo": "Foto do Pet",
                    },
                    "enums": {
                        "species": {
                            "canine": "Cachorro",
                            "feline": "Gato",
                            "bird": "Pássaro",
                            "rodent": "Roedor",
                            "other": "Outros",
                        },
                        "gender": {"male": "Macho", "female": "Fêmea"},
                    },
                    "validations": {
                        "microchip_format": "Microchip deve conter até 15 dígitos.",
                        "gender_invalid": 'Gênero deve ser "macho" ou "fêmea".',
                        "species_invalid": "Espécie deve ser uma das seguintes: Cachorro, Gato, Pássaro, Roedor ou Outros.",
                    },
                },
                "User": {
                    "fields": {
                        "username": "Nome de Usuário",
                        "owner_name": "Nome Completo",
                        "email": "Email",
                        "contact_number": "Número para Contato",
                        "has_cpf": "Possui CPF?",
                        "cpf": "CPF",
                        "passport_number": "Número do Passaporte",
                        "has_special_needs": "Possui Necessidades Especiais?",
                        "special_needs_details": "Detalhes das Necessidades Especiais",
                        "how_did_you_know": "Como Conheceu Nosso Serviço",
                        "residential_address": "Endereço Residencial",
                        "delivery_address": "Endereço de Entrega",
                        "registration_date": "Data de Cadastro",
                        "last_access": "Último Acesso",
                        "allowed_pages": "Páginas Permitidas",
                        "pets": "Pets",
                    },
                    "enums": {
                        "how_did_you_know": {
                            "instagram": "Instagram",
                            "facebook": "Facebook",
                            "google": "Google",
                            "youtube": "Youtube",
                            "recommendation": "Indicação",
                            "other": "Outro",
                        },
                        "boolean": {"yes": "Sim", "no": "Não"},
                    },
                    "validations": {
                        "cpf_required": "CPF é obrigatório quando possui CPF é Sim.",
                        "cpf_format": "CPF deve conter 11 dígitos.",
                        "passport_required": "Número do passaporte é obrigatório quando possui CPF é Não.",
                        "passport_format": "Passaporte deve conter 8-9 caracteres alfanuméricos (A-Z, 0-9).",
                        "special_needs_details_required": "Detalhes de necessidades especiais são obrigatórios quando possui necessidades especiais é Sim.",
                    },
                },
                "Address": {
                    "fields": {
                        "lat": "Latitude",
                        "lng": "Longitude",
                        "formatted": "Endereço Formatado",
                        "city": "Cidade",
                        "state": "Estado",
                        "zip_code": "CEP",
                    }
                },
                "PetDocument": {
                    "fields": {
                        "vaccinationCard": "Carteira de Vacinação",
                        "microchipCertificate": "Certificado Microchip",
                        "rabiesSerologyReport": "Laudo Sorologia - Raiva",
                        "leishmaniasisSerologyReport": "Laudo Sorologia - Leishmaniose",
                        "importPermit": "Import Permit",
                        "petPassport": "Passaporte do Pet",
                        "cvi": "CVI",
                        "exportAuthorization": "Export Authorization",
                        "arrivalNotice": "Aviso de Chegada (Só PDF)",
                        "endorsedCvi": "CVI Chancelado",
                        "awbCargo": "AWB Cargo",
                        "petFacilities": "Pet Facilities",
                        "otherPetDocuments": "Outros",
                    },
                    "descriptions": {
                        "vaccinationCard": "Documento que comprova a vacinação do animal contendo informações como as vacinas aplicadas, datas e veterinário responsável.",
                        "microchipCertificate": "Declaração que comprova o implante do microchip de identificação no pet, contendo o número e informações sobre a aplicação.",
                        "rabiesSerologyReport": "Exame laboratorial que atesta a presença de anticorpos contra o vírus da raiva, comumente exigido para viagens internacionais.",
                        "leishmaniasisSerologyReport": "Exame que demonstra a não infecção por leishmaniose ou a baixa incidência, dependendo das exigências do país de destino.",
                        "importPermit": "Autorização oficial emitida pelo país de destino permitindo a entrada do animal.",
                        "petPassport": "Documento internacional que registra a identidade, vacinas e histórico de saúde do animal para viagens ao exterior.",
                        "cvi": "Certificado Veterinário Internacional emitido pelo veterinário oficial do país de origem, atestando a saúde do pet.",
                        "exportAuthorization": "Documento que comprova permissão oficial para exportar o animal, emitido pela autoridade competente.",
                        "arrivalNotice": "Notificação às autoridades sobre a chegada do pet, obrigatória em alguns destinos.",
                        "endorsedCvi": "Certificado Veterinário Internacional que recebeu aval e endosso das autoridades sanitárias competentes.",
                        "awbCargo": "Air Waybill: documento de embarque aéreo que acompanha cargas, incluindo animais, contendo detalhes do transporte.",
                        "petFacilities": "Documento que descreve as instalações ou acomodações previstas para o pet antes/durante a viagem.",
                        "otherPetDocuments": "Qualquer outro documento relevante que não se enquadre nas categorias acima.",
                    },
                },
                "HumanDocument": {
                    "fields": {
                        "identityDocument": "Documento com Foto",
                        "cviIssuanceAuthorization": "Autorização de Emissão do CVI",
                        "passport": "Passaporte",
                        "travelTicket": "Passagem",
                        "travelAuthorization": "Autorização de Viagem",
                        "carDocument": "Documento do Carro",
                        "addressProof": "Comprovante de Endereço",
                        "otherHumanDocuments": "Outros",
                    },
                    "descriptions": {
                        "identityDocument": "Documento oficial de identificação com foto (RG, CNH ou similar).",
                        "cviIssuanceAuthorization": "Termo que autoriza a emissão do Certificado Veterinário Internacional em nome do proprietário ou tutor.",
                        "passport": "Passaporte do viajante, exigido para viagens internacionais.",
                        "travelTicket": "Passagem aérea, rodoviária ou ferroviária do passageiro.",
                        "travelAuthorization": "Autorização de viagem, geralmente exigida quando há menores desacompanhados ou exigências legais específicas.",
                        "carDocument": "Documento do veículo, caso seja parte da viagem (ex.: CRLV no Brasil).",
                        "addressProof": "Documento que comprova o endereço residencial (conta de luz, água, etc.).",
                        "otherHumanDocuments": "Qualquer outro documento que não se enquadre nas categorias acima.",
                    },
                },
                "Travel": {
                    "fields": {
                        "origin": "Origem",
                        "destination": "Destino",
                        "travelTicketFile": "Passagem",
                        "travelTicketDate": "Data da passagem",
                        "estimatedDate": "Data estimada",
                        "travelingPets": "Pets viajantes",
                        "destinationAddress": "Endereço de destino",
                        "travelMethod": "Método da viagem",
                        "borderCity": "Cidade de Fronteira",
                        "vehiclePlate": "Placa do Veículo",
                    },
                    "descriptions": {
                        "origin": "Cidade e país de onde inicia a viagem, seguindo a padronização das companhias aéreas.",
                        "destination": "Cidade e país de destino, seguindo a padronização das companhias aéreas.",
                        "travelTicketFile": "Arquivo contendo a passagem (pode ser PDF ou imagem).",
                        "travelTicketDate": "Data e hora exatos referentes à passagem adquirida.",
                        "estimatedDate": "Data aproximada ou previsão de embarque (ano e mês).",
                        "travelingPets": "Identificadores dos pets que irão viajar (pode ser um índice ou ID gerado internamente).",
                        "destinationAddress": "Endereço completo onde o pet/pessoa irá se hospedar ou residir no destino.",
                        "travelMethod": "Forma de transporte utilizada (ex.: Avião, Ônibus, Veículo Próprio, Petransport).",
                        "borderCity": "Cidade que faz fronteira em viagens terrestres ou mistas, se aplicável.",
                        "vehiclePlate": "Placa do veículo usado na viagem (até 7 dígitos).",
                    },
                    "enums": {
                        "travelMethod": {
                            "plane": "Avião",
                            "bus": "Ônibus",
                            "car": "Veículo Próprio",
                            "petTransport": "Petransport",
                            "other": "Outro",
                        }
                    },
                },
            },
            "ui": {
                "buttons": {
                    "save": "Salvar",
                    "cancel": "Cancelar",
                    "add": "Adicionar",
                    "remove": "Remover",
                    "edit": "Editar",
                    "update": "Atualizar",
                    "delete": "Excluir",
                    "search": "Buscar",
                    "filter": "Filtrar",
                    "close": "Fechar",
                    "back": "Voltar",
                    "next": "Próximo",
                },
                "titles": {
                    "pet_registration": "Cadastro de Pet",
                    "user_registration": "Cadastro de Responsável",
                    "pet_list": "Lista de Pets",
                    "user_list": "Lista de Usuários",
                    "pet_details": "Detalhes do Pet",
                    "user_details": "Detalhes do Usuário",
                },
                "messages": {
                    "success": {
                        "user_created": "Usuário criado com sucesso!",
                        "user_updated": "Usuário atualizado com sucesso!",
                        "pet_created": "Pet adicionado com sucesso!",
                        "pet_updated": "Pet atualizado com sucesso!",
                        "pet_photo_updated": "Foto do pet atualizada com sucesso!",
                    },
                    "errors": {
                        "general": "Ocorreu um erro. Por favor, tente novamente.",
                        "user_not_found": "Usuário não encontrado.",
                        "pet_not_found": "Pet não encontrado.",
                        "form_invalid": "Por favor, corrija os erros no formulário.",
                        "file_size": "O arquivo é muito grande. Tamanho máximo: 5MB.",
                        "file_type": "Tipo de arquivo não permitido. Formatos aceitos: JPG, PNG, GIF.",
                    },
                    "confirmations": {
                        "delete_pet": "Tem certeza que deseja excluir este pet?",
                        "delete_user": "Tem certeza que deseja excluir este usuário?",
                    },
                },
                "placeholders": {
                    "search_user": "Buscar por nome, email ou username...",
                    "search_pet": "Buscar por nome do pet...",
                    "select_species": "Selecione a espécie",
                    "select_gender": "Selecione o sexo",
                    "email": "seu.email@exemplo.com",
                    "phone": "+55 11 99999-9999",
                    "date": "DD/MM/AAAA",
                },
                "tooltips": {
                    "add_pet": "Adicionar um novo pet",
                    "edit_pet": "Editar informações do pet",
                    "update_photo": "Atualizar foto do pet",
                    "required_field": "Este campo é obrigatório",
                },
                "help_texts": {
                    "cpf": "Digite apenas números (11 dígitos)",
                    "passport": "Letras maiúsculas e números (8-9 caracteres)",
                    "microchip": "Máximo 15 dígitos",
                    "photo": "Formatos aceitos: JPG, PNG, GIF. Tamanho máximo: 5MB",
                },
            },
        }

    def _get_default_en_translations(self) -> Dict[str, Any]:
        """Retorna traduções padrão em inglês."""
        return {
            "models": {
                "Pet": {
                    "fields": {
                        "name": "Pet Name",
                        "species": "Species",
                        "breed": "Breed",
                        "gender": "Gender",
                        "birth_date": "Birth Date",
                        "microchip": "Microchip Code",
                        "weight": "Weight (kg)",
                        "photo": "Pet Photo",
                    },
                    "enums": {
                        "species": {
                            "canine": "Dog",
                            "feline": "Cat",
                            "bird": "Bird",
                            "rodent": "Rodent",
                            "other": "Other",
                        },
                        "gender": {"male": "Male", "female": "Female"},
                    },
                    "validations": {
                        "microchip_format": "Microchip must contain up to 15 digits.",
                        "gender_invalid": 'Gender must be "male" or "female".',
                        "species_invalid": "Species must be one of the following: Dog, Cat, Bird, Rodent, or Other.",
                    },
                },
                "User": {
                    "fields": {
                        "username": "Username",
                        "owner_name": "Full Name",
                        "email": "Email",
                        "contact_number": "Contact Number",
                        "has_cpf": "Has CPF?",
                        "cpf": "CPF",
                        "passport_number": "Passport Number",
                        "has_special_needs": "Has Special Needs?",
                        "special_needs_details": "Special Needs Details",
                        "how_did_you_know": "How Did You Hear About Us",
                        "residential_address": "Residential Address",
                        "delivery_address": "Delivery Address",
                        "registration_date": "Registration Date",
                        "last_access": "Last Access",
                        "allowed_pages": "Allowed Pages",
                        "pets": "Pets",
                    },
                    "enums": {
                        "how_did_you_know": {
                            "instagram": "Instagram",
                            "facebook": "Facebook",
                            "google": "Google",
                            "youtube": "Youtube",
                            "recommendation": "Recommendation",
                            "other": "Other",
                        },
                        "boolean": {"yes": "Yes", "no": "No"},
                    },
                    "validations": {
                        "cpf_required": "CPF is required when Has CPF is Yes.",
                        "cpf_format": "CPF must contain 11 digits.",
                        "passport_required": "Passport number is required when Has CPF is No.",
                        "passport_format": "Passport must contain 8-9 alphanumeric characters (A-Z, 0-9).",
                        "special_needs_details_required": "Special needs details are required when Has Special Needs is Yes.",
                    },
                },
                "Address": {
                    "fields": {
                        "lat": "Latitude",
                        "lng": "Longitude",
                        "formatted": "Formatted Address",
                        "city": "City",
                        "state": "State",
                        "zip_code": "ZIP Code",
                    }
                },
                "PetDocument": {
                    "fields": {
                        "vaccinationCard": "Vaccination Card",
                        "microchipCertificate": "Microchip Certificate",
                        "rabiesSerologyReport": "Rabies Serology Report",
                        "leishmaniasisSerologyReport": "Leishmaniasis Serology Report",
                        "importPermit": "Import Permit",
                        "petPassport": "Pet Passport",
                        "cvi": "CVI (International Veterinary Certificate)",
                        "exportAuthorization": "Export Authorization",
                        "arrivalNotice": "Arrival Notice (PDF Only)",
                        "endorsedCvi": "Endorsed CVI",
                        "awbCargo": "AWB Cargo",
                        "petFacilities": "Pet Facilities",
                        "otherPetDocuments": "Other",
                    },
                    "descriptions": {
                        "vaccinationCard": "Document that proves the animal's vaccination containing information such as vaccines administered, dates, and responsible veterinarian.",
                        "microchipCertificate": "Declaration that proves the implantation of the identification microchip in the pet, containing the number and information about the application.",
                        "rabiesSerologyReport": "Laboratory test that attests to the presence of antibodies against the rabies virus, commonly required for international travel.",
                        "leishmaniasisSerologyReport": "Test that demonstrates non-infection by leishmaniasis or low incidence, depending on the requirements of the destination country.",
                        "importPermit": "Official authorization issued by the destination country allowing the entry of the animal.",
                        "petPassport": "International document that records the identity, vaccines, and health history of the animal for travel abroad.",
                        "cvi": "International Veterinary Certificate issued by the official veterinarian of the country of origin, attesting to the health of the pet.",
                        "exportAuthorization": "Document that proves official permission to export the animal, issued by the competent authority.",
                        "arrivalNotice": "Notification to authorities about the arrival of the pet, mandatory in some destinations.",
                        "endorsedCvi": "International Veterinary Certificate that has received endorsement from the competent health authorities.",
                        "awbCargo": "Air Waybill: air shipping document that accompanies cargo, including animals, containing transport details.",
                        "petFacilities": "Document that describes the facilities or accommodations planned for the pet before/during travel.",
                        "otherPetDocuments": "Any other relevant document that does not fall into the above categories.",
                    },
                },
                "HumanDocument": {
                    "fields": {
                        "identityDocument": "Photo ID",
                        "cviIssuanceAuthorization": "Authorization to Issue CVI",
                        "passport": "Passport",
                        "travelTicket": "Travel Ticket",
                        "travelAuthorization": "Travel Authorization",
                        "carDocument": "Car Document",
                        "addressProof": "Proof of Address",
                        "otherHumanDocuments": "Other",
                    },
                    "descriptions": {
                        "identityDocument": "Official photo identification document (ID card, driver's license, or similar).",
                        "cviIssuanceAuthorization": "Term that authorizes the issuance of the International Veterinary Certificate on behalf of the owner or guardian.",
                        "passport": "Traveler's passport, required for international travel.",
                        "travelTicket": "Air, road, or rail passenger ticket.",
                        "travelAuthorization": "Travel authorization, usually required when there are unaccompanied minors or specific legal requirements.",
                        "carDocument": "Vehicle document, if it is part of the trip (e.g., registration certificate).",
                        "addressProof": "Document that proves residential address (utility bill, etc.).",
                        "otherHumanDocuments": "Any other document that does not fall into the above categories.",
                    },
                },
                "Travel": {
                    "fields": {
                        "origin": "Origin",
                        "destination": "Destination",
                        "travelTicketFile": "Travel Ticket (File)",
                        "travelTicketDate": "Travel Date and Time",
                        "estimatedDate": "Estimated Date (Month/Year)",
                        "travelingPets": "Traveling Pets",
                        "destinationAddress": "Destination Address",
                        "travelMethod": "Travel Method",
                        "borderCity": "Border City",
                        "vehiclePlate": "Vehicle Plate",
                    },
                    "descriptions": {
                        "origin": "City and country where the journey starts, following airline standardization.",
                        "destination": "City and country of destination, following airline standardization.",
                        "travelTicketFile": "File containing the ticket (can be PDF or image).",
                        "travelTicketDate": "Exact date and time referring to the purchased ticket.",
                        "estimatedDate": "Approximate date or forecast of boarding (year and month).",
                        "travelingPets": "Identifiers of pets that will travel (can be an index or ID generated internally).",
                        "destinationAddress": "Complete address where the pet/person will stay or reside at the destination.",
                        "travelMethod": "Form of transport used (e.g., Airplane, Bus, Own Vehicle, Petransport).",
                        "borderCity": "Border city in land or mixed travels, if applicable.",
                        "vehiclePlate": "License plate of the vehicle used in the trip (up to 7 digits).",
                    },
                    "enums": {
                        "travelMethod": {
                            "plane": "Airplane",
                            "bus": "Bus",
                            "car": "Own Vehicle",
                            "petTransport": "Petransport",
                            "other": "Other",
                        }
                    },
                },
            },
            "ui": {
                "buttons": {
                    "save": "Save",
                    "cancel": "Cancel",
                    "add": "Add",
                    "remove": "Remove",
                    "edit": "Edit",
                    "update": "Update",
                    "delete": "Delete",
                    "search": "Search",
                    "filter": "Filter",
                    "close": "Close",
                    "back": "Back",
                    "next": "Next",
                },
                "titles": {
                    "pet_registration": "Pet Registration",
                    "user_registration": "Owner Registration",
                    "pet_list": "Pet List",
                    "user_list": "User List",
                    "pet_details": "Pet Details",
                    "user_details": "User Details",
                },
                "messages": {
                    "success": {
                        "user_created": "User created successfully!",
                        "user_updated": "User updated successfully!",
                        "pet_created": "Pet added successfully!",
                        "pet_updated": "Pet updated successfully!",
                        "pet_photo_updated": "Pet photo updated successfully!",
                    },
                    "errors": {
                        "general": "An error occurred. Please try again.",
                        "user_not_found": "User not found.",
                        "pet_not_found": "Pet not found.",
                        "form_invalid": "Please correct the errors in the form.",
                        "file_size": "File is too large. Maximum size: 5MB.",
                        "file_type": "File type not allowed. Accepted formats: JPG, PNG, GIF.",
                    },
                    "confirmations": {
                        "delete_pet": "Are you sure you want to delete this pet?",
                        "delete_user": "Are you sure you want to delete this user?",
                    },
                },
                "placeholders": {
                    "search_user": "Search by name, email or username...",
                    "search_pet": "Search by pet name...",
                    "select_species": "Select species",
                    "select_gender": "Select gender",
                    "email": "your.email@example.com",
                    "phone": "+1 555-123-4567",
                    "date": "MM/DD/YYYY",
                },
                "tooltips": {
                    "add_pet": "Add a new pet",
                    "edit_pet": "Edit pet information",
                    "update_photo": "Update pet photo",
                    "required_field": "This field is required",
                },
                "help_texts": {
                    "cpf": "Enter numbers only (11 digits)",
                    "passport": "Uppercase letters and numbers (8-9 characters)",
                    "microchip": "Maximum 15 digits",
                    "photo": "Accepted formats: JPG, PNG, GIF. Maximum size: 5MB",
                },
            },
        }

    def get(
        self, key_path: str, lang: str = "pt", default: Optional[str] = None
    ) -> Any:
        """
        Obtém uma tradução baseada em um caminho de chaves e idioma.

        Args:
            key_path: Caminho para a tradução separado por pontos (ex: "models.Pet.fields.name")
            lang: Código do idioma desejado
            default: Valor padrão caso a tradução não seja encontrada

        Returns:
            A tradução ou o valor padrão
        """
        # Usa "pt" como fallback se o idioma solicitado não estiver disponível
        if lang not in self.translations:
            lang = "pt"

        # Navega pela estrutura de traduções seguindo o key_path
        parts = key_path.split(".")
        value = self.translations[lang]

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default or key_path.split(".")[-1]

        return value

    def get_field_label(self, model: str, field: str, lang: str = "pt") -> str:
        """
        Obtém o rótulo traduzido para um campo de modelo.

        Args:
            model: Nome do modelo (ex: "Pet", "User")
            field: Nome do campo
            lang: Código do idioma

        Returns:
            Rótulo traduzido do campo
        """
        return self.get(f"models.{model}.fields.{field}", lang, field)

    def get_enum_value(
        self, model: str, field: str, value: str, lang: str = "pt"
    ) -> str:
        """
        Obtém o valor traduzido de um enum.

        Args:
            model: Nome do modelo (ex: "Pet", "User")
            field: Nome do campo enum (ex: "species", "gender")
            value: Valor do enum (ex: "canine", "male")
            lang: Código do idioma

        Returns:
            Valor traduzido do enum
        """
        # Para campos que não são do tipo enum mas têm valores traduzíveis
        if field == "has_cpf" or field == "has_special_needs":
            return self.get(f"models.User.enums.boolean.{value}", lang, value)

        return self.get(f"models.{model}.enums.{field}.{value}", lang, value)

    def get_validation_message(
        self, model: str, validation_key: str, lang: str = "pt"
    ) -> str:
        """
        Obtém uma mensagem de validação traduzida.

        Args:
            model: Nome do modelo (ex: "Pet", "User")
            validation_key: Chave da validação (ex: "microchip_format")
            lang: Código do idioma

        Returns:
            Mensagem de validação traduzida
        """
        return self.get(
            f"models.{model}.validations.{validation_key}", lang, validation_key
        )

    def get_ui_text(
        self, category: str, key: str, subkey: Optional[str] = None, lang: str = "pt"
    ) -> str:
        """
        Obtém um texto de interface traduzido.

        Args:
            category: Categoria da UI (ex: "buttons", "messages")
            key: Chave da categoria (ex: "save", "success")
            subkey: Subchave opcional (ex: "user_created")
            lang: Código do idioma

        Returns:
            Texto de interface traduzido
        """
        # Verificação para "common" na ui
        if category == "common" and key in [
            "yes",
            "no",
            "select_option",
            "select_species",
            "select_gender",
        ]:
            return self.get(f"ui.common.{key}", lang, key)

        # Verificação para "languages"
        if category == "languages" and subkey is None:
            return self.get(f"languages.{key}.name", lang, key)

        # Verificação para "languages" com subkey
        if category == "languages" and subkey == "name":
            return self.get(f"languages.{key}.{subkey}", lang, key)

        # Verificação para "pages"
        if category == "pages" and key == "owner_registration" and subkey:
            return self.get(
                f"ui.pages.owner_registration.{subkey}", lang, subkey or key
            )

        # Caminho padrão
        path = f"ui.{category}.{key}"
        if subkey:
            path += f".{subkey}"
        return self.get(path, lang, subkey or key)

    def save_translations(self) -> None:
        """Salva as traduções em arquivos JSON."""
        base_dir = Path(self.translations_dir)

        for lang, translations in self.translations.items():
            file_path = base_dir / f"{lang}.json"
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(translations, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Erro ao salvar traduções para {lang}: {str(e)}")

    def add_language(self, lang_code: str, base_lang: str = "pt") -> None:
        """
        Adiciona um novo idioma copiando de um idioma base.

        Args:
            lang_code: Código do novo idioma
            base_lang: Idioma base para copiar as traduções
        """
        if lang_code in self.translations:
            print(f"Idioma {lang_code} já existe.")
            return

        if base_lang not in self.translations:
            print(f"Idioma base {base_lang} não encontrado.")
            return

        # Copia as traduções do idioma base
        self.translations[lang_code] = self.translations[base_lang].copy()
        self.available_languages.append(lang_code)

        # Salva o novo arquivo de traduções
        self.save_translations()
        print(f"Idioma {lang_code} adicionado com sucesso.")

    def update_translation(self, lang: str, key_path: str, value: str) -> bool:
        """
        Atualiza uma tradução específica.

        Args:
            lang: Código do idioma
            key_path: Caminho para a tradução separado por pontos
            value: Novo valor da tradução

        Returns:
            True se a atualização foi bem-sucedida, False caso contrário
        """
        if lang not in self.translations:
            print(f"Idioma {lang} não encontrado.")
            return False

        parts = key_path.split(".")
        current = self.translations[lang]

        # Navega pela estrutura até o penúltimo nível
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]

        # Atualiza o valor
        current[parts[-1]] = value

        # Salva as alterações
        self.save_translations()
        return True

    def get_supported_languages(self) -> List[str]:
        """Retorna a lista de idiomas suportados."""
        return list(self.translations.keys())

    def get_language_name(self, lang_code: str) -> str:
        """Retorna o nome do idioma para um código de idioma específico."""
        language_names = {
            "pt": "Português",
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
        }
        return language_names.get(lang_code, lang_code.upper())

    def get_flag_emoji(self, lang_code: str) -> str:
        """Retorna o emoji da bandeira para um código de idioma específico."""
        flag_emojis = {"pt": "🇧🇷", "en": "🇺🇸", "es": "🇪🇸", "fr": "🇫🇷", "de": "🇩🇪"}
        return flag_emojis.get(lang_code, lang_code.upper())


# Instância global para uso no aplicativo
translations = TranslationManager()


def get_supported_languages():
    """Retorna a lista de idiomas suportados."""
    return translations.get_supported_languages()


def set_translation_language(lang: str = "pt"):
    """
    Configura o idioma para traduções.
    Usado principalmente em templates para definir o idioma atual.
    """
    # Esta função seria usada em conjunto com a sessão do Flask
    return lang if lang in translations.available_languages else "pt"


# Funções auxiliares para uso nos templates
def t(key_path: str, lang: str = "pt", default: Optional[str] = None) -> str:
    """Traduz um texto baseado no caminho da chave."""
    return translations.get(key_path, lang, default)


def t_field(model: str, field: str, lang: str = "pt") -> str:
    """Traduz o rótulo de um campo de modelo."""
    return translations.get_field_label(model, field, lang)


def t_enum(model: str, field: str, value: str, lang: str = "pt") -> str:
    """Traduz um valor de enum."""
    return translations.get_enum_value(model, field, value, lang)


def t_ui(
    category: str, key: str, subkey: Optional[str] = None, lang: str = "pt"
) -> str:
    """Traduz texto da interface do usuário."""
    return translations.get_ui_text(category, key, subkey, lang)


def get_languages() -> List[str]:
    """Função para obter a lista de idiomas suportados com apenas códigos."""
    return translations.get_supported_languages()


def get_language_name(lang_code: str) -> str:
    """Função para obter o nome de um idioma a partir do seu código."""
    return translations.get_language_name(lang_code)


def get_flag_emoji(lang_code: str) -> str:
    """Função para obter o emoji da bandeira de um idioma a partir do seu código."""
    return translations.get_flag_emoji(lang_code)
