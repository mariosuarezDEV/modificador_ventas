from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Cheques, Cheqdet, Productos, Chequespagos, Productosdetalle
from .serializers import ChequesSerializer, CheqdetSerializer, ChequespagosSerializer, ChequeFolioSerializer

@api_view(['POST']) # Obtener la ventas para mantenimiento
def obtener_ventas(request):
    fecha = request.data["fecha"]
    ventas = Cheques.objects.filter(fecha__date=fecha)
    serializer = ChequeFolioSerializer(ventas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PATCH']) # Actualizar una venta
def actualizar_venta(request, folio):
    """
    Este endpoint recibe un folio el cual será afectado para actualizar datos de la tabla de cheques, cheqdet y chequespagos.
    """
    # Datos recibidor del frontend
    articulos = request.data["cantidad_articulos"]
    producto_id = request.data["producto"]

    # Obtener el producto
    detalle_producto = get_object_or_404(Productosdetalle, idproducto=producto_id)

    # Actualizar la venta
    venta = get_object_or_404(Cheques, folio=folio)    
    try:
        venta.cierre = venta.fecha + timedelta(minutes=3)
        venta.mesa= "P/LL"
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
        venta.totalarticulos = articulos
        venta.subtotal = detalle_producto.preciosinimpuestos * articulos
        venta.subtotalsinimpuestos = detalle_producto.preciosinimpuestos * articulos
        venta.total = detalle_producto.precio * articulos
        venta.totalconpropina = venta.total
        venta.totalimpuesto1 = detalle_producto.precio * articulos
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
        venta.save()
    except Exception as e:
        return Response({"Error al actualizar las ventas": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Eliminar los movimientos de los detalles
    Cheqdet.objects.exclude(movimiento=1).filter(foliodet=folio).delete()
    # Actualizar los movimientos de los detalles
    detalle = get_object_or_404(Cheqdet, foliodet=folio)  
    try:      
        detalle.cantidad = articulos
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
        return Response({"Error al actualizar los detalles de las ventas": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar los pagos
    pagos = get_object_or_404(Chequespagos, folio=folio)
    try:
        pagos.importe = venta.total
        pagos.propina = 0
        pagos.tipodecambio = 0
        pagos.save()
    except Exception as e:
        return Response({"Error al actualizar los pagos de las ventas": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
        "datos actualizados":{
            "venta": serializer.data,
            "detalle": serializer_detalle.data,
            "pago": serializer_pago.data
        }
        }, status=status.HTTP_200_OK)