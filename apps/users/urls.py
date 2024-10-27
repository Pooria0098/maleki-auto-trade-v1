from django.urls import path
from apps.users import views

app_name = 'users'
urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-mode/', views.change_mode, name='change_mode'),

    path('api/list/',views.APIListView.as_view(), name='api_list'),
    path('api/create/',views.APICreateView.as_view(), name='api_create'),
    path('api/<int:pk>/update/',views.APIUpdateView.as_view(), name='api_update'),
    path('api/<int:pk>/update/active/',views.APIActiveView.as_view(), name='api_update_active'),
    path('api/<int:pk>/update/deactive/',views.APIDeActiveView.as_view(), name='api_update_deactive'),
    path('api/<int:pk>/connect/',views.APIDeActiveView.as_view(), name='api_connect'),
]
