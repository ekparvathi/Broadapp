from django.shortcuts import render
from .models import doctors,specialization,timeslot,Appointment,hospital,PaymentForAppoint
from .serializers import doctorSerializer,reminderSerializer,specializeSerializer,hospitalSerializer,paymentForAppSerializer, appointmentSerializer,timeslotSerializer
from rest_framework.decorators import api_view
from rest_framework import response,status
from django.contrib import messages
from datetime import datetime,timedelta
from usersection.models import Userinfo,Userpersonal_data
from django.utils import timezone
from django.shortcuts import get_object_or_404
import os,smtplib
from twilio.rest import Client
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
# import geocoder
import socket
import razorpay
from rest_framework.response import Response

# Create your views here.


#--1--filter based on doctorName
@api_view(['GET'])
def getDoctorsN(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    name = request.query_params.get('name', None)
    print(name)
    if name:
        # Filter doctors by name (case insensitive)
        data = doctors.objects.filter(name__icontains=name)
        
        if not data.exists():
            return Response({"ERROR": "NO DOCTORS FOUND"}, status=status.HTTP_404_NOT_FOUND)

        serializer = doctorSerializer(data, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"ERROR": "NAME QUERY PARAMETER REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
    
    

#--2--filter all doctors based on specialization by specialization id
@api_view(['GET'])
def getDoctorsS(request, id):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    # Filter doctors based on specialization id
    data = doctors.objects.filter(specialise_id=id)    
    if request.method == 'GET':
        if data:        
            serializer = doctorSerializer(data, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"ERROR": "NO DOCTORS FOUND WITH THIS SPECIALIZATION"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)


#--3--filter all doctors based on specialization by specialization name
@api_view(['GET'])
def getDoctorsBySpecialization(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    specialization_name = request.query_params.get('special', None)
    
    if specialization_name:
        # Filter doctors based on specialization (assuming 'specialise' is the field name)
        data = doctors.objects.filter(specialise__name__icontains=specialization_name)
        
        if not data.exists():
            return Response({"ERROR": "NO DOCTORS FOUND"}, status=status.HTTP_404_NOT_FOUND)

        serializer = doctorSerializer(data, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({"ERROR": "SPECIALIZATION QUERY PARAMETER REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)
    
#--4---Filter doctor based on name and specialization
@api_view(['GET'])
def searchDoctorByNameAndSpecialization(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    doctor_name = request.query_params.get('doctor', None)
    specialization_name = request.query_params.get('special', None)
    print(doctor_name,specialization_name)
    if not doctor_name or not specialization_name:
        return Response({"error": "Both doctor and specialization query parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the specialization based on name (case-insensitive)
        special = specialization.objects.get(name__iexact=specialization_name)
        # Fetch doctors with the provided name and specialization
        doctors_data = doctors.objects.filter(name__icontains=doctor_name, specialise=special)
    except specialization.DoesNotExist:
        return Response({"error": "Specialization not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if doctors_data.exists():
        serializer = doctorSerializer(doctors_data, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"error": "Doctor not found with the given specialization."}, status=status.HTTP_404_NOT_FOUND)

#--5------Filter doctor based on name and hospital
@api_view(['GET'])
def searchDoctorByNameAndHospital(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    doctor_name = request.query_params.get('doctor', None)
    hospital_name = request.query_params.get('hosp', None)
    
    # Ensure both parameters are provided
    if not doctor_name or not hospital_name:
        return Response({"error": "Both doctor and hospital query parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the hospital based on name (case-insensitive)
        hosp = hospital.objects.get(name__iexact=hospital_name)
        # Fetch doctors with the provided name and hospital
        doctors_data = doctors.objects.filter(name__icontains=doctor_name, hosp=hosp)
    except hospital.DoesNotExist:
        return Response({"error": "Hospital not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if doctors_data.exists():
        serializer = doctorSerializer(doctors_data, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response({"error": "Doctor not found in the given hospital."}, status=status.HTTP_404_NOT_FOUND)


#--6-------filter doctors based on hospital id
@api_view(['GET'])
def getDoctorsH(request,id):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    try:
        data=doctors.objects.filter(hosp_id=id)
    except doctors.DoesNotExist:
        return Response({"ERROR","NOT FOUND"},status=status.HTTP_404_NOT_FOUND)
    if request.method=='GET':
        serializer=doctorSerializer(data,many=True,context={'request':request})
        return Response(serializer.data)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#--7---------filter doctors based on hospital name
@api_view(['GET'])
def getDoctorsByHospital(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    hospital_name = request.query_params.get('hospital', None)
    print(hospital_name)
    if hospital_name:
        # Filter doctors based on the hospital name (case insensitive)
        doctors_list = doctors.objects.filter(hosp__name__icontains=hospital_name)
        
        if not doctors_list.exists():
            return Response({"ERROR": "NO DOCTORS FOUND FOR THIS HOSPITAL"}, status=status.HTTP_404_NOT_FOUND)

        serializer = doctorSerializer(doctors_list, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({"ERROR": "HOSPITAL QUERY PARAMETER REQUIRED"}, status=status.HTTP_400_BAD_REQUEST)

#--8---------filter All doctors 
@api_view(['GET'])
def getDoctorsAll(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    try:
        data=doctors.objects.all()
    except doctors.DoesNotExist:
        return Response({"ERROR","NOT FOUND"},status=status.HTTP_404_NOT_FOUND)
    if request.method=='GET':
        serializer=doctorSerializer(data,many=True,context={'request':request})
        return Response(serializer.data)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#--9------All Category
@api_view(['GET'])
def getSpecializeAll(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    try:
        data=specialization.objects.all()
    except specialization.DoesNotExist:
        return Response({"ERROR","NOT FOUND"},status=status.HTTP_404_NOT_FOUND)
    if request.method=='GET':        
        serializer=specializeSerializer(data,many=True,context={'request':request})
        return Response(serializer.data)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

#--10----------All Hospital
@api_view(['GET'])
def getHospitalAll(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    print(current_user)
    try:
        data=hospital.objects.all()
    except hospital.DoesNotExist:
        return Response({"ERROR","NOT FOUND"},status=status.HTTP_404_NOT_FOUND)
    if request.method=='GET':        
        serializer=hospitalSerializer(data,many=True,context={'request':request})
        return Response(serializer.data)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


#--11----------------All nearby Hospitals --------
@api_view(['GET'])
def getHospitalsNear(request): 
# Set a test email for session (remove in production)  
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    
    try:
        user = Userinfo.objects.get(Email=current_user)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        user_data = Userpersonal_data.objects.get(User_id=user.id)
    except Userpersonal_data.DoesNotExist:
        return Response({'msg': 'Add your Address to profile'}, status=status.HTTP_400_BAD_REQUEST)

    user_address = f"{user_data.District}, {user_data.Place}"
    if not user_address:
        return Response({'error': 'Address parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Initialize geolocator
    geolocator = Nominatim(user_agent="GetLoc", timeout=20)
    
    # Geocode the user's address
    location_2 = geolocator.geocode(user_address)
    if not location_2:
        return Response({'error': 'Invalid user address.'}, status=status.HTTP_400_BAD_REQUEST)
    
    currentLoc = (location_2.latitude, location_2.longitude)
    
    near = []
    data = hospital.objects.all()  # Consider optimizing this query if needed

    for d in data:
        # Assuming d.hosp.location is a valid address
        location_1 = geolocator.geocode(d.location)
        if not location_1:
            print(f"Could not geocode the address for doctor {d.name}")
            continue  # Skip this doctor if the location cannot be found
        
        docLoc = (location_1.latitude, location_1.longitude)
        mydist = geodesic(docLoc, currentLoc).km
        
        print(f"Doctor Location: {docLoc}, Distance: {mydist} km")
        
        if mydist < 5:  # If within 10 km
            print(f"Doctor {d.name} is nearby.")
            near.append(d)

    if not near:
        return Response({"ERROR": "NO NEARBY DOCTORS FOUND"}, status=status.HTTP_404_NOT_FOUND)

    serializer = hospitalSerializer(near, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


    
#--12-------------------All nearby Doctors ----------------------
@api_view(['GET'])
def getDoctorsNear(request):

    # Set a test email for session (remove in production)
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    
    try:
        user = Userinfo.objects.get(Email=current_user)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        user_data = Userpersonal_data.objects.get(User_id=user.id)
    except Userpersonal_data.DoesNotExist:
        return Response({'msg': 'Add your Address to profile'}, status=status.HTTP_400_BAD_REQUEST)

    user_address = f"{user_data.District}, {user_data.Place}"
    if not user_address:
        return Response({'error': 'Address parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Initialize geolocator
    geolocator = Nominatim(user_agent="GetLoc", timeout=20)
    
    # Geocode the user's address
    location_2 = geolocator.geocode(user_address)
    if not location_2:
        return Response({'error': 'Invalid user address.'}, status=status.HTTP_400_BAD_REQUEST)
    
    currentLoc = (location_2.latitude, location_2.longitude)
    
    near = []
    data = doctors.objects.all()  # Consider optimizing this query if needed

    for d in data:
        # Assuming d.hosp.location is a valid address
        location_1 = geolocator.geocode(d.hosp.location)
        if not location_1:
            print(f"Could not geocode the address for doctor {d.name}")
            continue  # Skip this doctor if the location cannot be found
        
        docLoc = (location_1.latitude, location_1.longitude)
        mydist = geodesic(docLoc, currentLoc).km
        
        print(f"Doctor Location: {docLoc}, Distance: {mydist} km")
        
        if mydist < 10:  # If within 10 km
            print(f"Doctor {d.name} is nearby.")
            near.append(d)

    if not near:
        return Response({"ERROR": "NO NEARBY DOCTORS FOUND"}, status=status.HTTP_404_NOT_FOUND)

    serializer = doctorSerializer(near, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


    
#--13-----Make Doctor Appointment
@api_view(['POST'])
def makeAppoint(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    if request.method == 'POST':
        print(request.data)
        
        # Access timeslot_id and doctor_id from request.data (not request.POST)
        time_slot_id = request.data['timeslot_id']
        doctor_id = request.data['appDoc']
        
        # Fetch the timeslot and ensure it's not already booked
        slot = get_object_or_404(timeslot, id=time_slot_id, timeForDoc_id=doctor_id, isBooked=False)
        print(slot.isBooked)
        timeslot_date = slot.date  # Assuming this is a date object
        timeslot_start_time = slot.start_time  # Assuming this is a time object

        # Create naive datetime by combining date and time
        naive_datetime = datetime.combine(timeslot_date, timeslot_start_time)
        print(naive_datetime)
        # Make the naive datetime timezone-aware
        aware_datetime = timezone.make_aware(naive_datetime)  # Adjust to specific timezone if necessary
        print(aware_datetime)
        # logger.debug("Aware datetime for the appointment: %s", aware_datetime)
        if slot.isBooked:  # Correctly check slot.isBooked
            return Response({"error": "This timeslot is already booked."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure to assign the timeslot instance directly to the appointment
        serializer = appointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save(time_slot=slot)  # Save with the timeslot instance
            
            # Mark the timeslot as booked
            slot.isBooked = True
            slot.save()
            
            # Optional: Print and send email, SMS, etc.
            print(slot.apptoken)
            sendEmail(request.data, slot)
            sendSMS(request.data, slot)
            
            return Response({'msg': 'Appointment Booked Successfully', 'data': serializer.data})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(request.data)

#send appointment confirmation Email
def sendEmail(data,slot):
    # if 'Email' in request.session:
    #     print(request.session['Email'])
    #     current_user=request.session['Email']
    #     print(current_user)
        print(data)    
        doc=doctors.objects.get(id=data['appDoc'])
        content="Date "+str(slot.date)+"\nDoctor "+doc.name+"\nTime "+str(slot.start_time)+"\nToken "+str(slot.apptoken)
        print(content)
        mail=smtplib.SMTP('smtp.gmail.com',587)
        mail.ehlo()
        mail.starttls()
        sender=''
        recipient=data['appEmail']
        mail.login(sender,'')
        header='To:'+recipient+'\n'+'From:'+sender+'\n'+'subject:Appointment\n'
        content=header+content
        mail.sendmail(sender,recipient,content)
        mail.close()

#send SMS confirmation
def sendSMS(data,slot):
     # if 'Email' in request.session:
    #     print(request.session['Email'])
    #     current_user=request.session['Email']
    #     print(current_user)
    print(data) 
    doc=doctors.objects.get(id=data['appDoc'])
    content="Date "+str(slot.date)+"\nDoctor "+doc.name+"\nTime "+str(slot.start_time)+"\nToken "+str(slot.apptoken)
    print(content)
    account_sid = 'ACdb865cdf09521f8a25d78a099f5df936'
    auth_token = 'b40ae1fc5271fec3d27d168eba0a6bf9'
    client = Client(account_sid, auth_token)    
    print(data['appContact'])
    message = client.messages.create(
    from_='+18725886906',
    body=content,
    to=str(data['appContact'])
    )
    print(message.sid)   

#--14--------Check All booked timeslots of a Doctor
@api_view(['GET'])
def getBookedTimeSlots(request, id):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    if request.method == 'GET':
        slot = timeslot.objects.filter(timeForDoc=id, isBooked=True)
        
        if not slot.exists():
            return Response({"error": "No booked timeslots found"}, status=status.HTTP_404_NOT_FOUND)  # Updated error message
        
        serializer = timeslotSerializer(slot, many=True, context={'request': request})
        return Response(serializer.data)
    
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)


#--15--------Check all available timeslots of a Doctor
@api_view(['GET'])
def getAvailableTimeSlots(request, id):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    if request.method == 'GET':
        slot = timeslot.objects.filter(
    timeForDoc=id,
    isBooked=False,
    date__gte=datetime.now().date(),
    start_time__lt=datetime.now().time()
)
        
        if not slot.exists():
            return Response({"error": "No available timeslots found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = timeslotSerializer(slot, many=True, context={'request': request})
        return Response(serializer.data)
    
    return Response({"error": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)


#--16--------Check particular appointment Details
@api_view(['GET'])
def getAppointmentDetail(request, id):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    try:
        # Retrieve appointment and timeslot
        appoint = Appointment.objects.get(id=id)
        slot = timeslot.objects.get(id=appoint.time_slot_id)

    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
    except timeslot.DoesNotExist:
        return Response({"error": "Timeslot not found"}, status=status.HTTP_404_NOT_FOUND)

    # Use DRF serializers with the correct context
    slotserializer = timeslotSerializer(slot, many=False, context={'request': request})
    serializer = appointmentSerializer(appoint, many=False, context={'request': request})

    return Response({'appointment': serializer.data,'timeslot': slotserializer.data})


#--17---------------------Set Appointment reminder
@api_view(['POST'])
def setAppointmentReminder(request, id):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    print(request.data, id)  # Log incoming data for debugging
    remind_time = request.data.get('reminder_time')  # Fetch reminder time from request
    token = request.data.get('reminder_token')  # Fetch reminder token from request
    print(remind_time)
    # Fetch the appointment instance, or return a 404 if not found
    appoint = get_object_or_404(Appointment, id=id)  # Ensure you use the correct model name

    # Step 1: Combine the date and time into a datetime object
    naive_datetime = datetime.combine(appoint.time_slot.date, appoint.time_slot.start_time)

    # Step 2: Calculate the updated reminder time
    try:
        remind_time_minutes = int(remind_time)  # Convert remind_time to integer minutes

        # If you're also handling float hours (e.g., 5.30 hours), convert it to minutes
        float_hours_to_add = 5.30
        whole_hours = int(float_hours_to_add)
        additional_minutes = (float_hours_to_add - whole_hours) * 60
        total_float_minutes = whole_hours * 60 + int(additional_minutes)

        # Subtract the total reminder time (in minutes) from the appointment time
        updated_datetime = naive_datetime - timedelta(minutes=remind_time_minutes + total_float_minutes)
    except ValueError:
        return Response({"error": "Invalid reminder time."}, status=status.HTTP_400_BAD_REQUEST)

    updated_datetime = naive_datetime - timedelta(minutes=remind_time_minutes)
    print("Updated datetime:", updated_datetime)

    # Log the appointment for debugging
    print("Appointment:", appoint)  

    # Create the reminder message using appointment details
    title = "Appointment Reminder"
    message = (
        f"\nDoctor: {appoint.appDoc.name}"
        f"\nDate: {appoint.time_slot.date}"
        f"\nTime: {appoint.time_slot.start_time}"
        f"\nToken: {appoint.time_slot.apptoken}"
        f"\nToken Now: {token}"
    )
    
    print("Generated Message:", message)

    # Prepare data for the serializer
    reminder_data = {
        'title': title,
        'message': message,
        'appointment': appoint.id,
        'reminder_time': updated_datetime,
        'reminder_token': token,
    }

    # Initialize the reminder serializer with the new data
    serializer = reminderSerializer(data=reminder_data)

    if serializer.is_valid():
        # Save the reminder with the appointment instance
        reminder = serializer.save(appointment=appoint)  
        
        return Response(reminderSerializer(reminder).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#------------------------Payment with razorpay----------------------------

def makePayment(request,id):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    total_price = request.data.get('total_price')  # Get total price from request data

    razorpay_client = razorpay.Client(auth=("rzp_test_RygLyDPora5U2G", "EYw9ReCWe4hioEnnq7OaF8ZM"))

    try:
        razorpay_order = razorpay_client.order.create({
            'amount': total_price * 100,
            'currency': 'INR',
            'payment_capture': '0'
        })
        app=get_object_or_404(Appointment,id=id)
        request.session['razorpay_order_id'] = razorpay_order['id']
        payment_details = {
            'amount': total_price * 100,  # Amount in paise
            'razorpay_order_id': razorpay_order['id'],
            'created_at': datetime.now()
        }
        serializer=paymentForAppSerializer(data=payment_details)
        if serializer.is_valid():
            payment_success=serializer.save(Appoint=app)
        
            return Response({
                'razorpay_order_id': razorpay_order['id'],
                'total_price': total_price,
                'msg': 'Order created, please proceed with payment.'
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'msg': 'Error creating order',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    
#--18--Search for doctor or hospital-------
@api_view(['GET'])
def search_Doctor_Hospital(request):
    print('HI')
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)
    current_user = request.session['Email']
    name = request.query_params.get('name', '')
    print(name)
    doctor = doctors.objects.filter(name__icontains=name)
    hospitals = hospital.objects.filter(name__icontains=name)
    print(doctor)
    print(hospitals)
    doctor_serializer = doctorSerializer(doctor, many=True)
    hospital_serializer = hospitalSerializer(hospitals, many=True)
    
    response_data = {
        'doctors': doctor_serializer.data,
        'hospitals': hospital_serializer.data,
    }
    
    # If no doctors and hospitals were found
    if not response_data['doctors'] and not response_data['hospitals']:
        return Response({"message": "No results found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(response_data, status=status.HTTP_200_OK)

#--19--------Check all appointments Details
@api_view(['GET'])
def getAllAppointments(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Please Login!'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    try:
        # Retrieve appointment and timeslot
        appoint = Appointment.objects.filter(appEmail=current_user).prefetch_related('time_slot')
        
        if not appoint.exists():
            return Response({"msg": "No appointments found"}, status=status.HTTP_404_NOT_FOUND)
        timeslot_data=[]
        doctor_data=[]
        for app in appoint:
                print(app.appDoc)
                if app.time_slot:  # Ensure time_slot is not None
                    slot = timeslot.objects.filter(id=app.time_slot.id).first()
                    doc=doctors.objects.filter(id=app.appDoc.id)  # Get the first matching timeslot
                if slot:
                    # Serialize the timeslot
                    slot_serializer = timeslotSerializer(slot, context={'request': request})
                    timeslot_data.append(slot_serializer.data)
        serializer = appointmentSerializer(appoint, many=True, context={'request': request})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'appointments': serializer.data,
        'timeslots': timeslot_data 
        
    }, status=status.HTTP_200_OK)