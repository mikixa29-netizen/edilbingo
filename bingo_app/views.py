from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, GameRoom, ActiveSelection
from .cartelas_data import CARTELAS
import json

def index(request):
    return render(request, 'index.html')
from django.shortcuts import render

def game_view(request):
    # ተጫዋቹ ሲገባ የሚሰራው ኮድ ወይም ሬንደር የሚደረገው ቴምፕሌት እዚህ አለ
    return render(request, 'bingo_app/game.html')

def get_game_data(request):
    telegram_id = request.GET.get('tg_id')
    stake = int(request.GET.get('stake', 5))

    user = UserProfile.objects.filter(telegram_id=telegram_id).first()
    room, _ = GameRoom.objects.get_or_create(stake_amount=stake, status='waiting')

    taken_cards = list(ActiveSelection.objects.filter(room=room).values_list('cartela_id', flat=True))
    my_cards = list(ActiveSelection.objects.filter(room=room, user=user).values_list('cartela_id', flat=True)) if user else []
    
    balance = user.demo_balance if stake == 0 else user.balance if user else 0

    return JsonResponse({
        'balance': float(balance),
        'stake': stake,
        'takenCards': taken_cards,
        'myCards': my_cards,
        'gameStatus': room.status,
        'totalFixedCards': 200 # 200 ካርዶች እንዳሉ ያሳውቃል
    })

@csrf_exempt
def select_cartela(request):
    data = json.loads(request.body)
    tg_id, cartela_id, stake = data.get('telegramId'), data.get('cartelaId'), data.get('stake')

    if cartela_id not in CARTELAS:
        return JsonResponse({'message': 'ትክክለኛ ያልሆነ ካርድ!'}, status=400)

    user = UserProfile.objects.get(telegram_id=tg_id)
    room, _ = GameRoom.objects.get_or_create(stake_amount=stake, status='waiting')

    if ActiveSelection.objects.filter(room=room, user=user).count() >= 2:
        return JsonResponse({'message': 'ከ2 ካርድ በላይ መያዝ አይቻልም!'}, status=400)

    if ActiveSelection.objects.filter(room=room, cartela_id=cartela_id).exists():
        return JsonResponse({'message': 'ይህ ካርድ በሌላ ሰው ተይዟል!'}, status=400)

    ActiveSelection.objects.create(room=room, user=user, cartela_id=cartela_id)
    return JsonResponse({'success': True, 'message': f'ካርድ {cartela_id} ተመርጧል!'})