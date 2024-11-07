from django.urls import path
from .import views

urlpatterns = [

    path('admindashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin-add-category/', views.add_category, name='add-category'),
    path('admin-manage-categories/', views.manage_categories, name='manage-categories'),
    path('admin-delete-category/<int:category_id>/', views.delete_category, name='admin-delete-category'),
    path('admin-manage-users/', views.manage_users, name='manage-users'),
    path('admin-manage-sellers/', views.manage_sellers, name='manage-sellers'),
    path('admin-manage-products/', views.manage_products, name='manage-products'),
    path('admin-delete-user/<int:user_id>/', views.delete_user, name='delete-user'),
    path('admin-delete-seller/<int:seller_id>/', views.delete_seller, name='delete-seller'),
    path('admin-delete-product/<int:product_id>/', views.delete_product, name='delete-product'),
    path('admin-logout/', views.admin_logout, name='admin-logout'),

]