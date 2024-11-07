from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.decorators import api_view
from .models import Admindata,DeliveryFee,Foodmanager,Jobmanager,BuySellmanager,Doctormanager
from django.contrib import messages
from foodsection.models import RestaurantReview,Orders,Categories
from usersection.models import Userinfo,Userpersonal_data
from restaurant.models import RestaurantRegistration,Menu_Lists,Promo
from django.db.models import Avg
import smtplib
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator

# Create your views here.

def createadmin(request):
    if request.method=='POST':
       adminname=request.POST['name']
       email=request.POST['email']
       password=request.POST['password']
       verifypass=request.POST['repassword']
       if password==verifypass:
            emailexists=Admindata.objects.filter(Email=email)
            if Admindata.objects.exists():
                messages.error(request, 'An admin is already registered.')
                return render(request, 'admintemp/create.html')
            if emailexists:
                messages.error(request,'Email already exists')
            else:
                Admindata(Admin_Name=adminname,Email=email,Password=password).save()
                return redirect('adminlogin')
    return render(request,'admintemp/create.html')

def updateadmin(request):
    # Get the existing admin instance
    admin = Admindata.objects.first()  # Assumes there's only one admin instance

    if request.method == 'POST':
        adminname = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        verifypass = request.POST['repassword']

        # Check if passwords match
        if password != verifypass:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'admintemp/updateadmin.html', {'admin': admin})

        # Check if the email already exists for another admin
        if Admindata.objects.filter(Email=email).exclude(pk=admin.pk).exists():
            messages.error(request, 'Email already exists for another admin.')
            return render(request, 'admintemp/updateadmin.html', {'admin': admin})

        # Update the admin data
        admin.Admin_Name = adminname
        admin.Email = email
        admin.Password = password # Hash the password
        admin.save()

        messages.success(request, 'Admin updated successfully.')
        return redirect('adminlogin')

    return render(request, 'admintemp/updateadmin.html', {'admin': admin})
    
            
# def adminlogin(request):
#     if request.method=='POST':
#         adminemail=request.POST['email']
#         password=request.POST['password']
#         admin=Admindata.objects.filter(Email=adminemail,Password=password)
#         if admin:
#             return redirect('home')
#         else:
#             messages.error(request,'Invalid Credentials')

#     return render(request,'admintemp/login.html')
def adminlogin(request):
    if request.method == 'POST':
        adminemail = request.POST['email']
        password = request.POST['password']
        
        admin = Admindata.objects.filter(Email=adminemail, Password=password).first()
        
        if admin:
            request.session['admin_id'] = admin.id  
            request.session['admin_email'] = admin.Email 

            return redirect('home')  
        else:
            messages.error(request, 'Invalid Credentials')

    return render(request, 'admintemp/login.html')

def adminhome(request):
    
    return render (request,'admintemp/adminhome.html')

    
def restaurantdashbord(request):
    Restaurants_data=RestaurantRegistration.objects.all()
    no_restauarnt=Restaurants_data.count()
    orders=Orders.objects.all()
    cancelledorders=Orders.objects.filter(status='Order Cancelled')
    no_canceled=cancelledorders.count()
    sucessorders=Orders.objects.filter(status='Order Delivered')
    num_success=sucessorders.count()
    ongoingorders=Orders.objects.filter(status='Order Accepted')
    num_ongoing=ongoingorders.count()
    promos=Menu_Lists.objects.filter(OfferCoupon__gte=1)
    num_promos=promos.count()
    menulists=Menu_Lists.objects.all()
    total_menu=menulists.count()
    total_orders=orders.count()
    return render (request,'adminrestaurant/dashbord.html',{'restaurant':Restaurants_data,'no_restau':no_restauarnt,'totalorders':total_orders,'totalmenu':total_menu,'total_cancelation':no_canceled,'successorders':num_success,'ongoing':num_ongoing,'totalpromo':num_promos})

def admin_restaurant(request):
    Restaurants_data=RestaurantRegistration.objects.all()
    if request.method=='POST':
        search=request.POST['search']
        results=RestaurantRegistration.objects.filter(Restaurant_Name__icontains=search)
        return render(request,'adminrestaurant/searchedrestau.html',{'result':results})
    return render (request,'adminrestaurant/restau_info.html',{'restaurant':Restaurants_data})


def viewrestaurantdata(request,id):
    restaurants=RestaurantRegistration.objects.get(id=id)
    
    return render (request,'adminrestaurant/restau_detail.html',{'restaurant_data':restaurants})

def rating(request,id):
    rating_data=RestaurantReview.objects.filter(Restaurant_id=id)
    average_rating = rating_data.aggregate(Avg('Rating'))['Rating__avg']

    rating_review=[]
    for i in rating_data:
        rating_review.append({
            'Customer_Name':i.Customer_Name,
            'Review':i.Review,
            'Rating':i.Rating
        })
    return render(request,'adminrestaurant/rating.html',{'rating_data':rating_review,'averagerating':average_rating})

def restaurantmenu(request,id):
    menu_data=Menu_Lists.objects.filter(Restaurant_id=id)
    return render(request,'adminrestaurant/restau_menu.html',{'menu_data':menu_data,})

def orderhistory(request,id):
    orders_data=Orders.objects.filter(Restaurant_id=id).order_by('-DateTime')
    
    return render(request,'adminrestaurant/orderhistory.html',{'order_data':orders_data})

def deleterestaurant(request,id):
    restauarnt=RestaurantRegistration.objects.get(id=id)
    restauarnt.delete()
    return redirect('restaurantdata')

def userinfo(request):
    user=Userinfo.objects.all()
    return render(request,'usersadmin/user_data.html',{'user':user})

def viewuser(request, id):
    user = Userinfo.objects.get(id=id)
    user_password = user.Password
    user_personaldata = None  # Initialize as None

    try:
        user_personaldata = Userpersonal_data.objects.get(User_id=id)
    except Userpersonal_data.DoesNotExist:
        messages.error(request, 'No data available for this user.')

    return render(request, 'usersadmin/viewuser.html', {'password': user_password, 'personal_data': user_personaldata})

def deleteuser(request,id):
    user=Userinfo.objects.get(id=id)
    user.delete()
    return redirect('userinfo')


def deliveryfee(request):
    if request.method=='POST':
        range=request.POST['distance']
        price=request.POST['deliveryfee']
        if not range or not price:
            messages.error(request, 'Please provide both distance and delivery fee.')
            return render(request, 'deliveryfee.html')
        try:
            DeliveryFee.objects.create(Range=range,Deliveryfee=price)
        except Exception as e:
            messages.error(request, f'Something went wrong: {str(e)}')
    return render(request,'adminrestaurant/deliveryfee.html')

def adminindex(request):
    return render(request,'index.html')

def getdeliveryfee(request):
    delivery_fee=DeliveryFee.objects.all()
    return render(request,'adminrestaurant/getdelivery.html',{'deliveryfee':delivery_fee})

def removedeliveryfee(request,id):
    delivery_fee = get_object_or_404(DeliveryFee, id=id)

    delivery_fee.delete()
    return redirect('getdeliveryfee')



def update_delivery_fee(request):
    if request.method == 'POST':
        # Update existing ranges
        for fee in DeliveryFee.objects.all():
            range_key = f'range_{fee.id}'
            fee_key = f'fee_{fee.id}'

            if range_key in request.POST and fee_key in request.POST:
                fee.Range = request.POST[range_key]
                fee.Deliveryfee = request.POST[fee_key]
                fee.save()
    deliveryfee = DeliveryFee.objects.all()
    return render(request, 'adminrestaurant/getdelivery.html', {'deliveryfee': deliveryfee})

def totalorders(request):
    orders=Orders.objects.all().order_by('-DateTime')
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')  # Get the current page number from query parameters
    page_obj = paginator.get_page(page_number)
    return render(request,'adminrestaurant/totalorders.html',{'totalorder':page_obj})


def online_payment_received(request):
    orders=Orders.objects.filter(Payment_method="Paid via Razorpay").order_by('-DateTime')
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')  # Get the current page number from query parameters
    page_obj = paginator.get_page(page_number)
    return render(request,'adminrestaurant/razor_pay_rece.html',{'totalorder':page_obj})
    

def fullmenu(request):
    fullmenu=Menu_Lists.objects.all()
    paginator = Paginator(fullmenu, 5)  # Show 10 orders per page
    page_number = request.GET.get('page')  # Get the current page number from query parameters
    page_obj = paginator.get_page(page_number)
    return render(request,'adminrestaurant/fullmenu.html',{'fullmenu':page_obj})

def categories(request):
    categories=Categories.objects.all()
    return render(request,'adminrestaurant/categories.html',{'categories':categories})

def viewbycategory(request,id):
    category=Categories.objects.get(id=id)
    category_name=category.Categorie_name
    menuitems=Menu_Lists.objects.filter(Category=category_name)
    return render(request,'adminrestaurant/viewbycategory.html',{'items':menuitems})


def totalusers(request):
    users=Userinfo.objects.all()
    totalusers=users.count()
    return render(request,'usersadmin/userdashbord.html',{'totalusers':totalusers})

# def forgotpass(request):
#     if request.method=='POST':
#         email=request.POST['email']

#         try:
#             user=Admindata.objects.get(Email=email)
#         except Admindata.DoesNotExist:
#             messages.error(request,'user not exists')
#             return render(request, 'admintemp/forgotpassword.html')  # Return after error

#         password=user.Password
#         content=f"Your Password :{password}"
#         mail=smtplib.SMTP('smtp.gmail.com', 587)
#         mail.ehlo()
#         mail.starttls()
#         sender='suryakrishnavaliyapurakkal@gmail.com'
#         recipient=email
#         mail.login('suryakrishnavaliyapurakkal@gmail.com','vryl fwbx wiud wtco')
#         header = f'To: {email}\nFrom: {sender}\nSubject: PASSWORD\n'
#         full_message = header + '\n' + content
#         mail.sendmail(sender, recipient, full_message)
#         mail.close()
#     return render(request,'admintemp/forgotpassword.html')

def forgotpass(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = None
        password = None

        # List of models to search for the email
        models = [Admindata, Foodmanager, Jobmanager, Doctormanager, BuySellmanager]
        
        # Loop through each model to find a user with the given email
        for model in models:
            try:
                user = model.objects.get(Email=email)
                password = user.Password
                break  # Stop searching once the user is found
            except model.DoesNotExist:
                continue  # Move to the next model if user not found in current model

        if user is None:
            # If no user found in any model
            messages.error(request, 'User does not exist')
            return render(request, 'admintemp/forgotpassword.html')  # Return after error

        # Send email with password
        content = f"Your Password: {password}"
        try:
            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            sender = 'suryakrishnavaliyapurakkal@gmail.com'
            recipient = email
            mail.login(sender, 'vryl fwbx wiud wtco')
            header = f'To: {email}\nFrom: {sender}\nSubject: PASSWORD\n'
            full_message = header + '\n' + content
            mail.sendmail(sender, recipient, full_message)
            mail.close()
            messages.success(request, 'Password has been sent to your email')
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')

    return render(request, 'admintemp/forgotpassword.html')

def promodata(request):
    promotions=Promo.objects.all()
    return render(request,'adminrestaurant/promotions.html',{'promotion':promotions})

def createfoodboss(request):
    if request.method=='POST':
       adminname=request.POST['name']
       email=request.POST['email']
       password=request.POST['password']
       verifypass=request.POST['repassword']
       if password==verifypass:
            emailexists=Foodmanager.objects.filter(Email=email)
            if Foodmanager.objects.exists():
                messages.error(request, 'An admin is already registered.')
                return render(request, 'admintemp/create.html')
            if emailexists:
                messages.error(request,'Email already exists')
            else:
                Foodmanager(Food_Boss=adminname,Email=email,Password=password).save()
                return redirect('foodbosslogin')
    return render(request,'foodmanager/createmanager.html')


def managerLogin(request):
    
    return render(request,'admintemp/choosemanager.html')

def foodbosslogin(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        admin=Foodmanager.objects.filter(Email=email,Password=password)
        if admin:
            return redirect('restaurantdata')
        else:
            messages.error(request,'Invalid Credentials')

    return render(request,'foodmanager/foodbosslogin.html')

def createjobboss(request):
    if request.method=='POST':
       adminname=request.POST['name']
       email=request.POST['email']
       password=request.POST['password']
       verifypass=request.POST['repassword']
       if password==verifypass:
            emailexists=Jobmanager.objects.filter(Email=email)
            if Jobmanager.objects.exists():
                messages.error(request, 'An admin is already registered.')
                return render(request, 'jobmanager/create.html')
            if emailexists:
                messages.error(request,'Email already exists')
            else:
                Jobmanager(Job_Boss=adminname,Email=email,Password=password).save()
                return redirect('adminlogin')
    return render(request,'jobmanager/create.html')



def jobbosslogin(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        admin=Jobmanager.objects.filter(Email=email,Password=password)
        if admin:
            return redirect('restaurantdata')
        else:
            messages.error(request,'Invalid Credentials')

    return render(request,'jobmanager/login.html')





def createbuysellManager(request):
    if request.method=='POST':
       name=request.POST['name']
       email=request.POST['email']
       password=request.POST['password']
       repassword=request.POST['retype_password']
       if password==repassword:
            emailexists=BuySellmanager.objects.filter(Email=email)
            if BuySellmanager.objects.exists():
                messages.error(request, 'An admin is already registered.')
                return render(request, 'buysellmanager/create.html')
            if emailexists:
                messages.error(request,'Email already exists')
            else:
                BuySellmanager(Buysell_Boss=name,Email=email,Password=password).save()
                return redirect('buysell-manager-login')

    return render(request,'buysellmanager/create.html')


from django.db.models import Sum


def buysellManagerLogin(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        admin=BuySellmanager.objects.filter(Email=email,Password=password)
        if admin:
            return redirect('admin-dashboard')
        else:
            messages.error(request,'Invalid Credentials')
    return render(request,'buysellmanager/login.html')




# def forgotpass_buysell_managers(request):
    
#     return render (request,'buysellmanager/forgot_password.html')


def revenue_calcu(request):
    context = {
            'orders': 0,
            'total_revenue': 0,
            'start_date': None,
            'end_date': None,
            'payment_method': 'both',  # Default to 'both'
    }

        # Retrieve date range and payment method from GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payment_method = request.GET.get('payment_method', 'both')  

        # Base query with restaurant filter
    orders_query = Orders.objects.filter(status="Order Delivered")

        # Only apply filters if start and end dates are provided
    if start_date and end_date:
        orders_query = orders_query.filter(DateTime__range=(start_date, end_date))

        # Apply payment method filter if specified
    if payment_method == 'cash_on_delivery':
        orders_query = orders_query.filter(Payment_method='cash_on_delivery')
    elif payment_method == 'online_payment':
        orders_query = orders_query.filter(Payment_method='online_payment')

        # Calculate total revenue and order count
    total_revenue = orders_query.aggregate(Sum('TotalPrice'))['TotalPrice__sum'] or 0
    order_count = orders_query.count()
        
        # Update context with calculated values
    context['orders'] = order_count
    context['total_revenue'] = total_revenue
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['payment_method'] = payment_method

    return render(request, 'adminrestaurant/revenue.html', {'revenue': context})    

        
        
    