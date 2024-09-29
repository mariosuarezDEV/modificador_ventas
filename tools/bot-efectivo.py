import requests
import random

# Obtener los folios
endpoint_fecha = "http://127.0.0.01:8000/mantenimiento/cuentas/efectivo"
fecha ={
    "fecha": "2024-08-28"
}
folios_response = requests.get(endpoint_fecha, json=fecha)
# respusta ejemplo: [{"folio": 3328,"total": "248.0000"},{"folio": 3330,"total": "253.0000"}]

# Crear una lista de folios
folios = [folio["folio"] for folio in folios_response.json()]
# Ver folios:
#print(folios)

# Suma de los totales de los folios
total = sum([float(folio["total"]) for folio in folios_response.json()])
efectivo_inicial = 16282
# Obtener el 50% del efectivo inicial
efectivo_final = efectivo_inicial / 2
# Ver total:
#print(total)

# Lista de productos:
productos = ["034003", "042035"]
# 034003 = Cafe en grano -> $80
# 042035 = Pan -> $40

# Hacer que el bot escoja un producto al azar de la lista de productos y lo asigne a la variable idproducto.
folios_actualizados = 0
mantenimiento = 0
folios_random = folios.copy()
random.shuffle(folios_random)
for folio in folios_random:
    datos ={
        "cantidad": 1,
        "idproducto": random.choice(productos)
    }
    endpoint = f"http://127.0.0.1:8000/mantenimiento/actualizar/{folio}/"
    response = requests.put(endpoint, json=datos)
    if response.status_code == 200:
        folios_actualizados += 1
        mantenimiento += float(folios_response.json()[folios.index(folio)]["total"])
        if datos["idproducto"] == "034003":
            print(f"Se actualizó el folio {folio} por café en grano")
            mantenimiento -= 80
        elif datos["idproducto"] == "042035":
            print(f"Se actualizó el folio {folio} por pan")
            mantenimiento -= 40
        if mantenimiento >= efectivo_final:
            print(f"Se llegó al 50% del efectivo inicial")
            break
    else:
        print(f"Error al actualizar el folio {folio}")

print(f"Se actualizaron {folios_actualizados} folios")

# Por cada folio en la lista de folios, se debe hacer una petición PUT a la URL: http://192.168.193.250:8080/mantenimiento/actualizar/{folio}/