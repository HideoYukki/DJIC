from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import MongoUser


class MongoJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('user_id')
            return MongoUser.objects.get(id=user_id)
        except Exception:
            return None
