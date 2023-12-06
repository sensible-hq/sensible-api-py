import json
import time
from urllib.parse import urlencode
import requests

baseUrl = "https://api.sensible.so/v0"


class SensibleSDK:
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def extract(self, *,
                file=None,
                url=None,
                path=None,

                documentType=None,
                configurationName=None,
                documentTypes=None,

                webhook=None,
                documentName=None,
                environment=None
                ):
        requestUrl = baseUrl + \
            ("/extract_from_url" if url else "/generate_upload_url") + \
            (f'/{documentType}' if documentType else
                (f'/{configurationName}' if configurationName else "")) + \
            querystring(environment, documentName)

        body = {}
        if url:
            body["document_url"] = url
        if webhook:
            body["webhook"] = webhook
        if documentTypes:
            body["types"] = documentTypes

        headers = {"authorization": f'Bearer {self.apiKey}',
                   "content-type": "application/json"}

        response = requests.post(
            requestUrl, headers=headers, data=json.dumps(body))
        if response.status_code != 200:
            throwError(response)

        responseBody = response.json()
        if url:
            if not isExtractionResponse(responseBody):
                raise Exception(
                    f'Got invalid response from generate_upload_url: {response.text}')
            return {"type": "extraction", "id": responseBody["id"]}

        if not isExtractionUrlResponse(responseBody):
            raise Exception(
                f'Got invalid response from extract_from_url: {response.text}')

        if path:
            file = open(path, "rb")
        putResponse = requests.put(responseBody["upload_url"], data=file)

        if putResponse.status_code != 200:
            raise Exception(
                f'Error {putResponse.status_code} uploading file to S3: ${putResponse.text}')

        return {"type": "extraction", "id": responseBody["id"]}

    def classify(self, *, file=None, path=None):
        url = f'{baseUrl}/classify/async'
        headers = {"authorization": f'Bearer {self.apiKey}',
                   "content-type": "application/pdf"}
        if path:
            file = open(path, "rb")
        response = requests.post(url, headers=headers, data=file)
        if response.status_code != 200:
            throwError(response)
        responseBody = response.json()
        if not isClassificationResponse(responseBody):
            raise Exception(
                f'Got invalid response from extract_from_url: {response.text}')
        return {
            "type": "classification",
            "id": responseBody["id"],
            "downloadLink": responseBody["download_link"]
        }

    def waitFor(self, request):
        headers = {"authorization": f'Bearer {self.apiKey}',
                   "content-type": "application/json"}
        while True:
            if request["type"] == "extraction":
                response = requests.get(
                    f'{baseUrl}/documents/{request["id"]}', headers=headers)
                if response.status_code != 200:
                    throwError(response)
                responseBody = response.json()
                if "status" in responseBody and responseBody["status"] != "WAITING":
                    return responseBody
            else:
                response = requests.get(request["downloadLink"])
                if response.status_code == 200:
                    return response.json()
                if response.status_code != 404:
                    throwError(response)
            time.sleep(5)

    def generateExcel(self, extractions):
        headers = {"authorization": f'Bearer {self.apiKey}'}

        if type(extractions) not in (tuple, list):
            extractions = [extractions]
        url = baseUrl + "/generate_excel/" + \
            ",".join(map(lambda extraction: extraction["id"], extractions))
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        throwError(response)


def querystring(environment, documentName):
    query = {}
    if environment:
        query["environment"] = environment
    if documentName:
        query["documentName"] = documentName
    return f'?{urlencode(query)}'


def throwError(response):
    status = response.status_code
    if status == 400:
        raise Exception(f'Bad Request (400): {response.text}')
    if status == 401:
        raise Exception("Unauthorized (401), please check your API key")
    if status == 415:
        raise Exception(
            "Unsupported Media Type (415), please check your document format")
    if status == 429:
        # automatic retry?
        raise Exception("Too Many Requests (429)")
    if status == 500:
        raise Exception(f'Internal Server Error (500): {response.text}')
    raise Exception(f'Got unknown HTTP status code {status}: {response.text}')


def isExtractionResponse(response):
    return "id" in response


def isExtractionUrlResponse(response):
    return "id" in response and "upload_url" in response


def isClassificationResponse(response):
    return "id" in response and "download_link" in response
