# zpages/forms.py
from django import forms
from zpages.models import LvSchedules

#class ContactForm(forms.Form):
#    from_email = forms.EmailField(required=True)
#    subject = forms.CharField(required=True)
#    message = forms.CharField(widget=forms.Textarea, required=True)


class LvApproverEdit(forms.Form):
    staffId = forms.CharField(required=True)
    Approva1 = forms.CharField(required=True)
    Approva2 = forms.CharField(required=True)
    Approva3 = forms.CharField(required=True)

class LvBalanceEdit(forms.Form):
    staffId = forms.CharField(required=True)
    Approva1 = forms.CharField(required=True)
    Approva2 = forms.CharField(required=True)
    Approva3 = forms.CharField(required=True)


class LvApplyForm(forms.Form):
    #staff_id = forms.CharField(required=True)
    #lv_type = forms.CharField(required=True)

    LV_TYPES= [
    ('1', 'Annual'),
    ('2', 'Maternity'),
    ('3', 'Paternity'),
    ('4', 'Study'),
    ('5', 'Compassion'),
    ('6', 'Sick'),
    ('7', 'Other'),
    ]

    lv_type= forms.CharField(label='Type Of Leave',
                             widget=forms.Select(choices=LV_TYPES))

    Start_Date = forms.DateField(widget=forms.TextInput(attrs=
                                {
                                    'class':'datepicker'
                                }))
    Days = forms.CharField(required=True)
    Remarks = forms.CharField(required=False)

# Create the form class.
class LvScheduleForm(forms.ModelForm):
    class Meta:
        model = LvSchedules

        fields = ('sched1_start', 'sched1_days', 'sched2_start', 'sched2_days' ,'sched3_start', 'sched3_days',
                  'sched4_start', 'sched4_days','sched5_start', 'sched5_days',  'lv_description')

        widgets = {'sched1_start': forms.DateInput(attrs={'class': 'datepicker'}),
                   'sched2_start': forms.DateInput(attrs={'class': 'datepicker'}),
                   'sched3_start': forms.DateInput(attrs={'class': 'datepicker'}),
                   'sched4_start': forms.DateInput(attrs={'class': 'datepicker'}),
                   'sched5_start': forms.DateInput(attrs={'class': 'datepicker'})
                   }
        required = ('sched1_start', 'sched1_days', 'sched2_start', 'sched2_days')
