from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from datetime import date, datetime, timedelta
# Create your models here.
    
class specialization(models.Model):
    name=models.CharField(max_length=200,blank=True,null=True)   
    sepcialDescri=models.CharField(max_length=200,default='default')  
    def __str__(self):
        return(self.name)


class hospital(models.Model):
    name=models.CharField(max_length=200,blank=True)
    profile_pic=models.FileField(upload_to='static/images/',default='static/images/hospital.jpg')
    hospDescri=models.CharField(max_length=200,blank=True,null=True)
    district=models.CharField(max_length=200,blank=True,null=True)
    location=models.CharField(max_length=200,blank=True)
    contact=models.CharField(max_length=13,blank=True)
    web_site=models.URLField(blank=True)
    departments = models.ManyToManyField(specialization)
    def __str__(self):
        return(self.name) 


class doctors(models.Model):
    name=models.CharField(max_length=200,default='default')
    Email=models.CharField(max_length=200,default='default')
    district=models.CharField(max_length=200,default='default')
    location=models.CharField(max_length=200,default='default')
    password=models.CharField(max_length=200,default='default')
    descri=models.CharField(max_length=200,blank=True,null=True)
    profile_pic=models.FileField(upload_to='static/images/',default='static/images/defaultImage.jpg')
    qualification=models.CharField(max_length=200,default='MBBS')
    hosp=models.ForeignKey(hospital,on_delete=models.CASCADE,blank=True,null=True)
    specialise=models.ForeignKey(specialization,on_delete=models.CASCADE,blank=True,null=True)
    joinDate=models.DateTimeField(blank=True,null=True)
    status=models.CharField(max_length=50,default='active')


    def __str__(self):
        return(self.name)
    

class PasswordResetToken(models.Model):
    user = models.ForeignKey(doctors, on_delete=models.CASCADE)
    token = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.token

class timeslot(models.Model):
    date=models.DateField()
    timeForDoc=models.ForeignKey(doctors,on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slotDuration=models.IntegerField(default=5)
    isBooked=models.BooleanField(default=False)
    apptoken=models.IntegerField(null=True,blank=True)
    class Meta:
        unique_together = [('start_time', 'end_time',)]      
    def __str__(self):
         return f" {self.date} {self.start_time} to {self.end_time}"

    
class Appointment(models.Model):
    appPatient=models.CharField(max_length=100,blank=True,null=True)
    appEmail=models.EmailField(blank=True,null=True)
    appContact=models.CharField(max_length=15,blank=True,null=True)
    appAge=models.IntegerField(blank=True,null=True)
    appGender=models.CharField(max_length=20,blank=True,null=True)
    appAddress=models.CharField(max_length=300,blank=True,null=True)
    appDoc=models.ForeignKey(doctors,on_delete=models.CASCADE)  
    appBookDT=models.DateTimeField(auto_now_add=True,blank=True,null=True) 
    time_slot = models.OneToOneField(timeslot, on_delete=models.CASCADE,blank=True,null=True)
    def __str__(self):
        return(str(self.appPatient)) 


class Reminder(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    reminder_token = models.IntegerField(blank=True, null=True, default=1)
    reminder_time = models.DateTimeField(default=None)  # This will be set in the save method
    is_sent = models.BooleanField(default=False)

    # def __str__(self):
    #     return f"Reminder for appointment {self.appointment.id}: {self.title} at {self.reminder_time}"

    def save(self, *args, **kwargs):
        # Check if reminder_time is not already set
        if not self.reminder_time:
            # Combine the date and start_time to create a naive datetime object
            timeslot_date = self.appointment.time_slot.date
            timeslot_start_time = self.appointment.time_slot.start_time
            naive_appointment_datetime = datetime.combine(timeslot_date, timeslot_start_time)

            # Make the naive datetime timezone-aware
            aware_appointment_datetime = timezone.make_aware(naive_appointment_datetime)

            # Set reminder_time to be 24 hours before the appointment's datetime
            self.reminder_time = aware_appointment_datetime - timedelta(hours=24)
        
        super().save(*args, **kwargs)

    def is_due(self):
        """Check if the reminder time has passed and has not been sent."""
        return timezone.now() >= self.reminder_time and not self.is_sent

    def send_reminder(self):
    #Send the reminder to the user (implement your sending logic here).
        if self.is_due():
            try:
                sendto=[self.appointment.appEmail]
                print(sendto)
                send_mail(
                    subject=self.title,
                    message=self.message,
                    from_email='ekparvathi@gmail.com',  # Use your email
                    recipient_list=sendto,  # Patient's email
                    fail_silently=False,
                )
                if self.appointment.appEmail and isinstance(self.appointment.appEmail, str):
                    sendto = [self.appointment.appEmail]
                else:
                    raise ValueError("Invalid email address for appointment")

                self.is_sent = True  # Mark as sent
                self.save()
                print("Email sent successfully!")  # Log success message
            except Exception as e:
                print(f"Error sending email: {str(e)}")  # or use traceback for detailed logs

class PaymentForAppoint(models.Model):
    Appoint=models.ForeignKey(Appointment, on_delete=models.CASCADE, blank=True, null=True)
    amount=models.FloatField( blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.razorpay_order_id