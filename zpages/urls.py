# pages/urls.py
from django.urls import path

from .views import HomePageView, AboutPageView, lvDefaultView, successView
from .views import lvApplications, lvApproval, lvApprovalDetail, lvBalance
from .views import lvScheduleShow, lvSchedApproval, lvSchedApprovalDetail
from .views import lvScheduleList, lvStaffSummary,lvApplicationList, lvApplicationsDept

from .views import lvCreateUsers,lvCentral, lvApprovers,lvBalanceAdd
from .views import lvMakeApprovers, lvApproverEdit, lvApproversCopy
from .views import lvBalanceEdit #, lvBalanceCopy

from .views import lvLogsView, xamClassXForm, xamClassMarksPost


urlpatterns = [
    path('', HomePageView, name='home'),
    path('about', AboutPageView.as_view(), name='about'),
    path('defaultView/', lvDefaultView, name='lvDefaultView'),

    path('success/', successView, name='success'),
    path('lvApplied/', lvApplications, name='lvApplications'),
    path('lvApplicationList/', lvApplicationList, name='lvApplicationList'),
    path('ApplicationsDept/', lvApplicationsDept, name='lvApplicationsDept'),

    path('lvApproval/', lvApproval, name='lvApproval'),
    path('lvApprovalDetail/', lvApprovalDetail, name='lvApprovalDetail'),

    path('lvCentral/', lvCentral, name='lvCentral'),
    path('Approvers/', lvApprovers, name='lvApprovers'),

    path('lvBalance/', lvBalance, name='lvBalance'),
    path('lvBalanceAdd/', lvBalanceAdd, name='lvBalanceAdd'),
    path('BalanceEdit/', lvBalanceEdit, name='lvBalanceEdit'),
    path('lvStaffSummary/', lvStaffSummary, name='lvStaffSummary'),

    path('lvScheduleList/', lvScheduleList, name='lvScheduleList'),
    #path('lvMySchedule/', lvMySchedule, name='lvMySchedule'),
    path('lvScheduleShow/', lvScheduleShow, name='lvScheduleShow'),


    path('lvSchedApproval/', lvSchedApproval, name='lvSchedApproval'),
    path('lvSchedApprovalDetail/', lvSchedApprovalDetail, name='lvSchedApprovalDetail'),

    path('CreateUsers/', lvCreateUsers, name='lvCreateUsers'),
    path('LogsView/', lvLogsView, name='lvLogsView'),

    path('MakeApprovers/', lvMakeApprovers, name='lvMakeApprovers'),
    path('ApproverEdit/', lvApproverEdit, name='ApproverEdit'),
    path('ApproversCopy/', lvApproversCopy, name='ApproversCopy'),

    path('ClassXForm/', xamClassXForm, name='ClassXForm'),
    path('ClassMarksPost', xamClassMarksPost, name='ClassMarksPost'),

]
