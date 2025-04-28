# Sistema de Traduções - Documentação para IA

## Visão Geral do Sistema de Traduções

Este projeto usa um sistema de traduções baseado em arquivos JSON separados organizados por idioma. Esta abordagem é projetada para:

1. Separar completamente o conteúdo traduzível do código
2. Facilitar a manutenção de traduções sem alterar o código
3. Suportar múltiplos idiomas sem refatoração
4. Padronizar mensagens de erro e textos de interface

## Arquivos e Estrutura

```
project/
├── translations/              # Diretório com arquivos JSON de idiomas
│   ├── pt.json               # Traduções em português
│   └── en.json               # Traduções em inglês
├── translations.py           # Gerenciador de traduções
├── models.py                 # Modelos Pydantic que usam as traduções
├── templates/
│   └── language_selector.html # Componente de seleção de idioma
```

## Como o Sistema Funciona

### 1. Carregamento de Traduções

As traduções são carregadas automaticamente pela classe `TranslationManager` em `translations.py`. Os arquivos JSON são lidos do diretório `translations/`. Se o diretório não existir, ele é criado com traduções padrão.

### 2. Estrutura dos Arquivos JSON

Cada arquivo JSON segue esta estrutura hierárquica:

```json
{
  "models": {
    "ModelName": {
      "fields": {
        "field_name": "Campo Traduzido"
      },
      "enums": {
        "enum_field": {
          "value": "Valor Traduzido"
        }
      },
      "validations": {
        "validation_key": "Mensagem de validação traduzida"
      }
    }
  },
  "ui": {
    "buttons": {
      "save": "Salvar"
    },
    "messages": {
      "category": {
        "key": "Mensagem traduzida"
      }
    }
  }
}
```

### 3. Funções de Tradução

O sistema expõe várias funções para facilitar o acesso às traduções:

- `t(key_path, lang, default)`: Obtém uma tradução por caminho completo (ex: "models.Pet.fields.name")
- `t_field(model, field, lang)`: Obtém o rótulo traduzido de um campo de modelo
- `t_enum(model, field, value, lang)`: Obtém o valor traduzido de uma enumeração
- `t_ui(category, key, subkey, lang)`: Obtém um texto de interface traduzido

### 4. Uso em Modelos Pydantic

Nos modelos, as mensagens de validação usam o sistema de traduções:

```python
@validator("gender")
def validate_gender(cls, v):
    if v not in ["male", "female"]:
        raise ValueError(translations.get_validation_message("Pet", "gender_invalid"))
    return v
```

### 5. Uso em Templates Flask

Nos templates, as traduções são acessadas via funções injetadas:

```html
{{ t_field("Pet", "name", current_lang) }}
{{ t_ui("buttons", "save", lang=current_lang) }}
```

## Como Adicionar ou Modificar Traduções

### Para Adicionar um Novo Texto

1. Identifique a categoria apropriada (models.X.fields, ui.buttons, etc.)
2. Adicione a chave e o valor traduzido nos arquivos JSON relevantes
3. Use a função apropriada para acessar a tradução

### Para Adicionar um Novo Idioma

```python
from translations import translations
translations.add_language("es", base_lang="pt")
```

Isso criará `translations/es.json` baseado no português, que você pode então editar.

## Exemplos de Uso para IA

### Exemplo 1: Acessando uma tradução de campo

```python
# Para obter "Nome do Pet" em português:
field_label = t_field("Pet", "name", "pt")
```

### Exemplo 2: Criando opções para um select

```python
# Gerar opções de espécies traduzidas:
species_options = [
    {"value": species, "label": t_enum("Pet", "species", species, current_lang)}
    for species in ["canine", "feline", "bird", "rodent", "other"]
]
```

### Exemplo 3: Mensagem de validação em modelo

```python
# Validação com mensagem traduzida:
if value is None:
    raise ValueError(translations.get_validation_message("User", "cpf_required"))
```

### Exemplo 4: Formando uma resposta de API

```python
# Resposta de API com mensagem traduzida:
return {
    "success": True,
    "message": t_ui("messages", "success", "pet_created", user_lang)
}
```

## Prevenção de Erros Comuns

1. **Sempre use chaves existentes**: Verifique os arquivos JSON para confirmar que a chave existe
2. **Respeite a hierarquia**: Use o caminho completo correto para acessar traduções aninhadas
3. **Forneça valores padrão**: Use o parâmetro `default` para evitar erros quando uma chave não existir
4. **Use funções específicas**: Prefira `t_field()` e `t_enum()` em vez de caminhos manuais com `t()`
5. **Mantenha sincronizados**: Atualize todos os arquivos de idioma ao adicionar novas chaves

## Funções Internas

A classe `TranslationManager` fornece métodos adicionais para manipulação de traduções:

- `get()`: Obtém uma tradução por caminho de chave
- `save_translations()`: Salva as traduções em disco
- `update_translation()`: Atualiza uma tradução específica
- `add_language()`: Adiciona um novo idioma

Ao trabalhar com este sistema de traduções, a IA deve sempre respeitar a estrutura existente e verificar os arquivos JSON para garantir consistência. 