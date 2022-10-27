import requests


def get_model_languages() -> dict[str, dict[str, str]]:
    response = requests.get('http://localhost:9100/state/models/languages')
    if not response.ok:
        pass  # todo do something?
    return response.json()
