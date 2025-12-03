
import pandas as pd
from django.contrib import admin, messages
from django.db import transaction
from .models import ArchivoExcel, ConfiguracionColumna, Registro

class ConfiguracionColumnaInline(admin.TabularInline):
    model = ConfiguracionColumna
    extra = 0
    fields = ('nombre_columna', 'visible', 'es_dni', 'es_fecha_ingreso')
    readonly_fields = ('nombre_columna',)

@admin.register(ArchivoExcel)
class ArchivoExcelAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_subida', 'activo')
    list_filter = ('activo',)
    inlines = [ConfiguracionColumnaInline]

    def save_model(self, request, obj, form, change):
        # Al guardar, procesamos el Excel y poblamos columnas + registros
        super().save_model(request, obj, form, change)
        try:
            with transaction.atomic():
                df = pd.read_excel(obj.archivo.path, engine='openpyxl')
                # Convertir todos los valores a string para consistencia
                df = df.astype(str).fillna('')
                # Crear/actualizar configuraciones de columnas
                existing = set(ConfiguracionColumna.objects.filter(archivo=obj).values_list('nombre_columna', flat=True))
                for col in df.columns:
                    if col not in existing:
                        ConfiguracionColumna.objects.create(archivo=obj, nombre_columna=col, visible=True)
                # Limpiar registros previos del mismo archivo y cargar nuevos
                Registro.objects.filter(archivo=obj).delete()
                registros = [Registro(archivo=obj, datos=row.to_dict()) for _, row in df.iterrows()]
                Registro.objects.bulk_create(registros, batch_size=1000)

                # Si este archivo se marca activo, desactivar otros
                if obj.activo:
                    ArchivoExcel.objects.exclude(id=obj.id).update(activo=False)
            messages.success(request, 'Excel procesado correctamente: columnas y registros actualizados.')
        except Exception as e:
            messages.error(request, f'Error procesando Excel: {e}')

@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('id', 'archivo')
    search_fields = ('datos',)
    list_filter = ('archivo',)

@admin.register(ConfiguracionColumna)
class ConfiguracionColumnaAdmin(admin.ModelAdmin):
    list_display = ('archivo', 'nombre_columna', 'visible', 'es_dni', 'es_fecha_ingreso')
    list_filter = ('archivo', 'visible', 'es_dni', 'es_fecha_ingreso')
