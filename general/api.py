from general.models import EmailNews, Message, Setting, Social, Team
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from general.serializers import SocialSerializer, TeamsSerializer
from blog.serializers import PostCardSerializer, PostTagSerializer
from account.serializers import AuthorSerializer
from blog.models import Tag, Post
from account.models import User


class AboutUsApi(APIView):
    def get(self, reauest):
        data = {
            'image': "https://www.ausnewtechs.com/wp-content/uploads/2021/11/iStock-1207062970.jpg",
            'about_us': Setting.objects.get(key='about.about_us').value,
            'founder': Setting.objects.get(key='about.founder').value,
            # 'teams': TeamsSerializer(Team.objects.all(), many=True).data,
            'teams': [{
                'id': Team.objects.get(id=1).hash,
                'name': Team.objects.get(id=1).name,
                'job': Team.objects.get(id=1).description,
                'avatar': Team.objects.get(id=1).avatar_url()
            }],
            'fast_facts': {
                'text': Setting.objects.get(key='about.fast_facts.text').value,
                'facts': [
                    {
                        'id': "about.fast_facts.facts.1",
                        'title': Setting.objects.get(key='about.fast_facts.facts.1.title').value,
                        'desc': Setting.objects.get(key='about.fast_facts.facts.1.desc').value,
                    },
                    {
                        "id": 'about.fast_facts.facts.2',
                        'title': Setting.objects.get(key='about.fast_facts.facts.2.title').value,
                        'desc': Setting.objects.get(key='about.fast_facts.facts.2.desc').value,
                    },
                    {
                        "id": 'about.fast_facts.facts.3',
                        'title': Setting.objects.get(key='about.fast_facts.facts.3.title').value,
                        'desc': Setting.objects.get(key='about.fast_facts.facts.3.desc').value,
                    },
                ],
            }
        }
        return Response(data, status=status.HTTP_200_OK)


class NewsletterApi(APIView):
    def post(self, request):
        email = request.data.get('email')
        if email:
            if not EmailNews.objects.filter(email=email).exists():
                email_news = EmailNews(email=email)
                email_news.save()
            data = {
                'email': 'email',
                'success': True,
                'message': 'ایمیل شما با موفقیت ثبت شد'
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                'success': False,
                'error': 'ایمیل نامعتبر است'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class ContactUsApi(APIView):
    def get(self, reauest):
        data = {
            'address': Setting.objects.get(key='contact_us.address').value,
            'email': Setting.objects.get(key='contact_us.email').value,
            'phone': Setting.objects.get(key='contact_us.phone').value,
            'socials': SocialSerializer(Social.objects.all(), many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)


class ContactFormApi(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        message = request.data.get('message')

        if name and email and message:
            message_model = Message(name=name, email=email, message=message)
            message_model.save()
            data = {
                'name': name,
                'success': True,
                'message': f'{name} عزیز پیام شما ثبت شد'
            }
            return Response(data, status=status.HTTP_200_OK)
        data = {
            'success': False,
            'error': 'اطلاعات نامعتبر است'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class LandingApi(APIView):
    def get(self, request):
        data = {
            "head_section": [
                PostCardSerializer(Post.objects.get(id=1), context={
                                   'request': request}).data,
                PostCardSerializer(Post.objects.get(id=1), context={
                                   'request': request}).data,
                PostCardSerializer(Post.objects.get(id=1), context={
                                   'request': request}).data,
                PostCardSerializer(Post.objects.get(id=1), context={
                                   'request': request}).data,
            ],
            "top_trending_tags": PostTagSerializer(Tag.objects.all(), many=True, context={'request': request}).data,
            "event": {
                "image": "https://www.ausnewtechs.com/wp-content/uploads/2021/11/iStock-1207062970.jpg",
                "link": "https://evand.com/events/%D8%AF%D9%88%D8%B1%D9%87-%D9%87%D8%A7%DB%8C-%D8%B1%D8%A8%D8%A7%D8%AA%DB%8C%DA%A9-%D8%AF%D8%A7%D9%86%D8%B4%DA%AF%D8%A7%D9%87-%D8%B9%D9%84%D9%85-%D9%88-%D8%B5%D9%86%D8%B9%D8%AA-%D8%A7%DB%8C%D8%B1%D8%A7%D9%86-927948393?icn=frontpage&type=recom&formula=ube&ici=11",
            },
            "sorted_post": {
                "tabs": ["تب دو", "تب 1"],
                "posts": {
                    "تب 1": PostCardSerializer(Post.objects.all()[0:6], many=True, context={'request': request}).data,
                    "تب دو": PostCardSerializer(Post.objects.all()[5:11], many=True, context={'request': request}).data
                }
            },
            'latest_posts': PostCardSerializer(Post.objects.all()[0:15], many=True, context={'request': request}).data,
            'uiai_selected': {
                "tabs": ["تب چهار", "تب 3"],
                "posts": {
                    "تب چهار": PostCardSerializer(Post.objects.all()[0:4], many=True, context={'request': request}).data,
                    "تب 3": PostCardSerializer(Post.objects.all()[4:8], many=True, context={'request': request}).data
                }
            },
            'top_author': AuthorSerializer(User.objects.filter(level=User.LEVEL_WRITER)[0:5], many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)
