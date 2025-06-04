from rest_framework import serializers
from .models import OfferLetter, AuditLog

class OfferLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferLetter
        fields = ['student', 'consultant','document', 'sent_at']
        read_only_fields = ['sent_at']

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
