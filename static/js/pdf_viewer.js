/**
 * PDF Viewer Module
 * Handles PDF viewing functionality
 */

// Initialize the PDF viewer
function initPdfViewer() {
  // Configure PDF.js worker
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';

  // References to DOM elements
  const elements = {
    // PDF Viewer Modal
    pdfViewerModal: document.getElementById('pdfViewerModal'),
    closePdfModal: document.getElementById('closePdfModal'),
    pdfTitle: document.getElementById('pdfTitle'),
    pdfCanvasElement: document.getElementById('pdfCanvas'),
    pdfLoading: document.getElementById('pdfLoading'),
    pdfCurrentPage: document.getElementById('pdfCurrentPage'),
    pdfTotalPages: document.getElementById('pdfTotalPages'),
    pdfCurrentPageMobile: document.getElementById('pdfCurrentPageMobile'),
    pdfTotalPagesMobile: document.getElementById('pdfTotalPagesMobile'),
    pdfZoomLevel: document.getElementById('pdfZoomLevel'),

    // PDF Actions - Desktop
    pdfDownloadBtn: document.getElementById('pdfDownloadBtn'),
    pdfDeleteBtn: document.getElementById('pdfDeleteBtn'),
    pdfFirstPage: document.getElementById('pdfFirstPage'),
    pdfPrevPage: document.getElementById('pdfPrevPage'),
    pdfNextPage: document.getElementById('pdfNextPage'),
    pdfLastPage: document.getElementById('pdfLastPage'),
    pdfZoomIn: document.getElementById('pdfZoomIn'),
    pdfZoomOut: document.getElementById('pdfZoomOut'),
    pdfRotate: document.getElementById('pdfRotate'),
    pdfFullscreen: document.getElementById('pdfFullscreen'),

    // PDF Actions - Mobile
    pdfPrevPageMobile: document.getElementById('pdfPrevPage-mobile'),
    pdfNextPageMobile: document.getElementById('pdfNextPage-mobile'),
    pdfZoomOutMobile: document.getElementById('pdfZoomOut-mobile'),
    pdfRotateMobile: document.getElementById('pdfRotate-mobile'),
    pdfDownloadBtnMobile: document.getElementById('pdfDownloadBtn-mobile'),
    pdfDeleteBtnMobile: document.getElementById('pdfDeleteBtn-mobile')
  };

  // Initialize canvas context
  const pdfCanvasContext = elements.pdfCanvasElement ? elements.pdfCanvasElement.getContext('2d') : null;

  // PDF Viewer State
  const pdfState = {
    document: null,
    pageNum: 1,
    scale: 1.0,
    rotation: 0,
    rendering: false,
    numPages: 0,
    pagePending: null,
    currentUrl: null
  };

  // Load and display a PDF
  function loadPDF(url, title) {
    console.log("Loading PDF:", url);
    elements.pdfLoading.classList.remove('hidden');
    pdfState.currentUrl = url;

    // Reset view settings
    pdfState.pageNum = 1;
    pdfState.scale = 1.0;
    pdfState.rotation = 0;
    elements.pdfZoomLevel.textContent = '100%';

    // Configure loading task with withCredentials option for CORS
    const loadingTask = pdfjsLib.getDocument({
      url: url,
      withCredentials: false, // Needed for Firebase Storage cross-origin
      cMapUrl: 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.4.120/cmaps/',
      cMapPacked: true,
    });

    // Load the PDF
    loadingTask.promise.then(function (pdf) {
      pdfState.document = pdf;
      pdfState.numPages = pdf.numPages;

      // Update UI
      elements.pdfTitle.textContent = title;
      elements.pdfTotalPages.textContent = pdfState.numPages;
      elements.pdfTotalPagesMobile.textContent = pdfState.numPages;

      // Render first page
      renderPDFPage(pdfState.pageNum);

      // Update navigation state
      updatePDFNavigationState();
    }).catch(function (error) {
      console.error('Error loading PDF:', error);
      elements.pdfLoading.classList.add('hidden');
      // Notify parent window of error
      if (window.showDocumentError) {
        window.showDocumentError();
      }
    });
  }

  // Render a specific page of the PDF
  function renderPDFPage(pageNum) {
    if (pdfState.rendering) {
      pdfState.pagePending = pageNum;
      return;
    }

    pdfState.rendering = true;
    elements.pdfLoading.classList.remove('hidden');

    pdfState.document.getPage(pageNum).then(function (page) {
      // Get the viewport at scale 1.0
      const originalViewport = page.getViewport({ scale: 1.0, rotation: pdfState.rotation });

      // Calculate the appropriate scale to fit the container width
      const container = elements.pdfCanvasElement.parentElement;
      const containerWidth = container.clientWidth - 40; // Subtract padding

      // Calculate scale based on width only
      const widthScale = containerWidth / originalViewport.width;

      // Always fit horizontally
      const fitScale = widthScale;

      // Apply scale with user zoom factor
      const finalScale = fitScale * pdfState.scale;

      // Create viewport with the calculated scale
      const viewport = page.getViewport({ scale: finalScale, rotation: pdfState.rotation });

      // Set canvas dimensions
      elements.pdfCanvasElement.height = viewport.height;
      elements.pdfCanvasElement.width = viewport.width;

      const renderContext = {
        canvasContext: pdfCanvasContext,
        viewport: viewport
      };

      const renderTask = page.render(renderContext);

      renderTask.promise.then(function () {
        pdfState.rendering = false;
        elements.pdfLoading.classList.add('hidden');

        if (pdfState.pagePending !== null) {
          renderPDFPage(pdfState.pagePending);
          pdfState.pagePending = null;
        }

        // Update page counters for both desktop and mobile
        elements.pdfCurrentPage.textContent = pageNum;
        elements.pdfCurrentPageMobile.textContent = pageNum;
      });
    }).catch(function (error) {
      console.error('Error rendering PDF page:', error);
      pdfState.rendering = false;
      elements.pdfLoading.classList.add('hidden');
    });
  }

  // Update PDF navigation controls based on current state
  function updatePDFNavigationState() {
    const isFirstPage = pdfState.pageNum <= 1;
    const isLastPage = pdfState.pageNum >= pdfState.numPages;

    // Navigation buttons to update
    const navButtons = [
      { el: elements.pdfFirstPage, disabled: isFirstPage },
      { el: elements.pdfPrevPage, disabled: isFirstPage },
      { el: elements.pdfNextPage, disabled: isLastPage },
      { el: elements.pdfLastPage, disabled: isLastPage },
      // Mobile controls
      { el: elements.pdfPrevPageMobile, disabled: isFirstPage },
      { el: elements.pdfNextPageMobile, disabled: isLastPage }
    ];

    // Apply state to all buttons
    navButtons.forEach(({ el, disabled }) => {
      if (el) {
        el.disabled = disabled;
        if (disabled) {
          el.classList.add('opacity-50', 'cursor-not-allowed');
        } else {
          el.classList.remove('opacity-50', 'cursor-not-allowed');
        }
      }
    });
  }

  // Set up event listeners for PDF controls
  function setupPDFControls() {
    // Navigation controls
    const navControls = [
      { el: elements.pdfFirstPage, action: () => { pdfState.pageNum = 1; } },
      { el: elements.pdfPrevPage, action: () => { if (pdfState.pageNum > 1) pdfState.pageNum--; } },
      { el: elements.pdfNextPage, action: () => { if (pdfState.pageNum < pdfState.numPages) pdfState.pageNum++; } },
      { el: elements.pdfLastPage, action: () => { pdfState.pageNum = pdfState.numPages; } },
      // Mobile controls
      { el: elements.pdfPrevPageMobile, action: () => { if (pdfState.pageNum > 1) pdfState.pageNum--; } },
      { el: elements.pdfNextPageMobile, action: () => { if (pdfState.pageNum < pdfState.numPages) pdfState.pageNum++; } }
    ];

    navControls.forEach(({ el, action }) => {
      if (el) {
        el.addEventListener('click', () => {
          const initialPage = pdfState.pageNum;
          action();
          if (initialPage !== pdfState.pageNum) {
            renderPDFPage(pdfState.pageNum);
            updatePDFNavigationState();
          }
        });
      }
    });

    // Zoom controls
    const zoomControls = [
      {
        el: elements.pdfZoomIn, action: () => {
          if (pdfState.scale < 3.0) {
            pdfState.scale += 0.25;
            elements.pdfZoomLevel.textContent = `${Math.round(pdfState.scale * 100)}%`;
            renderPDFPage(pdfState.pageNum);
          }
        }
      },
      {
        el: elements.pdfZoomOut, action: () => {
          if (pdfState.scale > 0.5) {
            pdfState.scale -= 0.25;
            elements.pdfZoomLevel.textContent = `${Math.round(pdfState.scale * 100)}%`;
            renderPDFPage(pdfState.pageNum);
          }
        }
      },
      // Mobile zoom
      {
        el: elements.pdfZoomOutMobile, action: () => {
          if (pdfState.scale > 0.5) {
            pdfState.scale -= 0.25;
            elements.pdfZoomLevel.textContent = `${Math.round(pdfState.scale * 100)}%`;
            renderPDFPage(pdfState.pageNum);
          }
        }
      }
    ];

    zoomControls.forEach(({ el, action }) => {
      if (el) {
        el.addEventListener('click', action);
      }
    });

    // Rotation controls
    const rotateAction = () => {
      pdfState.rotation = (pdfState.rotation + 90) % 360;
      renderPDFPage(pdfState.pageNum);
    };

    [elements.pdfRotate, elements.pdfRotateMobile].forEach(el => {
      if (el) {
        el.addEventListener('click', rotateAction);
      }
    });

    // Fullscreen toggle
    if (elements.pdfFullscreen) {
      elements.pdfFullscreen.addEventListener('click', () => {
        const viewerElement = document.getElementById('pdfViewer');
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else if (viewerElement && viewerElement.requestFullscreen) {
          viewerElement.requestFullscreen();
        }
      });
    }

    // Close button
    if (elements.closePdfModal) {
      elements.closePdfModal.addEventListener('click', () => {
        elements.pdfViewerModal.classList.add('hidden');
        pdfState.document = null;
        document.body.style.overflow = '';
      });
    }

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !elements.pdfViewerModal.classList.contains('hidden')) {
        elements.pdfViewerModal.classList.add('hidden');
        pdfState.document = null;
        document.body.style.overflow = '';
      }
    });
  }

  // Public API
  return {
    loadPDF,
    initialize: function () {
      if (elements.pdfCanvasElement && elements.pdfViewerModal) {
        setupPDFControls();
        console.log('PDF Viewer initialized');
      } else {
        console.warn('PDF Viewer elements not found in the DOM');
      }
    }
  };
}

// Create and export the PDF viewer
window.PdfViewer = initPdfViewer(); 