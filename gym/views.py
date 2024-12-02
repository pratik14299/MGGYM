from datetime import timedelta, datetime
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from .models import Member,MembershipSubscription,SubscriptionPlan,Payment
from .serializers import MemberSerializer,MembershipSubscriptionSerializer,SubscriptionPlanSerializer,PaymentSerializer
from rest_framework.views import APIView
from rest_framework import status
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font 
from io import BytesIO
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils.dateparse import parse_datetime
from django.db.models.functions import TruncMonth, TruncDate
from django.db import transaction
from django.shortcuts import get_object_or_404



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
    def get(self, request):
        """
        Return all payments.
        """
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """
        Handle the creation of a new payment and a new subscription for a member.
        """
        data = request.data

        # Validate member and subscription plan existence
        member = get_object_or_404(Member, id=data['member'])
        subscription_plan = get_object_or_404(SubscriptionPlan, id=data['subscription_plan'])

        active_subscription = MembershipSubscription.objects.filter(
            member=member, status="Active").exists()

        if active_subscription:
            return Response({"error": "Member already has an active subscription."}, status=status.HTTP_403_FORBIDDEN)

        # Start transaction to ensure atomicity
        with transaction.atomic():
            # Create a new subscription every time
            subscription = MembershipSubscription.objects.create(
                member=member,
                subscription_plan=subscription_plan,
                start_date=data["start_date"],
                end_date=data["end_date"],
                is_active=False,
                status="Pending",
            )

            # Create payment data and handle the payment status
            payment_data = {
                "member": member.id,
                "amount_paid": data['amount_paid'],
                "payment_status": data['payment_status'],
                "subscription": subscription.id  # Link the payment to the new subscription
            }

            # Update the subscription status based on payment status
            if data['payment_status'] == 'Success':
                subscription.status = "Active"
                subscription.is_active = True
            elif data['payment_status'] == 'Failed':
                subscription.status = "Pending"
                subscription.is_active = False

            # Save the subscription after updating status
            subscription.save()

            # Now create the payment record
            payment_serializer = PaymentSerializer(data=payment_data)
            if payment_serializer.is_valid():
                payment = payment_serializer.save()

                # Return the payment and subscription data in the response
                return Response({
                    "payment": payment_serializer.data,
                    "subscription": MembershipSubscriptionSerializer(subscription).data
                }, status=status.HTTP_201_CREATED)

            return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Update an existing payment and the associated subscription.
        """
        data = request.data

        # Fetch the existing payment using the provided pk (Primary Key)
        payment = get_object_or_404(Payment, pk=pk)

        # Validate member and subscription plan existence
        member = get_object_or_404(Member, id=data['member'])
        subscription_plan = get_object_or_404(SubscriptionPlan, id=data['subscription_plan'])

        # Parse end_date directly from the request data
        end_date = data.get("end_date")
        if not end_date:
            raise ValidationError({"end_date": "This field is required."})

        # Ensure the provided date is valid
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError({"end_date": "Invalid date format. Use 'YYYY-MM-DD'."})

        # Start transaction to ensure atomicity
        with transaction.atomic():
            # If the payment is linked to an existing subscription, fetch that subscription
            subscription = payment.subscription

            if subscription:
                # Update the existing subscription
                subscription.subscription_plan = subscription_plan
                subscription.start_date = data["start_date"]
                subscription.end_date = end_date

                # Check if the subscription has expired
                if end_date < now().date():
                    subscription.status = "Expired"
                    subscription.is_active = False
                else:
                    subscription.is_active = False  # Set to false before payment confirmation
                    subscription.status = "Pending"
                subscription.save()
            else:
                # Handle case where no existing subscription is found
                if end_date < now().date():
                    stat = "Expired"
                    is_active = False
                else:
                    stat = "Pending"
                    is_active = False
                subscription = MembershipSubscription.objects.create(
                    member=member,
                    subscription_plan=subscription_plan,
                    start_date=data["start_date"],
                    end_date=end_date,
                    is_active=is_active,
                    status=stat,  # Assign `status` correctly
                )

            # Update the payment data based on the request
            payment_data = {
                "member": member.id,
                "amount_paid": data['amount_paid'],
                "payment_status": data['payment_status'],
                "subscription": subscription.id
            }

            # Update the subscription status based on the payment status
            if data['payment_status'] == 'Success':
                if subscription.status != "Expired":  # Only activate if not already expired
                    subscription.status = "Active"
                    subscription.is_active = True
            elif data['payment_status'] == 'Failed':
                subscription.status = "Pending"
                subscription.is_active = False

            # Save the subscription after updating status
            subscription.save()

            # Update the payment record
            payment_serializer = PaymentSerializer(payment, data=payment_data)
            if payment_serializer.is_valid():
                payment = payment_serializer.save()

                # Return the updated payment and subscription data in the response
                return Response({
                    "payment": payment_serializer.data,
                    "subscription": MembershipSubscriptionSerializer(subscription).data
                }, status=status.HTTP_200_OK)

            return Response(payment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def member_typeahead(request): 
    query = request.GET.get('q', '')  
    if query:
        # Perform the search using `icontains` for a case-insensitive search
        members = Member.objects.filter(name__icontains=query)
    else:
        # Return no members if no query is provided
        members = Member.objects.none()

    # Serialize the results into JSON
    return JsonResponse(list(members.values('id', 'name')), safe=False)


class Notification(APIView):
    """
    Provides members who's subscriptions will be end .
    """
    # permission_classes = [IsAuthenticated]
    def get(self, request): 

        notify_date = now().date() + timedelta(days=5)

        # Fetch all subscriptions
        data = MembershipSubscription.objects.all()

        # Filter memberships manually
        about_to_end_memberships = []
        for i in data:
            if i.is_active and i.end_date:
                if now().date() <= i.end_date <= notify_date:
                    about_to_end_memberships.append(i)

        # Serialize the filtered data
        serializer = MembershipSubscriptionSerializer(about_to_end_memberships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def analytics_view(request):
    # Total revenue
    total_revenue = Payment.objects.filter(payment_status='Success').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    # Total active subscriptions
    total_active_subscriptions = MembershipSubscription.objects.filter(is_active=True).count()

    # Increase in subscriptions from last month
    today = now()
    last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    current_month_start = today.replace(day=1)
    last_month_subscriptions = MembershipSubscription.objects.filter(start_date__gte=last_month_start, start_date__lt=current_month_start).count()
    current_month_subscriptions = MembershipSubscription.objects.filter(start_date__gte=current_month_start).count()
    subscription_increase = current_month_subscriptions - last_month_subscriptions

    # Total members and members with active subscriptions
    total_members = Member.objects.count()
    members_with_active_subscriptions = Member.objects.filter(subscriptions__is_active=True).distinct().count()

    # Total subscriptions till date
    total_subscriptions = MembershipSubscription.objects.count()

    # Chart data for revenue
    payments = Payment.objects.filter(payment_status='Success')
    monthly_revenue = (
        payments.annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total_revenue=Sum('amount_paid'))
        .order_by('month')
    )
    chart_data = [
        {"month": revenue["month"].strftime("%B"), "revenue": revenue["total_revenue"]}
        for revenue in monthly_revenue
    ]

    # Recent members (new members in the last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    recent_members = Member.objects.filter(joined_date__gte=thirty_days_ago).count()

    response_data = {
        "total_revenue": total_revenue,
        "total_active_subscriptions": {
            "count": total_active_subscriptions,
            "increase_from_last_month": subscription_increase
        },
        "total_members": {
            "count": total_members,
            "with_active_subscriptions": members_with_active_subscriptions
        },
        "total_subscriptions": total_subscriptions,
        "chart_data": chart_data,
        "recent_members": recent_members,
    }
    return Response(response_data)


class AnalyticsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the date range from the query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Parse dates if they are provided, otherwise use defaults
        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)
        if not start_date:
            start_date = now() - timedelta(days=365)  # Default to 1 year ago
        if not end_date:
            end_date = now()  # Default to the current time

        # Convert datetime to date for consistency
        start_date = start_date.date() if isinstance(start_date, datetime) else start_date
        end_date = end_date.date() if isinstance(end_date, datetime) else end_date

        # Member statistics
        total_members = Member.objects.count()
        active_members = Member.objects.filter(
            subscriptions__status='Active',
            subscriptions__start_date__lte=end_date,
            subscriptions__end_date__gte=start_date
        ).distinct().count()
        inactive_members = total_members - active_members

        # New members by date (e.g., monthly, weekly)
        new_members_by_date = Member.objects.filter(joined_date__range=[start_date, end_date])\
            .annotate(date=TruncDate('joined_date'))\
            .values('date')\
            .annotate(count=Count('id'))

        # Subscription Plan Distribution
        subscription_plan_data = SubscriptionPlan.objects.annotate(
            member_count=Count('membershipsubscription')
        )

        total_revenue_from_subscriptions = 0

        for subscription in MembershipSubscription.objects.filter(start_date__lte=end_date, end_date__gte=start_date):
            effective_start = max(subscription.start_date, start_date)
            effective_end = min(subscription.end_date, end_date)
            days_active = (effective_end - effective_start).days + 1
            daily_rate = subscription.subscription_plan.price / subscription.subscription_plan.duration_in_days
            total_revenue_from_subscriptions += daily_rate * days_active

        # Calculate total revenue from payments
        payment_data = Payment.objects.filter(payment_date__range=[start_date, end_date])
        total_revenue = payment_data.aggregate(total_revenue=Sum('amount_paid'))['total_revenue'] or 0

        # Ensure revenue from subscriptions is properly considered along with payments
        total_revenue = total_revenue_from_subscriptions + total_revenue

        # Revenue Over Time
        revenue_by_date = payment_data\
            .values('payment_date')\
            .annotate(total_revenue=Sum('amount_paid'))

        # Payments Data
        total_payments = payment_data.count()
        successful_payments = payment_data.filter(payment_status='Success').count()
        failed_payments = total_payments - successful_payments
        payment_status_distribution = payment_data\
            .values('payment_status')\
            .annotate(count=Count('id'))

        # Expiration Trends
        expired_subscriptions = MembershipSubscription.objects.filter(
            end_date__lt=now().date(),  # Convert `now` to date for comparison
            end_date__range=[start_date, end_date]
        ).count()
        renewals = MembershipSubscription.objects.filter(
            status='Active',
            end_date__gte=now().date(),
            created_at__range=[start_date, end_date]
        ).count()

        expiration_trends = MembershipSubscription.objects.filter(end_date__range=[start_date, end_date])\
            .values('end_date')\
            .annotate(count=Count('id'))

        # Retention Rate Calculation
        retention_rate = (active_members / total_members) * 100 if total_members else 0

        # Retention Rate Trends (Monthly Retention)
        active_members_start_of_month = Member.objects.filter(
            subscriptions__start_date__lte=start_date
        ).annotate(month=TruncMonth('subscriptions__start_date')).values('month').distinct()

        retention_rate_trends = []
        for month in active_members_start_of_month:
            # Get the count of active members at the start of the month
            start_of_month_count = active_members_start_of_month.filter(month=month['month']).count()

            # Get the count of those members who are still active by the end of the month
            still_active_at_end_of_month = Member.objects.filter(
                subscriptions__end_date__gte=month['month'] + timedelta(days=30),  # Assuming monthly retention
                subscriptions__start_date__lte=month['month']
            ).distinct().count()

            # Calculate retention rate
            retention_rate_for_month = (still_active_at_end_of_month / start_of_month_count) * 100 if start_of_month_count else 0

            retention_rate_trends.append({
                'month': month['month'],
                'retentionRate': retention_rate_for_month
            })

        # Return the analytics response
        return Response({
            'memberStatistics': {
                'totalMembers': total_members,
                'activeMembers': active_members,
                'inactiveMembers': inactive_members,
                'newMembersByDate': new_members_by_date
            },
            'subscriptionPlans': {
                'totalRevenue': total_revenue_from_subscriptions,
                'planDistribution': [
                    {
                        'planName': plan.name,
                        'memberCount': plan.member_count,
                        'price': plan.price
                    }
                    for plan in subscription_plan_data
                ]
            },
            'revenueOverTime': {
                'totalRevenue': total_revenue,
                'revenueByDate': revenue_by_date
            },
            'payments': {
                'totalPayments': total_payments,
                'successfulPayments': successful_payments,
                'failedPayments': failed_payments,
                'paymentStatusDistribution': payment_status_distribution
            },
            'expirations': {
                'expiredSubscriptions': expired_subscriptions,
                'renewals': renewals,
                'expirationTrends': expiration_trends
            },
            'memberRetention': {
                'retentionRate': retention_rate,
                'retentionTrends': retention_rate_trends  # Monthly retention trends added
            }
        }, status=status.HTTP_200_OK)


class DownloadExcelView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the date range from the query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Parse dates if provided, otherwise use defaults
        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)
        if not start_date:
            start_date = now() - timedelta(days=365)  # Default to 1 year ago
        if not end_date:
            end_date = now()  # Default to the current time

        # Filter data based on the date range and active subscriptions
        active_subscriptions = MembershipSubscription.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_active=True  # Only consider active subscriptions
        )

        # Get the related members for active subscriptions
        members = Member.objects.filter(subscriptions__in=active_subscriptions).distinct()

        # Create an Excel workbook and worksheet
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Revenue Report"

        # Add the date range at the top
        date_range_row = f"Report for Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        worksheet.append([date_range_row])

        # Add a blank row after the date range
        worksheet.append([])

        # Define header row
        headers = ['Name', 'Phone', 'Start Date', 'End Date', 'Plan', 'Amount']
        worksheet.append(headers)

        # Style the header row
        for col_num, header in enumerate(headers, 1):
            cell = worksheet.cell(row=3, column=col_num)  # Adjust row index for the header
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        # Add data rows
        total_earning = 0
        for member in members:
            active_subscription = member.subscriptions.filter(is_active=True).first()
            plan = active_subscription.subscription_plan if active_subscription else None

            # Fetch the corresponding payment amount
            payment = Payment.objects.filter(subscription=active_subscription, payment_status='Success').first()
            amount_paid = payment.amount_paid if payment else 0

            row = [
                member.name,
                member.phone,
                active_subscription.start_date if active_subscription else 'N/A',
                active_subscription.end_date if active_subscription else 'N/A',
                plan.name if plan else 'N/A',
                amount_paid
            ]
            total_earning += amount_paid
            worksheet.append(row)

        # Add total earning row at the end
        total_row = ['Total', '', '', '', '', total_earning]
        worksheet.append(total_row)

        # Adjust column widths without merged cells
        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter  # Get the column letter
            
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except Exception:
                    pass

            adjusted_width = max_length + 2
            worksheet.column_dimensions[col_letter].width = adjusted_width

        # Save the workbook to a BytesIO stream
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)

        # Generate a response with the Excel file
        response = HttpResponse(
            excel_file,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Revenue_Report.xlsx"'
        return response