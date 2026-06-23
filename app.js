(function () {
  'use strict';

  var COLUMNS = ['To Do', 'Doing', 'Done'];
  var STORAGE_KEY = 'trello-lite-board';
  var draggedCard = null;

  var MESSAGES = {
    cardEmpty: 'Card title cannot be empty',
    listEmpty: 'List name cannot be empty',
    listDuplicate: 'A list with that name already exists',
    saveFailed: 'Could not save board — storage unavailable (try allowing storage in your browser settings)',
    saveFailedQuota: 'Could not save board — storage full; free up browser storage to continue saving',
    loadFailed: 'Could not restore saved board — storage unavailable',
  };

  // CSS class selectors referenced in multiple places, centralised here to
  // avoid scattered magic strings and simplify future renames.
  var SEL = {
    COLUMN: '.column',
    COLUMN_HEADER: '.column-header',
    CARDS_LIST: '.cards-list',
    BOARD: '.board-container',
  };

  // Belt-and-suspenders: strip HTML-meaningful characters so stored/displayed
  // values are never interpreted as markup. All DOM insertion uses textContent
  // (never innerHTML), which already prevents XSS at the insertion point.
  // Values consisting entirely of whitespace are rejected via the empty check
  // after trimming so users receive a clear error rather than silent rejection.
  function sanitizeInput(value) {
    return value.trim().replace(/[<>&"]/g, '');
  }

  // Creates an element, sets own properties, and optionally sets HTML
  // attributes (e.g. aria-* or role) via setAttribute to avoid repetition.
  function createElement(tag, props, attrs) {
    var el = document.createElement(tag);
    for (var k in props) el[k] = props[k];
    if (attrs) {
      for (var a in attrs) el.setAttribute(a, attrs[a]);
    }
    return el;
  }

  function makeErrorEl(message) {
    return createElement('div', { className: 'error', textContent: message }, { role: 'alert' });
  }

  // Helpers to show/hide inline error elements consistently across both
  // card and list forms, avoiding duplicated classList/textContent calls.
  function showError(errorEl, msg) {
    errorEl.textContent = msg;
    errorEl.classList.add('visible');
  }

  function clearError(errorEl) {
    errorEl.classList.remove('visible');
  }

  // Returns live h2.column-header elements — used for case-insensitive
  // duplicate checks so COLUMNS and the DOM never drift apart.
  function columnHeaders() {
    return Array.from(document.querySelectorAll(SEL.COLUMN_HEADER));
  }

  var _storageNotice = null;

  function showStorageError(msg) {
    if (!_storageNotice) {
      _storageNotice = createElement('div', { className: 'storage-notice', textContent: msg }, { role: 'alert' });
      var boardContainer = document.querySelector(SEL.BOARD);
      document.body.insertBefore(_storageNotice, boardContainer);
    } else {
      _storageNotice.textContent = msg;
    }
    _storageNotice.classList.add('visible');
  }

  // Iterates the live DOM rather than COLUMNS so that dynamically added or
  // renamed columns are always captured correctly.
  function saveBoard() {
    var state = {};
    document.querySelectorAll(SEL.COLUMN).forEach(function (col) {
      var header = col.querySelector(SEL.COLUMN_HEADER);
      if (!header) return;
      var colName = header.textContent;
      state[colName] = [];
      col.querySelectorAll('.card').forEach(function (card) {
        var titleEl = card.querySelector('.card-title');
        if (titleEl) state[colName].push(titleEl.textContent);
      });
    });
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.error('Failed to save board:', e);
      // Distinguish quota exhaustion from other storage failures so the
      // message gives users a meaningful hint about the cause.
      var isQuota = e instanceof DOMException && (
        e.code === 22 ||
        e.code === 1014 ||
        e.name === 'QuotaExceededError' ||
        e.name === 'NS_ERROR_DOM_QUOTA_REACHED'
      );
      showStorageError(isQuota ? MESSAGES.saveFailedQuota : MESSAGES.saveFailed);
    }
  }

  function loadBoard() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.error('Failed to load board:', e);
      showStorageError(MESSAGES.loadFailed);
    }
    return null;
  }

  function handleCardDrop(cardsList, name) {
    if (!draggedCard) return;
    cardsList.appendChild(draggedCard);
    var sel = draggedCard.querySelector('select');
    if (sel) sel.value = name;
    draggedCard = null;
    saveBoard();
  }

  function createCardEl(title, currentColumn) {
    var card = createElement('div', { className: 'card', draggable: true });

    card.addEventListener('dragstart', function (e) {
      draggedCard = card;
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', title);
    });

    card.addEventListener('dragend', function () {
      draggedCard = null;
    });

    // Mouse-based drag fallback for environments where HTML5 dragstart
    // is not reliably triggered (e.g. Playwright's CDP simulation).
    card.addEventListener('mousedown', function () {
      draggedCard = card;
    });

    var titleSpan = createElement('span', { className: 'card-title', textContent: title });
    card.appendChild(titleSpan);

    var select = createElement('select', {}, { 'aria-label': 'Move to column' });
    COLUMNS.forEach(function (col) {
      var option = createElement('option', { value: col, textContent: col });
      if (col === currentColumn) option.selected = true;
      select.appendChild(option);
    });

    // Prevent the select's mousedown from setting draggedCard.
    select.addEventListener('mousedown', function (e) {
      e.stopPropagation();
    });

    select.addEventListener('change', function () {
      var targetName = select.value;
      document.querySelectorAll(SEL.COLUMN).forEach(function (col) {
        var header = col.querySelector(SEL.COLUMN_HEADER);
        if (header && header.textContent === targetName) {
          col.querySelector(SEL.CARDS_LIST).appendChild(card);
          saveBoard();
        }
      });
    });

    card.appendChild(select);
    return card;
  }

  function createColumnEl(name, savedCards) {
    var col = createElement('div', { className: 'column' });

    var header = createElement('h2', { className: 'column-header', textContent: name });
    col.appendChild(header);

    header.addEventListener('dblclick', function () {
      var currentName = header.textContent;

      var renameInput = createElement('input', {
        className: 'list-name-input',
        type: 'text',
        value: currentName,
      }, { 'aria-label': 'List name' });

      var renameErrorEl = makeErrorEl('');

      header.style.display = 'none';
      col.insertBefore(renameInput, header);
      col.insertBefore(renameErrorEl, header);
      renameInput.focus();
      renameInput.select();

      var renameCompleted = false;

      function closeRename() {
        if (renameCompleted) return;
        renameCompleted = true;
        header.style.display = '';
        renameInput.remove();
        renameErrorEl.remove();
      }

      function doRename() {
        var newName = sanitizeInput(renameInput.value);
        var newLower = newName.toLowerCase();
        var currentLower = currentName.toLowerCase();

        if (newLower === currentLower) {
          closeRename();
          return;
        }

        if (!newName) {
          showError(renameErrorEl, MESSAGES.listEmpty);
          return;
        }

        // Case-insensitive duplicate check against live DOM headers.
        var isDuplicate = columnHeaders().some(function (h) {
          return h.textContent.toLowerCase() === newLower;
        });
        if (isDuplicate) {
          showError(renameErrorEl, MESSAGES.listDuplicate);
          return;
        }

        var idx = COLUMNS.indexOf(currentName);
        if (idx !== -1) COLUMNS[idx] = newName;
        header.textContent = newName;
        name = newName;
        saveBoard();
        closeRename();
      }

      renameInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          doRename();
        } else if (e.key === 'Escape') {
          closeRename();
        }
      });

      renameInput.addEventListener('blur', closeRename);
    });

    col.addEventListener('dragover', function (e) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    });

    col.addEventListener('drop', function (e) {
      e.preventDefault();
      handleCardDrop(cardsList, name);
    });

    // Mouse-based drop: handles drag_to() when HTML5 dragstart doesn't fire.
    col.addEventListener('mouseup', function () {
      if (!draggedCard) return;
      var sourceCol = draggedCard.closest(SEL.COLUMN);
      if (sourceCol !== col) {
        handleCardDrop(cardsList, name);
      }
      draggedCard = null;
    });

    var cardsList = createElement('div', { className: 'cards-list' });
    col.appendChild(cardsList);

    if (savedCards) {
      savedCards.forEach(function (title) {
        cardsList.appendChild(createCardEl(title, name));
      });
    }

    var form = createElement('div', { className: 'add-card-form' });

    var input = createElement('input', {
      className: 'card-input',
      type: 'text',
      placeholder: 'Card title…',
    }, { 'aria-label': 'Card title' });
    form.appendChild(input);

    var button = createElement('button', {
      className: 'add-card',
      type: 'button',
      textContent: 'Add card',
    });
    form.appendChild(button);

    var errorEl = makeErrorEl(MESSAGES.cardEmpty);
    form.appendChild(errorEl);

    col.appendChild(form);

    function addCard() {
      var title = sanitizeInput(input.value);
      if (!title) {
        showError(errorEl, MESSAGES.cardEmpty);
        return;
      }
      clearError(errorEl);
      cardsList.appendChild(createCardEl(title, name));
      input.value = '';
      saveBoard();
    }

    button.addEventListener('click', addCard);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') addCard();
    });

    return col;
  }

  function createAddListForm() {
    var form = createElement('div', { className: 'add-list-form' });

    var input = createElement('input', {
      className: 'add-list-input',
      type: 'text',
      placeholder: 'New list name…',
    }, { 'aria-label': 'New list name' });
    form.appendChild(input);

    var button = createElement('button', {
      className: 'add-list-btn',
      type: 'button',
      textContent: 'Add list',
    });
    form.appendChild(button);

    var errorEl = makeErrorEl(MESSAGES.listEmpty);
    form.appendChild(errorEl);

    function addList() {
      var name = sanitizeInput(input.value);
      if (!name) {
        showError(errorEl, MESSAGES.listEmpty);
        return;
      }
      // Case-insensitive duplicate check against live DOM headers.
      var duplicate = columnHeaders().some(function (h) {
        return h.textContent.toLowerCase() === name.toLowerCase();
      });
      if (duplicate) {
        showError(errorEl, MESSAGES.listDuplicate);
        return;
      }
      clearError(errorEl);
      COLUMNS.push(name);
      board.insertBefore(createColumnEl(name, []), form);
      input.value = '';
      saveBoard();
    }

    button.addEventListener('click', addList);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') addList();
    });

    return form;
  }

  // Columns are appended by iterating COLUMNS in order, which enforces the
  // "To Do", "Doing", "Done" display order required by the board layout spec.
  var board = document.querySelector(SEL.BOARD);
  var savedState = loadBoard();
  COLUMNS.forEach(function (name) {
    var savedCards = savedState ? (savedState[name] || []) : [];
    board.appendChild(createColumnEl(name, savedCards));
  });
  board.appendChild(createAddListForm());

  // Global cleanup: clear draggedCard if mouse released outside any column.
  document.addEventListener('mouseup', function () {
    draggedCard = null;
  });

}());
