import os
import requests
import json
import logging

def get_transcript(file_path):
    swiftink_api_key = os.environ.get("SWIFTINK_API_KEY")
    name = file_path.split("/")[-1]

    # get presigned URL from swiftink database
    presigned_url_response = requests.post(
        "https://api.swiftink.io/transcripts/upload", 
        headers={
            "accept": "application/json",
            "authorization": swiftink_api_key
        }
    )

    # if response is not 200 wait 30seconds and stop after 3 tries (also log)
    print(presigned_url_response.text)

    presigned_url = presigned_url_response.json()['url']
    bucket_token = presigned_url.split('token=')[1]

    # upload file to presigned URL
    upload_response = requests.put(
        presigned_url, 
        headers={
            "authorization": "Bearer " + bucket_token,
            "x-upsert": "true"
        }, 
        files={'file': open(file_path,'rb')}
    )

    # if response is not 200 log
    print(upload_response.text)

    # get transcript of file
    transcript_request = requests.post(
        "https://api.swiftink.io/transcripts/", 
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": swiftink_api_key
        }, 
        json={
            "name": name,
            "url": presigned_url,
            "do_async": False,
            "language": "fr"
        }
    )

    # also return swiftink transcript ID to store in the database
    return transcript_request.json()["text"]