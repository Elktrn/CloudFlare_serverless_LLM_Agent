from workers import Response,fetch
import json
import uuid
import datetime

async def on_fetch(request, env,ctx):
    if request.method == "POST":
        payload = await request.json()
        try:
            # Check if the request contains a jobId (user is checking job status)
            job_id = payload.jobId
            jsond = await env.itinerarykv.get(f"job_{job_id}")
            return Response(json.dumps(jsond), status=202)
        except Exception as e:
            try:
                # No jobId, so register a new job

                    job_id = str(uuid.uuid4())
                    
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
                    # json_data = json.dumps(processed_data)
                    # await env.itinerarykv.put(f"job_{job_id}", json_data)
                    
                    # fabricated_itinerary=[]
                    # for i in range(1,payload.durationDays+1):
                    #     fabricated_itinerary.append({"day":i,"theme":"FILL","activities":[{"time":"morning","description":"FILL","location":"FILL"},{"time":"afternoon","description":"FILL","location":"FILL"},{"time":"evening","description":"FILL","location":"FILL"}]})

                                    # Use ctx.waitUntil to ensure the background task completes
                    # background_task = fetch(
                    #     "https://llm-itinerary-generator-processor.mohammad-e-asadolahi.workers.dev/",
                    #     {
                    #         "method": "POST",
                    #         "headers": {
                    #             "Content-Type": "application/json"
                    #         },
                    #         "body": json.dumps({
                    #             "jobId": job_id,
                    #             "iten": str(fabricated_itinerary)
                    #         })
                    #     }
                    # )
                    
                    # ctx.wait_until(background_task)

                    # env.fetch(
                    #         "https://llm-itinerary-generator-processor.mohammad-e-asadolahi.workers.dev/",
                    #         method="POST",
                    #         body={"jobId": job_id,"iten":str(ite)})
                    # pd =json.loads(processed_data)
                    return Response(json.dumps(processed_data), status=202)
            except Exception as e:
                error_data = {"error": f"Failed to process POST request: {str(e)}"}
                return Response(json.dumps(error_data), status=400)
    else:
        data = {"error": "Failed to process non-POST request"}
        return Response(json.dumps(data), status=500)