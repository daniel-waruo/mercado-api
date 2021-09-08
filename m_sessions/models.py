from django.db import models
from django.utils import timezone
from jsonfield import JSONField


class SessionState(models.Model):
    session_id = models.CharField(max_length=200, primary_key=True)
    state = models.CharField(max_length=200, null=True)
    data = JSONField(null=True)
    context = models.CharField(max_length=20, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.session_id

    def update(self, state, data, context):
        self.state = state
        self.data = data
        if context:
            self.context = context
        self.save()

    def reset(self):
        self.state = None
        self.data = None
        self.save()

    def is_expired(self, time_difference: timezone.timedelta = timezone.timedelta(minutes=2)):
        time_now = timezone.now()
        last_interaction_diff = time_now - self.updated_at
        return time_difference < last_interaction_diff
