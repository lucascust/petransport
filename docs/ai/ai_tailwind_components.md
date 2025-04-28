# Instruções para IA: Criação de Componentes com Tailwind CSS para PetTransport


## Sistema de Tradução

O projeto utiliza um sistema robusto de traduções baseado em arquivos JSON. Ao criar componentes, você DEVE garantir a compatibilidade com este sistema, utilizando as funções de tradução apropriadas:

```python
# Funções principais de tradução:
t(key_path, lang, default)         # Obtém uma tradução por caminho completo
t_field(model, field, lang)        # Obtém o rótulo traduzido de um campo de modelo
t_enum(model, field, value, lang)  # Obtém o valor traduzido de uma enumeração
t_ui(category, key, subkey, lang)  # Obtém um texto de interface traduzido
```

### Exemplos de Uso Correto do Sistema de Tradução

```html
<!-- Rótulo de campo de formulário -->
<label class="block text-sm font-medium text-gray-700">
  {{ t_field("Pet", "name", current_lang) }}
</label>

<!-- Valor de enumeração para select -->
<option value="canine">{{ t_enum("Pet", "species", "canine", current_lang) }}</option>

<!-- Texto de botão -->
<button class="bg-primary-600 text-white px-4 py-2 rounded-md">
  {{ t_ui("buttons", "save", lang=current_lang) }}
</button>

<!-- Mensagem de erro/sucesso -->
<div class="bg-green-100 text-green-800 p-3 rounded">
  {{ t_ui("messages", "success", "pet_created", current_lang) }}
</div>
```

## Diretrizes de Estilo com Tailwind

### 1. Paleta de Cores

Use APENAS as seguintes classes de cores para manter consistência:

- **Primárias**: `text-primary-{50-950}`, `bg-primary-{50-950}`, `border-primary-{50-950}`
- **Secundárias**: `text-secondary-{50-950}`, `bg-secondary-{50-950}`, `border-secondary-{50-950}`
- **Neutras**: `text-gray-{50-950}`, `bg-gray-{50-950}`, `border-gray-{50-950}`
- **Funcionais**: 
  - Sucesso: `text-green-{100,700,800}`, `bg-green-{100,500,600}`, `border-green-{400,500}`
  - Erro: `text-red-{100,700,800}`, `bg-red-{100,500,600}`, `border-red-{400,500}`
  - Alerta: `text-yellow-{100,700,800}`, `bg-yellow-{100,500,600}`, `border-yellow-{400,500}`
  - Informação: `text-blue-{100,700,800}`, `bg-blue-{100,500,600}`, `border-blue-{400,500}`

### 2. Tipografia

Hierarquia de texto consistente:

- **Títulos**:
  - H1: `text-4xl font-bold text-gray-900`
  - H2: `text-3xl font-semibold text-gray-800`
  - H3: `text-2xl font-semibold text-gray-800`
  - H4: `text-xl font-medium text-gray-800`

- **Corpo**:
  - Padrão: `text-base text-gray-700`
  - Secundário: `text-sm text-gray-600`
  - Pequeno: `text-xs text-gray-500`

### 3. Espaçamento

Utilize a escala de espaçamento padrão do Tailwind:

- Espaçamento interno: `p-{1-12}`, `px-{1-12}`, `py-{1-12}`
- Margens: `m-{1-12}`, `mx-{1-12}`, `my-{1-12}`
- Para layouts maiores: `p-{3-6}` para cartões, `px-4 py-2` para botões

### 4. Componentes Base

#### Botões

```html
<!-- Botão primário -->
<button class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors">
  {{ t_ui("buttons", "save", lang=current_lang) }}
</button>

<!-- Botão secundário -->
<button class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors">
  {{ t_ui("buttons", "cancel", lang=current_lang) }}
</button>
```

#### Formulários

```html
<!-- Campo de input padrão -->
<div class="mb-4">
  <label for="field_id" class="block text-sm font-medium text-gray-700 mb-1">
    {{ t_field("ModelName", "field_name", current_lang) }}
  </label>
  <input type="text" id="field_id" name="field_name" 
    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
    placeholder="{{ t_ui('placeholders', 'field_name_placeholder', lang=current_lang) }}">
</div>

<!-- Select -->
<div class="mb-4">
  <label for="species" class="block text-sm font-medium text-gray-700 mb-1">
    {{ t_field("Pet", "species", current_lang) }}
  </label>
  <select id="species" name="species" 
    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500">
    <option value="">{{ t_ui("placeholders", "select_species", lang=current_lang) }}</option>
    {% for species_value in ["canine", "feline", "bird", "rodent", "other"] %}
      <option value="{{ species_value }}">{{ t_enum("Pet", "species", species_value, current_lang) }}</option>
    {% endfor %}
  </select>
</div>
```

#### Cards

```html
<div class="bg-white rounded-lg shadow-md p-6 border border-gray-200">
  <h3 class="text-xl font-semibold text-gray-800 mb-4">{{ t_ui("titles", "card_title", lang=current_lang) }}</h3>
  <p class="text-gray-600 mb-4">{{ card_content }}</p>
  <div class="flex justify-end">
    <button class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors">
      {{ t_ui("buttons", "view_details", lang=current_lang) }}
    </button>
  </div>
</div>
```

#### Alertas e Mensagens

```html
<!-- Sucesso -->
<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
  <span class="block sm:inline">{{ t_ui("messages", "success", "operation_success", current_lang) }}</span>
</div>

<!-- Erro -->
<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
  <span class="block sm:inline">{{ t_ui("messages", "errors", "general", current_lang) }}</span>
</div>
```

## Responsividade

Todos os componentes devem ser responsivos. Use as seguintes estratégias:

1. **Layout Fluido**: Prefira unidades relativas como `w-full` em vez de larguras fixas
2. **Breakpoints**: Use os modificadores responsivos do Tailwind (`sm:`, `md:`, `lg:`, `xl:`)
3. **Mobile-First**: Comece com a visualização móvel e adicione modificadores para telas maiores

Exemplo:
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- Cards responsivos -->
</div>
```

## Acessibilidade

Todos os componentes devem seguir boas práticas de acessibilidade:

1. Use atributos `aria-*` apropriados
2. Certifique-se de que todos os elementos interativos são acessíveis via teclado
3. Adicione estilos de foco visíveis para navegação por teclado (`focus:ring-2`, etc.)
4. Use cores com contraste adequado
5. Forneça textos alternativos para imagens (`alt`)

## Integração com Sistema de Tradução - Casos Específicos

### 1. Validação de Formulários

Para mensagens de erro de validação, use a função `t()` com o caminho completo ou `get_validation_message()`:

```html
{% if validation_error %}
<p class="mt-1 text-sm text-red-600">
  {{ get_validation_message("Pet", "microchip_format", current_lang) }}
</p>
{% endif %}
```

### 2. Enumerações em Listas

Quando exibir listas de opções baseadas em enumerações:

```html
<select class="w-full px-3 py-2 border border-gray-300 rounded-md">
  <option value="">{{ t_ui("placeholders", "select_gender", lang=current_lang) }}</option>
  {% for gender_value in ["male", "female"] %}
  <option value="{{ gender_value }}">
    {{ t_enum("Pet", "gender", gender_value, current_lang) }}
  </option>
  {% endfor %}
</select>
```

### 3. Textos Dinâmicos de Interface

Para textos dinâmicos que variam com estado:

```html
<button class="px-4 py-2 bg-primary-600 text-white rounded-md">
  {% if is_editing %}
    {{ t_ui("buttons", "update", lang=current_lang) }}
  {% else %}
    {{ t_ui("buttons", "add", lang=current_lang) }}
  {% endif %}
</button>
```

## Lista de Verificação para Novos Componentes

Ao criar um novo componente, verifique:

- [ ] Utiliza as cores do design system do PetTransport
- [ ] Usa as funções de tradução para todos os textos visíveis
- [ ] É totalmente responsivo e funciona em dispositivos móveis
- [ ] Segue as diretrizes de acessibilidade
- [ ] Tem estados de hover, focus e active claramente definidos
- [ ] Mantém a consistência com outros componentes do sistema
- [ ] Usa convenções de nomenclatura consistentes
- [ ] Inclui animações sutis para feedback visual quando apropriado

## Recomendações de Implementação

1. **Sempre verifique os arquivos de tradução** antes de implementar um novo componente para garantir que as chaves necessárias existam
2. **Prefira componentes existentes** antes de criar novos para evitar duplicação
3. **Mantenha o HTML limpo** usando classes Tailwind de forma organizada
4. **Use as utilidades de extração de componentes** do Tailwind quando apropriado para reduzir repetição
5. **Teste em diferentes tamanhos de tela** para garantir a responsividade
6. **Siga o padrão de nomenclatura** estabelecido no projeto para IDs e classes personalizadas

---

Siga estas diretrizes ao criar componentes com Tailwind CSS para garantir consistência, acessibilidade e compatibilidade com o sistema de traduções do PetTransport. 