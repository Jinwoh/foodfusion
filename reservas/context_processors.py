from .models import Cliente  # ajusta según ubicación real

def cliente_context(request):
    cliente = None
    if request.session.get('cliente_id'):
        try:
            cliente = Cliente.objects.get(id=request.session['cliente_id'])
        except Cliente.DoesNotExist:
            pass
    return {'cliente': cliente}
