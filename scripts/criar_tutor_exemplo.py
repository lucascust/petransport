from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import shutil

# Carrega as variáveis de ambiente
load_dotenv()

# Conecta ao MongoDB
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client["petransport"]

# Dados do tutor
tutor = {
    "owner_name": "Maria Silva",
    "username": "maria_silva_example",
    "registration_date": datetime.now(),
    "last_access": datetime.now(),
    "checklist": [
        {"id": 1, "text": "Checklist item 1", "completed": False},
        {"id": 2, "text": "Checklist item 2", "completed": False},
        {"id": 3, "text": "Checklist item 3", "completed": False},
    ],
    "documents": [
        {
            "title": "Example Document",
            "description": "This is an example document",
            "url": "example.pdf",
        }
    ],
    "theme": "light",
    "notifications": ["email"],
    "pets": [
        {
            "name": "Thor",
            "species": "canine",
            "breed": "Golden Retriever",
            "gender": "male",
            "birth_date": datetime(2020, 3, 15),
            "microchip": "123456789012345",
            "photo": "thor.jpg",
        },
        {
            "name": "Luna",
            "species": "canine",
            "breed": "Labrador",
            "gender": "female",
            "birth_date": datetime(2021, 6, 20),
            "microchip": "234567890123456",
            "photo": "luna.jpg",
        },
        {
            "name": "Max",
            "species": "canine",
            "breed": "German Shepherd",
            "gender": "male",
            "birth_date": datetime(2019, 8, 10),
            "microchip": "345678901234567",
            "photo": "max.jpg",
        },
        {
            "name": "Bella",
            "species": "canine",
            "breed": "Poodle",
            "gender": "female",
            "birth_date": datetime(2022, 1, 5),
            "microchip": "456789012345678",
            "photo": "bella.jpg",
        },
        {
            "name": "Rocky",
            "species": "canine",
            "breed": "Bulldog",
            "gender": "male",
            "birth_date": datetime(2021, 11, 30),
            "microchip": "567890123456789",
            "photo": "rocky.jpg",
        },
    ],
}

# Cria a pasta de uploads se não existir
os.makedirs("static/uploads", exist_ok=True)

# Copia as imagens de exemplo para a pasta de uploads
imagens_exemplo = ["thor.jpg", "luna.jpg", "max.jpg", "bella.jpg", "rocky.jpg"]

for imagem in imagens_exemplo:
    if os.path.exists(f"static/images/exemplo/{imagem}"):
        shutil.copy(f"static/images/exemplo/{imagem}", f"static/uploads/{imagem}")
    else:
        print(
            f"Aviso: A imagem {imagem} não foi encontrada na pasta static/images/exemplo/"
        )

# Insere o tutor no banco de dados
resultado = db.users.insert_one(tutor)

if resultado.inserted_id:
    print("Tutor com 5 cachorros criado com sucesso!")
else:
    print("Erro ao criar o tutor.")
