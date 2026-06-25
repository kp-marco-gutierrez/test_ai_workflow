from pytest_bdd import scenarios

# All step definitions are already provided by the global pytest-bdd registry:
#   - "the board app is open"                              → conftest.py
#   - 'a card "…" is in the "…" column'                   → conftest.py
#   - 'I move the card "…" up in the "…" column'          → test_reorder_cards_within_a_list.py
#   - "I reload the page"                                  → test_persist_the_board_across_reloads.py
#   - 'the "…" column lists "…" before "…"'               → test_reorder_cards_within_a_list.py

scenarios("../features/card-order-persists-across-a-reload.feature")
