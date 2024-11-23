from datetime import timedelta
from django.shortcuts import render
from .models import Member,MembershipSubscription,SubscriptionPlan,Payment
from .serializers import MemberSerializer,MembershipSubscriptionSerializer,SubscriptionPlanSerializer,PaymentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class LoggedInUserView(APIView):
    permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, status=200)
    
    
class MemberDetails(APIView):
    """
    Handles CRUD operations for members.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        if pk:
            try:
                member = Member.objects.get(pk=pk)
                serializer = MemberSerializer(member)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Member.DoesNotExist:
                return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        data = Member.objects.all()
        serializer = MemberSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = MemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            member = Member.objects.get(pk=pk)
            member.delete()
            return Response({"message": "Member deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Member.DoesNotExist:
            return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)


class SubscriptionPlanDetails(APIView):
    """
    Handles CRUD operations for subscription plans.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        if pk:
            try:
                plan = SubscriptionPlan.objects.get(pk=pk)
                serializer = SubscriptionPlanSerializer(plan)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except SubscriptionPlan.DoesNotExist:
                return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)
        data = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            plan = SubscriptionPlan.objects.get(pk=pk)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubscriptionPlanSerializer(plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            plan = SubscriptionPlan.objects.get(pk=pk)
            plan.delete()
            return Response({"message": "Plan deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND)


class MembershipSubscriptionDetails(APIView):
    """
    Handles CRUD operations for memberships.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, pk=None):
        if pk:
            try:
                subscription = MembershipSubscription.objects.get(pk=pk)
                serializer = MembershipSubscriptionSerializer(subscription)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except MembershipSubscription.DoesNotExist:
                return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        data = MembershipSubscription.objects.all()
        serializer = MembershipSubscriptionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            subscription = MembershipSubscription.objects.get(pk=pk)
        except MembershipSubscription.DoesNotExist:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = MembershipSubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            subscription = MembershipSubscription.objects.get(pk=pk)
            subscription.delete()
            return Response({"message": "Subscription deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except MembershipSubscription.DoesNotExist:
            return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
 
class PaymentAPIView(APIView):
    """
    API to handle payments, create or update subscriptions, and manage subscription status.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data

        try:
            # Fetch the member and subscription plan from the request
            member = Member.objects.get(id=data['member'])
            subscription_plan = SubscriptionPlan.objects.get(id=data['subscription_plan'])
        except (Member.DoesNotExist, SubscriptionPlan.DoesNotExist) as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        # Create or update the MembershipSubscription linked to the selected subscription plan
        subscription, created = MembershipSubscription.objects.get_or_create(
            member=member,
            subscription_plan=subscription_plan,
            defaults={
                "start_date": now(),
                "end_date": now() + timedelta(days=subscription_plan.duration_in_days),
                "is_active": False,
                "status": "Pending",
            },
        )

        if not created:
            # If subscription already exists, update the end_date and reset status
            subscription.start_date = now()
            subscription.end_date = now() + timedelta(days=subscription_plan.duration_in_days)
            subscription.status = "Pending"
            subscription.is_active = False
            subscription.save()

        # Now create the payment record
        payment_serializer = PaymentSerializer(data={
            "member": member.id,
            "subscription_plan": subscription_plan.id,  # Here we pass the subscription_plan to link with the payment
            "amount_paid": data['amount_paid'],
            "payment_status": data['payment_status'],
        })

        if payment_serializer.is_valid():
            payment = payment_serializer.save()

            # Update subscription status based on payment status
            if payment.payment_status == 'Success':
                subscription.status = "Active"
                subscription.is_active = True
            elif payment.payment_status == 'Failed':
                subscription.status = "Expired"
                subscription.is_active = False

            subscription.save()

            return Response({
                "payment": payment_serializer.data,
                "subscription": MembershipSubscriptionSerializer(subscription).data
            }, status=status.HTTP_201_CREATED)

        return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
