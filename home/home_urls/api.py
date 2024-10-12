from django.urls import path
from home.home_views import api

urlpatterns = [
    path('api/new/', view=api.APICreateView.as_view(), name='new_api'),
]
