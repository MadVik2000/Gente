"""
This file contains all the custom models used in the project
"""

from django.db import models

from helpers.mixins import ModelDifferenceMixin


class CustomModel(models.Model, ModelDifferenceMixin):
    """
    This custom model class will be used to implement models
    throughout this project
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
