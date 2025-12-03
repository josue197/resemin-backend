
from django.db import models

class ArchivoExcel(models.Model):
    archivo = models.FileField(upload_to='excels/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True, help_text='Marca este Excel como el activo para consultas.')

    class Meta:
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"Excel {self.id} - {self.fecha_subida:%Y-%m-%d %H:%M}"

class ConfiguracionColumna(models.Model):
    archivo = models.ForeignKey(ArchivoExcel, on_delete=models.CASCADE, related_name='columnas')
    nombre_columna = models.CharField(max_length=150)
    visible = models.BooleanField(default=True)
    es_dni = models.BooleanField(default=False)
    es_fecha_ingreso = models.BooleanField(default=False)

    class Meta:
        unique_together = ('archivo', 'nombre_columna')
        ordering = ['nombre_columna']

    def __str__(self):
        flags = []
        if self.visible: flags.append('visible')
        if self.es_dni: flags.append('dni')
        if self.es_fecha_ingreso: flags.append('fecha')
        return f"{self.nombre_columna} ({', '.join(flags)})"

class Registro(models.Model):
    archivo = models.ForeignKey(ArchivoExcel, on_delete=models.CASCADE, related_name='registros')
    datos = models.JSONField()

    def __str__(self):
        return f"Registro {self.id} del archivo {self.archivo_id}"
