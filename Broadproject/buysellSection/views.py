from .models import Userinfo, Prodcategory, Addedproduct, ProductReview,ProductChat
#from buysellAdmin.models import Admin
from .serializers import ProdcategorySerializer,ProductSerializer,ProductSearchSerializer,SellersListSerializer,SellerbyIDSerializer,SellerSearchSerializer,ProductsListSerializer,ProductbyIDSerializer,ProductReviewSerializer, ProductChatSerializer
#from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from usersection.models import Userinfo,Userpersonal_data
from rest_framework import status
from django.shortcuts import get_object_or_404

#from django.contrib import messages
from django.contrib.sessions.backends.db import SessionStore
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from django.db.models import Q
from collections import defaultdict
from django.utils import timezone
from datetime import timedelta

#from django.core.mail import send_mail





# To get category     
@api_view(['GET'])
def prodcategory(request):
    if request.method=='GET':
        categories=Prodcategory.objects.all()
        serializer=ProdcategorySerializer(categories,many=True)
        data={
            'message':'Your Categories are...',
            'categories': serializer.data
        }
        return Response(serializer.data)
    





@api_view(['POST'])
def add_product(request, category_id):
    
    user_email = request.session.get('Email')  

    if user_email:
        try:
            
            user = Userinfo.objects.get(Email=user_email)
        except Userinfo.DoesNotExist:
            return Response({'msg': 'Invalid user session. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'msg': 'You must be logged in to add a product.'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            # Save the product with the session user as the seller
            serializer.save(user=user, category_id=category_id)
            return Response({'msg': 'Product added successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)








# To Search product or seller.
   
@api_view(['POST'])
def search_product_seller(request):
    search_query = request.data.get('search')

    
    if not search_query:
        return Response({'error': 'Search parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

   
    response_data = {}
    product_found = False
    seller_found = False

    # Search for products by name or category
    products = Addedproduct.objects.filter(
        name__icontains=search_query
    ) | Addedproduct.objects.filter(
        category__name__icontains=search_query
    )

    if products.exists():
        product_serializer = ProductSearchSerializer(products, many=True, context={'request': request})
        response_data['products'] = product_serializer.data
        product_found = True

    # Search for sellers by username
    sellers = Userpersonal_data.objects.filter(
        User_id__addedproduct__isnull=False,
        User_id__Username__icontains=search_query
    ).distinct()

    if sellers.exists():
        seller_serializer = SellerSearchSerializer(sellers, many=True, context={'request': request})
        response_data['sellers'] = seller_serializer.data
        seller_found = True

    
    if not product_found and not seller_found:
        return Response({'message': 'No such product or seller matches your search query.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(response_data, status=status.HTTP_200_OK)










@api_view(['GET'])
def allsellers(request):
    # Fetch distinct users with added products
    users = Userpersonal_data.objects.filter(User_id__addedproduct__isnull=False).distinct()
    
    # Serialize the user data
    serializer = SellersListSerializer(users, many=True)

    return Response(serializer.data)






@api_view(['GET'])
def get_seller_by_id(request, id):
    try:
        # Check if the seller has added any products
        if not Addedproduct.objects.filter(user_id=id).exists():
            return Response({'error': 'This seller has not added any products.'}, status=404)

        # Fetch the Userpersonal_data entry for the given user ID
        seller_data = Userpersonal_data.objects.get(User_id=id)

        # Serialize the seller's details along with product names
        serializer = SellerbyIDSerializer(seller_data)
        return Response(serializer.data)
    
    except Userpersonal_data.DoesNotExist:
        return Response({'error': 'No such seller found.'}, status=404)





@api_view(['GET'])
def allproducts(request):
   
    products = Addedproduct.objects.all()

    serializer = ProductsListSerializer(products, many=True)

    return Response(serializer.data, status=200)





@api_view(['GET'])
def get_product_by_id(request, id):
    try:
        product = Addedproduct.objects.get(id=id)
        serializer = ProductbyIDSerializer(product)
        return Response(serializer.data)

    except Addedproduct.DoesNotExist:
        return Response({'error': 'Product not found.'}, status=404)







@api_view(['GET'])
def nearby_products(request):
    user_id = request.session.get('user_id')
    
    if not user_id:
        return Response({'msg': 'You must be logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
    try:
        user_profile = Userpersonal_data.objects.get(User_id=user_id)
    except Userpersonal_data.DoesNotExist:
        return Response({'msg': 'User profile not found. Please add your address details.'}, status=status.HTTP_400_BAD_REQUEST)

    
    if not user_profile.District or not user_profile.Place:
        return Response({'msg': 'Add your district and place to your profile.'}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize the geolocator
    geolocator = Nominatim(user_agent="GetLoc", timeout=20)

    # Get user address from district and place
    user_address = f"{user_profile.District}, {user_profile.Place}"
    user_location = geolocator.geocode(user_address)
    
    if not user_location:
        return Response({'error': 'Invalid user address.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user_coords = (user_location.latitude, user_location.longitude)
    
    
    nearby_products = []

    # Iterate over products and calculate distances
    for product in Addedproduct.objects.all():
        product_address = f"{product.district}, {product.place}"
        product_location = geolocator.geocode(product_address)
        
        if product_location:
            product_coords = (product_location.latitude, product_location.longitude)
            distance = geodesic(product_coords, user_coords).kilometers
            
            # Include products within a 5 km radius
            if distance <= 5:
                nearby_products.append({
                    'id': product.id,
                    'image': product.image.url if product.image else None,  
                    'amount': product.amount,
                    'name': product.name,
                    'place': product.place
                })
    
    
    nearby_products.sort(key=lambda x: distance)

    return Response(nearby_products, status=status.HTTP_200_OK)





@api_view(['POST'])
def add_review(request, product_id):
    
    email = request.session.get('Email')
    if not email:
        return Response({'msg': 'You must be logged in to add a review.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = Userinfo.objects.get(Email=email)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'Invalid email. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        product = Addedproduct.objects.get(id=product_id)
    except Addedproduct.DoesNotExist:
        return Response({'msg': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Check if a review already exists for this product by the user
        existing_review = ProductReview.objects.filter(product=product, reviewer=user).first()
        if existing_review:
            return Response({'msg': 'You have already reviewed this product.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            
            review = serializer.save(product=product, reviewer=user)

           
            response_serializer = ProductReviewSerializer(review)
            return Response({'msg': 'Review added successfully!', 'review': response_serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_product_reviews(request, product_id):
    try:
        reviews = ProductReview.objects.filter(product_id=product_id)
    except ProductReview.DoesNotExist:
        return Response({'msg': 'No reviews found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)







@api_view(['POST'])
def send_message_to_seller(request, product_id):
    
    email = request.session.get('Email')
    if not email:
        return Response({'msg': 'You must be logged in to send a message.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        sender = Userinfo.objects.get(Email=email)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'Invalid email. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        product = Addedproduct.objects.get(id=product_id)
    except Addedproduct.DoesNotExist:
        return Response({'msg': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure the seller is the user associated with the product
    receiver = product.user
    if sender == receiver:
        return Response({'msg': 'You cannot send a message to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    message_content = request.data.get('message')
    if not message_content:
        return Response({'msg': 'Message content is required.'}, status=status.HTTP_400_BAD_REQUEST)

    
    chat_message = ProductChat.objects.create(
        product=product,
        sender=sender,
        receiver=receiver,
        message=message_content
    )

    serializer = ProductChatSerializer(chat_message)
    return Response({'msg': 'Message sent successfully!', 'message': serializer.data}, status=status.HTTP_201_CREATED)










@api_view(['POST'])
def seller_reply_to_user(request, user_id):
    
    email = request.session.get('Email')
    if not email:
        return Response({'msg': 'You must be logged in as the seller to send a reply.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        seller = Userinfo.objects.get(Email=email)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'Invalid email. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)

    
    message_content = request.data.get('message')
    if not message_content:
        return Response({'msg': 'Message content is required.'}, status=status.HTTP_400_BAD_REQUEST)

    
    try:
        receiver = Userinfo.objects.get(id=user_id)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


    try:
        product = Addedproduct.objects.filter(user=seller).first()  
        if not product:
            return Response({'msg': 'No product found to associate with this message.'}, status=status.HTTP_404_NOT_FOUND)
    except Addedproduct.DoesNotExist:
        return Response({'msg': 'Error retrieving product.'}, status=status.HTTP_404_NOT_FOUND)

    
    reply_message = ProductChat.objects.create(
        product=product,
        sender=seller,
        receiver=receiver,
        message=message_content
    )

    serializer = ProductChatSerializer(reply_message)
    return Response({'msg': 'Reply sent successfully!', 'message': serializer.data}, status=status.HTTP_201_CREATED)










@api_view(['GET'])
def seller_get_messages_user(request, sender_id, product_id):
    
    email = request.session.get('Email')
    if not email:
        return Response({'msg': 'You must be logged in as the seller to view messages.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        seller = Userinfo.objects.get(Email=email)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'Invalid email. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)

    # Filter messages from the last 24 hours
    one_day_ago = timezone.now() - timedelta(days=1)
    messages = ProductChat.objects.filter(
        Q(sender_id=sender_id, receiver=seller, product_id=product_id) |
        Q(sender=seller, receiver_id=sender_id, product_id=product_id),
        timestamp__gte=one_day_ago
    ).order_by('-timestamp')

    if not messages.exists():
        return Response({'msg': 'No messages found between the seller and the specified user for this product in the last day.'}, status=status.HTTP_404_NOT_FOUND)

    # Group messages by date
    grouped_messages = defaultdict(list)
    for message in messages:
        date_key = message.timestamp.date()  
        grouped_messages[date_key].append(message)

    
    serialized_data = {}
    for date, msgs in grouped_messages.items():
        serialized_data[str(date)] = ProductChatSerializer(msgs, many=True).data

    return Response({'msg': 'Messages retrieved successfully.', 'messages': serialized_data}, status=status.HTTP_200_OK)









@api_view(['GET'])
def user_get_messages_seller(request, sender_id, product_id):
   
    email = request.session.get('Email')
    if not email:
        return Response({'msg': 'You must be logged in as a user to view messages.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = Userinfo.objects.get(Email=email)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'Invalid email. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)
   
    try:
        seller = Userinfo.objects.get(id=sender_id)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'Seller not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    one_day_ago = timezone.now() - timedelta(days=1)
   
    messages = ProductChat.objects.filter(
        Q(sender=seller, receiver=user, product_id=product_id) |
        Q(sender=user, receiver=seller, product_id=product_id),
        timestamp__gte=one_day_ago  
    ).order_by('-timestamp')

    if not messages.exists():
        return Response({'msg': 'No messages found between you and the seller for this product within the last day.'}, status=status.HTTP_404_NOT_FOUND)

    
    grouped_messages = defaultdict(list)
    for message in messages:
        date_key = message.timestamp.date()  
        grouped_messages[date_key].append(message)
   
    serialized_data = {}
    for date, msgs in grouped_messages.items():
        serialized_data[str(date)] = ProductChatSerializer(msgs, many=True).data

    return Response({'msg': 'Messages retrieved successfully.', 'messages': serialized_data}, status=status.HTTP_200_OK)







"""@api_view(['POST'])
def seller_reply_to_user(request, product_id, receiver_id):
    # Check if the seller is logged in using session email
    email = request.session.get('Email')
    if not email:
        return Response({'msg': 'You must be logged in as the seller to send a reply.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        seller = Userinfo.objects.get(Email=email)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'Invalid email. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        product = Addedproduct.objects.get(id=product_id, user=seller)
    except Addedproduct.DoesNotExist:
        return Response({'msg': 'Product not found or you are not the seller of this product.'}, status=status.HTTP_404_NOT_FOUND)

    # Get the message content from the request
    message_content = request.data.get('message')
    if not message_content:
        return Response({'msg': 'Message content is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve the user who inquired based on the receiver ID
    try:
        receiver = Userinfo.objects.get(id=receiver_id)
    except Userinfo.DoesNotExist:
        return Response({'msg': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Create and save the chat message
    chat_message = ProductChat.objects.create(
        product=product,
        sender=seller,
        receiver=receiver,
        message=message_content
    )

    serializer = ProductChatSerializer(chat_message)
    return Response({'msg': 'Reply sent successfully!', 'message': serializer.data}, status=status.HTTP_201_CREATED)"""
