from workers import Response

def on_fetch(request):
    return Response("Hello World!")