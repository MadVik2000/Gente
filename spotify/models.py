from django.core.exceptions import ValidationError
from django.db import models

from helpers.models import CustomModel


# Create your models here.
class SpotifyAccessToken(CustomModel):
    """
    This model stores all the access tokens used to access Spotify web API
    """

    access_token = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)

    def validate_is_active(self):
        if not self.id and self.is_active:
            active_access_tokens = SpotifyAccessToken.objects.filter(
                is_active=True
            )
            if active_access_tokens.exists():
                active_access_tokens.update(is_active=False)

        elif self.id and self.is_active and self.diff.get("is_active"):
            raise ValidationError("Inactive access tokens cannot be activated.")

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)
        self.validate_is_active()
