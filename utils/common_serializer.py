from rest_framework import serializers

class BaseModelSerializer(serializers.ModelSerializer):
    
    def create(self, validated_data):

        return super().create(validated_data)
    
    