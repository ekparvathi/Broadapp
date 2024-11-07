from rest_framework import serializers
from .models import JobPostings,Profile,Applications_received

class jobpostserializer(serializers.ModelSerializer):
    class Meta:
        model=JobPostings
        fields= '__all__'
        
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__' 
        
class applyserializer(serializers.ModelSerializer):
    class Meta:
        model=Applications_received
        fields='__all__'