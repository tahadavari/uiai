from django.db import models
from django.db.models import Q
# Create your models here.
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from account.models import User
from core.models import BaseModel

from itertools import chain
from django.utils import timezone

from core.utils import convert_days_to_duration, convert_duration_to_persian


class Tag(BaseModel):
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, verbose_name=_(
        'Slug'), allow_unicode=True, default=None, blank=True)
    image = models.ImageField(
        upload_to='tag/images', verbose_name=_('image'), null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        self.slug = self.slug + '-' + self.hash
        super(Tag, self).save()

    def __str__(self):
        return self.name

    def href(self):
        return f"/tag/{self.slug}"

    def get_top_author(self):
        return ''

    def get_other_tags(self):
        return Tag.objects.all().exclude(id=self.id)

    def get_posts(self, sort):

        main = self.posts_main_tag.filter(status=Post.STATUS_PUBLISHED)
        if not main:
            main = []
        tags = self.posts_tags.filter(status=Post.STATUS_PUBLISHED)
        if not tags:
            tags = []
        posts = []
        if not sort or sort == 'mostRecent':
            posts = sorted(list(chain(main, tags)),
                           key=lambda obj: obj.created_at)
        elif sort == 'mostView':
            posts = sorted(list(chain(main, tags)),
                           key=lambda obj: obj.view_count)
        elif sort == 'mostLike':
            posts = sorted(list(chain(main, tags)),
                           key=lambda obj: obj.like_count)
        return posts

    def image_url(self):
        return f"https://api.ui-ai.ir{self.image.url}"

    @staticmethod
    def get_trend_tag():
        return Tag.objects.all()[:5]


class Post(BaseModel):
    STATUS_PUBLISHED = 1
    STATUS_AWAITING_APPROVAL = 2
    STATUS_DELETE_BY_AUTHOR = 3
    STATUS_DISAPPROVAL = 4
    STATUS_HIDDEN = 5
    STATUS_REPORT = 6
    STATUS_REVIEW = 7

    POST_STATUS = [
        (STATUS_PUBLISHED, _('PUBLISHED')),
        (STATUS_AWAITING_APPROVAL, _('AWAITING APPROVAL')),
        (STATUS_DELETE_BY_AUTHOR, _('DELETE BY AUTHOR')),
        (STATUS_DISAPPROVAL, _('DISAPPROVAL')),
        (STATUS_HIDDEN, _('HIDDEN')),
        (STATUS_REPORT, _('REPORT')),
        (STATUS_REVIEW, _('REVIEW')),
    ]

    POST_TYPE_TEXT = 1
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_('Author'), related_name='posts')
    status = models.IntegerField(choices=POST_STATUS, verbose_name=_('Status'))
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.CharField(
        max_length=500, verbose_name=_('Description'))
    body = models.CharField(verbose_name=_('Body'), max_length=50000)
    like_count = models.PositiveIntegerField(
        verbose_name=_('Like count'), default=0)
    bookmark_count = models.PositiveIntegerField(
        verbose_name=_('Bookmark count'), default=0)
    comment_count = models.PositiveIntegerField(
        verbose_name=_('Comment count'), default=0)
    view_count = models.PositiveIntegerField(
        verbose_name=_('View count'), default=0)
    reading_time = models.PositiveIntegerField(verbose_name=_('Reading time'))
    published_at = models.DateTimeField(
        verbose_name=_('Published at'), null=True)
    main_tag = models.ForeignKey(Tag, on_delete=models.PROTECT, verbose_name=_('Main tag'),
                                 related_name='posts_main_tag')
    tags = models.ManyToManyField(
        Tag, verbose_name=_('Tags'), related_name='posts_tags')
    cover = models.ImageField(
        upload_to='post/cover/%Y/%m', verbose_name=_('cover'))
    slug = models.SlugField(max_length=100, verbose_name=_(
        'Slug'), allow_unicode=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        self.slug = self.slug + '-' + self.hash
        super(Post, self).save()

    def liked(self, user):
        if user.is_authenticated:
            like = Like.objects.filter(
                user=user, likeable_type=Like.TYPE_POST, likeable_id=self.id).exists()
            return True if like else False
        else:
            return False

    def bookmarked(self, user):
        if user.is_authenticated:
            bookmark = Bookmark.objects.filter(
                user=user, post_id=self.id).exists()
            return True if bookmark else False
        else:
            return False

    def tags_list(self):
        tags = []
        for tag in self.tags.all():
            tags.append(tag.name)
        return tags

    def href(self):
        return f"/post/{self.slug}"

    def cover_url(self):
        return f"https://api.ui-ai.ir{self.cover.url}"

    def get_more_from_author(self):
        most_popular = self.author.posts.order_by('like_count').filter(
            status=Post.STATUS_PUBLISHED).exclude(id=self.id)
        if not most_popular:
            return None
        else:
            most_popular = most_popular[0]
        newest = self.author.posts.order_by('-created_at').filter(
            status=Post.STATUS_PUBLISHED).exclude(id__in=[self.id, most_popular.id])

        if len(newest) > 3:
            newest = newest[0:3]

        return list(chain(newest, [most_popular]))

    def get_realted_post(self):
        related_post = Post.objects.filter(main_tag=self.main_tag).order_by(
            '-created_at').exclude(id=self.id)

        if related_post and len(related_post) > 3:
            related_post = related_post[0:4]
        return related_post

    def get_string_published_at(self):
        if self.published_at:
            now = timezone.now()
            difference = now-self.published_at
            return convert_duration_to_persian(convert_days_to_duration(difference))
        else:
            return "منتشر نشده"


    @staticmethod
    def filter(filters):
        posts = Post.objects.all()
        if filters.get('tag'):
            hash_tag = filters.get('tag').split('-')[-1]
            tag = Tag.objects.hash(hash_tag)
            main = tag.posts_main_tag.all()
            if not main:
                main = []
            tags = tag.posts_tags.all()
            if not tags:
                tags = []
            posts = list(chain(main, tags))
        if not posts:
            return None
        if filters.get('author'):
            username = filters.get('author')
            if username.startswith('@'):
                username=username[1:]
            posts = posts.filter(author__username = username)
        if not posts:
            return None
        if filters.get('search'):
            key = filters.get('search')
            posts = posts.filter(Q(title__contains = key) | Q(description__contains = key))
        if not posts:
            return None
        return posts

    @staticmethod
    def sort(posts,key):
        if not key or key == 'mostRecent':
            posts = posts.order_by('-published_at')
        elif key == 'mostView':
            posts = posts.order_by('-view_count')
        elif key == 'mostLike':
            posts = posts = posts.order_by('-like_count')
        return posts


class Like(BaseModel):
    TYPE_POST = 1
    TYPE_COMMENT = 2
    LIKE_TYPE = [
        (TYPE_POST, _('POST')),
        (TYPE_COMMENT, _('COMMENT'))
    ]
    likeable_id = models.IntegerField(verbose_name=_('Likeable ID'))
    likeable_type = models.IntegerField(
        choices=LIKE_TYPE, verbose_name=_('Likeable type'))
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_('User'), related_name='likes')

    @classmethod
    def get_type_by_name(cls, type):
        if type == 'post':
            return cls.TYPE_POST
        elif type == 'comment':
            return cls.TYPE_COMMENT

    @staticmethod
    def check_like_available(likeable_id, likeable_type, user):
        like = Like.objects.filter(
            likeable_id=likeable_id, likeable_type=likeable_type, user=user)
        return like.first() if like else False

    def get_like_count(self):
        return Like.objects.filter(likeable_type=self.likeable_type, likeable_id=self.likeable_id).count()


class Comment(BaseModel):
    STATUS_PUBLISHED = 1
    STATUS_AWAITING_APPROVAL = 2
    STATUS_DELETE_BY_AUTHOR = 3
    STATUS_DISAPPROVAL = 4
    STATUS_HIDDEN = 5
    STATUS_REPORT = 6
    STATUS_REVIEW = 7

    COMMENT_STATUS = [
        (STATUS_PUBLISHED, _('PUBLISHED')),
        (STATUS_AWAITING_APPROVAL, _('AWAITING APPROVAL')),
        (STATUS_DELETE_BY_AUTHOR, _('DELETE BY AUTHOR')),
        (STATUS_DISAPPROVAL, _('DISAPPROVAL')),
        (STATUS_HIDDEN, _('HIDDEN')),
        (STATUS_REPORT, _('REPORT')),
        (STATUS_REVIEW, _('REVIEW')),
    ]
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_(
        'User'), related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.PROTECT, verbose_name=_(
        'Post'), related_name='comments')
    parent = models.ForeignKey('Comment', on_delete=models.PROTECT, null=True,
                               default=None, verbose_name='childes', related_name='childes')
    body = models.CharField(max_length=2000, verbose_name=_('Body'))
    like_count = models.IntegerField(default=0, verbose_name=_('Like count'))
    comment_count = models.IntegerField(
        default=0, verbose_name=_('Comment count'))
    published_at = models.DateTimeField(verbose_name=_('Published at'))
    status = models.IntegerField(
        choices=COMMENT_STATUS, verbose_name=_('Status'))

    def liked(self, user):
        if user.is_authenticated:
            like = Like.objects.filter(
                user=user, likeable_type=Like.TYPE_COMMENT, likeable_id=self.id).exists()
            return True if like else False
        else:
            return False

    def get_level(self):
        if not self.parent:
            return 1
        else:
            return self.parent.get_level() + 1

    def get_string_published_at(self):
        if self.published_at:
            now = timezone.now()
            difference = now-self.published_at
            return convert_duration_to_persian(convert_days_to_duration(difference))
        else:
            return "منتشر نشده"


class Report(BaseModel):
    OBJECT_TYPE_POST = 1
    OBJECT_TYPE_COMMENT = 2
    REPOST_OBJECT_TYPE = [
        (OBJECT_TYPE_POST, _('POST')),
        (OBJECT_TYPE_COMMENT, _('COMMENT'))
    ]

    TYPE_SPAM = 1
    TYPE_VIOLATION = 2
    TYPE_INAPPROPRIATE = 3
    TYPE_OTHER = 4
    REPOST_TYPE = [
        (TYPE_SPAM, _('POST')),
        (TYPE_VIOLATION, _('COMMENT')),
        (TYPE_INAPPROPRIATE, _('INAPPROPRIATE')),
        (TYPE_OTHER, _('OTHER'))
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_(
        'User'), related_name='reports')
    report_object_type = models.IntegerField(
        choices=REPOST_OBJECT_TYPE, verbose_name=_('Object type'))
    report_type = models.IntegerField(
        choices=REPOST_TYPE, verbose_name=_('Report type'))
    body = models.CharField(max_length=1000, verbose_name=_('Body'))

    report_object_id = models.IntegerField(default=0)


class Bookmark(BaseModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_(
        'User'), related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.PROTECT, verbose_name=_(
        'Post'), related_name='bookmarks')

    @staticmethod
    def check_bookmark_available(post, user):
        bookmark = Bookmark.objects.filter(post=post, user=user)
        return bookmark.filter() if bookmark else False
