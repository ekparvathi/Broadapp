from django.urls import path
from foodsection import views


urlpatterns = [
    path('getmenu/',views.Menu_list,name='getmenu'),
    path('categories/',views.category_list,name='categories'),
    path('restaurants/',views.Getrestaurant,name='addrestaurant'),
    path('restaurants/<int:id>',views.Searchedrestaurant,name='restaurant'),
    path('restaurantmenu/<int:id>',views.restaurantmenu,name='restaurantmenu'),
    path('addcart/<int:id>',views.Addcart,name='addcart'),
    path('viewcart/',views.viewcart,name='viewcart'),
    path('cartupdate/<int:id>',views.updatecart,name='updatecart'),
    path('deletecart/<int:id>',views.deletecart,name='deletecart'),
    path('addreviews/<int:id>',views.RestaurantReviews,name='restaurantreview'),
    path('getreviews/<int:id>',views.getreview,name='getreview'),
    path('addorders/',views.addorders,name='addorders'),
    path('orderhistory/',views.getorder,name='getorders'),
    path('ongoingorders/',views.getongoingorders,name='ongoingorders'),
    path('categories/<int:id>',views.getmenubycategory,name='getmenubycategory'),
    path('getbyprice/',views.getbyprice,name='getbyprice'),
    path('getbysearch/',views.searchresult,name='searchresult'),
    # path('ordercheck/',views.getordercheck,name='getordercheck'),
    # path('updateorder/<int:id>',views.Updateorder,name='updateorder'),
    path('recommended/',views.recommendeditems,name='recommeded'),
    path('mostpopular/',views.mostpopularitems,name='mostpopular'),
    path('nearbysearch/',views.nearby,name='nearby'),
    path('cancelorder/<int:id>',views.cancelorder,name='cancelorder'),
    path('bestsellers/',views.bestsellers,name="bestsellers"),
    path('promocode/',views.Promocodecalcu,name="promocalcu"),
    path('verify_payment/',views.verify_payment, name='verify_payment'),  

]