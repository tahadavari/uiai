import ast
from datetime import datetime
import readtime

from django.db.models import Q
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.paginations import PostsListProfileSetPagination, PostsArchivePagination,TagsArchivePagination
from core.permissions import IsAuthenticated
from blog.models import Post, Like, Comment, Bookmark, Report, Tag
from blog.serializers import PostSerializer, CommentSerializer, CommentCreateSerializer, ReportSerializer, \
    TagsListSerializer, AddPostSerializer, PostsListProfileSerializer, UpdatePostSerializer, GetUpdatePostSerializer, PostCommentSerializer, PostCardSerializer, TagViewSerializer, PostTagSerializer


class PostViewAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug: str):
        hash = slug.split('-')[-1]
        post = Post.objects.hash(hash)
        post.view_count += 1
        post.save()
        post_data = PostSerializer(post, context={'request': request}).data
        return Response(post_data, status=status.HTTP_200_OK)


class LikeApi(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, type):
        user = request.user
        data = {}
        if type == 'post':
            post_id = Post.objects.hash(request.data.get('hash')).id
            if Like.check_like_available(post_id, Like.TYPE_POST, user):
                like = Like.check_like_available(post_id, Like.TYPE_POST, user)
                like.delete()
                post = Post.objects.get(id=post_id)
                post.like_count -= 1
                if not post.like_count:
                    post.like_count = 0
                post.save()
                data = {
                    'liked': False,
                    'count': like.get_like_count()
                }
            else:
                like = Like(likeable_id=post_id,
                            likeable_type=Like.TYPE_POST, user=user)
                like.save()
                post = Post.objects.get(id=post_id)
                post.like_count += 1
                post.save()
                data = {
                    'liked': True,
                    'count': like.get_like_count()
                }
        elif type == 'comment':
            comment_id = Comment.objects.hash(request.data.get('hash')).id
            if Like.check_like_available(comment_id, Like.TYPE_COMMENT, user):
                like = Like.check_like_available(
                    comment_id, Like.TYPE_COMMENT, user)
                like.delete()
                comment = Comment.objects.get(id=comment_id)
                comment.like_count -= 1
                if not comment.like_count:
                    comment.like_count = 0
                comment.save()
                data = {
                    'liked': False,
                    'count': like.get_like_count()
                }
            else:
                like = Like(likeable_id=comment_id,
                            likeable_type=Like.TYPE_COMMENT, user=user)
                like.save()
                comment = Comment.objects.get(id=comment_id)
                comment.like_count += 1
                comment.save()
                data = {
                    'liked': True,
                    'count': like.get_like_count()
                }
        else:
            data = {
                'message': 'type not support'
            }
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(data, status=status.HTTP_200_OK)


class BookmarkApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post = Post.objects.hash(request.data.get('hash'))
        user = request.user
        data = {}
        if Bookmark.check_bookmark_available(post, user):
            bookmark = Bookmark.objects.filter(post=post, user=user).filter()
            bookmark.delete()
            data = {
                'bookmarked': False
            }
            post.bookmark_count -= 1
            post.save()
        else:
            bookmark = Bookmark(post=post, user=user)
            bookmark.save()
            data = {
                'bookmarked': True
            }
            post.bookmark_count += 1
            post.save()
        return Response(data, status=status.HTTP_200_OK)


class CommentApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        body = request.data.get('body')
        parent = Comment.objects.hash_or_null(request.data.get('parent_hash'))
        if parent:
            post = parent.post
        else:
            post = Post.objects.hash(request.data.get('post_hash'))
        parent = parent.id if parent else None
        user = request.user
        data = {
            'body': body,
            'author': user.id,
            'parent': parent,
            'post': post.id,
            'status': Comment.STATUS_PUBLISHED,
            'published_at': datetime.now()
        }
        comment_serializer = CommentCreateSerializer(data=data)
        comment_serializer.is_valid(raise_exception=True)
        comment = comment_serializer.save()
        post.comment_count += 1
        post.save()
        data = PostCommentSerializer(
            comment, context={'request': request}).data
        return Response(data, status=status.HTTP_200_OK)


class CommentViewApi(APIView):
    def get(self, request, hash):
        post = Post.objects.hash(hash)
        data = {
            'comments': PostCommentSerializer(post.comments, many=True, context={'request': request}).data,
        }
        return Response(data, status=status.HTTP_200_OK)


class ChildCommentApi(APIView):
    def get(self, request, hash):
        comment = Comment.objects.hash(hash)
        child = comment.childes.all()
        child_data = PostCommentSerializer(
            child, context={'request': request}, many=True).data
        data = {
            'comments': child_data
        }
        return Response(data, status=status.HTTP_200_OK)


class ReportApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, type):
        data = {}
        if type == 'post':
            body = request.data.get('body')
            report_type = request.data.get('type')
            post = Post.objects.hash(request.data.get('post_hash'))
            user = request.user
            data = {
                'body': body,
                'user': user.id,
                'report_object_id': post.id,
                'report_type': report_type,
                'report_object_type': Report.OBJECT_TYPE_POST,
            }
        elif type == 'comment':
            body = request.data.get('body')
            report_type = request.data.get('type')
            comment = Comment.objects.hash(request.data.get('comment_hash'))
            user = request.user
            data = {
                'body': body,
                'user': user.id,
                'report_object_id': comment.id,
                'report_type': report_type,
                'report_object_type': Report.OBJECT_TYPE_COMMENT,
            }
        report_serializer = ReportSerializer(data=data)
        report_serializer.is_valid(raise_exception=True)
        report = report_serializer.save()
        response = {
            'message': 'گزارش با موفقیت ثبت شد',
            'success': True
        }
        return Response(response, status=status.HTTP_200_OK)


class TagsListApi(generics.GenericAPIView):
    serializer_class = TagsListSerializer
    queryset = Tag.objects.all()

    # permission_classes = []

    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagsListSerializer(data=tags, many=True)
        serializer.is_valid()
        data = serializer.data
        data = [{'label': x['name'], 'value': x['hash']} for x in data]
        return Response(data=data, status=status.HTTP_200_OK)


class AddPostApi(generics.GenericAPIView):
    serializer_class = AddPostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        data['body'] = data['body']
        data['author'] = request.user.id
        data['main_tag'] = Tag.objects.hash(request.data.get('main_tag')).id
        tags = ast.literal_eval(data['tags'])
        data['tags'] = [Tag.objects.hash(x).id for x in tags]
        if data['main_tag'] in data['tags']:
            data['tags'].remove(data['main_tag'])
        if request.data.get('status') == 5:
            data['status'] = Post.STATUS_HIDDEN
        else:
            data['status'] = Post.STATUS_AWAITING_APPROVAL
        data['reading_time'] = readtime.of_html(request.data.get('body')).seconds // 60
        post_serializer = AddPostSerializer(data=data)
        post_serializer.is_valid(raise_exception=True)
        post_serializer.save()
        return Response({'success': True, 'status': data['status']}, status=status.HTTP_200_OK)


class UpdatePostApi(generics.GenericAPIView):
    serializer_class = UpdatePostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, hash):
        post = Post.objects.hash(hash)
        post_serializer = GetUpdatePostSerializer(post)
        data = post_serializer.data
        tag = Tag.objects.hash(data['main_tag'])
        tags = [Tag.objects.hash(x) for x in data['tags']]
        status_post = data['status']
        data['tags'] = [{'label': x.name, 'value': x.hash} for x in tags]
        data['main_tag'] = {'label': tag.name, 'value': tag.hash}
        if data['status'] == 2:
            data['status'] = {
            'label': 'انتشار', 'value': status_post}
        else:
            data['status'] = {
            'label': 'پیش نویس', 'value': status_post}
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request):
        post = Post.objects.hash(request.data.get('hash'))
        data = request.data.copy()
        data['body'] = request.data.get('body')
        data['author'] = request.user.id
        data['main_tag'] = Tag.objects.hash(request.data.get('main_tag')).id
        tags = ast.literal_eval(data['tags'])
        data['tags'] = [Tag.objects.hash(x).id for x in tags]
        if data['main_tag'] in data['tags']:
            data['tags'].remove(data['main_tag'])
        if request.data.get('status') == 5:
            data['status'] = Post.STATUS_HIDDEN
        else:
            data['status'] = Post.STATUS_AWAITING_APPROVAL
        data['reading_time'] = readtime.of_html(request.data.get('body')).seconds // 60
        post_serializer = UpdatePostSerializer(post, data=data)
        post_serializer.is_valid(raise_exception=True)
        post_serializer.save()
        return Response({'success': True, 'status': data['status']}, status=status.HTTP_200_OK)


class PostsListProfileApi(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostsListProfileSerializer
    pagination_class = PostsListProfileSetPagination
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(
            author=request.user).order_by('-created_at')
        posts_paginate = self.paginate_queryset(posts)
        if posts_paginate:
            return self.get_paginated_response(
                PostsListProfileSerializer(posts_paginate, many=True).data)
        else:
            return Response({}, status=status.HTTP_200_OK)


class DeletePostApi(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post = Post.objects.hash(request.data.get('hash'))
        post.status = Post.STATUS_DELETE_BY_AUTHOR
        post.save()
        return Response({"message": "پست شما با موفقیت حذف شد", "success": True}, status=status.HTTP_200_OK)


class MorePostFromAuthor(generics.GenericAPIView):
    queryset = Post.objects.all()

    def get(self, request, hash):
        queryset = Post.objects.all()
        post = Post.objects.hash(hash)
        more_post = post.get_more_from_author()
        data = PostCardSerializer(more_post, many=True, context={
                                  'request': request}).data
        return Response(data=data, status=status.HTTP_200_OK)


class RelatedPost(generics.GenericAPIView):
    queryset = Post.objects.all()

    def get(self, request, hash):
        post = Post.objects.hash(hash)
        related_post = post.get_realted_post()
        data = PostCardSerializer(related_post, many=True, context={
                                  'request': request}).data
        return Response(data=data, status=status.HTTP_200_OK)


class TagView(generics.ListAPIView):
    queryset = Tag.objects.all()

    def get(self, request, slug):
        hash = slug.split('-')[-1]
        tag = Tag.objects.hash(hash)
        data = TagViewSerializer(tag).data
        return Response(data=data, status=status.HTTP_200_OK)


class OtherTags(generics.GenericAPIView):
    queryset = Tag.objects.all()

    def get(self, request, slug):
        hash = slug.split('-')[-1]
        tag = Tag.objects.hash(hash)
        data = PostTagSerializer(tag.get_other_tags(), context={
                                 'request': request}, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class AllTags(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = PostTagSerializer
    pagination_class = TagsArchivePagination

class PostArchive(generics.ListAPIView):
    queryset = Post.objects.filter(status=Post.STATUS_PUBLISHED)
    serializer_class = PostCardSerializer
    pagination_class = PostsArchivePagination

    def get(self, request):
        posts = None
        if request.GET.get('tag'):
            hash_tag = request.GET.get('tag').split('-')[-1]
            tag = Tag.objects.hash(hash_tag)
            posts = tag.posts_main_tag.all() | tag.posts_tags.all()
        elif request.GET.get('username'):
            username = request.GET.get('username')
            if username.startswith('@'):
                username=username[1:]
            posts = Post.objects.filter(author__username = username)
        elif request.GET.get('search'):
            key = request.GET.get('search')
            if key and len(key)>=3:
                posts = posts.filter(Q(title__contains = key) | Q(description__contains = key))
            else:
                posts = Post.objects.all()
        if posts:
            posts.filter(status=Post.STATUS_PUBLISHED)
        if posts == None:
            return Response({
                    'links': {
                        'next': None,
                        'previous': None
                    },
                    'count': 0,
                    'max_page': 1,
                    'posts': [],
                }, status=status.HTTP_200_OK)
        
        if request.GET.get('sort'):
            posts = Post.sort(posts, request.GET.get('sort'))

        posts_paginate = self.paginate_queryset(posts)
        if posts_paginate and posts != None:
            return self.get_paginated_response(
                PostCardSerializer(posts_paginate, many=True, context={'request': request}).data)

        else:
            return Response({
                    'links': {
                        'next': None,
                        'previous': None
                    },
                    'count': 0,
                    'max_page': 1,
                    'posts': [],
                }, status=status.HTTP_200_OK)
