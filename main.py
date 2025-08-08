from workers import Response
import json
import uuid;
import asyncio

async def on_fetch(request,env):
    if request.method == "POST":
        try:
            job_Id=(await request.json()).jobId
            jsond = await env.itinerarykv.get(f"job_{job_Id}")
            parsed_data = json.loads(jsond)
            return Response(json.dumps(parsed_data), status=202)
        except Exception as e:
            try:
                
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
                            "greeting": f"dd at async, {duration_days}!",
                            "status":"processing"
                        }
                        json_data = json.dumps(processed_data)
                        await env.itinerarykv.put(f"job_{jobId}", json_data)
                        print('Successful job_{jobId} injection to kv', processed_data)
                    except Exception as e:
                        print('Unsuccessful job_{jobId} injection to kv:', e)

                await process_async()

                async def generate_itinerary_llm():
                    try:
                        #env.openaikey
                        jsond = await env.itinerarykv.get(f"job_{jobId}")
                        parsed_data = json.loads(jsond)
                        parsed_data["status"]="llmgenerated"
                        json_data = json.dumps(parsed_data)
                        await env.itinerarykv.put(f"job_{jobId}", json_data)
                        print('Processed:', parsed_data)
                    except Exception as e:
                        print('Async error:', e)
                    
                asyncio.create_task(generate_itinerary_llm())
                jsond = await env.itinerarykv.get(f"job_{jobId}")
                parsed_data = json.loads(jsond)
                return Response(json.dumps(parsed_data), status=202)
            except Exception as e:
                error_data = {"error": f"Failed to process POST request: {str(e)}"}
                return Response(json.dumps(error_data), status=400)
    else:
        data = {
            "error": "Failed to process Non-POST request"
        }
        return Response(json.dumps(data), status=400)