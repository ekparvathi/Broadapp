# Generated by Django 5.1 on 2024-10-29 06:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('restaurant', '0001_initial'),
        ('usersection', '0002_userpersonal_data_profile_pic'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Categorie_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Item_name', models.CharField(max_length=100)),
                ('Quantity', models.IntegerField(default=1)),
                ('Price', models.FloatField()),
                ('TotalPrice', models.FloatField(default=1)),
                ('DeliveryCharge', models.FloatField(default=50)),
                ('Offer_Price', models.FloatField(default=0)),
                ('Customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usersection.userinfo')),
                ('Menuitem_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.menu_lists')),
                ('Restaurant_id', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='restaurant.restaurantregistration')),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Customer_Name', models.CharField(max_length=100)),
                ('Customer_Location', models.CharField(max_length=100)),
                ('Customer_Phonenumber', models.CharField(max_length=15)),
                ('Item_name', models.CharField(default='FOOD', max_length=100)),
                ('Quantity', models.IntegerField()),
                ('Price', models.FloatField()),
                ('status', models.CharField(default='Order Submitted.', max_length=100)),
                ('DateTime', models.DateTimeField(auto_now_add=True)),
                ('Deliverycharge', models.FloatField(default=1)),
                ('TotalPrice', models.FloatField(default=10)),
                ('Payment_method', models.CharField(default='cash_on_delivery', max_length=50)),
                ('PromoCode', models.CharField(blank=True, max_length=100, null=True)),
                ('PromoUsed', models.BooleanField(default=False)),
                ('Customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usersection.userinfo')),
                ('Restaurant_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.restaurantregistration')),
            ],
        ),
        migrations.CreateModel(
            name='RestaurantReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Customer_Name', models.CharField(max_length=100)),
                ('Review', models.TextField(max_length=100, null=True)),
                ('Rating', models.IntegerField(null=True)),
                ('Customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='usersection.userinfo')),
                ('Restaurant_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.restaurantregistration')),
            ],
        ),
    ]
