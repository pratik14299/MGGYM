from gym.models import Member,SubscriptionPlan,MembershipSubscription,Payment
from rest_framework.serializers import ModelSerializer


class SubscriptionPlanSerializer(ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'



class MembershipSubscriptionSerializer(ModelSerializer):
    class Meta:
        model = MembershipSubscription
        fields = '__all__'


class MemberSerializer(ModelSerializer):
    subscriptions = MembershipSubscriptionSerializer(many = True,read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'phone', 'dob', 'joined_date', 'passport_photo', 'subscriptions']


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'