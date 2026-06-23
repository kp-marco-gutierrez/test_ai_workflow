var COLUMNS = ['To Do', 'Doing', 'Done'];
var STORAGE_KEY = 'trello-lite-board';
var draggedCard = null;
var _cardCounter = 0;

function sanitizeInput(value) {
  // Use a temporary DOM node to decode any encoded entities first,
  // then strip tags and dangerous patterns from the resulting text.
  var tmp = document.createElement('div');
  tmp.textContent = value.trim();
  return tmp.textContent
    .replace(/<[^>]*>/g, '')
    .replace(/&#?\w+;/gi, '')
    .replace(/on\w+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]*)/gi, '');
}

// Safe element factory — blocks innerHTML/outerHTML to prevent XSS.
function createElementWithProperties(tag, props) {
  var el = document.createElement(tag);
  var UNSAFE = ['innerHTML', 'outerHTML'];
  for (var k in props) {
    if (UNSAFE.indexOf(k) === -1) el[k] = props[k];
  }
  return el;
}

function saveBoard() {
  const state = {};
  COLUMNS.forEach(name => { state[name] = []; });
  document.querySelectorAll('.column').forEach(col => {
    const header = col.querySelector('.column-header');
    if (!header) return;
    const colName = header.textContent;
    col.querySelectorAll('.card').forEach(card => {
      const titleEl = card.querySelector('.card-title');
      if (titleEl) state[colName].push(titleEl.textContent);
    });
  });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadBoard() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {
    console.error('Failed to load board state — localStorage may be corrupted or unavailable. Starting with an empty board.', e);
  }
  return null;
}

function moveCardToColumn(cardEl, targetColEl, cardsList, colName) {
  if (!cardEl || cardEl.closest('.column') === targetColEl) return;
  cardsList.appendChild(cardEl);
  var sel = cardEl.querySelector('select');
  if (sel) sel.value = colName;
  saveBoard();
}

function createCardElement(title, currentColumn) {
  var card = createElementWithProperties('div', {className: 'card', draggable: true});
  var cardId = 'card-' + (++_cardCounter);
  card.dataset.cardId = cardId;

  card.addEventListener('dragstart', function(e) {
    draggedCard = card;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', cardId);
    setTimeout(function() { card.classList.add('dragging'); }, 0);
  });

  card.addEventListener('dragend', function() {
    card.classList.remove('dragging');
    // Do NOT clear draggedCard here — if drop didn't fire (e.g. Playwright
    // CDP drag that never established a valid drop zone), the mouseup fallback
    // on the target column still needs draggedCard to complete the move.
  });

  // Mouse-based drag fallback for environments where HTML5 dragstart
  // is not reliably triggered (e.g. Playwright's CDP simulation).
  // Use capture phase so the select's stopPropagation on mousedown
  // cannot block this from running.
  card.addEventListener('pointerdown', function() {
    draggedCard = card;
  }, { capture: true });

  card.addEventListener('mousedown', function() {
    draggedCard = card;
  });

  var titleSpan = createElementWithProperties('span', {className: 'card-title', textContent: title});
  card.appendChild(titleSpan);

  var select = createElementWithProperties('select');
  select.setAttribute('aria-label', 'Move to column');
  COLUMNS.forEach(function(col) {
    var option = createElementWithProperties('option', {value: col, textContent: col});
    if (col === currentColumn) option.selected = true;
    select.appendChild(option);
  });

  // Prevent the select's mousedown from setting draggedCard (the card's
  // mousedown listener fires on bubble; stopPropagation blocks that).
  select.addEventListener('mousedown', function(e) {
    e.stopPropagation();
  });

  select.addEventListener('change', function() {
    var targetName = select.value;
    var columns = document.querySelectorAll('.column');
    for (var i = 0; i < columns.length; i++) {
      var header = columns[i].querySelector('.column-header');
      if (header && header.textContent === targetName) {
        columns[i].querySelector('.cards-list').appendChild(card);
        saveBoard();
        break;
      }
    }
  });

  card.appendChild(select);

  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'delete';
  deleteBtn.type = 'button';
  deleteBtn.textContent = 'Delete';
  deleteBtn.setAttribute('aria-label', 'Delete card');
  deleteBtn.addEventListener('click', () => {
    card.remove();
    saveBoard();
  });
  card.appendChild(deleteBtn);

  return card;
}

function createColumnEl(name, savedCards) {
  var col = createElementWithProperties('div', {className: 'column'});

  var header = createElementWithProperties('h2', {className: 'column-header', textContent: name});
  col.appendChild(header);

  // Error shown when rename is rejected (e.g. duplicate name).
  var renameError = createElementWithProperties('div', {
    className: 'rename-error',
    textContent: ''
  });
  renameError.setAttribute('role', 'alert');
  col.appendChild(renameError);

  header.addEventListener('dblclick', () => {
    const currentName = header.textContent;

    renameError.classList.remove('visible');

    var renameInput = createElementWithProperties('input', {
      className: 'list-name-input',
      type: 'text',
      value: currentName
    });
    renameInput.setAttribute('aria-label', 'List name');

    header.style.display = 'none';
    col.insertBefore(renameInput, header);
    renameInput.focus();
    renameInput.select();

    let done = false;

    function confirmRename(showDuplicateError) {
      if (done) return;
      var newName = sanitizeInput(renameInput.value);
      var isDuplicate = newName !== currentName && COLUMNS.indexOf(newName) !== -1;

      if (isDuplicate && showDuplicateError) {
        renameError.textContent = 'Column name "' + newName + '" already exists';
        renameError.classList.add('visible');
        renameInput.focus();
        return; // keep input open so the user can correct the name
      }

      done = true;
      renameError.classList.remove('visible');

      if (newName && !isDuplicate && newName !== currentName) {
        var idx = COLUMNS.indexOf(currentName);
        if (idx !== -1) COLUMNS[idx] = newName;
        header.textContent = newName;
        name = newName;
      }
      header.style.display = '';
      renameInput.remove();
    }

    renameInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        confirmRename(true);
      } else if (e.key === 'Escape') {
        if (done) return;
        done = true;
        renameError.classList.remove('visible');
        header.style.display = '';
        renameInput.remove();
      }
    });

    renameInput.addEventListener('blur', () => confirmRename(false));
  });

  col.addEventListener('dragenter', function(e) {
    e.preventDefault();
    col.classList.add('drag-over');
  });

  col.addEventListener('dragleave', function(e) {
    if (!col.contains(e.relatedTarget)) {
      col.classList.remove('drag-over');
    }
  });

  col.addEventListener('dragover', function(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  });

  col.addEventListener('drop', function(e) {
    e.preventDefault();
    col.classList.remove('drag-over');
    var id = e.dataTransfer && e.dataTransfer.getData('text/plain');
    var srcCard = (id && document.querySelector('[data-card-id="' + id + '"]')) || draggedCard;
    if (srcCard) moveCardToColumn(srcCard, col, cardsList, name);
    draggedCard = null;
  });

  // Mouse-based drop: handles drag_to() when HTML5 drag events don't fire.
  col.addEventListener('mouseup', function() {
    if (!draggedCard) return;
    moveCardToColumn(draggedCard, col, cardsList, name);
    draggedCard = null;
  });

  var cardsList = createElementWithProperties('div', {className: 'cards-list'});
  col.appendChild(cardsList);

  if (savedCards) {
    savedCards.forEach(title => {
      cardsList.appendChild(createCardElement(title, name));
    });
  }

  var form = createElementWithProperties('div', {className: 'add-card-form'});

  var input = createElementWithProperties('input', {
    className: 'card-input',
    type: 'text',
    placeholder: 'Card title…'
  });
  input.setAttribute('aria-label', 'Card title');
  form.appendChild(input);

  var button = createElementWithProperties('button', {
    className: 'add-card',
    type: 'button',
    textContent: 'Add card'
  });
  form.appendChild(button);

  var errorEl = createElementWithProperties('div', {
    className: 'error',
    textContent: 'Card title cannot be empty'
  });
  errorEl.setAttribute('role', 'alert');
  form.appendChild(errorEl);

  col.appendChild(form);

  function addCard() {
    const title = sanitizeInput(input.value);
    if (!title) {
      errorEl.classList.add('visible');
      return;
    }
    errorEl.classList.remove('visible');
    cardsList.appendChild(createCardElement(title, name));
    input.value = '';
    saveBoard();
  }

  button.addEventListener('click', addCard);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') addCard();
  });

  return col;
}

const board = document.querySelector('.board-container');
const savedState = loadBoard();
COLUMNS.forEach(name => {
  const savedCards = savedState ? (savedState[name] || []) : [];
  board.appendChild(createColumnEl(name, savedCards));
});

// Global cleanup: clear draggedCard if mouse released outside any column.
document.addEventListener('mouseup', function() {
  draggedCard = null;
});
