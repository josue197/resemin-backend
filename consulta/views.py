
# ---------- API pública: consulta por DNI y fecha ----------
def consulta_api(request):
    dni = request.GET.get('dni')
    fecha = request.GET.get('fecha')

    if not dni or not fecha:
        return JsonResponse({"error": "Debe proporcionar DNI y fecha"}, status=400)

    archivo = _get_activo()
    if not archivo:
        return JsonResponse({"error": "No hay un Excel activo"}, status=404)

    dni_col, fecha_col, visibles = _get_config(archivo)
    if not dni_col or not fecha_col:
        return JsonResponse({"error": "Configura columnas DNI y Fecha en el panel"}, status=400)

    posibles = Registro.objects.filter(**{f"datos__{dni_col}": dni, 'archivo': archivo})
    fecha_norm = _normalize_fecha(fecha)
    hallado = None
    for reg in posibles:
        valor_fecha = (reg.datos.get(fecha_col) or '').strip()
        if valor_fecha == fecha or valor_fecha == fecha_norm:
            hallado = reg
            break

    if hallado:
        return JsonResponse({"resultado": {col: hallado.datos.get(col) for col in visibles}})
    return JsonResponse({"error": "No encontrado"}, status=404)


# ---------- API pública: columnas visibles ----------
def columnas_visibles_api(request):
    archivo = _get_activo()
    if not archivo:
        return JsonResponse({"error": "No hay un Excel activo"}, status=404)

    _, _, visibles = _get_config(archivo)
    return JsonResponse({"columnas_visibles": visibles})

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import ArchivoExcel, ConfiguracionColumna, Registro

# ---------- Funciones de apoyo que ya usamos en la API ----------
def _get_activo():
    return ArchivoExcel.objects.filter(activo=True).first()

def _get_config(archivo):
    columnas = ConfiguracionColumna.objects.filter(archivo=archivo)
    dni_col = columnas.filter(es_dni=True).values_list('nombre_columna', flat=True).first()
    fecha_col = columnas.filter(es_fecha_ingreso=True).values_list('nombre_columna', flat=True).first()
    visibles = list(columnas.filter(visible=True).values_list('nombre_columna', flat=True))
    return dni_col, fecha_col, visibles

def _normalize_fecha(fecha_str):
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(fecha_str.strip(), fmt).date().isoformat()
        except Exception:
            pass
    return (fecha_str or '').strip()

# ---------- API existente (no tocar si ya la tienes) ----------
# consulta_api y columnas_visibles_api

# ---------- Panel (admin simple) que ya tienes con login ----------
@login_required
def panel_dashboard(request):
    archivos = ArchivoExcel.objects.all().order_by('-fecha_subida')
    activo = _get_activo()
    return render(request, 'panel/dashboard.html', {'archivos': archivos, 'activo': activo})

@login_required
def panel_subir_excel(request):
    import pandas as pd  # lo usamos aquí para subir Excel
    if request.method == 'POST':
        archivo_file = request.FILES.get('excel_file')
        marcar_activo = request.POST.get('activo') == 'on'
        if not archivo_file:
            messages.error(request, 'Debes seleccionar un archivo Excel.')
            return redirect('panel_dashboard')
        obj = ArchivoExcel.objects.create(archivo=archivo_file, activo=marcar_activo)
        try:
            df = pd.read_excel(obj.archivo.path, engine='openpyxl').astype(str).fillna('')
            existentes = set(ConfiguracionColumna.objects.filter(archivo=obj).values_list('nombre_columna', flat=True))
            nuevas = [ConfiguracionColumna(archivo=obj, nombre_columna=col, visible=True) for col in df.columns if col not in existentes]
            if nuevas:
                ConfiguracionColumna.objects.bulk_create(nuevas, batch_size=1000)
            registros = [Registro(archivo=obj, datos=row.to_dict()) for _, row in df.iterrows()]
            Registro.objects.bulk_create(registros, batch_size=1000)
            if obj.activo:
                ArchivoExcel.objects.exclude(id=obj.id).update(activo=False)
            messages.success(request, 'Excel subido y procesado correctamente.')
        except Exception as e:
            messages.error(request, f'Error procesando Excel: {e}')
        return HttpResponseRedirect(reverse('panel_configurar_columnas', args=[obj.id]))
    return redirect('panel_dashboard')

@login_required
def panel_configurar_columnas(request, archivo_id):
    archivo = get_object_or_404(ArchivoExcel, id=archivo_id)
    columnas = ConfiguracionColumna.objects.filter(archivo=archivo).order_by('nombre_columna')
    if request.method == 'POST':
        ConfiguracionColumna.objects.filter(archivo=archivo).update(es_dni=False, es_fecha_ingreso=False)
        dni_col = request.POST.get('dni_col')
        fecha_col = request.POST.get('fecha_col')
        if dni_col:
            ConfiguracionColumna.objects.filter(archivo=archivo, nombre_columna=dni_col).update(es_dni=True)
        if fecha_col:
            ConfiguracionColumna.objects.filter(archivo=archivo, nombre_columna=fecha_col).update(es_fecha_ingreso=True)
        visibles = request.POST.getlist('visibles')
        for c in columnas:
            c.visible = c.nombre_columna in visibles
            c.save()
        messages.success(request, 'Configuración actualizada.')
        return redirect('panel_dashboard')
    dni_actual = columnas.filter(es_dni=True).values_list('nombre_columna', flat=True).first()
    fecha_actual = columnas.filter(es_fecha_ingreso=True).values_list('nombre_columna', flat=True).first()
    return render(request, 'panel/configurar_columnas.html', {
        'archivo': archivo, 'columnas': columnas, 'dni_actual': dni_actual, 'fecha_actual': fecha_actual,
    })

@login_required
def panel_activar_excel(request, archivo_id):
    archivo = get_object_or_404(ArchivoExcel, id=archivo_id)
    ArchivoExcel.objects.update(activo=False)
    archivo.activo = True
    archivo.save()
    messages.success(request, f'Excel {archivo.id} activado.')
    return redirect('panel_dashboard')

# ---------- NUEVO: formulario de consulta para colaboradores (sin login) ----------
def consulta_form(request):
    """
    Vista simple para colaboradores: ingresa DNI y fecha; consulta directo a DB
    según el Excel ACTIVO y las columnas marcadas como visibles.
    """
    context = {'resultado': None, 'error': None}
    if request.method == 'POST':
        dni = (request.POST.get('dni') or '').strip()
        fecha = (request.POST.get('fecha') or '').strip()
        archivo = _get_activo()
        if not archivo:
            context['error'] = 'No hay un Excel activo para consultar.'
        elif not dni or not fecha:
            context['error'] = 'Ingrese DNI y fecha.'
        else:
            dni_col, fecha_col, visibles = _get_config(archivo)
            if not dni_col or not fecha_col:
                context['error'] = 'Configura las columnas DNI y Fecha de ingreso en el panel.'
            else:
                posibles = Registro.objects.filter(**{f"datos__{dni_col}": dni, 'archivo': archivo})
                fecha_norm = _normalize_fecha(fecha)
                hallado = None
                for reg in posibles:
                    valor_fecha = (reg.datos.get(fecha_col) or '').strip()
                    if valor_fecha == fecha or valor_fecha == fecha_norm:
                        hallado = reg
                        break
                if hallado:
                    context['resultado'] = {col: hallado.datos.get(col) for col in visibles}
                else:
                    context['error'] = 'No encontrado.'
    return render(request, 'panel/consulta_form.html', context)


from django.http import JsonResponse
from .models import Registro

def consulta_api(request):
    dni = request.GET.get('dni')
    fecha = request.GET.get('fecha')

    if not dni or not fecha:
        return JsonResponse({"error": "Debe proporcionar DNI y fecha"}, status=400)

    registros = Registro.objects.filter(dni=dni, fecha_ingreso=fecha)
    data = list(registros.values())


