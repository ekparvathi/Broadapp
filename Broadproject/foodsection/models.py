from django.db import models

# Create your models here.
from django.db import models
from usersection.models import Userinfo
from restaurant.models import RestaurantRegistration,Menu_Lists
from django.utils import timezone

# Create your models here.

class RestaurantReview(models.Model):
    Customer_id=models.ForeignKey(Userinfo,on_delete=models.CASCADE)
    Restaurant_id=models.ForeignKey(RestaurantRegistration,on_delete=models.CASCADE)
    Customer_Name=models.CharField(max_length=100)
    Review=models.TextField(max_length=100,null=True)
    Rating=models.IntegerField(null=True)



class Categories(models.Model):
    Categorie_name=models.CharField(max_length=50)


class Cart(models.Model):
    Restaurant_id=models.ForeignKey(RestaurantRegistration,on_delete=models.CASCADE,default=1)
    Customer_id=models.ForeignKey(Userinfo,on_delete=models.CASCADE)
    Menuitem_id=models.ForeignKey(Menu_Lists,on_delete=models.CASCADE)
    Item_name=models.CharField(max_length=100)
    Quantity=models.IntegerField(null=False,default=1)
    Price=models.FloatField(null=False)
    TotalPrice=models.FloatField(default=1)
    DeliveryCharge=models.FloatField(default=50)
    Offer_Price=models.FloatField(default=0)



class Orders(models.Model):
    Restaurant_id=models.ForeignKey(RestaurantRegistration,on_delete=models.CASCADE)
    Customer_id=models.ForeignKey(Userinfo,on_delete=models.CASCADE)
    Customer_Name=models.CharField(max_length=100)
    Customer_Location=models.CharField(max_length=100)
    Customer_Phonenumber=models.CharField(max_length=15)
    Item_name=models.CharField(max_length=100,default="FOOD")
    Quantity=models.IntegerField()
    Price=models.FloatField()
    status=models.CharField(max_length=100,default='Order Submitted.')
    DateTime = models.DateTimeField(auto_now_add=True)
    Deliverycharge=models.FloatField(default=1)
    TotalPrice=models.FloatField(default=10)
    Offer_price=models.FloatField(default=0)
    Payment_method = models.CharField(max_length=50, default='cash_on_delivery')
    PromoCode = models.CharField(max_length=100, null=True, blank=True)  # Store the promo code
    PromoUsed = models.BooleanField(default=False)



