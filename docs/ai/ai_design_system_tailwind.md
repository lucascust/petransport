# Design System PetTransport com Tailwind CSS

## Introdução

Este documento descreve o design system do PetTransport implementado com Tailwind CSS. O objetivo é padronizar componentes, cores, tipografia e outros elementos visuais para manter a consistência em toda a aplicação.

## Paleta de Cores

```javascript
colors: {
  primary: {
    50: '#eef2ff',   // Fundo muito claro
    100: '#e0e7ff',  // Fundo claro
    200: '#c7d2fe',  // Fundo médio
    300: '#a5b4fc',  // Elementos sutis
    400: '#818cf8',  // Elementos de destaque secundário
    500: '#6366f1',  // Elementos padrão
    600: '#4f46e5',  // Elementos primários, botões principais
    700: '#4338ca',  // Hover de elementos primários
    800: '#3730a3',  // Elementos ativos, textos sobre fundos claros
    900: '#312e81',  // Textos de destaque
    950: '#1e1b4b',  // Textos principais
  },
  secondary: {
    50: '#f0f9ff',   // Fundo muito claro
    100: '#e0f2fe',  // Fundo claro
    200: '#bae6fd',  // Fundo médio
    300: '#7dd3fc',  // Elementos sutis
    400: '#38bdf8',  // Elementos de destaque secundário
    500: '#0ea5e9',  // Elementos padrão
    600: '#0284c7',  // Elementos secundários, botões secundários
    700: '#0369a1',  // Hover de elementos secundários
    800: '#075985',  // Elementos ativos, textos sobre fundos claros
    900: '#0c4a6e',  // Textos de destaque
    950: '#082f49',  // Textos principais
  },
  gray: {
    50: '#f9fafb',   // Fundo de página
    100: '#f3f4f6',  // Fundo de cards, elementos
    200: '#e5e7eb',  // Bordas sutis
    300: '#d1d5db',  // Bordas padrão
    400: '#9ca3af',  // Textos desabilitados
    500: '#6b7280',  // Textos secundários
    600: '#4b5563',  // Textos padrão
    700: '#374151',  // Textos de destaque
    800: '#1f2937',  // Títulos
    900: '#111827',  // Títulos principais
  },
  success: '#10b981',  // Mensagens de sucesso
  danger: '#ef4444',   // Mensagens de erro
  warning: '#f59e0b',  // Alertas
  info: '#3b82f6',     // Informações
}
```

## Tipografia

```javascript
fontFamily: {
  sans: ['Inter', 'sans-serif'],
  // Opcionalmente, adicionar uma fonte de título diferente
  // display: ['Montserrat', 'sans-serif'],
}
```

### Tamanhos e Pesos

- **Títulos**
  - H1: `text-4xl font-bold text-gray-900`
  - H2: `text-3xl font-semibold text-gray-800`
  - H3: `text-2xl font-semibold text-gray-800`
  - H4: `text-xl font-medium text-gray-800`

- **Corpo de texto**
  - Padrão: `text-base text-gray-700`
  - Secundário: `text-sm text-gray-600`
  - Pequeno: `text-xs text-gray-500`

## Componentes

### Botões

1. **Botão Primário**
```html
<button class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors">
  Texto do Botão
</button>
```

2. **Botão Secundário**
```html
<button class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors">
  Texto do Botão
</button>
```

3. **Botão de Perigo**
```html
<button class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors">
  Texto do Botão
</button>
```

4. **Botão com Ícone**
```html
<button class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors">
  <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
    <!-- ícone SVG aqui -->
  </svg>
  Texto do Botão
</button>
```

### Cards

```html
<div class="bg-white rounded-lg shadow-md p-6 border border-gray-200">
  <h3 class="text-xl font-semibold text-gray-800 mb-4">Título do Card</h3>
  <p class="text-gray-600">Conteúdo do card aqui.</p>
</div>
```

### Formulários

1. **Grupo de Formulário**
```html
<div class="mb-4">
  <label for="campo" class="block text-sm font-medium text-gray-700 mb-1">Nome do Campo</label>
  <input type="text" id="campo" name="campo" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500">
  <p class="mt-1 text-sm text-gray-500">Texto de ajuda opcional</p>
</div>
```

2. **Campo de Seleção**
```html
<div class="mb-4">
  <label for="selecao" class="block text-sm font-medium text-gray-700 mb-1">Opções</label>
  <select id="selecao" name="selecao" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500">
    <option value="">Selecione uma opção</option>
    <option value="opcao1">Opção 1</option>
    <option value="opcao2">Opção 2</option>
  </select>
</div>
```

3. **Checkbox**
```html
<div class="flex items-center mb-4">
  <input type="checkbox" id="checkbox" name="checkbox" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
  <label for="checkbox" class="ml-2 block text-sm text-gray-700">Texto do checkbox</label>
</div>
```

4. **Radio Button**
```html
<div class="flex items-center mb-2">
  <input type="radio" id="radio1" name="radio" value="opcao1" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300">
  <label for="radio1" class="ml-2 block text-sm text-gray-700">Opção 1</label>
</div>
```

### Alertas e Mensagens

1. **Alerta de Sucesso**
```html
<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
  <span class="block sm:inline">Operação realizada com sucesso!</span>
</div>
```

2. **Alerta de Erro**
```html
<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
  <span class="block sm:inline">Ocorreu um erro. Por favor, tente novamente.</span>
</div>
```

3. **Alerta de Informação**
```html
<div class="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded relative mb-4" role="alert">
  <span class="block sm:inline">Informação importante aqui.</span>
</div>
```

### Tabelas

```html
<table class="min-w-full bg-white border border-gray-200 rounded-lg overflow-hidden">
  <thead class="bg-gray-50">
    <tr>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Coluna 1</th>
      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Coluna 2</th>
    </tr>
  </thead>
  <tbody class="divide-y divide-gray-200">
    <tr>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">Dado 1</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">Dado 2</td>
    </tr>
    <!-- Mais linhas aqui -->
  </tbody>
</table>
```

### Navegação

1. **Navegação Principal**
```html
<nav class="bg-primary-600 text-white shadow-md">
  <div class="container mx-auto px-4 py-3 flex justify-between items-center">
    <a href="#" class="text-2xl font-bold">Petransport</a>
    <div class="hidden md:flex space-x-6">
      <a href="#" class="hover:text-primary-200 transition">Link 1</a>
      <a href="#" class="hover:text-primary-200 transition">Link 2</a>
      <a href="#" class="hover:text-primary-200 transition">Link 3</a>
    </div>
  </div>
</nav>
```

2. **Breadcrumbs**
```html
<nav class="flex py-3 px-5 text-gray-700 bg-gray-50 rounded-lg" aria-label="Breadcrumb">
  <ol class="inline-flex items-center space-x-1 md:space-x-3">
    <li class="inline-flex items-center">
      <a href="#" class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-primary-600">
        <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path></svg>
        Home
      </a>
    </li>
    <li>
      <div class="flex items-center">
        <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
        <a href="#" class="ml-1 text-sm font-medium text-gray-700 hover:text-primary-600 md:ml-2">Categoria</a>
      </div>
    </li>
    <li aria-current="page">
      <div class="flex items-center">
        <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
        <span class="ml-1 text-sm font-medium text-gray-500 md:ml-2">Página Atual</span>
      </div>
    </li>
  </ol>
</nav>
```

### Paginação

```html
<nav class="flex justify-center mt-8">
  <ul class="inline-flex items-center -space-x-px">
    <li>
      <a href="#" class="block px-3 py-2 ml-0 leading-tight text-gray-500 bg-white border border-gray-300 rounded-l-lg hover:bg-gray-100 hover:text-gray-700">
        <span class="sr-only">Anterior</span>
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>
      </a>
    </li>
    <li>
      <a href="#" class="px-3 py-2 leading-tight text-gray-500 bg-white border border-gray-300 hover:bg-gray-100 hover:text-gray-700">1</a>
    </li>
    <li>
      <a href="#" class="px-3 py-2 leading-tight text-white bg-primary-600 border border-primary-600 hover:bg-primary-700">2</a>
    </li>
    <li>
      <a href="#" class="px-3 py-2 leading-tight text-gray-500 bg-white border border-gray-300 hover:bg-gray-100 hover:text-gray-700">3</a>
    </li>
    <li>
      <a href="#" class="block px-3 py-2 leading-tight text-gray-500 bg-white border border-gray-300 rounded-r-lg hover:bg-gray-100 hover:text-gray-700">
        <span class="sr-only">Próximo</span>
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
      </a>
    </li>
  </ul>
</nav>
```

## Acessibilidade

- Use contraste adequado entre texto e fundo
- Adicione atributos `aria-*` para elementos interativos
- Use `sr-only` para textos acessíveis apenas para leitores de tela
- Mantenha a navegação via teclado funcional com `:focus`

## Sistema de Tradução

### Integração com Tailwind

Para integrar o sistema de traduções existente com os componentes Tailwind, mantenha o uso das funções de tradução nos campos de texto e mensagens:

```html
<label for="name" class="block text-sm font-medium text-gray-700 mb-1">
  {{ t_field("Pet", "name", current_lang) }}
</label>

<button class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700">
  {{ t_ui("buttons", "save", lang=current_lang) }}
</button>

{% if success %}
<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative">
  {{ t_ui("messages", "success", "pet_created", user_lang) }}
</div>
{% endif %}
```

## Responsividade

Use os breakpoints do Tailwind para criar layouts responsivos:

- `sm`: >= 640px
- `md`: >= 768px
- `lg`: >= 1024px
- `xl`: >= 1280px
- `2xl`: >= 1536px

Exemplo:

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  <!-- Cards responsivos aqui -->
</div>
```

## Instruções para IA

Ao criar novos componentes para o PetTransport:

1. Siga a paleta de cores definida neste documento
2. Utilize as classes Tailwind já padronizadas para os componentes
3. Mantenha a consistência com os componentes existentes
4. Respeite o sistema de traduções, utilizando as funções `t()`, `t_field()`, `t_enum()` e `t_ui()`
5. Garanta que o componente seja responsivo
6. Adicione sempre foco visual nos elementos interativos
7. Prefira usar o design system a criar estilos personalizados
8. Utilize os componentes de alerta adequados para feedback ao usuário
9. Adicione animações sutis com `transition-*` quando apropriado
10. Mantenha a nomenclatura dos componentes consistente

### Como Criar Novos Componentes

Para criar novos componentes:

1. Verifique se já existe um componente similar neste documento
2. Use as classes base para manter a aparência consistente
3. Adicione todas as variações necessárias (tamanhos, estados, etc.)
4. Documente o novo componente seguindo o formato deste documento

## Exemplo de Integração de Traduções com Tailwind

```html
<!-- Form field with translation -->
<div class="mb-4">
  <label for="species" class="block text-sm font-medium text-gray-700 mb-1">
    {{ t_field("Pet", "species", current_lang) }}
  </label>
  <select id="species" name="species" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500">
    <option value="">{{ t_ui("placeholders", "select_species", lang=current_lang) }}</option>
    {% for species_value in ["canine", "feline", "bird", "rodent", "other"] %}
    <option value="{{ species_value }}">{{ t_enum("Pet", "species", species_value, current_lang) }}</option>
    {% endfor %}
  </select>
  <p class="mt-1 text-sm text-gray-500">{{ t_ui("help_texts", "species", lang=current_lang) }}</p>
</div>
``` 