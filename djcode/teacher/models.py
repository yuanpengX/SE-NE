# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.
class Question(models.Model):
    QuestionId = models.CharField(max_length=20)
    Stem = models.CharField(max_length=2000)
    OptionA = models.CharField(max_length=100)
    OptionB = models.CharField(max_length=100)
    OptionC = models.CharField(max_length=100, blank=True)
    OptionD = models.CharField(max_length=100, blank=True)
    Type = models.IntegerField  # 1 choose 3- judge 1. 单选 2 , 多选 3. 判断
    Difficulty = models.FloatField # 1-5 integer
    Flag = models.BooleanField #whether modify flag
    Answer = models.CharField(max_length=20)
    Chapter = models.CharField(max_length=20)
    ClassId = models.CharField(max_length=20)
    Score = models.IntegerField

class Paper(models.Model):
    PaperId = models.CharField(max_length=20)
    PaperName = models.CharField(max_length=30)
    QId = models.CharField(max_length=400)
    Creator = models.CharField(max_length=20)  #TEAACHER'S id
    ClassId = models.CharField(max_length=20)
    StartTime = models.DateTimeField
    Deadline = models.DateTimeField
    MaxScore = models.FloatField(null=True)
    MinScore = models.FloatField(null=True)
    SumScore = models.FloatField(null=True)
    SubmitNum = models.IntegerField(null=True)

# database below is used to analyze
class Score(models.Model):
    StudentId = models.CharField(max_length=20)
    PaperId = models.CharField(max_length=20)
    ValidScore = models.FloatField(null=True)
    SubmitTimes = models.IntegerField(null=True)
# Used to Analysis
class History(models.Model):
    PaperId = models.CharField(max_length=20)
    StudentId = models.CharField(max_length=20)
    QIdError = models.CharField(max_length=20)

class OnAuth(models.Model):
    OnAuthClassId = models.CharField(max_length=10)