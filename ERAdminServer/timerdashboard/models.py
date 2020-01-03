from django.db import models

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=128)
    default_time = models.IntegerField(default=3600)


class GameResult(models.Model):
    name = models.CharField(max_length=64)

class TimerState(models.Model):
    name = models.CharField(max_length=32)

class RoomDevice(models.Model):
    mac = models.CharField(max_length=32)
    local_ip = models.CharField(max_length=32)
    room = models.ForeignKey(to=Room, on_delete=models.SET_NULL, null=True)

class GameInstance(models.Model):
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    date_start = models.DateTimeField('Started on')
    date_maxend = models.DateTimeField('End expected on')
    date_finished = models.DateTimeField('Finished on', null=True)
    result = models.ForeignKey(to=GameResult, on_delete=models.SET_NULL, null=True)

class TimerDeviceInstance(models.Model):
    status = models.ForeignKey(to=TimerState, on_delete=models.CASCADE)
    time_left = models.IntegerField(default=0)
    device = models.ForeignKey(to=RoomDevice, on_delete=models.CASCADE)



