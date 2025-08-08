from workers import Response
import json
import uuid;
import asyncio

async def on_fetch(request,env):
    if request.method == "POST":
        try:
            # If the request of user contains jobID it means it has been already submitted 
            # and the user wants the result of the job
            job_Id=(await request.json()).jobId
            jsond = await env.itinerarykv.get(f"job_{job_Id}")
            parsed_data = json.loads(jsond)
            return Response(json.dumps(parsed_data), status=202)
        except Exception as e:
            # So no jobId found in the input json therefore user is trying to register a job for llm
            try:
                
                pyaload = await request.json()
                duration_days =pyaload.durationDays
                
                jobId = str(uuid.uuid4())
                immediate_response = {
                    "jobId": jobId,
                    "status": "accepted",
                    "duration days":duration_days
                }
            
                def DB_register_job_():
                    # We want to inject the job to the database (KV of CouldFlare in here)
                    #  to be processsed async by the LLM generation function
                    try:
                        processed_data = {
                            "jobId": jobId,
                            "greeting": f"dd at async, {duration_days}!",
                            "status":"processing"
                        }
                        json_data = json.dumps(processed_data)
                        env.itinerarykv.put(f"job_{jobId}", json_data)
                        print('Successful job_{jobId} injection to kv', processed_data)
                    except Exception as e:
                        print('Unsuccessful job_{jobId} injection to kv:', e)

                DB_register_job_()

                async def generate_itinerary_llm():
                    # The injected job into the db is processed async by this function
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