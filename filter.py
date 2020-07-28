import re

URL_PATTERN = re.compile(r"(?:http|https):\/\/\S*[^(. )]")


def extendlinks(value):
    if value:
        for url_match in URL_PATTERN.finditer(value):
            url = url_match.group(0)
            value = value.replace(url, f"<a href='{url}'>{url}</a>")
    return value
