import requests
import json
import pandas as pd
import numpy as np
import random

# Pedir la fecha al usuario
fecha = input("Fecha de la venta (YYYY-MM-DD): ")
importe = float(input("Efectivo mostrado en reporte: "))
servidor = input("Servidor: ")



api = f"http://{servidor}:8000/florcatorce/"

# Obtener los datos de la venta
response = requests.post(f'{api}ventas', json={"fecha": fecha})

# Convertir la respuesta a un DataFrame
df = pd.DataFrame(response.json())
df["efectivo"] = df["efectivo"].astype(float)
df["tarjeta"] = df["tarjeta"].astype(float)
df["total"] = df["total"].astype(float)

# Obtener los folios a hacer mantenimiento
df_folios = df[
    (df["efectivo"] >= 120) & (df["tarjeta"] == 0) & (df["facturado"] == False)
]

# Reporte inicial
df.to_csv(f'ventas_{fecha}.csv', index=False)
df_folios.to_csv(f'folios_{fecha}.csv', index=False)

# Hacer el mantenimiento
productos = {
    "cafe_en_grano": "034003",
    "pan_para_llevar": "042035"
}

folios = df_folios["folio"].tolist()
random.shuffle(folios)

suma_efectivo = 0
monto_final = 6000

for folio in folios:
    # Obtener el $ del folio
    efectivo_folio = df[df["folio"] == folio]["total"].values[0]
    suma_efectivo += efectivo_folio
    
    # Escoger un producto aleatorio
    producto = random.choice(list(productos.keys()))
    producto_id = productos[producto]
    
    if producto_id == "034003":
        suma_efectivo -= 80
    elif producto_id == "042035":
        suma_efectivo -= 40
    
    ajuste = importe - suma_efectivo
    
    # Si el ajuste es mayor o igual a monto_final, se hace el mantenimiento
    if ajuste >= monto_final:
        print(f"Haciendo mantenimiento del folio {folio}")
        mant = requests.patch(f"{api}mantenimiento/{folio}", json={"cantidad_articulos": 1, "producto": producto_id})
    
    # Si el ajuste es igual o ligeramente mayor a 6000, salir del bucle
    if ajuste <= monto_final:
        print("Se llego al limite de ajuste")
        break

print(f"Se ha hecho un mantenimiento con un total de {suma_efectivo} y un ajuste de {ajuste}")
