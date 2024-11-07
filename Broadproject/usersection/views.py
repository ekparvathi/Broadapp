from django.shortcuts import render

# Create your views here.
from .models import Userinfo,Userpersonal_data
from .serializers import RegisterSerializer,LoginSerializer,userdataSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import smtplib
from twilio.rest import Client
import random
import string
from rest_framework import status
from django.shortcuts import get_object_or_404


# Create your views here.
def verify_phone(phone):
    api_key='9b2521b53975490fb81d04e45ae45628'
    url="https://phonevalidation.abstractapi.com/v1"
    params = {
        'api_key':api_key,
        'phone':phone
    }
    try:
        response = requests.get(url, params=params,timeout=10)

        result = response.json()

        # Log the API response for debugging
        print(f"Phonenumber Verification Response: {result}")

        # Check if the email status is valid
        if result.get('valid')==True:
            return True
        else:
            # Log the reason for failure
            error_message = result.get('error', 'Unknown error')
            print(f"Phone number verification failed: {error_message}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error verifying phone: {e}")
        return False

def verify_email_abstract(email):
    # Abstract API email verification URL
    url = "https://emailvalidation.abstractapi.com/v1/"
    
    # Your Abstract API key
    api_key = 'de0d04f6649e46bdba8acbfb36f9e6b5'

    # Construct the request
    params = {
        'api_key': api_key,
        'email': email,
    }

    try:
        # Send the request to Abstract API
        response = requests.get(url, params=params)

        # Parse the response
        result = response.json()

        # Log the API response for debugging
        print(f"Email Verification Response: {result}")

        # Check if the email is valid
        if result.get('deliverability') == 'DELIVERABLE':
            return True
        else:
            print(f"Email verification failed: {result.get('quality_score')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error verifying email: {e}")
        return False


    
@api_view(['POST'])
def Createuser(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            email = request.data.get('Email')
            phone = request.data.get('Phonenumber')

            # Check if the email already exists in the database
            if Userinfo.objects.filter(Email=email).exists():
                return Response({'error': 'Email address already exists. Please use a different email.'}, status=400)
            if Userinfo.objects.filter(Phonenumber=phone).exists():
                return Response({'error': 'Phonenumber already exists. Please use a different phone.'}, status=400)
            if verify_phone(phone):
                if verify_email_abstract(email):
                    serializer.save()
                    return Response({'msg':'Rgisteration success'},status=200)
                else:
                    return Response({'error': 'Invalid or inactive Email. Please enter a valid Email ID.'}, status=400)
 
            else:
                return Response({'error': 'Invalid or inactive phone number. Please enter a valid phone number.'}, status=400)

            
        else:         
                    
            return Response(serializer.errors, status=400)

@api_view(['POST'])
def Login(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():           
            email = serializer.validated_data['Email']
            password = serializer.validated_data['Password']
            user = Userinfo.objects.filter(Email=email, Password=password).first()
            
            if user:
                # Create a session
                request.session['user_id'] = user.id
                request.session['Email'] = user.Email
                
                return Response({'msg': 'Login Success','id':user.id})
            else:
                return Response({'msg': 'Email or Password is incorrect'})
        else:
            return Response({'msg': 'Something went wrong'})


@api_view(['POST'])
def forgot_password(request):
    email=request.data.get('Email')
    try:
        instance=Userinfo.objects.get(Email=email)
    except Userinfo.DoesNotExist:
        return Response({'msg':'User not exists'})
    if request.method=='POST':
        return Response({'Phonenumber':instance.Phonenumber,'email':email})
    

def generate_otp(length=4):
    return ''.join(random.choices(string.digits, k=length))

@api_view(['POST'])
def request_otp(request):
    phone=request.data.get("Phonenumber")
    user=Userinfo.objects.get(Phonenumber=phone)
    otp = generate_otp()
        
        # Twilio credentials
    TWILIO_ACCOUNT_SID = 'ACd49593b2e12c63d313b6e694bfdda05a'
    TWILIO_AUTH_TOKEN = '47b1be65db4d018fe90a431cb59cf33d'
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    TWILIO_PHONE_NUMBER = '+12132961360'
   
        # Send OTP via SMS or Email
    message = client.messages.create(
                body=f"Your OTP code is {otp}",
                from_=TWILIO_PHONE_NUMBER,
                to=phone
            )        
    if message.sid :
        request.session['otp'] = otp
        request.session['user_id'] = user.id

        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def sendotp_email(request):
    email=request.data.get('Email')

    try:
        user=Userinfo.objects.get(Email=email)
    except Userinfo.DoesNotExist:
        return Response({'msg':'user not exists'})
    try:
        otp=generate_otp()
        content=f"Your OTP code :{otp}"
        mail=smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        sender='suryakrishnavaliyapurakkal@gmail.com'
        recipient=email
        mail.login('suryakrishnavaliyapurakkal@gmail.com','vryl fwbx wiud wtco')
        header = f'To: {email}\nFrom: {sender}\nSubject: OTP Code\n'
        full_message = header + '\n' + content
        mail.sendmail(sender, recipient, full_message)
        mail.close()
        if user:
            request.session['otp'] = otp
            request.session['Email']=user.Email

        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
    except smtplib.SMTPException as e:
        return Response({'error': f'Failed to send OTP: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
@api_view(['POST'])
def verify_otp_and_reset_password(request):
    # if 'Email' in request.session:
    #     current_user=request.session['Email']
    otp = request.data.get('otp')
    session_otp = request.session.get('otp')
    # current_user=request.data.get('Email')
    if otp == session_otp:
        # user = Userinfo.objects.get(Email=current_user)
        # user.Password=request.data.get('Password')
        # user.save()

        return Response({'message': 'OTP verification success'}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)    
    # else:
    #     return Response({'msg':'something went wrong'})


   
@api_view(['PUT'])
def changepassword(request):
    if 'Email' not in request.session:
        return Response({'msg': 'Something went wrong'}, status=400)
    
    current_user_email = request.session['Email']

    try:
        user = Userinfo.objects.get(Email=current_user_email)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'User not found'}, status=404)

    new_password = request.data.get('Password')
    
    if not new_password:
        return Response({'msg': 'Password not provided'}, status=400)
    
    # Use set_password to securely update the password
    user.Password=new_password
    user.save()

    return Response({'msg': 'Password changed successfully'}, status=200)


@api_view(['POST'])
def createuserdata(request):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=Userinfo.objects.get(Email=current_user)
    else:
        return Response({'msg':'User not authenticated'})
    # try:
    #     # Retrieve the existing user personal data object by the User_id (user.id)
    #     userdata = get_object_or_404(Userpersonal_data, User_id=user.id)
    # except Userpersonal_data.DoesNotExist:
    #     return Response({'msg': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # request.data['User_id'] = user.id

    if request.method=='POST':
        request.data['User_id'] = user.id
        serializer=userdataSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'Data saved Successfully'})
        else:
            return Response({'msg':'Something Went wrong'})
        


@api_view(['POST'])
def logout(request):
    # Clear the session data
    request.session.flush()  # This will delete the session data
    return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)