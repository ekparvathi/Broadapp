from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from doctorSection.models import hospital,specialization,doctors,timeslot,Appointment,Reminder,PasswordResetToken
from adminsection.models import Doctormanager
from usersection.models import Userinfo,Userpersonal_data
from django.core.paginator import Paginator
import logging
logger = logging.getLogger(__name__)
from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count
from twilio.rest import Client
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from datetime import time
from django.shortcuts import render, redirect
from django.contrib import messages



#-----------------Login , logout , Admin password change ----------------
# @login_required
# def change_admin_password(request):
#     print("hello")
#     user = request.user  # Assuming the logged-in user is the admin
#     print("hi  0001")
#     if request.method == 'POST':
#         print("hi 002")
#         form = AdminPasswordChangeForm(user, request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Your password has been updated successfully.')
#             return redirect('doctorAdmin/home')  # Redirect to a success page or admin home
#     else:
#         form = AdminPasswordChangeForm(user)

#     return render(request, 'admin/auth/password_change_form.html', {
#         'form': form,
#         'title': 'Change Password',
#         'user': user,
#     })


# def doctorAdminLogin(request):
#     print("hi")
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         print(username,password)
#         user = authenticate(request, username=username, password=password)
#         print(user)
#         if user is not None:
#             # If user exists and credentials are correct, log them in

#             login(request, user)   
#             print(user)         
#             current_user=user
#             return redirect('/')  # Redirect to home page or other page
#         else:
#             # Invalid login credentials
#             messages.error(request, 'Invalid username or password.')
#     print("hello")
#     return render(request, 'doctorAdmin/doctorAdminLogin.html')



# def logout_view(request):
#     # Log the user out
#     request.session.clear()
#     logout(request)
    
#     # Redirect to the login page (or home page)
#     return redirect('doctorAdmin/doctorAdminLogin')

#---------------Admin home page/Dash board--------------------
def doctorAdminHome(request):
    messages=None
    doc=doctors.objects.all().count()
    hosp=hospital.objects.all().count()
    dept=specialization.objects.all().count()
    future_appoint = Appointment.objects.filter(time_slot__date__gt=datetime.now()).count()
    slot=timeslot.objects.filter(isBooked=False).count()
    rem=Reminder.objects.filter(is_sent=False).count()
    if not doc: doc=0
    elif not hosp: hosp=0
    elif not dept: dept=0
    elif not future_appoint: future_appoint=0
    elif not slot: slot=0
    elif not rem: rem=0
    context={
        'doc':doc,
        'hosp':hosp,
        'dept':dept,
        'future_appoint':future_appoint,
        'slot':slot,
        'rem':rem,
        "messages":messages
    }
    return render(request,'doctorAdmin/doctorAdminHome.html',context)

################### Show all hospitals #####################
def hospitals(request):
    messages=None
    data=hospital.objects.all()
    print("-----",data)
    paginator = Paginator(data, 10)  # Show 10 doctors per page
    page_number = request.GET.get('page')  # Get the page number from the query parameters
    page_obj = paginator.get_page(page_number)
    if page_obj:
        
        return render(request,'doctorAdmin/hospitals.html',{'data':page_obj})
    else:
        messages="No Hospitals to display"
        return render(request,'doctorAdmin/hospitals.html',{'messages':messages})
   

#------------------Search Doctors-----------------------------
def searchHospitals(request):
    messages=None
    if request.method=="GET":
        name = request.GET.get('name', None)  # Use request.GET for query parameters
        print(name)
        
        if name:
            # Filter doctors by name (case insensitive)
            data = hospital.objects.filter(name__icontains=name)  # Use the correct model name
            print("Data:", data)
            
            if not data.exists():
                messages="No Doctors Found"
                return render(request, "doctorAdmin/hospitals.html", {'messages': messages})
            
            return render(request, "doctorAdmin/hospitals.html", {'data': data,'messages': messages})

    # Optionally handle the case when name is not provided
    return render(request, "doctorAdmin/hospitals.html",)

#------------------------Display Details of a Hospital--------------
def dispHosp(request,id):
    messages=None
    try:
        hosp=hospital.objects.get(id=id)
        print("@@@",hosp," ID  ",id)
        print(hosp)
        dept=specialization.objects.filter(hospital=hosp)
        print("----",dept)
    except hospital.DoesNotExist:
        messages='Cannot find '
        return render(request,"doctorAdmin/dispHosp.html",{'messages':messages}) 
    else:
        return render(request,"doctorAdmin/dispHosp.html",{'hosp':hosp,'dept':dept,"messages":messages})
    

# -----------------Add new Hospitals---------------
def addModHosp(request):
    messages=None
    dept=specialization.objects.all()
    print(request.method)
    if request.method=='POST':
        name=request.POST['name']
        location=request.POST['location']
        profile_pic='static/images/hospital.jpg'
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']       
        print(profile_pic)
        hospDescri=request.POST['hospDescri']
        deprtmnts=request.POST.getlist('dept')
        print(deprtmnts)
        district=request.POST['district']
        location=request.POST['location']
        contact=request.POST['contact']
        dist=0
        web=request.POST['web']
        try:
            instance=hospital.objects.get(name=name,location=location,web_site=web)
            print(instance)
            instance.name=name
            instance.location=location
            instance.district=district
            instance.location=location
            instance.contact=contact
            instance.web_site=web
            instance.profile_pic=profile_pic
            instance.save
            for department_id in deprtmnts:
                data.departments.add(specialization.objects.get(id=department_id))
            messages.success(request,{"updated hospital successfuly"})
            print("hospital updated successfuly!!!!!")
                # messages.error(request,{"Hospital already exists"})           
        except hospital.DoesNotExist:
            data=hospital(name=name,location=location,district=district,contact=contact,web_site=web,hospDescri=hospDescri,profile_pic=profile_pic)
            data.save()
            for department_id in deprtmnts:
                depart = specialization.objects.get(id=department_id)  # Get the Department instance
                data.departments.add(depart) 
                messages =" hospital added successfuly"
            return render(request,'doctorAdmin/addModHosp.html',{'dept':dept,'messages':messages})
    return render(request,'doctorAdmin/addModHosp.html',{'dept':dept,"messages":messages})
    

#---------------------Modify Hopitals--------------------
def modifyHosp(request,id):
    messages=None
    instance=get_object_or_404(hospital, id=id)
    dept=specialization.objects.all()
    selected_departments = instance.departments.all() 
    print(instance)
    print(request.method)
    if request.method=='POST':
        print(request.method)
        instance.name=request.POST['name']
        if 'profile_pic' in request.FILES:
            instance.profile_pic = request.FILES['profile_pic']
        else:
            instance.profile_pic='static/images/hospital.jpg'
        print(instance.profile_pic)
        instance.location=request.POST['location']
        instance.district=request.POST['district']
        deprtmnts=request.POST.getlist('dept')
        instance.contact=request.POST['contact']
        instance.web_site=request.POST['web']  
        instance.hospDescri=request.POST['hospDescri']    
        instance.save()     
        instance.departments.clear()
        for department_id in deprtmnts:
            depart = specialization.objects.get(id=department_id)  # Get the Department instance
            instance.departments.add(depart)  
        print("hospital updated successfuly!!!!!")        
        messages='Hospital updated successfuly'
        return render(request,'doctorAdmin/modifyHosp.html',{'data':instance,'dept':dept,'selected_departments':selected_departments,'messages':messages})
    return render(request,'doctorAdmin/modifyHosp.html',{'data':instance,'dept':dept,'selected_departments':selected_departments,"messages":messages})
   

#---------------------Delete Hospital---------------------
def deleteHosp(request,id):
    try:
        instance=hospital.objects.get(id=id)            
    except hospital.DoesNotExist:
        messages.error(request,"doctorAdmin/hospitals.html",{"Cannot find"}) 
    else:
        print(instance)
        print("hi")
        instance.delete()
        return redirect("/doctorAdmin/hospitals")

################# Show all Specializations #######################
def specializations(request):
    messages=None
    data=specialization.objects.all()
    print("-----",data)
    if data:
        return render(request,'doctorAdmin/specializations.html',{'data':data})    
    else:
        messages="No departments added yet"
        return render(request,'doctorAdmin/specializations.html',{'messages':messages})    
   

#------------------------Add New Specialization----------------------
def addModSpecialization(request):
    messages=None
    print(request.method)
    if request.method=='POST':
        name=request.POST['name']
        sepcialDescri=request.POST['sepcialDescri']
        print(name)
        try:
            instance=specialization.objects.get(name=name)                
        except specialization.DoesNotExist:
            data=specialization.objects.create(name=name,sepcialDescri=sepcialDescri)
            if data:
                print("specialization added successfuly!!!!!")
                messages="saved specialization added successfuly"
                return render(request,'doctorAdmin/addModSpecialization.html',{"data":data,"messages":messages})
    return render(request,'doctorAdmin/addModSpecialization.html',{"messages":messages})
   

 #------------------ Modify Specializations--------------------------   
def modifySpecial(request,id):
    messages=None
    instance=get_object_or_404(specialization,id=id)
    print(instance)
    print(request.method)
    if request.method=='POST':
        print(request.method)
        instance.name=request.POST['name'] 
        instance.sepcialDescri=request.POST['sepcialDescri']
        instance.save()     
        if instance:
            messages="Specialization updated successfuly"
            print("Specialization updated successfuly!!!!!")
            return render(request,"doctorAdmin/modifySpecial.html",{'data':instance,"messages":messages})   
        else:
            messages="Specialization could not updated"
            return render(request,"doctorAdmin/modifySpecial.html",{'data':instance,"messages":messages})   

    return render(request,"doctorAdmin/modifySpecial.html",{'data':instance,"messages":messages})               
    
    
 #------------------ Add  new Department to a Hospital--------------------------   
def addHospDept(request,id):
    messages=None
    hosp=hospital.objects.all()
    dept=specialization.objects.all()
    existingDept = hosp.departments.all() 
    return render(request,'doctorAdmin/addHospDept.html',{'hosp':hosp,'dept':dept,'existingDept':existingDept,"messages":messages})
    

 #------------------ Delete Specializations--------------------------   
def deleteSpecial(request,id):
    try:
        instance=get_object_or_404(specialization,id=id)            
    except specialization.DoesNotExist:
        messages.error(request,"doctorAdmin/specializations.html",{"Cannot find"}) 
    else:
        print(instance)
        print("hi")
        instance.delete()
        return redirect("/doctorAdmin/specializations")

################# Show all Doctors #######################

def doctorss(request):
    messages=None
    data=doctors.objects.all()
    print("-----",data)
    paginator = Paginator(data, 5)  # Show 10 doctors per page
    page_number = request.GET.get('page')  # Get the page number from the query parameters
    page_obj = paginator.get_page(page_number)
    if page_obj:
        return render(request,'doctorAdmin/doctorss.html', {'data': page_obj})  
    else:
        messages="No Doctors Registered Yet"
        return render(request,'doctorAdmin/doctorss.html',{'messages':messages})     


#------------------Search Doctors-----------------------------
def searchDoctors(request):
    print(request.method)
    # data=doctors.objects.all()
    if request.method=="GET":
        name = request.GET.get('name', None)  # Use request.GET for query parameters
        print(name)
        
        if name:
            # Filter doctors by name (case insensitive)
            data = doctors.objects.filter(name__icontains=name)  # Use the correct model name
            print("Data:", data)
            
            if not data.exists():
                return render(request, "doctorAdmin/doctorss.html", {'messages': "No Doctors Found"})
            
            return render(request, "doctorAdmin/doctorss.html", {'data': data})        
    # Optionally handle the case when name is not provided
    return render(request, "doctorAdmin/doctorss.html")
     

#------------------------Diplay Details of a doctor--------------
def dispDoc(request, id):
    messages=None
    doc = get_object_or_404(doctors, id=id)
    print(doc)
    messages="No Doctor Found"
    return render(request, "doctorAdmin/dispDoc.html", {'doc': doc,'messages':messages})

    
#------------------------Add new doctor-------------------------
def addModDoc(request):
    messages=None
    hosp = hospital.objects.all()
    special = specialization.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        descri = request.POST.get('descri')
        profile_pic = request.FILES.get('profile_pic')
        qualification = request.POST.get('qualification')
        print(profile_pic)
        district = request.POST.get('district')
        location = request.POST.get('location')

        hosp_instance =get_object_or_404(hospital,id=request.POST['selectHosp'])
        specialise_instance =get_object_or_404(specialization,id=request.POST['selectSpecial'])
           
        doc=doctors(
            name=name,
            Email=email,
            password=password,
            profile_pic=profile_pic,
            qualification=qualification,
            hosp=hosp_instance,
            specialise=specialise_instance,
            district=district,
            location=location,
            descri=descri
        )
        doc.save()
        if doc:
            messages='"Doctor Added Successfuly"'
            return render(request, 'doctorAdmin/addModDoc.html', {'hosp': hosp, 'special': special,'messages':messages})
        else:
            messages="Doctor could not Added "
            return render(request, 'doctorAdmin/addModDoc.html', {'hosp': hosp, 'special': special,'messages':messages})


    return render(request, 'doctorAdmin/addModDoc.html', {'hosp': hosp, 'special': special,'messages':messages})


#------------------------Modify a doctor-----------------
def modifyDoc(request, id):
    messages=None
    instance = get_object_or_404(doctors, id=id)
    hosp = hospital.objects.all()
    special = specialization.objects.all()

    if request.method == 'POST':
        instance.name = request.POST.get('name', instance.name)

        # Handle profile picture
        if 'profile_pic' in request.FILES:
            instance.profile_pic = request.FILES['profile_pic']
        else:
            instance.profile_pic = 'static/images/doc.jpg'
        print(instance.profile_pic)
        instance.qualification = request.POST.get('qualification', instance.qualification)
        instance.descri = request.POST.get('descri', instance.descri)

        # Handle hospital and specialization selection
        instance.hosp = get_object_or_404(hospital, id=request.POST['selectHosp'])
        instance.specialise = get_object_or_404(specialization, id=request.POST['selectSpecial'])

        # Update latitude and longitude
        instance.district = request.POST.get('district', instance.district)
        instance.location = request.POST.get('location', instance.location)
        print(instance)
        # Save the updated instance
        instance.save()
        messages= "Doctor updated successfully!"
        return render(request, "doctorAdmin/modifyDoc.html", {'instance': instance, 'hosp': hosp, 'special': special,'messages':messages})

    return render(request, 'doctorAdmin/modifyDoc.html', {'instance': instance, 'hosp': hosp, 'special': special,'messages':messages})
   

#------------------------Delete a doctor--------------
def deleteDoc(request,id):
    try:
        instance=doctors.objects.get(id=id)            
    except doctors.DoesNotExist:
        messages.error(request,"appAdmin/doctorss.html",{"Cannot find"}) 
    else:
        print(instance)
        print("hi")
        instance.delete()
        return redirect("/doctorAdmin/doctorss")  
    
################# Show all Doctors To see their timeslot #######################
def timeslots(request):
    messages=None
    data = None  # Initialize data to None to handle the case of no data found    
    return render(request, "doctorAdmin/timeslots.html", {'data': data,'messages':messages})


#---------------Display a doctors time slot----------------------
def dispTimeSlot(request):
    messages=None
    doctor=doctors.objects.all() 
    slots = None  # Initialize slots to None to handle the case of no slots found
    submitted_data = {
        'selectDoc': 'selectDoc',  # Default to an empty string
        'slotDate': 'slotDate',    # Default to an empty string
    }
    if request.method=='POST':
        print("hi")
        submitted_data['selectDoc'] = request.POST.get('selectDoc')
        submitted_data['slotDate'] = request.POST.get('slotDate')
        if submitted_data['selectDoc']!='Select a Doctor':
            slots = timeslot.objects.filter(timeForDoc=submitted_data['selectDoc'], date=submitted_data['slotDate'])  # Adjust based on your model
            print(slots)
            if not slots.exists():
                messages = "No time slots available for the selected doctor on this date."
                return render(request, 'doctorAdmin/dispTimeSlot.html', {"doc":doctor, 'messages': messages,'submitted_data':submitted_data})
        else:
            # paginator = Paginator(slots, 5)  # Show 10 slots per page
            # page_number = request.GET.get('page')
            # page_obj = paginator.get_page(page_number)
            messages="Please select a Doctor"
            return render(request, 'doctorAdmin/dispTimeSlot.html', {"doc":doctor, 'slots': slots, 'messages': messages,'submitted_data':submitted_data})

    return render(request, 'doctorAdmin/dispTimeSlot.html', {"doc":doctor, 'slots': slots, 'messages':messages,'submitted_data':submitted_data})


#-----------Get timeslots of doctor with id    
# def get_timeslots(request, doctor_id):
#     if request.is_ajax():
#         try:
#             doctor = doctors.objects.get(id=doctor_id)
#             slots = timeslot.objects.filter(doctor=doctor)

#             # Render a partial template for the time slots
#             return render(request, 'timeslot_list.html', {'slots': slots})
#         except doctors.DoesNotExist:
#             return JsonResponse({'error': 'Doctor not found'}, status=404)
#     return JsonResponse({'error': 'Invalid request'}, status=400)
    

#---------------Add a doctors time slot----------------------
def addTimeSlot(request):
    messages=None
    doc=doctors.objects.all()
    if request.method == 'POST':
        doctor=request.POST['selectDoc']
        print(doctor)
        sdate = request.POST['slotDate']  # Get date from the form
        sTime = request.POST['slotSTime']  # e.g., '09:00'
        eTime = request.POST['slotETime']  # e.g., '17:00'
        slotDuration = int(request.POST['slotDuration'])  # Get slot duration in minutes
        token=0
        print(sdate)
        exist=timeslot.objects.filter(start_time=sTime,timeForDoc=doctor)
        print(exist)
        if  exist:
                messages="Time slot Already Exists.Please enter another timeslot"
                return render(request, 'doctorAdmin/addTimeSlot.html',{'doc':doc,'messages':messages})

        # Convert the string times to datetime.time objects
        start_time_obj = datetime.strptime(sTime, '%H:%M').time()
        end_time_obj = datetime.strptime(eTime, '%H:%M').time()
        
        # Initialize the starting time for iteration
        current_time = datetime.combine(datetime.today(), start_time_obj)
        end_time_limit = datetime.combine(datetime.today(), end_time_obj)
        print(current_time,end_time_limit)
        print(f"Creating slots for Doctor ID: {doctor} from {current_time} to {end_time_limit}")
        
        # Loop through time, incrementing by slot duration
        while current_time.time() < end_time_obj:
            print(token)
            start_time = current_time.time()
            current_time += timedelta(minutes=slotDuration)
            end_time = current_time.time()
            token+=1
            print(f"Slot from {start_time} to {end_time}")
            
            # Create and save the time slot
            slot = timeslot(
                timeForDoc_id=doctor,  # Assign the doctor ID
                date=sdate,
                start_time=start_time,
                end_time=end_time,
                slotDuration=slotDuration,
                apptoken=token
            )
            slot.save()  # Save the slot to the database
            messages="Added New Time Slot  "
            print(f"Saved slot: {slot}") 
        return render(request, 'doctorAdmin/addTimeSlot.html',{'doc':doc,'messages':messages})
            

    return render(request, 'doctorAdmin/addTimeSlot.html',{'doc':doc,'messages':messages})
   

#---------------Modify a doctors time slot----------------------
def modifyTimeSlot(request):
    messages=None
    doc = doctors.objects.all()  # Get all doctors
    if request.method == 'POST':
        doctor = request.POST['selectDoc']
        date = request.POST['slotDate']  # Get date from the form
        sTime = request.POST['slotSTime']  # Start time
        eTime = request.POST['slotETime']  # End time
        slotDuration = int(request.POST['slotDuration'])  # Slot duration in minutes

        try:
            # Check if time slots already exist for the given doctor and date
            slot = timeslots.objects.filter(timeForDoc_id=doctor, date=date)
            if slot.DoesNotExist():
                # Handle the case where slots already exist (modify or add behavior)
                error_message = f"Time slots does not exist for Doctor ID: {doctor} on {date}."
            else:
                # Convert start and end time strings to `time` objects
                start_time_obj = datetime.strptime(sTime, '%H:%M').time()
                end_time_obj = datetime.strptime(eTime, '%H:%M').time()

                # Initialize starting time for iteration
                current_time = datetime.combine(datetime.today(), start_time_obj)
                end_time_limit = datetime.combine(datetime.today(), end_time_obj)

                # Loop through time, incrementing by slot duration
                while current_time.time() < end_time_obj:
                    start_time = current_time.time()  # Starting time of the slot
                    current_time += timedelta(minutes=slotDuration)  # Increment by slot duration
                    end_time = current_time.time()  # End time of the slot

                    # Create a new time slot object
                    new_slot = timeslot(
                        timeForDoc_id=doctor,
                        date=date,
                        start_time=start_time,
                        end_time=end_time,
                        slotDuration=slotDuration
                    )
                    new_slot.save()  # Save the time slot to the database
                    print(f"Saved slot from {start_time} to {end_time} for Doctor ID: {doctor}")

                messages = f"Slots successfully updated for Doctor ID: {doctor} on {date}."

        except timeslots.DoesNotExist:
            messages = "No time slots available for the selected doctor on this date."
    
    context = {
        'doc': doc,
        'messages': locals().get('messages', None),
    }
    
    return render(request, 'doctorAdmin/modifyTimeSlot.html', context)

#----------Show appointments---------------------
def appointments(request):
    messages=None
    return render(request,'doctorAdmin/appointments.html',{'messages':messages})


def getDocTimeForAppoint(request):
    messages=None
    doctor=doctors.objects.all() 
    slots = None  # Initialize slots to None to handle the case of no slots found
    submitted_data = {
        'selectDoc': 'selectDoc',  # Default to an empty string
        'slotDate': 'slotDate',    # Default to an empty string
    }
    if request.method=='POST':
        submitted_data['selectDoc'] = request.POST.get('selectDoc')
        submitted_data['slotDate'] = request.POST.get('slotDate')
        print(submitted_data['selectDoc'],submitted_data['slotDate'])
        slots = timeslot.objects.filter(timeForDoc=submitted_data['selectDoc'], date=submitted_data['slotDate'],isBooked=False)  # Adjust based on your model
        print(slots)
        if not slots.exists():
            messages = "No time slots available for the selected doctor on this date."

    return render(request, 'doctorAdmin/getDocTimeForAppoint.html', {
        'doc': doctor,
        'slots': slots,
        'messages':messages,
        'submitted_data': submitted_data
    })
   

def makeAppointment(request, id):
    messages=None
    try:
        slot =get_object_or_404(timeslot,id=id)
    except timeslot.DoesNotExist:
        messages = "No time slots available for the selected doctor on this date."
        return render(request, 'doctorAdmin/makeAppointment.html', {'messages': messages})
    
    print(f"Time slot: {slot}, Doctor: {slot.timeForDoc}")
    
    # If the request method is POST, process the form data
    if request.method == 'POST':
        # Extract appointment data from the POST request
        appPatient = request.POST.get('appPatient')
        appEmail = request.POST.get('appEmail')
        appContact = request.POST.get('appContact')
        appAge = request.POST.get('appAge')
        appGender = request.POST.get('appGender')
        appAddress = request.POST.get('appAddress')
        # Get the associated doctor for the time slot
        doctor = doctors.objects.get(id=slot.timeForDoc.id)
        appDoc = doctor
        print(f"Doctor: {appDoc}")

        # Set the current date and time for the booking
        appBookDT = timezone.now()
        time_slot = slot
        
        # Create a new appointment record
        appoint = Appointment(
            appPatient=appPatient, 
            appGender=appGender, 
            appAddress=appAddress,
            appAge=appAge, 
            appBookDT=appBookDT, 
            appContact=appContact,
            appDoc=appDoc, 
            appEmail=appEmail, 
            time_slot=time_slot
        )
        if slot.isBooked==False:
        # Save the appointment
            appoint.save()
            print(f"Saved appointment: {appoint}")
            
            # Mark the slot as booked and save
            slot.isBooked = True
            slot.save()
        
        # Provide success message and context to the template
            messages = "Appointment successfully booked!"
            return render(request, 'doctorAdmin/makeAppointment.html', {'slot': slot, 'messages': messages})
        else:
            messages="Please select a different time slot"
            return render(request, 'doctorAdmin/makeAppointment.html', {'slot': slot, 'messages': messages})

    # If the request is GET, just display the available time slot
    return render(request, 'doctorAdmin/makeAppointment.html', {'slot': slot,'messages': messages})

def dispAppointments(request):
    doctor = doctors.objects.all()
    appoints = None  # Initialize appointments to None
    slots = None     # Initialize slots to None
    messages = None  # Initialize error message
    submitted_data = {
        'selectDoc': '',  # Default to an empty string
        'slotDate': '',   # Default to an empty string
    }

    if request.method == 'POST':
        submitted_data['selectDoc'] = request.POST.get('selectDoc')
        submitted_data['slotDate'] = request.POST.get('slotDate')
        print(submitted_data['selectDoc'],submitted_data['slotDate'])
        # Fetch time slots that are booked for the selected doctor and date
        slots = timeslot.objects.filter(
            timeForDoc=submitted_data['selectDoc'], 
            date=submitted_data['slotDate'],
            isBooked=True
        )
        print(slots)
        if slots.exists():
            # Fetch appointments based on the available slots
            appoints = Appointment.objects.filter(time_slot__in=slots)
            if not appoints.exists():
                messages = "No appointments found for the selected doctor on this date."
        else:
            messages = "No booked time slots available for the selected doctor on this date."
        print(appoints)
    return render(request, 'doctorAdmin/dispAppointments.html', {
        "doc": doctor, 
        'slots': slots, 
        'appoints': appoints, 
        'error_message': messages, 
        'submitted_data': submitted_data
    })



def reminders(request):
    # Fetch reminders (filter by some condition if needed)
    reminders = Reminder.objects.filter(is_sent=False)
    messages = None  # Initialize error message variable

    if not reminders:
        messages = "No reminders to display."
        print(messages)
    
    if request.method == 'POST' and reminders:
        try:
            for reminder in reminders:
                appointment = reminder.appointment  # Get the related appointment
                print(f"Appointment: {appointment}")
                
                if appointment and appointment.appEmail:
                    sendto = [appointment.appEmail]
                    print(f"Sending to: {sendto}")
                    
                    # Send email
                    send_mail(
                        subject=reminder.title,
                        message=reminder.message,
                        from_email='',  # Your email here
                        recipient_list=sendto,
                        fail_silently=False,
                    )
                    
                    # Mark the reminder as sent
                    reminder.is_sent = True
                    reminder.save()
                    print(f"Reminder for {appointment.appEmail} sent successfully!")
                else:
                    raise ValueError(f"Invalid or missing email for appointment {appointment}")
        
        except Exception as e:
            print(f"Error sending email: {str(e)}")
    
    # Render the template with reminders and error_message
    return render(request, 'doctorAdmin/reminders.html', {
            'reminders': reminders,
            'error_message': messages
        })


#-----------------------Set Reminders-------------------
def setReminder(request):
    current_date = timezone.now().date()
    # Filter for booked time slots with a future date
    # slot = timeslot.objects.filter(isBooked=True, date__gt=current_date)
    slot = timeslot.objects.filter(isBooked=True)

    appoint = Appointment.objects.filter(time_slot__in=slot)
    messages=None
    print("111", slot)
    print("222", appoint)

    if request.method == 'POST':
        remind_time = request.POST.get('remTime')  # Reminder time in minutes
        token = request.POST.get('remToken')  # Reminder token
        print("Reminder Time:", remind_time)
        app = request.POST.get('selectAppoint')
        apDate = request.POST.get('apDate')
        appoint = get_object_or_404(Appointment, id=app)
        # Combine the date and time into a timezone-aware datetime object
        naive_datetime = datetime.combine(appoint.time_slot.date, appoint.time_slot.start_time)
        localized_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())

        # Calculate the updated reminder time
        try:
            remind_time_minutes = int(remind_time)  # Convert to integer minutes
        except ValueError:
            messages= "Invalid reminder time."
            return render(request,"doctorAdmin/setReminder.html",{"messages":messages})

        # Calculate total reminder time in minutes
        updated_datetime = localized_datetime - timedelta(minutes=remind_time_minutes)
        print("Updated Reminder Time:", updated_datetime)

        # Prepare the reminder message
        title = "Appointment Reminder"
        message = (
            f"\nDoctor: {appoint.appDoc.name}"
            f"\nDate: {appoint.time_slot.date}"
            f"\nTime: {appoint.time_slot.start_time}"
            f"\nToken: {appoint.time_slot.apptoken}"
            f"\nToken Now: {token}"
        )
        
        print("Generated Message:", message)

        # Prepare data for the reminder serializer
        reminder_data = {
            'title': title,
            'message': message,
            'appointment': appoint,
            'reminder_time': updated_datetime,
            'reminder_token': token,
        }

        # Initialize the reminder instance and save it
        rem = Reminder(**reminder_data)
        try:
            rem.save()
            return redirect("/doctorAdmin/reminders")
        except Exception as e:
            print("Error saving reminder:", e)
            messages="Couldn't set Reminder.Try again Later"
            return render(request, 'doctorAdmin/setReminder.html', {'rem': rem,'messages': messages})
    return render(request,"doctorAdmin/setReminder.html",{"slots": slot, "appoint": appoint,'messages':messages})  # Return a proper response for GET
   


#------------------------Register as doctor-------------------------
def doctorRegistration(request):
    hosp = hospital.objects.all()
    special = specialization.objects.all()
    messages=None
    if request.method == 'POST':
        name = request.POST.get('name')
        descri = request.POST.get('descri')
        profile_pic = request.FILES.get('profile_pic')
        qualification = request.POST.get('qualification')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        print(profile_pic)
        # Attempt to convert latitude and longitude to floats
        district = request.POST.get('district')
        location =  request.POST.get('location')

        selectHosp = request.POST.get('selectHosp')
        selectSpecial = request.POST.get('selectSpecial')
        newHosp = request.POST.get('newHosp')
        newSpec = request.POST.get('newSpec')

        # Password validation and other checks
        if password != cpassword:
            messages='Passwords do not match'
            return render(request, 'doctorSection/doctorRegistration.html', {'hosp': hosp, 'special': special,'messages':messages})

        elif doctors.objects.filter(Email=email).exists():
            messages="Email already exists. Please use another Email"
            return render(request, 'doctorSection/doctorRegistration.html', {'hosp': hosp, 'special': special,'messages':messages})
        else:    
            try:
                if selectHosp == "new":
                    hosp_instance = hospital.objects.create(name=newHosp)
                    print(hosp_instance)
                else:
                    hosp_instance = hospital.objects.get(id=selectHosp)

                if selectSpecial == "new":
                    specialise_instance = specialization.objects.create(name=newSpec)
                    print(specialise_instance)
                else:
                    specialise_instance = specialization.objects.get(id=selectSpecial)

                # Create a new doctor instance
                doctor = doctors.objects.create(
                    name=name,
                    profile_pic=profile_pic,
                    qualification=qualification,
                    hosp=hosp_instance,
                    specialise=specialise_instance,
                    location=location,
                    district=district,
                    descri=descri,
                    Email=email,
                    password=password  # Make sure to hash the password
                )
                messages="Registration successful!.Please Login to continue"
                return render(request,'doctorSection/doctorRegistration.html',{'messages':messages})  # Redirect to login or another page
            except (hospital.DoesNotExist, specialization.DoesNotExist):
                messages='Invalid hospital or specialization selected'
                return render(request, 'doctorSection/doctorRegistration.html', {'hosp': hosp, 'special': special,'messages':messages})

    return render(request, 'doctorSection/doctorRegistration.html', {'hosp': hosp, 'special': special,'messages':messages})



#----------------------------------Doctor Login-----------------------------------------------------
def doctorLogin(request):
    messages=None
    request.session.flush()
    if request.method=='POST':
        Email=request.POST.get('username')
        password=request.POST.get('password')
        user=doctors.objects.filter(Email=Email,password=password)
        print("Email  ",Email,"Password  ",password)
        print("User  ",user)
        if user:
            request.session['Email']=Email
            current_user=Email
            return render(request,'doctorSection/doctorHome.html',{'current_user':current_user})
        else:
            messages='Invalid Username or Password'
            print(messages)
            return render(request,'doctorSection/doctorLogin.html',{"messages":messages})
    return render(request,'doctorSection/doctorLogin.html',{"messages":messages})


#----------------------------------Doctor Home----------------------------------------------------
def doctorHome(request):
    messages=None
    if 'Email' in request.session:
        current_user = request.session['Email']
        print(current_user)
        
        # Fetch the doctor or return a 404 if not found
        user = get_object_or_404(doctors, Email=current_user)
        
        appoint = Appointment.objects.filter(appDoc=user.id)
        slots = timeslot.objects.filter(timeForDoc=user.id)
        slotCount=slots.count()
        appointCount=appoint.count()
        print(user)
        return render(request, 'doctorSection/doctorHome.html', {
            'appoint': appoint,
            'slots': slots,
            'current_user': current_user,
            'appointCount':appointCount,
            'slotCount':slotCount
        })
    else:
        messages='Login to Continue'
        return render(request, 'doctorSection/doctorLogin.html', {'messages': messages})

#------------------------- Doctor Profile-------------------------------
def doctorProfile(request):
    messages=None
    if 'Email' in request.session:
        current_user = request.session['Email']
        print(current_user)
        
        # Fetch the doctor or return a 404 if not found
        doc = get_object_or_404(doctors, Email=current_user)
        return render(request,'doctorSection/doctorProfile.html',{'doc':doc,'current_user':current_user})
    else:
        messages="Login to Continue"
        return render(request,'doctorSection/doctorLogin.html',{'messages':messages})        

#------------------------- Doctor Apponitments-------------------------------
def doctorAppointments(request):
    messages=None
    if 'Email' in request.session:
        current_user = request.session['Email']
        print(current_user)
        if request.method=='POST':
            appDate=request.POST.get('slotDate')
        # Fetch the doctor or return a 404 if not found
            doc = get_object_or_404(doctors, Email=current_user)
            appoints=Appointment.objects.filter(appDoc=doc.id)
            slots=timeslot.objects.filter(timeForDoc=doc.id,date=appDate,isBooked=True)
            print(appoints,slots)
            if slots:
                return render(request,'doctorSection/doctorAppointments.html',{'appoints':appoints,'slots':slots,'current_user':current_user})
            else:
                messages="No appointments on this date"
                return render(request,'doctorSection/doctorAppointments.html',{'appoints':appoints,'slots':slots,'current_user':current_user,'messages':messages})
    else:
        messages="Login to Continue"
        return render(request,'doctorSection/doctorLogin.html',{'current_user':current_user,'messages':messages}) 
    return render(request,'doctorSection/doctorAppointments.html',{'current_user':current_user,'messages':messages}) 

#-----------------------------Doctor Create Timeslot-----------------
def doctorCreateTimeslot(request):
     messages=None
     if 'Email' in request.session:
        print(request.session['Email'])
        current_user=request.session['Email']
        print(current_user)
    #Get the doctor object by ID
        doc=doctors.objects.all()
        if request.method == 'POST':
            doctor=doctors.objects.get(Email=current_user)
            date = request.POST['slotDate']  # Get date from the form
            sTime = request.POST['slotSTime']  # e.g., '09:00'
            eTime = request.POST['slotETime']  # e.g., '17:00'
            slotDuration = int(request.POST['slotDuration'])  # Get slot duration in minutes
            token=0
            # Convert the string times to datetime.time objects
            start_time_obj = datetime.strptime(sTime, '%H:%M').time()
            end_time_obj = datetime.strptime(eTime, '%H:%M').time()
            
            # Initialize the starting time for iteration
            current_time = datetime.combine(datetime.today(), start_time_obj)
            end_time_limit = datetime.combine(datetime.today(), end_time_obj)
            
            print(f"Creating slots for Doctor ID: {doctor.id} from {current_time} to {end_time_limit}")
            
            # Loop through time, incrementing by slot duration
            while current_time.time() < end_time_obj:
                start_time = current_time.time()
                current_time += timedelta(minutes=slotDuration)
                end_time = current_time.time()
                token+=1
                print(f"Slot from {start_time} to {end_time}")
                
                # Create and save the time slot
                slot = timeslot(
                    timeForDoc_id=doctor.id,  # Assign the doctor ID
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    slotDuration=slotDuration,
                    apptoken=token
                )
                slot.save()  # Save the slot to the database
                print(f"Saved slot: {slot}")
                messages="Time slot created"    
        return render(request, 'doctorSection/doctorCreateTimeslot.html',{'doc':doc,'current_user':current_user,'messages':messages})
     

#-------------------------Doctor Display timeslot--------------------------
def doctorDispTimeslot(request):
     messages=None
     if 'Email' in request.session:
        print(request.session['Email'])
        current_user=request.session['Email']
        print(current_user)
        doctor=get_object_or_404(doctors,Email=current_user) 
        slots = None  # Initialize slots to None to handle the case of no slots found
        submitted_data = {
            'selectDoc': 'selectDoc',  # Default to an empty string
            'slotDate': 'slotDate',    # Default to an empty string
        }
        if request.method=='POST':
            # submitted_data['selectDoc'] = request.POST.get('selectDoc')
            submitted_data['slotDate'] = request.POST.get('slotDate')

            slots = timeslot.objects.filter(timeForDoc=doctor.id, date=submitted_data['slotDate'])  # Adjust based on your model
            print(slots)
            if not slots.exists():
                messages = "No time slots available for the selected doctor on this date."
        return render(request, 'doctorSection/doctorDispTimeSlot.html', {"doc":doctor, 'slots': slots, 'messages': messages,'submitted_data':submitted_data,'current_user':current_user})

#-----------------------------------------Doctor Logout-------------------------------------
def doctorLogout(request):
    messages=None
    if 'Email' in request.session:
        print(request.session['Email'])
        current_user=request.session['Email']
        print(current_user)
        print(request.session['Email'])
        if request.session['Email']:
            request.session.flush()
            request.session.pop('token')
            return redirect('/doctorSection/doctorLogin')
    return render(request,'doctorSection/doctorLogin.html',{'messages':messages})

#-----------------------Start OP of a Doctor-------------------------------------------------
def startOP(request):
    current_user = None
    token = 0
    messages=None
    if 'Email' in request.session:
        current_user = request.session['Email']
        print(current_user)

        if 'tok' in request.session:
            token = request.session['tok']
        request.session['tok'] = token  # This line might not be needed if token remains the same

    print(f"Token: {token}")
    
    return render(request, 'doctorSection/startOP.html', {'token': token, 'current_user': current_user,'messages':messages})

#-----------------------------Increment Token and send Reminder---------------------------
def incrementToken(request, token):
    current_user = None
    messages=None
    if 'Email' in request.session:
        current_user = request.session['Email']
        logger.info(f"Current user: {current_user}")
        doctor = get_object_or_404(doctors, Email=current_user)
        slot = timeslot.objects.filter(date=datetime.today().date(),isBooked=True)
        appoint = Appointment.objects.filter(appDoc=doctor.id, time_slot__in=slot)
        rem = Reminder.objects.filter(appointment__in=appoint)
        print(slot)
        if slot:

            try:
                token = int(token) + 1  # Increment token safely
                print("Token  ",token)
            except ValueError:
                logger.error("Token value is not an integer, defaulting to 1.")
                token = 1  # Default to 1 if increment fails

            request.session['tok'] = token

            for s in slot:

                # if token<=s.apptoken :
                print("Slot  ",slot," Appointment  ",appoint,"  Reminder ",rem)
                if rem:
                    for r in rem:
                        if r.reminder_token==token and r.is_sent==0:    
                            print(r)
                            sendSMS(r,current_user)
                            r.is_sent=1
                            r.save()
                logger.info(f"Appointments: {appoint}")
                logger.info(f"Reminders: {rem}")
                logger.info(f"New Token: {token}")
                # sendSMS(appoint,slot,current_user,"123")
        else:
            messages="No Time slots"
            return render(request, 'doctorSection/startOP.html', {'token': token, 'current_user': current_user,'messages':messages})
    return render(request, 'doctorSection/startOP.html', {'token': token, 'current_user': current_user,'messages':messages})

#send SMS confirmation
def sendSMS(rem,current_user):
    #  if 'Email' in request.session:
    #     print(request.session['Email'])
    #     current_user=request.session['Email']
    print(current_user,"Current USER")
    print (rem)
    account_sid = 'ACdb865cdf09521f8a25d78a099f5df936'
    auth_token = 'b40ae1fc5271fec3d27d168eba0a6bf9'
    client = Client(account_sid, auth_token)    
    print(rem.appointment.appContact)
    message = client.messages.create(
    from_='+18725886906',
    body=rem.message,
    to=str(rem.appointment.appContact)
    )
    print(message.sid)   



#---------Forgot Password for Doctors-------------------
def forgot_password_doctors(request):
    messages=None
    if request.method == 'POST':
        email = request.POST.get('username')
        print("Email received:", email)

        try:
            user = doctors.objects.get(Email=email)
            # Generate a unique token
            token = get_random_string(length=32)
            expiration_time = timezone.now() + timedelta(hours=1)

            print("User:", user, " Token:", token)

            # Save the token to the database
            PasswordResetToken.objects.create(user=user, token=token, expires_at=expiration_time)

            # Send email with the token
            send_mail(
                'Password Reset',
                f'Use this token to reset your password: {token}',
                '',  # This should be your verified sender email
                [email],
                fail_silently=False,
            )

            return redirect('/doctorsection/reset_password_doctors')
        except doctors.DoesNotExist:
            messages="User not found."
            return render(request, 'doctorSection/forgot_password_doctors.html', {"messages": messages})
        except Exception as e:
            print("An error occurred:", e)
            messages="An error occurred while processing your request."
            return render(request, 'doctorSection/forgot_password_doctors.html', {"messages": messages})

    return render(request, 'doctorSection/forgot_password_doctors.html', {"messages": messages})

def reset_password_doctors(request):
    messages=None
    if request.method == 'POST':
        token=request.POST.get('token')
        new_password = request.POST.get('password')
        c_password = request.POST.get('cpassword')
        print(new_password)
        # Find the user with the matching token
        user = get_object_or_404(PasswordResetToken, reset_token=token)
        if c_password==c_password:
        # Check if the token is still valid
            if user.token_expiration >= timezone.now():
                # Update the user's password
                user.Password = new_password  # Hash the password
                user.reset_token = None  # Clear the reset token
                user.token_expiration = None  # Clear expiration time
                user.save()
                print(user)
                messages= "Your password has been reset successfully."
                return redirect('doctorLogin')  # Redirect to login or another page
            else:
                messages="This token has expired."
    return render(request, 'doctorsection/reset_password_doctors.html',{'messages':messages})


#------------------------Edit Doctor Profile-----------------
def doctorModify(request):
    messages=None
    # Uncomment this block if you want to utilize the session for user email
    if 'Email' in request.session:
        current_user = request.session['Email']
        print(current_user)

        instance = get_object_or_404(doctors, Email=current_user)
        hosp = hospital.objects.all()
        special = specialization.objects.all()

        if request.method == 'POST':
            instance.name = request.POST.get('name', instance.name)

            # Handle profile picture
            if 'profile_pic' in request.FILES:
                instance.profile_pic = request.FILES['profile_pic']
            else:
                instance.profile_pic = 'static/images/doc.jpg'

            instance.qualification = request.POST.get('qualification', instance.qualification)
            instance.descri = request.POST.get('descri', instance.descri)

            # Handle hospital and specialization selection
            instance.hosp = get_object_or_404(hospital, id=request.POST['selectHosp'])
            instance.specialise = get_object_or_404(specialization, id=request.POST['selectSpecial'])

            # Update latitude and longitude
            instance.lat = request.POST.get('district', instance.district)
            instance.long = request.POST.get('location', instance.location)

            # Save the updated instance
            instance.save()

            messages="Doctor updated successfully!"
            return render(request, "doctorSection/doctorModify.html", {'instance': instance, 'hosp': hosp, 'special': special,'current_user':current_user,'messages':messages})

        return render(request, 'doctorSection/doctorModify.html', {'instance': instance, 'hosp': hosp, 'special': special,'current_user':current_user,'messages':messages})
    
def doctorChangePwd(request):
    messages=None
    if 'Email' in request.session:
        current_user = request.session['Email']
        print(current_user)

        instance = get_object_or_404(doctors, Email=current_user)  # Ensure the model name is correct

        if request.method == 'POST':
            new_password = request.POST.get('password', '')
            confirm_password = request.POST.get('cpassword', '')

            # Check if passwords match
            if new_password and new_password == confirm_password:
                instance.password = new_password  # Hash the password
                instance.save()
                messages="Password changed successfully!"
                return render(request,'doctorSection/doctorChangePwd.html', {'current_user': current_user,'messages':messages})  # Redirect to a success page or back to the change password page
            
            messages="Passwords do not match or are empty."

        return render(request, 'doctorSection/doctorChangePwd.html', {'current_user': current_user,'messages':messages})

    return render(request,'doctorSection/doctorLogin.html',{'messages':messages})  # Redirect to login if not authenticated

def createDocManager(request):
    messages=None
    if request.method=='POST':
       adminname=request.POST['name']
       email=request.POST['email']
       password=request.POST['password']
       verifypass=request.POST['cpassword']
       if password==verifypass:
            emailexists=Doctormanager.objects.filter(Email=email)
            if Doctormanager.objects.exists():
                messages='An admin is already registered.'
                return render(request, 'doctorManager/createDocManager.html',{'messages':messages})
            if emailexists:
                messages='Email already exists'
                return render(request, 'doctorManager/createDocManager.html',{'messages':messages})
            else:
                Doctormanager(Doctor_Boss=adminname,Email=email,Password=password).save()
                return redirect('docManagerLogin')
    return render(request,'doctorManager/createDocManager.html',{'messages':messages})

def docManagerLogin(request):
    messages=None
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        admin=Doctormanager.objects.filter(Email=email,Password=password)
        if admin:
            return redirect('doctorAdminHome')
        else:
            messages='Invalid Credentials'

    return render(request,'doctorManager/docManagerLogin.html',{'messages':messages})

#---------Forgot Password for Managers-------------------
def forgot_password_managers(request):
    messages=None
    if request.method == 'POST':
        email = request.POST.get('username')
        print("Email received:", email)

        try:
            user = Doctormanager.objects.get(Email=email)
            # Generate a unique token
            token = get_random_string(length=32)
            expiration_time = timezone.now() + timedelta(hours=1)

            print("User:", user, " Token:", token)

            # Store the token and expiration in the user model or a separate model
            user.reset_token = token
            user.token_expiration = expiration_time
            user.save()


            # Send email with the token
            send_mail(
                'Password Reset',
                f'Use this token to reset your password: {token}',
                'ekparvathi@gmail.com',  # This should be your verified sender email
                [email],
                fail_silently=False,
            )

            return redirect('/doctorAdmin/reset_password_managers')

        except doctors.DoesNotExist:
            messages= "User not found."
            return render(request, 'doctormanager/forgot_password_managers.html', {"messages":messages})
        except Exception as e:
            print("An error occurred:", e)
            messages="An error occurred while processing your request."
            return render(request, 'doctormanager/forgot_password_managers.html', {"messages": messages})

    return render(request, 'doctormanager/forgot_password_managers.html',{'messages':messages})



def reset_password_managers(request):
    messages=None
    if request.method == 'POST':
        token=request.POST.get('token')
        new_password = request.POST.get('password')
        c_password = request.POST.get('cpassword')
        print(new_password)
        # Find the user with the matching token
        user = get_object_or_404(Doctormanager, reset_token=token)
        if c_password==c_password:
        # Check if the token is still valid
            if user.token_expiration >= timezone.now():
                # Update the user's password
                user.Password = new_password  # Hash the password
                user.reset_token = None  # Clear the reset token
                user.token_expiration = None  # Clear expiration time
                user.save()
                print(user)
                messages="Your password has been reset successfully."
                return redirect('docManagerLogin',{'messages':messages})  # Redirect to login or another page
            else:
                messages="This token has expired."
                return render(request, 'doctormanager/reset_password_managers.html',{'messages':messages})

    return render(request, 'doctormanager/reset_password_managers.html',{'messages':messages})
