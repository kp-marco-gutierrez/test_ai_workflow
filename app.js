var STORAGE_KEY = 'trello-lite-board';

var ARIA_MOVE_TO_COLUMN = 'Move to column';
var ARIA_DELETE_LIST    = 'Delete list';
var ARIA_LIST_NAME      = 'List name';
var ARIA_CARD_TITLE     = 'Card title';
var MSG_EMPTY_CARD      = 'Card title cannot be empty';
var MSG_EMPTY_LIST_NAME = 'List name cannot be empty';

// Centralised mutable list of column names (order determines render order).
var COLUMNS = ['To Do', 'Doing', 'Done'];

// Returns trimmed input. XSS safety is enforced at the DOM layer by always
// assigning user content via textContent, never innerHTML.
function sanitizeInput(value) {
  return value.trim();
}

// Creates a DOM element and sets common properties from props in one call.
function makeEl(tag, props) {
  var el = document.createElement(tag);
  if (!props) return el;
  if (props.className)       el.className = props.className;
  if (props.textContent)     el.textContent = props.textContent;
  if (props.type)            el.type = props.type;
  if (props.placeholder)     el.placeholder = props.placeholder;
  if (props.value !== undefined) el.value = props.value;
  if (props.role)            el.setAttribute('role', props.role);
  if (props.ariaLabel)       el.setAttribute('aria-label', props.ariaLabel);
  return el;
}

// Wires Enter → onConfirm and (if provided) Escape → onCancel on an input.
function bindConfirmKeys(input, onConfirm, onCancel) {
  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter')  { e.preventDefault(); onConfirm(); }
    else if (onCancel && e.key === 'Escape') { e.preventDefault(); onCancel(); }
  });
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
  var card = makeEl('div', { className: 'card' });
  card.appendChild(makeEl('span', { className: 'card-title', textContent: title }));

  var select = makeEl('select', { ariaLabel: ARIA_MOVE_TO_COLUMN });
  COLUMNS.forEach(function(col) {
    var option = makeEl('option', { value: col, textContent: col });
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

// Attaches rename-on-dblclick behaviour to header within col.
// getColName/setColName let the handler read and update the column name closure.
function attachRenameHandler(header, col, getColName, setColName) {
  header.addEventListener('dblclick', function() {
    var prevError = col.querySelector('.rename-error');
    if (prevError) prevError.remove();

    var currentName = getColName();
    var renameInput = makeEl('input', {
      className: 'list-name-input',
      type: 'text',
      value: currentName,
      ariaLabel: ARIA_LIST_NAME,
    });

    header.style.display = 'none';
    col.insertBefore(renameInput, header);
    renameInput.focus();
    renameInput.select();

    var done = false;

    function confirmRename() {
      if (done) return;
      done = true;
      var newName = sanitizeInput(renameInput.value);
      header.style.display = '';
      renameInput.remove();
      if (!newName) {
        var errEl = makeEl('div', { className: 'rename-error', textContent: MSG_EMPTY_LIST_NAME });
        col.insertBefore(errEl, header.nextSibling);
        return;
      }
      var idx = COLUMNS.indexOf(currentName);
      if (idx !== -1) COLUMNS[idx] = newName;
      header.textContent = newName;
      setColName(newName);
    }

    function cancelRename() {
      if (done) return;
      done = true;
      header.style.display = '';
      renameInput.remove();
    }

    bindConfirmKeys(renameInput, confirmRename, cancelRename);
    renameInput.addEventListener('blur', confirmRename);
  });
}

// Builds the add-card form. getColName supplies the current column name at
// card-creation time (the column may have been renamed since the form was built).
function createAddCardForm(getColName, cardsList) {
  var form    = makeEl('div',    { className: 'add-card-form' });
  var input   = makeEl('input',  { className: 'card-input', type: 'text',
                                   placeholder: 'Card title…', ariaLabel: ARIA_CARD_TITLE });
  var button  = makeEl('button', { className: 'add-card', type: 'button',
                                   textContent: 'Add card' });
  var errorEl = makeEl('div',    { className: 'error', role: 'alert' });

  form.appendChild(input);
  form.appendChild(button);
  form.appendChild(errorEl);

  function addCard() {
    var title = sanitizeInput(input.value);
    if (!title) {
      errorEl.textContent = MSG_EMPTY_CARD;
      errorEl.classList.add('visible');
      return;
    }
    errorEl.textContent = '';
    errorEl.classList.remove('visible');
    cardsList.appendChild(createCardEl(title, getColName()));
    input.value = '';
    saveBoard();
  }

  button.addEventListener('click', addCard);
  bindConfirmKeys(input, addCard);

  return form;
}

// Builds a column element with a header, delete button, rename-on-dblclick,
// a cards list (optionally pre-populated from savedCards), and an add-card form.
// Deleting the column calls col.remove(), which removes all child card elements.
function createColumnEl(name, savedCards) {
  var col = makeEl('div', { className: 'column' });

  var header = makeEl('h2', { className: 'column-header', textContent: name });
  col.appendChild(header);

  var deleteBtn = makeEl('button', { className: 'delete-list',
                                     ariaLabel: ARIA_DELETE_LIST, textContent: '×' });
  deleteBtn.addEventListener('click', function() {
    var idx = COLUMNS.indexOf(name);
    if (idx !== -1) COLUMNS.splice(idx, 1);
    col.remove();
    saveBoard();
  });
  col.appendChild(deleteBtn);

  attachRenameHandler(header, col,
    function()        { return name; },
    function(newName) { name = newName; }
  );

  var cardsList = makeEl('div', { className: 'cards-list' });
  col.appendChild(cardsList);

  if (savedCards) {
    savedCards.forEach(function(title) {
      cardsList.appendChild(createCardEl(title, name));
    });
  }

  col.appendChild(createAddCardForm(function() { return name; }, cardsList));

  return col;
}

var board = document.querySelector('.board-container');
var savedState = loadBoard();
COLUMNS.forEach(function(name) {
  var savedCards = savedState ? (savedState[name] || []) : [];
  board.appendChild(createColumnEl(name, savedCards));
});
