"""Define how data types are passed to urls"""

class BooleanPathConverter:
    regex = '[0-1]{1}'

    def to_python(self, value):
        if value == '1':
            return True
        else:
            return False

    def to_url(self, value):
        if value:
            return '1'
        else:
            return '0'