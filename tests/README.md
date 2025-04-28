# Testes do Sistema PetTransport

Este diretório contém os testes automatizados para o sistema PetTransport.

## Estrutura de Testes

O sistema de testes foi reformulado para focar em testes funcionais que verificam o fluxo completo das principais funcionalidades:

1. **Testes de Criação de Usuário** (`test_user_creation.py`): Testa a criação de usuários, pets e endereços através do formulário de cadastro.

## Executando os Testes

Para executar os testes, você pode usar o script `run_tests.py` na raiz do projeto:

```bash
# Executar todos os testes
python run_tests.py

# Executar apenas os testes de criação de usuário
python run_tests.py --mode user_creation

# Executar testes com relatório de cobertura
python run_tests.py --mode coverage

# Executar com saída detalhada
python run_tests.py --verbose
```

Alternativamente, você pode executar os testes diretamente com pytest:

```bash
# Executar todos os testes
python -m pytest

# Executar teste específico
python -m pytest tests/test_user_creation.py

# Executar com cobertura de código
python -m pytest --cov=app --cov=database_operations --cov=models --cov-report term-missing
```

## Dependências de Teste

Para executar os testes, você precisa das seguintes dependências:

- pytest
- mongomock
- pytest-cov
- coverage

Você pode instalá-las com:

```bash
pip install pytest mongomock pytest-cov coverage
```

Ou instalar todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

## Estrutura dos Arquivos de Teste

### test_user_creation.py

Testa o fluxo completo de criação de usuário, incluindo:

- Criação de usuário básico
- Criação de usuário com pets
- Criação de usuário com múltiplos endereços
- Criação de usuário com necessidades especiais
- Criação de usuário com passaporte (em vez de CPF)
- Teste completo com todos os campos
- Leitura de dados do usuário após criação

Os testes usam mocks para simular as operações de banco de dados, garantindo que possam ser executados sem dependências externas. 