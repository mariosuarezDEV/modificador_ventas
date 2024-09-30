import requests
import random

# Pedir la fecha por consola:
fecha_consola = input("Ingresa la fecha (YYYY-MM-DD): ")

fecha ={
    "fecha": fecha_consola
}

# Obtener los folios
endpoint_fecha = "http://127.0.0.1:8000/mantenimiento/cuentas/efectivo/facturado"

folios_response = requests.get(endpoint_fecha, json=fecha)
# respusta ejemplo: [{"folio": 3328,"total": "248.0000"},{"folio": 3330,"total": "253.0000"}]

# Crear una lista de folios
folios = [folio["folio"] for folio in folios_response.json()]

# Suma de los totales de los folios
total = sum([float(folio["total"]) for folio in folios_response.json()])
print(f'El total facturado en efectivo de la fecha {fecha_consola} es: {total}')