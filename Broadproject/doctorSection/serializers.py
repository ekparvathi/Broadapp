from rest_framework import serializers
from .models import doctors,hospital,specialization,timeslot,Appointment,Reminder,PaymentForAppoint

class doctorSerializer(serializers.ModelSerializer):
    class Meta:
        model=doctors
        fields='__all__'

class hospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model=hospital
        fields='__all__'

class specializeSerializer(serializers.ModelSerializer):
    class Meta:
        model=specialization
        fields='__all__'

class timeslotSerializer(serializers.ModelSerializer):
    class Meta:
        model=timeslot
        fields='__all__'

class appointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Appointment
        fields='__all__'

class appForDocSerializer(serializers.ModelSerializer):
    class Meta:
        model=Appointment
        fields=('appPatient','appointTime','appointDate')

class reminderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reminder
        fields='__all__'

class paymentForAppSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reminder
        fields='__all__'