from workers import Response
import json
import uuidv4;

async def on_fetch(request,env):
    if request.method == "POST":
        try:
            #env.openaikey
            pyaload = await request.json()
            duration_days =pyaload.durationDays
            
            jobId = uuidv4()
            immediate_response = {
                "jobId": jobId,
                "status": "accepted",
                "duration days":duration_days
            }
            # processed_data = {
            #     "greeting": f"DurationDays, {name}!"}
            
            setTimeout(async () => {
                try:
                    processed_data = {
                        "jobId": jobId,
                        "duration days":duration_days
                    }
                    # Could store result in env.KV here
                    console.log('Processed:', processed_data)
                except Exception as e:
                    console.error('Async error:', e)
            }, 0)

            return Response(json.dumps(immediate_response), status=200)
        except Exception as e:
            error_data = {"error": f"Failed to process POST request: {str(e)}"}
            return Response(json.dumps(error_data), status=400)
    else:
        data = {
            "error": "Failed to process Non-POST request"
        }
        return Response(json.dumps(data), status=400)