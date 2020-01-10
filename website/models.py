# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin

class Category(models.Model):
    name = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u"%s" % self.name


class Boardgame(models.Model):
    name = models.CharField(max_length=255, null=False)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    min_players = models.IntegerField(null=False)
    max_players = models.IntegerField(null=False)
    best_players = models.IntegerField(null=False)
    rate = models.FloatField(null=True, default=5)
    learning_time = models.IntegerField(null=False)
    duration = models.IntegerField(null=False)
    image = models.ImageField(null=False)
    description = models.TextField()
    bgg_code = models.IntegerField(null=False)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u"%s" % self.name


class BoardgameAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class Tag(models.Model):
    name = models.CharField(max_length=255, null=False)
    boardgame = models.ForeignKey(to=Boardgame, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " == " + self.boardgame.name

    def __unicode__(self):
        return u"%s" % self.name


class Event(models.Model):
    title = models.CharField(max_length=250, null=False)
    description = models.TextField(null=False)
    datetime = models.DateTimeField(default=False)
    image = models.ImageField(null=False)
    evand_frame = models.TextField(null=False)


class EventDorna(models.Model):
    title = models.CharField(max_length=250, null=False)
    description = models.TextField(null=False)
    datetime = models.DateTimeField(default=False)
    image = models.ImageField(null=False)
    evand_frame = models.TextField(null=False)


class LeaderBoard(models.Model):
    boardgame_name = models.CharField(max_length=1250, null=False)
    robot_number = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.boardgame_name + " : " + self.robot_number


class PersonToLeaderBoard(models.Model):
    person_name = models.CharField(max_length=1250, null=False)
    rank = models.IntegerField(null=False)
    points = models.IntegerField(null=False)
    leader_board = models.ForeignKey(to=LeaderBoard, on_delete=models.CASCADE)

    def __str__(self):
        return self.person_name + " : " + str(self.rank) + " Point is : " + str(self.points)