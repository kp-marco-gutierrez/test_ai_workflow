var STORAGE_KEY = 'trello-lite-board';

var ARIA_MOVE_TO_COLUMN = 'Move to column';
var ARIA_DELETE_LIST    = 'Delete list';
var ARIA_LIST_NAME      = 'List name';
var ARIA_CARD_TITLE     = 'Card title';
var MSG_EMPTY_CARD      = 'Card title cannot be empty';

// Centralised mutable list of column names (order determines render order).
var COLUMNS = ['To Do', 'Doing', 'Done'];

// Returns trimmed input. XSS safety is enforced at the DOM layer by always
// assigning user content via textContent, never innerHTML.
function sanitizeInput(value) {
  return value.trim();
}

// Returns the first .column element whose header matches name, or null.
function findColumnEl(name) {
  var cols = document.querySelectorAll('.column');
  for (var i = 0; i < cols.length; i++) {
    var h = cols[i].querySelector('.column-header');
    if (h && h.textContent === name) return cols[i];
  }
  return null;
}

function saveBoard() {
  var state = {};
  COLUMNS.forEach(function(name) { state[name] = []; });
  document.querySelectorAll('.column').forEach(function(col) {
    var header = col.querySelector('.column-header');
    if (!header) return;
    var colName = header.textContent;
    col.querySelectorAll('.card').forEach(function(card) {
      var titleEl = card.querySelector('.card-title');
      if (titleEl) state[colName].push(titleEl.textContent);
    });
  });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadBoard() {
  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {}
  return null;
}

// Builds a card element with a title label and a column-select control for moving.
function createCardEl(title, currentColumn) {
  var card = document.createElement('div');
  card.className = 'card';

  var titleSpan = document.createElement('span');
  titleSpan.className = 'card-title';
  titleSpan.textContent = title;
  card.appendChild(titleSpan);

  var select = document.createElement('select');
  select.setAttribute('aria-label', ARIA_MOVE_TO_COLUMN);
  COLUMNS.forEach(function(col) {
    var option = document.createElement('option');
    option.value = col;
    option.textContent = col;
    if (col === currentColumn) option.selected = true;
    select.appendChild(option);
  });

  select.addEventListener('change', function() {
    var targetCol = findColumnEl(select.value);
    if (targetCol) {
      targetCol.querySelector('.cards-list').appendChild(card);
      saveBoard();
    }
  });

  card.appendChild(select);
  return card;
}

// Builds a column element with a header, delete button, rename-on-dblclick,
// a cards list (optionally pre-populated from savedCards), and an add-card form.
// Deleting the column calls col.remove(), which removes all child card elements.
function createColumnEl(name, savedCards) {
  var col = document.createElement('div');
  col.className = 'column';

  var header = document.createElement('h2');
  header.className = 'column-header';
  header.textContent = name;
  col.appendChild(header);

  var deleteBtn = document.createElement('button');
  deleteBtn.className = 'delete-list';
  deleteBtn.setAttribute('aria-label', ARIA_DELETE_LIST);
  deleteBtn.textContent = '×';
  deleteBtn.addEventListener('click', function() {
    var idx = COLUMNS.indexOf(name);
    if (idx !== -1) COLUMNS.splice(idx, 1);
    col.remove();
    saveBoard();
  });
  col.appendChild(deleteBtn);

  header.addEventListener('dblclick', function() {
    var currentName = header.textContent;

    var renameInput = document.createElement('input');
    renameInput.className = 'list-name-input';
    renameInput.type = 'text';
    renameInput.value = currentName;
    renameInput.setAttribute('aria-label', ARIA_LIST_NAME);

    header.style.display = 'none';
    col.insertBefore(renameInput, header);
    renameInput.focus();
    renameInput.select();

    var done = false;

    function confirmRename() {
      if (done) return;
      done = true;
      var newName = sanitizeInput(renameInput.value);
      if (newName) {
        var idx = COLUMNS.indexOf(currentName);
        if (idx !== -1) COLUMNS[idx] = newName;
        header.textContent = newName;
        name = newName;
      }
      header.style.display = '';
      renameInput.remove();
    }

    renameInput.addEventListener('keydown', function(e) {
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

  var cardsList = document.createElement('div');
  cardsList.className = 'cards-list';
  col.appendChild(cardsList);

  if (savedCards) {
    savedCards.forEach(function(title) {
      cardsList.appendChild(createCardEl(title, name));
    });
  }

  var form = document.createElement('div');
  form.className = 'add-card-form';

  var input = document.createElement('input');
  input.className = 'card-input';
  input.type = 'text';
  input.placeholder = 'Card title…';
  input.setAttribute('aria-label', ARIA_CARD_TITLE);
  form.appendChild(input);

  var button = document.createElement('button');
  button.className = 'add-card';
  button.type = 'button';
  button.textContent = 'Add card';
  form.appendChild(button);

  var errorEl = document.createElement('div');
  errorEl.className = 'error';
  errorEl.setAttribute('role', 'alert');
  errorEl.textContent = MSG_EMPTY_CARD;
  form.appendChild(errorEl);

  col.appendChild(form);

  function addCard() {
    var title = sanitizeInput(input.value);
    if (!title) {
      errorEl.classList.add('visible');
      return;
    }
    errorEl.classList.remove('visible');
    var card = createCardEl(title, name);
    cardsList.appendChild(card);
    input.value = '';
    saveBoard();
  }

  button.addEventListener('click', addCard);
  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') addCard();
  });

  return col;
}

var board = document.querySelector('.board-container');
var savedState = loadBoard();
COLUMNS.forEach(function(name) {
  var savedCards = savedState ? (savedState[name] || []) : [];
  board.appendChild(createColumnEl(name, savedCards));
});
