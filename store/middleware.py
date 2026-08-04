import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Extract the token out of the secure cookie storage layer
        token = request.COOKIES.get('access_token')
        
        if token:
            try:
                # Decode and verify token cryptographic signature
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
                user = User.objects.get(id=payload['user_id'])
                
                # Assign the authenticated user straight into the request state context
                request.user = user  
            except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
                # If token is tampered with or expired, gracefully fallback to AnonymousUser
                pass