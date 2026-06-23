import os
import threading
import http.server


class StaticServer:
    def __init__(self, root='.'):
        self.root = os.path.abspath(root)
        self.port = None
        self._server = None
        self._thread = None

    def start(self):
        handler = self._make_handler()
        self._server = http.server.HTTPServer(('127.0.0.1', 0), handler)
        self.port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server = None

    @property
    def url(self):
        return f'http://127.0.0.1:{self.port}'

    def _make_handler(self):
        root = self.root

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=root, **kwargs)

            def log_message(self, format, *args):
                pass

        return Handler
