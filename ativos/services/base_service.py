from django.contrib.auth import get_user_model

User = get_user_model()


class BaseUserService:
    def __init__(self, user):
        self.user = user
