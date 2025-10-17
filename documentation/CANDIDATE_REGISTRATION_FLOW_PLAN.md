# Candidate Registration & Management Flow - Implementation Plan

## Executive Summary
This plan outlines the complete implementation of a candidate registration and self-service management system for ElectNepal. The system will allow independent candidates to register, create profiles following the mandatory template, undergo admin verification, and manage their content post-approval.

## Current State Analysis

### ✅ What Already Exists
1. **Database Models**: Complete Candidate, CandidatePost, CandidateEvent models with bilingual support
2. **Forms**: CandidateRegistrationForm, CandidateUpdateForm (with minor field mismatch)
3. **Templates**: Professional candidate profile display following CANDIDATE_PROFILE_TEMPLATE.md
4. **Admin System**: Fully functional admin interface for verification
5. **Bilingual System**: 100% operational with auto-translation

### ❌ What's Missing
1. **Authentication System**: No public login/logout/registration
2. **Registration Flow**: Forms exist but no views/templates
3. **Candidate Dashboard**: No self-service portal
4. **Verification Workflow**: Admin can verify but no pending status implementation

## Detailed Implementation Plan

## PHASE 1: Fix Existing Issues (Day 1 - 2 hours)

### 1.1 Fix Model-Form Field Mismatch
**File**: `candidates/forms.py`
```python
# Change line in CandidateRegistrationForm
# FROM: 'date_of_birth'
# TO: 'age'
```
           <a href="{% url 'signup' %}">New candidate? Register here</a>
        </form>
    </div>
</div>
{% endblock %}
```

### 2.4 Add Authentication URLs
**File**: `authentication/urls.py`
```python
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('signup/', CandidateSignupView.as_view(), name='signup'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
]
```

**File**: `nepal_election_app/urls.py`
```python
# Add to main URL patterns
path('accounts/', include('authentication.urls')),
```

### 2.5 Update Navigation Bar
**File**: `templates/base.html`
```html
<!-- Add to navigation -->
{% if user.is_authenticated %}
    {% if user.candidate %}
        <a href="{% url 'candidate_dashboard' %}">Dashboard</a>
    {% else %}
        <a href="{% url 'candidate_register' %}">Create Profile</a>
    {% endif %}
    <a href="{% url 'logout' %}">Logout</a>
{% else %}
    <a href="{% url 'login' %}">Candidate Login</a>
    <a href="{% url 'signup' %}" class="btn-primary">Register as Candidate</a>
{% endif %}
```

## PHASE 3: Candidate Registration Flow (Day 2 - 6 hours)

### 3.1 Create Registration View
**File**: `candidates/views.py`
```python
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def candidate_register(request):
    # Check if user already has a candidate profile
    if hasattr(request.user, 'candidate'):
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.user = request.user
            candidate.status = 'pending'  # Automatically set to pending
            candidate.save()
            messages.success(request, 'Profile submitted for review!')
            return redirect('registration_success')
    else:
        form = CandidateRegistrationForm()

    return render(request, 'candidates/register.html', {'form': form})
```

### 3.2 Create Registration Template
**File**: `candidates/templates/candidates/register.html`
```html
{% extends 'base.html' %}
{% load i18n %}

{% block content %}
<div class="max-w-4xl mx-auto mt-8 px-4">
    <h1 class="text-3xl font-bold mb-6">Create Candidate Profile</h1>

    <!-- Progress Indicator -->
    <div class="mb-8">
        <div class="flex justify-between items-center">
            <span class="active">1. Basic Info</span>
            <span>2. Location</span>
            <span>3. Content</span>
            <span>4. Review</span>
        </div>
    </div>

    <form method="post" enctype="multipart/form-data" x-data="registrationForm()">
        {% csrf_token %}

        <!-- Step 1: Basic Information -->
        <div x-show="step === 1">
            <h2>Basic Information</h2>
            {{ form.full_name }}
            {{ form.age }}
            {{ form.phone_number }}
            {{ form.photo }}
        </div>

        <!-- Step 2: Location Selection -->
        <div x-show="step === 2">
            <h2>Position & Location</h2>
            {{ form.position_level }}
            <!-- Dynamic dropdowns for Province/District/Municipality/Ward -->
        </div>

        <!-- Step 3: Profile Content -->
        <div x-show="step === 3">
            <h2>Profile Content (English)</h2>
            <p class="text-sm text-gray-600">Content will be auto-translated to Nepali</p>
            {{ form.bio_en }}
            {{ form.education_en }}
            {{ form.experience_en }}
            {{ form.manifesto_en }}
        </div>

        <!-- Step 4: Review & Submit -->
        <div x-show="step === 4">
            <h2>Review Your Profile</h2>
            <!-- Preview of all entered data -->
            <button type="submit">Submit for Review</button>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex justify-between mt-6">
            <button @click="previousStep()" x-show="step > 1">Previous</button>
            <button @click="nextStep()" x-show="step < 4">Next</button>
        </div>
    </form>
</div>

<script>
function registrationForm() {
    return {
        step: 1,
        nextStep() {
            if (this.validateStep()) {
                this.step++;
            }
        },
        previousStep() {
            this.step--;
        },
        validateStep() {
            // Add validation logic for each step
            return true;
        }
    }
}
</script>
{% endblock %}
```

### 3.3 Create Success Page
**File**: `candidates/templates/candidates/registration_success.html`
```html
{% extends 'base.html' %}

{% block content %}
<div class="text-center mt-16">
    <i class="fas fa-check-circle text-6xl text-green-500"></i>
    <h1 class="text-3xl font-bold mt-4">Profile Submitted Successfully!</h1>
    <p class="mt-4 text-gray-600">
        Your profile has been submitted for review. You will be notified once approved.
    </p>
    <p class="mt-2 text-sm text-gray-500">
        Review typically takes 24-48 hours.
    </p>
    <a href="{% url 'home' %}" class="btn-primary mt-6">Return to Homepage</a>
</div>
{% endblock %}
```

## PHASE 4: Candidate Dashboard (Day 3 - 8 hours)

### 4.1 Create Dashboard View
**File**: `candidates/views.py`
```python
class CandidateDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'candidates/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate = self.request.user.candidate

        context['candidate'] = candidate
        context['posts'] = candidate.posts.all()
        context['events'] = candidate.events.all()
        context['can_edit'] = candidate.status == 'approved'

        return context

@login_required
def edit_profile(request):
    candidate = request.user.candidate

    # Only approved candidates can edit
    if candidate.status != 'approved':
        messages.error(request, 'Profile must be approved before editing')
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        form = CandidateUpdateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('candidate_dashboard')
    else:
        form = CandidateUpdateForm(instance=candidate)

    return render(request, 'candidates/edit_profile.html', {'form': form})

@login_required
def add_post(request):
    candidate = request.user.candidate

    if candidate.status != 'approved':
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        form = CandidatePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.candidate = candidate
            post.save()
            return redirect('candidate_dashboard')
    else:
        form = CandidatePostForm()

    return render(request, 'candidates/add_post.html', {'form': form})

@login_required
def add_event(request):
    # Similar to add_post
    pass
```

### 4.2 Create Dashboard Template
**File**: `candidates/templates/candidates/dashboard.html`
```html
{% extends 'base.html' %}
{% load i18n %}

{% block content %}
<div class="max-w-6xl mx-auto mt-8 px-4">
    <h1 class="text-3xl font-bold mb-6">Candidate Dashboard</h1>

    <!-- Status Banner -->
    {% if candidate.status == 'pending' %}
    <div class="bg-yellow-100 border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-6">
        <i class="fas fa-clock"></i> Your profile is pending review
    </div>
    {% elif candidate.status == 'rejected' %}
    <div class="bg-red-100 border-red-400 text-red-700 px-4 py-3 rounded mb-6">
        <i class="fas fa-times"></i> Your profile was not approved
        {% if candidate.admin_notes %}
        <p class="mt-2 text-sm">Reason: {{ candidate.admin_notes }}</p>
        {% endif %}
    </div>
    {% elif candidate.status == 'approved' %}
    <div class="bg-green-100 border-green-400 text-green-700 px-4 py-3 rounded mb-6">
        <i class="fas fa-check"></i> Your profile is live!
        <a href="{% url 'candidate_detail' candidate.id %}" class="ml-2 underline">View Public Profile</a>
    </div>
    {% endif %}

    <!-- Dashboard Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <!-- Profile Section -->
        <div class="card-gradient p-6 rounded-lg">
            <h2 class="text-xl font-bold mb-4">Profile Information</h2>
            <div class="space-y-2">
                <p><strong>Name:</strong> {{ candidate.full_name }}</p>
                <p><strong>Position:</strong> {{ candidate.get_position_level_display }}</p>
                <p><strong>Location:</strong> {{ candidate.get_location_display }}</p>
                <p><strong>Status:</strong> {{ candidate.get_status_display }}</p>
            </div>
            {% if can_edit %}
            <a href="{% url 'candidate_edit' %}" class="btn-primary mt-4">Edit Profile</a>
            {% endif %}
        </div>

        <!-- Posts Section -->
        <div class="card-gradient p-6 rounded-lg">
            <h2 class="text-xl font-bold mb-4">Campaign Posts</h2>
            <p class="text-gray-600 mb-4">{{ posts.count }} posts</p>
            {% if can_edit %}
            <a href="{% url 'candidate_add_post' %}" class="btn-primary">Add New Post</a>
            {% endif %}

            <!-- Recent Posts List -->
            <div class="mt-4 space-y-2">
                {% for post in posts|slice:":3" %}
                <div class="border-b pb-2">
                    <p class="font-semibold">{{ post.title_en|truncatechars:30 }}</p>
                    <p class="text-sm text-gray-600">{{ post.created_at|date:"M d, Y" }}</p>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Events Section -->
        <div class="card-gradient p-6 rounded-lg">
            <h2 class="text-xl font-bold mb-4">Campaign Events</h2>
            <p class="text-gray-600 mb-4">{{ events.count }} events</p>
            {% if can_edit %}
            <a href="{% url 'candidate_add_event' %}" class="btn-primary">Add New Event</a>
            {% endif %}

            <!-- Upcoming Events -->
            <div class="mt-4 space-y-2">
                {% for event in events|slice:":3" %}
                <div class="border-b pb-2">
                    <p class="font-semibold">{{ event.title_en|truncatechars:30 }}</p>
                    <p class="text-sm text-gray-600">{{ event.event_date|date:"M d, Y" }}</p>
                </div>
                {% endfor %}
            </div>
        </div>

    </div>

    <!-- Quick Actions -->
    {% if can_edit %}
    <div class="mt-8 p-6 bg-white rounded-lg shadow">
        <h2 class="text-xl font-bold mb-4">Quick Actions</h2>
        <div class="flex gap-4">
            <a href="{% url 'candidate_edit' %}" class="btn-secondary">
                <i class="fas fa-edit"></i> Edit Profile
            </a>
            <a href="{% url 'candidate_add_post' %}" class="btn-secondary">
                <i class="fas fa-plus"></i> Add Post
            </a>
            <a href="{% url 'candidate_add_event' %}" class="btn-secondary">
                <i class="fas fa-calendar"></i> Add Event
            </a>
            <a href="{{ candidate.donation_link }}" class="btn-secondary" {% if not candidate.donation_link %}disabled{% endif %}>
                <i class="fas fa-dollar-sign"></i> Manage Donations
            </a>
        </div>
    </div>
    {% endif %}

</div>
{% endblock %}
```

### 4.3 Add Dashboard URLs
**File**: `candidates/urls.py`
```python
urlpatterns += [
    path('register/', candidate_register, name='candidate_register'),
    path('dashboard/', CandidateDashboardView.as_view(), name='candidate_dashboard'),
    path('edit/', edit_profile, name='candidate_edit'),
    path('posts/add/', add_post, name='candidate_add_post'),
    path('events/add/', add_event, name='candidate_add_event'),
    path('registration-success/', TemplateView.as_view(
        template_name='candidates/registration_success.html'
    ), name='registration_success'),
]
```

## PHASE 5: Admin Verification Workflow (Day 4 - 3 hours)

### 5.1 Update Admin Interface
**File**: `candidates/admin.py`
```python
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position_level', 'status', 'created_at']
    list_filter = ['status', 'position_level', 'province']
    search_fields = ['full_name', 'user__email']

    actions = ['approve_candidates', 'reject_candidates']

    def approve_candidates(self, request, queryset):
        count = queryset.filter(status='pending').update(
            status='approved',
            approved_at=timezone.now(),
            approved_by=request.user
        )
        self.message_user(request, f'{count} candidates approved.')

    def reject_candidates(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} candidates rejected.')

    fieldsets = (
        ('Status', {
            'fields': ('status', 'admin_notes', 'approved_at', 'approved_by'),
            'classes': ('wide',)
        }),
        # ... rest of fieldsets
    )
```

### 5.2 Create Email Notifications
**File**: `candidates/signals.py`
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

@receiver(post_save, sender=Candidate)
def notify_candidate_status(sender, instance, **kwargs):
    if instance.status == 'approved':
        send_mail(
            'Profile Approved!',
            'Your candidate profile has been approved and is now live.',
            'noreply@electnepal.com',
            [instance.user.email],
        )
    elif instance.status == 'rejected':
        send_mail(
            'Profile Review',
            f'Your profile needs revision: {instance.admin_notes}',
            'noreply@electnepal.com',
            [instance.user.email],
        )
```

## PHASE 6: Security & Permissions (Day 4 - 2 hours)

### 6.1 Add Middleware Protection
**File**: `candidates/middleware.py`
```python
class CandidateStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'candidate'):
            request.candidate_status = request.user.candidate.status
        else:
            request.candidate_status = None

        response = self.get_response(request)
        return response
```

### 6.2 Update View Permissions
```python
# Only show approved candidates in public views
class CandidateListView(ListView):
    queryset = Candidate.objects.filter(status='approved')

# Require login for all dashboard operations
@method_decorator(login_required, name='dispatch')
class CandidateDashboardView(TemplateView):
    # ... existing code
```

## PHASE 7: Testing & Refinement (Day 5 - 4 hours)

### 7.1 Create Test Cases
**File**: `candidates/tests.py`
```python
class CandidateRegistrationTestCase(TestCase):
    def test_registration_flow(self):
        # Test user signup
        # Test candidate profile creation
        # Test pending status assignment
        # Test admin approval
        # Test dashboard access
        pass

class CandidateDashboardTestCase(TestCase):
    def test_pending_candidate_cannot_edit(self):
        # Test edit restrictions
        pass

    def test_approved_candidate_can_edit(self):
        # Test full functionality
        pass
```

### 7.2 User Acceptance Testing Checklist
- [ ] User can sign up
- [ ] User can create candidate profile
- [ ] Profile shows as pending
- [ ] Admin can approve/reject
- [ ] Approved candidate can access dashboard
- [ ] Approved candidate can add posts/events
- [ ] Public only sees approved candidates
- [ ] Bilingual content works correctly

## Implementation Timeline

### Day 1 (6 hours)
- **Morning (2h)**: Fix field mismatches, add status field
- **Afternoon (4h)**: Implement authentication system

### Day 2 (6 hours)
- **Full Day**: Complete registration flow and templates

### Day 3 (8 hours)
- **Full Day**: Build candidate dashboard and management features

### Day 4 (5 hours)
- **Morning (3h)**: Admin verification workflow
- **Afternoon (2h)**: Security and permissions

### Day 5 (4 hours)
- **Morning (4h)**: Testing and refinement

**Total Time: 29 hours (approximately 4-5 days)**

## Database Migrations Required

```bash
# After adding status field
python manage.py makemigrations candidates
python manage.py migrate

# Update existing candidates to approved status
python manage.py shell
>>> from candidates.models import Candidate
>>> Candidate.objects.all().update(status='approved')
```

## Environment Variables to Add

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@electnepal.com
```

## Success Metrics

1. **Registration Completion Rate**: >80% of started registrations completed
2. **Approval Time**: <48 hours average
3. **Dashboard Usage**: >60% of approved candidates use dashboard weekly
4. **Content Creation**: Average 2+ posts per candidate per month

## Risk Mitigation

1. **Spam Registration**: Add CAPTCHA to registration form
2. **Inappropriate Content**: Admin review before publishing
3. **Performance**: Add pagination to dashboard lists
4. **Security**: Regular security audits, rate limiting

## Post-Implementation Enhancements

1. **Email Verification**: Verify email before profile creation
2. **Two-Factor Authentication**: For candidate accounts
3. **Analytics Dashboard**: View counts, engagement metrics
4. **Bulk Operations**: Admin bulk approval/rejection
5. **Revision System**: Allow candidates to revise rejected profiles
6. **Activity Log**: Track all profile changes

## Conclusion

This implementation plan provides a complete, production-ready candidate registration and management system. The phased approach ensures each component is properly built and tested before moving to the next phase. The system follows Django best practices, maintains the existing bilingual functionality, and provides a professional user experience for both candidates and administrators.

Key Features:
- ✅ Complete authentication system
- ✅ Multi-step registration with validation
- ✅ Admin verification workflow
- ✅ Self-service dashboard for approved candidates
- ✅ Secure permission system
- ✅ Email notifications
- ✅ Bilingual support maintained throughout

The implementation can be completed in approximately 5 working days with a single developer.