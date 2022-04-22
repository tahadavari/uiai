from general.models import EmailNews, Message, Setting, Social, Team
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from general.serializers import SocialSerializer, TeamsSerializer
from general.landing import get_head_section_data, get_latest_posts, get_top_author,get_top_trending_tag,get_event,get_sorted_posts, get_uiai_selected


class AboutUsApi(APIView):
    def get(self, reauest):
        data = {
            'image': Setting.objects.get(key='about.image').value,
            'about_us': Setting.objects.get(key='about.about_us').value,
            'founder': Setting.objects.get(key='about.founder').value,
            'teams': [x[0] for x in TeamsSerializer(Team.objects.all(), many=True).data],
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
            "head_section":get_head_section_data(request),
            "top_trending_tags": get_top_trending_tag(request),
            "event": get_event() if get_event() else None,
            "sorted_post": get_sorted_posts(request),
            'latest_posts': get_latest_posts(request),
            'uiai_selected': get_uiai_selected(request),
            'top_author': get_top_author()
        }
        return Response(data, status=status.HTTP_200_OK)
