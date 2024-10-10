from datetime import datetime, timedelta
from django.shortcuts import render

import random
import requests as req

# Create your views here.

def nexi_bot(request):
    if request.method == 'GET':
        return render(request, 'BotHome.html')
    else:
        # Obtener datos del formulario
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_final']
        servidor = request.POST['servidor']

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
            # Obtener un producto
            prod_aleatorio = random.choice(list(productos.keys()))
            prod_seleccionado = productos[prod_aleatorio]
            precio_prod_seleccionado = prod_seleccionado['precio']
            id_prod_seleccionado = prod_seleccionado['id']

            # Obtener las ventas
            ventas = req.get(f'{api}ventas', json={'fecha': fecha})
            if ventas.status_code == 200:
                ventas = ventas.json()
                print(f'Ventas del {fecha}: {ventas}')
            else:
                print(f'Error al obtener las ventas del {fecha}')

        return render(request, 'BotHome.html')









