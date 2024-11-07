from django.db import models

# Create your models here.

# Create your models here.
class Admindata(models.Model):
    Admin_Name=models.CharField(max_length=100)
    Email=models.EmailField()
    Password=models.CharField(max_length=20)

class DeliveryFee(models.Model):
    Range=models.CharField(max_length=120)
    Deliveryfee=models.IntegerField()
    
class Foodmanager(models.Model):
    Food_Boss=models.CharField(max_length=100)
    Email=models.EmailField()
    Password=models.CharField(max_length=100)
    
class Jobmanager(models.Model):
    Job_Boss=models.CharField(max_length=100)
    Email=models.EmailField()
    Password=models.CharField(max_length=100)

class Doctormanager(models.Model):
    Doctor_Boss=models.CharField(max_length=100)
    Email=models.EmailField()
    Password=models.CharField(max_length=100)
    reset_token = models.CharField(max_length=32, null=True, blank=True)
    token_expiration = models.DateTimeField(null=True, blank=True)

class BuySellmanager(models.Model):
    Buysell_Boss=models.CharField(max_length=100)
    Email=models.EmailField()
    Password=models.CharField(max_length=100)
