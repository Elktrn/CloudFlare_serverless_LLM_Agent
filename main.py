from workers import Response
import json

async def on_fetch(request,env):
    if request.method == "POST":
        try:
            #env.openaikey
            pyaload = await request.json()
            name =pyaload.name
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