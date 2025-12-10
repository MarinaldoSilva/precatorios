from typing import Any
from django.contrib.auth import get_user_model

#from user.models import User

User = get_user_model()

class BaseUserService:
    def __init__(self, user):
        self.user = user