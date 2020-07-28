import re

URL_PATTERN = re.compile(r"(?:http|https):\/\/\S*[^(. )]")


def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)


def extendlinks(value):
    if value:
        value = URL_PATTERN.sub(r"<a href='\g<0>' class='truncated'>\g<0></a>", value)
    return value
