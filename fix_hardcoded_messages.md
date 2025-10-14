# Hardcoded Messages to Fix

## authentication/views.py
1. Line 162: `'Welcome back, {username}!'` ✅ FIXED
2. Line 176: `'You have been logged out successfully.'`
3. Line 190: `'Your email has already been verified. You can log in.'`
4. Line 209: `'Verification failed. Please try again or contact support.'`
5. Line 213: `'Invalid verification link.'`
6. Line 230: `'Your email is already verified. You can log in.'`
7. Line 382: `'This password reset link has expired.'`
8. Line 390: `'Passwords do not match.'`
9. Line 401: `'Your password has been reset successfully! You can now log in.'`
10. Line 405: `'Invalid password reset link.'`

## candidates/views.py
11. Line 608: `'You already have a candidate profile.'`
12. Line 644: `'Your candidate profile has been submitted for review! You will be notified once approved.'`
13. Line 648: `f'Registration failed: {str(e)}. Please try again.'`
14. Line 669: `'You need to create a candidate profile first.'`
15. Line 707: `'Your profile must be approved before you can edit it.'`
16. Line 728: `'Your profile has been updated successfully!'`
17. Line 731: `f'Profile update failed: {str(e)}. Please try again.'`
18. Line 777: `'Your profile must be approved before you can add events.'`
19. Line 788: `'Event created successfully!'`
20. Line 791: `f'Event creation failed: {str(e)}. Please try again.'`

## candidates/admin.py
21-24. Lines 138-156: Email notification messages (admin only, lower priority)

## Strategy
- Wrap each message with `_()` function
- For f-strings with variables, use `%` formatting: `_('text %(var)s') % {'var': value}`
- For error messages with exceptions, use: `_('Message: %(error)s') % {'error': str(e)}`
