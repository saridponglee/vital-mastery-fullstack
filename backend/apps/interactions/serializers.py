from rest_framework import serializers
from apps.users.serializers import UserSerializer
from .models import Comment, Like, Bookmark


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = (
            'id', 'content', 'author', 'parent', 'is_approved',
            'created_at', 'updated_at', 'replies', 'reply_count'
        )
        read_only_fields = ('id', 'author', 'is_approved', 'created_at', 'updated_at')
    
    def get_replies(self, obj):
        """Get replies to this comment."""
        if obj.is_reply:  # Don't get replies for replies (keep it simple)
            return []
        
        replies = obj.get_replies()
        return CommentSerializer(replies, many=True, context=self.context).data
    
    def get_reply_count(self, obj):
        """Get count of replies."""
        return obj.replies.filter(is_approved=True).count()


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments.
    """
    
    class Meta:
        model = Comment
        fields = ('content', 'parent')
    
    def validate_parent(self, value):
        """Validate parent comment."""
        if value and value.is_reply:
            raise serializers.ValidationError(
                "Cannot reply to a reply. Please reply to the original comment."
            )
        return value


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Like model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ('id', 'user', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')


class BookmarkSerializer(serializers.ModelSerializer):
    """
    Serializer for Bookmark model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'created_at')
        read_only_fields = ('id', 'user', 'created_at') 