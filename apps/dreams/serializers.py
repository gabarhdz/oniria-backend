from rest_framework import serializers
from .models import EmotionalEntry, EmotionalCategory, EmotionalMilestone, emotions
from apps.users.serializers import UserSerializer


class EmotionalCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionalCategory
        fields = ['id', 'name', 'color', 'icon']


class EmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = emotions
        fields = ['id', 'name']


class EmotionalEntrySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    categories = EmotionalCategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    emotions = EmotionSerializer(many=True, read_only=True)
    emotion_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = EmotionalEntry
        fields = [
            'id', 'user', 'title', 'content', 'entry_date',
            'created_at', 'updated_at', 'mood', 'intensity',
            'categories', 'category_ids', 'emotions', 'emotion_ids',
            'tags', 'tags_list', 'ai_analysis', 'ai_analyzed_at',
            'is_private', 'is_favorite'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'ai_analyzed_at']
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        emotion_ids = validated_data.pop('emotion_ids', [])
        
        entry = EmotionalEntry.objects.create(**validated_data)
        
        if category_ids:
            entry.categories.set(category_ids)
        if emotion_ids:
            entry.emotions.set(emotion_ids)
        
        return entry
    
    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        emotion_ids = validated_data.pop('emotion_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if category_ids is not None:
            instance.categories.set(category_ids)
        if emotion_ids is not None:
            instance.emotions.set(emotion_ids)
        
        return instance


class EmotionalEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear entradas rápidamente"""
    
    class Meta:
        model = EmotionalEntry
        fields = ['title', 'content', 'entry_date', 'mood', 'intensity', 'tags']
    
    def create(self, validated_data):
        return EmotionalEntry.objects.create(**validated_data)


class EmotionalMilestoneSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    entry = EmotionalEntrySerializer(read_only=True)
    entry_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = EmotionalMilestone
        fields = [
            'id', 'user', 'entry', 'entry_id', 'title',
            'description', 'milestone_date', 'icon', 'color', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmotionalStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas emocionales"""
    total_entries = serializers.IntegerField()
    entries_this_month = serializers.IntegerField()
    entries_this_week = serializers.IntegerField()
    mood_distribution = serializers.DictField()
    average_intensity = serializers.FloatField()
    most_common_emotions = serializers.ListField()
    most_common_categories = serializers.ListField()
    streak_days = serializers.IntegerField()
    favorite_entries = serializers.IntegerField()