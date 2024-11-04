import requests as req

import pandas as pd

servidores = {
    "araucarias": "26.217.212.35",
    "centro": "26.61.16.123",
}

fecha = "2024-10-01"

endpoint = f'http://{servidores["araucarias"]}:8000/florcatorce/mantenimiento/aplicado'

response = req.get(endpoint, json={"fecha": fecha})

data = response.json()

# Guardar las ventas en un archivo CSV
df = pd.DataFrame(data)
df.to_csv(f'ventas_{fecha}.csv', index=False)