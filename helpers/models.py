"""
This file contains all the custom models used in the project
"""

from django.contrib.auth import get_user_model
from django.db import models

from helpers.mixins import ModelDifferenceMixin

User = get_user_model()


class CustomModel(models.Model, ModelDifferenceMixin):
    """
    This custom model class will be used to implement models
    throughout this project
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name="%(class)s_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name="%(class)s_updated_by"
    )
    deleted_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name="%(class)s_deleted_by"
    )

    LOG_FIELDS = [created_at, updated_at, created_by, updated_by, deleted_by]

    def save(self, *args, **kwargs):
        skip_cleaning = kwargs.pop("skip_cleaning", False)
        if not skip_cleaning:
            self.full_clean(exclude=kwargs.pop("exclude_cleaning", None))
        super().save(*args, **kwargs)

    class Meta:
        """
        Defines meta information for the model
        """

        abstract = True
