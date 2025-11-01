from rest_framework import serializers
from .models import Event, Review, UserProfile , RSVP

class RegisterSerializer(serializers.ModelSerializer):
    password_2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'full_name', 'password', 'password_2', 'email', 'bio', 'location', 'profile_picture']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, data):
        if data['password'] != data['password_2']:
            raise serializers.ValidationError("Passwords do not match.")
        if UserProfile.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists.")
        if data['password'] and len(data['password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_2')
        user = UserProfile(
            username=validated_data['username'],
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            bio=validated_data.get('bio', ''),
            location=validated_data.get('location', ''),
            profile_picture=validated_data.get('profile_picture', None)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
        
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        
class ReviewSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Review
        fields = '__all__'        
        
class RSVPSerializer(serializers.ModelSerializer):    
    class Meta:
        model = RSVP
        fields = '__all__'        