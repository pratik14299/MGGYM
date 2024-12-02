from django.contrib import admin
from django.urls import path
from django.urls import path
from . import views
from .views import (
    MemberDetails,
    SubscriptionPlanDetails,
    MembershipSubscriptionDetails,
    PaymentAPIView,
    LoggedInUserView,
    Notification,
    analytics_view,
    AnalyticsAPIView,
    DownloadExcelView
)

urlpatterns = [
    path('members/', MemberDetails.as_view(), name="add_member"),
    path('member/<int:pk>/', MemberDetails.as_view(), name="member_detail"),
    path('plans/', SubscriptionPlanDetails.as_view(), name="list_plans"),
    path('plans/<int:pk>/', SubscriptionPlanDetails.as_view(), name="plan_detail"),
    path('subscriptions/', MembershipSubscriptionDetails.as_view(), name="manage_subscriptions"),
    path('subscriptions/<int:pk>/', MembershipSubscriptionDetails.as_view(), name="subscription_detail"),
    path('payments/', PaymentAPIView.as_view(), name="manage_payments"),
    path('payments/<int:pk>/', PaymentAPIView.as_view(), name="update_payments"),
    path('user/', LoggedInUserView.as_view(), name='logged_in_user'),
    path('search/', views.member_typeahead, name='member_typeahead'),
    path('notification/',Notification.as_view(),name="Notification"),
    path('analytics/', analytics_view, name='analytics'),
    path('analytics-full/', AnalyticsAPIView.as_view(), name='analytics'),
    path('Download/', DownloadExcelView.as_view(), name='download'),

    # path('payments/<int:pk>/', PaymentAPIView.as_view(), name="payment_detail"),
]
