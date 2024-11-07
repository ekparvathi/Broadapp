from django.urls import path
from restaurant import views
urlpatterns = [
    path('register/',views.RegisterRestaurant,name='register'),
    path('login/',views.login,name='login'),
    path('index/',views.index,name='index'),
    path('profile/',views.profile,name='profile'),
    path('addmenu/',views.add_menu,name='addmenu'),
    path('update_availability/<int:id>/',views.update_availability, name='update_availability'),
    path('showmenu/',views.list_menu_items,name='list_menu_items'),
    path('orders/', views.order_list, name='order_list'),
    path('orderdetail/<int:id>/',views.orderdetail,name='orderdetail'),
    path('acceptedorder/',views.accepted_list,name="acceptedorder"),
    path('cancelorder/',views.canceled_order,name="canceledorder"),
    path('deliveredorder/',views.delivered_order,name="deliveredorder"),
    path('review_rating/',views.review_ratings,name="reviewrating"),
    path('logout/', views.logout_view, name='restaurantlogout'),
    path('acceptorder/<int:id>/',views.acceptorder,name="orderaccept"),
    path('cancelorder/<int:id>/',views.cancelorder,name="ordercancelled"),
    path('orderdelivered/<int:id>/',views.orderdelivered,name="orderdelivered"),
    path('updateregister/',views.updaterestaurant,name="update"),
    path('forgotpass/',views.forgotpass,name="forgotpass"),
    path('editmenu/<int:id>',views.edit_menu,name="editmenu"),
    path('addpromo/',views.create_promo_code,name="addpromo"),
    path('activepromo/',views.activepromo,name="activepromo"),
    path('editpromo/<int:id>',views.edit_promo_code,name="editpromo"),
    path('deletepromo/<int:id>',views.deletepromo,name="deletepromo"),
    path('revenue_data/',views.accountinfo,name='revenueinfo'),
    path('paid_through_online/',views.paid_through_online,name="paid_through_online")



]