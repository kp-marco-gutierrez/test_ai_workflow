(function () {
  var COLUMNS = ['To Do', 'Doing', 'Done'];
  var STORAGE_KEY = 'trello-lite-board';
  var SELECTOR_COLUMN = '.column';
  var SELECTOR_CARD = '.card';
  var SELECTOR_COLUMN_HEADER = '.column-header';
  var SELECTOR_CARDS_LIST = '.cards-list';
  var DRAG_MIME_TYPE = 'text/plain';
  var MAX_CARD_TITLE_LENGTH = 50;
  var LABEL_COLORS = ['green', 'yellow', 'orange', 'red', 'purple', 'blue'];
  var draggedCard = null;

  function sanitizeInput(value) {
    // Strip HTML/script tags as defence-in-depth. All user-supplied strings are
    // written back via textContent (never innerHTML), so entity-encoding is not
    // required and would corrupt display of characters like & or <.
    return value.replace(/<[^>]*>?/gm, '').trim();
  }

  // Utility: create an element and assign own properties in one call.
  function makeEl(tag, props) {
    var el = document.createElement(tag);
    for (var k in props) el[k] = props[k];
    return el;
  }

  // Utility: create a button that stops mousedown propagation (prevents card drag
  // from firing when interacting with card controls) and attaches a click handler.
  function makeCardBtn(className, text, ariaLabel, onClick) {
    var btn = makeEl('button', {className: className, type: 'button', textContent: text});
    if (ariaLabel) btn.setAttribute('aria-label', ariaLabel);
    btn.addEventListener('mousedown', function(e) { e.stopPropagation(); });
    if (onClick) btn.addEventListener('click', onClick);
    return btn;
  }

  // Wire keyboard and blur handlers for an inline rename <input>.
  //   onConfirm(newValue) – called on Enter; return false to abort (keep input open).
  //   onCancel()          – called on Escape or blur when blurAction is 'cancel'.
  //   blurAction          – 'confirm' | 'cancel'
  //
  // done is set to true *before* calling onConfirm so that removing the input
  // element inside onConfirm (which synchronously fires blur) does not trigger
  // a reentrant onCancel call. If onConfirm returns false the flag is reset.
  function attachRenameHandlers(input, onConfirm, onCancel, blurAction) {
    var done = false;

    function doConfirm() {
      if (done) return;
      done = true;
      var result = onConfirm(sanitizeInput(input.value));
      if (result === false) done = false; // validation failed – re-arm
    }

    function doCancel() {
      if (done) return;
      done = true;
      onCancel();
    }

    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') { e.preventDefault(); doConfirm(); }
      else if (e.key === 'Escape') { doCancel(); }
    });

    input.addEventListener('blur', blurAction === 'confirm' ? doConfirm : doCancel);
  }

  function syncColumnsFromDOM() {
    COLUMNS = [];
    document.querySelectorAll(SELECTOR_COLUMN).forEach(function(col) {
      var header = col.querySelector(SELECTOR_COLUMN_HEADER);
      if (header) COLUMNS.push(header.textContent);
    });
  }

  function saveBoard() {
    var state = {};
    COLUMNS.forEach(function(name) { state[name] = []; });
    document.querySelectorAll(SELECTOR_COLUMN).forEach(function(col) {
      var header = col.querySelector(SELECTOR_COLUMN_HEADER);
      if (!header) return;
      var colName = header.textContent;
      col.querySelectorAll(SELECTOR_CARD).forEach(function(card) {
        var titleEl = card.querySelector('.card-title');
        if (titleEl) {
          var labelEls = card.querySelectorAll('.card-labels .label[data-color]');
          var savedLabels = [];
          for (var li = 0; li < labelEls.length; li++) { savedLabels.push(labelEls[li].dataset.color); }
          state[colName].push({ title: titleEl.textContent, complete: card.classList.contains('complete'), description: card.dataset.description || '', labels: savedLabels, dueDate: card.dataset.dueDate || '' });
        }
      });
    });
    state._columns = COLUMNS.slice();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function loadBoard() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.warn('Failed to load saved board state:', e);
      return { _corrupt: true };
    }
    return null;
  }

  // Shared handler for both HTML5 drop and mouse-based drop fallback.
  function handleCardDrop(cardsList, name) {
    if (!draggedCard) return;
    cardsList.appendChild(draggedCard);
    var sel = draggedCard.querySelector('select');
    if (sel) sel.value = name;
    draggedCard = null;
    saveBoard();
  }

  function showCardModal(cardTitle, currentDescription, currentDueDate, onSave) {
    var existing = document.querySelector('.card-modal-overlay');
    if (existing) existing.remove();

    var overlay = makeEl('div', {className: 'card-modal-overlay'});
    var modal = makeEl('div', {className: 'card-modal'});
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', sanitizeInput(cardTitle));

    var titleEl = makeEl('h3', {textContent: cardTitle});
    var descLabel = makeEl('label', {textContent: 'Description'});
    var descField = makeEl('textarea', {className: 'card-description'});
    descField.value = currentDescription;

    var dueDateLabel = makeEl('label', {textContent: 'Due Date'});
    var dueDateField = makeEl('input', {className: 'due-date', type: 'date'});
    dueDateField.value = currentDueDate || '';

    var actions = makeEl('div', {className: 'modal-actions'});
    var saveBtn = makeEl('button', {className: 'save', type: 'button', textContent: 'Save'});
    var closeBtn = makeEl('button', {className: 'modal-close', type: 'button', textContent: 'Close'});

    saveBtn.addEventListener('click', function() {
      onSave(sanitizeInput(descField.value), dueDateField.value);
    });
    closeBtn.addEventListener('click', function() { overlay.remove(); });
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) overlay.remove();
    });

    actions.appendChild(saveBtn);
    actions.appendChild(closeBtn);
    modal.appendChild(titleEl);
    modal.appendChild(descLabel);
    modal.appendChild(descField);
    modal.appendChild(dueDateLabel);
    modal.appendChild(dueDateField);
    modal.appendChild(actions);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    descField.focus();
  }

  function createLabelEl(color) {
    var span = document.createElement('span');
    span.className = 'label label-' + color;
    span.dataset.color = color;
    return span;
  }

  function showLabelPicker(labelsArea, labels, anchorEl, onDone) {
    var existing = document.querySelector('.label-picker');
    if (existing) { existing.remove(); return; }

    var picker = document.createElement('div');
    picker.className = 'label-picker';
    picker.setAttribute('role', 'menu');

    LABEL_COLORS.forEach(function(color) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.dataset.color = color;
      btn.className = 'label-option label-' + color;
      btn.textContent = color.charAt(0).toUpperCase() + color.slice(1);
      if (labels.indexOf(color) !== -1) btn.classList.add('active');

      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var idx = labels.indexOf(color);
        if (idx !== -1) {
          labels.splice(idx, 1);
          var labelEl = labelsArea.querySelector('[data-color="' + color + '"]');
          if (labelEl) labelEl.remove();
        } else {
          labels.push(color);
          labelsArea.appendChild(createLabelEl(color));
        }
        closePicker();
        onDone();
      });

      picker.appendChild(btn);
    });

    var rect = anchorEl.getBoundingClientRect();
    picker.style.position = 'fixed';
    picker.style.top = rect.bottom + 'px';
    picker.style.left = rect.left + 'px';
    picker.style.zIndex = '2000';
    document.body.appendChild(picker);

    function closePicker() {
      if (picker.parentNode) picker.remove();
      document.removeEventListener('click', handleOutside, true);
    }

    function handleOutside(e) {
      if (!picker.contains(e.target) && e.target !== anchorEl) {
        closePicker();
      }
    }
    setTimeout(function() {
      document.addEventListener('click', handleOutside, true);
    }, 0);
  }

  function createCardEl(title, currentColumn, complete, cardDescription, cardLabels, cardDueDate) {
    var description = cardDescription || '';
    var labels = cardLabels ? cardLabels.slice() : [];
    var dueDate = cardDueDate || '';
    var card = makeEl('div', {className: complete ? 'card complete' : 'card'});
    card.dataset.description = description;
    card.dataset.dueDate = dueDate;

    // dragend is the safety-net for HTML5 drag that ends without a drop target.
    card.addEventListener('dragstart', function(e) {
      draggedCard = card;
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData(DRAG_MIME_TYPE, title);
    });

    card.addEventListener('dragend', function() {
      draggedCard = null;
    });

    // Mouse-based drag fallback for environments where HTML5 dragstart
    // is not reliably triggered (e.g. Playwright's CDP simulation).
    // The global mouseup listener is the safety-net for mouse drags that
    // end outside any column's mouseup handler.
    // Capture phase ensures this fires even when a child element (select,
    // delete button) calls e.stopPropagation() in the bubble phase.
    card.addEventListener('mousedown', function() {
      draggedCard = card;
    }, true);

    var checkbox = makeEl('input', {className: 'complete-toggle', type: 'checkbox'});
    checkbox.setAttribute('aria-label', 'Mark complete');
    checkbox.checked = !!complete;
    checkbox.addEventListener('mousedown', function(e) { e.stopPropagation(); });
    checkbox.addEventListener('change', function() {
      if (checkbox.checked) {
        card.classList.add('complete');
      } else {
        card.classList.remove('complete');
      }
      saveBoard();
    });

    var deleteBtn = makeCardBtn('delete', 'Delete', null, function() {
      card.remove();
      saveBoard();
    });

    var moveUpBtn = makeCardBtn('move-up', '↑', 'Move up', function() {
      var prev = card.previousElementSibling;
      if (prev) {
        card.parentNode.insertBefore(card, prev);
        saveBoard();
      }
    });

    var moveDownBtn = makeCardBtn('move-down', '↓', 'Move down', function() {
      var next = card.nextElementSibling;
      if (next) {
        card.parentNode.insertBefore(next, card);
        saveBoard();
      }
    });

    var labelsArea = makeEl('div', {className: 'card-labels'});
    labels.forEach(function(color) { labelsArea.appendChild(createLabelEl(color)); });

    var labelBtn = makeEl('button', {className: 'label-btn', type: 'button', textContent: 'Label'});
    labelBtn.addEventListener('mousedown', function(e) { e.stopPropagation(); });
    labelBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      showLabelPicker(labelsArea, labels, labelBtn, saveBoard);
    });

    var titleSpan = makeEl('span', {className: 'card-title', textContent: title});
    var dueDateSpan = makeEl('span', {className: 'card-due-date', textContent: dueDate});
    card.appendChild(checkbox);
    card.appendChild(labelsArea);
    card.appendChild(titleSpan);
    card.appendChild(dueDateSpan);

    titleSpan.addEventListener('dblclick', function() {
      var currentTitle = titleSpan.textContent;

      var editInput = makeEl('input', {
        className: 'card-edit',
        type: 'text',
        value: currentTitle
      });
      editInput.setAttribute('aria-label', 'Card title');

      titleSpan.style.display = 'none';
      card.insertBefore(editInput, titleSpan);
      editInput.focus();
      editInput.select();

      function restoreTitle() {
        titleSpan.style.display = '';
        editInput.remove();
      }

      attachRenameHandlers(
        editInput,
        function(newTitle) {
          if (newTitle) {
            titleSpan.textContent = newTitle;
            title = newTitle;
          }
          restoreTitle();
          saveBoard();
        },
        restoreTitle,
        'confirm'
      );
    });

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
      var columns = document.querySelectorAll(SELECTOR_COLUMN);
      for (var i = 0; i < columns.length; i++) {
        var header = columns[i].querySelector(SELECTOR_COLUMN_HEADER);
        if (header && header.textContent === targetName) {
          columns[i].querySelector(SELECTOR_CARDS_LIST).appendChild(card);
          saveBoard();
          break;
        }
      }
    });

    var openBtn = makeCardBtn('open-card', 'Open', 'Open card', function(e) {
      e.stopPropagation();
      showCardModal(title, description, dueDate, function(newDesc, newDueDate) {
        description = newDesc;
        card.dataset.description = newDesc;
        dueDate = newDueDate;
        card.dataset.dueDate = newDueDate;
        dueDateSpan.textContent = newDueDate;
        saveBoard();
      });
    });

    var singleClickTimer = null;
    card.addEventListener('click', function(e) {
      if (e.target.closest('button') || e.target.closest('select') || e.target.closest('input')) return;
      clearTimeout(singleClickTimer);
      if (e.detail >= 2) return; // second click of a dblclick — let the dblclick handler take over
      singleClickTimer = setTimeout(function() {
        showCardModal(title, description, dueDate, function(newDesc, newDueDate) {
          description = newDesc;
          card.dataset.description = newDesc;
          dueDate = newDueDate;
          card.dataset.dueDate = newDueDate;
          dueDateSpan.textContent = newDueDate;
          saveBoard();
        });
      }, 300);
    });

    card.appendChild(select);
    card.appendChild(openBtn);
    card.appendChild(labelBtn);
    card.appendChild(moveUpBtn);
    card.appendChild(moveDownBtn);
    card.appendChild(deleteBtn);
    return card;
  }

  function createColumnEl(name, savedCards) {
    var col = makeEl('div', {className: 'column'});

    var header = makeEl('h2', {className: 'column-header', textContent: name});
    col.appendChild(header);

    var deleteBtn = makeEl('button', {
      className: 'delete-list',
      type: 'button',
      textContent: 'Delete list'
    });
    deleteBtn.setAttribute('aria-label', 'Delete list');
    deleteBtn.addEventListener('click', function() {
      var idx = COLUMNS.indexOf(name);
      if (idx !== -1) COLUMNS.splice(idx, 1);
      col.remove();
      saveBoard();
    });
    col.appendChild(deleteBtn);

    var moveLeftBtn = makeEl('button', {
      className: 'move-left',
      type: 'button',
      textContent: '←'
    });
    moveLeftBtn.setAttribute('aria-label', 'Move list left');
    moveLeftBtn.addEventListener('click', function() {
      var prev = col.previousElementSibling;
      if (prev && prev.classList.contains('column')) {
        col.parentNode.insertBefore(col, prev);
        syncColumnsFromDOM();
        saveBoard();
      }
    });
    col.appendChild(moveLeftBtn);

    var moveRightBtn = makeEl('button', {
      className: 'move-right',
      type: 'button',
      textContent: '→'
    });
    moveRightBtn.setAttribute('aria-label', 'Move list right');
    moveRightBtn.addEventListener('click', function() {
      var next = col.nextElementSibling;
      if (next && next.classList.contains('column')) {
        col.parentNode.insertBefore(next, col);
        syncColumnsFromDOM();
        saveBoard();
      }
    });
    col.appendChild(moveRightBtn);

    header.addEventListener('dblclick', function() {
      var currentName = header.textContent;

      // CSS class list-name-input is intentional: tests locate this input by that selector.
      var renameInput = makeEl('input', {
        className: 'list-name-input',
        type: 'text',
        value: currentName
      });
      renameInput.setAttribute('aria-label', 'List name');

      var renameError = makeEl('div', {
        className: 'error',
        textContent: 'A column with that name already exists'
      });
      renameError.setAttribute('role', 'alert');

      header.style.display = 'none';
      col.insertBefore(renameInput, header);
      col.insertBefore(renameError, header);
      renameInput.focus();
      renameInput.select();

      renameInput.addEventListener('input', function() {
        renameError.classList.remove('visible');
      });

      function cleanup() {
        header.style.display = '';
        renameError.classList.remove('visible');
        renameInput.remove();
        renameError.remove();
      }

      attachRenameHandlers(
        renameInput,
        function(newName) {
          var isDuplicate = newName !== currentName && COLUMNS.indexOf(newName) !== -1;
          if (isDuplicate) {
            renameError.classList.add('visible');
            renameInput.select();
            return false;
          }
          renameError.classList.remove('visible');
          if (newName && newName !== currentName) {
            var idx = COLUMNS.indexOf(currentName);
            if (idx !== -1) COLUMNS[idx] = newName;
            header.textContent = newName;
            name = newName;
          }
          cleanup();
          saveBoard();
        },
        cleanup,
        'cancel'
      );
    });

    col.addEventListener('dragover', function(e) {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
    });

    col.addEventListener('drop', function(e) {
      e.preventDefault();
      handleCardDrop(cardsList, name);
    });

    // Mouse-based drop: handles drag_to() when HTML5 dragstart doesn't fire.
    col.addEventListener('mouseup', function() {
      if (!draggedCard) return;
      var sourceCol = draggedCard.closest(SELECTOR_COLUMN);
      if (sourceCol !== col) {
        handleCardDrop(cardsList, name);
      }
      draggedCard = null;
    });

    var cardsList = makeEl('div', {className: 'cards-list'});
    col.appendChild(cardsList);

    if (savedCards) {
      savedCards.forEach(function(item) {
        var t = typeof item === 'string' ? item : item.title;
        var c = typeof item === 'string' ? false : !!item.complete;
        var d = typeof item === 'string' ? '' : (item.description || '');
        var l = typeof item === 'string' ? [] : (item.labels || []);
        var dd = typeof item === 'string' ? '' : (item.dueDate || '');
        cardsList.appendChild(createCardEl(t, name, c, d, l, dd));
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
      errorEl.classList.remove('visible');
      var title = sanitizeInput(input.value);
      if (!title) {
        errorEl.textContent = 'Card title cannot be empty';
        errorEl.classList.add('visible');
        input.focus();
        return;
      }
      if (title.length > MAX_CARD_TITLE_LENGTH) {
        errorEl.textContent = 'Card title cannot exceed ' + MAX_CARD_TITLE_LENGTH + ' characters';
        errorEl.classList.add('visible');
        input.focus();
        return;
      }
      cardsList.appendChild(createCardEl(title, name));
      input.value = '';
      saveBoard();
    }

    button.addEventListener('click', addCard);
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') addCard();
    });
    input.addEventListener('input', function() {
      errorEl.classList.remove('visible');
    });

    return col;
  }

  var board = document.querySelector('.board-container');
  var savedState = loadBoard();
  if (savedState && savedState._corrupt) {
    var loadErrorEl = makeEl('p', {
      className: 'load-error',
      textContent: 'Your saved board could not be loaded. Starting with a fresh board.'
    });
    board.parentNode.insertBefore(loadErrorEl, board);
    savedState = null;
  }
  if (savedState && Array.isArray(savedState._columns) && savedState._columns.length) {
    COLUMNS = savedState._columns.slice();
  }
  COLUMNS.forEach(function(name) {
    var savedCards = savedState ? (savedState[name] || []) : [];
    board.appendChild(createColumnEl(name, savedCards));
  });

  // Add-list form
  var addListSection = makeEl('div', {className: 'add-list-section'});

  var addListInput = makeEl('input', {
    className: 'list-input',
    type: 'text',
    placeholder: 'New list name'
  });
  addListInput.setAttribute('aria-label', 'New list name');
  addListSection.appendChild(addListInput);

  var addListBtn = makeEl('button', {
    className: 'add-list',
    type: 'button',
    textContent: 'Add list'
  });
  addListSection.appendChild(addListBtn);

  var addListError = makeEl('div', {
    className: 'error',
    textContent: 'List name cannot be empty'
  });
  addListError.setAttribute('role', 'alert');
  addListSection.appendChild(addListError);

  board.parentNode.insertBefore(addListSection, board.nextSibling);

  function addList() {
    var listName = sanitizeInput(addListInput.value);
    if (!listName) {
      addListError.classList.add('visible');
      addListInput.focus();
      return;
    }
    addListError.classList.remove('visible');
    COLUMNS.push(listName);
    board.appendChild(createColumnEl(listName, []));
    addListInput.value = '';
    saveBoard();
  }

  addListBtn.addEventListener('click', addList);
  addListInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') addList();
  });
  addListInput.addEventListener('input', function() {
    addListError.classList.remove('visible');
  });

  // Global cleanup: clear draggedCard if mouse released outside any column.
  document.addEventListener('mouseup', function() {
    draggedCard = null;
  });

  // Clear stale drag state when the pointer leaves the browser window.
  // Without this, releasing the mouse outside the window skips the mouseup
  // event entirely, leaving draggedCard set and causing an unintended drop
  // on the next in-window interaction.
  document.addEventListener('mouseleave', function() {
    draggedCard = null;
  });

  var searchInput = document.getElementById('search');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      var term = searchInput.value.toLowerCase();
      document.querySelectorAll(SELECTOR_CARD).forEach(function(card) {
        var titleEl = card.querySelector('.card-title');
        var title = titleEl ? titleEl.textContent.toLowerCase() : '';
        card.style.display = (!term || title.indexOf(term) !== -1) ? '' : 'none';
      });
    });
  }
})();
