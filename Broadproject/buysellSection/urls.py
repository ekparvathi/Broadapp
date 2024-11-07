from django.contrib import admin
from django.urls import path
from buysellSection import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('categories/',views.prodcategory,name='category'),
    path('category/<int:category_id>/add-product/', views.add_product, name='add-product'),
    path('sellerslist/', views.allsellers, name='sellers'),
    path('seller-by-id/<int:id>/', views.get_seller_by_id, name='seller-by-id'),
    path('productslist/', views.allproducts, name='products'),
    path('product-by-id/<int:id>/', views.get_product_by_id, name='product-by-id'),
    path('nearby-products/', views.nearby_products, name='nearby-products'),
    path('search-product-seller/', views.search_product_seller, name='search-product-seller'),
    path('product/<int:product_id>/add-review/', views.add_review, name='add-review'),
    path('product/<int:product_id>/reviews/', views.get_product_reviews, name='product-reviews'),
    path('product/<int:product_id>/send-message/', views.send_message_to_seller, name='send_message_to_seller'),
    path('reply/<int:user_id>/', views.seller_reply_to_user, name='seller_reply_to_user'),
    path('seller-get-messages-user/<int:sender_id>/product/<int:product_id>/', views.seller_get_messages_user, name='seller_get_messages'),
    path('user-get-messages-seller/<int:sender_id>/product/<int:product_id>/', views.user_get_messages_seller, name='user_get_messages'),
    #path('product/<int:product_id>/reply/<int:receiver_id>/', views.seller_reply_to_user, name='seller_reply_to_user'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 