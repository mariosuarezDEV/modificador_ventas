from datetime import datetime, timedelta
from django.shortcuts import render

import random
import requests as req

import pandas as pd
import numpy as np
from numpy.testing.print_coercion_tables import print_new_cast_table


# Create your views here.

def nexi_bot(request):
    if request.method == 'GET':
        return render(request, 'BotHome.html')
    else:
        # Obtener datos del formulario
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_final']
        servidor = request.POST['servidor']
        limite = 6000

        # Si no se ingresó una fecha de inicio
        if fecha_inicio == '':
            error_fecha_invalida = "Debe ingresar una fecha de inicio"
            return render(request, 'BotHome.html', {'error': error_fecha_invalida})

        # Validar que la fecha de inicio sea menor a la fecha final
        if fecha_inicio > fecha_fin:
            error_fecha_invalida = "El formato de las fechas es incorrecto"
            return render(request, 'BotHome.html', {'error': error_fecha_invalida})

        # Si no se seleccionó un servidor
        if servidor == '':
            error_servidor_invalido = "Debe seleccionar un servidor"
            return render(request, 'BotHome.html', {'error': error_servidor_invalido})

        # Reliazar el proceso de mantenimiento de ventas

        # Obtener las fechas a las que se les realizará el mantenimiento
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        # Rango de fechas
        rango = fecha_fin - fecha_inicio
        fechas = [fecha_inicio + timedelta(days=i) for i in range(rango.days + 1)]

        # Definir lista de productos
        productos = {
            'cafe_cuarto' : {
                'id': '034003',
                'precio': 80
            },
            'pan_para_llevar' :{
                'id': '042035',
                'precio': 40
            },
        }
        # Definir API
        servidores = {
            'centro': '26.61.16.123',
            'araucarias': '26.217.212.35',
            'pruebas' : '26.144.145.93'
        }
        api = f'http://{servidores[servidor]}:8000/florcatorce/mantenimiento/'

        # Recorrer las fechas
        for fecha in fechas:
            # Formatear fecha
            fecha = fecha.strftime('%Y-%m-%d')
            ventas = req.get(f'{api}ventas', json={'fecha': fecha})

            # Si no se pudo obtener las ventas
            if ventas.status_code != 200:
                return render(request, 'BotHome.html', {'error': 'Hubo un error por parte del servidor.\nIntente más tarde'})

            ventas = ventas.json() # Creamos el diccionario de ventas

            # Crear dataframe
            df = pd.DataFrame(ventas)

            # Cambiar el tipo de dato
            df['efectivo'] = df['efectivo'].astype(float)
            df['tarjeta'] = df['tarjeta'].astype(float)
            df['total'] = df['total'].astype(float)

            # Obtener el total de efectivos
            total_efectivo = np.sum(df['efectivo'])
            print(f'Total de efectivo: {total_efectivo} de la fecha {fecha}')

            # Guardar las ventas
            df.to_csv(f'ventas_{fecha}.csv', index=False)

            # Ventas aptas para mantenimiento
            df_folios = df[
                (df['efectivo'] >= 120) & (df['tarjeta'] == 0) & (df['facturado'] == False)
            ]

            # Guardar las ventas aptas
            df_folios.to_csv(f'ventas_aptas_{fecha}.csv', index=False)

            # Guardar los folios
            folios_array = np.array(df_folios['folio'])
            # Folios totales
            folios_totales = np.size(folios_array)
            # Efectivo total
            efectivo_total = np.sum(df_folios['efectivo'])

            print(f'Folios totales: {folios_totales} de la fecha {fecha}')
            print(f'Efectivo total: {efectivo_total} de la fecha {fecha}')

            # Mezclar los folios
            np.random.shuffle(folios_array)

            # Recorrer los folios
            suma_efectivo_folios_por_fecha = 0
            for folio in folios_array:
                # Obtener el efectivo del folio actual
                efectivo_folio = df_folios[df_folios['folio'] == folio]['efectivo'].values[0]

                suma_efectivo_folios_por_fecha += efectivo_folio # Se agrega el efectivo a la cuenta global

                # Obtener un producto
                prod_aleatorio = random.choice(list(productos.keys()))
                prod_seleccionado = productos[prod_aleatorio]
                precio_prod_seleccionado = prod_seleccionado['precio']
                id_prod_seleccionado = prod_seleccionado['id']

                suma_efectivo_folios_por_fecha -= precio_prod_seleccionado # Se resta el precio del producto al efectivo

                bandera = total_efectivo - suma_efectivo_folios_por_fecha # 17000 - 2000 = 15000

                # Saber si la bandera esta en el rango de limite (6000)
                if limite <= bandera <= 6700:
                    print(f'Se llego al limite de {limite} de la fecha {fecha} con la bandera {bandera}')
                    print('\n')
                    break

                # Aplicar mantenimiento

        return render(request, 'BotHome.html')