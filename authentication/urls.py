from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    CandidateSignupView,
    RegistrationInfoView,
    EmailVerificationView,
    ResendVerificationView,
    ForgotPasswordView,
    ResetPasswordView
)

app_name = 'authentication'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register-info/', RegistrationInfoView.as_view(), name='register_info'),
    path('signup/', CandidateSignupView.as_view(), name='signup'),

    # Email verification
    path('verify-email/<uuid:token>/', EmailVerificationView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),

    # Password reset
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<uuid:token>/', ResetPasswordView.as_view(), name='reset_password'),
]