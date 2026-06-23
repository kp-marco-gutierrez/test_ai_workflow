import requests
from bs4 import BeautifulSoup


class BoardPage:
    def __init__(self, base_url):
        self.base_url = base_url
        self._soup = None

    def open(self):
        response = requests.get(self.base_url)
        response.raise_for_status()
        self._soup = BeautifulSoup(response.text, 'html.parser')

    def wait_for_load(self):
        pass  # static page — already parsed in open()

    def get_column_names(self):
        return [el.get_text(strip=True) for el in self._soup.select('.column-header')]

    def get_card_counts(self):
        return [len(cl.select('.card')) for cl in self._soup.select('.card-list')]

    def get_heading(self):
        h1 = self._soup.find('h1')
        return h1.get_text(strip=True) if h1 else ''
