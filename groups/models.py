from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='group_memberships')
    allowed_emails = models.TextField(blank=True)  # Comma-separated list of allowed emails

    def __str__(self):
        return self.name

    def get_allowed_emails_list(self):   
        """Helper method to get a list of allowed emails."""
        return [email.strip().lower() for email in self.allowed_emails.split(',') if email.strip()]

class Task(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    priority = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['priority', '-created_at']

    def __str__(self):
        return self.title