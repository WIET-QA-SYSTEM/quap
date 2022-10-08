import requests
from tika import language


class TikaClient:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

    @property
    def url(self):
        return f'http://{self._host}:{self._port}'

    def _url_join(self, *args):
        return '/'.join([self.url] + list(map(str, args)))

    def _tika(self, binary: bytes) -> str:
        response = requests.put(self._url_join('tika'), headers={
            'Content-Type': 'application/pdf',
            'Accept': 'text/plain'
        }, data=binary)
        return response.content.decode('utf-8')

    def extract(self, pdf: bytes) -> str:
        return self._tika(pdf)

    def _language(self, text: str) -> str:
        response = requests.put(self._url_join('language', 'string'), headers={
            'Content-Type': 'text/plain',
            'Accept': 'text/plain'
        }, data=text.encode('utf-8'))

        return response.content.decode('utf-8')

    def detect_language(self, text: str) -> str:
        return self._language(text)
