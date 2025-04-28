# Firebase Storage Integration for PetTransport

Este módulo fornece funcionalidade de armazenamento no Firebase para a aplicação PetTransport, incluindo suporte para módulos que salvam e recuperam arquivos.

## Uso

```python
from firebase import upload_file_to_firebase, delete_file_from_firebase, get_file_url

# Upload de um arquivo para o Firebase Storage
result = upload_file_to_firebase('/path/to/local/file.pdf', 'destination/filename.pdf')
print(f"Arquivo enviado para: {result['public_url']}")

# Obter a URL pública de um arquivo
url = get_file_url('destination/filename.pdf')

# Excluir um arquivo
success = delete_file_from_firebase('destination/filename.pdf')
```

## Padrão de Nomenclatura de Pastas

Para manter os arquivos organizados e evitar colisões de nomes, use os seguintes padrões ao salvar arquivos no Firebase Storage:

### Estrutura Geral
**SEMPRE** comece com o nome de usuário como a pasta principal. Dentro dessa pasta, os arquivos são organizados de acordo com o contexto.

### 1. Documentos de Viagem (incluindo documentos de pets em viagem):
A estrutura para **todos** os documentos relacionados a uma viagem:

```
{username}/travels/{viagem_id}/{tipo_documento}/{timestamp}_{nome_arquivo}
```

#### Para documentos do responsável/humano:
```
{username}/travels/{viagem_id}/{tipo_documento}/{timestamp}_{nome_arquivo}
```
**Exemplo:** `joao/travels/664f1a2b3c4d5e6f7a8b9c0d/passport/20240610_153000_passaporte.pdf`

#### Para documentos de pets associados à viagem:
```
{username}/travels/{viagem_id}/pets/{pet_id}/{tipo_documento}/{timestamp}_{pet_name}_{nome_arquivo}
```
**Exemplo:** `joao/travels/664f1a2b3c4d5e6f7a8b9c0d/pets/62f1a2b3c4d5e6f7a8b9c0d/vaccinationCard/20240610_153000_rex_carteira_vacina.pdf`

### 2. Documentos de Pets (fora do contexto de viagem):
```
{username}/pets/{pet_id}/{tipo_documento}/{timestamp}_{pet_name}_{nome_arquivo}
```
**Exemplo:** `joao/pets/62f1a2b3c4d5e6f7a8b9c0d/petPhoto/20240610_153000_rex_foto.jpg`

### 3. Documentos de Usuário (fora do contexto de viagem):
```
{username}/documents/{tipo_documento}/{timestamp}_{nome_arquivo}
```
**Exemplo:** `joao/documents/identityDocument/20240610_153000_identidade.jpg`

## Benefícios desta Estrutura
- **Organização:** Mantém todos os documentos claramente organizados por contexto.
- **Auditoria:** O timestamp no nome do arquivo permite acompanhar a ordem de uploads.
- **Evita colisões:** A combinação de username/viagem_id/pet_id/timestamp garante nomes únicos.
- **Segurança:** O padrão facilita a definição de regras de segurança do Firebase.