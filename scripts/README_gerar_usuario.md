# Gerador de Usuários Aleatórios

Este repositório contém dois scripts para gerar dados aleatórios para criação de usuários na plataforma PetTransport, respeitando os requisitos do modelo de dados e da rota de criação de usuários.

## Requisitos

Certifique-se de instalar todas as dependências necessárias:

```bash
pip install -r requirements.txt
```

## Scripts Disponíveis

Existem dois scripts disponíveis:

1. **gerar_usuario_aleatorio.py** - Script básico que gera usuários, mas não inclui autenticação de administrador
2. **gerar_usuario_aleatorio_api.py** - Versão que faz login como administrador antes de enviar os dados (recomendada)

## Como usar o script com autenticação (Recomendado)

O script `gerar_usuario_aleatorio_api.py` lida com a autenticação de administrador necessária:

```bash
python scripts/gerar_usuario_aleatorio_api.py [opções]
```

ou se tiver permissão de execução:

```bash
./scripts/gerar_usuario_aleatorio_api.py [opções]
```

### Opções disponíveis

- `--pets NUMERO`: Define o número de pets a serem gerados para o usuário (padrão: 1)
- `--sem-imagens`: Não inclui imagens nos pets gerados
- `--base-url URL`: URL base da aplicação (padrão: http://localhost:5000)
- `--password SENHA`: Senha de administrador (padrão: teamofernanda)
- `--apenas-gerar`: Apenas gera os dados sem enviar para a API (imprime em JSON)

### Exemplos

1. Gerar um usuário com 3 pets e enviar para a API local:
```bash
python scripts/gerar_usuario_aleatorio_api.py --pets 3
```

2. Gerar um usuário com 2 pets sem imagens:
```bash
python scripts/gerar_usuario_aleatorio_api.py --pets 2 --sem-imagens
```

3. Usar uma senha de administrador personalizada:
```bash
python scripts/gerar_usuario_aleatorio_api.py --password "minha_senha_secreta"
```

4. Enviar para uma aplicação em outro servidor:
```bash
python scripts/gerar_usuario_aleatorio_api.py --base-url https://meuserver.com
```

## Script sem autenticação (não recomendado)

O script `gerar_usuario_aleatorio.py` não faz login como administrador, então só funcionará se você já estiver autenticado no navegador com a mesma sessão:

```bash
python scripts/gerar_usuario_aleatorio.py --pets 3
```

### Opções disponíveis

- `--pets NUMERO`: Define o número de pets a serem gerados (padrão: 1)
- `--sem-imagens`: Não inclui imagens nos pets gerados
- `--url URL`: Define a URL da API de criação de usuário (padrão: http://localhost:5000/criar_usuario)
- `--apenas-gerar`: Apenas gera os dados sem enviar para a API (imprime em JSON)

## Detalhes

Os scripts geram dados aleatórios para os seguintes campos:

- Dados pessoais do usuário (nome, email, telefone, etc.)
- Documentos (CPF ou Passaporte)
- Necessidades especiais (se aplicável)
- Endereços (residencial e entrega)
- Pets (nome, espécie, raça, gênero, data de nascimento, etc.)
- Imagens de pets (obtidas de APIs públicas)

As imagens são baixadas de APIs públicas (dog.ceo ou thecatapi.com) e salvas na pasta `static/uploads`.

## Observações

- Os scripts requerem conexão com a internet para baixar imagens de pets
- As imagens são armazenadas localmente antes de serem enviadas para a API
- Todos os dados pessoais são fictícios, gerados pela biblioteca Faker
- A rota de criação de usuário requer autenticação de administrador 