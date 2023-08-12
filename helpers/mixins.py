"""
This file contains all the mixins that can be used within the project
"""
from django.db import models
from django.utils.functional import empty


class ModelDifferenceMixin:
    """
    This mixin tracks all the changes in a model instance before it is saved
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial = self._dict

    @property
    def _dict(self):
        """
        Returns a dictionary representation of model field and their values
        """
        deferred_fields = self.get_deferred_fields()
        fields = []

        for field in self._meta.fields:
            if (
                field.name in deferred_fields
                or isinstance(field, (models.ForeignKey, models.OneToOneField))
                and field.attname in deferred_fields
            ):
                continue

            fields.append(field)

        return {field.name: getattr(self, field.name, None) for field in fields}

    def save(self, *args, **kwargs):
        """
        Saves the model instance and sets their initial state
        """
        super().save(*args, **kwargs)
        self._initial = self._dict

    @property
    def diff(self):
        """
        Returns the difference between initial and current model instance
        """
        if not self.pk:
            return {}

        difference_one = self._initial
        difference_two = self._dict

        differences = {
            key: (
                difference_one.get(key, empty),
                difference_two.get(key, empty),
            )
            for key in set(difference_one.keys()).union(
                set(difference_two.keys())
            )
            if key not in difference_one
            or key not in difference_two
            or difference_one[key] != difference_two[key]
        }

        return differences
