from django.contrib import admin
from .models import UserProfile, GameRoom, ActiveSelection

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'first_name', 'phone_number', 'balance', 'demo_balance', 'created_at')
    search_fields = ('telegram_id', 'phone_number', 'first_name')
    list_editable = ('balance', 'demo_balance')

@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'stake_amount', 'status', 'created_at')
    list_filter = ('status', 'stake_amount')

@admin.register(ActiveSelection)
class ActiveSelectionAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'cartela_id', 'is_auto', 'is_terminated')