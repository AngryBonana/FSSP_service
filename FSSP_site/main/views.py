from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Card, FilterDate
from django.utils import timezone
from main.services.LLM.searcher import *
from django.views.decorators.csrf import csrf_exempt

def register(request):
    context = {'msg': ""}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')  # Редирект после успеха
        else:
            context['msg'] = "Данные некорректны!"

    return render(request, 'Front/Registration/index.html', context)

def logoutCastom(req):
    logout(req)
    return redirect('home')

@csrf_exempt
def loginCastom(req):
    if req.method == 'POST':
        username = req.POST.get('username')
        password = req.POST.get('password')
        if not req.user.is_authenticated:
            messages.success(req, f'Неудачная попытка входа!')
        # Проверяем аутентификацию
        user = authenticate(req, username=username, password=password)
        if user is not None:
            login(req, user)
            return redirect('mainp')  # Перенаправляем на главную
        else:
            messages.error(req, 'Неверный логин или пароль')

    return render(req, 'Front/Log_in/index.html')


def home(request):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
        context['is_admin'] = request.user.is_superuser

    # Получаем последнюю установленную дату фильтрации
    try:
        filter_date = FilterDate.objects.latest('created_at').filter_date
    except FilterDate.DoesNotExist:
        filter_date = timezone.now().date()  # Если нет даты, используем текущую

    # Фильтруем карточки
    cards = Card.objects.filter(
        is_active=True,
        parsed_date__date__gte=filter_date
    ).order_by('-parsed_date', 'order')

    # Добавляем дополнительную информацию
    for card in cards:
        card.parsed_date_formatted = card.parsed_date.strftime("%d.%m.%Y %H:%M")
        if card.source_url:
            card.source_domain = card.source_url.split('/')[2] if len(card.source_url.split('/')) > 2 else ''
    print("len cards = ", len(cards))
    context['cards'] = cards
    context['current_filter_date'] = filter_date.strftime("%Y-%m-%d")
    return render(request, 'Front/Main Website/index.html', context)


# Для разрабокти в продакшене будет программа которая автоматически запускает
def run_p(req):
    # parser = ArbitrAPIParser(api_key="KAD_API_KEY")
    # parser.run("2025-05-25", "2025-05-27")
    # llm
    analyze_parsed()
    return redirect('login')
    # pass

def start(request):
    # if request.user.is_authenticated:
    #     return redirect('mainp')
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'main/profile.html')

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_panel(request):
    return render(request, 'main/admin_panel.html')