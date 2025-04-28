# Formulário de Cadastro de Tutor de Pet - Documentação para IA

Este documento descreve o comportamento e a estrutura do formulário de cadastro de tutores de pets. Use-o como referência para implementar interfaces de usuário semelhantes.

## 1. Sistema de Validação de Formulário

### Estilo e Apresentação de Erros
- Os campos com erro recebem uma classe `.error` que adiciona uma borda vermelha
- Mensagens de erro aparecem em um elemento `.error-message` abaixo de cada campo
- As mensagens de erro têm cor vermelha (#dc3545) e fonte de tamanho 0.85em
- Os rótulos dos campos com erro também ficam vermelhos
- Os erros só são exibidos quando o formulário é enviado ou quando a validação é acionada

### Comportamento da Validação
- O formulário valida todos os campos obrigatórios ao enviar
- Ao encontrar erros, faz rolagem automática (scroll) até o primeiro erro
- O primeiro campo com erro recebe foco automaticamente
- Os grupos de campos condicionais têm validações específicas para cada caso

### Campos Obrigatórios
- Nome Completo (owner_name)
- Email (email) - valida formato de email
- Número de Contato (contact_number)
- Endereço Residencial (residential_address) - deve ser selecionado no mapa
- Opção de CPF (hasCpf) - obrigatório escolher Sim ou Não
- Necessidades Especiais (hasSpecialNeeds) - obrigatório escolher Sim ou Não

### Validações Específicas
- **CPF**: Se "Possui CPF?" = Sim, o campo CPF é obrigatório
- **Passaporte**: Se "Possui CPF?" = Não, o campo Passaporte é obrigatório
- **Detalhes de Necessidades**: Se "Necessidades Especiais?" = Sim, o campo de detalhes é obrigatório
- **Endereço Residencial**: Deve ser um endereço válido com localização no mapa
- **Pets**: Pelo menos um pet deve ser adicionado
- **Campos obrigatórios por pet**: Nome, Raça, Sexo e Data de Nascimento

### Formatação Automática 
- CPF: Formata automaticamente com pontos e traço (123.456.789-00)
- Data: Formata automaticamente com barras (DD/MM/AAAA)
- Microchip: Formata automaticamente com pontos a cada 3 dígitos

## 2. Layout de Duas Colunas e Mapa

### Estrutura do Layout
- O formulário utiliza uma estrutura de tabela para criar duas colunas
- As classes `.form-table`, `.form-row` e `.form-cell` criam a grade
- Cada `.form-row` contém duas `.form-cell` (uma para cada coluna)
- Em dispositivos móveis (tela < 768px), as colunas colapsam para uma única coluna

### Distribuição dos Campos nas Colunas

**Primeira Seção (Informações do Responsável)**
| Coluna Esquerda | Coluna Direita |
|-----------------|----------------|
| Nome Completo | (vazio) |
| Email | Número para contato |
| Possui CPF? | CPF ou Passaporte (condicional) |
| Endereço Residencial | Botão "Usar endereço diferente para entregas" |
| Como soube do meu trabalho? | (vazio) |
| Necessidades de adaptação? | Detalhes das necessidades (condicional) |

**Seção de Mapa**
- O mapa ocupa a largura total do formulário (100%)
- Aparece entre as duas seções de campos
- Altura fixa de 180px com bordas arredondadas

**Seção de Pets**
- Cada pet tem seu próprio grid de duas colunas
- Alguns campos ocupam a largura total (como a foto do pet)

### Responsividade
- Em telas menores que 768px, o layout colapsa para uma coluna
- Os botões de envio e adicionar pet ocupam 100% da largura em telas pequenas
- Os controles do mapa se reorganizam em telas menores

## 3. Campos Dinâmicos Condicionais

### Campo CPF/Passaporte
- Ao clicar em "Sim" para "Possui CPF?": 
  - O campo CPF é exibido
  - O campo Passaporte é escondido
- Ao clicar em "Não" para "Possui CPF?":
  - O campo CPF é escondido
  - O campo Passaporte é exibido
- Ambos começam invisíveis até que uma opção seja selecionada

### Campo de Endereço de Entrega
- Inicialmente apenas o endereço residencial é exibido
- Ao clicar em "Usar endereço diferente para entregas":
  - O campo de endereço de entrega é exibido
  - Os controles do mapa para alternar entre residencial/entrega são exibidos
- Clicar novamente esconde esses elementos

### Campo de Necessidades Especiais
- Ao clicar em "Sim" para "Necessidades de adaptação?":
  - O campo de texto para detalhes é exibido
- Ao clicar em "Não", esse campo é escondido

### Adição Dinâmica de Pets
- O formulário começa com um pet
- O botão "Adicionar Pet" cria novos formulários de pet dinamicamente
- Cada pet adicionado recebe numeração automática (Pet #1, Pet #2, etc.)
- Pets podem ser removidos (exceto o primeiro)
- IDs e nomes dos campos são atualizados automaticamente ao adicionar/remover pets

## 4. Comportamento do Mapa

### Inicialização
- O mapa é inicializado com a API Google Places
- Localização padrão inicial no mapa: São Paulo (-23.550520, -46.633308)
- Zoom inicial: 12

### Funcionalidade de Autocompletar Endereço
- Os campos de endereço utilizam o autocompletar do Google Places
- Restrição para endereços brasileiros apenas (country: 'br')
- Ao selecionar um endereço do autocomplete:
  1. O mapa é atualizado com a nova localização
  2. O zoom é ajustado para 15
  3. Um marcador é adicionado na localização escolhida

### Marcadores do Mapa
- **Endereço Residencial**: Marcador circular azul (#007bff)
- **Endereço de Entrega**: Marcador circular verde (#28a745)
- Os marcadores têm borda branca e tamanho de escala 8

### Alternância entre Endereços
- Botões de alternância permitem visualizar um endereço por vez
- Ao clicar em "Residencial":
  - O mapa centraliza no endereço residencial
  - O botão residencial fica destacado em azul
- Ao clicar em "Entrega":
  - O mapa centraliza no endereço de entrega
  - O botão entrega fica destacado em azul
- Os controles do mapa só são exibidos quando há dois endereços cadastrados

### Campos Ocultos do Endereço
- Cada endereço salva dados completos em campos ocultos:
  - Latitude e Longitude
  - Endereço formatado
  - Cidade
  - Estado
  - País
  - CEP
- Esses campos são enviados com o formulário

## Comportamentos Adicionais

### Botões de Rádio Personalizados
- Os botões de rádio são implementados como botões normais com estado ativo
- Ao clicar em um botão, ele recebe a classe `.active` e a cor azul
- Um campo oculto armazena o valor selecionado

### Formatação e Validação de Dados
- **Datas**: Formatação DD/MM/AAAA, valida meses, dias, datas futuras e muito antigas
- **CPF**: Formata com pontos e traço, valida 11 dígitos
- **Passaporte**: Aceita apenas 8-9 caracteres alfanuméricos maiúsculos
- **Email**: Valida formato básico de email
- **Microchip**: Formata com pontos a cada 3 dígitos, máximo 15 dígitos 