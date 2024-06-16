import os
import time
import requests
import json
import logging

def get_transcript(file_path, logger):
    swiftink_api_key = os.environ.get("SWIFTINK_API_KEY")
    file_name = file_path.split("/")[-1]

    # get presigned URL from swiftink database
    pres_url_retries = 0
    pres_url_success = False
    while pres_url_retries < 3 and pres_url_success == False :
        pres_url_request = requests.post(
            "https://api.swiftink.io/transcripts/upload", 
            headers={
                "accept": "application/json",
                "authorization": swiftink_api_key
            }
        )

        if str(pres_url_request.status_code)[0] == '2' :
            pres_url_success = True
        else :
            # log swift API response
            print(pres_url_request.status_code)
            time.sleep(30)
        pres_url_retries += 1

    # if response is not 200 wait 30seconds and stop after 3 tries (also log)
    if pres_url_success :
        print(pres_url_request.text)
        # log
    else :
        return "Failed to communicate with swiftink API", 408
        # log

    pres_url = pres_url_request.json()['url']
    bucket_token = pres_url.split('token=')[1]

    # upload file to presigned URL
    upload_retries = 0
    upload_success = False
    while upload_retries < 3 and upload_success == False :
        upload_request = requests.put(
            pres_url, 
            headers={
                "authorization": "Bearer " + bucket_token,
                "x-upsert": "true"
            }, 
            files={'file': open(file_path,'rb')}
        )

        if str(upload_request.status_code)[0] == '2' :
            upload_success = True
        else :
            # log swift API response
            time.sleep(30)
        upload_retries += 1

    if upload_success :
        print(upload_request.text)
        # log
    else :
        return "Failed to communicate with Swiftink's supabase API", 408
        # log

    # get transcript of file
    transcript_retries = 0
    transcript_success = False
    while transcript_retries < 3 and transcript_success == False :
        transcript_request = requests.post(
            "https://api.swiftink.io/transcripts/", 
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": swiftink_api_key
            }, 
            json={
                "name": file_name,
                "url": pres_url,
                "do_async": False,
                "language": "fr"
            }
        )

        if str(transcript_request.status_code)[0] == '2' :
            transcript_success = True
        else :
            # log swift API response
            time.sleep(30)
        transcript_retries += 1

    if transcript_success :
        print(transcript_request.text)
        # log
    else :
        return "Failed to communicate with Swiftink's API", 408
        # log

    # also return swiftink transcript ID to store in the database
    return {
        "text": transcript_request.json()["text"],
        "swiftink_id": transcript_request.json()["id"]
    }