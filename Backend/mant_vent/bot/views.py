from django.shortcuts import render
from datetime import datetime, timedelta
import requests as req
import pandas as pd
import numpy as np
import random
import os
import locale

# Create your views here.

def nexium_bot(request):
    # Definir servidores
    servidores = {
        "araucarias": "26.45.221.222",
        "centro": "26.61.16.123",
        "beta": "26.144.145.93",
        "desarrollo": "127.0.0.1"
    }

    # Productos
    productos = {
        "Cafe 1/4": {
            "id": "034003",
            "precio": 80
        },
        "Pan para llevar": {
            "id": "042035",
            "precio": 40
        }
    }
    # V007021 <- Extra shot de cafe

    # Version del Bot
    version = "1.2.11"

    # Establecer el locale
    locale.setlocale(locale.LC_TIME, 'spanish')

    if request.method == "GET":

        return render(request, "NexiBot.html", {"version": version, "animate": True})
    elif request.method == "POST":

        # Obtener el mes en el que estamos
        mes = datetime.now().strftime("%B")

        # Obtener las fechas
        fecha_inicio = request.POST.get("fecha_inicial")
        fecha_fin = request.POST.get("fecha_final")
        servidor = request.POST.get("servidor")

        # Validar que tenemos una fecha inicial en la petición
        if fecha_inicio == "":
            return render(request, "NexiBot.html", {"error": "No se proporcionó una fecha inicial", "version": version})
        if fecha_fin == "":
            return render(request, "NexiBot.html", {"error": "No se proporcionó una fecha final", "version": version})
        if servidor == "":
            return render(request, "NexiBot.html",
                          {"error": "El servidor es necesario para consumir la API REST", "version": version})

        # Crear un directorio para el mes en caso de que no exista
        if not os.path.exists(f'reportes/{mes}/{servidor}'):
            os.makedirs(f'reportes/{mes}/{servidor}')
            # Crear la plantilla del csv
            df_plantilla = pd.DataFrame({
                "Fecha": [],
                "Efectivo Inicial": [],
                "Efectivo Final": []
            })
            df_plantilla.to_csv(f'reportes/{mes}/{servidor}/reporte.csv', index=False)

        # Abrir un reporte csv ya guardado
        df_reporte = pd.read_csv(f'reportes/{mes}/{servidor}/reporte.csv')

        # Obtener el rango de fechas desde inicio a fin
        rango_fechas = []
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        delta = fecha_fin - fecha_inicio
        for i in range(delta.days + 1):
            temp = fecha_inicio + timedelta(days=i)
            temp = temp.strftime("%Y-%m-%d")
            rango_fechas.append(temp)

        # Establecer conexión con la API del servidor
        api = f'http://{servidores[servidor]}:8000/florcatorce/mantenimiento'

        # Obtener las ventas de X fecha
        for fecha in rango_fechas:
            # La informacion que regresa el endpoint son las ventas que se realizaron en la fecha que se le proporciona
            ventas = req.get(f'{api}/ventas', json={
                "fecha": fecha
            })

            # Crear un df de las ventas
            if ventas.status_code != 200:
                return render(request, "NexiBot.html",
                              {"error": f'La peteción a la API regreso un código de estado diferente a 200',
                               "version": version})

            # En este DF estan todas las ventas de la fecha
            df = pd.DataFrame(ventas.json())
            # Cambiar el tipo de datos de las columnas
            df["efectivo"] = df["efectivo"].astype(float)
            df["tarjeta"] = df["tarjeta"].astype(float)
            df["total"] = df["total"].astype(float)

            # Efectivo original del día
            total_efectivo = df["efectivo"].sum()

            # Filtrar las ventas para el mantenimiento

            # Filtro: efectivo >= 120 && tarjeta == 0 && facturado == False (Cuentas que aptas para el ajuste)
            df_ajuste = df[(df["efectivo"] >= 120) & (df["tarjeta"] == 0) & (df["facturado"] == False)]

            # Crear un array de folios para recorrerlos
            folios_df = np.array(df_ajuste["folio"])
            # Mezclar folios
            np.random.shuffle(folios_df)

            # Control del efectivo que se a modificado
            sum_efectivos = 0
            for folio in folios_df:
                # Efectivo que tiene la venta
                efectivo_folio = df.loc[df['folio'] == folio, 'efectivo'].values[
                    0]  # df_ventas.loc[df_ventas['folio'] == folio, 'efectivo'].values[0]

                #print(f'Folio: {folio} Efectivo: {efectivo_folio}')
                # Escoger un producto
                producto = random.choice(list(productos.keys()))
                producto_id = productos[producto]["id"]
                precio = productos[producto]["precio"]

                # Hacer petición a la api
                response = req.patch(f'{api}/{folio}', json={
                    "producto": producto_id,
                    "cantidad": 1
                })
                if response.status_code == 200:
                    sum_efectivos += efectivo_folio - precio

                    delimitador = total_efectivo - sum_efectivos
                    # Poner el delimitador con 1 decimal
                    delimitador = round(delimitador, 1)

                    if 6000 < delimitador < 7020:
                        #print(f'El efectivo inicial de la fecha {fecha} es de {total_efectivo} y termino con un efectivo de {delimitador}')
                        # Agregar los datos al DataFrame
                        mantenimiento = pd.DataFrame({
                            "Fecha": [fecha],
                            "Efectivo Inicial": [total_efectivo],
                            "Efectivo Final": [delimitador]
                        })
                        # Agregar el registro al mantenimiento
                        df_reporte = pd.concat([df_reporte, mantenimiento], ignore_index=True)
                        break
        # Guardar el reporte con los registros agregaddos
        df_reporte.to_csv(f'reportes/{mes}/{servidor}/reporte.csv', index=False)

        # Obtener del df_reporte los registros que se agregaron
        df_reporte = df_reporte.tail(len(rango_fechas))

        # Cambiar los nombres de las claves en el DataFrame
        df_reporte = df_reporte.rename(
            columns={'Efectivo Inicial': 'Efectivo_Inicial', 'Efectivo Final': 'Efectivo_Final'})

        reporte_data = df_reporte.to_dict(orient='records')

        return render(request, "NexiBot.html", {
            "version": version,
            "bien": f'Se ha enviado un reporte de los datos del servidor en {servidor} a tu correo',
            "reportes": reporte_data
        })