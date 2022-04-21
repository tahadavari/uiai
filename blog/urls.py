from django.urls import path

from blog.api import PostViewAPI, BookmarkApi, LikeApi, CommentApi, ChildCommentApi, ReportApi, TagsListApi, AddPostApi, \
    PostsListProfileApi, UpdatePostApi, DeletePostApi, MorePostFromAuthor, RelatedPost, TagView,OtherTags,PostArchive,CommentViewApi,AllTags

urlpatterns = [
    # Post
    path('post/view/<str:slug>', PostViewAPI.as_view()),
    path('post/add', AddPostApi.as_view()),
    path('post/list/profile', PostsListProfileApi.as_view()),
    path('post/update/<str:hash>', UpdatePostApi.as_view()),
    path('post/update', UpdatePostApi.as_view()),
    path('post/delete', DeletePostApi.as_view()),
    # Comment
    path('comment/child/<str:hash>', ChildCommentApi.as_view()),
    path('comment/add', CommentApi.as_view()),
    path('comment/post/<str:hash>',CommentViewApi.as_view()),
    # Like
    path('like/<str:type>', LikeApi.as_view()),

    # Bookmark
    path('bookmark/post', BookmarkApi.as_view()),

    # Report
    path('report/<str:type>', ReportApi.as_view()),

    # Tags
    path('post/add/tags-list', TagsListApi.as_view()),

    #
    path('post/more-post-from-author/<str:hash>', MorePostFromAuthor.as_view()),
    path('post/related-post/<str:hash>', RelatedPost.as_view()),

    #
    path('post/archive', PostArchive.as_view()),
    #
    path('tag/view/<str:slug>', TagView.as_view()),
    path('tag/other-tag/<str:slug>', OtherTags.as_view()),
    path('tag/all', AllTags.as_view()),
]
