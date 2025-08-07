from workers import Response
import json

def on_fetch(request):
    headers = {
        "content-type": "application/json",
        "Access-Control-Allow-Origin": "*"  # For CORS, adjust as needed
    }

    if request.method == "POST":
        try:
            # Read the JSON payload
            payload = request.json()

            # Extract variables with defaults
            # name = payload.get("name", "Unknown")

            # Example processing
            processed_data = {
                "greeting": f"Hello, {name}!",
                "received_payload": payload  # Echo the full payload
            }

            return Response(json.dumps(processed_data), headers=headers, status=200)
        except Exception as e:
            # Handle invalid JSON or errors
            error_data = {"error": f"Failed to process POST request: {str(e)}"}
            return Response(json.dumps(error_data), headers=headers, status=400)
    else:
        # Handle non-POST requests
        data = {
            "message": "Hello Python Worker! Use POST to send variables.",
            "status": "Non-POST request"
        }
        return Response(json.dumps(data), headers=headers, status=200)