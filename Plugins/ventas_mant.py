import requests as req

import pandas as pd

servidores = {
    "animas": "26.217.212.35",
    "centro":"26.61.16.123",
    "desarrollo": "127.0.0.1"
}

fecha_inicio = "2024-10-01"
fecha_fin = "2024-10-31"

fechas = pd.date_range(fecha_inicio, fecha_fin, freq='D')
fechas = [fecha.strftime('%Y-%m-%d') for fecha in fechas]


api = f'http://{servidores["desarrollo"]}:8000/florcatorce/mantenimiento'


# Plantilla de DF Reporte Contabilidad
df_bi = pd.DataFrame(columns=["fecha", "producto", "piezas", "monto", "total"])

for fecha in fechas:
    endpoint = f'{api}/tasa_cero/'

    # Peticion a la API
    response = req.post(endpoint, json={"fecha": fecha}) #Esperado: 6240
    data = response.json()

    kilos_cafe = 0
    piezas_pan = 0

    monto_cafe = 0
    monto_pan = 0

    # Recorrer las ventas
    for venta in data:
        if float(venta["precio"]) == 80:
            kilos_cafe += 1
            monto_cafe += 80
        elif float(venta["precio"]) == 40:
            piezas_pan += 1
            monto_pan += 40
        else:
            kilos_cafe += 1
            monto_cafe += float(venta["precio"])
            
    # Recopoilar datos
    df_repo = pd.DataFrame([
        {"fecha": fecha, "producto": "Kilos de Cafe", "piezas": kilos_cafe, "monto": monto_cafe, "total": monto_cafe + monto_pan},
        {"fecha": fecha, "producto": "Pan para llevar", "piezas": piezas_pan, "monto": monto_pan}
    ])
    
    # Concatenar los DataFrames
    df_bi = pd.concat([df_bi, df_repo], ignore_index=True)

# Cambiar el tipo de dato del df
df_bi["fecha"] = pd.to_datetime(df_bi["fecha"])
df_bi["producto"] = df_bi["producto"].astype(str)
df_bi["piezas"] = df_bi["piezas"].astype(float)
df_bi["monto"] = df_bi["monto"].astype(float)
df_bi["total"] = df_bi["total"].astype(float)

# Archivo CSV
df_bi.to_csv(f'ventas_octubre-{fecha_inicio}-{fecha_fin}_centro.csv', index=False)
