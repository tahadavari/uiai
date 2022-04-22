from rest_framework import serializers
from account.serializers import AuthorSerializer
from blog.models import Post, Comment, Report, Tag


class PostCommentSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        request = self.context.get('request')
        data = {
            "id": instance.hash,
            "author": AuthorSerializer(instance=instance.author).data,
            "date": instance.get_string_published_at(),
            "content": instance.body,
            "parentId": instance.parent.hash if instance.parent else None,
            "children": PostCommentSerializer(instance.childes, many=True, context={'request': request}).data,
            "like": {
                "count": int(instance.like_count),
                "isLiked": instance.liked(request.user)
            },
            "level": instance.get_level()
        }
        return data


class PostTagSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        data = {
            "id": instance.hash,
            "name": instance.name,
            "href": instance.href(),
            "taxonomy": "tag",
            "thumbnail":instance.image_url(),
            "count" : instance.posts_main_tag.filter(status=Post.STATUS_PUBLISHED).count() + instance.posts_tags.filter(status=Post.STATUS_PUBLISHED).count(),
        }
        return data


class PostSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        request = self.context.get('request')

        data = {
            "id": instance.hash,
            "author": AuthorSerializer(instance=instance.author).data,
            "date": instance.get_string_published_at(),
            "href": instance.href(),
            "categories": PostTagSerializer(instance=instance.tags, many=True).data,
            "title": instance.title,
            "featuredImage": instance.cover_url(),
            "desc": instance.description,
            "like": {
                "count": int(instance.like_count),
                "isLiked": instance.liked(request.user)
            },
            "bookmark": {
                "count": int(instance.bookmark_count),
                "isBookmarked": instance.bookmarked(request.user)
            },
            "commentCount": int(instance.comment_count),
            "viewdCount": int(instance.view_count),
            "readingTime": int(instance.reading_time),
            "postType": "standard",
            "data": instance.body,
        }
        data['categories'].append({
            "id": instance.main_tag.hash,
            "name": instance.main_tag.name,
            "href": instance.main_tag.href(),
            "taxonomy": "category",
            "color": "red"
        })
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['hash', 'author', 'liked', 'comment_count',
                  'like_count', 'body', 'published_at']

    def get_liked(self, obj):
        request = self.context.get('request')
        return obj.liked(user=request.user)


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['author', 'parent', 'body', 'post', 'status', 'published_at']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['user', 'body', 'report_object_type',
                  'report_type', 'report_object_id']


class TagsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'hash']


class AddPostSerializer(serializers.ModelSerializer):
    tags = serializers.ListField()
    body = serializers.JSONField(initial=dict)

    class Meta:
        model = Post
        fields = ['author', 'title', 'description', 'body',
                  'cover', 'main_tag', 'tags', 'status', 'reading_time']

    def create(self, validated_data):
        tags = validated_data['tags'][0]
        del validated_data['tags']
        post = Post.objects.create(**validated_data)
        for tag_id in tags:
            tag = Tag.objects.get(id=int(tag_id))
            post.tags.add(tag)
        post.save()
        return post


class UpdatePostSerializer(serializers.ModelSerializer):
    tags = serializers.ListField()
    body = serializers.JSONField(initial=dict)
    cover = serializers.ImageField(required=False)

    class Meta:
        model = Post
        fields = ['hash', 'author', 'title', 'description', 'body', 'cover', 'main_tag', 'tags', 'status',
                  'reading_time']
        extra_kwargs = {
            'cover': {'required': False}
        }

    def update(self, post, validated_data):
        tags = validated_data['tags'][0]
        del validated_data['tags']
        super().update(post, validated_data)
        post.tags.clear()
        for tag_id in tags:
            tag = Tag.objects.get(id=int(tag_id))
            post.tags.add(tag)
        post.save()
        return post


class GetUpdatePostSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='hash'
    )
    main_tag = serializers.SlugRelatedField(
        read_only=True,
        slug_field='hash'
    )

    class Meta:
        model = Post
        fields = ['title', 'description', 'body',
                  'cover', 'main_tag', 'tags', 'status']


class PostsListProfileSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(method_name='get_status')
    cover  = serializers.SerializerMethodField(method_name='get_cover_url')
    class Meta:
        model = Post
        fields = ['hash', 'title', 'cover', 'view_count', 'status', 'slug']

    def get_status(self, obj):
        status_object = {
            "value": obj.status,
            "label": obj.get_persian_status()
        }
        return status_object
        
    def get_cover_url(self, obj):
        return obj.cover_url()


class PostCardSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        request = self.context.get('request')

        data = {
            "id": instance.hash,
            "author": AuthorSerializer(instance=instance.author).data,
            "date": instance.get_string_published_at(),
            "href": instance.href(),
            "categories": PostTagSerializer(instance=instance.tags, many=True).data[0:2],
            "title": instance.title,
            "featuredImage": instance.cover_url(),
            "desc": instance.description,
            "like": {
                "count": int(instance.like_count),
                "isLiked": instance.liked(request.user)
            },
            "bookmark": {
                "count": int(instance.bookmark_count),
                "isBookmarked": instance.bookmarked(request.user)
            },
            "commentCount": int(instance.comment_count),
            "viewdCount": int(instance.view_count),
            "readingTime": int(instance.reading_time),
            "postType": "standard",
        }
        data['categories'].append({
            "id": instance.main_tag.hash,
            "name": instance.main_tag.name,
            "href": instance.main_tag.href(),
            "taxonomy": "category",
            "color": "red"
        })
        return data


class TagViewSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        data = {
            'hash': instance.hash,
            'name': instance.name,
            'post_count': instance.posts_main_tag.count() + instance.posts_tags.count(),
            'image': instance.image_url(),
            'href': instance.href(),
            'slug':instance.slug
        }
        return data

