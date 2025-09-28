from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    CandidateSignupView,
    CustomPasswordResetView,
    RegistrationInfoView
)

app_name = 'authentication'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register-info/', RegistrationInfoView.as_view(), name='register_info'),
    path('signup/', CandidateSignupView.as_view(), name='signup'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
]