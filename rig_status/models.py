from django.db import models
from django.utils import timezone

STATUS_COLORS = {'Running': '#98FF98',
                 'Stopped': 'white',
                 'Paused': 'red'}

class Rig(models.Model):
    name = models.CharField('Rig', max_length=10)
    status = models.CharField('Status', max_length=10, blank=True, default='')
    non_responses = models.IntegerField('Number non-responses', blank=True, default=0)
    correct = models.IntegerField('Trials correct', blank=True, default=0)
    n_trials = models.IntegerField('Num Trials', blank=True, default=0)
    last_heartbeat = models.DateTimeField('Last heartbeat', blank=True, default=timezone.now())

    def time_since_last(self):
        t = timezone.now() - self.last_heartbeat
        return "{0:0.0f}".format(t.total_seconds())

    def performance(self):
        try:
            p = self.correct / self.n_trials
        except ZeroDivisionError:
            p = 0.

        return "{0:0.2f}".format(p)

    def status_color(self):

        if int(self.time_since_last()) > 200 and not self.status == 'Stopped':
            return 'red'
        elif (float(self.performance()) < .4 or self.non_responses > 25) and not self.status == 'Stopped':
            return 'yellow'
        else:
            return STATUS_COLORS[self.status]

    def reset(self):
        self.correct = 0
        self.non_responses = 0
        self.n_trials = 0
        self.status = ''
        self.save()
