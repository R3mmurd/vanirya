from django.contrib.auth.models import AbstractUser
from model_utils import Choices
from model_utils.fields import StatusField


class User(AbstractUser):
    STATUS = Choices('active', 'banned')
    status = StatusField(default='active')
