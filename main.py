from workers import Response
import json
import uuid
import datetime
import aiohttp

async def on_fetch(request, env):
    if request.method == "POST":
        payload = await request.json()
        if not data.get("jobId"):
            # Check if the request contains a jobId (user is checking job status)
            job_id = payload.jobId
            jsond = await env.itinerarykv.get(f"job_{job_id}")
            parsed_data =await json.loads(jsond)
            return Response(json.dumps(parsed_data), status=202)
        else:
            # No jobId, so register a new job
            try:
                job_id = await str(uuid.uuid4())
                
                # Register job in KV storage
                processed_data = {
                    "jobId": job_id,
                    "destination": payload.destination,
                    "durationDays": payload.durationDays,
                    "status": "pending",
                    "createdAt": str(datetime.datetime.now()),
                    "completedAt": "null",
                    "itinerary": "null",
                    "error": "null"
                }
                json_data =await json.dumps(processed_data)
                await env.itinerarykv.put(f"job_{job_id}", json_data)
                
                # ite=[]
                # for i in range(1,payload.durationDays+1):
                #     ite.append({"day":i,"theme":"FILL","activities":[{"time":"morning","description":"FILL","location":"FILL"},{"time":"afternoon","description":"FILL","location":"FILL"},{"time":"evening","description":"FILL","location":"FILL"}]})

                # env.fetch(
                #         "https://llm-itinerary-generator-processor.mohammad-e-asadolahi.workers.dev/",
                #         method="POST",
                #         body={"jobId": job_id,"iten":str(ite)})
                pd =await json.loads(processed_data)
                return Response(json.dumps(pd), status=202)
            except Exception as e:
                error_data = {"error": f"Failed to process POST request: {str(e)}"}
                return Response(json.dumps(error_data), status=400)
    else:
        data = {"error": "Failed to process non-POST request"}
        return Response(json.dumps(data), status=500)