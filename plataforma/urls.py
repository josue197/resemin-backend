
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse

from consulta.views import (
    panel_dashboard, panel_subir_excel, panel_configurar_columnas, panel_activar_excel,
    consulta_api, columnas_visibles_api, consulta_form
)

def health(request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),

    # Panel interno (requiere login)
    path('panel/', panel_dashboard, name='panel_dashboard'),
    path('panel/subir/', panel_subir_excel, name='panel_subir_excel'),
    path('panel/configurar/<int:archivo_id>/', panel_configurar_columnas, name='panel_configurar_columnas'),
    path('panel/activar/<int:archivo_id>/', panel_activar_excel, name='panel_activar_excel'),

    # APIs públicas
    path('api/consulta/', consulta_api, name='consulta_api'),
    path('api/columnas/', columnas_visibles_api, name='columnas_visibles_api'),

    # Página para colaboradores (formulario)
    path('consulta/', consulta_form, name='consulta_form'),

    # Raíz → formulario
    path('', RedirectView.as_view(url='/consulta/', permanent=False)),

    # Healthcheck (opcional)
