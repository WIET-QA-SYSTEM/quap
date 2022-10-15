import re


_FORBIDDEN_CHARS = r'\/*?"<>| ,#:'
_FORBIDDEN_CHARS_PATTERN = re.compile('|'.join([re.escape(char) for char in _FORBIDDEN_CHARS]))


def normalize_index_name(index_name: str) -> str:
    """
    Source: https://discuss.elastic.co/t/index-name-type-name-and-field-name-rules/133039

    The rules for index names are encoded in MetaDataCreateIndexService 772. Essentially:

        Lowercase only
        Cannot include \, /, *, ?, ", <, >, |, space (the character, not the word), ,, #
        Indices prior to 7.0 could contain a colon (:), but that's been deprecated and won't be supported in 7.0+
        Cannot start with -, _, +
        Cannot be . or ..
        Cannot be longer than 255 characters
    """

    forbidden_chars = r'\/*?"<>| ,#:'
    index_name = _FORBIDDEN_CHARS_PATTERN.sub('', index_name)
    index_name = index_name.lstrip('-_+')

    if index_name in ('.', '..'):
        raise ValueError('index name cannot be normalized')

    return index_name[:255]
