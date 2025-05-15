from django.shortcuts import render

# Create your views here.

# core/views.py
import subprocess
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

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
