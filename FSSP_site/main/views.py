from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.context_processors import static

from .models import Card
# from .forms import CustomUserCreationForm  # Если используешь кастомную модель

def register(request):
    context = {'msg': ""}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        # for DB
        # username = req.POST.get('username')
        # password = req.POST.get('password')

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


def loginCastom(req):
    if req.method == 'POST':
        username = req.POST.get('username')
        password = req.POST.get('password')
        # messages.success(req, f'{username} {password}')
        if not req.user.is_authenticated:
            messages.success(req, f'zalupa')
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

    # Получаем все активные карточки, отсортированные по дате парсинга и порядку
    cards = Card.objects.filter(is_active=True).order_by('-parsed_date', 'order')
    
    # Добавляем дополнительную информацию для каждой карточки
    for card in cards:
        card.parsed_date_formatted = card.parsed_date.strftime("%d.%m.%Y %H:%M")
        if card.source_url:
            card.source_domain = card.source_url.split('/')[2] if len(card.source_url.split('/')) > 2 else ''
    
    context['cards'] = cards
    return render(request, 'Front/Main Website/index.html', context)


def start(req):
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'main/profile.html')

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_panel(request):
    return render(request, 'main/admin_panel.html')