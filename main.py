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
                    json_data = json.dumps(processed_data)
                    await env.itinerarykv.put(f"job_{job_id}", json_data)
                    
                    fabricated_itinerary=[]
                    for i in range(1,payload.durationDays+1):
                        fabricated_itinerary.append({"day":i,"theme":"FILL","activities":[{"time":"morning","description":"FILL","location":"FILL"},{"time":"afternoon","description":"FILL","location":"FILL"},{"time":"evening","description":"FILL","location":"FILL"}]})
                    api_url="https://llm-itinerary-generator-processor.mohammad-e-asadolahi.workers.dev/"
                    # "headers": {
                    #             "Content-Type": "application/json"
                    #         },
                    # Use ctx.waitUntil to ensure the background task completes
                    # fetc_results=fetch(api_url,method="POST",body= json.dumps({"jobId": job_id,"iten": str(fabricated_itinerary)}))
                    ctx.waitUntil(send_analytics_data(env,job_id,fabricated_itinerary))

                    # env.fetch(
                    #         "https://llm-itinerary-generator-processor.mohammad-e-asadolahi.workers.dev/",
                    #         method="POST",
                    #         body={"jobId": job_id,"iten":str(ite)})

                    return Response(json.dumps(processed_data), status=202)
            except Exception as e:
                error_data = {"error": f"Failed to process POST request: {str(e)}"}
                return Response(json.dumps(error_data), status=400)
    else:
        data = {"error": "Failed to process non-POST request"}
        return Response(json.dumps(data), status=500)


async def send_analytics_data(env,jobId,itinerary):
    # try:
    jsond = await env.itinerarykv.get(f"job_{jobId}")
    parsed_data = json.loads(jsond)
    parsed_data["status"] = "failed"
    parsed_data["error"] = str("err")
    parsed_data["itinerary"] = itinerary
    await env.itinerarykv.put(f"job_{jobId}", json.dumps(parsed_data))

#         system_prompt="""Task: Fill in the "FILL" placeholders in the provided itinerary JSON for the given city.

# Instructions:

#     You will be given a city name, for example, "Paris."

#     The itinerary JSON will contain one or more days, each with a "theme" and a list of "activities." Each activity specifies a "time" (Morning, Afternoon, Evening), a "description," and a "location."

#     For each day:
#         If any "location" fields in the activities are already provided (i.e., not "FILL"), choose a theme from the following options that best fits those locations: 'historical', 'modern', 'art', 'musical', 'cultural'.
#         If all "location" fields are "FILL," choose any theme from the options above.
#         Set the "theme" to the chosen theme with the first letter capitalized, followed by the city name (e.g., "Historical Paris").

#     For each activity in the day:
#         If the "location" is "FILL," select a location in the city that fits the day's theme and provide a one-sentence description of an activity to do at that location during the specified time.
#         If the "location" is already provided, provide a one-sentence description of an activity to do at that location during the specified time, ensuring it aligns with the day's theme.
#         Ensure that the description is concise and relevant to both the theme and the time of day.

#     Only modify the "FILL" placeholders; leave all other fields unchanged.

#     Only Provide the completed JSON with all "FILL" placeholders appropriately replaced. do not add any prefix, postfix, apologies or explanation only the desiered output starting with [ and end with ]. 

# Example Input:

# City: Paris
# [
# {
#   "day": 1,
#   "theme": "FILL",
#   "activities": [
#     {
#       "time": "Morning",
#       "description": "FILL",
#       "location": "FILL"
#     },
#     {
#       "time": "Afternoon",
#       "description": "FILL",
#       "location": "FILL"
#     },
#     {
#       "time": "Evening",
#       "description": "FILL",
#       "location": "FILL"
#     }
#   ]
# },
# {
#   "day": 2,
#   "theme": "FILL",
#   "activities": [
#     {
#       "time": "Morning",
#       "description": "FILL",
#       "location": "Musée d'Orsay"
#     },
#     {
#       "time": "Afternoon",
#       "description": "FILL",
#       "location": "FILL"
#     },
#     {
#       "time": "Evening",
#       "description": "FILL",
#       "location": "FILL"
#     }
#   ]
# }
# ]
# Expected Output:
# [
# {
#   "day": 1,
#   "theme": "Historical Paris",
#   "activities": [
#     {
#       "time": "Morning",
#       "description": "Visit the Louvre Museum. Pre-book tickets to avoid queues.",
#       "location": "Louvre Museum"
#     },
#     {
#       "time": "Afternoon",
#       "description": "Explore the Notre-Dame Cathedral area and walk along the Seine.",
#       "location": "Île de la Cité"
#     },
#     {
#       "time": "Evening",
#       "description": "Dinner in the Latin Quarter.",
#       "location": "Latin Quarter"
#     }
#   ]
# },
# {
#   "day": 2,
#   "theme": "Art Paris",
#   "activities": [
#     {
#       "time": "Morning",
#       "description": "Discover Impressionist masterpieces at the Musée d'Orsay.",
#       "location": "Musée d'Orsay"
#     },
#     {
#       "time": "Afternoon",
#       "description": "Explore contemporary art at the Centre Pompidou.",
#       "location": "Centre Pompidou"
#     },
#     {
#       "time": "Evening",
#       "description": "Stroll through Montmartre and visit the Sacré-Cœur Basilica.",
#       "location": "Montmartre"
#     }
#   ]
# }
# ]"""

#         api_url = "https://api.openai.com/v1/chat/completions"

#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {env.OPENAI_API_KEY}"
#         }

#         openai_payload = {
#             "model": "gpt-3.5-turbo",
#             "messages": [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": f"{parsed_data["destination"]}\n{itinerary}"}
#             ]
#         }
        
#         # Use the imported fetch function
#         response = await fetch(api_url, method="POST", headers=headers, body=json.dumps(openai_payload))

#         if response.status != 200:
#             error_text = await response.text()
#             parsed_data["status"] = "failed"
#             parsed_data["error"] = str(error_text)
#             parsed_data["itinerary"] = itinerary
#             await env.itinerarykv.put(f"job_{jobId}", json.dumps(parsed_data))
#             return Response(f"Error from OpenAI API: {response.status} - {error_text}", status=response.status)

#         response_data = await response.json()
        
#         itinerary = response_data["choices"][0]["message"]["content"]
#         #use the following commented code to fabricate an itinerary
#         # itinerary = [
#         #     {
#         #         "day": 1,
#         #         "theme": f"Historical ",
#         #         "activities": [
#         #             {"time": "Morning", "description": "Visit museum", "location": "Museum"},
#         #             {"time": "Afternoon", "description": "Explore historic district", "location": "District"},
#         #             {"time": "Evening", "description": "Dinner at local restaurant", "location": "Downtown"}
#         #         ]
#         #     }
#         # ]
#         parsed_data["itinerary"] = itinerary
#         parsed_data["status"] = "completed"
#         parsed_data["completedAt"] = str(datetime.datetime.now())
#     except Exception as e:
#         parsed_data["status"] = "failed"
#         parsed_data["error"] = str(e)

#     # Update KV with results
#     await env.itinerarykv.put(f"job_{jobId}", json.dumps(parsed_data))