from apps.category.models import Category

electronic = Category.objects.first()
electronic.get_children()
electronic = Category.objects.get(slug="electronics")
electronic.get_children()
electronic.get_ancestors()
children = electronic.get_children()
mobile = children.first()
computer = children.first()
mobile = children.last()
mobile.get_ancestors()
electronic.get_descendants()