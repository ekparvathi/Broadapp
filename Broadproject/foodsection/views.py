from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from .models import Categories,Cart,RestaurantReview,Orders
from .serializers import MenuSerializer,RestaurantSerializer,categorySerializer,AddcartSerializer,RestaurantreviewSerializer,OrderSerializer,GetrestuarntSerializer,recommededSerializer
from rest_framework import status
from usersection.models import Userinfo,Userpersonal_data
from rest_framework.response import Response
from django.db.models import Avg
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from restaurant.models import Menu_Lists,RestaurantRegistration,Promo,Promousage
from django.shortcuts import get_object_or_404,get_list_or_404
from adminsection.models import DeliveryFee
from datetime import date
import razorpay
from django.utils import timezone
from twilio.rest import Client
import random


# Create your views here.

@api_view(['GET'])
def Menu_list(request):
    if request.method=='GET':
        # data=Menu_items.objects.all()
        data=Menu_Lists.objects.all()
        serializer=MenuSerializer(data,many=True,context={'request':request})
        return Response(serializer.data)

@api_view(['GET'])
def category_list(request):
    if request.method=='GET':
        data=Categories.objects.all()
        serializer=categorySerializer(data,many=True,context={'request':request})
        return Response(serializer.data)

# @api_view(['GET'])
# def Getrestaurant(request):
#     if request.method=='GET':
#         # data=Restaurants.objects.all()
#         data = Restaurants.objects.annotate(average_rating=Avg('restaurant_review__Rating'))

#         serializer=GetrestuarntSerializer(data,many=True,context={'request':request})
#         return Response(serializer.data)


@api_view(['GET'])
def Getrestaurant(request):
    if 'Email' not in request.session:
        return Response({'msg': 'User not authenticated'}, status=401)
    
    # Get the current user's email and location
    current_user = request.session['Email']
    user = get_object_or_404(Userinfo, Email=current_user)
    try:
        user_address = Userpersonal_data.objects.get(User_id=user.id)
        user_location = f"{user_address.District}, {user_address.Place}"
        print(user_location)
    except Userpersonal_data.DoesNotExist:
        return Response({'msg':'Add your address first.'})
    # Initialize geolocator for converting addresses to coordinates
    geolocator = Nominatim(user_agent="GetLoc", timeout=20)

    # Get the user's coordinates
    try:
        user_coords = geolocator.geocode(user_location)
        if not user_coords:
            return Response({'msg': 'User address not found.'}, status=400)
        coords_1 = (user_coords.latitude, user_coords.longitude)
    except Exception as e:
        return Response({'msg': 'Error fetching user location: ' + str(e)}, status=500)
    
    

    # Get all restaurants and calculate distance for each one
    restaurant_data = []
    restaurants = RestaurantRegistration.objects.annotate(average_rating=Avg('restaurantreview__Rating'))

    for restaurant in restaurants:
        try:
            # Geocode restaurant location
            restaurant_coords = geolocator.geocode(restaurant.Location)
            if restaurant_coords:
                coords_2 = (restaurant_coords.latitude, restaurant_coords.longitude)
                distance = geodesic(coords_1, coords_2).kilometers
                distance = round(distance)
            else:
                distance = None  # If geocoding fails for a restaurant
        except Exception as e:
            distance = None  # Handle geocoding failure gracefully
        try:
            deliveryfee = DeliveryFee.objects.filter(Range__gte=distance).order_by('Range').first()
            deliverycharge = deliveryfee.Deliveryfee if deliveryfee else "No delivery fee available for this distance"
        except DeliveryFee.DoesNotExist:
            deliverycharge = "No delivery fee set for this distance"
        # Append restaurant data along with the distance
        today=date.today()
        promocodes = Promo.objects.filter(Restaurant=restaurant.id,End_Date__gte=today)
        promocode_list = [{'code': promo.Code, 'value': promo.Value} for promo in promocodes] # Assuming promo has a 'code' attribute
# Adjust this based on your models
        restaurant_data.append({
            'restaurant': restaurant,
            'average_rating': restaurant.average_rating,
            'distance': distance,
            'deliveryfee':deliverycharge,
            'promocode':promocode_list
        })

    # Serialize and return the response
    serializer = GetrestuarntSerializer([data['restaurant'] for data in restaurant_data], many=True, context={'request': request})

    # Add distance info to the serialized data
    for i, item in enumerate(serializer.data):
        item['distance'] = restaurant_data[i]['distance']
        item['deliveryfee'] = restaurant_data[i]['deliveryfee']
        item['promocode'] = restaurant_data[i]['promocode']  # Add promo codes here


    
    return Response(serializer.data)

@api_view(['GET'])
def Searchedrestaurant(request,id):
    if request.method=='GET':
        data=RestaurantRegistration.objects.get(id=id)
        serializer=RestaurantSerializer(data,context={'request':request})
        return Response(serializer.data)
    
@api_view(['GET'])
def restaurantmenu(request,id):
    if request.method=='GET':
        data=Menu_Lists.objects.filter(Restaurant=id)
        serializer=MenuSerializer(data,many=True,context={'request':request})
        return Response(serializer.data)






@api_view(['POST']) 
def Addcart(request, id):
    if 'Email' not in request.session:
        return Response({'msg': 'User not authenticated'})
    
    current_user = request.session['Email']
    user = get_object_or_404(Userinfo, Email=current_user)
    
    try:
        user_address = Userpersonal_data.objects.get(User_id=user.id)
        user_location = f"{user_address.District}, {user_address.Place}"
    except Userpersonal_data.DoesNotExist:
        return Response({'msg': 'Add your address first.'})

    # Initialize geolocator for converting addresses to coordinates
    geolocator = Nominatim(user_agent="GetLoc", timeout=20)

    # Get the user's coordinates
    try:
        user_coords = geolocator.geocode(user_location)
        if not user_coords:
            return Response({'msg': 'User address not found.'}, status=400)
        coords_1 = (user_coords.latitude, user_coords.longitude)
    except Exception as e:
        return Response({'msg': f'Error fetching user location: {e}'}, status=500)
    
    try:
        instance = Menu_Lists.objects.get(id=id)
    except Menu_Lists.DoesNotExist:
        return Response({'msg': 'Something went wrong'})
    
    # Check if the user already has items from this restaurant in the cart
    existing_cart_items = Cart.objects.filter(Customer_id=user, Menuitem_id__Restaurant=instance.Restaurant)
    
    if existing_cart_items.exists():
        # If items from the same restaurant already exist in the cart, no extra delivery fee
        deliverycharge = 0
    else:
        # Calculate delivery fee for the first item from this restaurant
        try:
            restaurant_coords = geolocator.geocode(instance.Restaurant.Location)
            if restaurant_coords:
                coords_2 = (restaurant_coords.latitude, restaurant_coords.longitude)
                distance = geodesic(coords_1, coords_2).kilometers
                distance = round(distance)
            else:
                distance = None
        except Exception as e:
            distance = None
        
        try:
            deliveryfee = DeliveryFee.objects.filter(Range__gte=distance).order_by('Range').first()
            deliverycharge = float(deliveryfee.Deliveryfee) if deliveryfee else 0
        except DeliveryFee.DoesNotExist:
            deliverycharge = 0  # No delivery fee available for this distance
    if deliverycharge >0:
        deliverydiscount=instance.DeliveryOffer
        deliverycharge=deliverycharge-deliverydiscount
    
    if request.method == 'POST':
        restaurantid=instance.Restaurant
        itemname = instance.Item
        quantity_str = request.data.get('Quantity', 1)
        quantity = int(quantity_str)
        availableoffer=instance.OfferCoupon
        if availableoffer>0:
            discount = instance.Price * (availableoffer / 100)

            price = instance.Price - discount
        else:
            price=instance.Price
        
        # Calculate total price

        total_price = (price * quantity) + deliverycharge if not existing_cart_items.exists() else (price * quantity)
        
        # Create or add to cart
        cart = Cart.objects.create(
            Restaurant_id=restaurantid,
            Customer_id=user,
            Menuitem_id=instance,
            Item_name=itemname,
            Quantity=quantity,
            Price=instance.Price,
            DeliveryCharge=deliverycharge,
            TotalPrice=total_price,
            Offer_Price=instance.OfferCoupon
        )
      
       
        cart.save()
    
        
        return Response({'msg': 'Cart Added Successfully'})
    else:
        return Response({'msg': 'Something went wrong'})


@api_view(['POST'])
def Promocodecalcu(request):
    if 'Email' not in request.session:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    current_user = request.session['Email']
    user = get_object_or_404(Userinfo, Email=current_user)

    # Fetch all cart items for the current user
    if request.method == 'POST':
        cart_items = Cart.objects.filter(Customer_id=user.id)
        
        # Check if there are any items in the cart
        if not cart_items.exists():
            return Response({'error': 'No items in cart'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the restaurant IDs from the cart items
        restaurant_ids = cart_items.values_list('Menuitem_id__Restaurant', flat=True).distinct()
        
        # Check for the promo code
        promocode = request.data.get('Code')
        today = date.today()

        # Fetch the active promo for any of the restaurants in the cart
        activepromo = Promo.objects.filter(
            Restaurant__id__in=restaurant_ids,
            Code=promocode,
            End_Date__gte=today
        ).first()  # Get the first matching promo, if any
        
        # Check if a valid promo was found
        if activepromo:
        # Create a record in Promousage to track the usage of the promo code
            try:
                Promousage.objects.create(Customer=user, Promocode=activepromo)
                request.session['promocode_value'] = activepromo.Value  
                request.session['promocode_code'] = activepromo.Code

                return Response({'msg': 'Promo code applied', 'promocode_value': activepromo.Value})
            except Exception as e:
                return Response({'error': 'Could not record promo code usage: {}'.format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Invalid or expired promo code'}, status=status.HTTP_400_BAD_REQUEST)

        

# @api_view(['GET'])
# def viewcart(request):
#     if 'Email' in request.session:
#         current_user = request.session['Email']
#         user = get_object_or_404(Userinfo, Email=current_user)
#     else:
#         return Response({'msg': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

#     if request.method == 'GET':
#         cart_items = Cart.objects.filter(Customer_id=user)
#         serializer = AddcartSerializer(cart_items, many=True, context={'request': request})

#         # Calculate total price of cart items
#         total_price = sum(item['TotalPrice'] for item in serializer.data)

#         # Optionally, retrieve the promo code from request or session
#         promocode_value = request.session.get('promocode_value', 0)  # Default to no discount

#         # Subtract the promo value from total price
#         total_price -= promocode_value
#         total_price = max(total_price, 0)  # Ensure total price does not go below zero

#         return Response({'Items': serializer.data, 'Total Price': total_price})

def calculate_total_price(cart_items, promocode_value):
    """Calculate the total price of cart items after applying promo code."""
    total_price = sum(item['TotalPrice'] for item in cart_items)
    total_price -= promocode_value
    return max(total_price, 0)  # Ensure total price does not go below zero

@api_view(['GET'])
def viewcart(request):
    if 'Email' in request.session:
        current_user = request.session['Email']
        user = get_object_or_404(Userinfo, Email=current_user)
    else:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        cart_items = Cart.objects.filter(Customer_id=user)
        serializer = AddcartSerializer(cart_items, many=True, context={'request': request})

        # Retrieve the promo code from request or session
        promocode_value = request.session.get('promocode_value', 0)  # Default to no discount

        # Calculate total price using the helper function
        total_price = calculate_total_price(serializer.data, promocode_value)

        return Response({'Items': serializer.data, 'Total Price': total_price})

    
@api_view(['PUT'])
def updatecart(request,id):
    try:
        instance=Cart.objects.get(id=id)
    except Cart.DoesNotExist:
        return Response({'msg':'data not present'})
    if request.method=='PUT':
        quantity_str= request.data.get('Quantity', 1)
        quantity=int(quantity_str)
        menuid=instance.Menuitem_id.id
        deliveryfee=instance.DeliveryCharge
        menuprice=Menu_Lists.objects.get(id=menuid)
        price=menuprice.Price
        if quantity>=1:
            finalprice=price*quantity + deliveryfee
            instance.Quantity=quantity
            instance.Price=price
            instance.TotalPrice=finalprice
            instance.save()
            return Response({'msg':'Cart updated Successfully'})
        elif quantity==1:
            instance.Quantity=quantity
            instance.Price=price
            instance.save()
            return Response({'msg':'Cart Updated Successfully'})
        elif quantity==0:
            instance.delete()
            return Response({'msg':'Cart removed Successfully'})
        else:
            return Response({'msg':'Something Went Wrong'})
        
@api_view(['DELETE'])
def deletecart(request,id):
    try:
        instance=Cart.objects.get(id=id)
    except Cart.DoesNotExist:
        return Response({'msg':'ERROR'})
    if request.method=='DELETE':
        instance.delete()
        return Response({'data':'DELETED'})

@api_view(['POST'])
def RestaurantReviews(request,id):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=get_object_or_404(Userinfo,Email=current_user)
    else:
        return Response({'msg':'User not authenticated'})
    try:
        instance=RestaurantRegistration.objects.get(id=id)
    except RestaurantRegistration.DoesNotExist:
        return Response({'msg':'Restaurant Does Not Exist'})
    if request.method=='POST':
        data = request.data.copy()
        data['Restaurant_id'] = instance.id
        data['Customer_id'] = user.id
        data['Customer_Name'] = user.Username
        print(data)
        serializer=RestaurantreviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'Review Added'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg':'Something went wrong '})
        

@api_view(['GET'])
def getreview(request,id):
    if request.method=='GET':
        data=RestaurantReview.objects.filter(Restaurant_id=id)
        serializer=RestaurantreviewSerializer(data,many=True,context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

        




TWILIO_ACCOUNT_SID = 'AC0bedc5d4fbeb2ebfe638791093342417'
TWILIO_AUTH_TOKEN = '35a4d1f7b555b712123f6448949772c2'
TWILIO_PHONE_NUMBER = '+15125234074'

def send_sms(to, message):
    # Initialize Twilio client
    client = Client(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)

    # Send SMS
    message = client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=to
    )
    return message.sid

# @api_view(['POST'])
# def addorders(request):
#     if 'Email' not in request.session:
#         return Response({'msg': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

#     current_user = request.session['Email']
#     user = get_object_or_404(Userinfo, Email=current_user)

#     if request.method == 'POST':
#         cart_items = Cart.objects.filter(Customer_id=user.id)

#         if not cart_items.exists():
#             return Response({'error': 'No items in cart'}, status=status.HTTP_400_BAD_REQUEST)

#         promocode_value = request.session.get('promocode_value', 0)  
#         promocode_code = request.session.get('promocode_code', 0)

#         total_price = calculate_total_price(cart_items.values('TotalPrice'), promocode_value)

#         payment_method = request.data.get('payment_method', '')  

#         if payment_method == 'cash_on_delivery':
#             for cart_item in cart_items:
#                 restaurant = cart_item.Menuitem_id.Restaurant
                
#                 try:
#                     customer_address = Userpersonal_data.objects.get(User_id=user)
#                 except Userpersonal_data.DoesNotExist:
#                     return Response({'error': 'Customer address not found'}, status=status.HTTP_400_BAD_REQUEST)

#                 Orders.objects.create(
#                     Restaurant_id=restaurant,
#                     Customer_id=user,
#                     Customer_Name=user.Username,
#                     Customer_Phonenumber=user.Phonenumber,
#                     Customer_Location=f"{customer_address.District}, {customer_address.Place}",
#                     Item_name=cart_item.Menuitem_id.Item,
#                     Quantity=cart_item.Quantity,
#                     Price=cart_item.Price,
#                     Deliverycharge=cart_item.DeliveryCharge,
#                     Offer_price=cart_item.Menuitem_id.OfferCoupon,
#                     TotalPrice=cart_item.TotalPrice,
#                     PromoCode=promocode_code,
#                     PromoUsed=promocode_value > 0,
#                     Payment_method="Cash_On_Delivery"
#                 )
#                 print(cart_item.Menuitem_id.OfferCoupon)
               
#                 sms_message = (
#                     f"Order Confirmation: Your order for {cart_item.Menuitem_id.Item} "
#                     f"has been placed successfully with Cash on Delivery. "
#                     f"Total Amount: ₹{Orders.TotalPrice}."
#                     )
#                 send_sms(user.Phonenumber, sms_message)
#                 cart_items.delete()


#             return Response({'msg': 'Order placed successfully with Cash on Delivery.'}, status=status.HTTP_200_OK)

#         else:
           
#             razorpay_client = razorpay.Client(auth=("rzp_test_RygLyDPora5U2G", "EYw9ReCWe4hioEnnq7OaF8ZM"))

#             razorpay_order = razorpay_client.order.create({
#                 'amount': total_price * 100, 
#                 'currency': 'INR',
#                 'payment_capture': '0'  
#             })

#             request.session['razorpay_order_id'] = razorpay_order['id']

#             return Response({
#                 'razorpay_order_id': razorpay_order['id'],
#                 'total_price': total_price,
#                 'msg': 'Order created, please proceed with payment.'
#             }, status=status.HTTP_200_OK)

@api_view(['POST'])
def addorders(request):
    if 'Email' not in request.session:
        return Response({'msg': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    current_user = request.session['Email']
    user = get_object_or_404(Userinfo, Email=current_user)

    if request.method == 'POST':
        cart_items = Cart.objects.filter(Customer_id=user.id)

        if not cart_items.exists():
            return Response({'error': 'No items in cart'}, status=status.HTTP_400_BAD_REQUEST)

        promocode_value = request.session.get('promocode_value', 0)  
        promocode_code = request.session.get('promocode_code', 0)

        total_price = calculate_total_price(cart_items.values('TotalPrice'), promocode_value)

        payment_method = request.data.get('payment_method', '')  

        if payment_method == 'cash_on_delivery':
            order_details = []  # To collect details of each item for a single SMS

            for cart_item in cart_items:
                restaurant = cart_item.Menuitem_id.Restaurant
                
                try:
                    customer_address = Userpersonal_data.objects.get(User_id=user)
                except Userpersonal_data.DoesNotExist:
                    return Response({'error': 'Customer address not found'}, status=status.HTTP_400_BAD_REQUEST)

                Orders.objects.create(
                    Restaurant_id=restaurant,
                    Customer_id=user,
                    Customer_Name=user.Username,
                    Customer_Phonenumber=user.Phonenumber,
                    Customer_Location=f"{customer_address.District}, {customer_address.Place}",
                    Item_name=cart_item.Menuitem_id.Item,
                    Quantity=cart_item.Quantity,
                    Price=cart_item.Price,
                    Deliverycharge=cart_item.DeliveryCharge,
                    Offer_price=cart_item.Menuitem_id.OfferCoupon,
                    TotalPrice=cart_item.TotalPrice,
                    PromoCode=promocode_code,
                    PromoUsed=promocode_value > 0,
                    Payment_method="Cash_On_Delivery"
                )

                order_details.append(
                    f"{cart_item.Menuitem_id.Item} (x{cart_item.Quantity}) - ₹{cart_item.TotalPrice}"
                )

            # Create a single SMS message with all items
            sms_message = (
                "Order Confirmation: Your order has been placed successfully with Cash on Delivery.\n"
                f"Items:\n{', '.join(order_details)}\n"
                f"Total Amount: ₹{total_price}."
            )
            send_sms(user.Phonenumber, sms_message)

            cart_items.delete()  # Clear the cart after placing the order

            return Response({'msg': 'Order placed successfully with Cash on Delivery.'}, status=status.HTTP_200_OK)

        else:
            # Razorpay order creation logic remains the same
            razorpay_client = razorpay.Client(auth=("rzp_test_RygLyDPora5U2G", "EYw9ReCWe4hioEnnq7OaF8ZM"))

            razorpay_order = razorpay_client.order.create({
                'amount': total_price * 100, 
                'currency': 'INR',
                'payment_capture': '0'  
            })

            request.session['razorpay_order_id'] = razorpay_order['id']

            return Response({
                'razorpay_order_id': razorpay_order['id'],
                'total_price': total_price,
                'msg': 'Order created, please proceed with payment.'
            }, status=status.HTTP_200_OK)





import hmac
import hashlib
# @api_view(['POST'])
# def verify_payment(request):
#     print("Incoming request data:", request.data)
    
#     # {
#     # "payment_id": "pay_1Hh8rZ2eDq3y8w",
#     # "order_id": "order_1Hh8rZ2eDq3y8x"
#     # }
    
#     payment_id = request.data.get('payment_id')
#     order_id = request.data.get('order_id')
#     secret = "EYw9ReCWe4hioEnnq7OaF8ZM" 
#     signature = hmac.new(secret.encode('utf-8'), 
#                 f"{order_id}|{payment_id}".encode('utf-8'), 
#                 hashlib.sha256).hexdigest()

#     razorpay_client = razorpay.Client(auth=("rzp_test_RygLyDPora5U2G", "EYw9ReCWe4hioEnnq7OaF8ZM"))

#     print(f"Verifying payment: order_id={order_id}, payment_id={payment_id}, signature={signature}")

#     try:
#         razorpay_client.utility.verify_payment_signature({
#             'razorpay_order_id': order_id,
#             'razorpay_payment_id': payment_id,
#             'razorpay_signature': signature
#         })

#         razorpay_order_id = request.session.get('razorpay_order_id')
#         promocode_value = request.session.get('promocode_value', 0)
#         user = get_object_or_404(Userinfo, Email=request.session['Email'])

#         cart_items = Cart.objects.filter(Customer_id=user.id)
#         for cart_item in cart_items:
#             restaurant = cart_item.Menuitem_id.Restaurant
            
#             try:
#                 customer_address = Userpersonal_data.objects.get(User_id=user)
#             except Userpersonal_data.DoesNotExist:
#                 return Response({'error': 'Customer address not found'}, status=status.HTTP_400_BAD_REQUEST)

#             Orders.objects.create(
#                 Restaurant_id=restaurant,
#                 Customer_id=user,
#                 Customer_Name=user.Username,
#                 Customer_Phonenumber=user.Phonenumber,
#                 Customer_Location=f"{customer_address.District}, {customer_address.Place}",
#                 Item_name=cart_item.Menuitem_id.Item,
#                 Quantity=cart_item.Quantity,
#                 Price=cart_item.Price,
#                 Deliverycharge=cart_item.DeliveryCharge,
#                 TotalPrice=cart_item.TotalPrice,
#                 PromoCode=request.session.get('promocode_code', 0),
#                 PromoUsed=promocode_value > 0,
#                 Payment_method="Paid via Razorpay"
#             )
#             sms_message = (
#                 f"Payment Confirmation: Your payment for order of {cart_item.Menuitem_id.Item} "
#                 f"has been successfully processed. Total Amount: ₹{cart_item.TotalPrice}."
#             )
#             send_sms(user.Phonenumber, sms_message)
        
#         cart_items.delete()

#         return Response({'msg': 'Payment verified successfully! Order placed.'}, status=status.HTTP_200_OK)

#     except razorpay.errors.SignatureVerificationError:
#         return Response({'msg': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
    

import hmac
import hashlib
@api_view(['POST'])
def verify_payment(request):
    print("Incoming request data:", request.data)
    # {
    # "payment_id": "pay_1Hh8rZ2eDq3y8w",
    # "order_id": "order_1Hh8rZ2eDq3y8x"
    # }
    payment_id = request.data.get('payment_id')
    order_id = request.data.get('order_id')
    secret = "EYw9ReCWe4hioEnnq7OaF8ZM"
    signature = hmac.new(secret.encode('utf-8'), 
                         f"{order_id}|{payment_id}".encode('utf-8'), 
                         hashlib.sha256).hexdigest()

    razorpay_client = razorpay.Client(auth=("rzp_test_RygLyDPora5U2G", "EYw9ReCWe4hioEnnq7OaF8ZM"))

    print(f"Verifying payment: order_id={order_id}, payment_id={payment_id}, signature={signature}")

    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        razorpay_order_id = request.session.get('razorpay_order_id')
        promocode_value = request.session.get('promocode_value', 0)
        promocode_code = request.session.get('promocode_code', 0)
        user = get_object_or_404(Userinfo, Email=request.session['Email'])

        cart_items = Cart.objects.filter(Customer_id=user.id)
        order_details = []  # List to collect item details for single SMS
        total_amount = 0  # Initialize total amount

        for cart_item in cart_items:
            restaurant = cart_item.Menuitem_id.Restaurant
            
            try:
                customer_address = Userpersonal_data.objects.get(User_id=user)
            except Userpersonal_data.DoesNotExist:
                return Response({'error': 'Customer address not found'}, status=status.HTTP_400_BAD_REQUEST)

            Orders.objects.create(
                Restaurant_id=restaurant,
                Customer_id=user,
                Customer_Name=user.Username,
                Customer_Phonenumber=user.Phonenumber,
                Customer_Location=f"{customer_address.District}, {customer_address.Place}",
                Item_name=cart_item.Menuitem_id.Item,
                Quantity=cart_item.Quantity,
                Price=cart_item.Price,
                Deliverycharge=cart_item.DeliveryCharge,
                TotalPrice=cart_item.TotalPrice,
                PromoCode=promocode_code,
                PromoUsed=promocode_value > 0,
                Payment_method="Paid via Razorpay"
            )

            # Append item details and add to total amount
            order_details.append(f"{cart_item.Menuitem_id.Item} (x{cart_item.Quantity}) - ₹{cart_item.TotalPrice}")
            total_amount += cart_item.TotalPrice

        # Construct a single SMS message with all items and total amount
        sms_message = (
            "Payment Confirmation: Your payment has been successfully processed.\n"
            f"Items:\n{', '.join(order_details)}\n"
            f"Total Amount: ₹{total_amount}."
        )
        send_sms(user.Phonenumber, sms_message)

        cart_items.delete()  # Clear the cart after placing the order

        return Response({'msg': 'Payment verified successfully! Order placed.'}, status=status.HTTP_200_OK)

    except razorpay.errors.SignatureVerificationError:
        return Response({'msg': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def getorder(request):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=get_object_or_404(Userinfo,Email=current_user)
    if request.method=='GET':
        data=Orders.objects.filter(Customer_id=user)
        serializer=OrderSerializer(data,many=True,context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def getongoingorders(request):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=get_object_or_404(Userinfo,Email=current_user)
    else:
        return Response({'msg':'User not authenticated'})
    if request.method=='GET':
        data=Orders.objects.filter(Customer_id=user,status='Order Accepted')
        if len(data)==0:
            return Response({'msg':'No item ongoing'})
        serializer=OrderSerializer(data,many=True,context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getmenubycategory(request,id):
    try:
        instance=Categories.objects.get(id=id)
    except Categories.DoesNotExist:
        return Response({'msg':'Category does not exists'})
    if request.method=='GET':
        category=instance.Categorie_name
        category_list=Menu_Lists.objects.filter(Category=category)
        if len(category_list)==0:
            return Response({'msg':'No item avaliable'})
        serializer=MenuSerializer(category_list,many=True,context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)
        

@api_view(['POST'])
def getbyprice(request):
    price_range = request.data.get('Price', None)

    if price_range is None:
        return Response({'msg': 'Please provide a price range'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        price_range = int(price_range)  # Convert to integer
    except ValueError:
        return Response({'msg': 'Invalid price range format. Please provide a number.'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method=='POST':
    
        data = Menu_Lists.objects.filter(Price__lte=price_range)
        serializer = MenuSerializer(data, many=True, context={'request': request})
        if serializer.data:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'No products found for the specified price range'}, status=status.HTTP_404_NOT_FOUND)

    else:
        return Response({'msg':'Choose a Price range'})
        
        

@api_view(['POST'])
def searchresult(request):
    search = request.data.get('Search')
    
    if not search:
        return Response({'error': 'Search parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    list_one = Menu_Lists.objects.filter(Item__icontains=search)
    menu_serializer = MenuSerializer(list_one, many=True, context={'request': request})
    
    list_two = RestaurantRegistration.objects.filter(Restaurant_Name__icontains=search)
    
    # Initialize restaurant serializer
    restaurant_serializer = None
    
    if list_two.exists():
        # Get the first restaurant's ID
        restitem = list_two.first()
        restitem_id = restitem.id
        searchbyrest = Menu_Lists.objects.filter(Restaurant=restitem_id)
        restaurant_serializer = MenuSerializer(searchbyrest, many=True, context={'request': request})

    return Response({
        'menu_items': menu_serializer.data,
        'restaurants': restaurant_serializer.data if restaurant_serializer else []
    }, status=status.HTTP_200_OK)





# @api_view(['PUT'])
# def Updateorder(request,id):
#     try:
#         instance=Orders.objects.get(id=id)
#     except Orders.DoesNotExist:
#         return Response({'msg':'Order unavailable'})
#     if request.method=='PUT':
#         status=request.data.get('Status')
#         if not status:
#             return Response({'msg':'You need to enter status'})
#         else:
#             instance.status=status
#             instance.save()
#             return Response({'msg':'Order updated.'})
        
@api_view(['GET'])
def recommendeditems(request):
    if request.method=='GET':
        data = RestaurantRegistration.objects.annotate(average_rating=Avg('restaurantreview__Rating'))
        filtered_data = data.filter(average_rating__gt=3.0)  # Filtering based on average rating
        serializer = recommededSerializer(filtered_data, many=True, context={'request': request})
        return Response(serializer.data)
    
@api_view(['GET'])
def mostpopularitems(request):
    if request.method=='GET':
        data = RestaurantRegistration.objects.annotate(average_rating=Avg('restaurantreview__Rating'))
        filtered_data = data.filter(average_rating__gt=3.5)  # Filtering based on average rating
        serializer = recommededSerializer(filtered_data, many=True, context={'request': request})
        return Response(serializer.data)
        


@api_view(['GET'])
def nearby(request):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=Userinfo.objects.get(Email=current_user)
    else:
        return Response({'msg':'Please Login!'})
    if request.method == 'GET':
        # Initialize geolocator
        geolocator = Nominatim(user_agent="GetLoc",timeout=20)
        
        # Get all restaurants
        restaurants = RestaurantRegistration.objects.all()
        # Get user address from query parameters
        try:
            user=Userpersonal_data.objects.get( User_id=user.id)
           
        except Userpersonal_data.DoesNotExist:
            return Response({'msg':'Add your Address to profile'})
        
        user_address = f"{user.District}, {user.Place}"
        
        if not user_address:
            return Response({'error': 'Address parameter is required.'}, status=400)
        
        # Geocode the user's address
        print(user_address)

        location_2 = geolocator.geocode(user_address)
        if not location_2:
            return Response({'error': 'Invalid user address.'}, status=400)
        
        coords_2 = (location_2.latitude, location_2.longitude)
        
        # Store nearby restaurants with their distance
        nearby_restaurants = []
        
        # Iterate through the restaurants and calculate distances
        for restaurant in restaurants:
            location_1 = geolocator.geocode(restaurant.Location)
            if location_1:
                coords_1 = (location_1.latitude, location_1.longitude)
                distance = geodesic(coords_1, coords_2).kilometers
                
                
                # Add restaurant and distance to list if distance is within a certain limit
                if distance <= 5:  # You can adjust the distance limit
                    nearby_restaurants.append({
                        'restaurant': restaurant.Restaurant_Name,
                        'address': f"{restaurant.Place},{restaurant.District}",
                        'distance_km': round(distance)
                    })
        
        nearby_restaurants = sorted(nearby_restaurants, key=lambda x: x['distance_km'])

        return Response(nearby_restaurants, status=200)


@api_view(['PUT'])
def cancelorder(request,id):
    if 'Email' in request.session:
        current_user=request.session['Email']
        user=get_object_or_404(Userinfo,Email=current_user)
    else:
        return Response({'msg':'User not authenticated'})
    try:
        instance=Orders.objects.get(id=id)
    except Orders.DoesNotExist:
        return Response({'msg':'Order unavailable'})
    if instance.Customer_id != user:
        return Response({'msg': 'You cannot cancel this order.'})

    # Update the status of the order
    if request.method == 'PUT':
        instance.status = 'Order Cancelled By User!!!'
        instance.save()
        return Response({'msg': 'Order cancelled successfully.'},status=200)
    




@api_view(['GET'])
def bestsellers(request):
    if request.method == 'GET':
        bestsellers_list = []  # List to hold best sellers from all restaurants
        
        # Get all restaurants that have at least one promo code
        restaurants_with_promos = RestaurantRegistration.objects.filter(promo__isnull=False).distinct()

        for restaurant in restaurants_with_promos:
            # Retrieve promos for each restaurant
            bestsellers = Promo.objects.filter(Restaurant=restaurant)
            
            # Prepare a dictionary for each restaurant
            restaurant_data = {
                'restaurant_id': restaurant.id,
                'restaurant_name': restaurant.Restaurant_Name,  # Access the restaurant name
                'bestsellers': list(bestsellers.values('Code', 'Value', 'Start_Date', 'End_Date'))  # Get relevant promo fields
            }
            
            bestsellers_list.append(restaurant_data)  # Add each restaurant's best sellers to the list

    return Response({'Best sellers': bestsellers_list})