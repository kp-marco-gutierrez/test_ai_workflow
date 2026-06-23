(function () {
  var STORAGE_KEY = 'trello-lite-board';
  var draggedCard = null;

  function makeEl(tag, props) {
    var el = document.createElement(tag);
    if (props) for (var k in props) el[k] = props[k];
    return el;
  }

  function saveBoard() {
    var state = [];
    document.querySelectorAll('.column').forEach(function (col) {
      var hdr = col.querySelector('.column-header');
      if (!hdr) return;
      var cards = [];
      col.querySelectorAll('.card-title').forEach(function (t) {
        cards.push(t.textContent);
      });
      state.push({ name: hdr.textContent, cards: cards });
    });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function loadBoard() {
    try {
      var s = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
      if (Array.isArray(s)) return s;
    } catch (e) {}
    return null;
  }

  function findColumnEl(name) {
    var found = null;
    document.querySelectorAll('.column').forEach(function (col) {
      var h = col.querySelector('.column-header');
      if (h && h.textContent === name) found = col;
    });
    return found;
  }

  function buildSelectOptions(sel, currentColName) {
    sel.innerHTML = '';
    document.querySelectorAll('.column .column-header').forEach(function (h) {
      var opt = makeEl('option', { value: h.textContent, textContent: h.textContent });
      if (h.textContent === currentColName) opt.selected = true;
      sel.appendChild(opt);
    });
  }

  function createCardEl(title, colName) {
    var card = makeEl('div', { className: 'card', draggable: true });

    card.addEventListener('dragstart', function (e) {
      draggedCard = card;
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', title);
    });
    card.addEventListener('dragend', function () { draggedCard = null; });
    card.addEventListener('mousedown', function () { draggedCard = card; });

    card.appendChild(makeEl('span', { className: 'card-title', textContent: title }));

    var sel = makeEl('select');
    sel.setAttribute('aria-label', 'Move to column');
    sel.addEventListener('mousedown', function (e) { e.stopPropagation(); });
    sel.addEventListener('change', function () {
      var target = findColumnEl(sel.value);
      if (target) {
        target.querySelector('.cards-list').appendChild(card);
        saveBoard();
      }
    });
    card.appendChild(sel);

    // Populate options once card is in the DOM (deferred to next tick so all
    // columns exist when loading saved state).
    setTimeout(function () { buildSelectOptions(sel, colName); }, 0);

    return card;
  }

  function startRename(col, header) {
    var oldName = header.textContent;
    var input = makeEl('input', { className: 'list-name-input', type: 'text', value: oldName });
    input.setAttribute('aria-label', 'List name');

    header.style.display = 'none';
    header.parentNode.insertBefore(input, header);
    input.focus();
    input.select();

    var done = false;

    function commit() {
      if (done) return;
      done = true;
      input.remove();
      header.style.display = '';
      var newName = input.value.trim();
      if (!newName) return;
      header.textContent = newName;
      saveBoard();
    }

    function cancel() {
      if (done) return;
      done = true;
      input.remove();
      header.style.display = '';
    }

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') commit();
      else if (e.key === 'Escape') cancel();
    });
    input.addEventListener('blur', commit);
  }

  function createColumnEl(name, savedCards) {
    var col = makeEl('div', { className: 'column' });

    var headerRow = makeEl('div', { className: 'column-header-row' });
    var header = makeEl('h2', { className: 'column-header', textContent: name });

    var renameBtn = makeEl('button', { className: 'rename-list', type: 'button', textContent: '✎' });
    renameBtn.setAttribute('aria-label', 'Rename list');

    var deleteBtn = makeEl('button', { className: 'delete-list', type: 'button', textContent: '✕' });
    deleteBtn.setAttribute('aria-label', 'Delete list');

    headerRow.appendChild(header);
    headerRow.appendChild(renameBtn);
    headerRow.appendChild(deleteBtn);
    col.appendChild(headerRow);

    header.addEventListener('dblclick', function () { startRename(col, header); });
    renameBtn.addEventListener('click', function () { startRename(col, header); });
    deleteBtn.addEventListener('click', function () {
      col.remove();
      saveBoard();
    });

    var cardsList = makeEl('div', { className: 'cards-list' });

    col.addEventListener('dragover', function (e) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    });

    col.addEventListener('drop', function (e) {
      e.preventDefault();
      if (draggedCard) {
        cardsList.appendChild(draggedCard);
        var s = draggedCard.querySelector('select');
        if (s) s.value = name;
        draggedCard = null;
        saveBoard();
      }
    });

    col.addEventListener('mouseup', function () {
      if (draggedCard && draggedCard.closest('.column') !== col) {
        cardsList.appendChild(draggedCard);
        var s = draggedCard.querySelector('select');
        if (s) s.value = name;
        draggedCard = null;
        saveBoard();
      }
    });

    col.appendChild(cardsList);

    (savedCards || []).forEach(function (t) {
      cardsList.appendChild(createCardEl(t, name));
    });

    var form = makeEl('div', { className: 'add-card-form' });
    var cardInput = makeEl('input', { className: 'card-input', type: 'text', placeholder: 'Card title…' });
    cardInput.setAttribute('aria-label', 'Card title');
    var addBtn = makeEl('button', { className: 'add-card', type: 'button', textContent: 'Add card' });
    var errEl = makeEl('div', { className: 'error', textContent: 'Card title cannot be empty' });
    errEl.setAttribute('role', 'alert');

    form.appendChild(cardInput);
    form.appendChild(addBtn);
    form.appendChild(errEl);
    col.appendChild(form);

    function addCard() {
      var t = cardInput.value.trim();
      if (!t) { errEl.classList.add('visible'); return; }
      errEl.classList.remove('visible');
      cardsList.appendChild(createCardEl(t, name));
      cardInput.value = '';
      saveBoard();
    }

    addBtn.addEventListener('click', addCard);
    cardInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') addCard(); });

    return col;
  }

  function init() {
    var board = document.querySelector('.board-container');
    var saved = loadBoard();
    var initial = saved || [
      { name: 'To Do', cards: [] },
      { name: 'Doing', cards: [] },
      { name: 'Done', cards: [] }
    ];
    initial.forEach(function (colData) {
      board.appendChild(createColumnEl(colData.name, colData.cards));
    });
  }

  document.addEventListener('mouseup', function () { draggedCard = null; });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
