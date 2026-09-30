from django.db import models

class UserProfile(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    demo_balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} ({self.phone_number or 'No Phone'})"

class GameRoom(models.Model):
    STAKE_CHOICES = [(0, 'Demo'), (5, '5 Birr'), (10, '10 Birr'), (50, '50 Birr')]
    stake_amount = models.IntegerField(choices=STAKE_CHOICES, default=5)
    status = models.CharField(max_length=20, default='waiting')
    called_numbers = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)  # <-- የተጨመረ

    def __str__(self):
        return f"Room #{self.id} Stake: {self.stake_amount}"

class ActiveSelection(models.Model):
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    cartela_id = models.IntegerField()
    is_auto = models.BooleanField(default=True)            # <-- የተጨመረ
    is_terminated = models.BooleanField(default=False)    # <-- የተጨመረ


# ---------------------------------------------------------
# አዳዲሶቹ የቦት ሴቲንግ እና በተኖች መቆጣጠሪያ ሞዴሎች (Dynamic Admin Bot)
# ---------------------------------------------------------

class BotSetting(models.Model):
    welcome_text = models.TextField(default="Welcome to Edil Bingo! Choose an option below.")
    logo = models.ImageField(upload_to='bot_logos/', blank=True, null=True, help_text="የቦቱን ሎጎ ፎቶ እዚህ ይጫኑ")

    def __str__(self):
        return "Bot General Settings"

class BotButton(models.Model):
    text = models.CharField(max_length=100, help_text="የተኑ ስም (ለምሳሌ: Play Bingo 🎮)")
    url = models.URLField(blank=True, null=True, help_text="የዌብ አፕ ወይም የድር ጣቢያ ሊንክ")
    is_web_app = models.BooleanField(default=False, help_text="ይህ በተን Mini App (WebApp) የሚከፍት ከሆነ ቲክ ያድርጉት")
    order = models.IntegerField(default=0, help_text="የተኖች ቅደም ተከተል ቁጥር (ለምሳሌ: 1, 2, 3...)")
    is_active = models.BooleanField(default=True, help_text="ቦቱ ላይ እንዲታይ ከፈለጉ ቲክ ያድርጉ")

    def __str__(self):
        return self.text