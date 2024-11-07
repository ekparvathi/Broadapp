from django.db import models
from django.core.validators import MinLengthValidator


class Userinfo(models.Model):
    Username=models.CharField(max_length=50)
    Email=models.EmailField(max_length=50,unique=True,null=False,blank=False)
    Phonenumber=models.CharField(max_length=128,unique=True,null=False,blank=False)
    Password=models.CharField(max_length=128,validators=[MinLengthValidator(8)])

class Userpersonal_data(models.Model):
    User_id=models.ForeignKey(Userinfo,on_delete=models.CASCADE)
    Address=models.TextField(max_length=100)
    Country=models.CharField(max_length=100,null=True)
    District=models.CharField(max_length=100,null=True)
    Place=models.CharField(max_length=100,null=True)
    Id_Image=models.ImageField(upload_to='media/images',null=True)
    Gender=models.CharField(max_length=20,null=True)
    Profile_pic=models.ImageField(upload_to='media/profilepics', null=False, blank=False,default='profile pic')
    
    