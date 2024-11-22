from django.contrib import admin

# Register your models here.
from gym.models import Member,SubscriptionPlan,MembershipSubscription,Payment

# admin.site.register(Member)
# admin.site.register(SubscriptionPlan)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id','name')

@admin.register(MembershipSubscription)
class MembershipSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('member', 'subscription_plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'subscription_plan')
    search_fields = ('member__name', 'subscription_plan__name')

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('id','name')

admin.site.register(Payment)
