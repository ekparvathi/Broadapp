from django.db import models
from usersection.models import Userinfo
from datetime import datetime

# Create your models here.

class Prodcategory(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name
  
    

class Addedproduct(models.Model):
    category = models.ForeignKey(Prodcategory, on_delete=models.CASCADE,null=False,default=1)
    name = models.CharField(max_length=255,null=False,blank=False)
    gstin = models.CharField(max_length=15,null=False,blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=False,blank=False)
    description = models.TextField(max_length=500,null=False,blank=False)
    country = models.CharField(max_length=255,null=False,blank=False)
    state = models.CharField(max_length=255,null=False,blank=False)
    district = models.CharField(max_length=255,null=False,blank=False)
    place = models.CharField(max_length=150,null=False,blank=False)
    image = models.ImageField(upload_to='images/products/', null=False,blank=False)
    user = models.ForeignKey(Userinfo, on_delete=models.CASCADE,null=False)

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    product = models.ForeignKey(Addedproduct, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(Userinfo, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # A field for ratings from 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'reviewer']  # Ensure a user can only review a product once




class ProductChat(models.Model):
    product = models.ForeignKey(Addedproduct, on_delete=models.CASCADE, related_name='chats')
    sender = models.ForeignKey(Userinfo, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Userinfo, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"Chat on {self.product.name} from {self.sender.Username} to {self.receiver.Username}"