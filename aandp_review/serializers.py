from rest_framework import serializers  # Import the serializer class
from .models import Note  # Import the Note model

# Create a serializer class
# This class will convert the Note model into JSON


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
