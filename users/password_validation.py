from collections import Counter
import math
import re
from django.forms import ValidationError
from django.utils.translation import gettext as _


class CharacterRepeatValidator:
    def validate(self, password, user=None):
        """
        Validate whether the password contains the same character more than three times in a row.
        """
        if re.search(r"(.)\1\1", password):
            raise ValidationError(
                _(
                    "This password contains the same character more than two times in a row."
                ),
                code="password_character_repetition",
            )

    def get_help_text(self):
        return "Your password must not contain the same character more than three times in a row."


class EntropyValidator:
    def _calculate_password_entropy(self, password):
        if not password:
            return 0

        freq_dist = Counter(password)
        password_length = len(password)

        entropy = -sum(
            (freq / password_length) * math.log2(freq / password_length)
            for freq in freq_dist.values()
        )

        return entropy

    def validate(self, password, user=None):
        """
        Validate whether the password contains the same character more than three times in a row.
        """
        if self._calculate_password_entropy(password) < 3:
            raise ValidationError(
                _("This password is too weak. Please use a stronger password."),
                code="password_weakness",
            )

    def get_help_text(self):
        return "Please use as many different characters as possible. Try not to repeat the same characters."
