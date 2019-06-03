# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
# pages/views.py
from django.views.generic import TemplateView
import datetime;
#from datetime import datetime, date, timedelta

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

from .forms import LvApproverEdit, LvBalanceEdit, LvApplyForm, LvScheduleForm
from .models import LvApplications, LvBalances, StaffMaster, StaffUsers, LvSchedules, User
from .models import LvHoliday, LvDepartment, LvApprovers

'''class HomePageView(TemplateView):
    template_name = 'home.html'
'''
def HomePageView(request):
    response = redirect('/defaultView/')
    return response

class AboutPageView(TemplateView):
    template_name = 'about.html'

@login_required(login_url='/uzers/login/') #redirects
def lvApplications(request):
    if request.method == 'GET':
        form = LvApplyForm()
    else:
        form = LvApplyForm(request.POST)
        if form.is_valid():

            myitem1 = request.user.username[5:9]
            myitem2 = form.cleaned_data['lv_type']
            myitem3 = form.cleaned_data['Start_Date']
            myitemx = int(form.cleaned_data['Days'])
            myRemarks = form.cleaned_data['Remarks']

            nowx=datetime.datetime.now().date()     #application_dt=now.strftime("%Y-%m-%d"),

            tblHolidays = LvHoliday.objects.all().values('lv_holidate')
            myfinaldate =date_by_adding_business_days(myitem3, myitemx, myitem2, tblHolidays)


            leadTime = (myitem3 - nowx).days   # CAREFUL DOUBLE /// WHAt Is This Date Stuff ??

            myStaff = StaffMaster.objects.get(staff_id = myitem1)
            myLvBals = LvBalances.objects.filter(staff_id = myStaff).first()   #CAREFUL , Repeated further Down

            lvErrorMessage = ''
            lvAppLike = LvApplications.objects.filter(staff_id=myStaff, approval__gt=6, lv_type=myitem2)
            if len(lvAppLike) > 0:
                lvErrorMessage = 'You Already Applied For This Type of Leave - Delete The Older Application First'
            else:
                dummyx ='x'

            if myitem2=='1' and myLvBals.lv_annual - myitemx < 0:
                lvErrorMessage = "The Annual Leave Balance is Inadequate. Confirm Your Leave Balances"
            if myitem2=='2' and myLvBals.lv_maternity - myitemx  < 0:
                lvErrorMessage = "The Maternity Leave Balance is Inadequate. Confirm Your Leave Balances"
            if myitem2=='3' and myLvBals.lv_paternity - myitemx  < 0:
                lvErrorMessage = "The Paternity Leave Balance is Inadequate. Confirm Your Leave Balances"
            if myitem2=='4' and myLvBals.lv_study - myitemx  < 0:
                lvErrorMessage = "The Study Leave Balance is Inadequate. Confirm Your Leave Balances"
            if myitem2=='5' and myLvBals.lv_compassion - myitemx  < 0:
                lvErrorMessage = "The Compassion Leave Balance is Inadequate. Confirm Your Leave Balances"
            if myitem2=='6' and myLvBals.lv_sick - myitemx  < 0:
                lvErrorMessage = "The Sick Leave Balance is Inadequate. Confirm Your Leave Balances"

            if myitemx <0:
                lvErrorMessage = "The Leave Dates Are Not Properly Put. Check The Dates Selected"
            if leadTime < 14 and myitem2 in ('1','3','4'):
                lvErrorMessage = "Your Leave Application Is Late : 14 Days Lead Time Required"
            if leadTime < 60 and myitem2 =='2':
                lvErrorMessage = "Your Maternity Leave Application Is Late : 60 Days Lead Time Required"

            if myitemx < 0:
                lvErrorMessage = "The Leave Dates Are Not Properly Put. Duration Less Than ZERO"
            if (myitem3 - nowx).days < 0:
                lvErrorMessage = "The Leave Dates Are Not Properly Put. Check The Dates Again"

            lvApprovas = LvApprovers.objects.filter(staff_id=myStaff).first()

            if len(lvErrorMessage) <= 3:        # VERY CAREFUL, Which Error Message Is Firing ?
                try:
                    myUser = StaffMaster.objects.get(staff_id = myitem1)
                    lvAppn = LvApplications(staff_id=myUser, dept_id=myUser.dept_id,first_name=myUser.first_name,second_name=myUser.last_name,
                                            lv_type=myitem2, lv_days=myitemx,application_dt=nowx,
                                            lv_startdate=myitem3,lv_enddate=myfinaldate,
                                            approval=9,
                                            approver1_id=lvApprovas.approver1_id[5:9],
                                            approver2_id=lvApprovas.approver2_id[5:9],
                                            approver3_id=lvApprovas.approver3_id[5:9],
                                            approval1_dt='1900-02-14',approval2_dt='1900-02-14',approval3_dt='1900-02-14',
                                            cancelled_dt='1900-02-14',deducted=0, cancelled=0, remarks=myRemarks)
                    lvAppn.save();

                    myLog =  StaffUsers(staff_id=request.user.username[5:9], xtrainfo =request.user.username,
                                        xtrainfo2 = "Created Lv Appn at " + str(nowx))
                    myLog.save()
                    #notifyEmail(staff01, appova1, appova2, appova3, action)

                    saveMsg="You Have Just Submitted A Leave Application. Notifications Will Be sent on Approvals"

                    myLvBals = LvBalances.objects.filter(staff_id = myUser).first
                    lvApps = LvApplications.objects.filter(staff_id=myUser)
                    lvholidays = LvHoliday.objects.all()
                    lvApproveds = LvApplications.objects.filter(staff_id=myUser, approval=6)
                    lvSchedule = LvSchedules.objects.filter(staff_id = myUser, reschedule=0, sched_status__gt=5).first  #CAREFUL HERE // GET VS FILTER

                    form = LvApplyForm()
                    return render(request, 'lvApplications.html',{'lvApps': lvApps,'lvApproveds':lvApproveds,'myLvBals':myLvBals,
                                                                  'lvholidays':lvholidays,'query': myUser,'form': form,'saveMsg':saveMsg,
                                                                  'myitemx':myitemx, 'myitem3':myitem3, 'lvSchedule':lvSchedule, 'myfinaldate': myfinaldate})
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                #return redirect('success')
                #return render(request, "LvApplications.html", {'form': form})
            else:
                uid = request.user.username[5:9]
                theStaff = StaffMaster.objects.get(staff_id = uid)
                myLvBals = LvBalances.objects.filter(staff_id = theStaff).first
                lvApps = LvApplications.objects.filter(staff_id=theStaff).order_by('-approval')
                lvholidays = LvHoliday.objects.all()
                lvSchedule = LvSchedules.objects.filter(staff_id = theStaff, reschedule=0, sched_status__gt=5).first  #CAREFUL HERE // GET VS FILTER

                form = LvApplyForm()
                return render(request, 'lvApplications.html', {'lvApps': lvApps, 'myLvBals':myLvBals,'lvholidays':lvholidays,
                                                               'myitemx':myitemx, 'myitem3':myitem3 , 'myfinaldate': myfinaldate,
                                                               'theStaff': theStaff,'lvSchedule':lvSchedule,'lvErrorMessage':lvErrorMessage,'form': form})
    uid = request.user.username[5:9]
    theStaff = StaffMaster.objects.get(staff_id = uid)
    myLvBals = LvBalances.objects.filter(staff_id = theStaff).first
    lvApps = LvApplications.objects.filter(staff_id=theStaff).order_by('-approval')
    lvholidays = LvHoliday.objects.all()
    lvSchedule = LvSchedules.objects.filter(staff_id = theStaff, reschedule=0, sched_status__gt=5).first  #CAREFUL HERE // GET VS FILTER

    return render(request, 'lvApplications.html', {'lvApps': lvApps, 'myLvBals':myLvBals,'lvholidays':lvholidays,
                                                   'lvSchedule':lvSchedule, 'theStaff': theStaff,'form': form})

@login_required(login_url='/uzers/login/') #redirects
def lvApproval(request):

    lvholidays = LvHoliday.objects.all()

    try:
        if request.method == 'GET':

            uid = request.user.username[5:9]
            myLogUser = request.user.username
            uidfull = request.user.username
            lid = int(request.GET['id'])
            approvalMsg=''

            if uid and lid:
                if lid > 0:
                    #lid = request.GET['id']
                    llvl = request.GET['lvl']

                    #lvAppn = LvApplications.objects.get(id=lid)
                    lvAppn = LvApplications.objects.get(id=lid)     #BE CAREFUL - Why Filter NOT get()
                    lvBalan = LvBalances.objects.filter(staff_id=lvAppn.staff_id).first()

                    #print(lvAppn)
                    #print(lvBalan)

                    now=datetime.datetime.now();  mynow=now.strftime("%Y-%m-%d")

                    if llvl=='1': lvAppn.approval=8; lvAppn.approver1_id=uid; lvAppn.approval1_dt=mynow;
                    if llvl=='2': lvAppn.approval=7; lvAppn.approver2_id=uid; lvAppn.approval2_dt=mynow;
                    if llvl=='2' and lvAppn.approver2_id == 'ZUSR_000':
                        lvAppn.approval=6; lvAppn.approver3_id=uid; lvAppn.approval3_dt=mynow; llvl='3';  # when Level 3 Approver is  not defined
                    if llvl=='3':
                        #deductLeave(lvAppn.id, lvBalanc.staff_id);
                        #lvAppn = LvApplications.objects.get(id=lid)
                        #lvBalan = LvBalances.objects.filter(staff_id=staff)

                        if lvAppn.lv_type==1:
                            lvBalan.lv_annual = int(lvBalan.lv_annual) - int(lvAppn.lv_days)
                        if lvAppn.lv_type==2:
                            lvBalan.lv_maternity = lvBalan.lv_maternity - lvAppn.lv_days
                        if lvAppn.lv_type==3:
                            lvBalan.lv_paternity = lvBalan.lv_paternity - lvAppn.lv_days
                        if lvAppn.lv_type==4:
                            lvBalan.lv_study = lvBalan.lv_study - lvAppn.lv_days
                        if lvAppn.lv_type==5:
                            lvBalan.lv_compassion = lvBalan.lv_compassion - lvAppn.lv_days
                        if lvAppn.lv_type==6:
                            lvBalan.lv_sick = lvBalan.lv_sick - lvAppn.lv_days
                        if lvAppn.lv_type==7:
                            lvBalan.lv_other = lvBalan.lv_other - lvAppn.lv_days

                        lvAppn.approval=6; lvAppn.approver3_id=uid; lvAppn.approval3_dt=mynow; lvAppn.deducted=1
                        lvBalan.save()

                        myLog =  StaffUsers(staff_id = myLogUser[5:9], xtrainfo = myLogUser, xtrainfo2 = "Approved Lv # " + str(lvAppn.id) + " at " + str(mynow))
                        #myLog.save()

                    approvalMsg = '*** You Have Approved Leave Application ID : '+ str(lid)

                    if llvl=='c':
                        lvAppn.approval=5; lvAppn.cancelled=1; lvAppn.cancelled_dt=mynow
                        approvalMsg = '*** You Have Cancelled Leave Application ID : '+ str(lid)

                        myLog =  StaffUsers(staff_id = myLogUser[5:9], xtrainfo = myLogUser,
                                            xtrainfo2 = "Canced Lv # " + str(lvAppn.id) + " at " + str(mynow))
                        #myLog.save()

                    if llvl=='0': approvalMsg = ''

                    lvAppn.save()
                    #notifyEmail(staff01, appova1, appova2, appova3, action)
                    #myLog =  StaffUsers(staff_id = myLogUser[5:9], xtrainfo = myLogUser, xtrainfo2 = "Appd/Cancd Lv#" + str(lvAppn.id) + " at " + str(mynow))
                    myLog.save()

            # ================
            # CAREFUL APPROVERS Checked  Here

            boss_lvl = 0
            approva1 = LvApplications.objects.filter(approver1_id=uid, cancelled=0)  #Add Sched_Status + UserId ???
            if approva1:
                boss_lvl=9
            approva2 = LvApplications.objects.filter(approver2_id=uid, cancelled=0)  #Add Sched_Status + UserId ???
            if approva2:
                boss_lvl=8
            approva3 = LvApplications.objects.filter(approver3_id=uid, cancelled=0)  #Add Sched_Status + UserId ???
            if approva3:
                boss_lvl=7

            myLvApps1 = LvApplications.objects.filter(approval=9, approver1_id=uid, cancelled=0)
            #for myAppnn in myLvApps1:
                #myStf = StaffMaster.objects.get(staff_id = myAppnn.staff_id)
                #myAppnn.staffname = myStf.first_name #+" "+myStf.last_name

            myLvApps2 = LvApplications.objects.filter(approval=8, approver2_id=uid, cancelled=0)
            #for myAppnn in myLvApps2:
                #myStf = StaffMaster.objects.get(staff_id = myAppnn.staff_id)
                #myAppnn.staffname = myStf.first_name #+" "+myStf.last_name

            myLvApps3 = LvApplications.objects.filter(approval=7, approver3_id=uid, cancelled=0)
            #for myAppnn in myLvApps3:
                #myStf = StaffMaster.objects.get(staff_id = myAppnn.staff_id)
                #myAppnn.staffname = myStf.first_name #+" "+myStf.last_name

        #BE CAREFUL to Improve Next Query
        myUser = StaffMaster.objects.get(staff_id = uid)

        return render(request, 'lvApprovals.html',
                              {'myLvApps1': myLvApps1,'myLvApps2': myLvApps2,'myLvApps3': myLvApps3, 'myDepts':1,'user_id': uid, 'myUser':myUser,
                               'boss_lvl':boss_lvl,'lvholidays':lvholidays, 'approvalMsg':approvalMsg})     #CAREFUL With Variables
    except BadHeaderError:
        #return HttpResponse('Invalid header found.')
        return render(request, "lvApprovals.html", {'form': form})

@login_required(login_url='/uzers/login/') #redirects
def lvApprovalDetail(request):

    lvholidays = LvHoliday.objects.all()
    uid = request.user.username[5:9]
    myLogUser = request.user.username

    try:
        if request.method == 'GET':

            uid = request.user.username[5:9]
            lid = request.GET['id']
            saveMsg =''

            if uid and lid:
                llvl = request.GET['lvl']

                now=datetime.datetime.now()

                lvAppn = LvApplications.objects.get(id=lid)      #BE CAREFUL - Why Filter NOT get()
                lvBalan = LvBalances.objects.filter(staff_id= lvAppn.staff_id).first

                mynow=now.strftime("%Y-%m-%d")

                if llvl=='1': lvAppn.approval=8; lvAppn.approver1_id=uid; lvAppn.approval1_dt=mynow;
                if llvl=='2':
                    lvAppn.approval=7; lvAppn.approver2_id=uid; lvAppn.approval2_dt=mynow;
                if llvl=='2' and lvAppn.approver2_id == 'ZUSR_000':
                    lvAppn.approval=6; lvAppn.approver3_id=uid; lvAppn.approval3_dt=mynow; llvl='3';  # when Level 3 Approver is  not defined
                if llvl=='3':
                    lvAppn.approval1=6; lvAppn.approver3_id=uid; lvAppn.approval3_dt=mynow;

                    if lvAppn.lv_type ==1:
                        lvBalan.lv_annual = lvBalan.lv_annual - lvAppn.lv_days
                    if lvAppn.lv_type ==2:
                        lvBalan.lv_maternity = lvBalan.lv_maternity - lvAppn.lv_days
                    if lvAppn.lv_type ==3:
                        lvBalan.lv_paternity = lvBalan.lv_paternity - lvAppn.lv_days
                    if lvAppn.lv_type ==4:
                        lvBalan.lv_study = lvBalan.lv_study - lvAppn.lv_days
                    if lvAppn.lv_type ==5:
                        lvBalan.lv_compassion = lvBalan.lv_compassion - lvAppn.lv_days
                    if lvAppn.lv_type ==6:
                        lvBalan.lv_sick = lvBalan.lv_sick - lvAppn.lv_days

                    lvAppn.deducted=1;
                saveMsg="*** You Have Just Approved A Leave Application"
                myLog =  StaffUsers(staff_id = myLogUser[5:9], xtrainfo = myLogUser,
                                    xtrainfo2 = "Approved Lv # " + str(lvAppn.id) + " at " + str(mynow))

                if llvl=='c':
                    lvAppn.approval=5; lvAppn.cancelled=1; lvAppn.cancelled_dt=mynow
                    saveMsg="*** You Have Just Cancelled A Leave Application"
                    myLog =  StaffUsers(staff_id = myLogUser[5:9], xtrainfo = myLogUser,
                                    xtrainfo2 = "Canced Lv # " + str(lvAppn.id) + " at " + str(mynow))
                if llvl=='0':
                    saveMsg=''

                if llvl > '0':
                    lvAppn.save()
                    #notifyEmail(staff01, appova1, appova2, appova3, action)
                    myLog.save()


            # ===============================
            # CAREFUL APPROVERS Checked  Here

            boss_lvl = 0
            approva1 = LvApplications.objects.filter(approver1_id=uid, cancelled=0)
            if approva1:
                boss_lvl=9
            approva2 = LvApplications.objects.filter(approver2_id=uid, cancelled=0)  #Add Sched_Status + UserId ???
            if approva2:
                boss_lvl=8
            approva3 = LvApplications.objects.filter(approver3_id=uid, cancelled=0)  #Add Sched_Status + UserId ???
            if approva3:
                boss_lvl=7

        #BE CAREFUL to Improve Next Query
        #lvApps = LvApplications.objects.all()
        myUser = StaffMaster.objects.get(staff_id = uid)
        theAppn = LvApplications.objects.get(id=lid)
        theStaffBalances = LvBalances.objects.filter(staff_id = theAppn.staff_id).first  #CAREFUL HERE // GET VS FILTER
        theStaff = StaffMaster.objects.get(id = int(theAppn.staff_id_id))
        theStaffSchedule = LvSchedules.objects.filter(staff_id = theAppn.staff_id, reschedule=0, sched_status__gt=5).first  #CAREFUL HERE // GET VS FILTER

        lvAppsList = LvApplications.objects.filter(staff_id = theAppn.staff_id).order_by('-approval')

        #return redirect('/lvApprovalDetail/')

        return render(request,
                      'lvApprovalDetail.html', {'lvAppsList': lvAppsList,'boss_lvl':boss_lvl,'saveMsg':saveMsg,
                                                'theAppn': theAppn,'lvholidays':lvholidays, 'myUser':myUser,'theStaff':theStaff, 'saveMsg': saveMsg,
                               'theStaffBalances':theStaffBalances, 'theStaffSchedule':theStaffSchedule})

    except BadHeaderError:      #CAREFUL HERE - Broken Logic Block
        #return render(request, "LvApplications.html", {'form': form})
        return render(request, "lvApprovalDetail.html", {'form': form})


@login_required(login_url='/uzers/login/') #redirects
def lvBalance(request):
    try:
        uid = request.user.username[5:9]
        lvBalances = StaffMaster.objects.all()

        if 'deptIdX' in request.GET and int(request.GET['deptIdX']) > 0:
            #allStaff = StaffMaster.objects.filter(dept_id=request.GET['dept_id'])
            lvBalances = StaffMaster.objects.filter(dept_id=request.GET['deptIdX'])
        '''
        allApprovers =[]
        for astaff in allStaff:
            astaff.lvapprovers_set.all()
            allApprovers.append(astaff)
        '''
        return render(request, 'LvBalance.html',
                              {'lvBals': lvBalances, 'user_id': 0})
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
    return render(request, "lvBalance.html", {})


@login_required(login_url='/uzers/login/') #redirects
def lvBalanceEdit(request):
    if (request.method == 'GET') and ('BalAnnual' in request.GET):
        try:
            #staffid = form.cleaned_data['staffId']  #[5:9]
            nowx=datetime.datetime.now().date()

            balAnnual = request.GET['BalAnnual']
            balMaternity = request.GET['BalMaternity']
            balPaternity = request.GET['BalPaternity']
            balStudy = request.GET['BalStudy']
            balCompassion = request.GET['BalCompassion']
            balSick = request.GET['BalSick']

            staffid = request.GET['targetStaff']

            staffBals = LvBalances.objects.get(staff_id=staffid)
            staffBals.lv_annual= balAnnual
            staffBals.lv_maternity= balMaternity
            staffBals.lv_paternity= balPaternity
            staffBals.lv_study= balStudy
            staffBals.lv_compassion= balCompassion
            staffBals.lv_sick= balSick
            staffBals.save()

            myLog =  StaffUsers(staff_id=request.user.username[5:9], xtrainfo =request.user.username,
                                    xtrainfo2 = "Edt Balances "+ staffid + " at " + str(nowx))
            myLog.save()

            saveMessage="Saved New Balances for Staff Member " + staffid

            return render(request, 'lvBalanceEdit.html',
                                  {'saveMessage':saveMessage })
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
            #return redirect('success')
            #return render(request, "lvBalanceEdit.html", {'form': form})

    form = LvBalanceEdit()
    uid = request.user.username
    staffid = request.GET['staff_id']
    form.fields["staffId"].initial = staffid
    form.fields["staffId"].disabled = True
    #theStaff = StaffMaster.objects.get(staff_id = staffid[5:9])    # BE CAREFUL to update these lines of code
    theStaff = StaffMaster.objects.get(id = staffid)    # BE CAREFUL to update these lines of code

    staffBal = LvBalances.objects.get(staff_id=staffid)
    '''
    appova1Staff = StaffMaster.objects.get(staff_id = theApprovers.approver1_id[5:9])
    appova2Staff = StaffMaster.objects.get(staff_id = theApprovers.approver2_id[5:9])
    appova3Staff = StaffMaster.objects.filter(staff_id = theApprovers.approver3_id[5:9])
    '''

    return render(request, "lvBalanceEdit.html",
                  {'form':form, 'staff_id':staffid, 'theStaff':theStaff,
                   'staffBal':staffBal})


@login_required(login_url='/uzers/login/') #redirects
def lvBalanceAdd(request):

    sid = request.user.username[5:9]
    theStaff = StaffMaster.objects.get(staff_id = sid)
    lvBalanceNew = LvBalances(staff_id=theStaff, dept_id=0, lv_annual=1, lv_maternity=0, lv_paternity=14, lv_study=14, lv_compassion=7,lv_sick=9,lv_other=9,lv_other2=7)

    lvBalanceNew.save()
    return True

@login_required(login_url='/uzers/login/') #redirects
def lvBalanceInitialize(request):

    if "Initialize" in request.GET:      #ONLY IF Run With Initialize Parameter
        allStaff = StaffMaster.objects.filter(staff_id__gte=0)
        #allStaff = StaffMaster.objects.all()

        for astaff in allStaff:
            lvBalanceNew = LvBalances(staff_id=astaff, dept_id=0, lv_annual=26, lv_maternity=90, lv_paternity=0, lv_study=14, lv_compassion=7,lv_sick=60,lv_other=7,lv_other2=7)

            if astaff.sex == "F":
                lvBalanceNew = LvBalances(staff_id=astaff, dept_id=0, lv_annual=26, lv_maternity=90, lv_paternity=0, lv_study=14, lv_compassion=7,lv_sick=60,lv_other=7,lv_other2=7)
            if astaff.sex == "M":
                lvBalanceNew = LvBalances(staff_id=astaff, dept_id=0, lv_annual=26, lv_maternity=0, lv_paternity=14, lv_study=14, lv_compassion=7,lv_sick=60,lv_other=7,lv_other2=7)

            lvBalanceNew.save()

    return True

@login_required(login_url='/uzers/login/') #redirects
def lvStaffSummary(request):
    try:
        if request.method == 'GET':

            uid = request.user.username[5:9]
            sid = request.GET['staff_id']

        myUser = StaffMaster.objects.get(staff_id = uid)
        theStaff = StaffMaster.objects.get(staff_id = sid)

        lvCancelleds = LvApplications.objects.filter(staff_id = theStaff, cancelled=1)
        approvedLvs = LvApplications.objects.filter(staff_id = theStaff, approval=6)
        pendingLvs = LvApplications.objects.filter(staff_id = theStaff, approval__gt=6, cancelled=0)
        lvSchedule = LvSchedules.objects.filter(staff_id = theStaff).first
        theStaffBalances = LvBalances.objects.filter(staff_id = theStaff).first

        return render(request, 'lvStaffSummary.html',
                              {'pendingLvs': pendingLvs,'lvCancelleds': lvCancelleds,'approvedLvs': approvedLvs,
                               'lvSchedule':lvSchedule, 'theStaff':theStaff, 'theStaffBalances':theStaffBalances})

    except BadHeaderError:

        return render(request, "lvApprovals.html", { })

@login_required(login_url='/uzers/login/') #redirects
def lvCentral(request):
    try:
        #lvAllUsers = User.objects.all()
        uid = request.user.username[5:9]

        lvAllUsers = StaffMaster.objects.all()

        if 'dept_id' in request.GET:        #int(deptid) > 0:
            deptid = request.GET['dept_id']
            lvAllUsers = StaffMaster.objects.filter(dept_id=deptid)
        if 'dept_id' in request.GET and int(request.GET['dept_id']) == 0:
            #deptid = request.GET['dept_id']
            lvAllUsers = StaffMaster.objects.all()
        if 'txt_search' in request.GET:
            txtsch = request.GET['txt_search']
            lvAllUsers = StaffMaster.objects.filter(first_name__icontains=txtsch )| StaffMaster.objects.filter(last_name__icontains=txtsch)

        # CAREFUL boss Level In Next Line Not Appropriate
        return render(request, 'lvCentral.html',
                              {'lvAllUsers': lvAllUsers, 'boss_lvl':9, 'user_id': uid})
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
        #return redirect('success')
        #return render(request, "LvApplications.html", {'form': form})
    return render(request, "lvCentral.html", {'form': form})


@login_required(login_url='/uzers/login/') #redirects
def lvDefaultView(request):

    uid = request.user.username[5:9]
    uidfull = request.user.username

    theStaffBalances = LvBalances.objects.filter(staff_id = uid)   #CAREFUL , Repeated further Down
    if len(theStaffBalances) < 1:  #if False: #
        lvBalanceAdd(request)

    # print user.username, user.get_full_name(), user.email

    try:
        if request.method == 'GET':

            theStaff = StaffMaster.objects.get(staff_id = uid)
            myLvApps = LvApplications.objects.filter(staff_id = theStaff).order_by('-approval')
            theStaffBalances = LvBalances.objects.filter(staff_id = theStaff).first
            theStaffSchedule = LvSchedules.objects.filter(staff_id = theStaff, reschedule=0, sched_status__gt=5).first     # BE CAREFUL

            # CAREFUL APPROVERS Checked  Here

            schedboss_lvl=0
            boss_lvl = 0
            appns_count=0
            scheds_count=0

            approva1 = LvApplications.objects.filter(approver1_id=uid, cancelled=0, approval=9 )  #Add Sched_Status + UserId ???
            if approva1:
                boss_lvl=9;     appns_count=appns_count+len(approva1)
            approva2 = LvApplications.objects.filter(approver2_id=uid, cancelled=0, approval=8)  #Add Sched_Status + UserId ???
            if approva2:
                boss_lvl=8;     appns_count=appns_count+len(approva2)
            approva3 = LvApplications.objects.filter(approver3_id=uid, cancelled=0, approval=7)  #Add Sched_Status + UserId ???
            if approva3:
                boss_lvl=7;     appns_count=appns_count+len(approva3)


            # FOR Leave Schedules
            approvaScd = LvSchedules.objects.filter(approver_id=uid, reschedule=0, sched_status=9)  #Add Sched_Status + UserId ???
            if approvaScd:
                schedboss_lvl=1;     scheds_count=len(approvaScd)


            lvApps = LvApplications.objects.filter(staff_id=uid)  # BE CAREFUL URGENT WITH GTE and LTE and LT and GT
            return render(request, 'lvDefaultView.html',
                                          {'appns_count':appns_count,'scheds_count':scheds_count,'lvApps': lvApps,'theStaff': theStaff,'myLvApps': myLvApps,
                                           'theStaffSchedule':theStaffSchedule,'theStaffBalances':theStaffBalances,
                                           'boss_lvl': boss_lvl,'schedboss_lvl':schedboss_lvl})

    except BadHeaderError:
        return HttpResponse('Invalid header found.')
        #return redirect('success')

    myLvApps = LvApplications.objects.filter(staff_id=uid).order_by('-approval')

    theStaff = StaffMaster.objects.get(staff_id = uid)
    theStaffBalances = LvBalances.objects.get(staff_id = uid)
    theStaffSchedule = LvSchedules.objects.get(staff_id = uid)

    # BE CAREFUL WITH GET Variable next line
    return render(request, "lvDefaultView.html",
                  {'user_id':uid, 'theStaff': theStaff,'myLvApps': myLvApps,'theStaffSchedule':theStaffSchedule,'theStaffBalances':theStaffBalances})
    #use redirect to another template for those that are approvers


@login_required(login_url='/uzers/login/') #redirects
def lvApprovers(request):
    try:
        uid = request.user.username[5:9]
        allStaff = StaffMaster.objects.all()

        if 'dept_id' in request.GET and int(request.GET['dept_id']) > 0:
            allStaff = StaffMaster.objects.filter(dept_id=request.GET['dept_id'])

        allApprovers =[]
        for astaff in allStaff:
            astaff.lvapprovers_set.all()
            allApprovers.append(astaff)

        return render(request, 'lvApprovers.html',
                              {'allApprovers': allApprovers, 'boss_lvl':9, 'user_id': uid})
    except BadHeaderError:
        return HttpResponse('Invalid header found.')

    return render(request, "lvApprovers.html", {'form': form})

@login_required(login_url='/uzers/login/') #redirects
def lvApproverEdit(request):
    if (request.method == 'GET') and ('Approva1' in request.GET):
        try:
            #staffid = form.cleaned_data['staffId']  #[5:9]
            nowx=datetime.datetime.now().date()

            approva01 = request.GET['Approva1']
            approva02 = request.GET['Approva2']
            approva03 = request.GET['Approva3']

            if request.GET['Approva1'] == '':   approva01 = '000'
            if request.GET['Approva2'] == '':   approva02 = '000'
            if request.GET['Approva3'] == '':   approva03 = '000'

            staffid = request.GET['targetStaff']

            theApprova = LvApprovers.objects.get(staff_id=staffid)

            theApprova.approver1_id= 'ZUSR_'+ str(approva01)
            theApprova.approver2_id= 'ZUSR_'+ str(approva02)
            theApprova.approver3_id= 'ZUSR_'+ str(approva03)
            theApprova.save()

            myLog =  StaffUsers(staff_id=request.user.username[5:9], xtrainfo =request.user.username,
                                    xtrainfo2 = "Ed Approvers "+ staffid + " at " + str(nowx))
            myLog.save()

            #update pending LV Applications with new approvers
            lvApps = LvApplications.objects.filter(staff_id=staffid)
            for lvAppn in lvApps:
                lvAppn.approver1_id = str(approva01)
                lvAppn.approver2_id = str(approva02)
                lvAppn.approver3_id = str(approva03)
                lvAppn.save()

            myLog =  StaffUsers(staff_id=request.user.username[5:9], xtrainfo =request.user.username,
                                    xtrainfo2 = "Updated LvAppns "+ staffid + " at " + str(nowx))
            myLog.save()

            saveMessage="Saved Approvers for Staff Member " + staffid

            return render(request, 'lvApproverEdit.html',
                                  {'saveMessage':saveMessage })
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
            #return redirect('success')
            #return render(request, "LvApplications.html", {'form': form})

    form = LvApproverEdit()
    uid = request.user.username
    staffid = request.GET['staff_id']
    form.fields["staffId"].initial = staffid
    form.fields["staffId"].disabled = True
    #theStaff = StaffMaster.objects.get(staff_id = staffid[5:9])    # BE CAREFUL to update these lines of code
    theStaff = StaffMaster.objects.get(id = staffid)    # BE CAREFUL to update these lines of code

    theApprovers = LvApprovers.objects.get(staff_id=staffid)
    appova1Staff = StaffMaster.objects.get(staff_id = theApprovers.approver1_id[5:9])
    appova2Staff = StaffMaster.objects.get(staff_id = theApprovers.approver2_id[5:9])
    appova3Staff = StaffMaster.objects.filter(staff_id = theApprovers.approver3_id[5:9])

    return render(request, "lvApproverEdit.html",
                  {'form':form, 'staff_id':staffid, 'theStaff':theStaff,
                   'appova1Staff':appova1Staff, 'appova2Staff':appova2Staff, 'appova3Staff':appova3Staff })


@login_required(login_url='/uzers/login/') #redirects
def lvApproversCopy(request):
    if (request.method == 'GET') and ('Approva1' in request.GET):
        try:
            #staffid = form.cleaned_data['staffId']  #[5:9]
            nowx=datetime.datetime.now().date()

            approva01 = request.GET['Approva1']
            approva02 = request.GET['Approva2']
            approva03 = request.GET['Approva3']

            if request.GET['Approva1'] == '':   approva01 = '000'
            if request.GET['Approva2'] == '':   approva02 = '000'
            if request.GET['Approva3'] == '':   approva03 = '000'

            targetStaff1 = request.GET['targetStaff1']
            targetStaff2 = request.GET['targetStaff2']
            targetStaff3 = request.GET['targetStaff3']

            targetsx = []
            if 'targetStaff1' in request.GET and request.GET['targetStaff1'] != '':
                staffid1 = 'ZUSR_'+targetStaff1; targetsx.append(staffid1)
            if 'targetStaff2' in request.GET and request.GET['targetStaff2'] != '':
                staffid2 = 'ZUSR_'+targetStaff2; targetsx.append(staffid2)
            if 'targetStaff3' in request.GET and request.GET['targetStaff3'] != '':
                staffid3 = 'ZUSR_'+targetStaff3; targetsx.append(staffid3)

            for aStaff in targetsx:
                theApprova = LvApprovers.objects.get(first_name=aStaff)

                theApprova.approver1_id= 'ZUSR_'+ str(approva01)
                theApprova.approver2_id= 'ZUSR_'+ str(approva02)
                theApprova.approver3_id= 'ZUSR_'+ str(approva03)

                theApprova.save()

                myLog =  StaffUsers(staff_id=request.user.username[5:9], xtrainfo =request.user.username,
                                    xtrainfo2 = "Cpd Approvers "+ aStaff + " at " + str(nowx))
                myLog.save()


            saveMessage="Saved Approvers for Staff Members "

            return render(request, 'lvApproversCopy.html',
                                  {'saveMessage':saveMessage })
        except BadHeaderError:
            return HttpResponse('Invalid header found.')

    staffid = request.GET['staff_id']

    #theStaff = StaffMaster.objects.get(staff_id = staffid)    # BE CAREFUL to update these lines of code
    theStaff = StaffMaster.objects.get(id = staffid)    # BE CAREFUL to update these lines of code
    theApprovers = LvApprovers.objects.get(staff_id=staffid)
    appova1Staff = StaffMaster.objects.get(staff_id = theApprovers.approver1_id[5:9])
    appova2Staff = StaffMaster.objects.get(staff_id = theApprovers.approver2_id[5:9])
    appova3Staff = StaffMaster.objects.filter(staff_id = theApprovers.approver3_id[5:9])

    return render(request, "lvApproversCopy.html",
                  {'staff_id':staffid, 'theStaff':theStaff,
                   'appova1Staff':appova1Staff, 'appova2Staff':appova2Staff, 'appova3Staff':appova3Staff })

@login_required(login_url='/uzers/login/') #redirects
def lvApplicationList(request):
    try:
        if 'lvTypeX' in request.GET:
            lvTypex  = request.GET['lvTypeX']
            deptidx  = request.GET['deptIdX']
            appvox  = request.GET['approvalX']

        xstaff_id = request.user.username[5:9]
        myUser = StaffMaster.objects.get(staff_id = xstaff_id)    # BE CAREFUL to update these lines of code

        myX=999;
        lvRpt=0

        if 'lvTypeX' in request.GET and (int(lvTypex)==0) and (int(deptidx)==0) and (int(appvox)==0):
            lvAppList = LvApplications.objects.filter(approval__gte=4).order_by('-lv_startdate')     #lvCancelledAMonth

        if 'lvTypeX' in request.GET and (int(lvTypex)==0) and (int(deptidx)==0) and (int(appvox) > 0):
            lvAppList = LvApplications.objects.filter(approval=appvox).order_by('-lv_startdate')     #lvCancelledAMonth

        if 'lvTypeX' in request.GET and (int(lvTypex)==0) and (int(deptidx) > 0) and (int(appvox)==0):
            lvAppList = LvApplications.objects.filter(dept_id=deptidx).order_by('-lv_startdate')     #lvCancelledAMonth

        if 'lvTypeX' in request.GET and (int(lvTypex)> 0) and (int(deptidx)==0) and (int(appvox)==0):
            lvAppList = LvApplications.objects.filter(lv_type=lvTypex).order_by('-lv_startdate')     #lvCancelledAMonth

        if 'lvTypeX' in request.GET and (int(lvTypex) > 0) and (int(deptidx)==0) and (int(appvox)> 0):
            lvAppList = LvApplications.objects.filter(lv_type=lvTypex, approval=appvox).order_by('-lv_startdate')     #lvCancelledAMonth

        if 'lvTypeX' in request.GET and (int(lvTypex)> 0) and (int(deptidx)> 0) and (int(appvox)==0):
            lvAppList = LvApplications.objects.filter(lv_type=lvTypex, dept_id=deptidx).order_by('-lv_startdate')     #lvCancelledAMonth

        if 'lvTypeX' in request.GET and (int(lvTypex) > 0) and (int(deptidx)> 0) and (int(appvox)> 0):
            lvAppList = LvApplications.objects.filter(lv_type=lvTypex, dept_id=deptidx,approval=appvox ).order_by('-lv_startdate')     #lvCancelledAMonth

        '''
        if 'txt_search' in request.GET:
            txtsch = request.GET['txt_search']
            lvAppList = LvApplications.objects.filter(first_name__icontains=txtsch )| LvApplications.objects.filter(last_name__icontains=txtsch)
        '''

        #tblHolidays = LvHoliday.objects.all().values('lv_holidate')
        #myStaffs = LvApplications.objects.all().values('staff_id_id');

        rptMessage4 ='Leave Applications Selection'

        return render(request, 'lvApplicationList.html',
                          {'lvApplicationList1': lvAppList, 'myUser':myUser, 'lvTypex':lvTypex,'deptidx':deptidx, 'appvox':appvox })
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
        #return redirect('success')

    return render(request, 'lvApplicationList.html',
                  {'lvApplicationList1': lvAppList,'myUser':myUser, 'lvTypex':lvTypex,'deptidx':deptidx, 'appvox':appvox })


@login_required(login_url='/uzers/login/') #redirects
def lvApplicationsDept(request):
    try:
        if 'lvTypeX' in request.GET:
            lvTypex  = request.GET['lvTypeX']
            appvox  = request.GET['approvalX']

        xstaff_id = request.user.username[5:9]
        myUser = StaffMaster.objects.get(staff_id = xstaff_id)    # BE CAREFUL to update these lines of code
        deptidx = myUser.dept_id
        if int(deptidx) < 1:
            deptidx = 0

        #hdept = LvDepartment.objects.get(dept_id=str(myStaff.dept_id))
        #hodds = hdept.dept_hod

        myX=999;
        lvRpt=0


        if 'lvTypeX' in request.GET and (int(lvTypex)==0) and (int(appvox)==0): # and (int(deptidx) > 0):
            lvAppList = LvApplications.objects.filter(dept_id=deptidx).order_by('-lv_startdate')     #lvCancelledAMonth

        if 'lvTypeX' in request.GET and (int(lvTypex)==0) and (int(appvox)> 0): # and (int(deptidx) > 0):
            lvAppList = LvApplications.objects.filter(dept_id=deptidx, approval=appvox).order_by('-lv_startdate')     #lvCancelledAMonth

        if 'lvTypeX' in request.GET and (int(lvTypex)> 0) and (int(appvox)==0): # and (int(deptidx)> 0):
            lvAppList = LvApplications.objects.filter(dept_id=deptidx, lv_type=lvTypex).order_by('-lv_startdate')     #lvCancelledAMonth

        if 'lvTypeX' in request.GET and (int(lvTypex) > 0) and (int(appvox)> 0): # and (int(deptidx)> 0):
            lvAppList = LvApplications.objects.filter(dept_id=deptidx, lv_type=lvTypex, approval=appvox ).order_by('-lv_startdate')     #lvCancelledAMonth

        rptMessage4 ='Leave Applications Selection'

        return render(request, 'lvApplicationsDept.html',
                          {'lvAppList': lvAppList, 'myUser':myUser, 'lvTypex':lvTypex,'deptidx':deptidx, 'appvox':appvox })
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
        #return redirect('success')

    return render(request, 'lvApplicationsDept.html',
                  {'lvAppList': lvAppList,'myUser':myUser, 'lvTypex':lvTypex,'deptidx':deptidx, 'appvox':appvox })


def successView(request):
    return HttpResponse('Success! Thank you for your message.')

def date_by_adding_business_days(from_date, add_days, lvtype, myHolidays):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += datetime.timedelta(days=1)
        weekday = current_date.weekday()

        # if (weekday >= 5) MEANS ... sunday = 6, Maternity (lvtype 2) counts weekends too
        if (weekday >= 5) and (int(lvtype) != 2) and (int(lvtype) != 3):
            continue
        if current_date in myHolidays:
            continue
        business_days_to_add -= 1
    return current_date

def deductLeave(lid, staff):        # This Function is Not Used or Called, Code is in the views

    lvAppn = LvApplications.objects.get(id=lid)
    lvBalan = LvBalances.objects.filter(staff_id=staff)

    if lvAppn.lv_type ==1:
        lvBalan.lv_annual = lvBalan.lv_annual - lvAppn.lv_days
    if lvAppn.lv_type ==2:
        lvBalan.lv_maternity = lvBalan.lv_maternity - lvAppn.lv_days
    if lvAppn.lv_type ==3:
        lvBalan.lv_paternity = lvBalan.lv_paternity - lvAppn.lv_days
    if lvAppn.lv_type ==4:
        lvBalan.lv_study = lvBalan.lv_study - lvAppn.lv_days
    if lvAppn.lv_type ==5:
        lvBalan.lv_compassion = lvBalan.lv_compassion - lvAppn.lv_days
    if lvAppn.lv_type ==6:
        lvBalan.lv_sick = lvBalan.lv_sick - lvAppn.lv_days

    return True

def notifyEmail(staff01, appova1, appova2, appova3, action):

    myStaff = StaffMaster.objects.get(staff_id=staffid0).email
    myAppova1 = StaffMaster.objects.get(staff_id=staffid1).email
    myAppova2 = StaffMaster.objects.get(staff_id=staffid2).email

    emailMsg = "Email Notification \n"
    emailMsg1 = emailMsg + "Leave Application Was Successfully Submitted"
    emailMsg2 = emailMsg + "Leave Application From Staff Requires Your Attention"
    emailMsg3 = emailMsg + "Leave Applications Are Pending Your Approval"

    # sendThe Email ()

################################


@login_required(login_url='/uzers/login/') #redirects
def lvScheduleShow(request):

    if request.method == 'GET':
        form = LvScheduleForm()
    else:
        form = LvScheduleForm(request.POST)
        if form.is_valid():

            #staffid = form.cleaned_data['staff_id']

            staffid = request.user.username[5:9]
            s1_start = form.cleaned_data['sched1_start']
            s2_start = form.cleaned_data['sched2_start']
            s3_start = form.cleaned_data['sched3_start']
            s4_start = form.cleaned_data['sched4_start']
            s5_start = form.cleaned_data['sched5_start']


            s1_days = form.cleaned_data['sched1_days']
            s2_days = form.cleaned_data['sched2_days']
            s3_days = form.cleaned_data['sched3_days']
            s4_days = form.cleaned_data['sched4_days']
            s5_days = form.cleaned_data['sched5_days']

            if type(s3_days) != int: s3_days = 0
            if type(s4_days) != int: s4_days = 0
            if type(s5_days) != int: s5_days = 0

            schedText = form.cleaned_data['lv_description']


            overlapp = 0
            if s1_start + datetime.timedelta(s1_days) > s2_start and s1_start < s2_start:
                overlapp = 2

            if 'sched3_start' in request.POST and type(s3_start) == datetime.date:
                if s2_start + datetime.timedelta(s2_days) > s3_start and s2_start < s3_start:
                    overlapp = 3

            if 'sched3_start' in request.POST and 'sched4_start' in request.POST and type(s4_start) == datetime.date:
                if s3_start + datetime.timedelta(s3_days) > s4_start and s3_start < s4_start:
                    overlapp = 4
            if 'sched4_start' in request.POST and 'sched5_start' in request.POST and type(s5_start) == datetime.date:
                if s4_start + datetime.timedelta(s4_days) > s5_start and s4_start < s5_start:
                    overlapp = 5

            if s1_days + s2_days + s3_days + s4_days + s5_days > 26:    # CAREFUL not exceed LvBalances
                overlapp = 6

            #overlapp = "The Dates Are OverLapping At Block " + str(overlapp)

            if overlapp == 0:

                lvStaffer = StaffMaster.objects.get(staff_id=request.user.username[5:9])
                lvApprovers = LvApprovers.objects.get(staff_id=lvStaffer.id)

                lvSched = LvSchedules(staff_id=lvStaffer, dept_id=lvStaffer.dept_id, sched1_start=s1_start, sched1_days=s1_days,
                                          sched2_start=s2_start, sched2_days=s2_days, sched3_start=s3_start,sched3_days=s3_days,
                                          sched4_start=s4_start,sched4_days=s4_days,sched5_start=s5_start,sched5_days=s5_days,
                                          lv_description=schedText, lv_comments='blank',sched_status=9,
                                          approver_id=lvApprovers.approver1_id[5:9],
                                          approval_dt='2000-01-10',
                                          reschedule=0, returned_dt='2000-02-01', returner_id='0')

                lvSched.save();
                schedExist=1
                #schedExist=0        # BE CAREFUL toremove this
                saveMsg="You Have Just Submitted A Leave Schedule. Notifications Will Be sent on Approvals"
                #notifyEmail(staff01, appova1, appova2, appova3, action)

                myUser = StaffMaster.objects.get(staff_id = staffid)

                theStaff = StaffMaster.objects.get(staff_id = staffid)
                theStaffBalances = LvBalances.objects.filter(staff_id = staffid).first
                theStaffSchedule = LvSchedules.objects.filter(staff_id = theStaff.id, reschedule = 0)
                theStaffSchedules = LvSchedules.objects.filter(staff_id = theStaff.id).order_by('-sched_status')

                form = LvScheduleForm()

                return redirect('/lvScheduleShow')
            else:
                #overlapp = 1
                #overlapp = " *** Your Leave Dates Seem Overlapping: Please Check Them Again "
                uid = request.user.username[5:9]
                theStaff = StaffMaster.objects.get(staff_id = uid)
                theStaffBalances = LvBalances.objects.filter(staff_id = uid).first
                theStaffSchedule =  LvSchedules.objects.filter(staff_id =theStaff.id, reschedule = 0)     #BE CAREFUL WHY GET, NOT FILTER
                theStaffSchedules = LvSchedules.objects.filter(staff_id = uid).order_by('-sched_status')     #BECAREFUL

                lvSchedLike = LvSchedules.objects.filter(staff_id=theStaff.id, sched_status__gt=6)
                if len(lvSchedLike) > 0:
                    schedExist=1
                else:
                    schedExist=0

                return render(request, 'lvScheduleShow.html',
                  {'theStaffSchedules': theStaffSchedules,'theStaffSchedule':theStaffSchedule,'theStaffBalances':theStaffBalances,
                   'schedExist':schedExist,'overlapp':overlapp,'theStaff': theStaff,'form': form})

    #return redirect('/lvScheduleShow')

    #overlapp = -1
    uid = request.user.username[5:9]
    theStaff = StaffMaster.objects.get(staff_id = uid)
    theStaffBalances = LvBalances.objects.filter(staff_id = theStaff.id).first
    theStaffSchedule =  LvSchedules.objects.filter(staff_id = theStaff.id, reschedule = 0).first     #BE CAREFUL WHY GET, NOT FILTER
    theStaffSchedules = LvSchedules.objects.filter(staff_id = theStaff.id).order_by('-sched_status')     #BECAREFUL

    lvSchedLike = LvSchedules.objects.filter(staff_id=theStaff.id, sched_status__gt=6)
    if len(lvSchedLike) > 0:
        schedExist=1
    else:
        schedExist=0

    return render(request, 'lvScheduleShow.html',
                  {'theStaffSchedules': theStaffSchedules,'theStaffSchedule':theStaffSchedule,'theStaffBalances':theStaffBalances,
                   'schedExist':schedExist,'theStaff': theStaff,'form': form})


@login_required(login_url='/uzers/login/') #redirects
def lvSchedApproval(request):
    try:
        if request.method == 'GET':

            uid = request.user.username[5:9]
            lid = request.GET['id']
            boss_lvl=0

            approva1 = LvSchedules.objects.filter(approver_id=uid, reschedule=0)  #Add Sched_Status + UserId ???
            if approva1:
                boss_lvl=9

            schedApprovalMsg=''		# BE CAREFUL

            if uid and lid:
                if lid > '0':
                    #lid = request.GET['id']
                    llvl = request.GET['lvl']

                    now=datetime.datetime.now()
                    mynow=now.strftime("%Y-%m-%d")

                    lvSched = LvSchedules.objects.get(id=lid)

                    if llvl=='1':
                        lvSched.sched_status=6; lvSched.approver_id=uid; lvSched.approval_dt=mynow;
                        schedApprovalMsg = 'You Have just Approved A Leave Schedule'
                    if llvl=='c':
                        lvSched.sched_status=5; lvSched.reschedule=1; lvSched.returned_dt=mynow
                        schedApprovalMsg = 'You Have just Cancelled A Leave Schedule'

                    lvSched.save()
                    #notifyEmail(staff01, appova1, appova2, appova3, action)


        #BE CAREFUL to Improve Next Query
        #lvScheds = LvSchedule.objects.all()
        myUser = StaffMaster.objects.get(staff_id = uid)
        myLvBals = LvBalances.objects.filter(staff_id = uid)

        lvScheds = LvSchedules.objects.filter(approver_id=uid, sched_status=boss_lvl, reschedule=0) #and LvSchedule.objects.filter(lv_days__gt=4)

        return render(request, 'lvSchedApproval.html',
                              {'lvScheds': lvScheds, 'myLvBals':myLvBals,'user_id': uid, 'myUser':myUser,'boss_lvl':boss_lvl,'schedApprovalMsg':schedApprovalMsg})
    except BadHeaderError:
        return render(request, "lvSchedApproval.html", {'form': form})


@login_required(login_url='/uzers/login/') #redirects
def lvSchedApprovalDetail(request):
    try:
        if request.method == 'GET':

            uid = request.user.username[5:9]
            lid = request.GET['id']
            saveMsg =''

            boss_lvl=0

            approva1 = LvSchedules.objects.filter(approver_id=uid, reschedule=0)  #Add Sched_Status + UserId ???
            if approva1:
                boss_lvl=9

            if uid and lid:
                #lid = request.GET['id']
                llvl = request.GET['lvl']

                now=datetime.datetime.now()

                lvSched = LvSchedules.objects.get(id=lid)
                mynow=now.strftime("%Y-%m-%d")

                if llvl=='0': dummy=''
                if llvl=='1':
                    lvSched.sched_status=8; lvSched.approver_id=uid; lvSched.approval_dt=mynow;
                    saveMsg="You Have Just Approved A Leave Schedule"

                if llvl=='c':
                    lvSched.sched_status=5; lvSched.reschedule=1; lvSched.returned_dt=mynow
                    saveMsg="You Have Just Cancelled A Leave Schedule"

                lvSched.save()
                #notifyEmail(staff01, appova1, appova2, appova3, action)


        #BE CAREFUL to Improve Next Query
        uid = request.user.username[5:9]
        lid = request.GET['id']
        myUser = StaffMaster.objects.get(staff_id = uid)
        theStaffSchedule = LvSchedules.objects.get(id=lid)
        theStaff = StaffMaster.objects.get(id = theStaffSchedule.staff_id_id)

        allStaffScheds = LvSchedules.objects.filter(staff_id = theStaff)
        theStaffBalances = LvBalances.objects.filter(staff_id = theStaff).first
        lvholidays = LvHoliday.objects.all()

        return render(request, 'lvSchedApprovalDetail.html', {'allStaffScheds': allStaffScheds,'theStaffBalances': theStaffBalances,
                               'lvholidays':lvholidays,'theStaff':theStaff, 'saveMsg': saveMsg,
                               'theStaffSchedule':theStaffSchedule, 'boss_lvl':boss_lvl})

    except BadHeaderError:
        return render(request, "lvSchedApprovalDetail.html", {'form': form})


@login_required(login_url='/uzers/login/') #redirects
def lvScheduleList(request):
    try:
        uid = request.user.username[5:9]

        deptidx  = request.GET['deptIdX']
        appvox  = request.GET['approvalX']

        if (int(deptidx)==0) and (int(appvox)==0):
            lvScheds = LvSchedules.objects.filter(sched_status__gt=4)     #lvCancelledAMonth

        if (int(deptidx)==0) and (int(appvox) > 0):
            lvScheds = LvSchedules.objects.filter(sched_status=appvox)     #lvCancelledAMonth

        if (int(deptidx)> 0) and (int(appvox)==0):
            lvScheds = LvSchedules.objects.filter(dept_id=deptidx)     #lvCancelledAMonth

        if (int(deptidx)> 0) and (int(appvox)> 0):
            lvScheds = LvSchedules.objects.filter(dept_id=deptidx, sched_status=appvox)     #lvCancelledAMonth

            rptMessage ='Annual Leave Schedules  Selection'

        return render(request, 'lvScheduleList.html',
                                      {'lvScheds': lvScheds })
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
        #return redirect('success')

    return render(request, "lvScheduleList.html", {})

def lvCreateUsers(request):
    try:
        if "Initialize" in request.GET:      #ONLY IF Run With Initialize Parameter
            lvStaff = StaffMaster.objects.filter(id__gte=2)

            for myStaff in lvStaff:
                myUser = User(password='fd87g5w67ae35j543',last_login='1900-01-01',is_superuser=0,
                                    username='ZUSR_'+ str(myStaff.staff_id),first_name=myStaff.first_name, last_name=myStaff.last_name,
                                    email=myStaff.email, is_staff=0,is_active=0,date_joined='1900-01-01')

                myUser.set_password('password99')
                myUser.save()           #BE CAREFUL , Duplicates Cause Faulure

            saveMsg="You Have Just Submitted User Creation Action"
            return render(request, 'lvCreateUsers.html')

    except BadHeaderError:
        return HttpResponse('Invalid header found.')
        #return redirect('success')

    return render(request, "lvCreateUsers.html", {})

def lvMakeApprovers(request):
    try:
        if "Initialize" in request.GET:      #ONLY IF Run With Initialize Parameter
            lvStaff = StaffMaster.objects.filter(staff_id__gte=0)

            for myStaff in lvStaff:
                hdept = LvDepartment.objects.get(dept_id=str(myStaff.dept_id))
                hodds = hdept.dept_hod
                '''
                myAppova = LvApprovers(staff_id=myStaff.staff_id,first_name=myStaff.first_name,
                                       created_at='1900-01-01', approver1_id='ZUSR_'+hodds, approver2_id='ZUSR_4',
                                       approver3_id='708')
                '''

                myAppova = LvApprovers(staff_id_id=myStaff.id, first_name='ZUSR_'+ myStaff.staff_id,
                                       created_at='1900-01-01', approver1_id='ZUSR_'+hodds, approver2_id='ZUSR_4',
                                       approver3_id='ZUSR_708')

                myAppova.save()        #BE CAREFUL , Duplicates Cause Failure

            saveMsg="You Have Just Submitted Leave Approvers Action"
            return render(request, 'lvMakeApprovers.html')

    except BadHeaderError:
        #return HttpResponse('Invalid header found.')
        return render(request, "lvMakeApprovers.html", {})

    return render(request, "lvMakeApprovers.html", {})


@login_required(login_url='/uzers/login/') #redirects
def lvLogsView(request):
    try:
        uid = request.user.username[5:9]
        lvLogs = StaffUsers.objects.all()

        '''
        if 'deptIdX' in request.GET and int(request.GET['deptIdX']) > 0:
            #allStaff = StaffMaster.objects.filter(dept_id=request.GET['dept_id'])
            lvBalances = StaffMaster.objects.filter(dept_id=request.GET['deptIdX'])
        '''

        return render(request, 'LvLogsView.html',
                              {'lvLogs': lvLogs, 'user_id': 0})
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
    return render(request, "LvLogsView.html", {})


# ===========================  EXAMS INITIAL SCRIPTS

def xamClassXForm(request):
    try:
        #lvAllUsers = User.objects.all()
        uid = request.user.username[5:9]
        xsize = request.GET['size']

        allStudents = LvApprovers.objects.all()

        if int(xsize) > 0:
            allStudents = LvApprovers.objects.filter(id__lte=xsize)

        # CAREFUL boss Level In Next Line Not Appropriate
        return render(request, 'xamClassXForm.html',
                              {'allApprovers':allStudents , 'boss_lvl':9, 'user_id': uid})
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
        #return redirect('success')
        #return render(request, "LvApplications.html", {'form': form})
    return render(request, "xamClassXForm.html", {'form': form})

#@login_required(login_url='/uzers/login/') #redirects
def xamClassMarksPost(request):
    if request.method == 'GET':
        try:
            if True:  #form.is_valid():
                approva01 = request.GET['txtONE']
                approva02 = request.GET['txtTWO']

                theClass = LvApprovers.objects.filter(id__lte=1475)
                #Recreate The IDs and Names of Text boxes , Capture and SAVE ! DONE

                myClass = []

                for myStudent in theClass:

                    sid1a=myStudent.staff_id + ''
                    sid1=myStudent.staff_id + '_25FGD34'
                    sid2=myStudent.staff_id + '_54GS334'
                    sid3=myStudent.staff_id + '_6765D34'
                    sid4=myStudent.staff_id + '_786DH34'

                    myMarks = []
                    myMarks.append(sid1a)
                    myMarks.append(request.GET[sid1])
                    myMarks.append(request.GET[sid2])
                    myMarks.append(request.GET[sid3])
                    myMarks.append(request.GET[sid4])

                    myClass.append(myMarks)

            saveMessage="Displaying Entered Exam Marks "

            pdfprint(request)

        except BadHeaderError:
            return HttpResponse('Invalid header found.')
            #return redirect('success')
            #return render(request, "LvApplications.html", {'form': form})

def pdfprint(request):

    c = canvas.Canvas("hello.pdf")
    c.drawString(100,750,"Welcome to Reportlab!")
    c.save()

    '''
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")
    p.drawString(100, 100, "Hello world.")
    p.drawString(100, 140, "Welcome Solomon Chege.")
    p.drawString(100, 180, "PDF on Python With Django.")
    p.drawString(100, 200, "Getting Started With Exams Processing System.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response
    '''
