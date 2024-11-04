import requests as req

import pandas as pd

servidores = {
    "araucarias": "26.217.212.35",
    "centro": "26.61.16.123",
}

fecha = "2024-10-31"

endpoint = f'http://{servidores["centro"]}:8000/florcatorce/mantenimiento/aplicado'

# Dataframe plantilla fecha - producto - cantidad - monto
df = pd.DataFrame(columns=["fecha", "producto", "cantidad", "monto"])

response = req.get(endpoint, json={"fecha": fecha})

data = response.json()

cant_cafe = 0
cant_pan = 0

monto_cafe = 0
monto_pan = 0

# Recorrer las ventas
for venta in data:
    print(venta["total"])
    if float(venta["total"]) == 80:
        cant_cafe += 0.25
        monto_cafe += 80
        print(f"Venta de café 1/4 en la fecha {fecha}")
    elif float(venta["total"]) == 40:
        cant_pan += 1
        monto_pan += 40
        print(f"Venta de pan para llevar en la fecha {fecha}")

# Crear un nuevo DataFrame con los resultados
nuevo_df = pd.DataFrame([
    {"fecha": fecha, "producto": "Café 1/4", "cantidad": cant_cafe, "monto": monto_cafe},
    {"fecha": fecha, "producto": "Pan para llevar", "cantidad": cant_pan, "monto": monto_pan}
])

# Concatenar los DataFrames
df = pd.concat([df, nuevo_df], ignore_index=True)

# Archivo CSV
df.to_csv(f'ventas_{fecha}.csv', index=False)

print(df)