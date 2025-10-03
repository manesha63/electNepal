from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class CandidateSignupForm(UserCreationForm):
    """Custom signup form with email field"""
    email = forms.EmailField(
        required=True,
        label=_("Email Address"),
        help_text=_("Required. Enter a valid email address."),
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 min-h-[44px] border rounded-lg focus:outline-none focus:border-blue-400',
            'placeholder': _('Email address')
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 min-h-[44px] border rounded-lg focus:outline-none focus:border-blue-400',
                'placeholder': _('Username')
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 min-h-[44px] border rounded-lg focus:outline-none focus:border-blue-400',
            'placeholder': _('Password')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 min-h-[44px] border rounded-lg focus:outline-none focus:border-blue-400',
            'placeholder': _('Confirm Password')
        })

        # Make all fields translatable
        self.fields['username'].label = _("Username")
        self.fields['username'].help_text = _("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.")
        self.fields['password1'].label = _("Password")
        self.fields['password1'].help_text = _("Your password must contain at least 8 characters.")
        self.fields['password2'].label = _("Confirm Password")
        self.fields['password2'].help_text = _("Enter the same password as before, for verification.")

    def clean_email(self):
        """Validate email is not already in use"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("This email address is already registered."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = True  # TODO: Implement email verification
        if commit:
            user.save()
        return user