from rest_framework import serializers
from .models import OfferLetter, AuditLog, UserProfile, User
from django.utils.timesince import timesince

class OfferLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferLetter
        fields = ['user','student','document', 'sent_at']
        read_only_fields = ['sent_at']
        
class OfferLetterListSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    document = serializers.ReadOnlyField(source='document.name')
    time_elapsed = serializers.SerializerMethodField()
    
    class Meta:
        model = OfferLetter
        fields = '__all__'
        read_only_fields = ['sent_at']
        
    def get_time_elapsed(self, obj):
        return timesince(obj.sent_at)

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role']

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'userprofile']