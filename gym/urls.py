from django.contrib import admin
from django.urls import path
from django.urls import path
from .views import (
    MemberDetails,
    SubscriptionPlanDetails,
    MembershipSubscriptionDetails,
    PaymentAPIView
)

urlpatterns = [
    path('members/', MemberDetails.as_view(), name="add_member"),
    path('members/<int:pk>/', MemberDetails.as_view(), name="member_detail"),
    path('plans/', SubscriptionPlanDetails.as_view(), name="list_plans"),
    path('plans/<int:pk>/', SubscriptionPlanDetails.as_view(), name="plan_detail"),
    path('subscriptions/', MembershipSubscriptionDetails.as_view(), name="manage_subscriptions"),
    path('subscriptions/<int:pk>/', MembershipSubscriptionDetails.as_view(), name="subscription_detail"),
    path('payments/', PaymentAPIView.as_view(), name="manage_payments"),
    # path('payments/<int:pk>/', PaymentAPIView.as_view(), name="payment_detail"),
]
