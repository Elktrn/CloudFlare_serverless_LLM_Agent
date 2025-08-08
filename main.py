from workers import Response
import json
import uuid;
import asyncio
import time
import datetime

async def on_fetch(request,env):
    if request.method == "POST":
        pyaload=await request.json()
        try:
            # If the request of user contains jobID it means it has been already submitted 
            # and the user wants the result of the job
            job_Id=pyaload.jobId
            jsond = await env.itinerarykv.get(f"job_{job_Id}")
            parsed_data = json.loads(jsond)
            return Response(json.dumps(parsed_data), status=202)
        except Exception as e:
            # So no jobId found in the input json therefore user is trying to register a job for llm
            try:
                jobId = str(uuid.uuid4())
            
                def DB_register_job_():
                    # We want to inject the job to the database (KV of CouldFlare in here)
                    #  to be processsed async by the LLM generation function
                    try:
                        processed_data = {
                            "jobId": jobId,
                            "destination":pyaload.destination,
                            "durationDays": pyaload.durationDays,
                            "status":"processing",
                            "createdAt":"null",
                            "completedAt":"null",
                            "itinerary":"null",
                            "error":'null'
                        }
                        json_data = json.dumps(processed_data)
                        env.itinerarykv.put(f"job_{jobId}", json_data)
                        print('Successful job_{jobId} injection to kv', processed_data)
                    except Exception as e:
                        print('Unsuccessful job_{jobId} injection to kv:', e)

                DB_register_job_()
                    
                asyncio.create_task(generate_itinerary_llm(env,jobId))

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
    
async def generate_itinerary_llm(env,jobId):
    # The injected job into the db is processed async by this function
    try:
        #env.openaikey
        jsond = await env.itinerarykv.get(f"job_{jobId}")
        parsed_data = json.loads(jsond)
        retries=0
        try :
            # llm.get_message(input_text,prompt)
            itinerary= [{"day": 1,
                    "theme": "Historical Paris",
                    "activities": [{
                        "time": "Morning",
                        "description": "Visit the Louvre Museum. Pre-book tickets to avoid queues.",
                        "location": "Louvre Museum"},
                        {
                        "time": "Afternoon",
                        "description": "Explore the Notre-Dame Cathedral area and walk along the Seine.",
                        "location": "Île de la Cité"},
                        {
                        "time": "Evening",
                        "description": "Dinner in the Latin Quarter.",
                        "location": "Latin Quarter"}]}]
            parsed_data["itinerary"]=itinerary
            parsed_data["completedAt"]=datetime.now()
            parsed_data["status"]="completed"

        except Exception as e:
            parsed_data["status"]="failed"
            parsed_data["error"]=str(e)
            
        json_data = json.dumps(parsed_data)
        await env.itinerarykv.put(f"job_{jobId}", json_data)

    except Exception as e:
        parsed_data["status"]="failed"
        parsed_data["error"]=str(e)
            
        json_data = json.dumps(parsed_data)
        await env.itinerarykv.put(f"job_{jobId}", json_data)
        print('Async generate_itinerary_llm fundumental error:', e)