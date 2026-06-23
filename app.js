var COLUMNS = ['To Do', 'Doing', 'Done'];
var STORAGE_KEY = 'trello-lite-board';
var draggedCard = null;
var _cardCounter = 0;

function sanitizeInput(value) {
  return value
    .trim()
    .replace(/<[^>]*>/g, '')                                     // strip HTML tags
    .replace(/&#?\w+;/gi, '')                                    // strip HTML entities
    .replace(/on\w+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]*)/gi, ''); // strip event handler attrs
}

// Utility: create an element and assign own properties in one call.
function makeEl(tag, props) {
  var el = document.createElement(tag);
  for (var k in props) el[k] = props[k];
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
    console.error('Failed to load board state:', e);
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

function createCardEl(title, currentColumn) {
  var card = makeEl('div', {className: 'card', draggable: true});
  var cardId = 'card-' + (++_cardCounter);
  card.dataset.cardId = cardId;

  card.addEventListener('dragstart', function(e) {
    draggedCard = card;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', cardId);
  });

  card.addEventListener('dragend', function() {
    draggedCard = null;
  });

  // Mouse-based drag fallback for environments where HTML5 dragstart
  // is not reliably triggered (e.g. Playwright's CDP simulation).
  card.addEventListener('mousedown', function() {
    draggedCard = card;
  });

  var titleSpan = makeEl('span', {className: 'card-title', textContent: title});
  card.appendChild(titleSpan);

  var select = makeEl('select');
  select.setAttribute('aria-label', 'Move to column');
  COLUMNS.forEach(function(col) {
    var option = makeEl('option', {value: col, textContent: col});
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
  var col = makeEl('div', {className: 'column'});

  var header = makeEl('h2', {className: 'column-header', textContent: name});
  col.appendChild(header);

  header.addEventListener('dblclick', () => {
    const currentName = header.textContent;

    var renameInput = makeEl('input', {
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

    function confirmRename() {
      if (done) return;
      done = true;
      var newName = sanitizeInput(renameInput.value);
      // Only rename if non-empty, changed, and not a duplicate column name.
      var isDuplicate = newName !== currentName && COLUMNS.indexOf(newName) !== -1;
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
        confirmRename();
      } else if (e.key === 'Escape') {
        if (done) return;
        done = true;
        header.style.display = '';
        renameInput.remove();
      }
    });

    renameInput.addEventListener('blur', confirmRename);
  });

  col.addEventListener('dragover', function(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  });

  col.addEventListener('drop', function(e) {
    e.preventDefault();
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

  var cardsList = makeEl('div', {className: 'cards-list'});
  col.appendChild(cardsList);

  if (savedCards) {
    savedCards.forEach(title => {
      cardsList.appendChild(createCardEl(title, name));
    });
  }

  var form = makeEl('div', {className: 'add-card-form'});

  var input = makeEl('input', {
    className: 'card-input',
    type: 'text',
    placeholder: 'Card title…'
  });
  input.setAttribute('aria-label', 'Card title');
  form.appendChild(input);

  var button = makeEl('button', {
    className: 'add-card',
    type: 'button',
    textContent: 'Add card'
  });
  form.appendChild(button);

  var errorEl = makeEl('div', {
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
    cardsList.appendChild(createCardEl(title, name));
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
