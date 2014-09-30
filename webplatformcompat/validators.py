from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import ugettext_lazy as _
from django.utils.six import string_types


class LanguageDictValidator(object):
    '''Check for valid language dictionary'''

    def __call__(self, value):
        if not isinstance(value, dict):
            raise ValidationError(
                _("Value must be a JSON dictionary of language codes to"
                  " strings."))
        if 'en' not in value:
            raise ValidationError(_("Missing required language code 'en'."))
        for language_code, text in value.items():
            if not isinstance(text, string_types):
                raise ValidationError(
                    _('For language "%(lang)s, text "%(text)s" is not a'
                      ' string.'),
                    params={'lang': language_code, 'text': text})


class SecureURLValidator(URLValidator):
    '''URLValidator, but protocol must be https'''

    def __call__(self, value):
        super(SecureURLValidator, self).__call__(value)
        if not value.lower().startswith('https://'):
            raise ValidationError(_("URI must use the 'https' protocol."))
