# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class StaffMaster(models.Model):
	staff_id  = models.CharField(max_length=10,null=False)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	sex = models.CharField(max_length=1)
	birth_date = models.DateField()
	dept_id  = models.IntegerField()
	campus_id  = models.IntegerField()
	phone_number = models.CharField(max_length=30)
	email = models.EmailField(max_length=40)
	id_number = models.CharField(max_length=30)
	position = models.CharField(max_length=30)
	contract_type  = models.IntegerField()
	job_grade  = models.IntegerField()
	appt_date = models.DateField()
	last_date = models.DateField()

	def __str__(self):
            return self.first_name

class LvBalances(models.Model):
   #staff_id   = models.CharField(max_length=10,null=False) #not null auto_increment primary key,
   staff_id   = models.ForeignKey(StaffMaster, on_delete=models.CASCADE)
   dept_id  = models.IntegerField()
   lv_annual  = models.IntegerField(null=False)
   lv_maternity  = models.IntegerField(null=False)
   lv_paternity  = models.IntegerField(null=False)
   lv_study  = models.IntegerField(null=False)
   lv_compassion  = models.IntegerField(null=False)
   lv_sick  = models.IntegerField(null=False)
   lv_other  = models.IntegerField()
   lv_other2  = models.IntegerField()

class LvSchedules(models.Model):
   #staff_id   = models.CharField(max_length=10) #not null auto_increment primary key,

   staff_id   = models.ForeignKey(StaffMaster, on_delete=models.CASCADE)
   dept_id   = models.IntegerField()
   sched1_start  = models.DateField()
   sched1_days  = models.IntegerField(null=False)
   sched2_start  = models.DateField()
   sched2_days  = models.IntegerField(null=False)
   sched3_start  = models.DateField(blank=True)
   sched3_days  = models.IntegerField(blank=True)
   sched4_start  = models.DateField(blank=True)
   sched4_days  = models.IntegerField(blank=True)
   sched5_start  = models.DateField(blank=True)
   sched5_days  = models.IntegerField(blank=True)
   lv_description =  models.CharField(max_length=100)
   lv_comments =  models.CharField(max_length=100)
   sched_status  = models.IntegerField(null=False)
   approver_id  = models.IntegerField(null=False)
   approval_dt  = models.DateField()
   returned_dt  = models.DateField()
   reschedule  = models.IntegerField()
   returner_id  = models.CharField(max_length=10)

class LvHoliday(models.Model):
    lv_year = models.CharField(max_length=4)
    lv_holidate = models.DateField(blank=False)
    lv_holiday = models.CharField(max_length=20)
    other = models.CharField(max_length=10)

    def __str__(self):
        return self.lv_holiday

class LvDepartment(models.Model):
    dept_id = models.IntegerField()
    dept_name = models.CharField(max_length=50)
    dept_hod = models.CharField(max_length=10)
    created_at = models.DateField()
    approver1_id  = models.CharField(max_length=10)
    approver2_id  = models.CharField(max_length=10)
    approver3_id  = models.CharField(max_length=10)
    approver4_id  = models.CharField(max_length=10)

    def __str__(self):
        return self.dept_name

class LvApprovers(models.Model):
   #staff_id  = models.CharField(max_length=10,null=False)
   staff_id   = models.ForeignKey(StaffMaster, on_delete=models.CASCADE)
   first_name = models.CharField(max_length=50)
   created_at = models.DateField()
   approver1_id  = models.CharField(max_length=10)
   approver2_id  = models.CharField(max_length=10)
   approver3_id  = models.CharField(max_length=10)

class StaffUsers(models.Model):
   staff_id  = models.CharField(max_length=10,null=False)   #not null auto_increment primary key,
   xtrainfo = models.CharField(max_length=30)
   xtrainfo2 = models.CharField(max_length=100)

   def __str__(self):
        return self.staff_id

class LvWorkLocation(models.Model):
   place_id  = models.IntegerField()    #not null auto_increment primary key,
   place_name = models.CharField(max_length=30)

   def __str__(self):
        return self.place_name

class LvApplications(models.Model):
   #staff_id = models.CharField(max_length=10,null=False)   # auto_increment primary key,

   staff_id = models.ForeignKey(StaffMaster, on_delete=models.CASCADE)
   dept_id = models.IntegerField(null=False)
   first_name =  models.CharField(max_length=30)
   second_name =  models.CharField(max_length=30)
   lv_type  = models.IntegerField(null=False)
   lv_days = models.IntegerField(null=False)
   lv_startdate = models.DateField()
   lv_enddate = models.DateField()
   application_dt = models.DateField()
   approval  = models.IntegerField(null=False)
   approver1_id  = models.IntegerField()
   approver2_id  = models.IntegerField()
   approver3_id  = models.IntegerField()  # ADD CancellER ID !!!
   approval1_dt  = models.DateField()
   approval2_dt  = models.DateField()
   approval3_dt  = models.DateField()
   cancelled_dt  = models.DateField()
   deducted   = models.IntegerField(null=False)
   cancelled  = models.IntegerField()
   remarks =   models.CharField(max_length=100)

class LvTypes(models.Model):
    lv_typeid = models.IntegerField(null=False)
    lv_name = models.CharField(max_length=20)
    lv_type_comment = models.CharField(max_length=100)
