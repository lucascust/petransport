# Petransport - Plataforma Web Personalizada

Uma plataforma web personalizada desenvolvida com Flask e MongoDB, que permite acesso personalizado a conteúdo específico por usuário.

## Características

- Sistema de URLs personalizadas por usuário
- Controle de acesso por página
- Sistema de expiração de acesso após 60 dias de inatividade
- Visualização de PDFs
- Sistema de checklist
- Interface responsiva
- Sem necessidade de login/cadastro

## Requisitos

- Python 3.8 ou superior
- MongoDB 4.4 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/petransport.git
cd petransport
```

2. Crie um ambiente virtual Python:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=sua-chave-secreta-aqui
```

5. Inicie o MongoDB:
Certifique-se de que o MongoDB está em execução em sua máquina.

## Executando o Projeto

1. Ative o ambiente virtual (se ainda não estiver ativo):
```bash
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

2. Inicie o servidor Flask:
```bash
python app.py
```

3. Acesse a aplicação:
Abra seu navegador e acesse `http://localhost:5000`

## Estrutura do Projeto

```
petransport/
├── app.py              # Aplicação principal Flask
├── requirements.txt    # Dependências do projeto
├── .env               # Variáveis de ambiente
├── static/            # Arquivos estáticos
│   ├── css/
│   ├── js/
│   └── uploads/
└── templates/         # Templates HTML
    ├── base.html
    ├── home.html
    └── usuario_home.html
```

## Adicionando um Novo Usuário

Para adicionar um novo usuário ao sistema, você pode usar o MongoDB Compass ou o shell do MongoDB:

```javascript
db.users.insertOne({
    username: "user_name",
    name: "Full Name",
    last_access: new Date(),
    checklist: [
        { id: 1, text: "Item 1", completed: false },
        { id: 2, text: "Item 2", completed: false }
    ]
})
```

## Segurança

- O acesso é baseado em URLs personalizadas
- O conteúdo expira após 60 dias de inatividade
- As URLs podem ser tornadas mais complexas após um período
- Não há sistema de login/cadastro

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Modelos de Dados com Pydantic

O projeto agora utiliza Pydantic para definir schemas e validação dos dados. Os modelos estão definidos no arquivo `models.py`.

### Principais Modelos

- `Address`: Representa um endereço com coordenadas e informações de localização
- `Pet`: Representa os dados de um animal de estimação
- `User`: Modelo principal de usuário com todos os seus dados e pets associados
- `Travel`: Modelo para viagens e deslocamentos com pets
- `Document`: Modelo unificado para todos os documentos do sistema
- `Event`: Modelo para eventos e histórico de atividades
- `AdminUserView`: Modelo simplificado para visualização no admin

### Nova Estrutura do Banco de Dados

O sistema usa MongoDB com as seguintes coleções:

- `users`: Usuários do sistema
- `pets`: Animais de estimação
- `travels`: Viagens planejadas ou realizadas
- `documents`: Documentos de todos os tipos (centralizados)
- `addresses`: Endereços de usuários e destinos
- `events`: Histórico de atividades e eventos

#### Relacionamentos

- Um usuário pode ter múltiplos pets (referência via `pet_ids`)
- Um usuário pode ter múltiplos endereços (referência via `residential_address_id` e `delivery_address_id`)
- Um usuário pode ter múltiplas viagens (referenciadas através da coleção de viagens)
- Um pet pertence a um usuário (referência via `owner_id`)
- Uma viagem pertence a um usuário (referência via `user_id`)
- Documentos podem pertencer a qualquer entidade (referência via `entity_type` e `entity_id`)
- Eventos registram atividades para qualquer entidade (referência via `entity_type` e `entity_id`)

### Operações de Banco de Dados

O módulo `database_operations.py` fornece classes para manipulação das coleções:

- `UsersDB`: Operações com usuários
- `PetsDB`: Operações com pets
- `TravelsDB`: Operações com viagens
- `DocumentsDB`: Operações com documentos
- `AddressesDB`: Operações com endereços
- `EventsDB`: Operações com eventos

### Como usar

Os modelos podem ser utilizados para validar, serializar e deserializar dados:

```python
# Exemplo de validação de dados
from models import User, Pet, Address
from database_operations import users_db, pets_db
from bson import ObjectId

# Criar um pet com validação
try:
    pet = Pet(
        owner_id=ObjectId("user_object_id_here"),
        name="Rex",
        species="canine",
        breed="Labrador",
        gender="male",
        birth_date=datetime.now(),
        microchip="123456789",
        weight="15.5"
    )
    
    # Salvar no banco de dados
    pet_id = pets_db.create_pet(pet)
    
except ValueError as e:
    print(f"Erro de validação: {e}")

# Criar um usuário completo
user = User(
    username="joaosilva",
    owner_name="João Silva",
    email="joao@example.com",
    contact_number="(11) 98765-4321",
    has_cpf=True,
    cpf="123.456.789-00",
    has_special_needs=False
)

# Salvar no banco de dados
user_id = users_db.create_user(user)

# Consultar usuário
user_data = users_db.get_user_by_username("joaosilva")
```

#### Migração de Dados

Use o script `migrate_db.py` para migrar dados da estrutura antiga para a nova:

```bash
python migrate_db.py
```

### Benefícios da Nova Estrutura

- **Normalização**: Dados organizados em coleções específicas
- **Performance**: Índices apropriados para consultas frequentes
- **Escalabilidade**: Documentos menores e mais organizados
- **Manutenção**: Mais fácil evoluir o esquema no futuro
- **Histórico**: Eventos registrados para todas as ações
- **Referência**: Uso de ObjectId para relacionamentos entre coleções
- **Validação**: Uso de enums e validadores para garantir integridade
- **Centralização**: Documentos gerenciados em uma coleção única 

# PetTransport Application

A Flask application for managing pet transport services.

## New: Firebase Storage Integration

This application now uses Firebase Storage for file uploads. This provides:

- Secure and scalable file storage
- Public URLs for easy access to files
- Backup of important documents in the cloud

### Firebase Setup

To set up Firebase Storage:

1. Create a service account key in Firebase Console
2. Save it as `service-account.json` in the project root
3. See detailed instructions in [Firebase Setup Guide](docs/FIREBASE_SETUP.md)

### Testing Firebase

You can test the Firebase integration using:

```bash
# Run the text file upload test
python -m tests.test_firebase_upload

# Run the image upload test
python -m tests.test_firebase_image_upload

# List available buckets
python -m tests.list_buckets

# Run the Flask test app
python -m tests.test_flask_firebase
```

## Project Structure

```
petransport/
├── app.py                    # Main Flask application
├── database_operations.py    # Database operations
├── models.py                 # Data models
├── translation_manager.py    # Translation utilities
├── firebase/                 # Firebase Storage integration
│   ├── __init__.py           # Package exports
│   ├── storage.py            # Storage implementation
│   └── README.md             # Firebase module documentation
├── tests/                    # Test scripts
│   ├── __init__.py
│   ├── test_firebase_upload.py
│   ├── test_firebase_image_upload.py
│   ├── list_buckets.py
│   └── test_flask_firebase.py
├── docs/                     # Documentation
│   ├── FIREBASE_SETUP.md     # Firebase setup guide
│   ├── service-account.json.example
│   └── env.example           # Environment variables example
├── service-account.json      # Firebase credentials (not in repo)
├── .env                      # Environment variables (not in repo)
└── README.md                 # This file
```

## Running the Application

1. Install dependencies: `pip install -r requirements.txt`
2. Set up Firebase as described above
3. Run the application: `python app.py` 