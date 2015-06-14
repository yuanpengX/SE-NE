# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from form import PaperGenerateForm,CHQuestionAddForm,JUQuestionAddForm,QuestionSearchForm
from django.http import Http404,HttpResponseRedirect,HttpResponse
from math import exp
import random
from models import Paper, Question, Score, History
from IMS.models import Class_info,Student_user,Course_info,Faculty_user
import datetime
import re
import os
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group,Permission
#from django.views.decorators.csrf import csrf_protect, csrf_exempt

# Create your views here.

#finish0.9

def SelectQuestion(ChL,ChH,Type_i,Num,Diff):
    SelectQue = []
    mysum = 0
    CourseId = Class_info.objects.get(class_id="0000000001")
    CourseId = CourseId.course_id.course_id
    p =[]
    for i in [1,2,3,4,5]:
        p.append(exp(-abs(i-Diff)))
    sum_p = sum(p)
    #print p
    for i in [2,3,4,5]:
        p[i-1] = p[i-1]/sum_p
        NumQ = int(round(Num*p[i-1]))
        mysum +=NumQ
        Q = Question.objects.filter(Chapter__in=range(ChL,ChH+1), Type__in=Type_i, Difficulty=i,CourseId=CourseId)
        # print Q
        #SelectQue
        if len(Q)<NumQ:
            return []
        else:
            for i in random.sample(range(len(Q)),NumQ):
                SelectQue.append(Q[i])
    #print SelectQue
    Q = Question.objects.filter(Chapter__in=range(ChL,ChH+1), Type__in=Type_i, Difficulty=1)
    NumQ = Num-mysum
    if len(Q)<NumQ:
        return []
    else:
        for i in random.sample(range(len(Q)),NumQ):
            SelectQue.append(Q[i])
    #print SelectQue
    return SelectQue
#finish0.9
def PaperAutoGenerate(request):
    # here we need user_auth
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/');
    errors = []
    if request.POST:
        #print request.POST
        cd = request.POST
        chL= cd['ChL']
        chH = cd['ChH']
        SNum = cd['SelectNum']
        JNum = cd['CheckNum']
        Diff = cd['Difficulty']
        Name = cd['PaperName']
        Dead =cd['DeadLine']
        dead = re.sub(r'\.','-',Dead)
        mtime = cd['mytime']
        if mtime is u'':
            errors.append('please input time!')
            return render_to_response('P_auto.html', {'errors': errors},context_instance=RequestContext(request))
        deadline = dead+' '+mtime
        #print cd
        #print mtime
        try:
            Diff = int(Diff)
            SNum = int(SNum)
            JNum = int(JNum)
            chL = int(chL)
            chH = int(chH)
        except ValueError:
            errors.append('Please input integer!')
            return render_to_response('P_auto.html', {'errors': errors},context_instance=RequestContext(request))
        ChL = SelectQuestion(chL,chH, [2,3], SNum, Diff)
        if not ChL:
            errors.append('Not Enough Select Question!')
            return render_to_response('P_auto.html', {'errors': errors},context_instance=RequestContext(request))
        JuL = SelectQuestion(chL, chH,[1], JNum, Diff)
        if not JuL:
            errors.append('Not Enough Judge Question')
            return render_to_response('P_auto.html', {'errors': errors},context_instance=RequestContext(request))
        QuestList = [ChL, JuL]
        #print QuestList
        # add paper into database
        Qid = ''
        mylist = []
        for questionL in QuestList:
            for question in questionL:
            #print type(question)
                Qid = Qid + question.QuestionId
                mylist.append(question)
        print mylist
        paperid = re.sub(r'[-:\\.\\ ]','',str(datetime.datetime.now()))
        paperid = request.user.username + paperid[0:(20-len(request.user.username))]
        paper = Paper.objects.create(PaperId= paperid,
                            PaperName = Name,
                            QId = Qid,
                            Creator = request.user.username,
                            # jfaj
                            MaxScore = 0,
                            MinScore = 10000,
                            SumScore = 0,
                            SubmitNum = 0,
                            ClassId = '0000000001',
            #                StartTime = datetime.datetime.now(),
                            #Deadline = Dead )
                             Deadline = deadline)
        #return HttpResponse('create paper successfully!')
        return render_to_response('P_view_tea.html', {'QuestionList': mylist,'Paper':paper},context_instance=RequestContext(request))
    return render_to_response('P_auto.html', {'errors': errors},context_instance=RequestContext(request))

def PaperD(request,offset):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/');
    if request.POST:
        errors = []
        try:
            paper = Paper.objects.get(PaperId = offset)
        except Paper.DoesNotExist:
            raise Http404
        paper.delete()
        return render_to_response('P_auto.html', {'errors': errors},context_instance=RequestContext(request))

def PaperManualGenerate(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.POST:
        form = request.POST
        chL = form['ChapterL']
        chU = form['ChapterU']
        if chL is u'':
            chL = 1
        if chU is u'':
            chU = 100
        dfl = form['DifL']
        dfu = form['DifU']
        if dfl is u'':
            dfl = 1
        if dfu is u'':
            dfu = 5
        keyword = form['Keyword']
        #print form
        type_i = form['Type']
        #print type_i
        try:
            type_i = int(type_i)
            dfl = int(dfl)
            dfu = int(dfu)
            chL = int(chL)
            chU = int(chU)
        except ValueError:
            return render_to_response('Q_mod.html',{'pagename':'Paper Manual Generate','QuestionList':QuestionList},context_instance=RequestContext(request))
        if (dfl>dfu) or (chU<chL) or (dfl<=0) or (dfu>6) or chL<=0 or chU>100:
            return render_to_response('Q_mod.html',{'pagename':'Paper Manual Generate','QuestionList':QuestionList},context_instance=RequestContext(request))
        if type_i is 0:
            type_i = [1,2,3]
        else:
            type_i = [type_i]
        if keyword is '':
            QuestionList = Question.objects.filter(Chapter__in=range(chL,chU+1),Type__in=type_i,Difficulty__in=range(dfl,dfu+1),Flag=1)
        else:
            QuestionList = Question.objects.filter(Chapter__in=range(chL,chU+1),Type__in=type_i,Stem__icontains=keyword,Difficulty__in=range(dfl,dfu+1),Flag=1)
    return render_to_response('Q_mod.html',{'pagename':'modify question','QuestionList':QuestionList},context_instance=RequestContext(request))

def PaperMG(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    pagename = 'Paper Manual Generate'
    errors = []
    if request.POST:
        form = request.POST
        qid = form.getlist('Choose')
        Name = form['PaperName']
        Dead =form['DeadLine']
        dead = re.sub(r'\.','-',Dead)
        mtime = form['mytime']
        if mtime is u'':
            errors.append('please input time!')
            return render_to_response('P_auto.html', {'errors': errors},context_instance=RequestContext(request))
        deadline = dead+' '+mtime
        if len(qid) is not 20:
            errors.append('Number of question is not 20!')
            return render_to_response('Q_mod.html',locals(),context_instance=RequestContext(request))
        paperid = re.sub(r'[-:\\.\\ ]','',str(datetime.datetime.now()))
        paperid = request.user.username + paperid[0:(20-len(request.user.username))]
        paper = Paper.objects.create(PaperId= paperid,
                            PaperName = Name,
                            QId = qid,
                            Creator = request.user.username,
                            # jfaj
                            ClassId = '0000000001',
            #                StartTime = datetime.datetime.now(),
                            #Deadline = Dead )
                             Deadline = deadline)

def PaperAnalysis(request, offset):
    #this view generate PapeAnalysis with ID (get from url)
    PaperView = False
    AuthError = False
    if request.user.is_authenticated():
        try:
           PaperL = Paper.objects.filter(PaperId=offset)
        except Paper.DoesNotExist:
           raise Http404()
        # get score
        PaperL = Paper.objects.filter(PaperId=offset)
        QuesId = PaperL['QId']
        QuestionList = []
        for i in range(len(QuesId)):
            QuestionList[i]
    else:
        AuthError = True
    return render_to_response('',{'AuthError':AuthError,'QuestionList':QuestionList,'PaperView':PaperView})

'''
#finish0.9
def PaperView(request,offset):
    #this view generate PapeAnalysis with ID (get from url)
    Paperview = True
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/user_auth/')
    else:
        try:
           PaperL = Paper.objects.filter(PaperId=offset)
        except Paper.DoesNotExist:
           raise Http404()
        QuesId = PaperL['QId']
        QuestionList = []
        for i in range(20):
            QuestionList[i] = Question.objects.filter(QuestionId=QuesId[i*20:i*20+19])
    return render_to_response('paper.html',{'QuestionList':QuestionList,'view':PaperView})
'''
def QuestionModify(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/user_auth/')
    QuestionList = []
    if request.method == 'POST':
        form = request.POST
        chL = form['ChapterL']
        chU = form['ChapterU']
        if chL is u'':
            chL = 1
        if chU is u'':
            chU = 100
        dfl = form['DifL']
        dfu = form['DifU']
        if dfl is u'':
            dfl = 1
        if dfu is u'':
            dfu = 5
        keyword = form['Keyword']
        #print form
        type_i = form['Type']
        #print type_i
        try:
            type_i = int(type_i)
            dfl = int(dfl)
            dfu = int(dfu)
            chL = int(chL)
            chU = int(chU)
        except ValueError:
            return render_to_response('Q_mod.html',{'pagename':'modify question','QuestionList':QuestionList},context_instance=RequestContext(request))
        if (dfl>dfu) or (chU<chL) or (dfl<=0) or (dfu>6) or chL<=0 or chU>100:
            return render_to_response('Q_mod.html',{'pagename':'modify question','QuestionList':QuestionList},context_instance=RequestContext(request))
        if type_i is 0:
            type_i = [1,2,3]
        else:
            type_i = [type_i]
        if keyword is '':
            QuestionList = Question.objects.filter(Chapter__in=range(chL,chU+1),Type__in=type_i,Difficulty__in=range(dfl,dfu+1),Flag=1)
        else:
            QuestionList = Question.objects.filter(Chapter__in=range(chL,chU+1),Type__in=type_i,Stem__icontains=keyword,Difficulty__in=range(dfl,dfu+1),Flag=1)
    return render_to_response('Q_mod.html',{'pagename':'modify question','QuestionList':QuestionList},context_instance=RequestContext(request))
#    return HttpResponse('hello')

def QuestionM(request,offset):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/user_auth/')
    if request.POST:
            #print offset
        QuestionName = Question.objects.filter(QuestionId=offset)
        if not QuestionName:
            return HttpResponse('<html>Question Do not Exist!</html>')
        form = request.POST;
        option = form.getlist('Option')
        option= str(''.join(option))
        if len(option)<=0:
            return HttpResponse('<html>No Answer!</html>')
        difficulty = form['Difficulty']
        score = form['Score']
        stem = form['Stem']
        try:
            difficulty = int(difficulty)
            score = int(score)
        except ValueError:
            return HttpResponse('<html>TYpe ERROR!</html>')
        try:
            optionA = form['OptionA']
            optionB = form['OptionB']
            optionC = form['OptionC']
            optionD = form['OptionD']
            if (optionA is u'') or (optionB is u'') or (optionC is u'') or (optionD is u''):
                return HttpResponse('You input no options!')
            QuestionName.update(Difficulty = difficulty,Stem=stem,Score=score,Answer = option,OptionA=optionA,OptionB=optionB,OptionC=optionC,OptionD=optionD)
        except KeyError:
            QuestionName.update(Difficulty = difficulty,Stem=stem,Score=score,Answer = option)
        return HttpResponse('Modify successfully!')

def QuestionD(request,offset):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.POST:
        try:
            QuestionName = Question.objects.filter(QuestionId = offset).update(Flag=0)
            return HttpResponse('Delete Sucessfully!')
        except Question.DoesNotExist:
            return HttpResponse('Question Does Not Exist!')

def QuestionDelete(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    QuestionList = []
    if request.method == 'POST':
        form = request.POST
        chL = form['ChapterL']
        chU = form['ChapterU']
        if chL is u'':
            chL = 1
        if chU is u'':
            chU = 100
        dfl = form['DifL']
        dfu = form['DifU']
        if dfl is u'':
            dfl = 1
        if dfu is u'':
            dfu = 5
        keyword = form['Keyword']
        #print form
        type_i = form['Type']
        #print type_i
        try:
            type_i = int(type_i)
            dfl = int(dfl)
            dfu = int(dfu)
            chL = int(chL)

            chU = int(chU)
        except ValueError:
            return render_to_response('Q_del.html',{'pagename':'modify question','QuestionList':QuestionList},context_instance=RequestContext(request))
        if (dfl>dfu) or (chU<chL) or (dfl<=0) or (dfu>6) or chL<=0 or chU>100:
            return render_to_response('Q_del.html',{'pagename':'modify question','QuestionList':QuestionList},context_instance=RequestContext(request))
        if type_i is 0:
            type_i = [1,2,3]
        else:
            type_i = [type_i]
        if keyword is '':
            QuestionList = Question.objects.filter(Chapter__in=range(chL,chU+1),Type__in=type_i,Difficulty__in=range(dfl,dfu+1),Flag=1)
        else:
            QuestionList = Question.objects.filter(Chapter__in=range(chL,chU+1),Type__in=type_i,Stem__icontains=keyword,Difficulty__in=range(dfl,dfu+1),Flag=1)
    return render_to_response('Q_del.html',{'pagename':'modify question','QuestionList':QuestionList},context_instance=RequestContext(request))

#finish0.9
def QuestionAdd(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if not request.POST:
        #return  HttpResponse('hello')
        return render_to_response('Q_add.html',{'pagename':'Add Questions'},context_instance=RequestContext(request))

def QuestionAddForm1(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.POST:
        form = request.POST
        sOptionA = form['SOptionA']
        sOptionB = form['SOptionB']
        sOptionC = form['SOptionC']
        sOptionD = form['SOptionD']
        if (sOptionC is '') or (sOptionB is '') or (sOptionA is '') or (sOptionD is ''):
            return render_to_response('Q_add.html',{'pagename':'Add Questions'},context_instance=RequestContext(request))
        score = form['Score']
        difficulty = form['Difficulty']
        chapter = form['Chapter']
        stem = form['Stem']
        answer = str(''.join(request.POST.getlist('SOptionc')))
        try:
            difficulty = int(difficulty)
            chapter = int(chapter)
            score = int(score)
        except ValueError:
            return render_to_response('Q_add.html',{'pagename':'Add Questions'},context_instance=RequestContext(request))
        if (difficulty<0)or (score<=0) or (difficulty>6) or (chapter<=0) or (chapter>100) or (stem is ''):#or (len(answer) is 0):
            return render_to_response('Q_add.html',{'pagename':'Add Questions'},context_instance=RequestContext(request))
        flag = 1
        if answer>1:
            type_i = 3
        else:
            type_i = 2
        questionId = re.sub(r'[-:\\.\\ ]','',str(datetime.datetime.now()))
        length = len(str(request.user.username))
        questionId = request.user.username + questionId[0:(20-length)]
        Question.objects.create(QuestionId =questionId,
                                Stem = stem,
                                OptionA = sOptionA,
                                OptionB = sOptionB,
                                OptionC = sOptionC,
                                OptionD = sOptionD,
                                Type = type_i,
                                Difficulty = difficulty,
                                Flag = flag,
                                Answer = answer,
                                Chapter = chapter,
                                CourseId = '00000001',
                                Score = score,
            )
        return HttpResponse('<html>create successfully</html>')

def QuestionAddForm2(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.POST:
        form = request.POST
        score = form['Score']
        difficulty = form['Difficulty']
        chapter = form['Chapter']
        stem = form['JStem']
        answer = form['JTr']
        try:
            difficulty = int(difficulty)
            chapter = int(chapter)
            score = int(score)
        except ValueError:
            return render_to_response('Q_add.html',{'pagename':'Add Questions'},context_instance=RequestContext(request))
        if (difficulty<0)or (score<=0) or (difficulty>6) or (chapter<=0)or(chapter>100) or (stem is ''):#or (len(answer) is 0):
            return render_to_response('Q_add.html',{'pagename':'Add Questions'},context_instance=RequestContext(request))
        flag = 1
        '''if answer>1:
            type_i = 3
        else:
            type_i = 2'''
        type_i = 1
        questionId = re.sub(r'[-:\\.\\ ]','',str(datetime.datetime.now()))
        length = len(str(request.user.username))
        questionId = request.user.username + questionId[0:(20-length)]
        Question.objects.create(QuestionId =questionId,
                                Stem = stem,
             #                   OptionA = sOptionA,
              #                  OptionB = sOptionB,
               #                 OptionC = sOptionC,
                #                OptionD = sOptionD,
                                Type = type_i,
                                Difficulty = difficulty,
                                Flag = flag,
                                Answer = str(answer),
                                Chapter = chapter,
                                CourseId = '00000001',
                                Score = score,
            )
        return HttpResponse('<html>create successfully</html>')

def newf(request):
    for i  in range(20):
        questionId = re.sub(r'[-:\\.\\ ]','',str(datetime.datetime.now()))
        stem = questionId + 'hello,kitty'+questionId
        sOptionA = questionId + 'hello,kitty'+'A'
        sOptionB = questionId + 'hello,kitty'+'B'
        sOptionC = questionId + 'hello,kitty'+'C'
        sOptionD = questionId + 'hello,kitty'+'D'
        type_i = 3
        difficulty = i%5+1
        flag = 1
        answer = 'ACD'
        chapter = i%20+1
        score = i%10+1
        Question.objects.create(QuestionId =questionId,
                                Stem = stem,
                                OptionA = sOptionA,
                                OptionB = sOptionB,
                                OptionC = sOptionC,
                                OptionD = sOptionD,
                                Type = type_i,
                                Difficulty = difficulty,
                                Flag = flag,
                                Answer = answer,
                                Chapter = chapter,
                                CourseId = '00000001',
                                Score = score,
            )
    for i  in range(20):
        questionId = re.sub(r'[-:\\.\\ ]','',str(datetime.datetime.now()))
        stem = questionId + 'hello,kitty'+questionId
        sOptionA = questionId + 'hello,kitty'+'A'
        sOptionB = questionId + 'hello,kitty'+'B'
        sOptionC = questionId + 'hello,kitty'+'C'
        sOptionD = questionId + 'hello,kitty'+'D'
        type_i = 2
        difficulty = i%5+1
        flag = 1
        answer = 'A'
        chapter = i%20+1
        score = i%10+1
        Question.objects.create(QuestionId =questionId,
                                Stem = stem,
                                OptionA = sOptionA,
                                OptionB = sOptionB,
                                OptionC = sOptionC,
                                OptionD = sOptionD,
                                Type = type_i,
                                Difficulty = difficulty,
                                Flag = flag,
                                Answer = answer,
                                Chapter = chapter,
                                CourseId = '00000001',
                                Score = score,
            )
    for i  in range(20):
        questionId = re.sub(r'[-:\\.\\ ]','',str(datetime.datetime.now()))
        stem = questionId + 'hello,kitty'+questionId
        sOptionA = questionId + 'hello,kitty'+'A'
        sOptionB = questionId + 'hello,kitty'+'B'
        sOptionC = questionId + 'hello,kitty'+'C'
        sOptionD = questionId + 'hello,kitty'+'D'
        type_i = 2
        difficulty = i%5+1
        flag = 1
        answer = 'C'
        chapter = i%20+1
        score = i%10+1
        Question.objects.create(QuestionId =questionId,
                                Stem = stem,
                                OptionA = sOptionA,
                                OptionB = sOptionB,
                                OptionC = sOptionC,
                                OptionD = sOptionD,
                                Type = type_i,
                                Difficulty = difficulty,
                                Flag = flag,
                                Answer = answer,
                                Chapter = chapter,
                                CourseId = '00000001',
                                Score = score,
            )
    for i  in range(20):
        questionId = re.sub(r'[-:\\.\\ ]','',str(datetime.datetime.now()))
        stem = questionId + 'hello,kitty'+questionId
        #sOptionA = questionId + 'hello,kitty'+'A'
        ##sOptionB = questionId + 'hello,kitty'+'B'
        #sOptionC = questionId + 'hello,kitty'+'C'
        #sOptionD = questionId + 'hello,kitty'+'D'
        type_i = 1
        difficulty = i%5+1
        flag = 1
        answer = 'F'
        chapter = i%20+1
        score = i%10+1
        Question.objects.create(QuestionId =questionId,
                                Stem = stem,
                   #             OptionA = sOptionA,
                    #            OptionB = sOptionB,
                     #           OptionC = sOptionC,
                      #          OptionD = sOptionD,
                                Type = type_i,
                                Difficulty = difficulty,
                                Flag = flag,
                                Answer = answer,
                                Chapter = chapter,
                                CourseId = '00000001',
                                Score = score,
            )
    for i  in range(20):
        questionId = re.sub(r'[-:\\.\\ ]','',str(datetime.datetime.now()))
        stem = questionId + 'hello,kitty'+questionId
        #sOptionA = questionId + 'hello,kitty'+'A'
        #sOptionB = questionId + 'hello,kitty'+'B'
        #sOptionC = questionId + 'hello,kitty'+'C'
        #sOptionD = questionId + 'hello,kitty'+'D'
        type_i = 1
        difficulty = i%5+1
        flag = 1
        answer = 'T'
        chapter = i%20+1
        score = i%10+1
        Question.objects.create(QuestionId =questionId,
                                Stem = stem,
                   #             OptionA = sOptionA,
                    #            OptionB = sOptionB,
                     #           OptionC = sOptionC,
                      #          OptionD = sOptionD,
                                Type = type_i,
                                Difficulty = difficulty,
                                Flag = flag,
                                Answer = answer,
                                Chapter = chapter,
                                CourseId = '00000001',
                                Score = score,
            )

    return HttpResponse('why should i return ?')