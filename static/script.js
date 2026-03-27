const modal = document.getElementById('itemModal');
const modalTitle = document.getElementById('modalTitle');
const modalDescription = document.getElementById('modalDescription');
const modalPrice = document.getElementById('modalPrice');
const modalImage = document.getElementById('modalImage');
const modalNoImage = document.getElementById('modalNoImage');
const modalOptions = document.getElementById('modalOptions');

function openModalFromCard(card) {
  if (!modal || !modalTitle || !modalDescription || !modalPrice || !modalImage || !modalNoImage) {
    return;
  }

  const { name, description, price, image, options } = card.dataset;

  modalTitle.textContent = name || 'Item';
  modalDescription.textContent = description || 'Sem descricao.';
  modalPrice.textContent = `R$ ${price || '0.00'}`;

  if (modalOptions) {
    modalOptions.innerHTML = '';
    if (options) {
      try {
        const parsed = JSON.parse(options);
        if (Array.isArray(parsed) && parsed.length > 0) {
          parsed.forEach((option) => {
            const row = document.createElement('p');
            const optionName = option?.name || 'Opcao';
            const optionPrice = Number(option?.price || 0).toFixed(2);
            row.className = 'modal__option-row';
            row.textContent = `${optionName}: R$ ${optionPrice}`;
            modalOptions.appendChild(row);
          });
        }
      } catch (_err) {
        // Ignora JSON invalido para nao quebrar o modal.
      }
    }
  }

  if (image) {
    modalImage.src = `${window.menuMediaBase}${image}`;
    modalImage.hidden = false;
    modalNoImage.hidden = true;
  } else {
    modalImage.hidden = true;
    modalNoImage.hidden = false;
  }

  modal.classList.add('is-open');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  if (!modal) {
    return;
  }

  modal.classList.remove('is-open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

document.querySelectorAll('.menu-card').forEach((card) => {
  card.addEventListener('click', () => openModalFromCard(card));
  card.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      openModalFromCard(card);
    }
  });
});

document.querySelectorAll('[data-close-modal="true"]').forEach((closeElement) => {
  closeElement.addEventListener('click', closeModal);
});

document.addEventListener('keydown', (event) => {
  if (modal && event.key === 'Escape' && modal.classList.contains('is-open')) {
    closeModal();
  }
});

function buildOptionRow(name = '', price = '') {
  const row = document.createElement('div');
  row.className = 'option-row';
  row.innerHTML = `
    <input type="text" name="option_name" placeholder="Nome da opcao" value="${name}">
    <input type="text" name="option_price" placeholder="Preco" value="${price}">
    <button type="button" data-remove-option>Remover</button>
  `;
  return row;
}

document.querySelectorAll('[data-options-wrapper]').forEach((wrapper) => {
  const rows = wrapper.querySelector('[data-option-rows]');
  const addButton = wrapper.querySelector('[data-add-option]');

  if (!rows || !addButton) {
    return;
  }

  addButton.addEventListener('click', () => {
    rows.appendChild(buildOptionRow());
  });

  wrapper.addEventListener('click', (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    if (target.matches('[data-remove-option]')) {
      const row = target.closest('.option-row');
      if (row) {
        row.remove();
      }
    }
  });
});

// Smooth scroll suavizado para navegação de categorias
document.querySelectorAll('.smooth-scroll').forEach((link) => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const targetId = link.getAttribute('href');
    const targetElement = document.querySelector(targetId);
    
    if (targetElement) {
      const targetPosition = targetElement.offsetTop - 60;
      const startPosition = window.pageYOffset;
      const distance = targetPosition - startPosition;
      const duration = 1200; // 1.2 segundos para scroll suave
      let start = null;

      function easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      }

      function animateScroll(currentTime) {
        if (start === null) start = currentTime;
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        const ease = easeInOutCubic(progress);
        
        window.scrollTo(0, startPosition + distance * ease);
        
        if (progress < 1) {
          requestAnimationFrame(animateScroll);
        }
      }

      requestAnimationFrame(animateScroll);
    }
  });
});
