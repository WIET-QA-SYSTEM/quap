from more_itertools import windowed
from spacy.tokens import Token
import spacy

from quap.data import Document, Context


class PassageSegmentation:
    def __init__(
            self,
            split_strategy: str = 'spacy-tokens',
            window_size: int = 100,
            stride: float = 0.9,
            language: str = 'en',
    ) -> None:

        self.split_strategy = split_strategy
        self.window_size = window_size
        self.stride = stride
        self.step = int(self.stride * self.window_size)
        self.language = language

        # we load the tokenizer for all the strategies using spacy
        if split_strategy in ['spacy-tokens']:
            try:
                nlp = spacy.blank(language)
                self.spacy_tokenizer = nlp.tokenizer
            except (ModuleNotFoundError, ImportError) as ex:
                raise ValueError(f'{language} language not supported') from ex

    def split(self, document: Document) -> list[Context]:
        text = document.text
        if self.split_strategy == 'none':
            return [Context(document, 0, len(text))]

        contexts = []
        if self.split_strategy == 'spacy-tokens':
            doc = self.spacy_tokenizer(text)
            tokens: list[Token] = [token for token in doc if not token.is_space]  # skipping empty tokens

            for window in windowed(tokens, self.window_size, step=self.step):
                start = window[0].idx
                end = window[-1].idx + len(window[-1]) if window[-1] is not None else len(text)

                contexts.append(Context(document, start, end-start))
        else:
            raise ValueError(f'unknown split strategy - {self.split_strategy}')

        return contexts
