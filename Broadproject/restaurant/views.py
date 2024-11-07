from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from geopy.geocoders import Nominatim
from restaurant.models import RestaurantRegistration,Menu_Lists,Promo,Promousage
from datetime import date
from django.contrib import messages
import requests
from django.http import JsonResponse
from foodsection.models import Orders,RestaurantReview,Categories
from django.db.models import Avg
from adminsection.models import DeliveryFee
import smtplib
import datetime
from django.db.models import Sum
from django.core.paginator import Paginator

# Create your views here.
def verify_phone(phonenumber):
    api_key='9b2521b53975490fb81d04e45ae45628'
    url="https://phonevalidation.abstractapi.com/v1"
    params = {
        'api_key':api_key,
        'phone':phonenumber,
        'country':"IN"
        
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




def RegisterRestaurant(request):
    geolocator = Nominatim(user_agent="GetLoc")

    if request.method=='POST':
        restauarant_name=request.POST['restaurantname']
        owner_name=request.POST['OwnerName']
        phonenumber=request.POST['phonenumber']
        phone = f"+91{phonenumber}"
        email=request.POST['email']
        openingtime=request.POST['optime']
        closingtime=request.POST['cltime']
        password=request.POST['password']
        verifypass=request.POST['verifypass']
        image=request.FILES.get('Image')
        district=request.POST['district']
        place=request.POST['place']
        if password==verifypass:
            address=f"{district}, {place}"
            location = geolocator.geocode(address)
            print(location)
            if verify_phone(phonenumber):
                if verify_email_abstract(email):
                    if location:
                        coords = f"{location.latitude}, {location.longitude}"
                        location = coords
                        dateofreg=date.today()
                        try:
                            RestaurantRegistration.objects.create(Restaurant_Name=restauarant_name,Owner_Name=owner_name,
                                                District=district,Place=place,Phonenumber=phone,Email=email,Image=image,
                                                Password=password,Opening_time=openingtime,Closing_time=closingtime,Location=location,
                                                DateOfRegistration=dateofreg)
                            messages.success(request, "Restaurant registered successfully!")
                        except Exception as e:
                            messages.error(request, f"Error saving restaurant: {str(e)}")
                    else:
                        messages.error(request,'unavialable Location')
                else:
                    messages.error(request,'Invalid Email ID')
            else:
                messages.error(request,'Invalid Phonenumber')
        else:
            messages.error(request,'Password not same as above')
            
            
    return render(request,'restaurantfolder/reg_restau.html')


def login(request):
    if request.method=='POST':
        email=request.POST['Email']
        password=request.POST['Password']
        user=RestaurantRegistration.objects.filter(Email=email,Password=password).first()
        if user:
            request.session['Email'] = user.Email
            messages.success(request,'Login Sucess')
            return redirect('index')
        else:
            messages.error(request,'Invalid Email or Password')
    return render(request,'restaurantfolder/restau_login.html')
def index(request):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=RestaurantRegistration.objects.filter(Email=current_user).first()
        menulists=Menu_Lists.objects.filter(Restaurant=user).count()
        orders=Orders.objects.filter(Restaurant_id=user).count()
        deliveredorders=Orders.objects.filter(Restaurant_id=user,status='Order Delivered').count()
        canceledorders=Orders.objects.filter(Restaurant_id=user,status='Order Canceled').count()
        review=RestaurantReview.objects.filter(Restaurant_id=user).count()
        deliveryfee=DeliveryFee.objects.all()
        review_rating = RestaurantReview.objects.filter(Restaurant_id=user)
       
        average_rating = review_rating.aggregate(Avg('Rating'))['Rating__avg']
    return render(request,'restaurantfolder/index.html',{'user':user,'menucount':menulists,'ordercount':orders,'reviewcount':review,'deliveredorder':deliveredorders,'canceledorder':canceledorders,'deliveryfee':deliveryfee,'averagerating':average_rating})
def profile(request):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=RestaurantRegistration.objects.filter(Email=current_user).first()
        return render(request,'restaurantfolder/profile.html',{'user':user})
    else:
        return redirect('login')  # Redirect to login if not authenticated
    


def add_menu(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')  # Redirect to login if user not found

        if request.method == 'POST':
            restaurant = user
            restaurantname = user.Restaurant_Name
            item = request.POST.get('item')  # Use .get() to avoid MultiValueDictKeyError
            category = request.POST.get('category')
            description = request.POST.get('description')
            price = request.POST.get('price')
            offercoupon = request.POST.get('offercoupon')
            deliveryoffer = request.POST.get('delivery')
            image = request.FILES.get('image')

            # Check if all required fields are present
            if not all([item, category, description, price, offercoupon, deliveryoffer, image]):
                messages.error(request, 'Please fill in all fields.')
                return render(request, 'restaurantfolder/addmenu.html')

            Menu_Lists.objects.create(
                Restaurant=restaurant,
                Restaurant_Name=restaurantname,
                Item=item,
                Category=category,
                Description=description,
                Price=price,
                OfferCoupon=offercoupon,
                DeliveryOffer=deliveryoffer,
                Image=image
            )
            messages.success(request, 'Added Successfully!')
            existingcategory=Categories.objects.filter(Categorie_name=category)
            if existingcategory:
                return redirect('addmenu')
            else:
                Categories.objects.create(Categorie_name=category)
            return redirect('addmenu')  # Redirect after successful addition

        return render(request, 'restaurantfolder/addmenu.html')  # Show the form if GET request
    else:
        return redirect('login')  # Redirect to login if not authenticated


def list_menu_items(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')  # Redirect to login if user not found
        menu_items = Menu_Lists.objects.filter(Restaurant=user)  # Fetch all menu items
    else:
        messages.error(request, 'Login first')
        return redirect('login')  
    return render(request, 'restaurantfolder/listmenu.html', {'menu_items': menu_items})

def order_list(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')
        orders = Orders.objects.filter(Restaurant_id=user).order_by('-id') 
        paginator = Paginator(orders, 10)  # Show 10 orders per page
        page_number = request.GET.get('page')  # Get the current page number from query parameters
        page_obj = paginator.get_page(page_number)
    else:
        messages.error(request, 'Login first')
        return redirect('login') 
    return render(request, 'restaurantfolder/orders.html', {'orders': page_obj})

def accepted_list(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')
        orders = Orders.objects.filter(Restaurant_id=user,status='Order Accepted')

    else:
        messages.error(request, 'Login first')
        return redirect('login') 
    return render(request, 'restaurantfolder/acceptorder.html', {'orders': orders})

def canceled_order(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')
        orders = Orders.objects.filter(Restaurant_id=user,status='Order Cancelled')

    else:
        messages.error(request, 'Login first')
        return redirect('login') 
    return render(request, 'restaurantfolder/cancelorder.html', {'orders': orders})

def delivered_order(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')
        orders = Orders.objects.filter(Restaurant_id=user,status='Order Delivered')

    else:
        messages.error(request, 'Login first')
        return redirect('login') 
    return render(request, 'restaurantfolder/deliverdorder.html', {'orders': orders})

def orderdetail(request,id):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')
        orders = Orders.objects.filter(id=id,Restaurant_id=user).first()
        
    else:
        messages.error(request, 'Login first')
        return redirect('login') 
    return render(request, 'restaurantfolder/orderdetail.html', {'orders': orders})

def update_availability(request, id):
    if request.method == 'POST':
        # Fetch the menu item by its ID
        menu_item = get_object_or_404(Menu_Lists, id=id)

        # Toggle the availability
        if menu_item.Availability == 'Available':
            menu_item.Availability = 'Unavailable'
        else:
            menu_item.Availability = 'Available'

        # Save the updated item
        menu_item.save()

        # Redirect back to the menu list after updating
        return redirect('list_menu_items')

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


def acceptorder(request,id):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')
        orders = Orders.objects.filter(id=id,Restaurant_id=user).first()
        if orders:
            # Update the order status to 'Order Accepted'
            orders.status = 'Order Accepted'
            orders.save()  # Save the changes to the database
            messages.success(request, 'Order has been accepted')
        else:
            messages.error(request, 'Order not found or does not belong to your restaurant')

    else:
        messages.error(request, 'Login first')
        return redirect('login')

    return redirect('orderdetail',id=id)

def cancelorder(request,id):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')
        orders = Orders.objects.filter(id=id,Restaurant_id=user).first()
        if orders:
            # Update the order status to 'Order Accepted'
            orders.status = 'Order Cancelled'
            orders.save()  # Save the changes to the database
            messages.success(request, 'Order Cancelled')
        else:
            messages.error(request, 'Order not found or does not belong to your restaurant')

    else:
        messages.error(request, 'Login first')
        return redirect('login')

    return redirect('orderdetail',id=id)

    
def orderdelivered(request,id):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')
        orders = Orders.objects.filter(id=id,Restaurant_id=user).first()
        if orders:
            # Update the order status to 'Order Accepted'
            orders.status = 'Order Delivered'
            orders.save()  # Save the changes to the database
            messages.success(request, 'Order Delivered')
        else:
            messages.error(request, 'Order not found or does not belong to your restaurant')

    else:
        messages.error(request, 'Login first')
        return redirect('login')

    return redirect('orderdetail',id=id)

def review_ratings(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')
        review_rating = RestaurantReview.objects.filter(Restaurant_id=user)
        average_rating = review_rating.aggregate(Avg('Rating'))['Rating__avg']

    else:
        messages.error(request, 'Login first')
        return redirect('login')
    return render(request,'restaurantfolder/rating.html',{'rating':review_rating,'averagerating':average_rating})


def logout_view(request):
    if 'Email' in request.session:
        # Clear the session data
        del request.session['Email']
    else:
        messages.info(request, 'You are not logged in.')
    
    return redirect('login')  

def updaterestaurant(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()
        if not user:
            messages.error(request, 'Login first')
            return redirect('login')

        geolocator = Nominatim(user_agent="GetLoc")

        # Initialize form variables with existing user data
        restaurant_name = user.Restaurant_Name
        owner_name = user.Owner_Name
        phone = user.Phonenumber[3:]  # Assuming the phone number is stored with country code
        email = user.Email
        opening_time = user.Opening_time
        closing_time = user.Closing_time
        district = user.District
        place = user.Place
        image = user.Image

        if request.method == 'POST':
            restaurant_name = request.POST['restaurantname']
            owner_name = request.POST['OwnerName']
            phonenumber = request.POST['phonenumber']
            phone = f"+91{phonenumber}"
            email = request.POST['email']
            opening_time = request.POST['optime']
            closing_time = request.POST['cltime']
            password = request.POST['password']
            verifypass = request.POST['verifypass']
            image = request.FILES.get('Image') if request.FILES.get('Image') else user.Image  # Use existing image if not updated
            district = request.POST['district']
            place = request.POST['place']

            if password == verifypass:
                address = f"{district}, {place}"
                location = geolocator.geocode(address)
                print(location)

                if verify_phone(phonenumber):
                    if verify_email_abstract(email):
                        if location:
                            coords = f"{location.latitude}, {location.longitude}"
                            location = coords
                            # Update the restaurant registration entry
                            try:
                                user.Restaurant_Name = restaurant_name
                                user.Owner_Name = owner_name
                                user.Phonenumber = phone
                                user.Email = email
                                user.Image = image
                                user.Password = password
                                user.Opening_time = opening_time
                                user.Closing_time = closing_time
                                user.District = district
                                user.Place = place
                                user.Location = location
                                user.save()  # Save updated data
                                messages.success(request, "Restaurant updated successfully!")
                            except Exception as e:
                                messages.error(request, f"Error updating restaurant: {str(e)}")
                        else:
                            messages.error(request, 'Unavailable Location')
                    else:
                        messages.error(request, 'Invalid Email ID')
                else:
                    messages.error(request, 'Invalid Phone Number')
            else:
                messages.error(request, 'Passwords do not match')

        # Render the form with existing user data
        context = {
            'restaurant_name': restaurant_name,
            'owner_name': owner_name,
            'phone': phone,
            'email': email,
            'opening_time': opening_time,
            'closing_time': closing_time,
            'district': district,
            'place': place,
            'image': image,
        }
        return render(request, 'restaurantfolder/updatereg.html', context)

    else:
        messages.error(request, 'Login first')
        return redirect('login')
    


def forgotpass(request):
    if request.method=='POST':
        email=request.POST['email']

        try:
            user=RestaurantRegistration.objects.get(Email=email)
        except RestaurantRegistration.DoesNotExist:
            messages.error(request,'user not exists')
            return render(request,'restaurantfolder/forgotpass.html')
        
        password=user.Password
        content=f"Your Password :{password}"
        mail=smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        sender='suryakrishnavaliyapurakkal@gmail.com'
        recipient=email
        mail.login('suryakrishnavaliyapurakkal@gmail.com','vryl fwbx wiud wtco')
        header = f'To: {email}\nFrom: {sender}\nSubject: PASSWORD\n'
        full_message = header + '\n' + content
        mail.sendmail(sender, recipient, full_message)
        mail.close()
    return render(request,'restaurantfolder/forgotpass.html')
            
def edit_menu(request, id):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()

        if not user:
            messages.error(request, 'Login first')
            return redirect('login')  # Redirect to login if user not found

        menu = Menu_Lists.objects.filter(id=id).first()
        if not menu:
            messages.error(request, 'Menu item not found.')
            return redirect('menu_list')  # Redirect if menu not found

        if request.method == 'POST':
            item = request.POST.get('item')
            category = request.POST.get('category')
            description = request.POST.get('description')
            price = request.POST.get('price')
            offercoupon = request.POST.get('offercoupon')
            deliveryoffer = request.POST.get('delivery')
            image = request.FILES.get('image')

            # Check if all required fields except image are present
            if not all([item, category, description, price, offercoupon, deliveryoffer]):
                messages.error(request, 'Please fill in all fields.')
                return render(request, 'restaurantfolder/editmenu.html', {'menu': menu})

            # Update the menu item fields
            menu.Item = item
            menu.Category = category
            menu.Description = description
            menu.Price = price
            menu.OfferCoupon = offercoupon
            menu.DeliveryOffer = deliveryoffer

            # Update the image if a new one is uploaded
            if image:
                menu.Image = image

            # Save the updated menu item
            menu.save()

            # Check if the category exists, if not, create it
            existing_category = Categories.objects.filter(Categorie_name=category).exists()
            if not existing_category:
                Categories.objects.create(Categorie_name=category)

            messages.success(request, 'Menu item updated successfully!')
            return redirect('list_menu_items')  # Redirect after successful edit

        # For GET requests, render the form with existing data
        return render(request, 'restaurantfolder/editmenu.html', {'menu': menu})
    else:
        return redirect('login')  # Redirect to login if not authenticated

           

def create_promo_code(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()

        if not user:
            messages.error(request, 'Login first')
            return redirect('login')  # Redirect to login if user not found
    if request.method == 'POST':
        code = request.POST.get('code')
        value = request.POST.get('value')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Create the promo code
        promo_code = Promo(
            Code=code,
            Value=value,
            Start_Date=start_date,
            End_Date=end_date,
            Restaurant=user  # Assuming the restaurant is associated with the user
        )
        
        # Save the promo code to the database
        promo_code.save()
        
        messages.success(request, 'Promo Code created successfully!')
        return redirect('addpromo')  # Redirect to a page showing all promo codes
    else:
        return render(request, 'restaurantfolder/createpromo.html')


def activepromo(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()

        if not user:
            messages.error(request, 'Login first')
            return redirect('login')  # Redirect to login if user not found
        
    today = date.today()
    activepromos=Promo.objects.filter(Restaurant=user,Start_Date__lte=today,End_Date__gte=today)

    return render(request,'restaurantfolder/activepromo.html',{'activepromos':activepromos})


def edit_promo_code(request,id):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()

        if not user:
            messages.error(request, 'Login first')
            return redirect('login')  # Redirect to login if user not found
        
        promocode=Promo.objects.get(id=id)
    if request.method == 'POST':
        code = request.POST.get('code')
        value = request.POST.get('value')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Create the promo code
        
        promocode.Code=code
        promocode.Value=value
        promocode.Start_Date=start_date
        promocode.End_Date=end_date
            
        
        
        # Save the promo code to the database
        promocode.save()
        
        messages.success(request, 'Promo Code edited successfully!')
        return redirect('index')  # Redirect to a page showing all promo codes
    else:
        return render(request, 'restaurantfolder/editpromo.html',{'promocode':promocode})
    


def deletepromo(request,id):
    promocode=Promo.objects.get(id=id)
    promocode.delete()
    return redirect('activepromo')



def accountinfo(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()

        if not user:
            messages.error(request, 'Login first')
            return redirect('login')  
        
        # Initialize context with empty values
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
        orders_query = Orders.objects.filter(Restaurant_id=user, status="Order Delivered")

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

        return render(request, 'restaurantfolder/account.html', {'revenue': context})

    else:
        messages.error(request, 'Please log in first.')
        return redirect('login')


def paid_through_online(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = RestaurantRegistration.objects.filter(Email=current_user).first()

        if not user:
            messages.error(request, 'Login first')
            return redirect('login')  
        orders=Orders.objects.filter(Restaurant_id=user,Payment_method="Paid via Razorpay").order_by('-DateTime')
        paginator = Paginator(orders, 10)  # Show 10 orders per page
        page_number = request.GET.get('page')  # Get the current page number from query parameters
        page_obj = paginator.get_page(page_number)
        return render(request,'restaurantfolder/paid_online.html',{'totalorder':page_obj})
    else:
        messages.error(request, 'Please log in first.')
        return redirect('login')