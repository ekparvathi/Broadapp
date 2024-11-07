from django.urls import path
from usersection import views
urlpatterns = [
    path('createuser/',views.Createuser,name='createuser'),
    path('login/',views.Login,name='login'),
    path('forgotpassword/',views.forgot_password,name='forgotpassword'),
    path('sendotpphone/',views.request_otp,name='requestotp'),
    path('verifyotp/',views.verify_otp_and_reset_password,name='verifyotp'),
    path('sendotpemail/',views.sendotp_email,name='sendotpviaemail'),
    path('addaddress/',views.createuserdata,name='updateuser'),
    path('changepassword/',views.changepassword,name='changepassword'),
    path('logout/',views.logout,name='logout')
  
]