from uuid import uuid4
from functools import wraps
from flask import current_app, request, jsonify
from models import db, Users
import os
import re
import jwt
import time
import requests
import json
import logging
import datetime as dt

werkzeug_regex = r'\[.+\] '

class WerkzeugFilter(logging.Formatter):
    def filter(self, record):
        message = record.msg
        if re.findall(werkzeug_regex, message) :
            record.msg = re.sub(
                werkzeug_regex,
                '',
                message
            )
        return True

class JSONFormatter(logging.Formatter):
    def __init__(self, *, fmt_keys) :
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    def format(self, record):
        message = {
            key: getattr(record, val) for key, val in self.fmt_keys.items()} 
        message.update({
            "message": record.getMessage(), 
            "timestamp": dt.datetime.fromtimestamp(record.created, tz=dt.timezone.utc)})

        return json.dumps(message, default=str)

def generate_token(password):
    new_uuid = str(uuid4())
    token = jwt.encode(payload={'password': password, 'uuid': new_uuid}, key=current_app.secret_key, algorithm="HS256")
    return token, new_uuid

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token :
            try :
                decoded_token = jwt.decode(jwt=token, key=current_app.secret_key, algorithms=['HS256'])
            except :
                return jsonify({'message': 'Invalid token'}), 403
            user = db.session.query(Users).first()

            if decoded_token.get("password") == user.password and decoded_token.get("uuid") == user.uuid :
                return f(*args, **kwargs)
            else :
                return jsonify({'message': 'Invalid token'}), 403
        else :
            return jsonify({'message': 'Missing token'}), 403
    return decorated

class Swiftink() :
    def __init__(self, file_path, logger=None) :
        self.text = None
        self.id = None
        self.last_request = None

        swiftink_api_key = os.environ.get("SWIFTINK_API_KEY")
        file_name = file_path.split("/")[-1]

        # get presigned URL from swiftink database
        pres_url_request = self.call_API(
            req_type = "POST",
            api_url = "https://api.swiftink.io/transcripts/upload", 
            headers = {
                "accept": "application/json",
                "authorization": swiftink_api_key
            }
        )

        if pres_url_request == None :
            # log
            self.last_request = "Swiftink presigned URL"
            return None
        print(pres_url_request.text)
        # log
        
        # upload file to presigned URL
        pres_url = pres_url_request.json()['url']
        bucket_token = pres_url.split('token=')[1]
        upload_request = self.call_API(
            req_type = "PUT",
            api_url = pres_url, 
            headers = {
                "authorization": "Bearer " + bucket_token,
                "x-upsert": "true"
            }, 
            files = {'file': open(file_path,'rb')}
        )

        if upload_request == None :
            # log
            self.last_request = "Swiftink file upload"
            return None
        print(upload_request.text)
        # log

        # get transcript of file
        transcript_request = self.call_API(
            req_type = "POST",
            api_url = "https://api.swiftink.io/transcripts/", 
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": swiftink_api_key
            }, 
            payload = {
                "name": file_name,
                "url": pres_url,
                "do_async": False,
                "language": "fr"
            }
        )

        if transcript_request == None :
            # log
            self.last_request = "Swiftink get transcription"
            return None
        self.text = transcript_request.json()["text"]
        self.id = transcript_request.json()["id"]
        # log

    def call_API(self, req_type, api_url, headers, payload=None, files=None) :
        retries = 0
        success = False
        while retries < 3 and success == False :
            if req_type == "POST" :
                request = requests.post(
                    api_url,
                    headers=headers,
                    json=payload
                )
            elif req_type == "PUT" :
                request = requests.put(
                    api_url,
                    headers=headers,
                    files=files
                )
    
            retries += 1

            # if status code starts by 2 then request was successful
            if str(request.status_code)[0] == '2' :
                success = True
            else :
                # log swift API response
                print(request.status_code)
                time.sleep(30)
        
        if success :
            return request
        else :
            return None
