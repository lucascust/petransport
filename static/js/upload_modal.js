// upload_modal.js
// Lógica do modal de upload de documento (AJAX, validação, preview, progresso simulado)

(function () {
  // Seletores principais
  const modal = document.getElementById('modal-upload-documento');
  const dropArea = document.getElementById('upload-drop-area');
  const fileInput = document.getElementById('input-upload-documento');
  const filePreview = document.getElementById('file-preview');
  const fileNameSpan = document.getElementById('file-name');
  const fileSizeSpan = document.getElementById('file-size');
  const fileError = document.getElementById('file-error');
  const fileProgressBar = document.getElementById('file-progress-bar');
  const fileProgressInner = fileProgressBar ? fileProgressBar.querySelector('div') : null;
  const removeFileBtn = document.getElementById('remove-file-btn');
  const uploadLabel = document.getElementById('upload-label');
  const submitBtn = document.getElementById('submit-upload-btn');
  const cancelBtn = document.getElementById('cancel-upload-btn');
  const closeBtn = document.getElementById('close-upload-modal');

  // Configurações
  const MAX_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/png',
    'image/jpeg',
    'image/svg+xml',
  ];
  const ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'svg'];

  let selectedFile = null;
  let isUploading = false;

  // Variáveis para parâmetros dinâmicos
  let uploadUsuario = null;
  let uploadViagemId = null;
  let uploadTipo = null;
  let uploadDocumento = null;
  let uploadPetId = null;

  // Global flag to track initialization
  let listenersInitialized = false;

  function initializeFileUploadListeners() {
    // Only initialize once
    if (listenersInitialized) return;

    const dropArea = document.getElementById('upload-drop-area');
    const fileInput = document.getElementById('input-upload-documento');

    // Clean up any existing listeners first (optional but safer)
    const newDropArea = dropArea.cloneNode(true);
    dropArea.parentNode.replaceChild(newDropArea, dropArea);

    // Get fresh reference after replacement
    const freshDropArea = document.getElementById('upload-drop-area');
    const freshFileInput = document.getElementById('input-upload-documento');

    // Add click listener
    freshDropArea.addEventListener('click', (e) => {
      if (e.target === freshFileInput) return;
      freshFileInput.click();
    });

    // Add drag and drop listeners
    freshDropArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      freshDropArea.classList.add('bg-blue-50', 'border-blue-400');
    });

    freshDropArea.addEventListener('dragleave', (e) => {
      e.preventDefault();
      freshDropArea.classList.remove('bg-blue-50', 'border-blue-400');
    });

    freshDropArea.addEventListener('drop', (e) => {
      e.preventDefault();
      freshDropArea.classList.remove('bg-blue-50', 'border-blue-400');
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        freshFileInput.files = dataTransfer.files;
        handleFile(file);
      }
    });

    freshFileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFile(e.target.files[0]);
      }
    });

    // Set flag to prevent re-initialization
    listenersInitialized = true;
  }

  document.addEventListener('DOMContentLoaded', initializeFileUploadListeners);

  // --- Funções auxiliares ---
  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function resetModal() {
    selectedFile = null;
    isUploading = false;
    fileInput.value = '';
    filePreview.classList.add('hidden');
    fileError.classList.add('hidden');
    fileError.textContent = '';
    if (fileProgressBar) {
      fileProgressBar.classList.add('hidden');
      if (fileProgressInner) fileProgressInner.style.width = '0%';
    }
    submitBtn.disabled = false;
  }

  function showFile(file) {
    fileNameSpan.textContent = file.name;
    fileSizeSpan.textContent = formatSize(file.size);
    filePreview.classList.remove('hidden');
    fileError.classList.add('hidden');
    if (fileProgressBar) fileProgressBar.classList.add('hidden');
  }

  function showError(msg) {
    fileError.textContent = msg;
    fileError.classList.remove('hidden');
    filePreview.classList.add('hidden');
    selectedFile = null;
  }

  function validateFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return 'Tipo de arquivo não permitido.';
    }
    if (!ALLOWED_TYPES.includes(file.type) && !file.type.startsWith('image/')) {
      return 'Tipo de arquivo não permitido.';
    }
    if (file.size > MAX_SIZE) {
      return 'Arquivo muito grande (máx 10MB).';
    }
    if (file.size === 0) {
      return 'Arquivo vazio ou corrompido.';
    }
    return null;
  }

  function handleFile(file) {
    const error = validateFile(file);
    if (error) {
      showError(error);
      return;
    }
    selectedFile = file;
    showFile(file);
  }

  // Remove file
  removeFileBtn.addEventListener('click', (e) => {
    e.preventDefault();
    resetModal();
  });

  // --- Modal open/close logic ---
  function openUploadModal(tipo, documento, pet_id, usuario, viagem_id) {
    // Permitir chamada tanto com quanto sem viagem_id
    uploadTipo = tipo;
    uploadDocumento = documento;
    uploadPetId = pet_id || null;
    uploadUsuario = usuario || null;
    uploadViagemId = viagem_id || null;
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    resetModal();
  }
  function closeModal() {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
    resetModal();
  }
  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);
  // Optional: close on background click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // --- AJAX Upload (simulated progress) ---
  submitBtn.addEventListener('click', function (e) {
    e.preventDefault();
    if (!selectedFile || isUploading) return;
    fileError.classList.add('hidden');
    fileError.textContent = '';
    submitBtn.disabled = true;
    isUploading = true;
    // Show progress bar
    if (fileProgressBar) fileProgressBar.classList.remove('hidden');
    if (fileProgressInner) fileProgressInner.style.width = '0%';

    // Simulate progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 30 + 10; // random step
      if (progress >= 100) progress = 100;
      if (fileProgressInner) fileProgressInner.style.width = progress + '%';
      if (progress >= 100) {
        clearInterval(interval);
        // Do AJAX upload
        doUpload();
      }
    }, 200);
  });

  function doUpload() {
    const formData = new FormData();
    formData.append('documento', selectedFile);
    // Adicionar campos extras
    if (uploadPetId) formData.append('pet_id', uploadPetId);
    // Construir URL correta
    let url = '/upload_document'; // fallback
    if (uploadUsuario && uploadTipo && uploadDocumento) {
      if (uploadViagemId) {
        // Upload de documento em viagem
        url = `/${uploadUsuario}/upload_documento/${uploadViagemId}/${uploadTipo}/${uploadDocumento}`;
        if (uploadPetId) {
          url += `?pet_id=${encodeURIComponent(uploadPetId)}`;
        }
      } else {
        // Upload fora de viagem
        url = `/${uploadUsuario}/upload_documento/None/${uploadTipo}/${uploadDocumento}`;
        if (uploadPetId) {
          url += `?pet_id=${encodeURIComponent(uploadPetId)}`;
        }
      }
    }
    fetch(url, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    })
      .then(async (response) => {
        if (!response.ok) {
          const data = await response.json().catch(() => ({}));
          throw new Error(data.error || 'Erro ao enviar o documento.');
        }
        return response.json();
      })
      .then((data) => {
        closeModal();
        localStorage.setItem('showToastAfterReload', JSON.stringify({
          type: 'success',
          message: 'Documento enviado com sucesso!'
        }));
        window.location.reload();
      })
      .catch((err) => {
        showError(err.message || 'Erro ao enviar o documento.');
        submitBtn.disabled = false;
        isUploading = false;
        if (fileProgressBar) fileProgressBar.classList.add('hidden');
        if (fileProgressInner) fileProgressInner.style.width = '0%';
        // Exibir toast de erro via Alpine store
        if (window.Alpine && Alpine.store && Alpine.store('toast')) {
          Alpine.store('toast').showToast('error', err.message || 'Erro ao enviar o documento.');
        }
      });
  }

  // Expor globalmente a nova função
  window.openUploadModal = openUploadModal;
})(); 