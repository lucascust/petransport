from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()


def init_database():
    # Conecta ao MongoDB
    client = MongoClient(os.getenv("MONGODB_URI"))

    # Seleciona o banco de dados
    db = client["petransport"]

    # Cria as collections necessárias
    collections = ["users", "documents", "checklists"]

    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
            print(f"Collection '{collection}' criada com sucesso!")

    # Cria índices para otimização
    db.users.create_index("username", unique=True)
    db.users.create_index("last_access")

    print("\nBanco de dados inicializado com sucesso!")
    print("Collections criadas:", ", ".join(collections))


if __name__ == "__main__":
    init_database()
