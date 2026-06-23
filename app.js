const COLUMNS = ['To Do', 'Doing', 'Done'];
const STORAGE_KEY = 'trello-lite-board';

function sanitizeInput(value) {
  return value
    .trim()
    .replace(/<[^>]*>/g, '')                                     // strip HTML tags
    .replace(/&#?\w+;/gi, '')                                    // strip HTML entities
    .replace(/on\w+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]*)/gi, ''); // strip event handler attrs
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

function updateColumnName(oldName, newName) {
  const idx = COLUMNS.indexOf(oldName);
  if (idx !== -1) COLUMNS[idx] = newName;
}

function createCardEl(title, currentColumn) {
  const card = document.createElement('div');
  card.className = 'card';

  const titleSpan = document.createElement('span');
  titleSpan.className = 'card-title';
  titleSpan.textContent = title;
  card.appendChild(titleSpan);

  const select = document.createElement('select');
  select.setAttribute('aria-label', 'Move to column');
  COLUMNS.forEach(col => {
    const option = document.createElement('option');
    option.value = col;
    option.textContent = col;
    if (col === currentColumn) option.selected = true;
    select.appendChild(option);
  });

  select.addEventListener('change', () => {
    const targetName = select.value;
    for (const col of document.querySelectorAll('.column')) {
      const header = col.querySelector('.column-header');
      if (header && header.textContent === targetName) {
        col.querySelector('.cards-list').appendChild(card);
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
  const col = document.createElement('div');
  col.className = 'column';

  const header = document.createElement('h2');
  header.className = 'column-header';
  header.textContent = name;
  col.appendChild(header);

  header.addEventListener('dblclick', () => {
    const currentName = header.textContent;

    const renameInput = document.createElement('input');
    renameInput.className = 'list-name-input';
    renameInput.type = 'text';
    renameInput.value = currentName;
    renameInput.setAttribute('aria-label', 'List name');

    header.style.display = 'none';
    col.insertBefore(renameInput, header);
    renameInput.focus();
    renameInput.select();

    let done = false;

    function confirmRename() {
      if (done) return;
      done = true;
      const newName = sanitizeInput(renameInput.value);
      if (newName) {
        updateColumnName(currentName, newName);
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

  const cardsList = document.createElement('div');
  cardsList.className = 'cards-list';
  col.appendChild(cardsList);

  if (savedCards) {
    savedCards.forEach(title => {
      cardsList.appendChild(createCardEl(title, name));
    });
  }

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

  function addCard() {
    const title = sanitizeInput(input.value);
    if (!title) {
      errorEl.classList.add('visible');
      return;
    }
    errorEl.classList.remove('visible');
    const card = createCardEl(title, name);
    cardsList.appendChild(card);
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
