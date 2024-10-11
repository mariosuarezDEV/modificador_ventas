from datetime import datetime, timedelta
from time import strptime

from django.shortcuts import render

import random
import requests as req

import pandas as pd
import numpy as np

# Create your views here.

def nexi_bot(request):
    if request.method == 'GET':
        return render(request, 'BotHome.html')
    else:
        # Se hizo una petición POST
        consola = [] # Mostar mensajes en la consola
        analisis = [] # Mostrar datos de análisis

        # Obtener la fecha inicial
        fecha_inicial = request.POST.get('fecha_inicial')
        # Obtener la fecha final
        fecha_final = request.POST.get('fecha_final')
        # Obtener el servidor
        servidor = request.POST.get('servidor')

        # Validar que las fechas sean correctas
        if fecha_inicial == '' or fecha_final == '':
            consola.append('Por favor, ingrese las fechas')
            return render(request, 'BotHome.html', {'registros': consola})
        if servidor == '':
            consola.append('Por favor, seleccione un servidor')
            return render(request, 'BotHome.html', {'registros': consola})

        # Definir servidores
        servidores = {
            'centro' : '26.61.16.123',
            'araucarias': '26.217.212.35',
            'pruebas': '26.144.145.93'
        }
        # API:
        api = f'http://{servidores[servidor]}:8000/florcatorce/mantenimiento'

        # Definir productos
        productos = {
            'Pan para llevar' :{
                'id': '042035',
                'precio': 40
            },
            'Cafe 1/4': {
                'id': '034003',
                'precio': 80
            }
        }

        # Obtener las fechas a las que se les realizará el mantenimiento
        fecha_inicio = datetime.strptime(fecha_inicial, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_final, '%Y-%m-%d')
        # Rango de fechas
        rango = fecha_fin - fecha_inicio
        fechas = [fecha_inicio + timedelta(days=i) for i in range(rango.days + 1)]

        for fecha in fechas:
            # Realizar una peticion para obtener las ventas
            ventas = req.get(f'{api}/ventas', json={'fecha': fecha.strftime('%Y-%m-%d')})
            if ventas.status_code != 200:
                return render(request, 'BotHome.html', {'error': 'Error al obtener las ventas. Consulta los detalles en la consola del servidor'})

            consola.append(f'La API respondio con un status code {ventas.status_code} para obtener las ventas del {fecha.strftime("%Y-%m-%d")}')
            ventas = ventas.json()
            # Crear un DataFrame con las ventas
            df_ventas = pd.DataFrame(ventas)
            # Convertir los tipos de datos
            df_ventas['efectivo'] = df_ventas['efectivo'].astype(float)
            df_ventas['tarjeta'] = df_ventas['tarjeta'].astype(float)
            df_ventas['total'] = df_ventas['total'].astype(float)

            # Filtrar las ventas para el mantenimiento
            # Efectivo >= 120 & Tarjeta == 0 & facturado == False

            df = df_ventas[(df_ventas['efectivo'] >= 120) & (df_ventas['tarjeta'] == 0) & (df_ventas['facturado'] == False)]
            consola.append(f'El bot filtró {np.size(df)} ventas para el mantenimiento del {fecha.strftime("%Y-%m-%d")}')
            # Crear un array de folios
            folios_filtrados = np.array(df['folio'])
            folios_ventas = np.array(df_ventas['folio'])

            # Crear un array de efectivos
            efectivos_filtrados = np.array(df['efectivo'])
            efectivo_ventas = np.array(df_ventas['efectivo'])

            # Mezclar los folios
            np.random.shuffle(folios_filtrados)
            suma_efectivos_filtrados = 0
            folios_afectados = np.array([])
            for folio in folios_filtrados:
                # Configurar informacion del producto
                producto = random.choice(list(productos.keys()))
                id_producto = productos[producto]['id']
                precio = productos[producto]['precio']

                # Obtener el efectivo del folio
                efectivo = df_ventas.loc[df_ventas['folio'] == folio, 'efectivo'].values[0]

                # Realizar una peticion para ajustar la venta
                ajuste = req.patch(f'{api}/{folio}', json={
                    'producto': id_producto,
                    'cantidad': 1,
                })
                if ajuste.status_code != 200:
                    consola.append(f'Error al ajustar la venta {folio}. Consulta los detalles en la consola del servidor')
                    # Si el error persiste, no detener la ejecución
                    continue
                else:
                    suma_efectivos_filtrados += efectivo - precio
                    folios_afectados = np.append(folios_afectados, folio)

                # Decidir si hacer otro recorrido o no
                delimitador = np.sum(efectivo_ventas) - suma_efectivos_filtrados

                if 6000 < delimitador < 7000:
                    # Elaborar reporte data science
                    fecha_registro = fecha.strftime('%Y-%m-%d')
                    total_folios_ventas = np.size(folios_ventas)
                    total_folios_filtrados = np.size(folios_filtrados)
                    total_efectivo_ventas = round(np.sum(efectivo_ventas), 2)
                    total_efectivo_filtrados = round(np.sum(efectivos_filtrados), 2)
                    efectivo_final = delimitador
                    total_folios_afectados = np.size(folios_afectados)

                    analisis.append({
                        'fecha': fecha_registro,
                        'total_folios_ventas': total_folios_ventas,
                        'total_folios_filtrados': total_folios_filtrados,
                        'total_efectivo_ventas': total_efectivo_ventas,
                        'total_efectivo_filtrados': total_efectivo_filtrados,
                        'efectivo_final': efectivo_final,
                        'total_folios_afectados': total_folios_afectados
                    })
                    consola.append('El bot ha concluido el mantenimiento de ventas y ha generado un reporte, descargalo en el servidor')
                    break
        # Retornar la consola de mensajes
        return render(request, 'BotHome.html', {
            'registros': consola,
            'data_science': analisis
        })