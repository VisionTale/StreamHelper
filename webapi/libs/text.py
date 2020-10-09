def camel_case(text: str, delimiter: str = ' ') -> str:
    """
    Makes all words capitalized
    :param text: text to convert
    :param delimiter: delimiter to split words, defaults to the space character
    :return: camel case string
    """
    return ''.join([e.capitalize() for e in text.split(delimiter)])
