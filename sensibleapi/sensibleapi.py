import json
import time
from urllib.parse import urlencode
import requests

base_url = "https://api.sensible.so/v0"


class SensibleSDK:
    def __init__(self, api_key):
        self.api_key = api_key

    def extract(self, *,
                file=None,
                url=None,
                path=None,

                document_type=None,
                configuration_name=None,
                document_types=None,

                webhook=None,
                document_name=None,
                environment=None
                ):
        request_url = base_url + \
            ("/extract_from_url" if url else "/generate_upload_url") + \
            (f'/{document_type}' if document_type else
                (f'/{configuration_name}' if configuration_name else "")) + \
            querystring(environment, document_name)

        body = {}
        if url:
            body["document_url"] = url
        if webhook:
            body["webhook"] = webhook
        if document_types:
            body["types"] = document_types

        headers = {"authorization": f'Bearer {self.api_key}',
                   "content-type": "application/json"}

        response = requests.post(
            request_url, headers=headers, data=json.dumps(body))
        if response.status_code != 200:
            throw_error(response)

        response_body = response.json()
        if url:
            if not is_extraction_response(response_body):
                raise Exception(
                    f'Got invalid response from generate_upload_url: {response.text}')
            return {"type": "extraction", "id": response_body["id"]}
        elif not is_extraction_url_response(response_body):
            raise Exception(
                f'Got invalid response from extract_from_url: {response.text}')

        if path:
            file = open(path, "rb")
        put_response = requests.put(response_body["upload_url"], data=file)

        if put_response.status_code != 200:
            raise Exception(
                f'Error {put_response.status_code} uploading file to S3: ${put_response.text}')

        return {"type": "extraction", "id": response_body["id"]}

    def classify(self, *, file=None, path=None):
        url = f'{base_url}/classify/async'
        headers = {"authorization": f'Bearer {self.api_key}',
                   "content-type": "application/pdf"}
        if path:
            file = open(path, "rb")
        response = requests.post(url, headers=headers, data=file)
        if response.status_code != 200:
            throw_error(response)
        response_body = response.json()
        if not is_classification_response(response_body):
            raise Exception(
                f'Got invalid response from extract_from_url: {response.text}')
        return {
            "type": "classification",
            "id": response_body["id"],
            "download_link": response_body["download_link"]
        }

    def wait_for(self, request):
        headers = {"authorization": f'Bearer {self.api_key}',
                   "content-type": "application/json"}
        while True:
            if request["type"] == "extraction":
                response = requests.get(
                    f'{base_url}/documents/{request["id"]}', headers=headers)
                if response.status_code != 200:
                    throw_error(response)
                response_body = response.json()
                if "status" in response_body and response_body["status"] != "WAITING":
                    return response_body
            else:
                response = requests.get(request["download_link"])
                if response.status_code == 200:
                    return response.json()
                if response.status_code != 404:
                    throw_error(response)
            time.sleep(5)

    def generate_excel(self, extractions):
        headers = {"authorization": f'Bearer {self.api_key}'}

        if type(extractions) not in (tuple, list):
            extractions = [extractions]
        url = base_url + "/generate_excel/" + \
            ",".join(map(lambda extraction: extraction["id"], extractions))
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        throw_error(response)


def querystring(environment, document_name):
    query = {}
    if environment:
        query["environment"] = environment
    if document_name:
        query["documentName"] = document_name
    return f'?{urlencode(query)}'


def throw_error(response):
    status = response.status_code
    if status == 400:
        raise Exception(f'Bad Request (400): {response.text}')
    elif status == 401:
        raise Exception("Unauthorized (401), please check your API key")
    elif status == 415:
        raise Exception(
            "Unsupported Media Type (415), please check your document format")
    elif status == 429:
        # automatic retry?
        raise Exception("Too Many Requests (429)")
    elif status == 500:
        raise Exception(f'Internal Server Error (500): {response.text}')
    else:
        raise Exception(f'Got unknown HTTP status code {status}: {response.text}')


def is_extraction_response(response):
    return "id" in response


def is_extraction_url_response(response):
    return "id" in response and "upload_url" in response


def is_classification_response(response):
    return "id" in response and "download_link" in response
