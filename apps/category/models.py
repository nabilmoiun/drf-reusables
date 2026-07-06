from django.db import models
from django.core.exceptions import ValidationError

from core.tree.models import TreeModel
from apps.common.models import TimeStampedUUIDModel


class Category(TimeStampedUUIDModel, TreeModel):
    title = models.CharField(max_length=250)
    slug = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Category"

    def __str__(self):
        return self.title
    
    def clean(self):
        if self.parent == self:
            raise ValidationError("Category cannot be its own parent.")

        node = self.parent

        while node:
            if node == self:
                raise ValidationError("Circular hierarchy detected.")
            node = node.parent


