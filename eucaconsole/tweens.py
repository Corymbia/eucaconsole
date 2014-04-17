import os


def setup_tweens(config):
    """Since tweens order is important this function will take care of proper ordering"""
    config.add_tween('eucaconsole.tweens.https_tween_factory')
    config.add_tween('eucaconsole.tweens.xframe_tween_factory')
    config.add_tween('eucaconsole.tweens.request_id_tween_factory')


def https_tween_factory(handler, registry):
    def tween(request):
        response = handler(request)
        if request.environ.get('HTTP_X_FORWARDED_PROTO') == 'https':
            request.scheme = 'https'
        return response
    return tween


def xframe_tween_factory(handler, registry):
    def tween(request):
        response = handler(request)
        if response.content_type and response.content_type.strip().lower() == 'text/html':
            response.headers['X-FRAME-OPTIONS'] = 'SAMEORIGIN'
        return response
    return tween


def request_id_tween_factory(handler, registry):
    def tween(request):
        request.id = os.urandom(16).encode('base64').rstrip('=\n')
        response = handler(request)
        return response
    return tween
