from workers import Response
import json

def on_fetch(request):
    if request.method == "POST":
        try:
            # Read the JSON payload
            payload = request.json()
            name ="kkk"# payload.get("name", "Unknown")
            processed_data = {
                "greeting": f"Hello, {name}!"}
            return Response(json.dumps(processed_data), status=200)
        except Exception as e:
            error_data = {"error": f"Failed to process POST request: {str(e)}"}
            return Response(json.dumps(error_data), status=400)
    else:
        data = {
            "error": "Failed to process Non-POST request"
        }
        return Response(json.dumps(data), status=400)