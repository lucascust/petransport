from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    session,
    jsonify,
    send_from_directory,
    flash,
    send_file,
)
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import re
from functools import wraps
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from pprint import pprint
import bcrypt

# Import Firebase storage module
from firebase import upload_file_to_firebase, delete_file_from_firebase, get_file_url

# Import database operations
from database_operations import (
    UsersDB,
    PetsDB,
    TravelsDB,
    DocumentsDB,
    AddressesDB,
)

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
    PetSpecies,
    Gender,
    TravelMethod,
)

# Carrega as variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configuração do MongoDB
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client["petransport"]

# Inicialização das classes de operações de banco de dados
users_db = UsersDB()
pets_db = PetsDB()
travels_db = TravelsDB()
documents_db = DocumentsDB()
addresses_db = AddressesDB()

# Configurações da aplicação
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "sua-chave-secreta-aqui")
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max-limit
app.config["GOOGLE_MAPS_API_KEY"] = os.getenv("GOOGLE_MAPS_API_KEY", "")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


import unicodedata


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated_function


def remover_acentos(texto):
    """
    Remove acentos de uma string.
    Exemplo: 'João da Silva' -> 'Joao da Silva'
    """
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def validar_microchip(microchip):
    return bool(re.match(r"^[0-9]{1,15}$", str(microchip)))


# Adiciona a variável 'now' ao contexto global dos templates
@app.context_processor
def inject_now():
    """Adiciona variáveis globais para os templates"""
    # Importa funções do novo módulo translation_manager
    import translations.translation_manager as translation_manager

    return {
        "now": datetime.now(),
        "get_languages": translation_manager.get_languages,
        "get_language_name": translation_manager.get_language_name,
        "get_flag_emoji": translation_manager.get_flag_emoji,
        # Adiciona funções de tradução ao contexto global
        "t": translation_manager.t,  # <-- Adicione esta linha
        "t_ui": translation_manager.t_ui,
        "t_field": translation_manager.t_field,
        "t_enum": translation_manager.t_enum,
        "current_lang": session.get("lang", "pt"),
        "available_languages": [
            (code, translation_manager.get_language_name(code))
            for code in translation_manager.get_languages()
        ],
    }


def verificar_acesso(usuario):
    """Verifica se o usuário tem acesso válido"""
    user = users_db.get_user_by_username(usuario)
    if not user:
        return False

    # Verifica se o acesso expirou (60 dias de inatividade)
    last_access = user.get("last_access", datetime.now())
    if datetime.now() - last_access > timedelta(days=60):
        return False

    return True


def atualizar_ultimo_acesso(usuario):
    """Atualiza o timestamp do último acesso do usuário"""
    user = users_db.get_user_by_username(usuario)
    if user:
        users_db.update_user_last_access(user["_id"])


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/<usuario>")
def usuario_home(usuario):
    if not verificar_acesso(usuario):
        abort(404)

    atualizar_ultimo_acesso(usuario)
    user_data = users_db.get_user_by_username(usuario)
    user_id = user_data["_id"]

    # Logging para debug
    print(
        f"DEBUG: Buscando viagens para o usuário {usuario} com ID {user_id} (tipo: {type(user_id)})"
    )

    # Busca as viagens do usuário
    travels = travels_db.get_travels_by_owner(user_id)

    # Verificar se a viagem específica está sendo encontrada
    travel_id_str = "67fb7c9618768dd784992340"
    try:
        from bson import ObjectId

        travel_id = ObjectId(travel_id_str)
        specific_travel = travels_db.get_travel_by_id(travel_id)
        if specific_travel:
            travel_user_id = specific_travel.get("user_id")
            print(
                f"DEBUG: Viagem {travel_id} encontrada! Pertence ao user_id {travel_user_id} (tipo: {type(travel_user_id)})"
            )
            print(f"DEBUG: Comparação direta: {travel_user_id == user_id}")

            # Tenta converter para string e comparar
            if isinstance(travel_user_id, str):
                print(
                    f"DEBUG: Comparação após conversão: {travel_user_id == str(user_id)}"
                )

                # Adiciona a viagem manualmente à lista se não estiver incluída
                if travel_user_id == str(user_id) and travel_id_str not in [
                    str(t.get("_id")) for t in travels
                ]:
                    print(
                        f"DEBUG: Adicionando viagem manualmente porque o tipo de user_id é incompatível"
                    )
                    travels.append(specific_travel)
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")

    # Busca os pets do usuário da coleção pets
    pets = []
    pet_ids_set = set(str(pid) for pid in user_data.get("pet_ids", []) if pid)
    # Also collect all pet_ids from travels
    for travel in travels:
        # Ensure travel['pet_ids'] are strings
        travel["pet_ids"] = [str(pid) for pid in travel.get("pet_ids", []) if pid]
        pet_ids_set.update(travel["pet_ids"])
    # Fetch all unique pets
    for pet_id in pet_ids_set:
        pet = pets_db.get_pet_by_id(pet_id)
        if pet:
            pet["id"] = str(pet["_id"])  # Ensure string id for Jinja
            # Busca a foto do pet se existir
            if "photo_id" in pet and pet["photo_id"]:
                photo_doc = documents_db.get_document_by_id(pet["photo_id"])
                if photo_doc:
                    pet["photo"] = {"path": photo_doc["path"]}
            pets.append(pet)
    # Adiciona a lista de pets ao usuário para manter compatibilidade com o template
    user_data["pets"] = pets

    # --- BEGIN: Document Progress Calculation ---
    def get_travel_doc_progress(travel, user, pets):
        """
        Returns: {
            'completed': int,
            'total': int,
            'sent_docs': [ (label, type, pet_name or None) ],
            'missing_docs': [ (label, type, pet_name or None) ]
        }
        """
        from collections import defaultdict

        # Get required docs
        required = travel.get("required_documents", {})
        human_docs = required.get("human_docs", [])
        pet_docs_dict = required.get("pet_docs", {})
        # Get all pets for this travel
        travel_pet_ids = [str(pid) for pid in travel.get("pet_ids", [])]
        travel_pets = [p for p in pets if str(p["id"]) in travel_pet_ids]
        # Get all docs for this travel from DB
        travel_id = str(travel.get("_id"))
        travel_documents = list(
            documents_db.collection.find(
                {"entity_type": "travel", "entity_id": travel_id}
            )
        )
        # Human docs
        sent_docs = []
        missing_docs = []
        completed = 0
        total = 0
        # Human doc pretty names
        human_doc_names = {
            "identityDocument": "Documento de Identidade",
            "passport": "Passaporte",
            "travelTicket": "Passagem",
            "travelAuthorization": "Autorização de Viagem",
            "carDocument": "Documento do Carro",
            "addressProof": "Comprovante de Endereço",
            "cviIssuanceAuthorization": "Autorização de Emissão do CVI",
        }
        pet_doc_names = {
            "vaccinationCard": "Carteira de Vacinação",
            "microchipCertificate": "Certificado de Microchip",
            "rabiesSerologyReport": "Relatório de Sorologia Antirrábica",
            "leishmaniasisSerologyReport": "Relatório de Sorologia para Leishmaniose",
            "importPermit": "Permissão de Importação",
            "petPassport": "Passaporte do Pet",
            "cvi": "CVI (Certificado Veterinário Internacional)",
            "importAuthorization": "Autorização de Importação",
            "arrivalNotice": "Notificação de Chegada",
            "endorsedCvi": "CVI Endossado",
            "awbCargo": "AWB Cargo",
            "petFacilities": "Instalações para Pet",
        }
        # Human docs
        for doc_type in human_docs:
            total += 1
            found = next(
                (
                    doc
                    for doc in travel_documents
                    if doc.get("document_type") == doc_type and not doc.get("pet_id")
                ),
                None,
            )
            label = human_doc_names.get(doc_type, doc_type)
            if found:
                completed += 1
                sent_docs.append((label, doc_type, None))
            else:
                missing_docs.append((label, doc_type, None))
        # Pet docs
        for pet in travel_pets:
            pet_id = str(pet["id"])
            pet_name = pet["name"]
            required_pet_docs = pet_docs_dict.get(pet_id, [])
            for doc_type in required_pet_docs:
                total += 1
                found = next(
                    (
                        doc
                        for doc in travel_documents
                        if doc.get("document_type") == doc_type
                        and str(doc.get("pet_id")) == pet_id
                    ),
                    None,
                )
                label = pet_doc_names.get(doc_type, doc_type)
                if found:
                    completed += 1
                    sent_docs.append((label, doc_type, pet_name))
                else:
                    missing_docs.append((label, doc_type, pet_name))
        return {
            "completed": completed,
            "total": total,
            "sent_docs": sent_docs,
            "missing_docs": missing_docs,
        }

    # Build progress dict for all travels
    travel_doc_progress = {}
    for travel in travels:
        travel_doc_progress[str(travel["_id"])] = get_travel_doc_progress(
            travel, user_data, pets
        )
    # --- END: Document Progress Calculation ---

    # Busca os endereços do usuário
    if "residential_address_id" in user_data and user_data["residential_address_id"]:
        residential_address = addresses_db.get_address_by_id(
            user_data["residential_address_id"]
        )
        if residential_address:
            user_data["residential_address"] = residential_address

    if "delivery_address_id" in user_data and user_data["delivery_address_id"]:
        delivery_address = addresses_db.get_address_by_id(
            user_data["delivery_address_id"]
        )
        if delivery_address:
            user_data["delivery_address"] = delivery_address

    # Google Maps API Key for address autocompletion
    google_maps_api_key = app.config["GOOGLE_MAPS_API_KEY"]

    # Saudação dinâmica
    from datetime import datetime

    now = datetime.now()
    hour = now.hour
    if hour < 12:
        greeting = "Bom dia"
    elif hour < 18:
        greeting = "Boa tarde"
    else:
        greeting = "Boa noite"

    return render_template(
        "usuario_home.html",
        usuario=user_data,
        travels=travels,
        travel_doc_progress=travel_doc_progress,
        google_maps_api_key=google_maps_api_key,
        greeting=greeting,
    )


# Rotas para gerenciamento de perfil do usuário
@app.route("/<usuario>/editar_perfil", methods=["GET", "POST"])
def editar_perfil(usuario):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)

    if request.method == "POST":
        # Dados do formulário
        owner_name = request.form.get("owner_name")
        email = request.form.get("email")
        contact_number = request.form.get("contact_number")
        cpf = request.form.get("cpf")
        passport_number = request.form.get("passport_number")

        # Cria objeto de atualização
        update_data = {
            "owner_name": owner_name,
            "email": email,
            "contact_number": contact_number,
        }

        # Atualiza CPF se fornecido
        if cpf:
            update_data["cpf"] = cpf

        # Atualiza passaporte se fornecido
        if passport_number:
            update_data["passport_number"] = passport_number

        # Processa endereços
        # Endereço residencial
        if request.form.get("residential_address"):
            residential_address_data = {
                "entity_type": EntityType.USER,
                "entity_id": user_data["_id"],
                "formatted": request.form.get("residential_address"),
                "lat": request.form.get("residential_address_lat"),
                "lng": request.form.get("residential_address_lng"),
                "city": request.form.get("residential_address_cidade"),
                "state": request.form.get("residential_address_estado"),
                "zip_code": request.form.get("residential_address_cep"),
                "address_type": "residential",
            }

            # Verifica se o usuário já tem um endereço residencial
            if (
                "residential_address_id" in user_data
                and user_data["residential_address_id"]
            ):
                # Atualiza o endereço existente
                addresses_db.update_address(
                    user_data["residential_address_id"], residential_address_data
                )
            else:
                # Cria um novo endereço
                res_address = Address(**residential_address_data)
                addresses_db.create_address(res_address)

        # Endereço de entrega
        if request.form.get("delivery_address"):
            delivery_address_data = {
                "entity_type": EntityType.USER,
                "entity_id": user_data["_id"],
                "formatted": request.form.get("delivery_address"),
                "lat": request.form.get("delivery_address_lat"),
                "lng": request.form.get("delivery_address_lng"),
                "city": request.form.get("delivery_address_cidade"),
                "state": request.form.get("delivery_address_estado"),
                "zip_code": request.form.get("delivery_address_cep"),
                "address_type": "delivery",
            }

            # Verifica se o usuário já tem um endereço de entrega
            if "delivery_address_id" in user_data and user_data["delivery_address_id"]:
                # Atualiza o endereço existente
                addresses_db.update_address(
                    user_data["delivery_address_id"], delivery_address_data
                )
            else:
                # Cria um novo endereço
                del_address = Address(**delivery_address_data)
                addresses_db.create_address(del_address)

        # Atualiza o usuário
        users_db.update_user(user_data["_id"], update_data)

        # Redireciona de volta para a página inicial do usuário
        return redirect(url_for("usuario_home", usuario=usuario))

    # Busca e adiciona os endereços do usuário para o template
    if "residential_address_id" in user_data and user_data["residential_address_id"]:
        residential_address = addresses_db.get_address_by_id(
            user_data["residential_address_id"]
        )
        if residential_address:
            user_data["residential_address"] = residential_address

    if "delivery_address_id" in user_data and user_data["delivery_address_id"]:
        delivery_address = addresses_db.get_address_by_id(
            user_data["delivery_address_id"]
        )
        if delivery_address:
            user_data["delivery_address"] = delivery_address

    return render_template("editar_perfil.html", usuario=user_data)


@app.route("/<usuario>/configuracoes")
def configuracoes(usuario):
    if not verificar_acesso(usuario):
        abort(404)
    user_data = users_db.get_user_by_username(usuario)
    return render_template("configuracoes.html", usuario=user_data)


@app.route("/<usuario>/adicionar_pet", methods=["GET", "POST"])
def usuario_adicionar_pet(usuario):
    if not verificar_acesso(usuario):
        abort(404)

    if request.method == "POST":
        # Get user data
        user = users_db.get_user_by_username(usuario)
        if not user:
            abort(404)

        # Create pet from form data
        pet_data = {
            "name": request.form.get("name"),
            "species": request.form.get("species"),
            "breed": request.form.get("breed"),
            "gender": request.form.get("gender"),
            "birth_date": request.form.get("birth_date"),
            "microchip": request.form.get("microchip"),
            "weight": request.form.get("weight"),
            "fur_color": request.form.get("fur_color"),
            "owner_id": user["_id"],
        }

        # Create the pet using PetsDB
        pet = Pet(**pet_data)
        pet_id = pets_db.create_pet(pet)

        # Handle pet photo if uploaded
        if "photo" in request.files and request.files["photo"].filename:
            file = request.files["photo"]
            if allowed_file(file.filename):
                # Save file temporarily
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_filename = f"{timestamp}_{pet_data['name']}_{filename}"
                temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

                try:
                    # Save the file temporarily
                    file.save(temp_path)

                    # Upload to Firebase Storage
                    destination_blob_name = f"{user['username']}/pets/{temp_filename}"
                    firebase_result = upload_file_to_firebase(
                        temp_path, destination_blob_name
                    )

                    # Remove the temporary file
                    os.remove(temp_path)

                    # Create document for the pet photo
                    photo_document = Document(
                        entity_type=EntityType.PET,
                        entity_id=pet_id,
                        document_type=DocumentType.PET_PHOTO,
                        filename=filename,
                        path=firebase_result["blob_name"],
                        file_type=FileType.IMAGE,
                        description=f"Photo of {pet.name}",
                        firebase_path=firebase_result["firebase_path"],
                        public_url=firebase_result["public_url"],
                        storage_type="firebase",
                        size=(
                            os.path.getsize(temp_path)
                            if os.path.exists(temp_path)
                            else 0
                        ),
                    )
                    photo_id = documents_db.create_document(photo_document)

                    # Set photo_id reference in pet
                    pets_db.update_pet(pet_id, {"photo_id": photo_id})
                except Exception as e:
                    print(f"Error uploading pet photo to Firebase: {e}")
                    # Continue without photo if upload fails

        return redirect(url_for("usuario_home", usuario=usuario))

    user_data = users_db.get_user_by_username(usuario)
    return render_template("adicionar_pet.html", usuario=user_data)


@app.route("/<usuario>/contato")
def contato(usuario):
    if not verificar_acesso(usuario):
        abort(404)
    assunto = request.args.get("assunto", "")
    user_data = users_db.get_user_by_username(usuario)
    return render_template("contato.html", usuario=user_data, assunto=assunto)


# Rotas para gerenciamento de viagens
@app.route("/<usuario>/criar_viagem", methods=["GET", "POST"])
def criar_viagem(usuario):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    if request.method == "POST":
        try:
            # Criar uma instância de Travel usando o método from_form_data
            travel = Travel.from_form_data(
                form_data=request.form,
                user_id=user_data["_id"],
                username=user_data["username"],
            )

            # Criar a viagem no banco de dados
            travel_id = travels_db.create_travel(travel)

            if not travel_id:
                flash("Erro ao criar viagem", "error")
                return redirect(url_for("criar_viagem", usuario=usuario))

            # Processar o arquivo da passagem, se existir
            if (
                "travelTicketFile" in request.files
                and request.files["travelTicketFile"].filename
            ):
                ticket_file = request.files["travelTicketFile"]
                if ticket_file and allowed_file(ticket_file.filename):
                    filename = secure_filename(ticket_file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_path = f"{timestamp}_{filename}"
                    full_path = os.path.join(app.config["UPLOAD_FOLDER"], file_path)
                    ticket_file.save(full_path)

                    # Determina o tipo de arquivo
                    file_type = (
                        FileType.PDF
                        if file_path.lower().endswith(".pdf")
                        else FileType.IMAGE
                    )

                    # Criar documento no banco de dados
                    doc = Document.create_document(
                        file_path=file_path,
                        entity_type=EntityType.TRAVEL,
                        entity_id=travel_id,
                        document_type=DocumentType.TRAVEL_TICKET,
                        file_type=file_type,
                    )
                    doc_id = documents_db.create_document(doc)

                    # Atualizar a viagem com o ID do documento da passagem
                    travels_db.update_travel(travel_id, {"ticket_document_id": doc_id})

            return redirect(
                url_for("viagem_detalhes", usuario=usuario, viagem_id=travel_id)
            )
        except Exception as e:
            flash(f"Erro ao criar viagem: {str(e)}", "error")
            print(f"Erro ao criar viagem: {str(e)}")
            return redirect(url_for("criar_viagem", usuario=usuario))

    # Obter pets do usuário para o formulário
    pets = pets_db.get_pets_by_owner(user_data["_id"])

    # Debug print
    print(f"DEBUG: User {usuario} has {len(pets) if pets else 0} pets by owner_id")
    print(f"DEBUG: User pet_ids: {user_data.get('pet_ids')}")

    # Tentativa alternativa
    if not pets and user_data.get("pet_ids"):
        print(f"DEBUG: Trying alternative method")
        alt_pets = []
        for pet_id in user_data["pet_ids"]:
            pet = pets_db.get_pet_by_id(pet_id)
            if pet:
                alt_pets.append(pet)
        if alt_pets:
            print(f"DEBUG: Found {len(alt_pets)} pets by direct lookup")
            pets = alt_pets

    return render_template(
        "criar_viagem.html",
        usuario=user_data,
        pets=pets,
    )


@app.route("/<usuario>/viagem/<viagem_id>")
def viagem_detalhes(usuario, viagem_id):
    """
    View function for displaying travel details and required documents.
    Only fetches documents linked to the current travel (entity_type=TRAVEL, entity_id=travel._id).
    For each required human document, checks if it exists in the fetched documents.
    For each pet, for each required pet document, checks if it exists in the fetched documents and is associated with that pet.
    No alternative approaches. Multiple pets, one human.
    """
    import re
    import json
    from bson import json_util, ObjectId
    from pprint import pprint

    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    travel = travels_db.get_travel_by_id(viagem_id)
    if not travel:
        abort(404)

    # Garantir que required_documents seja sempre um dict
    if not isinstance(travel.get("required_documents"), dict):
        travel["required_documents"] = {"human_docs": [], "pet_docs": {}}

    if str(travel.get("user_id")) != str(user_data["_id"]):
        abort(403)

    travel_pets = travels_db.get_pets_in_travel(viagem_id)
    pet_documents = {str(pet["_id"]): {} for pet in travel_pets}
    user_documents = {}

    required_human_docs = travel["required_documents"].get("human_docs", [])
    required_pet_docs_dict = travel["required_documents"].get("pet_docs", {})

    print(f"DEBUG: Required human docs: {required_human_docs}")
    print(f"DEBUG: Required pet docs dict: {required_pet_docs_dict}")

    # DIRECT QUERY: Get all documents for this travel directly from MongoDB - using STRING ID!
    print(
        f"DEBUG: Querying for documents with entity_type='travel' and entity_id={viagem_id} as string"
    )
    travel_documents = db.documents.find(
        {"entity_type": "travel", "entity_id": str(viagem_id)}
    )
    travel_documents = list(travel_documents)  # Convert cursor to list

    # DEBUG: Log all documents found for this travel
    print(
        f"DEBUG: Direct MongoDB query - Found {len(travel_documents)} documents for travel {viagem_id}"
    )
    for doc in travel_documents:
        print(
            f"DEBUG: Document: id={doc.get('_id')}, type={doc.get('document_type')}, pet_id={doc.get('pet_id')}, path={doc.get('path')}"
        )

    # For each required human document, check if it exists
    for doc_type in required_human_docs:
        found = next(
            (doc for doc in travel_documents if doc.get("document_type") == doc_type),
            None,
        )
        if found:
            user_documents[doc_type] = found
            print(f"DEBUG: Found human document: {doc_type}")
        else:
            print(f"DEBUG: Missing human document: {doc_type}")

    # For each pet, for each required pet document, check if it exists and is associated with that pet
    for pet in travel_pets:
        pet_id = str(pet["_id"])
        print(f"DEBUG: Checking documents for pet {pet['name']} (ID: {pet_id})")
        pet_required_docs = required_pet_docs_dict.get(pet_id, [])
        for doc_type in pet_required_docs:
            # Direct matching by document_type and pet_id
            found = next(
                (
                    doc
                    for doc in travel_documents
                    if doc.get("document_type") == doc_type
                    and doc.get("pet_id") == pet_id
                ),
                None,
            )

            if found:
                pet_documents[pet_id][doc_type] = found
                print(
                    f"DEBUG: FOUND pet document: {doc_type} for pet {pet['name']} by direct pet_id match"
                )
                continue

            # Check if any documents match just by document_type
            type_matches = [
                doc for doc in travel_documents if doc.get("document_type") == doc_type
            ]
            if type_matches:
                print(
                    f"DEBUG: Found {len(type_matches)} documents with type={doc_type}, but none match pet_id={pet_id}"
                )
                for doc in type_matches:
                    print(
                        f"DEBUG: Type match - doc pet_id: {doc.get('pet_id')}, need: {pet_id}"
                    )

            # Fallback - search by path patterns
            for doc in travel_documents:
                if doc.get("document_type") != doc_type:
                    continue

                # Skip if already matched by direct pet_id
                if doc.get("pet_id") == pet_id:
                    continue

                # Check other indicators
                firebase_subfolder = doc.get("firebase_subfolder", "")
                path = doc.get("path", "")
                description = doc.get("description", "")

                patterns = [
                    f"pets/{pet_id}/",  # Pattern in firebase_subfolder
                    f"/pets/{pet_id}/",  # Pattern in path
                    pet["name"],  # Pet name in description
                ]

                matched_by = None
                if firebase_subfolder and any(
                    p in firebase_subfolder for p in patterns
                ):
                    matched_by = "firebase_subfolder"
                elif path and any(p in path for p in patterns):
                    matched_by = "path"
                elif description and pet["name"] in description:
                    matched_by = "description"

                if matched_by:
                    pet_documents[pet_id][doc_type] = doc
                    print(
                        f"DEBUG: FOUND pet document: {doc_type} for pet {pet['name']} by {matched_by}"
                    )
                    break

            if doc_type not in pet_documents[pet_id]:
                print(f"DEBUG: MISSING pet document: {doc_type} for pet {pet['name']}")

    # DEBUG: Print the final document collections being passed to the template
    print(f"DEBUG: Final user_documents: {list(user_documents.keys())}")
    for pet_id, docs in pet_documents.items():
        pet_name = next(
            (p["name"] for p in travel_pets if str(p["_id"]) == pet_id), "Unknown"
        )
        print(f"DEBUG: Final pet_documents for {pet_name}: {list(docs.keys())}")

    # After building pet_documents and user_documents
    # Calculate pet_progress
    pet_progress = {}
    for pet in travel_pets:
        pet_id = str(pet["_id"])
        pet_required_docs = required_pet_docs_dict.get(pet_id, [])
        completed = 0
        total = len(pet_required_docs)
        for doc_type in pet_required_docs:
            if (
                pet_id in pet_documents
                and doc_type in pet_documents[pet_id]
                and pet_documents[pet_id][doc_type]
            ):
                completed += 1
        pet_progress[pet_id] = {"completed": completed, "total": total}

    # Calculate owner_progress
    owner_completed = 0
    owner_total = len(required_human_docs)
    for doc_type in required_human_docs:
        if doc_type in user_documents and user_documents[doc_type]:
            owner_completed += 1
    owner_progress = {"completed": owner_completed, "total": owner_total}

    # DEBUG: Print progress
    print(f"DEBUG: pet_progress: {pet_progress}")
    print(f"DEBUG: owner_progress: {owner_progress}")

    return render_template(
        "viagem_detalhes.html",
        usuario=user_data,
        travel=travel,
        pets=travel_pets,
        pet_documents=pet_documents,
        user_documents=user_documents,
        pet_progress=pet_progress,
        owner_progress=owner_progress,
    )


@app.route("/<usuario>/editar_viagem/<viagem_id>", methods=["GET", "POST"])
def editar_viagem(usuario, viagem_id):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    # Busca a viagem na coleção de viagens
    travel = travels_db.get_travel_by_id(viagem_id)
    if not travel:
        abort(404)

    # Verifica se a viagem pertence ao usuário
    if str(travel.get("user_id")) != str(user_data["_id"]):
        abort(403)  # Não autorizado

    if request.method == "POST":
        # Obter dados do formulário
        origin = request.form.get("origin")
        destination = request.form.get("destination")
        estimatedDate = request.form.get("estimatedDate")
        travelMethod = request.form.get("travelMethod")
        vehiclePlate = (
            request.form.get("vehiclePlate")
            if request.form.get("vehiclePlate")
            else None
        )
        borderCity = (
            request.form.get("borderCity") if request.form.get("borderCity") else None
        )

        # Atualizar dados da viagem
        updates = {
            "origin": origin,
            "destination": destination,
            "estimatedDate": estimatedDate,
            "travelMethod": travelMethod,
            "vehiclePlate": vehiclePlate,
            "borderCity": borderCity,
            "updated_at": datetime.now(),
        }

        # Preservar os documentos existentes
        # Não atualizamos os pet_documents e human_documents para não perder dados

        # Registrar histórico da atualização
        history_event = {
            "type": "update",
            "description": "Viagem atualizada pelo usuário",
            "date": datetime.now(),
        }

        # Atualizar na coleção de viagens
        travels_db.update_travel(travel["_id"], updates)

        return redirect(
            url_for("viagem_detalhes", usuario=usuario, viagem_id=viagem_id)
        )

    return render_template("editar_viagem.html", usuario=user_data, travel=travel)


@app.route(
    "/<usuario>/upload_documento/<viagem_id>/<tipo>/<documento>",
    methods=["GET", "POST"],
)
def upload_documento(usuario, viagem_id, tipo, documento):
    """
    Endpoint para upload de documentos no sistema.

    Estrutura de armazenamento de acordo com ai_firebase_storage.md:
    - Documentos de viagem: {username}/travels/{viagem_id}/{documento}/{filename}
    - Documentos de pet em viagem: {username}/travels/{viagem_id}/pets/{pet_id}/{documento}/{filename}
    - Documentos de pet fora de viagem: {username}/pets/{pet_id}/{documento}/{filename}
    - Documentos de usuário: {username}/documents/{documento}/{filename}
    """
    # ----- Verificações preliminares -----
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    pet_id = request.args.get("pet_id")

    # Verificar acesso
    if not verificar_acesso(usuario):
        if is_ajax:
            return (
                jsonify({"success": False, "error": "Acesso não autorizado"}),
                403,
            )
        abort(404)

    # Verificar se estamos no contexto de uma viagem
    is_travel_context = viagem_id and viagem_id != "None" and viagem_id != "null"

    # Obter dados do usuário
    user = users_db.get_user_by_username(usuario)
    if not user:
        if is_ajax:
            return (
                jsonify({"success": False, "error": "Usuário não encontrado"}),
                404,
            )
        abort(404)

    # Obter dados de viagem se estamos no contexto de viagem
    travel = None
    if is_travel_context:
        travel = travels_db.get_travel_by_id(viagem_id)
        if not travel:
            if is_ajax:
                return (
                    jsonify({"success": False, "error": "Viagem não encontrada"}),
                    404,
                )
            abort(404)

        # Verificar se a viagem pertence ao usuário
        if str(travel.get("user_id")) != str(user["_id"]):
            if is_ajax:
                return (
                    jsonify({"success": False, "error": "Não autorizado"}),
                    403,
                )
            abort(403)  # Não autorizado

    # ----- Lógica principal para POST (upload) -----
    if request.method == "POST":
        # Verificar arquivo
        if (
            "documento" not in request.files
            or request.files["documento"].filename == ""
        ):
            error_msg = "Nenhum arquivo selecionado"
            if is_ajax:
                return (jsonify({"success": False, "error": error_msg}), 400)
            flash(error_msg, "error")
            return redirect(request.url)

        file = request.files["documento"]
        if not allowed_file(file.filename):
            error_msg = "Tipo de arquivo não permitido"
            if is_ajax:
                return (jsonify({"success": False, "error": error_msg}), 400)
            flash(error_msg, "error")
            return redirect(request.url)

        # Verificar conteúdo do arquivo
        file_content = file.read()
        file_size = len(file_content)
        if file_size == 0:
            error_msg = "Arquivo vazio ou corrompido"
            if is_ajax:
                return (jsonify({"success": False, "error": error_msg}), 400)
            flash(error_msg, "error")
            return redirect(request.url)

        # Reposicionar o ponteiro do arquivo para o início após a leitura
        file.seek(0)

        # Preparar metadados do arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        username = user["username"]
        file_ext = os.path.splitext(filename)[1].lower()
        file_type = FileType.PDF if file_ext == ".pdf" else FileType.IMAGE

        # ----- Determinar contexto e configurar caminhos -----
        if is_travel_context:
            # CONTEXTO DE VIAGEM
            entity_type = EntityType.TRAVEL
            entity_id = travel["_id"]

            if tipo == "pet":
                # Documento de pet em viagem

                # Verificar se o pet_id é válido e está associado à viagem
                if not pet_id or str(pet_id) not in [
                    str(pid) for pid in travel.get("pet_ids", [])
                ]:
                    error_msg = "Pet não está associado a esta viagem"
                    if is_ajax:
                        return (jsonify({"success": False, "error": error_msg}), 400)
                    flash(error_msg, "error")
                    return redirect(request.url)

                # Verificar se o documento é realmente requerido para este pet
                required_pet_docs = travel.get("required_documents", {}).get(
                    "pet_docs", {}
                )
                pet_required_docs = required_pet_docs.get(str(pet_id), [])
                if documento not in pet_required_docs:
                    error_msg = f"O documento '{documento}' não é requerido para este pet nesta viagem."
                    if is_ajax:
                        return (jsonify({"success": False, "error": error_msg}), 400)
                    flash(error_msg, "error")
                    return redirect(request.url)

                # Obter informações do pet
                pet = pets_db.get_pet_by_id(ObjectId(pet_id))
                if not pet:
                    error_msg = "Pet não encontrado"
                    if is_ajax:
                        return (jsonify({"success": False, "error": error_msg}), 404)
                    flash(error_msg, "error")
                    return redirect(request.url)

                pet_name = secure_filename(pet.get("name", "pet"))
                firebase_subfolder = f"pets/{pet_id}/{documento}"
                temp_filename = f"{timestamp}_{pet_name}_{filename}"
                doc_key = f"pets.{pet_id}.{documento}"
                doc_description = f"Documento de viagem: {documento} (pet: {pet_name})"
            else:
                # Documento humano de viagem
                # Restrição: só permitir upload se o documento for requerido
                if documento not in travel.get("required_documents", {}).get(
                    "human_docs", []
                ):
                    error_msg = (
                        f"O documento '{documento}' não é requerido para esta viagem."
                    )
                    if is_ajax:
                        return (jsonify({"success": False, "error": error_msg}), 400)
                    flash(error_msg, "error")
                    return redirect(request.url)
                firebase_subfolder = f"{documento}"
                temp_filename = f"{timestamp}_{documento}_{filename}"
                doc_key = documento
                doc_description = f"Documento de viagem: {documento}"

            # Caminho completo para documentos de viagem
            firebase_folder = f"{username}/travels/{viagem_id}/{firebase_subfolder}"
        else:
            # FORA DO CONTEXTO DE VIAGEM
            if tipo == "pet":
                # Documento de pet fora de viagem
                if not pet_id:
                    error_msg = "Pet ID não fornecido"
                    if is_ajax:
                        return (jsonify({"success": False, "error": error_msg}), 400)
                    flash(error_msg, "error")
                    return redirect(request.url)

                # Verificar se o pet pertence ao usuário
                pet = pets_db.get_pet_by_id(ObjectId(pet_id))
                if not pet or str(pet.get("owner_id")) != str(user["_id"]):
                    error_msg = "Pet não encontrado ou não pertence ao usuário"
                    if is_ajax:
                        return (jsonify({"success": False, "error": error_msg}), 404)
                    flash(error_msg, "error")
                    return redirect(request.url)

                entity_type = EntityType.PET
                entity_id = ObjectId(pet_id)
                pet_name = secure_filename(pet.get("name", "pet"))
                firebase_subfolder = f"{documento}"
                temp_filename = f"{timestamp}_{pet_name}_{filename}"
                doc_key = documento
                doc_description = f"Documento de pet: {documento}"
                firebase_folder = f"{username}/pets/{pet_id}/{firebase_subfolder}"
            else:
                # Documento do usuário fora de viagem
                entity_type = EntityType
                entity_id = user["_id"]
                firebase_subfolder = f"{documento}"
                temp_filename = f"{timestamp}_{filename}"
                doc_key = documento
                doc_description = f"Documento do usuário: {documento}"
                firebase_folder = f"{username}/documents/{firebase_subfolder}"

        # ----- Salvar e fazer upload do arquivo -----
        destination_blob_name = f"{firebase_folder}/{temp_filename}"
        temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

        try:
            # Salvar temporariamente
            file.save(temp_path)

            # Verificar se o arquivo foi salvo corretamente
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                error_msg = "Falha ao salvar o arquivo"
                if is_ajax:
                    return (jsonify({"success": False, "error": error_msg}), 500)
                flash(error_msg, "error")
                return redirect(request.url)

            # Upload para o Firebase
            firebase_result = upload_file_to_firebase(temp_path, destination_blob_name)

            # Remover arquivo temporário
            os.remove(temp_path)

        except Exception as e:
            error_msg = f"Erro ao processar arquivo: {str(e)}"
            if is_ajax:
                return (jsonify({"success": False, "error": error_msg}), 500)
            flash(error_msg, "error")
            return redirect(request.url)

        # ----- Criar e salvar o documento no MongoDB -----
        doc = Document(
            entity_type=entity_type,
            entity_id=entity_id,
            document_type=documento,
            filename=filename,
            path=firebase_result["blob_name"],
            file_type=file_type,
            size=file_size,
            description=doc_description,
            firebase_path=firebase_result["firebase_path"],
            public_url=firebase_result["public_url"],
            storage_type="firebase",
            firebase_subfolder=firebase_subfolder,
            pet_id=ObjectId(pet_id) if pet_id and tipo == "pet" else None,
        )

        # Inserir o documento e obter o ID
        doc_id = documents_db.insert_one(doc)

        # ----- Atualizar a entidade relacionada -----
        if is_travel_context:
            # Atualizar a viagem
            if "document_ids" not in travel:
                travel["document_ids"] = {}
            update_result = travels_db.update_one(
                {"_id": entity_id}, {"$set": {f"document_ids.{doc_key}": doc_id}}
            )

            # Adicionar evento ao histórico da viagem
            history_event = {
                "type": "document_upload",
                "description": f"Documento '{documento}' enviado para {'pet' if tipo == 'pet' else 'responsável'}",
                "date": datetime.now(),
            }
            history = travel.get("history", [])
            history.append(history_event)
            travels_db.update_travel(travel["_id"], {"history": history})

        elif tipo == "pet":
            # Atualizar o pet
            if "document_ids" not in pet:
                pet["document_ids"] = {}
            update_result = pets_db.update_one(
                {"_id": entity_id}, {"$set": {f"document_ids.{doc_key}": doc_id}}
            )
        else:
            # Atualizar o usuário
            if "document_ids" not in user:
                user["document_ids"] = {}
            update_result = users_db.update_one(
                {"_id": entity_id}, {"$set": {f"document_ids.{doc_key}": doc_id}}
            )

        # DEBUG: Log the document creation for debugging
        print(f"DEBUG: Created document with ID: {doc_id}")
        print(
            f"DEBUG: Document details: tipo={tipo}, documento={documento}, pet_id={pet_id if pet_id else 'None'}"
        )
        print(f"DEBUG: Document path: {firebase_result['blob_name']}")

        # Mensagem de sucesso
        if is_ajax:
            return jsonify(
                {"success": True, "message": "Documento enviado com sucesso"}
            )

        flash("Documento enviado com sucesso", "success")
        if is_travel_context:
            return redirect(
                url_for("viagem_detalhes", usuario=usuario, viagem_id=viagem_id)
            )
        elif tipo == "pet":
            return redirect(url_for("pet_details", usuario=usuario, pet_id=pet_id))
        else:
            return redirect(url_for("usuario_home", usuario=usuario))

    # Comportamento de fallback
    if is_travel_context:
        return render_template(
            "upload_documento.html",
            usuario=user,
            viagem_id=viagem_id,
            tipo=tipo,
            documento=documento,
            pet_id=pet_id,
        )
    else:
        return render_template(
            "upload_documento.html",
            usuario=user,
            tipo=tipo,
            documento=documento,
            pet_id=pet_id,
        )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        senha = request.form.get("password")
        if senha == os.getenv("ADMIN_PASSWORD", "admin123"):
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        return render_template("admin_login.html", error="Senha incorreta")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/criar_usuario", methods=["GET"])
@admin_required
def criar_usuario_page():
    google_maps_api_key = app.config["GOOGLE_MAPS_API_KEY"]
    return render_template(
        "criar_usuario.html", google_maps_api_key=google_maps_api_key
    )


@app.route("/cadastro_usuario_novo", methods=["GET"])
def cadastro_usuario_novo():
    # Importa as funções de tradução
    import translations.translation_manager as tm

    # Configuração do Google Maps API Key
    google_maps_api_key = app.config["GOOGLE_MAPS_API_KEY"]

    return render_template(
        "cadastro_usuario_novo.html",
        google_maps_api_key=google_maps_api_key,
    )


def gerar_username_unico(owner_name):
    """
    Gera um username único baseado no nome fornecido.
    Se o username base já existe, adiciona um número incremental até encontrar um disponível.
    Exemplos:
        "João da Silva" -> "joaoSilva"
        "José Roberto Café" -> "joseCafe"
    """
    # Remove acentos
    owner_name = remover_acentos(owner_name)

    # Remove caracteres especiais e substitui por espaços
    owner_name = "".join(c if c.isalnum() else " " for c in owner_name)

    # Divide a string em palavras
    words = owner_name.split()

    # Se não tiver pelo menos duas palavras, usa o nome completo
    if len(words) < 2:
        words_to_use = words
    else:
        # Pega apenas o primeiro e o último nome
        words_to_use = [words[0], words[-1]]

    # Converte para lowercase e capitaliza as palavras (exceto a primeira)
    words_to_use = [word.lower() for word in words_to_use]
    base_username = words_to_use[0] + "".join(
        word.capitalize() for word in words_to_use[1:]
    )

    # Busca todos os usernames que começam com o base_username
    existing_users = users_db.find({"username": {"$regex": f"^{base_username}"}})
    existing_usernames = [user.get("username", "") for user in existing_users]

    # Se não existir nenhum username similar, retorna o base
    if not existing_usernames:
        return base_username

    # Extrai os números dos usernames existentes
    numbers = []
    for username in existing_usernames:
        if username == base_username:
            numbers.append(0)
        elif username.startswith(base_username):
            try:
                num = int(username[len(base_username) :])
                numbers.append(num)
            except ValueError:
                continue

    # Se não houver números, começa com 1
    if not numbers:
        return f"{base_username}1"

    # Encontra o próximo número disponível
    numbers.sort()
    next_num = 1
    for num in numbers:
        if num != next_num:
            break
        next_num += 1

    return f"{base_username}{next_num}"


@app.route("/criar_usuario", methods=["POST"])
@admin_required
def criar_usuario():
    # Dados do usuário do formulário
    form_data = {
        "owner_name": request.form.get("owner_name"),
        "email": request.form.get("email"),
        "contact_number": request.form.get("contact_number"),
        "has_cpf": request.form.get("hasCpf") == "yes",
        "cpf": request.form.get("cpf") if request.form.get("hasCpf") == "yes" else None,
        "passport_number": (
            request.form.get("passport_number")
            if request.form.get("hasCpf") == "no"
            else None
        ),
        "has_special_needs": request.form.get("hasSpecialNeeds") == "yes",
        "special_needs_details": (
            request.form.get("special_needs_details")
            if request.form.get("hasSpecialNeeds") == "yes"
            else None
        ),
        "how_did_you_know": request.form.get("how_did_you_know"),
        "password": request.form.get("password"),  # Add password from form
    }

    # Gera um username único
    username = gerar_username_unico(form_data["owner_name"])
    form_data["username"] = username

    # Cria o usuário usando o modelo User
    user = User(**form_data)
    user_id = users_db.create_user(user)

    if not user_id:
        return jsonify({"error": "Erro ao criar usuário"}), 500

    # Processa o endereço residencial
    residential_address_data = {
        "lat": request.form.get("endereco_residential_lat"),
        "lng": request.form.get("endereco_residential_lng"),
        "formatted": request.form.get("endereco_residential_formatted"),
        "city": request.form.get("endereco_residential_cidade") or "",
        "state": request.form.get("endereco_residential_estado") or "",
        "zip_code": request.form.get("endereco_residential_cep") or "",
        "entity_type": EntityType.USER,
        "entity_id": user_id,
        "address_type": "residential",
    }

    # Cria o endereço residencial
    res_address = Address(**residential_address_data)
    addresses_db.create_address(res_address)

    # Processa o endereço de entrega, se fornecido
    if request.form.get("delivery_address"):
        delivery_address_data = {
            "lat": request.form.get("endereco_delivery_lat"),
            "lng": request.form.get("endereco_delivery_lng"),
            "formatted": request.form.get("endereco_delivery_formatted"),
            "city": request.form.get("endereco_delivery_cidade") or "",
            "state": request.form.get("endereco_delivery_estado") or "",
            "zip_code": request.form.get("endereco_delivery_cep") or "",
            "entity_type": EntityType.USER,
            "entity_id": user_id,
            "address_type": "delivery",
        }

        # Cria o endereço de entrega
        del_address = Address(**delivery_address_data)
        addresses_db.create_address(del_address)

    # Processa os pets
    pet_count = int(request.form.get("pet_count", 0))

    for i in range(pet_count):
        # Obtém os dados do pet
        birth_date_str = request.form.get(f"pets[{i}][birth_date]")
        birth_date = None

        # Converte a data para o formato correto
        try:
            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y")
        except ValueError:
            # Se falhar, tenta outro formato ou usa a data atual
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
            except ValueError:
                birth_date = datetime.now()

        pet_data = {
            "name": request.form.get(f"pets[{i}][name]"),
            "species": request.form.get(f"pets[{i}][species]"),
            "breed": request.form.get(f"pets[{i}][breed]"),
            "gender": request.form.get(f"pets[{i}][gender]"),
            "birth_date": birth_date,
            "microchip": request.form.get(f"pets[{i}][microchip]"),
            "weight": request.form.get(f"pets[{i}][weight]"),
            "fur_color": request.form.get(f"pets[{i}][fur_color]"),
            "owner_id": user_id,
        }

        # Cria o pet
        pet = Pet(**pet_data)
        pet_id = pets_db.create_pet(pet)

        # Processa a foto do pet se presente
        pet_photo_file = request.files.get(f"pets[{i}][photo]")
        if pet_photo_file and pet_photo_file.filename:
            # Salva o arquivo temporariamente
            filename = secure_filename(pet_photo_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"{timestamp}_{pet_data['name']}_{filename}"
            temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

            try:
                # Save the file temporarily
                pet_photo_file.save(temp_path)

                # Upload to Firebase Storage
                destination_blob_name = f"{form_data['username']}/pets/{temp_filename}"
                firebase_result = upload_file_to_firebase(
                    temp_path, destination_blob_name
                )

                # Remove the temporary file
                os.remove(temp_path)

                # Cria o documento para a foto
                photo_doc = Document(
                    entity_type=EntityType.PET,
                    entity_id=pet_id,
                    document_type=DocumentType.PET_PHOTO,
                    filename=filename,
                    path=firebase_result["blob_name"],
                    file_type=FileType.IMAGE,
                    upload_date=datetime.now(),
                    size=os.path.getsize(temp_path) if os.path.exists(temp_path) else 0,
                    firebase_path=firebase_result["firebase_path"],
                    public_url=firebase_result["public_url"],
                    storage_type="firebase",
                )
                photo_doc_id = documents_db.create_document(photo_doc)

                # Atualiza o pet com o ID da foto
                pets_db.update_pet(pet_id, {"photo_id": photo_doc_id})
            except Exception as e:
                print(f"Error uploading pet photo to Firebase: {e}")
                # Continue without photo if upload fails

    return jsonify({"message": "Usuário criado com sucesso", "username": username}), 200


@app.route("/admin")
@admin_required
def admin():
    # Busca todos os usuários usando o UsersDB
    users = users_db.list_users()

    # For each user, fetch their pets details using PetsDB
    for user in users:
        # Add pets field if it's missing
        if "pets" not in user:
            user["pets"] = []

        # Get pets details from PetsDB
        if "pet_ids" in user:
            pet_ids = user.get("pet_ids", [])
            if pet_ids:
                user_pets = []
                for pet_id in pet_ids:
                    pet = pets_db.get_pet_by_id(pet_id)
                    if pet:
                        # Check if pet has a photo
                        if pet.get("photo_id"):
                            # Get the photo document
                            photo_doc = documents_db.get_document_by_id(pet["photo_id"])
                            if photo_doc:
                                if photo_doc.get(
                                    "storage_type"
                                ) == "firebase" and photo_doc.get("public_url"):
                                    pet["photo"] = {
                                        "path": photo_doc["path"],
                                        "url": photo_doc["public_url"],
                                        "filename": photo_doc.get("filename", ""),
                                    }
                                    pet["photo_url"] = photo_doc["public_url"]
                                elif "path" in photo_doc:
                                    pet["photo"] = {"path": photo_doc["path"]}
                                    pet["photo_url"] = (
                                        f"/static/uploads/{photo_doc['path']}"
                                    )

                        # Format dates for template
                        if "birth_date" in pet and isinstance(
                            pet["birth_date"], datetime
                        ):
                            pet["birth_date"] = pet["birth_date"]

                        user_pets.append(pet)

                user["pets"] = user_pets

        # Get user's travel information
        user_id = user["_id"]
        user_travels = travels_db.get_travels_by_owner(user_id)

        # Find current/active travel
        active_travel = None
        upcoming_travel = None
        last_completed_travel = None

        for travel in user_travels:
            # Convert ObjectId to string for template
            if "_id" in travel:
                travel["id"] = str(travel["_id"])

            # Format dates for display
            if "ticket_date" in travel and travel["ticket_date"]:
                travel["formatted_ticket_date"] = travel["ticket_date"].strftime(
                    "%d/%m/%Y"
                )

            # Find active travel
            if travel.get("status") == "in_progress":
                active_travel = travel
            # Find upcoming travel
            elif travel.get("status") == "upcoming" and (
                not upcoming_travel
                or (
                    upcoming_travel.get("ticket_date")
                    and travel.get("ticket_date")
                    and travel["ticket_date"] < upcoming_travel["ticket_date"]
                )
            ):
                upcoming_travel = travel
            # Find last completed travel
            elif travel.get("status") == "completed" and (
                not last_completed_travel
                or (
                    last_completed_travel.get("ticket_date")
                    and travel.get("ticket_date")
                    and travel["ticket_date"] > last_completed_travel["ticket_date"]
                )
            ):
                last_completed_travel = travel

        # Add travel info to user object for template
        if active_travel:
            user["current_travel"] = {
                "id": active_travel.get("id"),
                "status": "active",
                "origin": active_travel.get("origin", ""),
                "destination": active_travel.get("destination", ""),
                "departure_date": active_travel.get("formatted_ticket_date", "N/A"),
            }
        elif upcoming_travel:
            user["current_travel"] = {
                "id": upcoming_travel.get("id"),
                "status": "scheduled",
                "origin": upcoming_travel.get("origin", ""),
                "destination": upcoming_travel.get("destination", ""),
                "departure_date": upcoming_travel.get("formatted_ticket_date", "N/A"),
            }
        elif last_completed_travel:
            user["last_completed_travel"] = {
                "id": last_completed_travel.get("id"),
                "origin": last_completed_travel.get("origin", ""),
                "destination": last_completed_travel.get("destination", ""),
                "completion_date": last_completed_travel.get(
                    "formatted_ticket_date", "N/A"
                ),
            }

    return render_template("admin.html", usuarios=users)


@app.route("/api/usuario/<username>/pet/<pet_name>", methods=["GET"])
@admin_required
def get_pet(username, pet_name):
    # Verifica se o usuário existe
    usuario = users_db.get_user_by_username(username)
    if not usuario:
        return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

    # Get pet_ids from the user
    pet_ids = usuario.get("pet_ids", [])

    # Find the pet by name in the pets collection
    pet = None
    for pet_id in pet_ids:
        temp_pet = pets_db.get_pet_by_id(pet_id)
        if temp_pet and temp_pet.get("name") == pet_name:
            pet = temp_pet
            break

    if not pet:
        return jsonify({"success": False, "error": "Pet não encontrado"}), 404

    # Prepara uma cópia do pet para retorno
    pet_data = dict(pet)

    # Converte datetime para string ISO
    if "birth_date" in pet_data and isinstance(pet_data["birth_date"], datetime):
        pet_data["birth_date"] = pet_data["birth_date"].isoformat()

    # Get photo information if it exists
    if "photo_id" in pet_data and pet_data["photo_id"]:
        photo_doc = documents_db.get_document_by_id(pet_data["photo_id"])
        if photo_doc:
            pet_data["photo"] = {"path": photo_doc["path"]}
            pet_data["photo_url"] = f"/static/uploads/{photo_doc['path']}"

    return jsonify({"success": True, "data": pet_data})


@app.route("/api/usuario/<username>", methods=["GET"])
@admin_required
def get_usuario(username):
    usuario = users_db.get_user_by_username(username)
    if usuario:
        # Converte ObjectId para string para serialização JSON
        usuario["_id"] = str(usuario["_id"])
        # Converte datetime para string ISO
        usuario["registration_date"] = usuario["registration_date"].isoformat()
        usuario["last_access"] = usuario["last_access"].isoformat()

        # Processa pets para manter formato consistente
        if "pets" in usuario:
            for pet in usuario["pets"]:
                if "birth_date" in pet and isinstance(pet["birth_date"], datetime):
                    pet["birth_date"] = pet["birth_date"].isoformat()

                # Processa as fotos para o formato esperado pelo frontend
                if "photo" in pet:
                    # Se for um dicionário, extrai o filename
                    if isinstance(pet["photo"], dict) and "filename" in pet["photo"]:
                        pet["photo_filename"] = pet["photo"]["filename"]
                        pet["photo_url"] = f"/static/uploads/{pet['photo']['filename']}"
                        # Para compatibilidade com o frontend, usa apenas o nome do arquivo
                        pet["photo"] = pet["photo"]["filename"]
                    # Se for string, já está no formato correto
                    elif pet["photo"]:
                        pet["photo_filename"] = pet["photo"]
                        pet["photo_url"] = f"/static/uploads/{pet['photo']}"

                # If pet has a photo_id, get the photo URL from Firebase if available
                if "photo_id" in pet and pet["photo_id"]:
                    photo_doc = documents_db.get_document_by_id(pet["photo_id"])
                    if photo_doc:
                        if photo_doc.get(
                            "storage_type"
                        ) == "firebase" and photo_doc.get("public_url"):
                            pet["photo_url"] = photo_doc["public_url"]
                            pet["photo_filename"] = photo_doc.get("filename", "")
                        elif photo_doc.get("file_path"):
                            pet["photo_url"] = (
                                f"/static/uploads/{photo_doc['file_path']}"
                            )
                            pet["photo_filename"] = photo_doc.get(
                                "filename", photo_doc.get("file_path", "")
                            )

        return usuario
    return {"error": "Usuário não encontrado"}, 404


@app.route("/api/usuario/<username>/pet", methods=["POST"])
@admin_required
def adicionar_pet(username):
    # Verifica se o usuário existe
    usuario = users_db.get_user_by_username(username)
    if not usuario:
        return {"success": False, "error": "Usuário não encontrado"}, 404

    # Obtém os dados do formulário
    name = request.form.get("name")
    species = request.form.get("species")
    breed = request.form.get("breed")
    gender = request.form.get("gender")

    # Processa a data de nascimento
    birth_date_str = request.form.get("birth_date")
    birth_date = None

    # Tenta converter a data
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    except ValueError:
        # Se falhar, usa a data atual
        birth_date = datetime.now()

    microchip = request.form.get("microchip")
    photo_file = request.files.get("photo")
    weight = request.form.get("weight")

    # Check if a pet with the same name already exists for this user
    pet_ids = usuario.get("pet_ids", [])
    for pet_id in pet_ids:
        pet = pets_db.get_pet_by_id(pet_id)
        if pet and pet.get("name") == name:
            return {"success": False, "error": "Já existe um pet com este nome"}, 400

    # Create the pet using PetsDB
    pet = Pet(
        owner_id=usuario["_id"],
        name=name,
        species=species,
        breed=breed,
        gender=gender,
        birth_date=birth_date,
        microchip=microchip,
        weight=weight,
        fur_color=request.form.get("fur_color"),
    )

    # Insert the pet into the database
    pet_id = pets_db.create_pet(pet)

    # If a photo was provided, process and save it
    if photo_file and photo_file.filename:
        if not allowed_file(photo_file.filename):
            return {"success": False, "error": "Tipo de arquivo não permitido"}, 400

        # Save the file temporarily
        filename = secure_filename(photo_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{timestamp}_{filename}"
        temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

        try:
            # Save photo to temporary location
            photo_file.save(temp_path)

            # Upload to Firebase Storage
            destination_blob_name = f"{usuario['username']}/pets/{temp_filename}"
            firebase_result = upload_file_to_firebase(temp_path, destination_blob_name)

            # Remove the temporary file
            os.remove(temp_path)

            # Create a document for the photo
            photo_doc = Document(
                entity_type=EntityType.PET,
                entity_id=pet_id,
                document_type=DocumentType.PET_PHOTO,
                filename=filename,
                path=firebase_result["blob_name"],
                file_type=FileType.IMAGE,
                size=os.path.getsize(temp_path) if os.path.exists(temp_path) else 0,
                firebase_path=firebase_result["firebase_path"],
                public_url=firebase_result["public_url"],
                storage_type="firebase",
            )
            photo_id = documents_db.create_document(photo_doc)

            # Update the pet with the photo ID
            pets_db.update_pet(pet_id, {"photo_id": photo_id})
        except Exception as e:
            print(f"Error uploading pet photo to Firebase: {e}")
            # Continue without photo if upload fails

    return {"success": True}


@app.route("/api/usuario/<username>/pet/<original_name>", methods=["PUT"])
@admin_required
def atualizar_pet(username, original_name):
    # Verifica se o usuário existe
    usuario = users_db.get_user_by_username(username)
    if not usuario:
        return {"success": False, "error": "Usuário não encontrado"}, 404

    # Find the pet by name in the pets collection
    pet_ids = usuario.get("pet_ids", [])
    pet_id = None
    for pid in pet_ids:
        pet = pets_db.get_pet_by_id(pid)
        if pet and pet.get("name") == original_name:
            pet_id = pid
            break

    if not pet_id:
        return {"success": False, "error": "Pet não encontrado"}, 404

    # Obtém os dados do formulário
    name = request.form.get("name")
    species = request.form.get("species")
    breed = request.form.get("breed")
    gender = request.form.get("gender")

    # Processa a data de nascimento
    birth_date_str = request.form.get("birth_date")
    birth_date = None

    # Tenta converter a data
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    except ValueError:
        # Se falhar, usa a data atual
        birth_date = datetime.now()

    microchip = request.form.get("microchip")
    photo_file = request.files.get("photo")

    # Se o nome do pet está sendo alterado, verifica se o novo nome já existe para outro pet
    if name != original_name:
        # Check for duplicates
        for pid in pet_ids:
            if pid != pet_id:  # Skip the current pet
                other_pet = pets_db.get_pet_by_id(pid)
                if other_pet and other_pet.get("name") == name:
                    return {
                        "success": False,
                        "error": "Já existe outro pet com este nome",
                    }, 400

    # Prepara os dados para atualização
    update_data = {
        "name": name,
        "species": species,
        "breed": breed,
        "gender": gender,
        "birth_date": birth_date,
        "microchip": microchip,
        "fur_color": request.form.get("fur_color"),
        "updated_at": datetime.now(),
    }

    # Se uma nova foto foi fornecida, processa e salva
    if photo_file and photo_file.filename:
        if not allowed_file(photo_file.filename):
            return {"success": False, "error": "Tipo de arquivo não permitido"}, 400

        # Salva o arquivo temporariamente
        filename = secure_filename(photo_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"{timestamp}_{filename}"
        temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

        try:
            # Save photo to temporary location
            photo_file.save(temp_path)

            # Upload to Firebase Storage following naming pattern from docs
            destination_blob_name = f"{usuario['username']}/pets/{temp_filename}"
            firebase_result = upload_file_to_firebase(temp_path, destination_blob_name)

            # Remove the temporary file
            os.remove(temp_path)
        except Exception as e:
            return {"success": False, "error": str(e)}, 500

        # Get current pet to check for existing photo
        current_pet = pets_db.get_pet_by_id(pet_id)

        # If the pet already has a photo, update the existing document
        if current_pet.get("photo_id"):
            # Get the existing document
            photo_doc = documents_db.get_document_by_id(current_pet["photo_id"])
            if photo_doc:
                # Delete the old file from Firebase if it's stored there
                if photo_doc.get("storage_type") == "firebase":
                    try:
                        delete_file_from_firebase(photo_doc.get("path"))
                    except Exception as e:
                        print(f"Error deleting old Firebase photo: {e}")

                # Update the document with new file info
                documents_db.update_document(
                    current_pet["photo_id"],
                    {
                        "filename": filename,
                        "path": firebase_result["blob_name"],
                        "firebase_path": firebase_result["firebase_path"],
                        "public_url": firebase_result["public_url"],
                        "storage_type": "firebase",
                        "updated_at": datetime.now(),
                    },
                )
        else:
            # Create a new document for the photo
            photo_doc = Document(
                entity_type=EntityType.PET,
                entity_id=pet_id,
                document_type=DocumentType.PET_PHOTO,
                filename=filename,
                path=firebase_result["blob_name"],
                file_type=FileType.IMAGE,
                size=os.path.getsize(temp_path) if os.path.exists(temp_path) else 0,
                firebase_path=firebase_result["firebase_path"],
                public_url=firebase_result["public_url"],
                storage_type="firebase",
            )
            photo_id = documents_db.create_document(photo_doc)
            update_data["photo_id"] = photo_id

    # Update the pet
    result = pets_db.update_pet(pet_id, update_data)

    if result > 0:
        return {"success": True}
    return {"success": True}  # Return success even if no changes were made


@app.route("/atualizar_foto_pet", methods=["POST"])
@admin_required
def atualizar_foto_pet_via_ajax():
    # Obtém os parâmetros do formulário
    username = request.form.get("username")
    pet_name = request.form.get("pet_name")
    photo_file = request.files.get("photo")

    # Verifica se todos os dados necessários foram fornecidos
    if not username or not pet_name or not photo_file:
        return jsonify({"success": False, "error": "Dados incompletos"}), 400

    # Verifica se o arquivo é permitido
    if not allowed_file(photo_file.filename):
        return (
            jsonify({"success": False, "error": "Tipo de arquivo não permitido"}),
            400,
        )

    # Verifica se o usuário existe
    usuario = users_db.get_user_by_username(username)
    if not usuario:
        return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

    # Find the pet by name
    pet_id = None
    for pid in usuario.get("pet_ids", []):
        pet = pets_db.get_pet_by_id(pid)
        if pet and pet.get("name") == pet_name:
            pet_id = pid
            break

    if not pet_id:
        return jsonify({"success": False, "error": "Pet não encontrado"}), 404

    # Salva o arquivo temporariamente
    filename = secure_filename(photo_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"{timestamp}_{filename}"
    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

    try:
        photo_file.save(temp_path)

        # Upload to Firebase Storage following naming pattern from docs/ai/ai_firebase_storage.md
        destination_blob_name = f"{usuario['username']}/pets/{temp_filename}"
        firebase_result = upload_file_to_firebase(temp_path, destination_blob_name)

        # Remove the temporary file
        os.remove(temp_path)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    # Get the current pet data
    pet = pets_db.get_pet_by_id(pet_id)

    # Check if pet already has a photo
    if pet.get("photo_id"):
        # Get the existing document
        photo_doc = documents_db.get_document_by_id(pet["photo_id"])
        if photo_doc:
            # Delete the old file from Firebase if it's stored there
            if photo_doc.get("storage_type") == "firebase":
                try:
                    delete_file_from_firebase(photo_doc.get("path"))
                except Exception as e:
                    print(f"Error deleting old Firebase photo: {e}")

            # Update the document with new file info
            documents_db.update_document(
                pet["photo_id"],
                {
                    "filename": filename,
                    "path": firebase_result["blob_name"],
                    "firebase_path": firebase_result["firebase_path"],
                    "public_url": firebase_result["public_url"],
                    "storage_type": "firebase",
                    "updated_at": datetime.now(),
                },
            )
            photo_id = pet["photo_id"]
    else:
        # Create a new document for the photo
        photo_doc = Document(
            entity_type=EntityType.PET,
            entity_id=pet_id,
            document_type=DocumentType.PET_PHOTO,
            filename=filename,
            path=firebase_result["blob_name"],
            file_type=FileType.IMAGE,
            size=os.path.getsize(temp_path) if os.path.exists(temp_path) else 0,
            firebase_path=firebase_result["firebase_path"],
            public_url=firebase_result["public_url"],
            storage_type="firebase",
        )
        photo_id = documents_db.create_document(photo_doc)

        # Update the pet record with the photo ID
        pets_db.update_pet(pet_id, {"photo_id": photo_id})

    # Return success response with the photo URL
    return jsonify({"success": True, "photo_url": firebase_result["public_url"]})


@app.route("/api/usuario/<username>/pet/<n>/photo", methods=["PUT"])
@admin_required
def atualizar_foto_pet(username, n):
    # Verifica se o usuário existe
    usuario = users_db.get_user_by_username(username)
    if not usuario:
        return {"success": False, "error": "Usuário não encontrado"}, 404

    # Verifica se o pet existe
    pet = next((p for p in usuario.get("pets", []) if p["name"] == n), None)
    if not pet:
        return {"success": False, "error": "Pet não encontrado"}, 404

    # Obtém a foto do formulário
    photo_file = request.files.get("photo")
    if not photo_file or not photo_file.filename:
        return {"success": False, "error": "Nenhuma foto fornecida"}, 400

    if not allowed_file(photo_file.filename):
        return {"success": False, "error": "Tipo de arquivo não permitido"}, 400

    # Salva o arquivo temporariamente
    filename = secure_filename(photo_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_filename = f"{timestamp}_{filename}"
    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

    try:
        # Save photo to temporary location
        photo_file.save(temp_path)

        # Upload to Firebase Storage following naming pattern from docs/ai/ai_firebase_storage.md
        destination_blob_name = f"{usuario['username']}/pets/{temp_filename}"
        firebase_result = upload_file_to_firebase(temp_path, destination_blob_name)

        # Remove the temporary file
        os.remove(temp_path)
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

    # Check if pet already has a photo
    if pet.get("photo_id"):
        # Get the existing document
        photo_doc = documents_db.get_document_by_id(pet["photo_id"])
        if photo_doc:
            # Delete the old file from Firebase if it's stored there
            if photo_doc.get("storage_type") == "firebase":
                try:
                    delete_file_from_firebase(photo_doc.get("path"))
                except Exception as e:
                    print(f"Error deleting old Firebase photo: {e}")

            # Update the document with new file info
            documents_db.update_document(
                pet["photo_id"],
                {
                    "filename": filename,
                    "path": firebase_result["blob_name"],
                    "firebase_path": firebase_result["firebase_path"],
                    "public_url": firebase_result["public_url"],
                    "storage_type": "firebase",
                    "updated_at": datetime.now(),
                },
            )
            photo_id = pet["photo_id"]
    else:
        # Create a new document for the photo
        photo_doc = Document(
            entity_type=EntityType.PET,
            entity_id=pet["_id"],
            document_type=DocumentType.PET_PHOTO,
            filename=filename,
            path=firebase_result["blob_name"],
            file_type=FileType.IMAGE,
            size=os.path.getsize(temp_path) if os.path.exists(temp_path) else 0,
            firebase_path=firebase_result["firebase_path"],
            public_url=firebase_result["public_url"],
            storage_type="firebase",
        )
        photo_id = documents_db.create_document(photo_doc)

        # Atualiza o pet
        pets_db.update_pet(pet["_id"], {"photo_id": photo_id})

    return {"success": True, "photo_url": firebase_result["public_url"]}


@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template("404.html"), 404


@app.route("/")
def index():
    return render_template("index.html")


# Rota para alterar o idioma
@app.route("/<usuario>/alterar-idioma/<string:lang>", methods=["GET"])
def alterar_idioma(usuario, lang):
    """Altera o idioma da sessão do usuário."""
    # Importa do novo módulo import manager
    import translations.translation_manager as translation_manager

    # Verifica se o idioma solicitado é suportado
    if lang in translation_manager.get_supported_languages():
        session["lang"] = lang

    # Redireciona de volta para a página anterior ou para a página inicial do usuário
    return redirect(request.referrer or url_for("usuario_home", usuario=usuario))


# Definir o idioma padrão para todas as requisições
@app.before_request
def before_request():
    """Define o idioma padrão para a requisição atual e controla autenticação de usuário/admin."""
    # Update session language if ?lang= is present in the URL
    lang = request.args.get("lang")
    if lang:
        lang = lang.strip().lower()
        from translations.translation_manager import get_supported_languages

        if lang in get_supported_languages():
            session["lang"] = lang

    if "lang" not in session:
        session["lang"] = "pt"  # Idioma padrão
    allowed_routes = [
        "home",
        "user_login",
        "static",
        "admin_login",
        "admin_logout",
        "cadastro_usuario_novo",
        "obrigado",
    ]
    if request.endpoint not in allowed_routes and not request.endpoint.startswith(
        "admin"
    ):
        # If admin is logged in, allow access to any user page
        if session.get("admin_logged_in"):
            return
        # Only enforce for user pages for non-admins
        if not session.get("user_logged_in") or not session.get("username"):
            return redirect(url_for("user_login"))
        # Check session expiry
        expiry = session.get("login_expiry")
        if expiry and datetime.now().timestamp() > expiry:
            session.clear()
            return redirect(url_for("user_login"))
        # Refresh expiry on activity
        session["login_expiry"] = (datetime.now() + timedelta(days=60)).timestamp()
        # Only allow user to access their own page unless admin
        if "usuario" in request.view_args:
            usuario = request.view_args["usuario"]
            if usuario != session.get("username"):
                abort(403)


@app.route("/gerar_templates_base")
@admin_required
def gerar_templates_base():
    # Templates básicos para as páginas faltantes
    templates = {
        "editar_perfil.html": """{% extends "base.html" %}
{% block title %}Editar Perfil{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Editar Perfil</h1>
  <p>Página em construção. Aqui você poderá editar seus dados pessoais.</p>
  <a href="{{ url_for('usuario_home', usuario=usuario.username) }}" class="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded">Voltar</a>
</div>
{% endblock %}""",
        "configuracoes.html": """{% extends "base.html" %}
{% block title %}Configurações{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Configurações</h1>
  <p>Página em construção. Aqui você poderá configurar preferências do sistema.</p>
  <a href="{{ url_for('usuario_home', usuario=usuario.username) }}" class="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded">Voltar</a>
</div>
{% endblock %}""",
        "adicionar_pet.html": """{% extends "base.html" %}
{% block title %}Adicionar Pet{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Adicionar Pet</h1>
  <p>Página em construção. Aqui você poderá adicionar um novo pet.</p>
  <a href="{{ url_for('usuario_home', usuario=usuario.username) }}" class="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded">Voltar</a>
</div>
{% endblock %}""",
        "contato.html": """{% extends "base.html" %}
{% block title %}Contato{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Contato</h1>
  {% if assunto %}
  <p class="mb-4">Assunto: {{ assunto }}</p>
  {% endif %}
  <p>Página em construção. Aqui você poderá entrar em contato conosco.</p>
  <a href="{{ url_for('usuario_home', usuario=usuario.username) }}" class="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded">Voltar</a>
</div>
{% endblock %}""",
        "editar_viagem.html": """{% extends "base.html" %}
{% block title %}Editar Viagem{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Editar Viagem</h1>
  <p>Página em construção. Aqui você poderá editar os detalhes da viagem.</p>
  <a href="{{ url_for('viagem_detalhes', usuario=usuario.username, viagem_id=travel.id) }}" class="mt-4 inline-block px-4 py-2 bg-blue-600 text-white rounded">Voltar</a>
</div>
{% endblock %}""",
        "criar_viagem.html": """{% extends "base.html" %}
{% block title %}Criar Viagem{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Criar Nova Viagem</h1>
  <p>Página de formulário para criar uma nova viagem.</p>
  
  <form action="{{ url_for('criar_viagem', usuario=usuario.username) }}" method="POST" enctype="multipart/form-data" class="mt-4 space-y-6">
    <div class="space-y-4">
      <div>
        <label for="origin" class="block text-sm font-medium text-gray-700">Origem</label>
        <input type="text" name="origin" id="origin" required class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
      </div>
      
      <div>
        <label for="destination" class="block text-sm font-medium text-gray-700">Destino</label>
        <input type="text" name="destination" id="destination" required class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
      </div>
      
      <div>
        <label for="estimatedDate" class="block text-sm font-medium text-gray-700">Data Estimada</label>
        <input type="date" name="estimatedDate" id="estimatedDate" required class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
      </div>
      
      <div>
        <label for="travelMethod" class="block text-sm font-medium text-gray-700">Método de Viagem</label>
        <select name="travelMethod" id="travelMethod" required class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
          <option value="carro">Carro</option>
          <option value="aviao">Avião</option>
          <option value="onibus">Ônibus</option>
          <option value="outro">Outro</option>
        </select>
      </div>
      
      <div>
        <label for="vehiclePlate" class="block text-sm font-medium text-gray-700">Placa do Veículo (se aplicável)</label>
        <input type="text" name="vehiclePlate" id="vehiclePlate" class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
      </div>
      
      <div>
        <label for="borderCity" class="block text-sm font-medium text-gray-700">Cidade Fronteiriça (se aplicável)</label>
        <input type="text" name="borderCity" id="borderCity" class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
      </div>
      
      <div>
        <label for="destinationAddress" class="block text-sm font-medium text-gray-700">Endereço de Destino</label>
        <input type="text" name="destinationAddress" id="destinationAddress" class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
      </div>
      
      <div>
        <label for="travelTicketDate" class="block text-sm font-medium text-gray-700">Data da Passagem</label>
        <input type="date" name="travelTicketDate" id="travelTicketDate" class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
      </div>
      
      <div>
        <label for="travelTicketFile" class="block text-sm font-medium text-gray-700">Comprovante da Passagem</label>
        <input type="file" name="travelTicketFile" id="travelTicketFile" class="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md">
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700">Pets que irão viajar</label>
        <div class="mt-2 space-y-2">
          {% for pet in usuario.pets %}
          <div class="flex items-center">
            <input type="checkbox" name="travelingPets" value="{{ pet._id }}" id="pet_{{ pet._id }}" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
            <label for="pet_{{ pet._id }}" class="ml-2 block text-sm text-gray-900">{{ pet.name }} ({{ pet.species }})</label>
          </div>
          {% endfor %}
        </div>
      </div>
    </div>
    
    <div class="flex justify-end space-x-3">
      <a href="{{ url_for('usuario_home', usuario=usuario.username) }}" class="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
        Cancelar
      </a>
      <button type="submit" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
        Salvar Viagem
      </button>
    </div>
  </form>
</div>
{% endblock %}""",
        "viagem_detalhes.html": """{% extends "base.html" %}
{% block title %}Detalhes da Viagem{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto p-4">
  <div class="flex items-center mb-6">
    <a href="{{ url_for('usuario_home', usuario=usuario.username) }}" class="text-blue-600 hover:text-blue-800 mr-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
    </a>
    <h1 class="text-2xl font-bold text-gray-900">Detalhes da Viagem</h1>
  </div>

  <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
    <div class="px-4 py-5 sm:px-6">
      <h2 class="text-lg leading-6 font-medium text-gray-900">Informações Gerais</h2>
      <p class="mt-1 max-w-2xl text-sm text-gray-500">Detalhes da viagem e documentação</p>
    </div>
    <div class="border-t border-gray-200">
      <dl>
        <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Origem</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ travel.origin }}</dd>
        </div>
        <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Destino</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ travel.destination }}</dd>
        </div>
        <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Data Estimada</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ travel.estimatedDate }}</dd>
        </div>
        <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Método de Viagem</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ travel.travelMethod }}</dd>
        </div>
        <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt class="text-sm font-medium text-gray-500">Status</dt>
          <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            {% if travel.status == 'upcoming' %}
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">Próxima</span>
            {% elif travel.status == 'in_progress' %}
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Em Andamento</span>
            {% elif travel.status == 'completed' %}
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Concluída</span>
            {% elif travel.status == 'cancelled' %}
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Cancelada</span>
            {% else %}
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">{{ travel.status }}</span>
            {% endif %}
          </dd>
        </div>
      </dl>
    </div>
  </div>

  <!-- Pets que estão viajando -->
  <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
    <div class="px-4 py-5 sm:px-6">
      <h2 class="text-lg leading-6 font-medium text-gray-900">Pets</h2>
      <p class="mt-1 max-w-2xl text-sm text-gray-500">Pets incluídos nesta viagem</p>
    </div>
    <div class="border-t border-gray-200 px-4 py-5">
      <ul class="divide-y divide-gray-200">
        {% for pet_id in travel.pet_ids %}
          {% for pet in usuario.pets %}
            {% if pet._id|string == pet_id|string %}
              <li class="py-4 flex">
                {% if pet.photo %}
                  <img class="h-10 w-10 rounded-full object-cover" src="{{ url_for('static', filename='uploads/' + pet.photo.path) }}" alt="{{ pet.name }}">
                {% else %}
                  <div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                    <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                {% endif %}
                <div class="ml-3">
                  <p class="text-sm font-medium text-gray-900">{{ pet.name }}</p>
                  <p class="text-sm text-gray-500">{{ pet.species }} - {{ pet.breed }}</p>
                </div>
              </li>
            {% endif %}
          {% endfor %}
        {% endfor %}
      </ul>
    </div>
  </div>

  <!-- Documentos necessários -->
  <div class="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
    <div class="px-4 py-5 sm:px-6">
      <h2 class="text-lg leading-6 font-medium text-gray-900">Documentos Necessários</h2>
      <p class="mt-1 max-w-2xl text-sm text-gray-500">Documentação para a viagem</p>
    </div>
    <div class="border-t border-gray-200">
      <div class="px-4 py-5">
        <h3 class="text-md font-medium text-gray-900 mb-3">Documentos do Tutor</h3>
        <ul class="divide-y divide-gray-200 mb-6">
          {% for doc_type in travel.required_documents.human_docs %}
            <li class="py-3">
              <div class="flex justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ doc_type }}</p>
                </div>
                <div>
                  {% if usuario.human_documents and doc_type in usuario.human_documents %}
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Enviado</span>
                  {% else %}
                    <a href="{{ url_for('upload_documento', usuario=usuario.username, viagem_id=travel.id, tipo='human', documento=doc_type) }}" class="text-blue-600 hover:text-blue-900 text-sm">Upload</a>
                  {% endif %}
                </div>
              </div>
            </li>
          {% endfor %}
        </ul>

        <h3 class="text-md font-medium text-gray-900 mb-3">Documentos dos Pets</h3>
        {% for pet_id in travel.pet_ids %}
          {% for pet in usuario.pets %}
            {% if pet._id|string == pet_id|string %}
              <div class="mb-4">
                <h4 class="text-sm font-semibold mb-2">{{ pet.name }}</h4>
                <ul class="divide-y divide-gray-200">
                  {% for doc_type in travel.required_documents.pet_docs %}
                    <li class="py-3">
                      <div class="flex justify-between">
                        <div>
                          <p class="text-sm font-medium text-gray-900">{{ doc_type }}</p>
                        </div>
                        <div>
                          {% set doc_key = pet._id|string + '_' + doc_type %}
                          {% if usuario.pet_documents and doc_key in usuario.pet_documents %}
                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Enviado</span>
                          {% else %}
                            <a href="{{ url_for('upload_documento', usuario=usuario.username, viagem_id=travel.id, tipo='pet', documento=doc_type, pet_id=pet._id) }}" class="text-blue-600 hover:text-blue-900 text-sm">Upload</a>
                          {% endif %}
                        </div>
                      </div>
                    </li>
                  {% endfor %}
                </ul>
              </div>
            {% endif %}
          {% endfor %}
        {% endfor %}
      </div>
    </div>
  </div>

  <!-- Histórico da viagem -->
  <div class="bg-white shadow overflow-hidden sm:rounded-lg">
    <div class="px-4 py-5 sm:px-6">
      <h2 class="text-lg leading-6 font-medium text-gray-900">Histórico</h2>
      <p class="mt-1 max-w-2xl text-sm text-gray-500">Eventos da viagem</p>
    </div>
    <div class="border-t border-gray-200 px-4 py-5">
      <ul class="divide-y divide-gray-200">
        {% for event in travel.history|sort(attribute='date', reverse=true) %}
          <li class="py-3">
            <div>
              <p class="text-sm font-medium text-gray-900">{{ event.description }}</p>
              <p class="text-xs text-gray-500">{{ event.date.strftime('%d/%m/%Y %H:%M') }}</p>
            </div>
          </li>
        {% endfor %}
      </ul>
    </div>
  </div>

  <!-- Botões de ação -->
  <div class="mt-6 flex justify-end space-x-3">
    <a href="{{ url_for('usuario_home', usuario=usuario.username) }}" class="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
      Voltar
    </a>
    <a href="{{ url_for('editar_viagem', usuario=usuario.username, viagem_id=travel.id) }}" class="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
      Editar Viagem
    </a>
  </div>
</div>
{% endblock %}""",
    }

    for template_name, content in templates.items():
        with open(f"templates/{template_name}", "w") as f:
            f.write(content)

    return "Templates básicos criados com sucesso!"


@app.route("/gerar_template_upload")
@admin_required
def gerar_template_upload():
    with open("templates/upload_documento.html", "w") as f:
        f.write(
            """{% extends "base.html" %}

{% block title %}Upload de Documento{% endblock %}

{% block content %}
<div class="max-w-3xl mx-auto">
  <div class="mb-6 flex items-center">
    <a href="{{ url_for('viagem_detalhes', usuario=usuario.username, viagem_id=viagem_id) }}" class="text-blue-600 hover:text-blue-800 mr-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
    </a>
    <h1 class="text-2xl font-bold text-gray-900">Upload de Documento</h1>
  </div>

  <div class="bg-white shadow-md rounded-lg overflow-hidden">
    <div class="px-4 py-5 sm:p-6">
      <form action="{{ url_for('upload_documento', usuario=usuario.username, viagem_id=viagem_id, tipo=tipo, documento=documento, pet_id=pet_id) }}" method="POST" enctype="multipart/form-data">
        <div class="space-y-6">
          <div>
            <h2 class="text-lg font-medium text-gray-900 mb-4">
              {% if tipo == 'pet' %}
                Upload de {{ documento }} para pet
              {% else %}
                Upload de {{ documento }}
              {% endif %}
            </h2>
            
            <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
              <div class="space-y-1 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <div class="flex text-sm text-gray-600">
                  <label for="documento" class="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                    <span>Fazer upload de arquivo</span>
                    <input id="documento" name="documento" type="file" class="sr-only">
                  </label>
                  <p class="pl-1">ou arraste e solte</p>
                </div>
                <p class="text-xs text-gray-500">PNG, JPG, PDF até 10MB</p>
              </div>
            </div>
          </div>

          <!-- Botões de Ação -->
          <div class="flex justify-end space-x-3 pt-5">
            <a href="{{ url_for('viagem_detalhes', usuario=usuario.username, viagem_id=viagem_id) }}" class="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Cancelar
            </a>
            <button type="submit" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Fazer Upload
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</div>
{% endblock %}"""
        )
    return "Template de upload criado com sucesso!"


@app.route("/<usuario>/pets")
def usuario_pets(usuario):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    # Busca os pets do usuário usando o PetsDB
    pets = pets_db.get_pets_by_owner(user_data["_id"])

    # Debug print
    print(f"DEBUG: User {usuario} has {len(pets) if pets else 0} pets")
    print(f"DEBUG: Pets data: {pets}")

    return render_template("pets.html", usuario=user_data, pets=pets)


@app.route("/<usuario>/pet/<pet_id>")
def pet_details(usuario, pet_id):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    # Busca o pet pelo ID
    pet = pets_db.get_pet_by_id(pet_id)
    if not pet:
        abort(404)

    # Verifica se o pet pertence ao usuário
    if pet.get("owner_id") != user_data["_id"]:
        abort(403)  # Não autorizado

    # Obtém a foto do pet se existir
    pet_photo = None
    photo_url = None
    if "photo_id" in pet:
        pet_photo = documents_db.get_document_by_id(pet["photo_id"])
        if pet_photo:
            if pet_photo.get("storage_type") == "firebase" and pet_photo.get(
                "public_url"
            ):
                photo_url = pet_photo["public_url"]
            elif pet_photo.get("file_path"):
                photo_url = url_for(
                    "static", filename=f"uploads/{pet_photo['file_path']}"
                )

    return render_template(
        "pet_details.html",
        usuario=user_data,
        pet=pet,
        pet_photo=pet_photo,
        photo_url=photo_url,
    )


@app.route("/<usuario>/pet/<pet_id>/update", methods=["POST"])
def update_pet(usuario, pet_id):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    # Busca o pet pelo ID
    pet = pets_db.get_pet_by_id(pet_id)
    if not pet or pet.get("owner_id") != user_data["_id"]:
        abort(403)  # Não autorizado

    # Atualizar pet com os novos dados
    update_data = {
        "name": request.form.get("name"),
        "species": request.form.get("species"),
        "breed": request.form.get("breed"),
        "gender": request.form.get("gender"),
        "birth_date": request.form.get("birth_date"),
        "microchip": request.form.get("microchip"),
        "weight": request.form.get("weight"),
        "fur_color": request.form.get("fur_color"),
    }

    # Processar nova foto se enviada
    if "photo" in request.files and request.files["photo"].filename:
        file = request.files["photo"]
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"{timestamp}_{filename}"
            temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

            try:
                # Save the file temporarily
                file.save(temp_path)

                # Upload to Firebase Storage
                destination_blob_name = f"{user_data['_id']}/pets/{temp_filename}"
                firebase_result = upload_file_to_firebase(
                    temp_path, destination_blob_name
                )

                # Remove the temporary file
                os.remove(temp_path)

                # Get current pet to see if it already has a photo
                if pet.get("photo_id"):
                    # Get the existing document
                    existing_photo = documents_db.get_document_by_id(pet["photo_id"])
                    if (
                        existing_photo
                        and existing_photo.get("storage_type") == "firebase"
                    ):
                        # Delete the old file from Firebase
                        try:
                            delete_file_from_firebase(existing_photo.get("path"))
                        except Exception as e:
                            print(f"Error deleting old photo from Firebase: {e}")

                    # Update the existing photo document
                    documents_db.update_document(
                        pet["photo_id"],
                        {
                            "filename": filename,
                            "path": firebase_result["blob_name"],
                            "firebase_path": firebase_result["firebase_path"],
                            "public_url": firebase_result["public_url"],
                            "storage_type": "firebase",
                            "updated_at": datetime.now(),
                        },
                    )
                    # No need to update pet as it already has the photo_id
                else:
                    # Criar documento para a foto
                    photo_document = Document(
                        entity_type=EntityType.PET,
                        entity_id=pet_id,
                        document_type=DocumentType.PET_PHOTO,
                        filename=filename,
                        path=firebase_result["blob_name"],
                        file_type=FileType.IMAGE,
                        description=f"Photo of {update_data['name']}",
                        firebase_path=firebase_result["firebase_path"],
                        public_url=firebase_result["public_url"],
                        storage_type="firebase",
                        size=(
                            os.path.getsize(temp_path)
                            if os.path.exists(temp_path)
                            else 0
                        ),
                    )
                    photo_id = documents_db.create_document(photo_document)

                    # Adicionar ID da foto aos dados de atualização
                    update_data["photo_id"] = photo_id
            except Exception as e:
                print(f"Error uploading pet photo to Firebase: {e}")
                # Continue without updating photo if upload fails

    # Atualizar pet
    pets_db.update_pet(pet_id, update_data)

    return redirect(url_for("pet_details", usuario=usuario, pet_id=pet_id))


@app.route("/<usuario>/pet/<pet_id>/delete", methods=["POST"])
def delete_pet(usuario, pet_id):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    # Busca o pet pelo ID
    pet = pets_db.get_pet_by_id(pet_id)
    if not pet or pet.get("owner_id") != user_data["_id"]:
        abort(403)  # Não autorizado

    # Exclui o pet
    pets_db.delete_pet(pet_id)

    return redirect(url_for("usuario_pets", usuario=usuario))


@app.route("/api/get_pet_photo/<pet_id>")
def get_pet_photo(pet_id):
    # Busca o pet pelo ID
    pet = pets_db.get_pet_by_id(pet_id)
    if not pet:
        return jsonify({"error": "Pet não encontrado"}), 404

    # Verifica se o pet tem uma foto
    if "photo_id" not in pet or not pet["photo_id"]:
        return jsonify({"error": "Pet não possui foto"}), 404

    # Obtém o documento da foto
    photo_doc = documents_db.get_document_by_id(pet["photo_id"])
    if not photo_doc:
        return jsonify({"error": "Documento da foto não encontrado"}), 404

    # If the photo is stored in Firebase, return the public URL
    if photo_doc.get("storage_type") == "firebase" and photo_doc.get("public_url"):
        return jsonify({"photo_url": photo_doc["public_url"]})
    elif photo_doc.get("file_path"):
        # For backwards compatibility with local storage
        photo_url = url_for("static", filename=f"uploads/{photo_doc['file_path']}")
        return jsonify({"photo_url": photo_url})
    else:
        return jsonify({"error": "URL da foto não disponível"}), 404


@app.route("/<usuario>/travels")
def usuario_travels(usuario):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    # Busca as viagens do usuário usando o TravelsDB
    travels = travels_db.get_travels_by_owner(user_data["_id"])

    return render_template("travels.html", usuario=user_data, travels=travels)


@app.route("/<usuario>/travel/<viagem_id>/cancel", methods=["POST"])
def cancel_travel(usuario, viagem_id):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    # Busca a viagem pelo ID
    travel = travels_db.get_travel_by_id(viagem_id)
    if not travel or travel.get("owner_id") != user_data["_id"]:
        abort(403)  # Não autorizado

    # Atualiza o status da viagem para CANCELADA
    travels_db.update_travel(viagem_id, {"status": TravelStatus.CANCELLED})

    return redirect(url_for("viagem_detalhes", usuario=usuario, viagem_id=viagem_id))


@app.route("/<usuario>/travel/<viagem_id>/complete", methods=["POST"])
def complete_travel(usuario, viagem_id):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    # Busca a viagem pelo ID
    travel = travels_db.get_travel_by_id(viagem_id)
    if not travel or travel.get("owner_id") != user_data["_id"]:
        abort(403)  # Não autorizado

    # Atualiza o status da viagem para COMPLETA
    travels_db.update_travel(viagem_id, {"status": TravelStatus.COMPLETED})

    return redirect(url_for("viagem_detalhes", usuario=usuario, viagem_id=viagem_id))

    return redirect(url_for("viagem_detalhes", usuario=usuario, viagem_id=viagem_id))


@app.route("/<usuario>/documents")
def user_documents(usuario):
    if not verificar_acesso(usuario):
        abort(404)

    user_data = users_db.get_user_by_username(usuario)
    if not user_data:
        abort(404)

    # Busca documentos do usuário
    user_documents = documents_db.get_documents_by_entity(
        EntityType.USER, user_data["_id"]
    )

    # Busca documentos dos pets do usuário
    pets = pets_db.get_pets_by_owner(user_data["_id"])
    pet_documents = []
    for pet in pets:
        pet_docs = documents_db.get_documents_by_entity(EntityType.PET, pet["_id"])
        for doc in pet_docs:
            doc["pet_name"] = pet["name"]
        pet_documents.extend(pet_docs)

    return render_template(
        "documents.html",
        usuario=user_data,
        user_documents=user_documents,
        pet_documents=pet_documents,
    )


@app.route("/static/uploads/<path:filename>")
def serve_static_file(filename):
    """
    Explicitly serve files from the static/uploads directory with proper headers.
    This ensures PDFs are displayed correctly in the browser.
    For Firebase Storage files, redirects to the public URL.
    """
    # First check if this file is actually stored in Firebase
    try:
        document = documents_db.find_one({"path": filename})
        if document and document.get("storage_type") == "firebase":
            if document.get("public_url"):
                return redirect(document.get("public_url"))
            else:
                # Try to get the public URL from Firebase
                blob_name = document.get("path")
                public_url = get_file_url(blob_name)
                # Update the document with the public URL
                documents_db.update_document(
                    document["_id"], {"public_url": public_url}
                )
                return redirect(public_url)
    except Exception as e:
        app.logger.error(f"Error checking Firebase document: {e}")

    # Check if the file exists locally
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        app.logger.error(f"File not found: {file_path}")
        return "File not found", 404

    # Determine MIME type based on file extension
    mime_type = None
    if filename.lower().endswith(".pdf"):
        mime_type = "application/pdf"
    elif filename.lower().endswith((".jpg", ".jpeg")):
        mime_type = "image/jpeg"
    elif filename.lower().endswith(".png"):
        mime_type = "image/png"
    elif filename.lower().endswith(".gif"):
        mime_type = "image/gif"
    elif filename.lower().endswith(".webp"):
        mime_type = "image/webp"

    # Create response with appropriate headers
    response = send_file(file_path, mimetype=mime_type, as_attachment=False)
    response.headers["Content-Type"] = (
        mime_type if mime_type else "application/octet-stream"
    )
    response.headers["Content-Disposition"] = (
        f'inline; filename="{os.path.basename(filename)}"'
    )

    return response


@app.route("/admin/viagem/<viagem_id>/documentos", methods=["GET", "POST"])
@admin_required
def admin_documentos_viagem(viagem_id):
    # Busca a viagem na coleção de viagens
    travel = travels_db.get_travel_by_id(viagem_id)
    if not travel:
        abort(404)

    # Busca o usuário dono da viagem
    user_id = travel.get("user_id")
    user = users_db.get_user_by_id(user_id)
    if not user:
        abort(404)

    if request.method == "POST":
        # Obter documentos selecionados
        human_docs = request.form.getlist("human_docs")
        # Build per-pet required docs dict
        pet_docs = {}
        for pet_id in travel.get("pet_ids", []):
            docs = request.form.getlist(f"pet_docs[{pet_id}][]")
            pet_docs[str(pet_id)] = docs

        # Atualizar dados da viagem
        updates = {
            "required_documents": {"human_docs": human_docs, "pet_docs": pet_docs},
            "updated_at": datetime.now(),
        }
        # Garantir que required_documents é sempre um dict
        if not isinstance(updates["required_documents"], dict):
            updates["required_documents"] = {"human_docs": [], "pet_docs": {}}

        # Registrar histórico da atualização
        history_event = {
            "type": "update",
            "description": "Documentos necessários atualizados pelo administrador",
            "date": datetime.now(),
        }

        # Atualizar na coleção de viagens
        travels_db.update_travel(travel["_id"], updates)

        flash("Documentos necessários atualizados com sucesso!", "success")
        return redirect(
            url_for("viagem_detalhes", usuario=user["username"], viagem_id=viagem_id)
        )

    # Prepare pet_doc_selection for the template
    pet_doc_selection = []
    pet_docs_dict = travel.get("required_documents", {}).get("pet_docs", {})
    for pet_id in travel.get("pet_ids", []):
        pet = pets_db.get_pet_by_id(pet_id)
        if pet:
            pet_doc_selection.append(
                {
                    "id": str(pet["_id"]),
                    "name": pet.get("name", ""),
                    "species": pet.get("species", ""),
                    "required_docs": pet_docs_dict.get(str(pet_id), []),
                }
            )

    return render_template(
        "admin_documentos_viagem.html",
        travel=travel,
        usuario=user,
        pet_doc_selection=pet_doc_selection,
    )


@app.route("/api/travel/<travel_id>")
@admin_required
def get_travel_details(travel_id):
    """API para obter detalhes completos de uma viagem."""

    # Parâmetro opcional para username
    username = request.args.get("username")

    # Buscar a viagem pelo ID
    travel = travels_db.get_travel_by_id(travel_id)
    if not travel:
        return jsonify({"error": "Viagem não encontrada"}), 404

    # Se username for fornecido, verifica se a viagem pertence a esse usuário
    if username:
        user = users_db.get_user_by_username(username)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        # Verifica se a viagem pertence ao usuário
        if str(travel.get("user_id")) != str(user["_id"]):
            return (
                jsonify({"error": "Essa viagem não pertence ao usuário informado"}),
                403,
            )

    # Prepara a resposta com detalhes da viagem
    travel_data = dict(travel)

    # Converte ObjectId para string para serialização JSON
    if "_id" in travel_data:
        travel_data["id"] = str(travel_data["_id"])

    # Formata datas
    if "ticket_date" in travel_data and travel_data["ticket_date"]:
        travel_data["formatted_ticket_date"] = travel_data["ticket_date"].strftime(
            "%d/%m/%Y %H:%M"
        )

    # Busca detalhes dos pets associados à viagem
    pets_data = []
    for pet_id in travel.get("pet_ids", []):
        pet = pets_db.get_pet_by_id(pet_id)
        if pet:
            pet_info = {
                "id": str(pet["_id"]),
                "name": pet.get("name", ""),
                "species": pet.get("species", ""),
                "breed": pet.get("breed", ""),
                "gender": pet.get("gender", ""),
            }

            # Adiciona URL da foto se disponível
            if pet.get("photo_id"):
                photo_doc = documents_db.get_document_by_id(pet["photo_id"])
                if photo_doc:
                    if photo_doc.get("storage_type") == "firebase" and photo_doc.get(
                        "public_url"
                    ):
                        pet_info["photo_url"] = photo_doc["public_url"]
                    elif "path" in photo_doc:
                        pet_info["photo_url"] = f"/static/uploads/{photo_doc['path']}"

            pets_data.append(pet_info)

    travel_data["pets"] = pets_data

    # Adiciona required_documents (human_docs e pet_docs) explicitamente na resposta
    required_documents = travel.get("required_documents", {})
    travel_data["required_documents"] = {
        "human_docs": required_documents.get("human_docs", []),
        "pet_docs": required_documents.get("pet_docs", {}),
    }

    # Formata histórico/eventos da viagem
    if "history" in travel_data:
        for event in travel_data["history"]:
            if "date" in event and isinstance(event["date"], datetime):
                event["date"] = event["date"].isoformat()

    # Converter todos os ObjectId para string
    travel_data = convert_objectid(travel_data)

    return jsonify(travel_data)


def convert_objectid(data):
    """Recursivamente converte todos os ObjectId para string em estruturas de dados"""
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    if isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    return data


@app.route("/api/user/<username>")
@admin_required
def get_user_details(username):
    """API para obter detalhes completos de um usuário."""

    # Buscar o usuário pelo username
    user = users_db.get_user_by_username(username)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Prepara a resposta com detalhes do usuário
    user_data = dict(user)

    # Converte ObjectId para string para serialização JSON
    if "_id" in user_data:
        user_data["id"] = str(user_data["_id"])

    # Formata datas para exibição
    if "registration_date" in user_data and isinstance(
        user_data["registration_date"], datetime
    ):
        user_data["formatted_registration_date"] = user_data[
            "registration_date"
        ].strftime("%d/%m/%Y")
    if "last_access" in user_data and isinstance(user_data["last_access"], datetime):
        user_data["formatted_last_access"] = user_data["last_access"].strftime(
            "%d/%m/%Y"
        )

    # Busca endereços do usuário
    addresses = {}
    if "residential_address_id" in user_data and user_data["residential_address_id"]:
        residential_address = addresses_db.get_address_by_id(
            user_data["residential_address_id"]
        )
        if residential_address:
            addresses["residential"] = residential_address

    if "delivery_address_id" in user_data and user_data["delivery_address_id"]:
        delivery_address = addresses_db.get_address_by_id(
            user_data["delivery_address_id"]
        )
        if delivery_address:
            addresses["delivery"] = delivery_address

    user_data["addresses"] = addresses

    # Busca histórico de viagens do usuário
    travel_history = []
    user_travels = travels_db.get_travels_by_owner(user["_id"])

    for travel in user_travels:
        travel_info = {
            "id": str(travel["_id"]),
            "origin": travel.get("origin", ""),
            "destination": travel.get("destination", ""),
            "status": travel.get("status", ""),
        }

        # Formata data da viagem
        if "ticket_date" in travel and travel["ticket_date"]:
            travel_info["date"] = travel["ticket_date"].strftime("%d/%m/%Y")

        travel_history.append(travel_info)

    # Ordenar viagens (mais recentes primeiro)
    travel_history.sort(
        key=lambda x: (
            datetime.strptime(x.get("date", "01/01/2000"), "%d/%m/%Y")
            if "date" in x
            else datetime.min
        ),
        reverse=True,
    )

    user_data["travel_history"] = travel_history

    # Converter todos os ObjectId para string
    user_data = convert_objectid(user_data)

    return jsonify(user_data)


@app.route("/login", methods=["GET", "POST"])
def user_login():
    # Redirect logged-in users to their home page
    if session.get("user_logged_in") and session.get("username"):
        return redirect(url_for("usuario_home", usuario=session["username"]))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = users_db.find_one({"email": email})
        if user and bcrypt.checkpw(
            password.encode("utf-8"), user["password_hash"].encode("utf-8")
        ):
            session["user_logged_in"] = True
            session["username"] = user["username"]
            session["user_id"] = str(user["_id"])
            session["login_expiry"] = (datetime.now() + timedelta(days=60)).timestamp()
            users_db.update_user_last_access(user["_id"])
            return redirect(url_for("usuario_home", usuario=user["username"]))
        return render_template("user_login.html", error="Email ou senha incorretos")
    return render_template("user_login.html")


@app.route("/logout")
def user_logout():
    session.pop("user_logged_in", None)
    session.pop("username", None)
    session.pop("user_id", None)
    session.pop("login_expiry", None)
    return redirect(url_for("home"))


@app.route("/obrigado")
def obrigado():
    return render_template("obrigado.html")


@app.route("/set_language", methods=["POST"])
def set_language():
    import translations.translation_manager as translation_manager

    data = request.get_json()
    lang = data.get("lang", "").strip().lower()
    if lang in translation_manager.get_supported_languages():
        session["lang"] = lang
    return jsonify(success=True)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
