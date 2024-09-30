# Desarrollo de API
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer

# Modelos del proyecto
from .models import Cheques, Cheqdet, Chequespagos, Productos, Productosdetalle

# Serializadores del proyecto
from .serializers import ChequeSerializer, CheqdetSerializer, ChequespagosSerializer, ChequeFolioSerializer

# Busqueda en base de datos con un 404 sino existe
from django.shortcuts import get_object_or_404

from django.db.models import Sum # Importamos el módulo Sum de Django

# Create

# Read
## Cheques (folio)
@api_view(['GET'])
def ver_cheques(request, folio):
    try:
        lista_cheques = Cheques.objects.get(folio=folio)
        serializer = ChequeSerializer(lista_cheques)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Cheques.DoesNotExist as e:
        return Response({'error': "No existe el cheque seleccionado"}, status=status.HTTP_404_NOT_FOUND)

## Cheqdet (foliodet)
@api_view(['GET'])
def ver_detalles(request, folio):
    try:
        lista_cheques = Cheqdet.objects.filter(foliodet=folio)
        serializer = CheqdetSerializer(lista_cheques, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Cheqdet.DoesNotExist as e:
        return Response({'error': "No existe el cheque seleccionado"}, status=status.HTTP_404_NOT_FOUND)

## Chequespagos (folio)
@api_view(['GET'])
def ver_pagos(request, folio):
    try:
        lista_cheques = Chequespagos.objects.get(folio=folio)
        serializer = ChequespagosSerializer(lista_cheques, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Chequespagos.DoesNotExist as e:
        return Response({'error': "No existe el cheque seleccionado"}, status=status.HTTP_404_NOT_FOUND)

## Cuentas en enfectivo mayores a 120 (que no tenga monto en tarjeta) que no esten facturadas de un fecha en especifico
@api_view(['GET'])
def cuentas_efectivo(request):
    fecha = request.data['fecha']
    cuentas = Cheques.objects.filter(total__gt=120, tarjeta=0, facturado=False, fecha__date=fecha)
    serializer = ChequeFolioSerializer(cuentas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

## Cuentas que en el total 0
@api_view(['GET'])
def cuentas_total_cero(request):
    cuentas = Cheques.objects.filter(total=0)
    serializer = ChequeFolioSerializer(cuentas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Ver todas las ventas en efectivo que fueron facturadas
@api_view(['GET'])
def cuentas_efectivo_facturadas(request):
    fecha = request.data['fecha']
    cuentas = Cheques.objects.filter(facturado=True, tarjeta=0, fecha__date=fecha)
    serializer = ChequeFolioSerializer(cuentas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Update

# Vamos a actualizar las informacion con el siguiente proceso:
# 1. Obtener la cantidad (cantidad de productos) y el id del producto
# Con base a esta informacion vamos a modificar la informacion de cheqdet
# 2. Eliminar TODOS los movimientos de cheqdet menos el primero.
# 3. Del registro quedate vamos a actualizar : cantidad - idproducto - descuento - precio - impuesto1 - preciosinimpuestos - modificador - usuariodescuento - comentariodescuento - idtipodescuento - idproductocompuesto - productocompuestoprincipal - preciocatalogo
# 4. Seguido a eso actualizamos la tabla de cheques.
# 5. Finalmente actualizamos la tabla de chequespagos

@api_view(['PUT'])
def mantenimiento_cuenta(request, folio):
    cantidad = request.data['cantidad']
    idproducto = request.data['idproducto']
    # Validar que el producto existe
    producto = get_object_or_404(Productos, idproducto=idproducto)
    # Obtener la informacion del producto
    producto_detalle = Productosdetalle.objects.get(idproducto=idproducto)
    
    # Actualizar Cheqdet
    # Eliminar todos los movimientos de cheqdet menos el primero
    primer_movimiento = Cheqdet.objects.filter(foliodet=folio).first().movimiento
    Cheqdet.objects.filter(foliodet=folio).exclude(movimiento=primer_movimiento).delete()
    # Actualizar el primer movimiento
    detalle = Cheqdet.objects.get(foliodet=folio)
    detalle.cantidad = cantidad
    detalle.idproducto = producto
    detalle.descuento = 0
    detalle.precio = producto_detalle.precio
    detalle.impuesto1 = producto_detalle.impuesto1
    detalle.preciosinimpuestos = producto_detalle.preciosinimpuestos
    detalle.modificador = 0
    detalle.usuariodescuento = ""
    detalle.comentariodescuento = ""
    detalle.idtipodescuento = 0
    detalle.idproductocompuesto = 0
    detalle.productocompuestoprincipal = 0
    detalle.preciocatalogo = producto_detalle.precio
    try:
        detalle.save()
        # Cuando se actualiza el detalle, se debe actualizar la tabla de cheques
        venta_general = Cheques.objects.get(folio=folio)
        # El cierre debe ser 3 minutos mas tarde que la fecha de la venta
        venta_general.cierre = venta_general.fecha + timedelta(minutes=3)
        venta_general.mesa = "P/LL"
        venta_general.nopersonas = 1
        venta_general.cambio = 0
        venta_general.descuento = 0
        venta_general.reabiertas = 0
        venta_general.comentariodescuento = ""
        venta_general.usuariodescuento = ""
        venta_general.idtipodescuento = 0
        venta_general.propinapagada = 0
        venta_general.propinafoliomovtocaja = 0
        venta_general.propinaincluida = 0
        venta_general.propinamanual = 0
        venta_general.totalarticulos = cantidad
        venta_general.subtotal = producto_detalle.preciosinimpuestos * cantidad # El total sin impuestos
        venta_general.subtotalsinimpuestos = producto_detalle.preciosinimpuestos * cantidad # El total sin impuestos
        venta_general.total = producto_detalle.precio * cantidad
        venta_general.totalconpropina = venta_general.total
        # El total impuesto 1 es el total de impuestos
        venta_general.totalimpuesto1 = producto_detalle.precio * producto_detalle.impuesto1/100 * 2
        venta_general.cargo = 0
        venta_general.totalconcargo = venta_general.total
        venta_general.totalconpropinacargo = venta_general.total
        venta_general.efectivo = venta_general.total
        venta_general.tarjeta = 0
        venta_general.vales = 0
        venta_general.otros = 0
        venta_general.propina = 0
        venta_general.totalsindescuento = venta_general.total
        venta_general.totalalimentos = 0
        venta_general.totalbebidas = 0
        venta_general.totalotros = venta_general.total
        venta_general.totaldescuentos = 0
        venta_general.totaldescuentoalimentos = 0
        venta_general.totaldescuentobebidas = 0
        venta_general.totaldescuentootros = 0
        venta_general.totalcortesias = 0
        venta_general.totalcortesiaalimentos = 0
        venta_general.totalcortesiabebidas = 0
        venta_general.totalcortesiaotros = 0
        venta_general.totaldescuentoycortesia = 0
        venta_general.totalalimentossindescuentos = 0
        venta_general.totalbebidassindescuentos = 0
        venta_general.totalotrossindescuentos = venta_general.total
        venta_general.descuentocriterio = 0
        venta_general.subtotalcondescuento = venta_general.total
        venta_general.totalimpuestod1 = venta_general.totalimpuesto1
        try:
            #print(f'Esto es lo que se obtuvo de venta general:{venta_general}')
            venta_general.save()
            #print(f'Esto es lo que se sube de venta general:{venta_general}')
            # Actualizar la tabla de chequespagos
            pago = Chequespagos.objects.get(folio=folio)
            pago.importe = venta_general.total
            pago.propina = 0
            try:
                pago.save()
                return Response({
                'Detalles': "http://127.0.0.1:8000/mantenimiento/detalles/" + folio,
                'Cheques': "http://127.0.0.1:8000/mantenimiento/ventas/" + folio,
                'Pagos': "http://127.0.0.1:8000/mantenimiento/pagos/" + folio
            }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': "Error al actualizar el registro en la tabla de chequespagos",
                    "message": str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': "Error al actualizar el registro en la tabla de cheques",
                "message": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': "Error al actualizar el registros en la tabla de cheqdet", "detalle":str(e)}, status=status.HTTP_400_BAD_REQUEST)
# Delete