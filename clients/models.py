from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.name} — {self.email}"


