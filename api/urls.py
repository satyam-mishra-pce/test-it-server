from django.urls import path
from api import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('token/', views.get_token, name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('contest/', views.get_contests, name='get_contests'),
    path('problem/', views.get_problems, name='get_problems'),
    path('compile/', views.compile, name='compile'),
    path('submission/',views.submission,name='submission'),
    path('run_code/',views.run_code,name='run_code'),
]
