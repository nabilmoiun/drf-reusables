from rest_framework import serializers


class TreeSerializer(serializers.ModelSerializer):
    
    children = serializers.SerializerMethodField()

    def get_children(self, obj) -> list:
        serializer =  self.__class__(
            obj.children.filter(is_active=True),
            many=True
        )
        return serializer.data

