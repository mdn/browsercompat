"""API field validators."""
import re

from django.core.exceptions import ValidationError
from django.db.models import Model
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _
from django.utils.six import string_types
from rest_framework.exceptions import ValidationError as DRFValidationError


@deconstructible
class LanguageDictValidator(object):
    """Check for valid language dictionary."""

    def __init__(self, allow_canonical=False):
        self.allow_canonical = allow_canonical

    def __call__(self, value):
        if value is None:
            return
        if not isinstance(value, dict):
            raise ValidationError(
                _('Value must be a JSON dictionary of language codes to'
                  ' strings.'))
        if 'zxx' in value:
            if self.allow_canonical and list(value.keys()) != ['zxx']:
                raise ValidationError(
                    _("Language code 'zxx' not allowed with other values."))
            elif not self.allow_canonical:
                raise ValidationError(_("Language code 'zxx' not allowed"))
        elif 'en' not in value:
            raise ValidationError(_("Missing required language code 'en'."))
        for language_code, text in value.items():
            if not isinstance(text, string_types):
                raise ValidationError(
                    _('For language "%(lang)s, text "%(text)s" is not a'
                      ' string.'),
                    params={'lang': language_code, 'text': text})

    def __eq__(self, other):
        """Check equivalency to another LanguageDictValidator.

        Required for migration detection.
        """
        if isinstance(other, self.__class__):
            return self.allow_canonical == other.allow_canonical
        else:
            return False

    def __ne__(self, other):
        """Check non-equivalency to another LanguageDictValidator."""
        return not self.__eq__(other)


class VersionAndStatusValidator(object):
    """For Version resource, restrict version/status combinations."""

    # From http://stackoverflow.com/questions/82064
    re_numeric = re.compile(r"^(?:(\d+)\.)?(?:(\d+)\.)?(\*|\d+)$")

    def __init__(self):
        """Initialize for Django model validation."""
        self.instance = None
        self.Error = ValidationError

    def set_context(self, serializer_field):
        """
        Switch to Django Rest Framework (DRF) Serializer validation.

        DRF 3.1.3 treats Django's ValidationError as non-field errors, ignoring
        the message dictionary calling out the particular fields. When
        DRF calls set_context(), switch to the DRF ValidationError class, so
        that errors will be targetted to the field that needs to be changed.
        """
        self.instance = serializer_field.instance
        self.Error = DRFValidationError

    def __call__(self, value):
        """Validate version/status combinations."""
        if isinstance(value, Model):
            # Called from Django model validation, value is Version instance
            version = value.version
            status = value.status
        else:
            # Called from DRF serializer validation, value is dict
            if self.instance:
                # Called from update
                version = value.get('version', self.instance.version)
                status = value.get('status', self.instance.status)
            else:
                # Called from create
                version = value['version']
                status = value.get('status', 'unknown')

        if not version:
            # DRF will catch in field validation
            raise self.Error({'version': ['This field may not be blank.']})

        is_numeric = bool(self.re_numeric.match(version))
        numeric_only = ['beta', 'retired beta', 'retired', 'unknown']
        if status in numeric_only and not is_numeric:
            msg = 'With status "{0}", version must be numeric.'.format(status)
            raise self.Error({'version': [msg]})

        if status == 'future' and is_numeric:
            msg = ('With status "future", version must be non-numeric.'
                   ' Use status "beta" for future numbered versions.')
            raise self.Error({'version': [msg]})

        if status == 'current' and not (is_numeric or version == 'current'):
            msg = ('With status "current", version must be numeric or'
                   ' "current".')
            raise self.Error({'version': [msg]})

        if version == 'current' and status != 'current':
            msg = 'With version "current", status must be "current".'
            raise self.Error({'status': [msg]})
