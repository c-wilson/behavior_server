import os

from django.db import models
from django.utils import timezone
from .utils import mouse_path
import tables as tb
import django_tables2 as tables
from django.db import transaction

# Create your models here.
SEX_CHOICES = (('M', 'male'),
               ('F', 'female'))




class Mouse(models.Model):
    mouse_number = models.IntegerField('Mouse Number', unique=True)
    surgery_date = models.DateField('Surgery Date', blank=True, default=timezone.now)
    dob = models.DateField('Date of birth', blank=True, default=timezone.now)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, default='')
    date_added = models.DateField('Date added to database', default=timezone.now)
    genotype = models.CharField('Genotype', default='Wild Type', blank=True, max_length=100)


    def __str__(self):
        return 'mouse {0}'.format(self.mouse_number)

    def age(self):
        return timezone.now() - self.dob

    def last_session_date(self):
        # TODO: last session date.
         if self.session_set:
             return self.session_set.latest('run_dtg').run_dtg
         else:
             return ''

    def rig(self):
        if self.session_set:
            return self.session_set.latest('run_dtg').rig
        else:
            return ''

    def last_session_performance(self):
        if self.session_set:
            return self.session_set.latest('run_dtg').performance
        else:
            return ''


class Session(models.Model):
    mouse = models.ForeignKey(Mouse)
    session_num = models.CharField('Session number', max_length=5)
    run_dtg = models.DateTimeField('Run DTG', unique=True)
    added_dtg = models.DateTimeField('Date added')
    file = models.FileField(upload_to=mouse_path)
    performance = models.DecimalField('Session performance', max_digits=3, decimal_places=2, default=0.0)
    valid_trials = models.IntegerField('Number trials completed', default=0)
    trials_correct = models.IntegerField('Trials correct', default=0)
    protocol_name = models.CharField('Protocol Name', max_length=32, default='', blank=True)
    rig = models.CharField('Rig', max_length=10, default='', blank=True)
    lickgraceperiod = models.IntegerField('Lick Grace Period', blank=True, default=0)
    odorset_name = models.CharField('Odorset name', max_length=32, blank=True, default='')

    @transaction.atomic
    def process(self):
        print("Processing")
        with tb.open_file(self.file.path) as f:
            assert isinstance(f, tb.File)
            tr_table = f.root.Trials.read()
            ncorrects = 0
            nvalids = 0
            ntrials = 0
            attrs = f.root._v_attrs.__dict__
            self.protocol_name = attrs.get('protocol_name', 'none_specified')
            self.rig = attrs.get('rig', tr_table[0]['rig'])
            self.odorset_name = attrs.get('odor_set_name', 'none_specified')
            self.lickgraceperiod = attrs.get('lickgraceperiod', -1)
            for tr in tr_table:
                result = tr['result']
                valid = result > 0 and result < 5
                correct = result > 0 and result < 3
                nvalids += valid  # boolean adds to integer just fine.
                ncorrects += correct
                ntrials += 1
                trial = Trial(session=self,
                              trial_num=tr['trialNumber'],
                              result=result,
                              valid=valid,
                              correct=correct,
                              odor=tr['odor'],
                              odorconc=tr['odorconc'],
                              laser_delay=tr['pulseOnsetDelay_1'],
                              laser_intensity=int(b'0'+tr['LaserIntensity_1'][:-2]),
                              laser_npulses=tr['trainlength_1']
                              )
                trial.save()
        self.performance = ncorrects / nvalids
        self.trials_correct = ncorrects
        self.valid_trials = nvalids
        self.save()

    def odorset(self):
        trials = self.trial_set.all()
        odorset = set()
        for t in trials:
            odorset.add(t.odor)
        return odorset

    def lasers(self):
        trials = self.trial_set.all()
        lasers = False
        for t in trials:
            if t.laser_intensity:
                lasers = True
        return lasers

    def __str__(self):
        return "session {0}".format(self.session_num)

class Trial(models.Model):
    session = models.ForeignKey(Session)
    trial_num = models.IntegerField('Trial Number')
    result = models.IntegerField('Result')
    valid = models.BooleanField('Valid')
    correct = models.BooleanField('Correct')
    odor = models.CharField('Odor', max_length=32)
    odorconc = models.FloatField('Odor concentration')
    laser_delay = models.IntegerField('Laser delay (ms)')
    laser_intensity = models.DecimalField(max_digits=10, decimal_places=7, verbose_name='Laser intensity (mW)')
    laser_npulses = models.IntegerField('Number laser pulses')

    def __str__(self):
        return "Trial {}".format(self.trial_num)

class TrialTable(tables.Table):
    class Meta:
        model = Trial
        exclude = ['session', 'id']
#  TODO: make extensible trial model that can encapsulate a dictionary of data based on what is present within the H5.



