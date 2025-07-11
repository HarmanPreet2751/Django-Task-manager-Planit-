from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    task = models.TextField()
    date = models.DateField()
    priority = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    username=models.CharField(max_length=200)
    def _str_(self):
        return self.title

    class Meta:
        ordering = ['-priority', 'date']
        


# models.py
from django.contrib.auth.models import User

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='user_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        ordering = ['-uploaded_at']