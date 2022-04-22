from account.models import User
from account.serializers import AuthorSerializer
from blog.models import Post, Tag
from blog.serializers import PostCardSerializer, PostTagSerializer
from general.models import Setting
from datetime import datetime, timedelta


def get_head_section_main_post(request):
    post_id = Setting.objects.get(key='landing.main_section.post_id').value
    post = PostCardSerializer(Post.objects.get(
        id=int(post_id)), context={'request': request}).data
    return post


def get_head_section_posts(request):
    most_liked = PostCardSerializer(Post.objects.filter(published_at__range=[datetime.now(
    )-timedelta(days=7), datetime.now()]).order_by("-like_count")[0], context={'request': request}).data
    most_view = PostCardSerializer(Post.objects.filter(published_at__range=[datetime.now(
    )-timedelta(days=7), datetime.now()]).order_by("-view_count")[0], context={'request': request}).data
    most_saved = PostCardSerializer(Post.objects.filter(published_at__range=[datetime.now(
    )-timedelta(days=7), datetime.now()]).order_by("-bookmark_count")[0], context={'request': request}).data
    return [most_liked, most_view, most_saved]


def get_head_section_data(request):
    return get_head_section_posts(request).append(get_head_section_main_post(request))


def get_top_trending_tag(request):
    return PostTagSerializer(sorted(Tag.objects.all(), key=lambda tag: tag.posts_main_tag.count() + tag.posts_tags.count(), reverse=True), many=True, context={'request': request}).data


def get_event():
    if Setting.objects.get(key='landing.event.have').value == 1:
        image = Setting.objects.get(key='landing.event.image').value
        link = Setting.objects.get(key='landing.event.link').value
        data = {
            "image": image,
            "link": link,
        }
        return data
    return False


def get_sorted_posts(request):
    tab1 = "محبوب ترین ها"
    tab2 = "پر بازدید ترین ها"
    tab3 = "بیشترین دخیره شده"
    data = {
        "tabs": [tab1, tab2, tab3],
        "posts": {
            tab1: PostCardSerializer(Post.objects.all().order_by('-like_count')[0:6], many=True, context={'request': request}).data,
            tab2: PostCardSerializer(Post.objects.all().order_by('-view_count')[0:6], many=True, context={'request': request}).data,
            tab3: PostCardSerializer(Post.objects.all().order_by('-bookmark_count')[0:6], many=True, context={'request': request}).data}
    }
    return data


def get_latest_posts(request):
    return PostCardSerializer(Post.objects.all().order_by('-created_at')[0:15], many=True, context={
        'request': request}).data


def get_uiai_selected(request):
    tab1 = Setting.objects.get(key='landing.uiai_selected.tab1').value
    tab1_post1 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab1.post1').value)), context={
        'request': request}).data
    tab1_post2 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab1.post2').value)), context={
        'request': request}).data
    tab1_post3 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab1.post3').value)), context={
        'request': request}).data
    tab1_post4 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab1.post4').value)), context={
        'request': request}).data
    tab1_post5 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab1.post5').value)), context={
        'request': request}).data
    tab1_post6 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab1.post6').value)), context={
        'request': request}).data

    tab2 = Setting.objects.get(key='landing.uiai_selected.tab2').value
    tab2_post1 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab2.post1').value)), context={
        'request': request}).data 
    tab2_post2 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab2.post2').value)), context={
        'request': request}).data
    tab2_post3 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab2.post3').value)), context={
        'request': request}).data
    tab2_post4 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab2.post4').value)), context={
        'request': request}).data
    tab2_post5 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab2.post5').value)), context={
        'request': request}).data
    tab2_post6 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab2.post6').value)), context={
        'request': request}).data

    tab3 = Setting.objects.get(key='landing.uiai_selected.tab3').value
    tab3_post1 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab3.post1').value)), context={
        'request': request}).data
    tab3_post2 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab3.post2').value)), context={
        'request': request}).data
    tab3_post3 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab3.post3').value)), context={
        'request': request}).data
    tab3_post4 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab3.post4').value)), context={
        'request': request}).data
    tab3_post5 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab3.post5').value)), context={
        'request': request}).data
    tab3_post6 = PostCardSerializer(Post.objects.get(id=int(Setting.objects.get(key='landing.uiai_selected.tab3.post6').value)), context={
        'request': request}).data

    data = {
        "tabs": [tab1, tab2, tab3],
        "posts": {
            tab1: [tab1_post1,tab1_post2,tab1_post3,tab1_post4,tab1_post5,tab1_post6],
            tab2: [tab2_post1,tab2_post2,tab2_post3,tab2_post4,tab2_post5,tab2_post6],
            tab3: [tab3_post1,tab3_post2,tab3_post3,tab3_post4,tab3_post5,tab3_post6],
        }
    }


def get_top_author():
    return AuthorSerializer(sorted(User.objects.filter(
        level=User.LEVEL_WRITER), key=lambda x: x.posts.count())[0:5], many=True).data
