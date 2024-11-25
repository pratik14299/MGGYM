from gym.models import Member,SubscriptionPlan,MembershipSubscription,Payment
from rest_framework.serializers import ModelSerializer,SerializerMethodField
from rest_framework import serializers


class SubscriptionPlanSerializer(ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class MemberSerializer(ModelSerializer):  
    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'phone', 'dob', 'joined_date', 'passport_photo']

    

class MembershipSubscriptionSerializer(ModelSerializer):
    member = MemberSerializer(read_only=True)
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = MembershipSubscription
        fields = '__all__'


class MemberSerializer(ModelSerializer):
    subscriptions = MembershipSubscriptionSerializer(many = True,read_only=True)
    status = SerializerMethodField()

    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'phone', 'dob', 'joined_date', 'passport_photo','status', 'subscriptions']

    def get_status(self, obj):
        lates_subscription = obj.subscriptions.order_by('-start_date').first()
        if lates_subscription:
            return lates_subscription.status
        return 'No subscription'


 