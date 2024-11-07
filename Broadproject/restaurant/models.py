
# Create your models here.
from django.db import models
from usersection.models import Userinfo
from django.core.validators import MinLengthValidator

# Create your models here.
class RestaurantRegistration(models.Model):
    Restaurant_Name=models.CharField(max_length=100,null=False,blank=False)
    Owner_Name=models.CharField(max_length=100)
    District=models.CharField(max_length=100)
    Place=models.CharField(max_length=100)
    Phonenumber=models.CharField(max_length=15,unique=True)
    Email=models.EmailField(unique=True)
    Image=models.ImageField(upload_to='media/images',null=True)
    Password=models.CharField(max_length=50,validators=[MinLengthValidator(8)])
    Opening_time=models.TimeField()
    Closing_time=models.TimeField()
    Location=models.TextField()
    DateOfRegistration=models.DateField()



class Menu_Lists(models.Model):
    Restaurant=models.ForeignKey(RestaurantRegistration,on_delete=models.CASCADE)
    Restaurant_Name=models.CharField(max_length=100)
    Item=models.CharField(max_length=100)
    Category=models.CharField(max_length=100,null=True)
    Description=models.TextField(max_length=300)
    Price=models.FloatField()
    OfferCoupon=models.IntegerField()
    DeliveryOffer=models.IntegerField()
    Image=models.ImageField(upload_to='media/images',null=True)
    Availability=models.CharField(max_length=100,default='Available')


class Promo(models.Model):
    Restaurant=models.ForeignKey(RestaurantRegistration,on_delete=models.CASCADE)
    Code=models.CharField(max_length=8)
    Value=models.FloatField()
    Start_Date=models.DateField()
    End_Date=models.DateField()
    
class Promousage(models.Model):
    Customer=models.ForeignKey(Userinfo,on_delete=models.CASCADE)
    Promocode=models.ForeignKey(Promo,on_delete=models.CASCADE)
    Used_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('Customer', 'Promocode') 