from workers import Response
import json

def on_fetch(request, env):
    print(env)
    if request.method == "POST":
        openai_api_key = env.openaikey
        try:
            # Read the JSON payload
            payload = request.json()
            name = payload.get("name", "Unknown")
            processed_data = {
                "greeting": f"Hello, {name}!","mykey":openai_api_key[0:10]}
            print(openai_api_key[0:10])
            return Response(json.dumps(processed_data), status=200)
        except Exception as e:
            error_data = {"error": f"Failed to process POST request: {str(e)}"}
            return Response(json.dumps(error_data), status=400)
    else:
        data = {
            "error": "Failed to process Non-POST request"
        }
        return Response(json.dumps(data), status=400)
