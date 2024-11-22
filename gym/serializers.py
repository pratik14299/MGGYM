from gym.models import Member,SubscriptionPlan,MembershipSubscription,Payment
from rest_framework.serializers import ModelSerializer

class MemberSerializer(ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

class SubscriptionPlanSerializer(ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'



class MembershipSubscriptionSerializer(ModelSerializer):
    class Meta:
        model = MembershipSubscription
        fields = '__all__'



class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'