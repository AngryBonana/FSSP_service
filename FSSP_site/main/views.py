from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import SiteText
# from .forms import CustomUserCreationForm  # Если используешь кастомную модель

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        # for DB
        # username = req.POST.get('username')
        # password = req.POST.get('password')

        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход
            return redirect('home')  # Редирект после успеха
    else:
        form = UserCreationForm()

    return render(request, 'main/register.html', {'form': form})

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
            return redirect('home')  # Перенаправляем на главную
        else:
            messages.error(req, 'Неверный логин или пароль')

    return render(req, 'main/login.html')


def home(request):
    # Проверяем, авторизован ли пользователь
    context = {}

    if request.user.is_authenticated:
        context['username'] = request.user.username
        context['is_admin'] = request.user.is_superuser

    welcome_text, created = SiteText.objects.get_or_create(
        name='welcome_message',
        defaults={'content': 'Добро пожаловать на наш сайт!'}
    )

    welcome_text1, created1 = SiteText.objects.get_or_create(
        name='welcome_us_message',
        defaults={'content': 'Добро пожаловать на наш сайт!'}
    )

    context['welcome_text'] = welcome_text.content
    context['welcome_us_text'] = welcome_text1.content
    return render(request, 'main/home.html', context)


@login_required
def profile(request):
    return render(request, 'main/profile.html')

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_panel(request):
    return render(request, 'main/admin_panel.html')