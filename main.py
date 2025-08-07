from js import Response
import json
import asyncio

async def on_fetch(request):
    if request.method == "POST":
        try:
            # Await the PyodideFuture to get the JSON payload
            payload = await request.json()
            name = payload.get("name", "Unknown")
            processed_data = {"greeting": f"Hello, {name}!"}
            return Response(json.dumps(processed_data), status=200, headers={"Content-Type": "application/json"})
        except Exception as e:
            error_data = {"error": f"Failed to process POST request: {str(e)}"}
            return Response(json.dumps(error_data), status=400, headers={"Content-Type": "application/json"})
    else:
        error_data = {"error": "Only POST requests are supported"}
        return Response(json.dumps(error_data), status=405, headers={"Content-Type": "application/json"})