const COLUMNS = ['To Do', 'Doing', 'Done'];

// Encapsulate drag state for both HTML5 drag API and mouse-based drag (Playwright)
const dragState = {
  html5Card: null,
  mouseCard: null,
};

// Shared helper used by all drag paths to move a card into a column
function moveCardToColumn(card, columnEl) {
  columnEl.querySelector('.cards-list').appendChild(card);
}

// Release mouse-based drag on any mouseup that bubbles to document
document.addEventListener('mouseup', function(e) {
  if (dragState.mouseCard) {
    const targetColumn = e.target.closest('.column');
    if (targetColumn && !targetColumn.contains(dragState.mouseCard)) {
      moveCardToColumn(dragState.mouseCard, targetColumn);
    }
    dragState.mouseCard = null;
  }
});

// textContent is used throughout to render user values, preventing XSS
function sanitizeInput(value) {
  return value.trim();
}

function createCardElement(title, currentColumn) {
  const card = document.createElement('div');
  card.className = 'card';
  card.draggable = true;

  // HTML5 drag API: standard pointer/keyboard drag
  card.addEventListener('dragstart', function(e) {
    dragState.html5Card = card;
    e.dataTransfer.effectAllowed = 'move';
  });

  card.addEventListener('dragend', function() {
    dragState.html5Card = null;
  });

  // Mouse-event fallback required for programmatic drag tools (e.g. Playwright drag_to)
  card.addEventListener('mousedown', function() {
    dragState.mouseCard = card;
  });

  const titleSpan = document.createElement('span');
  titleSpan.className = 'card-title';
  titleSpan.textContent = title;
  card.appendChild(titleSpan);

  const select = document.createElement('select');
  select.setAttribute('aria-label', 'Move to column');
  COLUMNS.forEach(function(col) {
    const option = document.createElement('option');
    option.value = col;
    option.textContent = col;
    if (col === currentColumn) option.selected = true;
    select.appendChild(option);
  });

  select.addEventListener('change', function() {
    const targetName = select.value;
    const columns = document.querySelectorAll('.column');
    for (let i = 0; i < columns.length; i++) {
      const header = columns[i].querySelector('.column-header');
      if (header && header.textContent === targetName) {
        moveCardToColumn(card, columns[i]);
        break;
      }
    }
  });

  card.appendChild(select);
  return card;
}

function createColumnEl(name) {
  const col = document.createElement('div');
  col.className = 'column';

  const header = document.createElement('h2');
  header.className = 'column-header';
  header.textContent = name;
  col.appendChild(header);

  const cardsList = document.createElement('div');
  cardsList.className = 'cards-list';
  col.appendChild(cardsList);

  const form = document.createElement('div');
  form.className = 'add-card-form';

  const input = document.createElement('input');
  input.className = 'card-input';
  input.type = 'text';
  input.placeholder = 'Card title…';
  input.setAttribute('aria-label', 'Card title');
  form.appendChild(input);

  const button = document.createElement('button');
  button.className = 'add-card';
  button.type = 'button';
  button.textContent = 'Add card';
  form.appendChild(button);

  const errorEl = document.createElement('div');
  errorEl.className = 'error';
  errorEl.setAttribute('role', 'alert');
  errorEl.textContent = 'Card title cannot be empty';
  form.appendChild(errorEl);

  col.appendChild(form);

  col.addEventListener('dragover', function(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  });

  col.addEventListener('drop', function(e) {
    e.preventDefault();
    if (dragState.html5Card) {
      moveCardToColumn(dragState.html5Card, col);
    }
  });

  function handleAddCard() {
    const title = sanitizeInput(input.value);
    if (!title) {
      errorEl.classList.add('visible');
      return;
    }
    errorEl.classList.remove('visible');
    cardsList.appendChild(createCardElement(title, name));
    input.value = '';
  }

  button.addEventListener('click', handleAddCard);
  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') handleAddCard();
  });

  return col;
}

const board = document.querySelector('.board-container');
COLUMNS.forEach(function(name) {
  board.appendChild(createColumnEl(name));
});
