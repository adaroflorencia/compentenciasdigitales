from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def registro_usuario(request):
    next_url = request.GET.get('next', 'index')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
            return redirect(request.POST.get('next') or 'index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def iniciar_sesion(request):
    next_url = request.GET.get('next', 'index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '¡Inicio de sesión exitoso!')
                return redirect(request.POST.get('next', 'index'))  # Redirige a la URL anterior
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

@login_required
def signout(request):
    logout(request)
    return redirect('index')
