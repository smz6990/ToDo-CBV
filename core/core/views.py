from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import requests
from datetime import datetime


class WeatherView(TemplateView):
    """
    getting weather from openweather api
    (it cached in urls.py)
    """
    template_name = 'weather.html'
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        url = "https://api.openweathermap.org/data/2.5/weather"
        api_key = '14c28b49f30220e538754ff09fe6b077'
        city = 'Tehran'
        params = {'q':city, 'appid':api_key,'units':'metric' }
        response = requests.get(url,params=params).json()
        context['data'] = {
            "City" : response['name'] , 
            "Temperature" : response['main']["temp"],
            'Temperature time' : datetime.fromtimestamp(response['dt']),
            'Cached at': datetime.now(),
        }
        return self.render_to_response(context)
    

class WeatherAPIView(APIView):
    """
    getting weather from openweather api
    (it cached with method decorator and cache_page decorator)
    """
    @method_decorator(cache_page(60*20))
    def get(self, request, format=None):
        url = "https://api.openweathermap.org/data/2.5/weather"
        api_key = '14c28b49f30220e538754ff09fe6b077'
        city = 'Tehran'
        params = {'q':city, 'appid':api_key,'units':'metric' }
        response = requests.get(url,params=params).json()
        data = {
            "City" : response['name'] , 
            "Temperature" : response['main']["temp"],
            'Temperature time' : datetime.fromtimestamp(response['dt']),
            'Cached at': datetime.now(),
        }
        return Response(data)