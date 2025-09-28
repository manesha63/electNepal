from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django import forms
from django.contrib.auth.models import User
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from django.conf import settings
import logging

# Get logger for authentication emails
logger = logging.getLogger('authentication.emails')


class CandidateSignupForm(UserCreationForm):
    """Custom signup form with email field"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-400',
        'placeholder': 'Email address'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-400',
                'placeholder': 'Username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-400',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-blue-400',
            'placeholder': 'Confirm Password'
        })

    def clean_email(self):
        """Validate email is not already in use"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = True  # For now, activate immediately (could require email verification)
        if commit:
            user.save()
        return user


class RegistrationInfoView(TemplateView):
    """Display registration process information before signup"""
    template_name = 'authentication/registration_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Candidate Registration Process'
        return context


class CandidateSignupView(CreateView):
    """User registration with automatic redirect to candidate registration"""
    template_name = 'authentication/signup.html'
    form_class = CandidateSignupForm
    success_url = reverse_lazy('candidates:register')

    def send_welcome_email(self, user):
        """Send welcome email to newly registered user"""
        try:
            subject = "[ElectNepal] Welcome to ElectNepal!"

            # Get domain for email links
            domain = self.request.get_host()
            protocol = 'https' if self.request.is_secure() else 'http'

            context = {
                'user': user,
                'domain': f"{protocol}://{domain}",
            }

            # Create welcome email content
            html_message = render_to_string(
                'authentication/emails/welcome.html',
                context
            )

            plain_message = f"""
            Welcome to ElectNepal, {user.username}!

            Thank you for creating an account. You can now register as a candidate and participate in Nepal's democratic process.

            Next Steps:
            1. Complete your candidate profile
            2. Submit for verification
            3. Once approved, your profile will be visible to voters

            Login: {protocol}://{domain}/auth/login/

            Best regards,
            The ElectNepal Team
            """

            logger.info(f"Sending welcome email to {user.email}")

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Welcome email sent successfully to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}", exc_info=True)
            # Don't block registration if email fails
            return False

    def form_valid(self, form):
        # Save the user
        user = form.save()

        # Send welcome email (don't block registration if it fails)
        try:
            self.send_welcome_email(user)
        except Exception as e:
            logger.error(f"Welcome email error for {user.username}: {e}")

        # Log them in automatically
        login(self.request, user)
        messages.success(self.request, 'Account created successfully! Now create your candidate profile.')
        return redirect('candidates:register')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register as Candidate'
        return context


class CustomLoginView(LoginView):
    """Login with candidate dashboard redirect if candidate exists"""
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # Check if user has a candidate profile
        if hasattr(self.request.user, 'candidate'):
            if self.request.user.candidate.status == 'approved':
                return reverse_lazy('candidates:dashboard')
            else:
                return reverse_lazy('candidates:dashboard')  # Still go to dashboard to see status
        else:
            # No candidate profile, redirect to registration
            return reverse_lazy('candidates:register')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Candidate Login'
        return context


class CustomLogoutView(LogoutView):
    """Logout with homepage redirect"""
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    """Password reset with custom template"""
    template_name = 'authentication/password_reset.html'
    email_template_name = 'authentication/password_reset_email.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.info(self.request, 'If an account exists with this email, password reset instructions will be sent.')
        return super().form_valid(form)