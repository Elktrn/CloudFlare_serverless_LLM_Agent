from workers import Response
import json
import uuid
import datetime
import aiohttp

async def on_fetch(request, env):
    if request.method == "POST":
        payload = await request.json()
        try:
            # Check if the request contains a jobId (user is checking job status)
            job_id = payload.get("jobId")
            if job_id:
                jsond = await env.itinerarykv.get(f"job_{job_id}")
                if jsond:
                    parsed_data = json.loads(jsond)
                    return Response(json.dumps(parsed_data), status=202)
                else:
                    return Response(json.dumps({"error": "Job not found"}), status=404)
        except Exception as e:
            print(f"Error checking job status: {str(e)}")
            # No jobId, so register a new job
            try:
                job_id = str(uuid.uuid4())
                
                # Register job in KV storage
                processed_data = {
                    "jobId": job_id,
                    "destination": payload.get("destination"),
                    "durationDays": payload.get("durationDays"),
                    "status": "pending",
                    "createdAt": str(datetime.datetime.now()),
                    "completedAt": "null",
                    "itinerary": "null",
                    "error": "null"
                }
                json_data = json.dumps(processed_data)
                await env.itinerarykv.put(f"job_{job_id}", json_data)
                print(f"Successful job_{job_id} injection to KV: {processed_data}")

                # Trigger Processor Worker via HTTP request
                processor_url = "https://llm-itinerary-generator-processor.mohammad-e-asadolahi.workers.dev/"
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            processor_url,
                            json={"jobId": job_id},
                            timeout=10
                        ) as response:
                            if response.status != 200:
                                print(f"Failed to trigger Processor Worker for job_{job_id}: HTTP {response.status}")
                                processed_data["error"] = f"Failed to trigger processor: HTTP {response.status}"
                                processed_data["status"] = "failed"
                                await env.itinerarykv.put(f"job_{job_id}", json.dumps(processed_data))
                            else:
                                print(f"Successfully triggered Processor Worker for job_{job_id}")
                except Exception as e:
                    print(f"Error triggering Processor Worker for job_{job_id}: {str(e)}")
                    processed_data["error"] = f"Failed to trigger processor: {str(e)}"
                    processed_data["status"] = "failed"
                    await env.itinerarykv.put(f"job_{job_id}", json.dumps(processed_data))

                return Response(json.dumps(processed_data), status=202)
            except Exception as e:
                error_data = {"error": f"Failed to process POST request: {str(e)}"}
                print(f"POST request error: {str(e)}")
                return Response(json.dumps(error_data), status=400)
    else:
        data = {"error": "Failed to process non-POST request"}
        return Response(json.dumps(data), status=400)