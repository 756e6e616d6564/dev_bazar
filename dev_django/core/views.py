from django.shortcuts import render

# Create your views here.

# core/views.py


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
import subprocess

def landing_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # You'll need to define a 'home' URL
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


@csrf_exempt  # Evita verificación CSRF para permitir que GitHub envíe POSTs
def github_webhook(request):
    if request.method == 'POST':
        try:
            # Ruta a tu repo en el EC2
            repo_path = "/home/ec2-user/dev/dev_bazar"

            # Ejecuta git pull
            subprocess.run(["git", "-C", repo_path, "pull"], check=True)

            # (Opcional) reiniciar Gunicorn o Supervisor
            # subprocess.run(["sudo", "systemctl", "restart", "gunicorn"], check=True)

            return HttpResponse("Actualizado", status=200)
        except subprocess.CalledProcessError as e:
            return HttpResponse(f"Error en git pull: {e}", status=500)
    else:
        return HttpResponse("Método no permitido", status=405)
