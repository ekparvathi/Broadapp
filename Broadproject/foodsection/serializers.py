from rest_framework import serializers
from .models import Categories,Cart,Orders,RestaurantReview
from restaurant.models import RestaurantRegistration,Menu_Lists


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model=Menu_Lists
        fields='__all__'

class categorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Categories
        fields='__all__'

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model=RestaurantRegistration
        fields='__all__'
    def validate_my_date(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Date must be a string in 'YYYY-MM-DD' format.")
        return value
    # def validate_phonenumber(self, value):
    #     if RestaurantRegistration.objects.filter(Phonenumber=value).exists():
    #         raise serializers.ValidationError("This phone number is already in use.")
    #     return value


# class RestaurantloginSerializer(serializers.Serializer):
#     Phonenumber=serializers.CharField()
#     Password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         phonenumber = data.get('Phonenumber')
#         password = data.get('Password')
        
#         if not phonenumber or not password:
#             raise serializers.ValidationError("Phonenumber and Password are required.")
        
#         # Additional validation can be added here if needed
#         return data


class AddcartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields='__all__'

class RestaurantreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=RestaurantReview
        fields='__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Orders
        fields='__all__'



class restoratingSerializer(serializers.ModelSerializer):
    class Meta:
        model=RestaurantReview
        fields=('Rating',)


class GetrestuarntSerializer(serializers.ModelSerializer):
    rating=restoratingSerializer(many=True,read_only=True)
    average_rating = serializers.FloatField(read_only=True)  # Add the average rating field

    class Meta:
        model=RestaurantRegistration
        fields=('id','Restaurant_Name','District','Place','average_rating','rating','Opening_time','Closing_time')


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu_Lists
        fields = ['Item', 'Price']

class recommededSerializer(serializers.ModelSerializer):
    food_items = FoodItemSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = RestaurantRegistration
        fields = ['id', 'Restaurant_Name', 'District','Place', 'food_items', 'average_rating', 'Opening_time', 'Closing_time']