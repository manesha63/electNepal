from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView, TemplateView, View
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.http import Http404
from django.utils.translation import gettext as _
from django.utils import timezone
from core.log_utils import sanitize_email, sanitize_username, get_user_identifier
import logging
import uuid

# Import our custom form and models
from .forms import CandidateSignupForm
from .models import EmailVerification, PasswordResetToken

# Get logger for authentication emails
logger = logging.getLogger('authentication.emails')


class RegistrationInfoView(TemplateView):
    """Display registration process information before signup"""
    template_name = 'authentication/registration_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Candidate Registration Process'
        return context


@method_decorator(ratelimit(key='ip', rate='5/h', method='POST', block=True), name='dispatch')
class CandidateSignupView(CreateView):
    """User registration with automatic redirect to candidate registration"""
    template_name = 'authentication/signup.html'
    form_class = CandidateSignupForm
    success_url = reverse_lazy('candidates:register')

    def send_verification_email(self, user, verification_token):
        """Send email verification link to newly registered user"""
        try:
            subject = "[ElectNepal] Verify Your Email Address"

            # Get domain for email links
            domain = self.request.get_host()
            protocol = 'https' if self.request.is_secure() else 'http'

            verification_url = f"{protocol}://{domain}/auth/verify-email/{verification_token}/"

            context = {
                'user': user,
                'domain': f"{protocol}://{domain}",
                'verification_url': verification_url,
                'expiry_hours': 72
            }

            # Create verification email content
            html_message = render_to_string(
                'authentication/emails/email_verification.html',
                context
            )

            plain_message = f"""
            Hello {user.username}!

            Please verify your email address to activate your ElectNepal account.

            Click the link below to verify your email:
            {verification_url}

            This link will expire in 72 hours.

            If you did not create this account, please ignore this email.

            Best regards,
            The ElectNepal Team
            """

            logger.info(f"Sending verification email to {sanitize_email(user.email)}")

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Verification email sent successfully to {sanitize_email(user.email)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send verification email to {sanitize_email(user.email)}: {str(e)}", exc_info=True)
            return False

    def form_valid(self, form):
        # Save the user but keep them inactive until email is verified
        user = form.save(commit=False)
        user.is_active = False  # Require email verification first
        user.save()

        # Create email verification record
        verification = EmailVerification.objects.create(user=user)

        # Send verification email
        email_sent = self.send_verification_email(user, verification.token)

        if email_sent:
            messages.success(
                self.request,
                f'Account created! Please check your email ({user.email}) to verify your account before logging in.'
            )
        else:
            messages.warning(
                self.request,
                'Account created but we could not send the verification email. Please contact support.'
            )

        # Don't log them in automatically - require verification first
        return redirect('authentication:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register as Candidate'
        return context


class CustomLoginView(LoginView):
    """Custom login view that redirects based on user type:
    - Admin users -> Admin dashboard
    - Candidates -> Candidate dashboard
    - New users -> Candidate registration
    """
    template_name = 'authentication/login.html'
    redirect_authenticated_user = False  # Don't redirect, always show login page

    def get_success_url(self):
        # Check if there's a 'next' parameter in the request
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url

        # Check if user is admin (staff or superuser) FIRST - prioritize admin dashboard
        if self.request.user.is_staff or self.request.user.is_superuser:
            # Admin users always go to admin dashboard, even if they have a candidate profile
            return '/admin/'

        # Check if user has a candidate profile (non-admin users only)
        if hasattr(self.request.user, 'candidate'):
            return reverse_lazy('candidates:dashboard')  # Redirect to candidate dashboard

        # If user has no candidate profile yet, redirect to registration
        return reverse_lazy('candidates:register')

    def form_valid(self, form):
        # Get the user before logging in
        user = form.get_user()

        # Check if user is active (basic check)
        if not user.is_active:
            messages.error(
                self.request,
                _('Your email address is not verified. Please check your email for the verification link.')
            )
            return redirect('authentication:resend_verification')

        # Check if user needs reverification (every 7 days)
        try:
            if hasattr(user, 'email_verification'):
                verification = user.email_verification
                if verification.needs_reverification():
                    # Generate new token and send verification email
                    new_token = verification.regenerate_token()

                    # Send verification email
                    self._send_reverification_email(user, new_token)

                    messages.warning(
                        self.request,
                        _('For security, please verify your email again (required every 7 days). '
                          'A verification link has been sent to %(email)s') % {'email': user.email}
                    )
                    return redirect('authentication:login')
                else:
                    # Update last verification check timestamp
                    verification.update_verification_check()
            else:
                # User has no email verification record at all - shouldn't happen but handle it
                EmailVerification.objects.create(user=user, is_verified=True, verified_at=timezone.now())
        except Exception as e:
            logger.error(f"Error checking email verification for {get_user_identifier(user)}: {e}")
            # Don't block login on verification check errors

        # Proceed with login
        response = super().form_valid(form)
        messages.success(self.request, _('Welcome back, %(username)s!') % {'username': self.request.user.username})
        return response

    def _send_reverification_email(self, user, token):
        """Send reverification email for 7-day check"""
        try:
            domain = self.request.get_host()
            protocol = 'https' if self.request.is_secure() else 'http'
            verification_url = f"{protocol}://{domain}/auth/verify-email/{token}/"

            context = {
                'user': user,
                'domain': f"{protocol}://{domain}",
                'verification_url': verification_url,
                'is_reverification': True,
                'expiry_hours': 72
            }

            # Create reverification email content
            html_message = render_to_string(
                'authentication/emails/email_verification.html',
                context
            )

            plain_message = f"""
            Hello {user.username}!

            For security purposes, we require email verification every 7 days.

            Please click the link below to verify your email and continue:
            {verification_url}

            This link will expire in 72 hours.

            Best regards,
            The ElectNepal Team
            """

            logger.info(f"Sending reverification email to {sanitize_email(user.email)}")

            send_mail(
                subject="[ElectNepal] Email Reverification Required",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Reverification email sent successfully to {sanitize_email(user.email)}")
            return True
        except Exception as e:
            logger.error(f"Failed to send reverification email to {sanitize_email(user.email)}: {str(e)}", exc_info=True)
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Candidate Login'
        return context


class CustomLogoutView(LogoutView):
    """Logout with homepage redirect"""
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _('You have been logged out successfully.'))
        return super().dispatch(request, *args, **kwargs)


class EmailVerificationView(View):
    """Handle email verification link clicks"""

    def get(self, request, token):
        try:
            # Find the verification record
            verification = EmailVerification.objects.get(token=token)

            # Check if already verified
            if verification.is_verified:
                messages.info(request, _('Your email has already been verified. You can log in.'))
                return redirect('authentication:login')

            # Check if expired
            if verification.is_expired():
                messages.error(
                    request,
                    'This verification link has expired. Please request a new one.'
                )
                return redirect('authentication:resend_verification')

            # Verify the email
            if verification.verify():
                # Also update last verification check
                verification.update_verification_check()
                messages.success(
                    request,
                    _('Your email has been verified successfully! You can now log in.')
                )
                return redirect('authentication:login')
            else:
                messages.error(request, _('Verification failed. Please try again or contact support.'))
                return redirect('authentication:login')

        except EmailVerification.DoesNotExist:
            messages.error(request, _('Invalid verification link.'))
            return redirect('authentication:login')


class ResendVerificationView(TemplateView):
    """Resend email verification link"""
    template_name = 'authentication/resend_verification.html'

    def post(self, request):
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            # Check if already verified
            if hasattr(user, 'email_verification'):
                if user.email_verification.is_verified:
                    messages.info(request, _('Your email is already verified. You can log in.'))
                else:
                    # Regenerate token and send new email
                    new_token = user.email_verification.regenerate_token()

                    # Send new verification email
                    email_sent = self._send_verification_email(user, new_token)
                    if email_sent:
                        messages.success(
                            request,
                            f'A new verification email has been sent to {email}'
                        )
                    else:
                        messages.error(
                            request,
                            'Failed to send verification email. Please try again later or contact support.'
                        )
            else:
                # Create new verification record
                verification = EmailVerification.objects.create(user=user)
                email_sent = self._send_verification_email(user, verification.token)
                if email_sent:
                    messages.success(
                        request,
                        f'A verification email has been sent to {email}'
                    )
                else:
                    messages.error(
                        request,
                        'Failed to send verification email. Please try again later or contact support.'
                    )

        except User.DoesNotExist:
            # Don't reveal if email exists or not
            messages.info(
                request,
                'If an account exists with this email, a verification link will be sent.'
            )

        return redirect('authentication:login')

    def _send_verification_email(self, user, token):
        """Helper to send verification email"""
        try:
            domain = self.request.get_host()
            protocol = 'https' if self.request.is_secure() else 'http'
            verification_url = f"{protocol}://{domain}/auth/verify-email/{token}/"

            context = {
                'user': user,
                'verification_url': verification_url,
                'expiry_hours': 72
            }

            html_message = render_to_string(
                'authentication/emails/email_verification.html',
                context
            )

            logger.info(f"Sending resend verification email to {sanitize_email(user.email)}")

            send_mail(
                subject="[ElectNepal] Verify Your Email Address",
                message=f"Click here to verify your email: {verification_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Resend verification email sent successfully to {sanitize_email(user.email)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send resend verification email to {sanitize_email(user.email)}: {str(e)}", exc_info=True)

            # Notify admins about email failure
            try:
                mail_admins(
                    subject=f"[ALERT] Failed to send resend verification email",
                    message=f"Failed to send resend verification email to {user.username} ({user.email}). Error: {str(e)}",
                    fail_silently=True
                )
            except Exception as admin_err:
                logger.error(f"Failed to notify admin of email failure: {admin_err}")

            return False


class ForgotPasswordView(TemplateView):
    """Custom password reset request view"""
    template_name = 'authentication/forgot_password.html'

    def post(self, request):
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            # Create password reset token
            reset_token = PasswordResetToken.objects.create(user=user)

            # Send reset email
            self._send_reset_email(user, reset_token.token)

        except User.DoesNotExist:
            # Don't reveal if email exists
            pass

        messages.info(
            request,
            'If an account exists with this email, password reset instructions will be sent.'
        )
        return redirect('authentication:login')

    def _send_reset_email(self, user, token):
        """Send password reset email"""
        try:
            domain = self.request.get_host()
            protocol = 'https' if self.request.is_secure() else 'http'
            reset_url = f"{protocol}://{domain}/auth/reset-password/{token}/"

            context = {
                'user': user,
                'reset_url': reset_url,
                'expiry_hours': 24
            }

            html_message = render_to_string(
                'authentication/emails/password_reset.html',
                context
            )

            plain_message = f"""
            Hello {user.username},

            You requested a password reset for your ElectNepal account.

            Click the link below to reset your password:
            {reset_url}

            This link will expire in 24 hours.

            If you did not request this, please ignore this email.

            Best regards,
            The ElectNepal Team
            """

            logger.info(f"Sending password reset email to {sanitize_email(user.email)}")

            send_mail(
                subject="[ElectNepal] Password Reset Request",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Password reset email sent successfully to {sanitize_email(user.email)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset email to {sanitize_email(user.email)}: {str(e)}", exc_info=True)

            # Notify admins about email failure
            try:
                mail_admins(
                    subject=f"[ALERT] Failed to send password reset email",
                    message=f"Failed to send password reset email to {user.username} ({user.email}). User may be unable to reset password. Error: {str(e)}",
                    fail_silently=True
                )
            except Exception as admin_err:
                logger.error(f"Failed to notify admin of email failure: {admin_err}")

            return False


class ResetPasswordView(TemplateView):
    """Handle password reset with token"""
    template_name = 'authentication/reset_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = kwargs.get('token')

        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)

            if reset_token.is_expired():
                context['error'] = 'This password reset link has expired.'
            else:
                context['valid_token'] = True
                context['token'] = token

        except PasswordResetToken.DoesNotExist:
            context['error'] = 'Invalid or already used password reset link.'

        return context

    def post(self, request, token):
        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)

            if reset_token.is_expired():
                messages.error(request, _('This password reset link has expired.'))
                return redirect('authentication:forgot_password')

            # Get new password
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            if password != password_confirm:
                messages.error(request, _('Passwords do not match.'))
                return redirect('authentication:reset_password', token=token)

            # Update password
            user = reset_token.user
            user.set_password(password)
            user.save()

            # Mark token as used
            reset_token.mark_as_used()

            messages.success(request, _('Your password has been reset successfully! You can now log in.'))
            return redirect('authentication:login')

        except PasswordResetToken.DoesNotExist:
            messages.error(request, _('Invalid password reset link.'))
            return redirect('authentication:forgot_password')