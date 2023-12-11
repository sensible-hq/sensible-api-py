import os
from setuptools import setup, find_packages

with open('./README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sensibleapi',
    version='0.0.10',
    author='Sensible Technologies, Inc',
    author_email='hello@sensible.so',
    description='Python SDK for Sensible, the developer-first platform for extracting structured data from documents so that you can build document-automation features into your SaaS products',
    packages=find_packages(),
    install_requires=['requests'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sensible-hq/sensible-api-py"
)

