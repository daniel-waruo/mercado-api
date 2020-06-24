from django.db import models
from jsonfield import JSONField


# Create your models here.
class USSDState(models.Model):
    session_id = models.CharField(max_length=200, primary_key=True)
    state = models.CharField(max_length=200, null=True)
    data = JSONField(null=True)

    def __str__(self):
        return self.session_id

    def update(self, state, data):
        self.state = state
        self.data = data
        self.save()
