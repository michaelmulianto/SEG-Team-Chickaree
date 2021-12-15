from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator

class ValueInListValidator(BaseValidator):
    message = 'Ensure this value (%(show_value)d) is in %(limit_value)s.'
    code = 'in_list'
    
    def compare(self, a, b):
        # return false when validation passes.........
        # This is how BaseValidator handles it.
        return not(a in b)