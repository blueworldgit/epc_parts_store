from rest_framework import serializers
from .models import SerialNumber, ParentTitle, ChildTitle, Part

class SerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SerialNumber
        fields = '__all__'

class ParentTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentTitle
        fields = '__all__'

class ChildTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildTitle
        fields = '__all__'

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = '__all__'
