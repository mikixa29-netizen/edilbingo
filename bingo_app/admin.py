from django.contrib import admin
from .models import UserProfile, GameRoom, ActiveSelection, BotSetting, BotButton

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

@admin.register(BotSetting)
class BotSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'welcome_text')

@admin.register(BotButton)
class BotButtonAdmin(admin.ModelAdmin):
    list_display = ('text', 'url', 'is_web_app', 'order', 'is_active')
    list_filter = ('is_active', 'is_web_app')
    list_editable = ('order', 'is_active')