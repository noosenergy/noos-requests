[![CircleCI](https://circleci.com/gh/noosenergy/noos-python-kit.svg?style=svg&circle-token=5c5370df196704b1e8a8dd7c6f2ec0731c154beb)](https://circleci.com/gh/noosenergy/noos-python-kit)

# Noos Energy Python Toolkit

This is a simple, yet useful toolkit that supports you in writing microservices-style Python apps.

## Installation

Package available from the [PyPi repository](https://pypi.org/project/noos-pyk/):

    $ pip install noos-pyk

## Usage as a library

The project currently houses a boilerplate to build Python clients for REST services.

As an example, to implement a Python client wrapping up HashiCorp's Terraform Cloud API,

```python
# Import the namespace within your project
from noos_pyk.clients import auth, json


# Define a bearer token authentication class
class TerraformAuth(auth.HTTPTokenAuth):
    default_header = "Authorization"
    default_value = "Bearer"


# Wireup all components for a JSON REST client
class TerraformClient(json.JSONClient, auth.AuthClient):
    default_base_url = "https://app.terraform.io/api/"
    default_content_type = "application/vnd.api+json"

    default_auth_class = TerraformAuth
```

## Development

On Mac OSX, make sure [poetry](https://python-poetry.org/) has been installed and pre-configured,

    $ brew install poetry

This project is shipped with a Makefile, which is ready to do basic common tasks.

```
$ make

help                           Display this auto-generated help message
update                         Lock and install build dependencies
clean                          Clean project from temp files / dirs
format                         Run auto-formatting linters
install                        Install build dependencies from lock file
lint                           Run python linters
test                           Run pytest with all tests
package                        Build project wheel distribution
release                        Publish wheel distribution to PyPi
```
