// Função para atualizar a barra de progresso
function atualizarBarraProgresso() {
  const progressBar = document.querySelector('.progress');
  if (progressBar) {
    const diasRestantes = parseInt(document.querySelector('.status-info p').textContent.match(/\d+/)[0]);
    const porcentagem = ((60 - diasRestantes) / 60) * 100;
    progressBar.style.width = `${porcentagem}%`;
  }
}

// Função para verificar se o usuário está inativo
function verificarInatividade() {
  let tempoInativo = 0;
  const tempoMaximo = 30 * 60 * 1000; // 30 minutos

  function resetarTempo() {
    tempoInativo = 0;
  }

  function verificarTempo() {
    tempoInativo += 1000;
    if (tempoInativo >= tempoMaximo) {
      alert('Sua sessão está prestes a expirar. Por favor, atualize a página para manter o acesso.');
    }
  }

  // Eventos para resetar o tempo
  ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(evento => {
    document.addEventListener(evento, resetarTempo);
  });

  // Verificar a cada segundo
  setInterval(verificarTempo, 1000);
}

// Função para carregar PDFs
function carregarPDF(url) {
  const iframe = document.createElement('iframe');
  iframe.src = url;
  iframe.style.width = '100%';
  iframe.style.height = '600px';
  iframe.style.border = 'none';

  const container = document.querySelector('.pdf-container');
  if (container) {
    container.innerHTML = '';
    container.appendChild(iframe);
  }
}

// Função para atualizar checklist
function atualizarChecklist(itemId) {
  const checkbox = document.getElementById(itemId);
  if (checkbox) {
    const status = checkbox.checked;
    // Aqui você pode adicionar uma chamada AJAX para salvar o status
    console.log(`Item ${itemId} atualizado para ${status}`);
  }
}

// Funções para gerenciar o upload de foto do pet
function inicializarUploadFoto() {
  console.log('Inicializando componente de upload de foto do pet...');

  // Elementos do DOM
  const photoModal = document.getElementById('petPhotoModal');
  const closeModalButton = document.getElementById('closePetPhotoModal');
  const cancelButton = document.getElementById('cancelPhotoButton');
  const confirmButton = document.getElementById('confirmPhotoButton');
  const dropArea = document.getElementById('dropArea');
  const imagePreview = document.getElementById('imagePreview');
  const previewArea = document.getElementById('previewArea');
  const uploadText = document.getElementById('uploadText');
  const uploadIcon = document.getElementById('uploadIcon');
  const fileNameDisplay = document.getElementById('fileNameDisplay');
  const changePhotoButton = document.getElementById('changePhoto');
  const removePhotoButton = document.getElementById('removePhoto');

  // Flag global para controlar se o diálogo de arquivo já está aberto
  window.isFileDialogOpen = false;

  // Variáveis para gerenciar o estado
  let selectedFile = null;
  let currentInputElement = null;
  let currentTextElement = null;

  if (!photoModal) {
    console.error('Modal não encontrado!');
    return;
  }

  // Processar os botões de upload iniciais
  initializeUploadButtons();

  // Observar novos pets adicionados
  observeNewPets();

  function initializeUploadButtons() {
    // Botão inicial
    const initialButton = document.getElementById('openPetPhotoModal');
    if (initialButton) {
      initialButton.addEventListener('click', handleOpenModal);
    }

    // Botões adicionados dinamicamente
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('openPetPhotoModal') ||
        (e.target.closest('button') && e.target.closest('button').classList.contains('openPetPhotoModal'))) {
        handleOpenModal.call(e.target.closest('button'), e);
      }
    });
  }

  function observeNewPets() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length) {
          mutation.addedNodes.forEach(node => {
            if (node.nodeType === 1) { // Element node
              const buttons = node.querySelectorAll('.openPetPhotoModal');
              buttons.forEach(btn => {
                btn.addEventListener('click', handleOpenModal);
              });
            }
          });
        }
      });
    });

    const petsContainer = document.getElementById('pets-container');
    if (petsContainer) {
      observer.observe(petsContainer, { childList: true, subtree: true });
    }
  }

  function handleOpenModal(e) {
    e.preventDefault();
    e.stopPropagation();

    const button = this.tagName === 'BUTTON' ? this : this.closest('button');

    // Encontrar o input associado
    const input = button.id === 'openPetPhotoModal'
      ? document.getElementById('petPhotoInput')
      : button.nextElementSibling.nextElementSibling;

    // Encontrar o elemento de texto
    const textElement = button.id === 'openPetPhotoModal'
      ? document.getElementById('selectedPhotoText')
      : button.querySelector('.selectedPhotoText');

    // Armazenar referências
    currentInputElement = input;
    currentTextElement = textElement;

    // Abrir o modal
    photoModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Resetar o estado do upload
    resetUpload();
  }

  // Fechar o modal
  const closeModal = () => {
    photoModal.classList.add('hidden');
    document.body.style.overflow = '';
    window.isFileDialogOpen = false; // Reset global flag
  };

  closeModalButton.addEventListener('click', closeModal);
  cancelButton.addEventListener('click', closeModal);

  // Fechar modal quando clicar fora da área
  photoModal.addEventListener('click', (e) => {
    if (e.target === photoModal) {
      closeModal();
    }
  });

  // Simplify: dropArea só abre seletor de arquivo uma vez
  dropArea.addEventListener('click', handleBrowseClick);
  changePhotoButton.addEventListener('click', (e) => {
    e.stopPropagation();
    handleBrowseClick(e);
  });

  // Manipulador unificado para selecionar arquivo
  function handleBrowseClick(e) {
    e.preventDefault();
    e.stopPropagation();

    // Evitar múltiplas aberturas
    if (window.isFileDialogOpen) return;
    window.isFileDialogOpen = true;

    // Usar um input temporário para evitar bugs
    const tempInput = document.createElement('input');
    tempInput.type = 'file';
    tempInput.accept = 'image/*';
    document.body.appendChild(tempInput);

    tempInput.onchange = function () {
      if (this.files.length > 0) {
        processFile(this.files[0]);
      }
      // Limpar após uso
      document.body.removeChild(this);
      // Não resetamos a flag aqui para evitar abertura duplicada
    };

    // Abrir seletor de arquivo
    tempInput.click();
  }

  // Suporte para arrastar e soltar
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(event => {
    dropArea.addEventListener(event, preventDefault);
  });

  function preventDefault(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  dropArea.addEventListener('dragenter', () => {
    dropArea.classList.add('border-blue-500', 'bg-blue-50');
  });

  dropArea.addEventListener('dragover', () => {
    dropArea.classList.add('border-blue-500', 'bg-blue-50');
  });

  dropArea.addEventListener('dragleave', () => {
    dropArea.classList.remove('border-blue-500', 'bg-blue-50');
  });

  dropArea.addEventListener('drop', (e) => {
    dropArea.classList.remove('border-blue-500', 'bg-blue-50');
    if (e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  });

  // Remover foto
  removePhotoButton.addEventListener('click', (e) => {
    e.stopPropagation();
    resetUpload();
  });

  // Processar o arquivo de imagem
  function processFile(file) {
    if (!file.type.match('image.*')) return;

    selectedFile = file;

    // Mostrar área de preview e esconder ícones de upload
    previewArea.classList.remove('hidden');
    uploadText.classList.add('hidden');
    uploadIcon.classList.add('hidden');

    // Exibir nome do arquivo
    fileNameDisplay.textContent = file.name;
    fileNameDisplay.classList.remove('hidden');

    // Habilitar botão de confirmação
    confirmButton.disabled = false;

    // Gerar preview da imagem
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // Resetar o estado de upload
  function resetUpload() {
    selectedFile = null;
    imagePreview.src = '';
    previewArea.classList.add('hidden');
    uploadText.classList.remove('hidden');
    uploadIcon.classList.remove('hidden');
    fileNameDisplay.classList.add('hidden');
    confirmButton.disabled = true;
    window.isFileDialogOpen = false;
  }

  // Confirmar a foto
  confirmButton.addEventListener('click', () => {
    if (!selectedFile || !currentInputElement || !currentTextElement) return;

    // Atualizar texto do botão
    currentTextElement.textContent = selectedFile.name;
    currentTextElement.classList.remove('text-gray-400');

    // Copiar o arquivo para o input do formulário
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(selectedFile);
    currentInputElement.files = dataTransfer.files;

    // Reset flag ao fechar modal
    closeModal();

    // Permitir nova seleção após pequeno delay
    setTimeout(() => {
      window.isFileDialogOpen = false;
    }, 500);
  });
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  atualizarBarraProgresso();
  verificarInatividade();
  inicializarUploadFoto();
});

// --- Upload Modal Logic ---
// (Removed duplicate upload modal event listeners to avoid conflicts. All upload modal logic is now handled in upload_modal.js)
// ... existing code ... 