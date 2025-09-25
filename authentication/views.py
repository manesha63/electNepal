from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django import forms
from django.contrib.auth.models import User


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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
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

    def form_valid(self, form):
        # Save the user
        user = form.save()
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