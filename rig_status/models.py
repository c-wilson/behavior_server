from django.db import models
from django.utils import timezone
import django_tables2 as tables

class Rig(models.Model):
    name = models.CharField('Rig', max_length=10)
    status = models.CharField('Status', max_length=10, blank=True, default='')
    non_responses = models.IntegerField('Number non-responses', blank=True, default=0)
    correct = models.IntegerField('Trials correct', blank=True, default=0)
    n_trials = models.IntegerField('Num Trials', blank=True, default=0)
    last_heartbeat = models.DateTimeField('Last heartbeat', blank=True, default=timezone.now())

    def performance(self):
        return self.correct / self.trials

    def time_since_last(self):
        t = timezone.now() - self.last_heartbeat
        return "{0:0.0f}".format(t.total_seconds())

    def reset(self):
        self.correct = 0
        self.non_responses = 0
        self.n_trials = 0
        self.status = ''
        self.save()
