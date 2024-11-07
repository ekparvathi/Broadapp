from buysellSection.models import Userinfo,Addedproduct,Prodcategory
#from rest_framework.views import APIView
#from rest_framework.decorators import api_view
#from rest_framework.response import Response
from django.shortcuts import render,redirect,get_object_or_404
#from .models import Admin
from usersection.models import Userinfo, Userpersonal_data
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import Q







def admin_dashboard(request):

    if 'admin_id' not in request.session:
        return redirect('adminlogin')

    #admin_name = request.session.get('admin_name')

    total_users = Userinfo.objects.count()
    total_sellers = Addedproduct.objects.values('user').distinct().count()
    total_products = Addedproduct.objects.count()

    context = {
        #'admin_name': admin_name,
        'total_users': total_users,
        'total_sellers': total_sellers,
        'total_products': total_products,
    }

    return render(request, 'buyselladmin/admin_dashboard.html', context)






def admin_logout(request):
    request.session.flush()  
    return redirect('/adminsection/login') 





def add_category(request):

    if request.method == "POST":

        category_name = request.POST.get('category').capitalize()

        if Prodcategory.objects.filter(name=category_name).exists():
            return render(request, 'buyselladmin/admin_add_category.html', {'error': 'Category already exists.'})

        Prodcategory.objects.create(name=category_name)

        messages.info(request, "Category added successfully!")

        return render(request, 'buyselladmin/admin_add_category.html')

    context = {"status": "Success"}
    return render(request, 'buyselladmin/admin_add_category.html',context)






def manage_categories(request):
    
    query = request.GET.get('q', None)
    if query:
        categories = Prodcategory.objects.filter(name__icontains=query)
    else:
        categories = Prodcategory.objects.all()

    paginator = Paginator(categories, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': page_obj,
        'pages': paginator.page_range,
        'current_page': page_obj.number,
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    }

    return render(request, 'buyselladmin/admin_manage_categories.html', context)







def delete_category(request, category_id):
    
    category = get_object_or_404(Prodcategory, id=category_id)

    category.delete()

    return redirect('manage-categories')










def manage_users(request):
    query = request.GET.get('q', '')
    if query:
        # Filter users based on multiple fields
        users_list = Userpersonal_data.objects.filter(
            Q(User_id__Username__icontains=query) |
            Q(User_id__Email__icontains=query) |
            Q(User_id__Phonenumber__icontains=query) |
            Q(Country__icontains=query) |
            Q(District__icontains=query) |
            Q(Place__icontains=query)
        ).select_related('User_id')
    else:
        users_list = Userpersonal_data.objects.select_related('User_id').all()

    paginator = Paginator(users_list, 10)  
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    

    context = {
        'users': users,
        'previous_page': users.number - 1 if users.has_previous() else None,
        'next_page': users.number + 1 if users.has_next() else None,
        'current_page': users.number,
        'pages': paginator.page_range,
        'query': query,
    }

    return render(request, 'buyselladmin/admin_manage_users.html', context)









def manage_sellers(request):
    query = request.GET.get('q', '')

    # Fetch unique user IDs from Addedproduct
    sellers_ids = Addedproduct.objects.values_list('user_id', flat=True).distinct()
    
    # Retrieve user details for those sellers
    sellers_details =  Userpersonal_data.objects.filter(id__in=sellers_ids)

    # Search functionality across relevant fields
    if query:
        sellers_details = sellers_details.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phonenumber__icontains=query) |
            Q(state__icontains=query) |
            Q(district__icontains=query) |
            Q(place__icontains=query)
        )

    
    paginator = Paginator(sellers_details, 10)  
    page_number = request.GET.get('page')
    sellers = paginator.get_page(page_number)

   
    previous_page = sellers.number - 1 if sellers.has_previous() else None
    next_page = sellers.number + 1 if sellers.has_next() else None
    current_page = sellers.number

    
    context = {
        'sellers': sellers,
        'previous_page': previous_page,
        'next_page': next_page,
        'current_page': current_page,
        'pages': paginator.page_range,
        'query': query,
    }

    return render(request, 'buyselladmin/admin_manage_sellers.html', context)








def manage_products(request):
    from django.db.models import Q

    # Fetch all products
    query = request.GET.get('q', '')
    if query:
        # Filter products based on multiple fields
        products = Addedproduct.objects.filter(
            Q(name__icontains=query) |
            Q(gstin__icontains=query) |
            Q(amount__icontains=query) |
            Q(state__icontains=query) |
            Q(district__icontains=query) |
            Q(place__icontains=query)
        ).select_related('user')  # Include related user data
    else:
        products = Addedproduct.objects.all().select_related('user')  

    
    paginator = Paginator(products, 10)  
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    
    previous_page = products_page.number - 1 if products_page.has_previous() else None
    next_page = products_page.number + 1 if products_page.has_next() else None
    current_page = products_page.number

    
    context = {
        'products': products_page,
        'previous_page': previous_page,
        'next_page': next_page,
        'current_page': current_page,
        'pages': paginator.page_range,
        'query': query,  # Pass the search query to the template
    }

    return render(request, 'buyselladmin/admin_manage_products.html', context)






def delete_user(request, user_id):
    
    user = get_object_or_404(Userinfo, id=user_id)
    user.delete()
    
    return redirect('manage-users')





def delete_seller(request, seller_id):
    # Get the user who is marked as a seller
    seller = get_object_or_404(Userinfo, id=seller_id)
    
    # Delete all the products associated with this seller
    Addedproduct.objects.filter(user=seller).delete()
    
    # Optionally, mark the user as no longer a seller 
    seller.is_seller = False 
    seller.save()
    
    return redirect('manage-sellers')






def delete_product(request, product_id):
    
    product = get_object_or_404(Addedproduct, id=product_id)
    
    product.delete()

    return redirect('manage-products')  




