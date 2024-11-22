from django.db import models
from django.utils import timezone
import datetime


# Create your models here.
class User(models.Model):
    userid = models.IntegerField()
    discorduserid = models.CharField(max_length=20)
    discordguildid = models.CharField(max_length=20)
    ismod = models.BooleanField(default=False)
    temporarypoints = models.IntegerField(default=0)
    permanentpoints = models.IntegerField(default=0)
    createtimestamp = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return str(self.userid)


class Exile(models.Model):
    exileid = models.IntegerField()
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField(default="")
    starttimestamp = models.DateTimeField(default=timezone.now)
    endtimestamp = models.DateTimeField(default=timezone.now)
    exilestatus = models.IntegerField()

    def __str__(self) -> str:
        return f'User {self.userid} exiled for reason: "{self.reason}"'


class Strike(models.Model):
    strikeid = models.IntegerField()
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    severity = models.IntegerField(default=0)
    reason = models.TextField()
    createtimestamp = models.DateTimeField(default=timezone.now)
    createdby = models.CharField(max_length=20, default="")
    lasteditedtimestamp = models.DateTimeField(default=timezone.now)
    lasteditedby = models.CharField(max_length=20, default="")

    def __str__(self) -> str:
        return f'User {self.userid} given strike for reason: "{self.reason}"'
