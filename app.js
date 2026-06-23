var COLUMNS = ['To Do', 'Doing', 'Done'];

function sanitizeInput(value) {
  // Strip leading/trailing whitespace; textContent assignment below prevents XSS
  return value.trim();
}

function createCardEl(title, currentColumn) {
  var card = document.createElement('div');
  card.className = 'card';

  var titleSpan = document.createElement('span');
  titleSpan.className = 'card-title';
  titleSpan.textContent = title;
  card.appendChild(titleSpan);

  var select = document.createElement('select');
  select.setAttribute('aria-label', 'Move to column');
  COLUMNS.forEach(function(col) {
    var option = document.createElement('option');
    option.value = col;
    option.textContent = col;
    if (col === currentColumn) option.selected = true;
    select.appendChild(option);
  });

  select.addEventListener('change', function() {
    var targetName = select.value;
    var columns = document.querySelectorAll('.column');
    for (var i = 0; i < columns.length; i++) {
      var header = columns[i].querySelector('.column-header');
      if (header && header.textContent === targetName) {
        columns[i].querySelector('.cards-list').appendChild(card);
        break;
      }
    }
  });

  card.appendChild(select);
  return card;
}

function createColumnEl(name) {
  var col = document.createElement('div');
  col.className = 'column';

  var header = document.createElement('h2');
  header.className = 'column-header';
  header.textContent = name;
  col.appendChild(header);

  var cardsList = document.createElement('div');
  cardsList.className = 'cards-list';
  col.appendChild(cardsList);

  var form = document.createElement('div');
  form.className = 'add-card-form';

  var input = document.createElement('input');
  input.className = 'card-input';
  input.type = 'text';
  input.placeholder = 'Card title…';
  input.setAttribute('aria-label', 'Card title');
  form.appendChild(input);

  var button = document.createElement('button');
  button.className = 'add-card';
  button.type = 'button';
  button.textContent = 'Add card';
  form.appendChild(button);

  var errorEl = document.createElement('div');
  errorEl.className = 'error';
  errorEl.setAttribute('role', 'alert');
  errorEl.textContent = 'Card title cannot be empty';
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
  }

  button.addEventListener('click', addCard);
  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') addCard();
  });

  return col;
}

var board = document.querySelector('.board-container');
COLUMNS.forEach(function(name) {
  board.appendChild(createColumnEl(name));
});
