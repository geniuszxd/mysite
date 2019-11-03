from django.urls import path
from .views import login, login_for_medal, logout, register, profile, change_alias, bind_email, send_verification_code, \
    change_password, forget_password


urlpatterns = [
    path('login/', login, name='login'),
    path('login_for_modal/', login_for_medal, name='login_for_modal'),
    path('logout/', logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('register/', register, name='register'),
    path('change_alias/', change_alias, name='change_alias'),
    path('bind_email/', bind_email, name='bind_email'),
    path('change_password/', change_password, name='change_password'),
    path('forget_password/', forget_password, name='forget_password'),
    path('send_verification_code/', send_verification_code, name='send_verification_code'),
]
