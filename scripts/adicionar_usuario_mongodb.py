#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random
import argparse
from datetime import datetime, timedelta
import uuid
from faker import Faker
import json
from pathlib import Path
import mimetypes
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração do MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGODB_URI)
db = client["petransport"]

# Configurar o Faker para português brasileiro
fake = Faker("pt_BR")

# Espécies, gêneros e como conheceu a empresa
ESPECIES = ["canine", "feline", "bird", "rodent", "other"]
GENEROS = ["male", "female"]
COMO_CONHECEU = [
    "Indicação de amigos",
    "Pesquisa no Google",
    "Instagram",
    "Facebook",
    "Indicação veterinária",
]

# Raças
RACAS_CAES = [
    "Labrador",
    "Poodle",
    "Bulldog",
    "Pastor Alemão",
    "Golden Retriever",
    "SRD",
    "Chihuahua",
]
RACAS_GATOS = ["Persa", "Siamês", "Maine Coon", "Bengal", "SRD", "Ragdoll"]
RACAS_AVES = ["Calopsita", "Periquito", "Canário", "Papagaio", "Arara"]
RACAS_ROEDORES = ["Hamster", "Porquinho da Índia", "Chinchila", "Rato", "Gerbil"]
RACAS_OUTROS = ["Iguana", "Cobra", "Tartaruga", "Coelho", "Furão"]


def gerar_cpf():
    """Gera um CPF formatado válido para teste."""
    numeros = [random.randint(0, 9) for _ in range(9)]

    # Cálculo do primeiro dígito verificador
    soma = sum((numeros[i] * (10 - i)) for i in range(9))
    digito1 = 11 - (soma % 11)
    if digito1 > 9:
        digito1 = 0

    # Cálculo do segundo dígito verificador
    numeros.append(digito1)
    soma = sum((numeros[i] * (11 - i)) for i in range(10))
    digito2 = 11 - (soma % 11)
    if digito2 > 9:
        digito2 = 0

    numeros.append(digito2)

    # Formatação do CPF
    cpf = "".join(map(str, numeros))
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def gerar_passaporte():
    """Gera um número de passaporte válido para teste."""
    letras = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(2))
    numeros = "".join(random.choice("0123456789") for _ in range(6))
    return letras + numeros


def gerar_microchip():
    """Gera um número de microchip válido para teste."""
    return "".join(random.choice("0123456789") for _ in range(15))


def gerar_raca(especie):
    """Gera uma raça aleatória baseada na espécie."""
    if especie == "canine":
        return random.choice(RACAS_CAES)
    elif especie == "feline":
        return random.choice(RACAS_GATOS)
    elif especie == "bird":
        return random.choice(RACAS_AVES)
    elif especie == "rodent":
        return random.choice(RACAS_ROEDORES)
    else:
        return random.choice(RACAS_OUTROS)


def gerar_endereco():
    """Gera um endereço aleatório."""
    endereco = fake.address()
    partes = endereco.split("\n")

    return {
        "lat": str(fake.latitude()),
        "lng": str(fake.longitude()),
        "formatted": partes[0],
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip_code": fake.postcode(),
    }


def remover_acentos(texto):
    """
    Remove acentos de uma string.
    Exemplo: 'João da Silva' -> 'Joao da Silva'
    """
    import unicodedata

    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def to_camel_case(text):
    """
    Converte uma string para camelCase, removendo acentos.
    """
    # Remove acentos
    text = remover_acentos(text)

    # Remove caracteres especiais e substitui por espaços
    text = "".join(c if c.isalnum() else " " for c in text)

    # Divide a string em palavras
    words = text.split()

    # Converte para lowercase e capitaliza as palavras (exceto a primeira)
    words = [word.lower() for word in words]
    return words[0] + "".join(word.capitalize() for word in words[1:])


def gerar_username_unico(base_username):
    """
    Gera um username único verificando no banco de dados.
    """
    # Tenta primeiro o username base
    if db.users.find_one({"username": base_username}) is None:
        return base_username

    # Se já existir, adiciona um número incremental
    next_num = 1
    while True:
        username = f"{base_username}{next_num}"
        if db.users.find_one({"username": username}) is None:
            return username
        next_num += 1


def obter_imagem_aleatoria():
    """Obtém uma imagem aleatória de pets de uma API pública e a salva localmente."""
    try:
        # Criar diretório para as imagens se não existir
        upload_folder = Path("static/uploads")
        upload_folder.mkdir(parents=True, exist_ok=True)

        # Gerar apenas o caminho da imagem sem baixar (para teste)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_pet{random.randint(1,1000)}.jpg"
        file_path = upload_folder / filename

        # Opcional: criar um arquivo em branco para simular (remova em ambiente de produção)
        with open(file_path, "wb") as f:
            f.write(b"Arquivo simulado de imagem")

        return str(file_path)
    except Exception as e:
        print(f"Erro ao criar arquivo de imagem: {e}")

    return None


def gerar_usuario_aleatorio(num_pets, incluir_imagens=True):
    """Gera um documento de usuário com dados aleatórios."""
    # Dados básicos do usuário
    nome_completo = fake.name()
    base_username = to_camel_case(nome_completo)
    username = gerar_username_unico(base_username)

    tem_cpf = random.choice([True, False])
    tem_necessidades_especiais = random.choice([True, False])

    # Endereços
    endereco_residencial = gerar_endereco()
    endereco_entrega = gerar_endereco() if random.choice([True, False]) else None

    # Pets
    pets = []

    for i in range(num_pets):
        especie = random.choice(ESPECIES)
        raca = gerar_raca(especie)

        # Data de nascimento entre 1 e 15 anos atrás
        data_nascimento = datetime.now() - timedelta(days=random.randint(365, 15 * 365))

        # Dados do pet
        pet = {
            "name": fake.first_name(),
            "species": especie,
            "breed": raca,
            "gender": random.choice(GENEROS),
            "birth_date": data_nascimento,
            "microchip": gerar_microchip() if random.choice([True, False]) else None,
            "weight": f"{random.randint(1, 50)}.{random.randint(0, 9)}",
        }

        # Adicionar imagem se solicitado
        if incluir_imagens:
            imagem_path = obter_imagem_aleatoria()
            if imagem_path:
                # Criar documento de arquivo
                file_id = str(uuid.uuid4())
                photo_document = {
                    "file_id": file_id,
                    "filename": os.path.basename(imagem_path),
                    "path": imagem_path,
                    "file_type": "image",
                    "size": (
                        os.path.getsize(imagem_path)
                        if os.path.exists(imagem_path)
                        else 0
                    ),
                    "uploaded_at": datetime.now(),
                }
                pet["photo"] = photo_document

        pets.append(pet)

    # Criar o documento do usuário
    usuario = {
        "username": username,
        "owner_name": nome_completo,
        "email": fake.email(),
        "contact_number": fake.phone_number(),
        "has_cpf": tem_cpf,
        "cpf": gerar_cpf() if tem_cpf else None,
        "passport_number": gerar_passaporte() if not tem_cpf else None,
        "has_special_needs": tem_necessidades_especiais,
        "special_needs_details": (
            fake.text(max_nb_chars=100) if tem_necessidades_especiais else None
        ),
        "how_did_you_know": random.choice(COMO_CONHECEU),
        "residential_address": endereco_residencial,
        "delivery_address": endereco_entrega,
        "registration_date": datetime.now(),
        "last_access": datetime.now(),
        "pets": pets,
        "pet_documents": {},
        "human_documents": {},
        "travel_ids": [],
    }

    return usuario


def adicionar_usuario_bd(usuario):
    """Adiciona um usuário ao banco de dados."""
    try:
        resultado = db.users.insert_one(usuario)
        return resultado.inserted_id
    except Exception as e:
        print(f"Erro ao adicionar usuário ao banco de dados: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Gera e adiciona usuário aleatório diretamente no MongoDB"
    )
    parser.add_argument(
        "--pets", type=int, default=1, help="Número de pets a serem gerados"
    )
    parser.add_argument(
        "--sem-imagens", action="store_true", help="Não incluir imagens nos pets"
    )
    parser.add_argument(
        "--apenas-gerar",
        action="store_true",
        help="Apenas gera os dados sem adicionar ao MongoDB",
    )
    parser.add_argument(
        "--quantidade",
        type=int,
        default=1,
        help="Quantidade de usuários a serem gerados",
    )

    args = parser.parse_args()

    # Gerar e adicionar usuários
    for i in range(args.quantidade):
        # Gerar usuário aleatório
        usuario = gerar_usuario_aleatorio(args.pets, not args.sem_imagens)

        # Se apenas gerar, imprimir o usuário
        if args.apenas_gerar:
            print(json.dumps(usuario, indent=2, default=str))
            continue

        # Adicionar ao banco de dados
        inserted_id = adicionar_usuario_bd(usuario)

        if inserted_id:
            print(
                f"Usuário {usuario['username']} adicionado com sucesso! ID: {inserted_id}"
            )
        else:
            print(f"Falha ao adicionar usuário {usuario['username']}")


if __name__ == "__main__":
    main()
