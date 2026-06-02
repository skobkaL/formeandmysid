from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomLoginForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('tools:dashboard')
    
    form = CustomLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Добро пожаловать, {user.get_full_name() or user.username}!')
        return redirect('tools:dashboard')
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('accounts:login')

def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})