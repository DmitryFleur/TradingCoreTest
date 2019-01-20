from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from social_network.models import UserProfile, Post
from social_network.constants import USE_HUNTER, HUNTER_API_KEY
from pyhunter import PyHunter


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True,
                                     validators=[UniqueValidator(queryset=UserProfile.objects.all())])
    email = serializers.EmailField(required=True,
                                   validators=[UniqueValidator(queryset=UserProfile.objects.all())])
    password = serializers.CharField(required=True,
                                     max_length=50)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError('Passwords are not the same')
        if USE_HUNTER:
            hunter = PyHunter(HUNTER_API_KEY)
            resp = hunter.email_verifier(data.get('email'))
            # Frankly saying have no idea what to check here,
            # as api poorly documented https://hunter.io/api/docs#email-verifier
            # At first I thought that it should mark as 'deliverable',
            # but my gmail address it marks as 'risky'.
            if not resp['regexp'] and not resp['gibberish']:
                raise serializers.ValidationError('Email has not passed Hunter verification')
        return data

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password', 'confirm_password')


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'phone', 'first_name', 'last_name', 'interests',
                  'about_me', 'city', 'country')


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'
