from workers import Response, DurableObject
import json
import uuid
import datetime

# Durable Object class
class ItineraryProcessor(DurableObject):
    async def process_job(self, job_id):
        try:
            # Fetch job data from KV
            jsond = await self.env.itinerarykv.get(f"job_{job_id}")
            if not jsond:
                print(f"Job_{job_id} not found in KV")
                return
            parsed_data = json.loads(jsond)

            # Generate itinerary (mock implementation)
            try:
                itinerary = [
                    {
                        "day": 1,
                        "theme": f"Historical {parsed_data['destination']}",
                        "activities": [
                            {
                                "time": "Morning",
                                "description": "Visit a major museum. Pre-book tickets.",
                                "location": "Museum"
                            },
                            {
                                "time": "Afternoon",
                                "description": "Explore the historic district.",
                                "location": "Historic District"
                            },
                            {
                                "time": "Evening",
                                "description": "Dinner in a local restaurant.",
                                "location": "Downtown"
                            }
                        ]
                    }
                ]
                parsed_data["itinerary"] = itinerary
                parsed_data["completedAt"] = str(datetime.datetime.now())
                parsed_data["status"] = "completed"
            except Exception as e:
                parsed_data["status"] = "failed"
                parsed_data["error"] = str(e)

            # Update KV with results
            json_data = json.dumps(parsed_data)
            await self.env.itinerarykv.put(f"job_{job_id}", json_data)
            print(f"Processed job_{job_id}: {parsed_data['status']}")

        except Exception as e:
            print(f"Error processing job_{job_id}: {str(e)}")
            parsed_data["status"] = "failed"
            parsed_data["error"] = str(e)
            json_data = json.dumps(parsed_data)
            await self.env.itinerarykv.put(f"job_{job_id}", json_data)

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
        except:
            # No jobId, so register a new job
            try:
                job_id = str(uuid.uuid4())
                
                # Register job in KV storage
                processed_data = {
                    "jobId": job_id,
                    "destination": payload.get("destination"),
                    "durationDays": payload.get("durationDays"),
                    "status": "processing",
                    "createdAt": str(datetime.datetime.now()),
                    "completedAt": "null",
                    "itinerary": "null",
                    "error": "null"
                }
                json_data = json.dumps(processed_data)
                await env.itinerarykv.put(f"job_{job_id}", json_data)
                print(f"Successful job_{job_id} injection to KV: {processed_data}")

                # Delegate to Durable Object
                durable_obj = env.ITINERARY_PROCESSOR.id_from_name(job_id)
                stub = env.ITINERARY_PROCESSOR.get(durable_obj)
                await stub.process_job(job_id)

                return Response(json.dumps(processed_data), status=202)
            except Exception as e:
                error_data = {"error": f"Failed to process POST request: {str(e)}"}
                return Response(json.dumps(error_data), status=400)
    else:
        data = {"error": "Failed to process non-POST request"}
        return Response(json.dumps(data), status=400)