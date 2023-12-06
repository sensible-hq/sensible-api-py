# Sensible Python SDK

The open-source Sensible Python SDK offers convenient access to the [Sensible API](https://docs.sensible.so/reference/choosing-an-endpoint). Use the Sensible Python SDK to:

- [Extract](#extract-document-data): Extract structured data from your custom documents. Configure the extractions for a set of similar documents, or *document type*, in the Sensible app or Sensible API, then you run extractions for documents of the type with this SDK.
- [Classify](#classify): Classify documents by the types you define, for example, bank statements or tax forms. Use classification to determine which documents to extract prior to calling a Sensible extraction endpoint, or route each document in a system of record.

## Documentation

- For extraction and classification response schemas, see [Sensible API](https://docs.sensible.so/reference/choosing-an-endpoint).
- For configuring document extractions, see [SenseML reference](https://docs.sensible.so/docs/senseml-reference-introduction).


## Install

In an environment in which you've installed Python, create a directory for a test project, open a command prompt in the directory, and install the dependencies:  

```shell
pip install sensibleapi
```

To import Sensible and other dependencies to your project,  create an `index.py` file in your test project, and add the following lines to the file:

```python
from sensibleapi import SensibleSDK
```

## Initialize

Get an account at [sensible.so](https://app.sensible.so/register) if you don't have one already.

To initialize the dependency, paste the following code into your `index.py` file and replace `YOUR_API_KEY` with your [API key](https://app.sensible.so/account/):

```python
sensible = SensibleSDK(apiKey)
```

**Note** In production ensure you secure your API key, for example as a GitHub secret.

## Extract document data

#### Option 1: document URL

To extract data from a sample document at a URL:

1. Paste the following code into your `index.py` file:

```python
request = sensible.extract(
    url="https://github.com/sensible-hq/sensible-docs/raw/main/readme-sync/assets/v0/pdfs/contract.pdf",
    documentType="sensible_instruct_basics",
    environment="development" # see Python SDK reference for full list of configuration options
    )

results = sensible.waitFor(request) # waitFor is optional if you configure a webhook
print(results) # see Python SDK reference to convert results from JSON to Excel
```

2. In a command prompt in the same directory as your `index.py` file, run the code with the following command:

```shell
python index.py
```

The code extracts data from an example document (`contract.pdf`) using an example document type (`sensible_instruct_basics`) and an example extraction configuration. 

#### Option 2: local file

To extract from a local file: 

1. Download the following example file and save it in the same directory as your `index.py` file: 

| Example document | [Download link](https://github.com/sensible-hq/sensible-docs/raw/main/readme-sync/assets/v0/pdfs/contract.pdf) |
| ---------------- | ------------------------------------------------------------ |

2. Paste the following code into your `index.py` file, then run it according to the steps in the previous option:


```python
request = sensible.extract(
      path="./contract.pdf",
      documentType="sensible_instruct_basics",
    )
results = sensible.waitFor(request) # waitFor is optional if you configure a webhook
print(results) # see Python SDK reference to convert results from JSON to Excel
```

This code uploads your local file to a Sensible-hosted URL and extracts data from an example document (`contract.pdf`) using an example document type (`sensible_instruct_basics`) and an example extraction configuration. 

#### Check results

The following excerpt of the results shows the extracted document text in the `parsed_document` object:

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

For more information about the response body schema, see [Extract data from a document](https://docs.sensible.so/reference/extract-data-from-a-document) and expand the 200 responses in the middle pane and the right pane to see the model and an example, respectively.

#### Optional: understand extraction

Navigate to https://app.sensible.so/editor/instruct/?d=sensible_instruct_basics&c=contract&g=contract to see how the extraction you just ran works in the Sensible app. You can add more fields to the extraction configuration to extract more data:

![Click to enlarge](https://raw.githubusercontent.com/sensible-hq/sensible-docs/main/readme-sync/assets/v0/images/final/sdk_node_1.png)

#### Complete code example

See the following code for a complete example of how to use the SDK for document extraction in your own app.

```python
from sensibleapi import SensibleSDK

sensible = SensibleSDK(YOUR_API_KEY)

request = sensible.extract(
      path="./contract.pdf",
      documentType="sensible_instruct_basics",
      environment="development" # see Python SDK reference for configuration options
    )
results = sensible.waitFor(request) # waitFor is optional if you configure  a webhook
print(results) # see Python SDK reference to convert results from JSON to Excel
```

## Classify

You can classify a document by its similarity to each document type you define in your Sensible account. For example, if you define a [bank statements](https://github.com/sensible-hq/sensible-configuration-library/tree/main/bank_statements) type and a [tax_forms](https://github.com/sensible-hq/sensible-configuration-library/tree/main/tax_forms) type in your account, you can classify 1040 forms, 1099 forms, Bank of America statements, Chase statements, and other documents, into those two types.

See the following code example for classifying a document.

```python
request = sensible.classify(path="./boa_sample.pdf") 
results = sensible.waitFor(request)
```

To classify an example document, take the following steps:

1. Follow the steps in [Out-of-the-box extractions](https://docs.sensible.so/docs/library-quickstart) to add support for bank statements to your account.

2. Follow the steps in the preceding sections to install and initialize the SDK.

3. Download the following example file and save it in the same directory as your `index.py` file: 

| Example document | [Download link](https://github.com/sensible-hq/sensible-configuration-library/raw/main/bank_statements/bank_of_america/boa_sample.pdf) |
| ---------------- | ------------------------------------------------------------ |

4. Paste the preceding code into your `index.py` file. Ensure you replaced`YOUR_API_KEY` with your [API key]((https://app.sensible.so/account/) and `YOUR_DOCUMENT.pdf` with `boa_sample.pdf`. See the following code example to check your code completeness.

5. In a command prompt in the same directory as your `index.py` file, run the code with the following command:

```shell
python index.py
```

#### Check results

The following excerpt of the results shows document classification:

```json
{
  "document_type": {
    "id": "22666f4f-b8d6-4cb5-ad52-d00996989729",
    "name": "bank_statements",
    "score": 0.8922476745112722
  },
  "reference_documents": [
    {
      "id": "c82ac28e-7725-4e42-b77c-e74551684caa",
      "name": "boa_sample",
      "score": 0.9999980536061833
    },
    {
      "id": "f80424a0-58f8-40e7-814a-eb49b199221e",
      "name": "wells_fargo_checking_sample",
      "score": 0.8946129923339182
    },
    {
      "id": "cf17daf8-7e8b-4b44-bc4b-7cdd6518d963",
      "name": "chase_consolidated_balance_summary_sample",
      "score": 0.8677569417649393
    }
  ]
}
```

#### Complete code example

Here's a complete example of how to use the SDK for document classification in your own app:

```python
from sensibleapi import SensibleSDK

sensible = SensibleSDK(YOUR_API_KEY)
request = sensible.classify(path="./boa_sample.pdf") 
results = sensible.waitFor(request)
print(results)
```
