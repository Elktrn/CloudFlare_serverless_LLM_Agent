from workers import Response
import json

def on_fetch(request):
    data = {
        "message": "Hello Python Worker!",
        "status": "completed request"
    }

    json_data = json.dumps(data)

    headers = {
        "content-type": "application/json"
    }
    return Response(json_data, headers=headers)