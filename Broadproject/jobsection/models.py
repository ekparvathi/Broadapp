from django.db import models

# Create your models here.
from django.db import models
from usersection.models import Userinfo
from django.utils import timezone  # This is used to ensure proper timezone handling
from django.core.exceptions import ValidationError

# Create your models here.

class JobPostings(models.Model):
    User=models.ForeignKey(Userinfo,on_delete=models.CASCADE)
    Jobtitle=models.CharField(max_length=100)
    Jobrole=models.CharField(max_length=100)
    Job_Category=models.CharField(max_length=100)
    Job_Type=models.CharField(max_length=100)
    Qualification=models.CharField(max_length=100,default='degree')
    Min_salary=models.FloatField()
    Max_salary=models.FloatField()
    Vaccancies=models.IntegerField()
    Jobexperience=models.CharField(max_length=100)
    Country=models.CharField(max_length=100)
    State=models.CharField(max_length=100)
    District=models.CharField(max_length=100)
    Place=models.CharField(max_length=100)
    Description=models.TextField(max_length=250)
    Logo=models.ImageField(upload_to='images/')
    Posted_Date=models.DateTimeField(auto_now_add=True)
    Company_name=models.CharField(max_length=100,default='nil')
    Company_license=models.CharField(max_length=100,null=True)
    
class Saved_Jobs(models.Model):
    User=models.ForeignKey(Userinfo,on_delete=models.CASCADE)
    Saved_job=models.ForeignKey(JobPostings,on_delete=models.CASCADE)
    
def validate_pdf(file):
    if not file.name.endswith('.pdf'):
        raise ValidationError("Only PDF files are allowed.")
    
class Profile(models.Model):
    User=models.ForeignKey(Userinfo,on_delete=models.CASCADE)
    User_Photo=models.ImageField(upload_to='static/images')
    User_Name=models.CharField(max_length=100)
    Email=models.EmailField(null=True)
    Phonenumber=models.CharField(max_length=12,null=True)
    Title=models.CharField(max_length=100)
    Qualification=models.CharField(max_length=100)
    Description=models.TextField(max_length=300)
    
class Applications_received(models.Model):
    Applicant=models.ForeignKey(Userinfo,on_delete=models.CASCADE)
    Applicant_profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    Posted_by=models.ForeignKey(JobPostings,on_delete=models.CASCADE)
    RelevantSkill=models.CharField(max_length=100,null=True)
    Portfolio_link=models.CharField(max_length=100,null=True)
    Cover_letter=models.FileField(upload_to='pdfs/covers/',validators=[validate_pdf],null=True)
    Resume=models.FileField(upload_to='pdfs/resumes/',validators=[validate_pdf])
    Applied_date=models.DateField(auto_now_add=True)
    
    