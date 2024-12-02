from datetime import timedelta
from django.db import models
from django.utils.timezone import now
import uuid


class Member(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    dob = models.DateField() 
    passport_photo = models.ImageField(upload_to='passport_photos/', blank=True, null=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-joined_date']

    @property
    def is_active(self):
        """
        Check if the member has at least one active subscription.
        """
        active_subscription = self.subscriptions.filter(is_active=True, end_date__gte=now()).exists()
        return active_subscription
    
    def save(self, *args, **kwargs):
        if self.passport_photo:
            # Create a unique file name based on UUID
            extension = self.passport_photo.name.split('.')[-1]
            filename = f"{uuid.uuid4()}.{extension}"
            self.passport_photo.name = f"passport_photos/{filename}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)  # e.g., Monthly, Yearly
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_in_days = models.PositiveIntegerField()  # e.g., 30 for monthly, 365 for yearly
    
    def __str__(self):
        return f"{self.name} - {self.price}"


class MembershipSubscription(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Pending', 'Pending'),
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='subscriptions')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()  # Allow blank/null for initial save
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Automatically mark as expired if the end date is in the past
        if self.status =='Expired':
            self.is_active = False 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member} - {self.subscription_plan.name}"



class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payment')
    subscription = models.OneToOneField(MembershipSubscription, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50, choices=(('Success', 'Success'), ('Failed', 'Failed')))

    def __str__(self):
        return f"{self.payment_status}"