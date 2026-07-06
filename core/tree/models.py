from django.db import models


class TreeModel(models.Model):
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children"
    )

    class Meta:
        abstract = True

    def get_children(self):
        return self.children.all()
    
    def get_ancestors(self):
        node = self
        ancestors = list()

        while node.parent:
            ancestors.insert(0, node.parent)
            node = node.parent

        return ancestors
    
    def get_descendants(self):
        descendants = list()

        def traverse(node):
            for child in node.get_children():
                descendants.append(child)
                traverse(child)

        traverse(self)

        return descendants
    

        


    
