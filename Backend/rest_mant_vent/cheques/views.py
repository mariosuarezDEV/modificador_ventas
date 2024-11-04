from datetime import timedelta

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

# Modelos
from .models import Cheques, Cheqdet, Productos, Chequespagos, Productosdetalle

# Serializadores
from .serializers import ChequesSerializer, CheqdetSerializer, ChequespagosSerializer, ChequeFolioSerializer

# Vistas / Metodos

# Obtener todas las ventas
@api_view(['GET'])
def ventas_view(request):
    # Obtener la fecha el cliente
    fecha = request.data.get("fecha")
    if fecha:
        ventas = Cheques.objects.filter(fecha__date=fecha)
        # Serializar ventas
        serializer = ChequeFolioSerializer(ventas, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    else:
        # No se pueden obtener ventas sin fecha
        return Response({
            "Error": "Es necesario enviar una fecha"
        }, status.HTTP_400_BAD_REQUEST)

# Obtener ventas con mantenimiento
@api_view(['GET'])
def ventas_mantenido_view(request):
    # Obtener la fecha el cliente
    fecha = request.data.get("fecha")
    if fecha:
        ventas = Cheques.objects.filter(fecha__date=fecha, mesa__exact="P/LL")
        # Serializar ventas
        serializer = ChequesSerializer(ventas, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    else:
        # No se pueden obtener ventas sin fecha
        return Response({
            "Error": "Es necesario enviar una fecha"
        }, status.HTTP_400_BAD_REQUEST)

# Ver informacion de un folio
@api_view(['GET'])
def folio_view(request, folio):
    # Obtener cheque del folio
    cheque = get_object_or_404(Cheques, folio=folio)
    # Obtener detalles del folio
    detalles = Cheqdet.objects.filter(foliodet=folio)
    # Obtener pagos del folio
    pago = get_object_or_404(Chequespagos, folio=folio)

    # Serializar los queryset
    cheque_serializer = ChequesSerializer(cheque)
    detalles_serializer = CheqdetSerializer(detalles, many=True)
    pago_serializer = ChequespagosSerializer(pago)

    return Response({
        "Cheque": cheque_serializer.data,
        "Detalles": detalles_serializer.data,
        "Pago": pago_serializer.data
    }, status.HTTP_200_OK)

# Mantenimiento de un folio
@api_view(['PATCH'])
def actualizar_venta(request, folio):
    # Datos recibidor del frontend
    producto_id = request.data.get("producto")
    cantidad = request.data.get("cantidad")

    if not producto_id or not cantidad:
        return Response({
            "Error": "Es necesario enviar el producto y la cantidad"
        }, status.HTTP_400_BAD_REQUEST)

    # Obtener el producto
    detalle_producto = get_object_or_404(Productosdetalle, idproducto=producto_id)

    # Actualizar la venta
    venta = get_object_or_404(Cheques, folio=folio)
    try:
        venta.cierre = venta.fecha + timedelta(minutes=3)
        venta.mesa = "P/LL"
        venta.nopersonas = 1
        venta.cambio = 0
        venta.descuento = 0
        venta.cambiorepartidor = 0
        venta.usuariodescuento = ""
        venta.idtipodescuento = 0
        venta.propinapagada = 0
        venta.propinafoliomovtocaja = 0
        venta.propinaincluida = 0
        venta.propinamanual = 0
        venta.totalarticulos = cantidad
        venta.subtotal = detalle_producto.preciosinimpuestos * cantidad
        venta.subtotalsinimpuestos = detalle_producto.preciosinimpuestos * cantidad
        venta.total = detalle_producto.precio * cantidad
        venta.totalconpropina = venta.total
        venta.totalimpuesto1 = detalle_producto.precio * cantidad
        venta.cargo = 0
        venta.totalconcargo = venta.total
        venta.totalconpropinacargo = venta.total
        venta.descuentoimporte = 0
        venta.efectivo = venta.total
        venta.tarjeta = 0
        venta.vales = 0
        venta.otros = 0
        venta.propina = 0
        venta.propinatarjeta = 0
        venta.totalsindescuento = venta.total
        venta.totalalimentos = 0
        venta.totalbebidas = 0
        venta.totalotros = venta.total
        venta.totaldescuentos = 0
        venta.totaldescuentoalimentos = 0
        venta.totaldescuentobebidas = 0
        venta.totaldescuentootros = 0
        venta.totalcortesias = 0
        venta.totalcortesiaalimentos = 0
        venta.totalcortesiabebidas = 0
        venta.totalcortesiaotros = 0
        venta.totaldescuentoycortesia = 0
        venta.totalalimentossindescuentos = 0
        venta.totalbebidassindescuentos = 0
        venta.totalotrossindescuentos = venta.total
        venta.descuentocriterio = 0
        venta.subtotalcondescuento = venta.subtotal
        venta.totalimpuestod1 = venta.totalimpuesto1
        venta.totalsindescuentoimp = venta.total
        venta.save()
    except Exception as e:
        print("Error al actualizar la tabla cheques", str(e))

    # Eliminar los movimientos de los detalles
    Cheqdet.objects.exclude(movimiento=1).filter(foliodet=folio).delete()
    # Actualizar los movimientos de los detalles
    detalle = get_object_or_404(Cheqdet, foliodet=folio)
    try:
        detalle.cantidad = cantidad
        detalle.idproducto = Productos.objects.get(idproducto=producto_id)
        detalle.descuento = 0
        detalle.precio = detalle_producto.precio
        detalle.impuesto1 = detalle_producto.impuesto1
        detalle.preciosinimpuestos = detalle_producto.preciosinimpuestos
        detalle.comentario = ""
        detalle.usuariodescuento = ""
        detalle.comentariodescuento = ""
        detalle.idtipodescuento = 0
        detalle.idproductocompuesto = ""
        detalle.productocompuestoprincipal = False
        detalle.preciocatalogo = detalle_producto.precio
        detalle.idcortesia = ""
        detalle.save()
    except Exception as e:
        print("Error al actualizar la tabla cheqdet", str(e))

    # Actualizar los pagos
    pagos = get_object_or_404(Chequespagos, folio=folio)
    try:
        pagos.importe = venta.total
        pagos.propina = 0
        pagos.tipodecambio = 0
        pagos.save()
    except Exception as e:
        print("Error al actualizar la tabla chequespagos", str(e))

    # Obtener los datos actualizados
    nueva_venta = get_object_or_404(Cheques, folio=folio)
    nuevo_detalle = get_object_or_404(Cheqdet, foliodet=folio)
    nuevo_pago = get_object_or_404(Chequespagos, folio=folio)

    # Serializar los datos
    serializer = ChequesSerializer(nueva_venta)
    serializer_detalle = CheqdetSerializer(nuevo_detalle)
    serializer_pago = ChequespagosSerializer(nuevo_pago)

    # Retornar los datos
    return Response({
        "datos actualizados": {
            "venta": serializer.data,
            "detalle": serializer_detalle.data,
            "pago": serializer_pago.data
        }
    }, status=status.HTTP_200_OK)

# Reporte: Folios con 