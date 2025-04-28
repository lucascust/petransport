/**
 * Document Manager Module
 * Handles document uploads, viewing, and management
 */

// Document Management Namespace - Global variables and utilities
const DocManager = {
  // Document type translations
  translations: {
    // Pet documents
    'vaccinationCard': 'Carteira de Vacinação',
    'microchipCertificate': 'Certificado de Microchip',
    'rabiesSerologyReport': 'Relatório de Sorologia Antirrábica',
    'leishmaniasisSerologyReport': 'Relatório de Sorologia para Leishmaniose',
    'importPermit': 'Permissão de Importação',
    'petPassport': 'Passaporte do Pet',
    'cvi': 'CVI (Certificado Veterinário Internacional)',
    'exportAuthorization': 'Autorização de Exportação',
    'arrivalNotice': 'Notificação de Chegada',
    'endorsedCvi': 'CVI Endossado',
    'awbCargo': 'AWB Cargo',
    'petFacilities': 'Instalações para Pet',

    // Human documents
    'identityDocument': 'Documento de Identidade',
    'passport': 'Passaporte',
    'travelTicket': 'Passagem',
    'travelAuthorization': 'Autorização de Viagem',
    'carDocument': 'Documento do Carro',
    'addressProof': 'Comprovante de Endereço',
    'cviIssuanceAuthorization': 'Autorização de Emissão do CVI'
  },

  // Document stats storage
  stats: {
    petDocs: [],
    petDocuments: {},
    humanDocs: [],
    humanDocuments: {}
  },

  // Initialize document stats
  init: function (petDocs, petDocuments, humanDocs, humanDocuments) {
    this.stats.petDocs = petDocs;
    this.stats.petDocuments = petDocuments;
    this.stats.humanDocs = humanDocs;
    this.stats.humanDocuments = humanDocuments;

    // Calculate and cache document counts
    this.calculateAllCounts();
  },

  // Cache for document counts
  counts: {
    perPet: {}, // {petId: {total: X, completed: Y}}
    human: { total: 0, completed: 0 }
  },

  // Calculate document counts for all pets and humans
  calculateAllCounts: function () {
    // Calculate for humans
    this.counts.human.total = this.stats.humanDocs.length;
    this.counts.human.completed = this.getHumanCompletedCount();

    // Calculate for each pet
    for (const petId in this.stats.petDocuments) {
      this.counts.perPet[petId] = {
        total: this.stats.petDocs.length,
        completed: this.getPetCompletedCount(petId)
      };
    }
  },

  // Get count of completed documents for a pet
  getPetCompletedCount: function (petId) {
    let count = 0;
    if (petId in this.stats.petDocuments) {
      for (const docType of this.stats.petDocs) {
        if (docType in this.stats.petDocuments[petId] && this.stats.petDocuments[petId][docType]) {
          count++;
        }
      }
    }
    return count;
  },

  // Get count of completed human documents
  getHumanCompletedCount: function () {
    let count = 0;
    for (const docType of this.stats.humanDocs) {
      if (docType in this.stats.humanDocuments && this.stats.humanDocuments[docType]) {
        count++;
      }
    }
    return count;
  },

  // Calculate percentage of completed documents
  getCompletionPercentage: function (completed, total) {
    return total > 0 ? Math.floor((completed / total) * 100) : 0;
  },

  // Get the appropriate CSS width class based on percentage
  getProgressWidthClass: function (percentage) {
    const brackets = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
    for (let i = 0; i < brackets.length - 1; i++) {
      if (percentage <= brackets[i + 1]) {
        return `w-${brackets[i + 1]}`;
      }
    }
    return 'w-0';
  },

  // Check if a document is uploaded
  isDocumentUploaded: function (docType, petId = null) {
    if (petId) {
      return petId in this.stats.petDocuments &&
        docType in this.stats.petDocuments[petId] &&
        this.stats.petDocuments[petId][docType];
    } else {
      return docType in this.stats.humanDocuments &&
        this.stats.humanDocuments[docType];
    }
  },

  // Get translated document name
  getDocumentName: function (docType) {
    return this.translations[docType] || docType;
  },

  // Get document ID if available
  getDocumentId: function (docType, petId = null) {
    if (petId) {
      if (this.isDocumentUploaded(docType, petId)) {
        return this.stats.petDocuments[petId][docType]._id || '';
      }
    } else {
      if (this.isDocumentUploaded(docType)) {
        return this.stats.humanDocuments[docType]._id || '';
      }
    }
    return '';
  },

  // Get document path if available
  getDocumentPath: function (docType, petId = null) {
    if (petId) {
      if (this.isDocumentUploaded(docType, petId)) {
        return this.stats.petDocuments[petId][docType].path || '';
      }
    } else {
      if (this.isDocumentUploaded(docType)) {
        return this.stats.humanDocuments[docType].path || '';
      }
    }
    return '';
  },

  // Update document status and return updated data
  updateDocumentStatus: function (tipo, documento, pet_id, documentPath, storage_type = '', public_url = '') {
    // Update internal state
    if (tipo === 'pet') {
      if (!this.stats.petDocuments[pet_id]) {
        this.stats.petDocuments[pet_id] = {};
      }
      this.stats.petDocuments[pet_id][documento] = {
        path: documentPath,
        _id: '', // Will be set by the server response
        storage_type: storage_type,
        public_url: public_url
      };

      // Recalculate pet document counts
      this.counts.perPet[pet_id] = {
        total: this.stats.petDocs.length,
        completed: this.getPetCompletedCount(pet_id)
      };
    } else {
      this.stats.humanDocuments[documento] = {
        path: documentPath,
        _id: '', // Will be set by the server response
        storage_type: storage_type,
        public_url: public_url
      };

      // Recalculate human document counts
      this.counts.human.completed = this.getHumanCompletedCount();
    }

    const documentUrl = storage_type === 'firebase' && public_url ?
      public_url : `/static/uploads/${documentPath}`;

    return {
      tipo,
      documento,
      pet_id,
      documentUrl,
      documentPath,
      isCompleted: true,
      storage_type,
      public_url,
      percentage: tipo === 'pet'
        ? this.getCompletionPercentage(this.counts.perPet[pet_id].completed, this.counts.perPet[pet_id].total)
        : this.getCompletionPercentage(this.counts.human.completed, this.counts.human.total)
    };
  },

  // Get progress data
  getProgressData: function (tipo, pet_id = null) {
    if (tipo === 'pet' && pet_id) {
      const petData = this.counts.perPet[pet_id];
      if (!petData) return null;

      return {
        completed: petData.completed,
        total: petData.total,
        percentage: this.getCompletionPercentage(petData.completed, petData.total),
        widthClass: this.getProgressWidthClass(this.getCompletionPercentage(petData.completed, petData.total))
      };
    } else {
      return {
        completed: this.counts.human.completed,
        total: this.counts.human.total,
        percentage: this.getCompletionPercentage(this.counts.human.completed, this.counts.human.total),
        widthClass: this.getProgressWidthClass(this.getCompletionPercentage(this.counts.human.completed, this.counts.human.total))
      };
    }
  }
};

// Export for global access
window.DocManager = DocManager;

document.addEventListener('DOMContentLoaded', function () {
  const portal = document.getElementById('tooltip-portal-root');
  let hideTimeout = null;

  function showTooltip(e) {
    const trigger = e.currentTarget;
    const tooltipText = trigger.getAttribute('data-tooltip');
    if (!tooltipText) return;

    // Remove tooltip antigo
    portal.innerHTML = '';

    // Cria tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'rounded-lg border bg-white text-xs text-gray-700 shadow-lg px-3 py-2';
    tooltip.style.position = 'fixed';
    tooltip.style.pointerEvents = 'auto';
    tooltip.style.maxWidth = '288px';
    tooltip.style.minWidth = '200px';
    tooltip.style.zIndex = 9999;
    tooltip.textContent = tooltipText;

    // Calcula posição
    const rect = trigger.getBoundingClientRect();
    tooltip.style.left = `${rect.left}px`;
    tooltip.style.top = `${rect.bottom + 8}px`;

    portal.appendChild(tooltip);

    // Remove ao sair
    trigger.addEventListener('mouseleave', hideTooltip);
    tooltip.addEventListener('mouseenter', () => clearTimeout(hideTimeout));
    tooltip.addEventListener('mouseleave', hideTooltip);
  }

  function hideTooltip() {
    hideTimeout = setTimeout(() => { portal.innerHTML = ''; }, 100);
  }

  // Ativa para todos os triggers
  function bindDocTooltips() {
    document.querySelectorAll('.doc-tooltip-trigger').forEach(el => {
      el.addEventListener('mouseenter', showTooltip);
      el.addEventListener('mouseleave', hideTooltip);
    });
  }

  bindDocTooltips();
  // Se tooltips forem renderizados dinamicamente, chame bindDocTooltips() novamente após renderização.
}); 