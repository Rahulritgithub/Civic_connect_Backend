from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Post, User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone_number', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

# serializers.py
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                # Get user by email
                user = User.objects.get(email=email)
                # Check password manually since we can't use authenticate without username
                if user.check_password(password):
                    if not user.is_active:
                        raise serializers.ValidationError("User account is disabled.")
                    attrs['user'] = user
                    return attrs
                else:
                    raise serializers.ValidationError("Invalid password.")
            except User.DoesNotExist:
                raise serializers.ValidationError("No user found with this email address.")
        else:
            raise serializers.ValidationError("Both email and password are required.")
        
class PostQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id','title', 'description', 'location', 'category', 
            'urgency', 'image', 'user', 'created_at', 'votes'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'votes']
    
    def create(self, validated_data):
        # Get the user from the request context
        user = self.context['request'].user
        
        # If user is authenticated, use that user, otherwise create anonymous user
        if user.is_authenticated:
            validated_data['user'] = user
        else:
            # Option 1: Use a default "anonymous" user
            # Option 2: Create a new user for anonymous posts
            # Option 3: Allow null user (if your model permits)
            anonymous_user, created = User.objects.get_or_create(
                username='anonymous',
                defaults={'email': 'anonymous@example.com'}
            )
            validated_data['user'] = anonymous_user
        
        return super().create(validated_data)
