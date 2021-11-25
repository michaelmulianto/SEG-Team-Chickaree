"""Define how data types are passed to urls"""

class BooleanPathConverter:
    regex = '[0-1]{1}'

    def to_python(self, value):
        return bool(value)

    def to_url(self, value):
        return value