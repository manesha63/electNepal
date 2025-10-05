"""
Utility functions for analytics
"""


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


def parse_user_agent(user_agent):
    """
    Parse user agent string to detect mobile and browser
    Simple implementation - can be enhanced with user-agents library
    """
    user_agent_lower = user_agent.lower()

    # Detect mobile
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone']
    is_mobile = any(keyword in user_agent_lower for keyword in mobile_keywords)

    # Detect browser
    browser = 'Unknown'
    if 'edg' in user_agent_lower:
        browser = 'Edge'
    elif 'chrome' in user_agent_lower:
        browser = 'Chrome'
    elif 'safari' in user_agent_lower:
        browser = 'Safari'
    elif 'firefox' in user_agent_lower:
        browser = 'Firefox'
    elif 'opera' in user_agent_lower or 'opr' in user_agent_lower:
        browser = 'Opera'
    elif 'msie' in user_agent_lower or 'trident' in user_agent_lower:
        browser = 'IE'

    return is_mobile, browser