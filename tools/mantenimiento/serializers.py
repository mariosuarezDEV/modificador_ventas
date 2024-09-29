from rest_framework import serializers # Importamos el módulo serializers de Django REST Framework

from .models import Cheques, Cheqdet, Chequespagos

from django.db.models import Sum # Importamos el módulo Sum de Django

class ChequeSerializer(serializers.ModelSerializer): # Creamos la clase ChequeSerializer que hereda de modelSerializer
    class Meta:
        model = Cheques
        fields = ['folio', 'numcheque', 'fecha', 'cierre', 'mesa', 'nopersonas', 'cambio', 'descuento', 'reabiertas', 'facturado', 'comentariodescuento', 'usuariodescuento', 'idtipodescuento', 'propinapagada','propinafoliomovtocaja', 'propinaincluida','propinamanual', 'totalarticulos', 'subtotal', 'subtotalsinimpuestos', 'total', 'totalconpropina', 'totalimpuesto1', 'cargo', 'totalconcargo', 'totalconpropinacargo', 'efectivo', 'tarjeta', 'vales', 'otros', 'propina', 'totalsindescuento', 'totalalimentos', 'totalbebidas', 'totalotros', 'totaldescuentos', 'totaldescuentoalimentos', 'totaldescuentobebidas', 'totaldescuentootros', 'totalcortesias', 'totalcortesiaalimentos', 'totalcortesiabebidas', 'totalcortesiaotros', 'totaldescuentoycortesia', 'totalalimentossindescuentos', 'totalbebidassindescuentos', 'totalotrossindescuentos', 'descuentocriterio', 'subtotalcondescuento', 'totalimpuestod1']

class CheqdetSerializer(serializers.ModelSerializer): # Creamos la clase CheqdetSerializer que hereda de modelSerializer
    class Meta:
        model = Cheqdet
        fields = ['foliodet', 'movimiento', 'cantidad', 'idproducto', 'descuento', 'precio', 'impuesto1', 'preciosinimpuestos', 'hora', 'modificador', 'usuariodescuento', 'comentariodescuento', 'idtipodescuento', 'idproductocompuesto', 'productocompuestoprincipal', 'preciocatalogo']

class ChequespagosSerializer(serializers.ModelSerializer): # Creamos la clase ChequespagosSerializer que hereda de modelSerializer
    class Meta:
        model = Chequespagos
        fields = ['folio', 'importe', 'propina']

# Serializadores personalizados

# Ver solo los folios de los cheques
class ChequeFolioSerializer(serializers.ModelSerializer): # Creamos la clase ChequeFolioSerializer que hereda de modelSerializer
    class Meta:
        model = Cheques
        fields = ['folio', 'total']