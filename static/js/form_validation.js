// Validações do Formulário
class ValidacaoFormulario {
  static formatarCPF(input) {
    // Remove todos os caracteres não numéricos
    let valor = input.value.replace(/\D/g, '');

    // Limita a 11 dígitos
    valor = valor.substring(0, 11);

    // Aplica a formatação
    if (valor.length > 3) {
      valor = valor.replace(/(\d{3})(\d)/, '$1.$2');
    }
    if (valor.length > 7) {
      valor = valor.replace(/(\d{3})(\d)/, '$1.$2');
    }
    if (valor.length > 11) {
      valor = valor.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    }

    // Atualiza o valor do input
    input.value = valor;
  }

  static formatarData(input) {
    // Remove caracteres não numéricos
    let valor = input.value.replace(/\D/g, '');

    // Limita a 8 dígitos (DDMMAAAA)
    valor = valor.substring(0, 8);

    // Aplica a formatação
    if (valor.length > 4) {
      valor = valor.replace(/(\d{2})(\d{2})(\d{4})/, '$1/$2/$3');
    } else if (valor.length > 2) {
      valor = valor.replace(/(\d{2})(\d{2})/, '$1/$2/');
    }

    // Atualiza o valor do input
    input.value = valor;
  }
}

// Função para formatar o microchip
function formatMicrochip(input) {
  // Remove caracteres não numéricos
  let valor = input.value.replace(/\D/g, '');

  // Limita a 15 dígitos
  valor = valor.substring(0, 15);

  // Aplica formatação com pontos a cada 3 dígitos
  if (valor.length > 3) {
    valor = valor.replace(/(\d{3})(\d)/, '$1.$2');
  }
  if (valor.length > 7) {
    valor = valor.replace(/(\d{3}\.\d{3})(\d)/, '$1.$2');
  }
  if (valor.length > 11) {
    valor = valor.replace(/(\d{3}\.\d{3}\.\d{3})(\d)/, '$1.$2');
  }

  // Atualiza o valor do input
  input.value = valor;
}

// Variável global para armazenar o último petId aberto
window.__lastOpenedPetId = null;

function abrirModalPet(button) {
  const username = button.dataset.username;
  const petName = button.dataset.nomePet;
  const petCard = button.closest('.pet-card');
  // Armazena o petId globalmente
  window.__lastOpenedPetId = petCard ? petCard.dataset.petId : null;

  // Preenche os campos do formulário com os dados do pet
  document.getElementById('pet_name').value = petName;
  document.getElementById('species').value = petCard.dataset.especie;
  document.getElementById('breed').value = petCard.dataset.raca;
  document.getElementById('fur_color').value = petCard.dataset.furColor || '';
  document.getElementById('gender').value = petCard.dataset.sexo;

  // Formata a data para o campo date
  const birthDate = new Date(petCard.dataset.nascimento);
  const formattedDate = birthDate.toISOString().split('T')[0];
  document.getElementById('birth_date').value = formattedDate;

  document.getElementById('microchip').value = petCard.dataset.microchip;
  document.getElementById('weight').value = petCard.dataset.weight || '';
  document.getElementById('username_pet').value = username;
  document.getElementById('nome_original_pet').value = petName;

  // Atualiza a imagem de preview
  const imgElement = petCard.querySelector('img');
  if (imgElement) {
    document.getElementById('foto_atual').src = imgElement.src;
  } else {
    document.getElementById('foto_atual').src = "";
  }

  // Exibe o modal
  document.getElementById('modal-pet').classList.remove('hidden');
  document.getElementById('modal-pet').classList.add('flex');
}

function abrirModalAdicionarPet(username) {
  // Reseta o formulário para garantir que não haja dados preenchidos de operações anteriores
  document.getElementById('form-adicionar-pet').reset();

  // Define o username para o qual o pet será adicionado
  document.getElementById('username_pet_novo').value = username;

  // Exibe o modal
  document.getElementById('modal-adicionar-pet').classList.remove('hidden');
  document.getElementById('modal-adicionar-pet').classList.add('flex');
}

function fecharModal(modalId) {
  document.getElementById(modalId).classList.add('hidden');
  document.getElementById(modalId).classList.remove('flex');
}

function triggerFileInput(element, username, petName, petId) {
  petId = petId || window.__lastOpenedPetId;
  // Cria um input de arquivo temporário
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';

  input.onchange = function (e) {
    if (input.files && input.files[0]) {
      const formData = new FormData();
      formData.append('photo', input.files[0]);
      formData.append('username', username);
      formData.append('pet_name', petName);
      formData.append('pet_id', petId);

      // Usa o elemento clicado para encontrar o container correto
      let photoContainer = element;
      // Se não for o container, procura o mais próximo
      if (!photoContainer.classList.contains('w-16') || !photoContainer.classList.contains('h-16')) {
        photoContainer = element.closest('.w-16.h-16');
      }
      if (!photoContainer) {
        console.warn('Photo container not found for element:', element);
        alert('Não foi possível encontrar o container da foto. Recarregue a página.');
        return;
      }
      photoContainer.innerHTML = '<div class="w-full h-full flex items-center justify-center bg-gray-200"><svg class="w-5 h-5 text-gray-500 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg></div>';

      fetch('/atualizar_foto_pet', {
        method: 'POST',
        body: formData
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            const timestamp = new Date().getTime();
            photoContainer.innerHTML = `<img src="${data.photo_url}?t=${timestamp}" alt="Foto de ${petName}" class="w-full h-full object-cover">
          <div class="absolute inset-0 bg-black bg-opacity-30 opacity-0 hover:opacity-100 flex items-center justify-center text-white text-xs transition-opacity">
            <svg class="w-4 h-4 mr-1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 5a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V7a2 2 0 00-2-2h-1.586a1 1 0 01-.707-.293l-1.121-1.121A2 2 0 0011.172 3H8.828a2 2 0 00-1.414.586L6.293 4.707A1 1 0 015.586 5H4zm6 9a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
            </svg>
          </div>`;
          } else {
            alert("Erro ao atualizar foto: " + (data.error || "Erro desconhecido"));
            location.reload();
          }
        })
        .catch(error => {
          console.error('Erro:', error);
          alert('Erro ao atualizar foto do pet. Tente novamente.');
          location.reload();
        });
    }
  };
  input.click();
}

// Configurações iniciais para formulários
document.addEventListener('DOMContentLoaded', function () {
  // Filtro de pesquisa para usuários
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const term = this.value.toLowerCase().trim();
      const cards = document.querySelectorAll('.usuario-card');

      cards.forEach(function (card) {
        const tutorName = card.dataset.tutor || '';
        const petNames = card.dataset.pets || '';

        if (tutorName.includes(term) || petNames.includes(term)) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  }

  // Adiciona validação para os formulários de pet
  const formEditarPet = document.getElementById('form-editar-pet');
  if (formEditarPet) {
    formEditarPet.addEventListener('submit', function (e) {
      let isValid = true;
      const requiredFields = formEditarPet.querySelectorAll('[required]');

      // Remove todos os avisos de erro anteriores
      formEditarPet.querySelectorAll('.error-message').forEach(elem => {
        elem.textContent = '';
        elem.classList.add('hidden');
      });

      // Verifica campos obrigatórios
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          const errorDiv = document.createElement('div');
          errorDiv.className = 'error-message text-red-600 text-xs mt-1';
          errorDiv.textContent = 'Este campo é obrigatório';
          field.classList.add('border-red-500');

          // Insere mensagem de erro após o campo
          const fieldParent = field.closest('div');
          const existingError = fieldParent.querySelector('.error-message');
          if (existingError) {
            existingError.textContent = 'Este campo é obrigatório';
            existingError.classList.remove('hidden');
          } else {
            fieldParent.appendChild(errorDiv);
          }
        }
      });

      if (!isValid) {
        e.preventDefault();
        // Rola até o primeiro erro
        const firstError = formEditarPet.querySelector('.error-message:not(.hidden)');
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    });
  }

  // Adiciona validação para o formulário de adicionar pet
  const formAdicionarPet = document.getElementById('form-adicionar-pet');
  if (formAdicionarPet) {
    formAdicionarPet.addEventListener('submit', function (e) {
      let isValid = true;
      const requiredFields = formAdicionarPet.querySelectorAll('[required]');

      // Remove todos os avisos de erro anteriores
      formAdicionarPet.querySelectorAll('.error-message').forEach(elem => {
        elem.textContent = '';
        elem.classList.add('hidden');
      });

      // Verifica campos obrigatórios
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          const errorDiv = document.createElement('div');
          errorDiv.className = 'error-message text-red-600 text-xs mt-1';
          errorDiv.textContent = 'Este campo é obrigatório';
          field.classList.add('border-red-500');

          // Insere mensagem de erro após o campo
          const fieldParent = field.closest('div');
          const existingError = fieldParent.querySelector('.error-message');
          if (existingError) {
            existingError.textContent = 'Este campo é obrigatório';
            existingError.classList.remove('hidden');
          } else {
            fieldParent.appendChild(errorDiv);
          }
        }
      });

      if (!isValid) {
        e.preventDefault();
        // Rola até o primeiro erro
        const firstError = formAdicionarPet.querySelector('.error-message:not(.hidden)');
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    });
  }
}); 