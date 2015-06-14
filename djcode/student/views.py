from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect,Http404
from teacher.models import Paper,Score,Question,Score,History
from IMS.models import Class_info,Student_user,Course_info,Faculty_user,class_table
import re
from django.template.context import RequestContext
# Create your views here.

def ViewClass(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        StudentId= request.user.username
        #print StudentId
        ClassTable = class_table.objects.filter(student_id__id=StudentId)
        if not ClassTable:
            return HttpResponse('<html><title></title><body></html>',)
        #if not ClassTable:
        #   return HttpResponseRedirect('/')
        #print  ClassTable
           #i = 0
        #ClassList = []
        ClassList = []
        for ClassName in ClassTable:
            ClassId = ClassName.class_id.class_id
        #print type(ClassId)
            CourseName = ClassName.class_id.course_id.name
            ClassList.append({'Name': CourseName+' '+ClassId,'Url':request.get_host()+'/student/'+ClassId+'/'})
        return render_to_response('Choose_Class.html',{'ClassList':ClassList})

def ViewPaper(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/ims/')
    if request.method =='GET':
        ClassID = '0000000001'
        Paperlist = Paper.objects.filter(ClassId = ClassID)
        PaperList =[]
        for paperid in Paperlist:
            #P = Score.objects.filter(StudentId=request.user.username,ClassId=ClassID,PaperId=paperid.PaperId)
            try:
                history = Score.objects.get(StudentId=request.user.username,PaperId = paperid.PaperId)
            except Score.DoesNotExist:
                history=Score.objects.create(StudentId=request.user.username,PaperId = paperid.PaperId,ValidScore=0, SubmitTimes=0)
            paperInfo = {'PaperName':paperid.PaperName,'ValidScore':history.ValidScore,'SubmitTime':history.SubmitTimes,'URL':'/student/test/'+paperid.PaperId+'/','DeadLine':paperid.Deadline}
            PaperList.append(paperInfo)
        return render_to_response('P_viewlist_stu.html',locals(),context_instance=RequestContext(request))

def OnlinePaper(request,offset):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    if request.method == 'GET':
        try:
            QId = Paper.objects.get(PaperId = offset)
        except Paper.DoesNotExist:
            raise Http404
        QuesId = QId['QId']
        QuestionList = []
        for i in range(20):
            QuestionList[i] = Question.objects.filter(QuestionId=QuesId[i*20:i*20+19])
            #if QuestionList[i].
        return render_to_response('',{'QuestionList':QuestionList})

def ReturnScore(request,offset):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/user_auth/')
    if request.method =='POST':
        url = request.get_full_path()
        PaperId = re.search(r'/student/test/\d{20}/',url).group()
        PaperId = PaperId[14:-1]
        paper = Paper.objects.get(PaperId).QId
        score = 0
        for i in range(20):
            QuestionL = Question.objects.get(QuestionId=paper[i*20:i*20+19])
            Answer = QuestionL['Answer']
            SumScore = QuestionL['score']
            Id= '%s' % i
            answer = request.getlist('Question'+Id)
            if not cmp(answer.sort(),Answer):
                score = score+SumScore
        return render_to_response('',{'score':score})


