# Sensible Python SDK

Welcome! Sensible is a developer-first platform for extracting structured data from documents, for example, business forms in PDF format. use Sensible to build document-automation features into your SaaS products. Sensible is highly configurable: you can get simple data [in minutes](https://docs.sensible.so/docs/getting-started-ai) by leveraging GPT-4 and other large-language models (LLMs), or you can tackle complex and idiosyncratic document formatting with Sensible's powerful [layout-based document primitives](https://docs.sensible.so/docs/getting-started).

![Click to enlarge](https://raw.githubusercontent.com/sensible-hq/sensible-docs/main/readme-sync/assets/v0/images/final/intro_SDK_2.png)

This open-source Sensible SDK offers convenient access to the [Sensible API](https://docs.sensible.so/reference/choosing-an-endpoint). Use this SDK to:

- [Extract](#usage-extract-document-data): Extract structured data from your custom documents. Configure the extractions for a set of similar documents, or *document type*, in the Sensible app or Sensible API, then run extractions for documents of the type with this SDK.
- [Classify](#usage-classify-documents-by-type): Classify documents by the types you define, for example, bank statements or tax forms. Use classification to determine which documents to extract prior to calling a Sensible extraction endpoint, or route each document in a system of record.

## Documentation

- For extraction and classification response schemas, see the [Sensible API reference](https://docs.sensible.so/reference/choosing-an-endpoint).
- For configuring document extractions, see [SenseML reference](https://docs.sensible.so/docs/senseml-reference-introduction).

## Versions

- The latest version of this SDK is v0.
- The latest version of the Sensible API is v0.

## Python support

- This SDK supports all non end-of-life versions of Python.

## Install

In an environment in which you've installed Python, create a directory for a test project, open a command prompt in the directory, and install the dependencies:

```shell
pip install sensibleapi
```

To import Sensible to your project,  create an `index.py` file in your test project, and add the following lines to the file:




```python
from sensibleapi import SensibleSDK
```

## Initialize

Get an account at [sensible.so](https://app.sensible.so/register) if you don't have one already.

To initialize the SDK, paste the following code into your `index.py` file and replace `YOUR_API_KEY` with your [API key](https://app.sensible.so/account/):

```python
sensible = SensibleSDK("YOUR_API_KEY")
```

**Note:** Ensure you secure your API key in production, for example as a GitHub secret.

## Quickstart<a id="quickstart"></a>

To extract data from a sample document at a URL:

1. Install the Sensible SDK using the steps in the previous section.
2. Paste the following code into an empty `index.py` file:

```python
from sensibleapi import SensibleSDK

sensible = SensibleSDK("YOUR_API_KEY")  # replace with your API key
request = sensible.extract(
    url="https://github.com/sensible-hq/sensible-docs/raw/main/readme-sync/assets/v0/pdfs/contract.pdf",
    document_type="sensible_instruct_basics",
    environment="development"
)
results = sensible.wait_for(request)  # polls every 5 seconds. Optional if you configure a webhook
print(results)
```

2. Replace `YOUR_API_KEY` with your [API key](https://app.sensible.so/account/).
3. In a command prompt in the same directory as your `index.py` file, run the code with the following command:

```shell
python index.py
```

The code extracts data from an example document (`contract.pdf`) using an example document type (`sensible_instruct_basics`) and an example extraction configuration.

#### Results

You should see the following extracted document text in the `parsed_document` object in the logged response:

```json
{
  "purchase_price": {
    "source": "$400,000",
    "value": 400000,
    "unit": "$",
    "type": "currency"
  },
  "street_address": {
    "value": "1234 ABC COURT City of SALT LAKE CITY County of Salt Lake -\nState of Utah, Zip 84108",
    "type": "address"
  }
}
```

#### Optional: Understand extraction

Navigate to the example in the [SenseML editor](https://app.sensible.so/editor/?d=sensible_instruct_basics&c=contract&g=contract) to see how the extraction you just ran works in the Sensible app. You can add more fields to the left pane to extract more data:

![Click to enlarge](https://raw.githubusercontent.com/sensible-hq/sensible-docs/main/readme-sync/assets/v0/images/final/sdk_node_1.png)

## Usage: Extract document data<a id="usage-extract-document-data"></a>

You can use this SDK to extract data from a document, as specified by the extraction configurations and document types defined in your Sensible account.

### Overview

See the following steps for an overview of the SDK's workflow for document data extraction:

1. Instantiate an SDK object with `SensibleSDK()`.
2. Request a document extraction with `sensible.extract()`. Use the following required parameters:
   1.  **(required)** Specify the document from which to extract data using the `url`, `path`, or `file` parameter.
   2.  **(required)** Specify the user-defined document type or types using the `document_type` or `document_types` parameter.
3. Wait for the results. Use `sensible.wait_for()`, or use a webhook.
4. Optionally convert extractions to an Excel file with `generate_excel()`.
5. Consume the data.

### Extraction configuration

 You can configure options for document data extraction:

```python
request = sensible.extract(
    path="./1040_john_doe.pdf",
    document_type="tax_forms",
    configuration_name="1040_2021",
    environment="development",
    webhook={
        "url": "YOUR_WEBHOOK_URL",
        "payload": "additional info, for example, a UUID for verification",
    }
)
```

See the following table for information about configuration options:

| key               | value                                                      | description                                                  |
| ----------------- | ---------------------------------------------------------- | ------------------------------------------------------------ |
| path              | string                                                     | The path to the document you want to extract from. For more information about supported file size and types, see  [Supported file types](https://docs.sensible.so/docs/file-types). |
| file              | string                                                     | The non-encoded bytes of the document you want to extract from. |
| url               | string                                                     | The URL of the document you want to extract from. URL must:<br/>- respond to a GET request with the bytes of the document you want to extract data from <br/>- be either publicly accessible, or presigned with a security token as part of the URL path.<br/>To check if the URL meets these criteria, open the URL with a web browser. The browser must either render the document as a full-page view with no other data, or download the document, without prompting for authentication. |
| document_type      | string                                                     | Type of document to extract from. Create your custom type in the Sensible app (for example, `rate_confirmation`, `certificate_of_insurance`, or `home_inspection_report`), or use Sensible's library of out-of-the-box supported document types. |
| document_types     | array                                                      | Types of documents to extract from. Use this parameter to extract from multiple documents that are packaged into one file (a "portfolio").  This parameter specifies the document types contained in the portfolio. Sensible then segments the portfolio into documents using the specified document types (for example, 1099, w2, and bank_statement) and then runs extractions for each document. For more information, see [Multi-doc extraction](https://docs.sensible.so/docs/portfolio). |
| configuration_name | string                                                     | If specified, Sensible uses the specified config to extract data from the document instead of automatically choosing the configuration.<br/>If unspecified, Sensible automatically chooses the best-scoring extraction from the configs in the document type.<br/>Not applicable for portfolios. |
| document_name      | string                                                     | If you specify the file name of the document using this parameter, then Sensible returns the file name in the extraction response and populates the file name in the Sensible app's list of recent extractions. |
| environment       | `"production"` or `"development"`. default: `"production"` | If you specify `development`, Sensible extracts preferentially using config versions published to the development environment in the Sensible app. The extraction runs all configs in the doc type before picking the best fit. For each config, falls back to production version if no development version of the config exists. |
| webhook           | object                                                     | Specifies to return extraction results to the specified webhook URL as soon as they're complete, so you don't have to poll for results status. Sensible also calls this webhook on error.<br/> The webhook object has the following parameters:<br/>`url`:  string. Webhook destination. Sensible will POST to this URL when the extraction is complete.<br/>`payload`: string, number, boolean, object, or array. Information additional to the API response, for example a UUID for verification. |

### Extraction results

Get extraction results by using a webhook or calling the Wait For method.

For the schema for the results of an extraction request,  see [Extract data from a document](https://docs.sensible.so/reference/extract-data-from-a-document) and expand the 200 responses in the middle pane and the right pane to see the model and an example, respectively.

### Example: Extract from PDFs in directory and output an Excel file

See the following code for an example of how to use the SDK for document extraction in your app.

The example:

1. Filters a directory to find the PDF files.
2. Extracts data from the PDF files using the extraction configurations in a  `bank_statements` document type.
4. Logs the extracted document data JSON to the console.
3. Writes the extractions to an Excel file. The Generate Excel method takes an extraction or an array of extractions, and outputs an Excel file. For more information about the conversion process, see [SenseML to spreadsheet reference](https://docs.sensible.so/docs/excel-reference).


```python
import os
import json
import requests
from sensibleapi import SensibleSDK
from pathlib import Path

api_key = os.environ.get(API_KEY)
sensible = SensibleSDK(api_key)
dir_path = Path("ABSOLUTE_PATH_TO_DOCUMENTS_DIR")
pdf_files = [file for file in dir_path.glob("*.pdf")]

extractions = []
for pdf_file in pdf_files:
    file_path = dir_path / pdf_file
    extraction = sensible.extract(path=str(file_path), document_type="bank_statements")
    extractions.append(extraction)

results = [sensible.wait_for(extraction) for extraction in extractions]

print("Extractions:")
print(json.dumps(extractions, indent=2))

print("\nResults:")
print(json.dumps(results, indent=2))

excel = sensible.generate_excel(extractions)
print("Excel download URL:")
print(excel)

excel_file = requests.get(excel["url"])
output_path = dir_path / "output.xlsx"
with open(output_path, "wb") as f:
    f.write(excel_file.content)
print("Excel file:")
print(output_path)

```


## Usage: Classify documents by type<a id="usage-classify-documents-by-type"></a>

You can use this SDK to classify a document by type, as specified by the document types defined in your Sensible account. For more information, see [Classifying documents by type](https://docs.sensible.so/docs/classify).

### Overview

See the following steps for an overview of the SDK's workflow for document classification:

1. Instantiate an SDK object (`new SensibleSDK()`.

2. Request a document classification (`sensible.classify()`.  Specify the document to classify using the `path` or  `file` parameter.

3. Poll for the result (`sensible.wait_for()`.

4. Consume the data.


### Classification configuration

You can configure options for document data extraction:

```python
from sensibleapi import SensibleSDK

sensible = SensibleSDK(api_key="YOUR_API_KEY")  # Replace with your API key
request = sensible.classify(path="./boa_sample.pdf")
results = sensible.wait_for(request)
print(results)
```

See the following table for information about configuration options:

| key  | value  | description                                                  |
| ---- | ------ | ------------------------------------------------------------ |
| path | string | The path to the document you want to classify. For information about supported file size and types, see [Supported file types](https://docs.sensible.so/docs/file-types). |
| file | string | The non-encoded bytes of the document you want to classify.  |

### Classification results

Get results from this method by calling the Wait For method. For the schema for the results of a classification request , see [Classify document by type (sync)](https://docs.sensible.so/reference/classify-document-sync) and expand the 200 responses in the middle pane and the right pane to see the model and an example, respectively.
