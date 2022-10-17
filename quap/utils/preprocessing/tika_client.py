import requests


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
            'Accept': 'text/plain'
        }, data=binary)

        if response.status_code != 200:
            raise ValueError('unknown format, Tika could not process the file')

        return response.content.decode('utf-8')

    def extract(self, binary: bytes) -> str:
        return self._tika(binary)

    def _language(self, text: str) -> str:
        response = requests.put(self._url_join('language', 'string'), headers={
            'Content-Type': 'text/plain',
            'Accept': 'text/plain'
        }, data=text.encode('utf-8'))

        return response.content.decode('utf-8')

    def detect_language(self, text: str) -> str:
        return self._language(text)
