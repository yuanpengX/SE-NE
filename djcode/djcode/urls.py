"""djcode URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
import django.contrib.auth.views as auth_views
from IMS.views import startup
import student.views as student_view
import teacher.views as teacher_view
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ims/', include('IMS.urls')),
    url(r'^$', startup),
    url(r'^class_list/$',student_view.ViewClass),
    url(r'^teacher/AddQuestion/$',teacher_view.QuestionAdd),
    url(r'^addform1/$',teacher_view.QuestionAddForm1),
    url(r'^addform2/$',teacher_view.QuestionAddForm2),
    url(r'^teacher/ModifyQuestion/$',teacher_view.QuestionModify),
    url(r'^modify/([0-9a-zA-Z]{20})/$',teacher_view.QuestionM),
    url(r'^teacher/DeleteQuestion/$',teacher_view.QuestionDelete),
    url(r'^delete/([0-9a-zA-Z]{20})/$',teacher_view.QuestionD),
   # url(r'^test/$',teacher_view.newf),
    url(r'^teacher/AutoGenerate/$',teacher_view.PaperAutoGenerate),
    url(r'^Cancel/([0-9a-zA-Z]{20})/$',teacher_view.PaperD),
    url(r'^teacher/ManualGenerate/$',teacher_view.PaperManualGenerate),
    url(r'^student/ViewPaper/$',student_view.ViewPaper),
    url(r'^student/test/([0-9a-zA-Z]{20})/$',student_view.OnlinePaper),
    url(r'^student/test/score/([0-9a-zA-Z]{20,30})/$',student_view.ReturnScore)
]
