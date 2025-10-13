# apps/notifications/middleware.py
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
import jwt
from django.conf import settings

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware para autenticar WebSockets con JWT
    """
    
    async def __call__(self, scope, receive, send):
        # Obtener token de la query string
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]
        
        print(f"🔐 JWT Auth Middleware - Token present: {token is not None}")
        
        # Autenticar usuario
        scope['user'] = await self.get_user_from_token(token)
        
        print(f"👤 Authenticated user: {scope['user']}")
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Validar JWT token y retornar usuario
        """
        if not token:
            print("❌ No token provided")
            return AnonymousUser()
        
        try:
            # Decodificar el token JWT
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            user_id = payload.get('user_id')
            
            if not user_id:
                print("❌ No user_id in token")
                return AnonymousUser()
            
            # Obtener usuario
            user = User.objects.get(id=user_id)
            print(f"✅ User found: {user.username}")
            return user
            
        except jwt.ExpiredSignatureError:
            print("❌ Token expired")
            return AnonymousUser()
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid token: {str(e)}")
            return AnonymousUser()
        except User.DoesNotExist:
            print("❌ User not found")
            return AnonymousUser()
        except Exception as e:
            print(f"❌ Auth error: {str(e)}")
            return AnonymousUser()