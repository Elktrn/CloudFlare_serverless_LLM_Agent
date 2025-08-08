from workers import Response
import json
import uuid;
import asyncio
async def on_fetch(request,env):
    if request.method == "POST":
        try:
            #env.openaikey
            pyaload = await request.json()
            duration_days =pyaload.durationDays
            
            jobId = str(uuid.uuid4())
            immediate_response = {
                "jobId": jobId,
                "status": "accepted",
                "duration days":duration_days
            }
        
            async def process_async():
                try:
                    processed_data = {
                        "jobId": jobId,
                        "greeting": f"dd at async, {duration_days}!"
                    }
                    json_data = json.dumps(processed_data)
                    await env.itinerarykv.put(f"job_{jobId}", json_data)
                    print('Processed:', processed_data)
                except Exception as e:
                    print('Async error:', e)

            asyncio.create_task(process_async())

            return Response(json.dumps(immediate_response), status=202)
        except Exception as e:
            error_data = {"error": f"Failed to process POST request: {str(e)}"}
            return Response(json.dumps(error_data), status=400)
    else:
        data = {
            "error": "Failed to process Non-POST request"
        }
        return Response(json.dumps(data), status=400)