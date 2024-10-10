from rest_framework import serializers

# Modelos a serializar
from .models import Cheques, Cheqdet, Chequespagos

class ChequesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cheques
        fields = ['folio', 'fecha', "salidarepartidor", "cierre", "mesa", "nopersonas", "cambio", 'descuento', 'facturado', "cambiorepartidor", "usuariodescuento", 'idtipodescuento', "propinapagada", "propinafoliomovtocaja", "propinaincluida", "propinamanual", "totalarticulos", "subtotal", 'subtotalsinimpuestos', 'total', 'totalconpropina', 'totalimpuesto1', 'cargo', 'totalconcargo', 'totalconpropinacargo', 'descuentoimporte', 'efectivo', 'tarjeta', 'vales', 'otros', 'propina', 'propinatarjeta', 'totalsindescuento',  'totalalimentos', 'totalbebidas', 'totalotros', 'totaldescuentos', 'totaldescuentoalimentos', 'totaldescuentobebidas', 'totaldescuentootros', 'totalcortesias', 'totalcortesiaalimentos', 'totalcortesiabebidas', 'totalcortesiaotros', 'totaldescuentoycortesia', 'totalalimentossindescuentos', 'totalbebidassindescuentos', 'totalotrossindescuentos', 'descuentocriterio', 'subtotalcondescuento', 'totalimpuestod1', 'totalcondonativo', 'totalconpropinacargodonativo', 'subtotal_ec', 'total_ec', 'totalconpropinacargo_ec', 'totalsindescuentoimp']

class CheqdetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cheqdet
        fields = [
            'foliodet', 'movimiento', 'cantidad', 'idproducto', 'descuento', 'precio', 'impuesto1', 'preciosinimpuestos', 'comentario', 'usuariodescuento', 'comentariodescuento', 'idtipodescuento', 'idproductocompuesto', 'productocompuestoprincipal', 'preciocatalogo', 'idcortesia'
        ]

class ChequespagosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chequespagos
        fields = [
            'folio', 'importe', 'propina', 'tipodecambio'
        ]

# Formato de ventas (esto es lo que devuelve el endpoint de ventas)
class ChequeFolioSerializer(serializers.ModelSerializer): # Creamos la clase ChequeFolioSerializer que hereda de modelSerializer
    class Meta:
        model = Cheques
        fields = ['folio', 'efectivo', 'tarjeta', 'total', 'facturado']