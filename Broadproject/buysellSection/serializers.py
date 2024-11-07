from rest_framework import serializers
from usersection.models import Userinfo,Userpersonal_data
from .models import Prodcategory,Addedproduct,ProductReview,ProductChat








class ProdcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Prodcategory
        fields = '__all__'




class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addedproduct
        fields = ['id', 'category','name', 'gstin', 'amount', 'description', 'country', 'state', 'district', 'place', 'image' ]

    image = serializers.ImageField(required=True, allow_null=False)
    



class ProductSearchSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  

    class Meta:
        model = Addedproduct
        fields = ['id', 'image', 'amount', 'name', 'place']

    def get_image(self, obj):
        return obj.image.url  
    




class SellerSearchSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='User_id.Username')  # Fetch seller's username
    profile_pic = serializers.SerializerMethodField()  

    class Meta:
        model = Userpersonal_data
        fields = ['id', 'profile_pic', 'name']  

    def get_profile_pic(self, obj):
        # Return the relative URL for the profile picture
        return obj.Profile_pic.url  





class SellersListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='User_id.Username')
    image = serializers.ImageField(source='Profile_pic')

    class Meta:
        model = Userpersonal_data
        fields = ['id', 'name', 'image']  





class SellerbyIDSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='User_id.Username')
    products = serializers.SerializerMethodField()

    class Meta:
        model = Userpersonal_data
        fields = ['id','name', 'Profile_pic', 'products']

    def get_products(self, obj):
        # Filter products added by the seller and return only their names
        products = Addedproduct.objects.filter(user=obj.User_id)
        product_names = products.values_list('name', flat=True)
        return list(product_names)

    


class ProductsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addedproduct
        fields = ['id', 'image', 'amount', 'name', 'place']




class ProductbyIDSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='user.Username')  # Assuming 'user' is a ForeignKey to Userinfo
    image = serializers.SerializerMethodField() 
    class Meta:
        model = Addedproduct
        fields = ['id', 'image', 'amount', 'name', 'description', 'seller_name']

    def get_image(self, obj):
        # Return the relative URL for the image
        return obj.image.url 
    



class ProductReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.Username', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'reviewer_name', 'rating', 'comment', 'created_at']



class ProductChatSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.Username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.Username', read_only=True)

    class Meta:
        model = ProductChat
        fields = ['id', 'product', 'sender_name', 'receiver_name', 'message', 'timestamp']
    