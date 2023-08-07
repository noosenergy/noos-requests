[![CircleCI](https://circleci.com/gh/noosenergy/noos-requests.svg?style=svg&circle-token=c08ede3341e1b8a80f87df87959f849fe40d148f)](https://circleci.com/gh/noosenergy/noos-requests)

# Noos Energy Request Toolkit

This is a simple, yet useful toolkit that supports you in writing Python clients to microservices-style apps.

## Installation

Package available from the [PyPi repository](https://pypi.org/project/noos-pyk/):

```sh
pip install noos-pyk
```

## Usage as a library

The project currently houses a boilerplate to build Python HTTP and WebSocket clients to web services.

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

```sh
brew install poetry
```

This project is shipped with a Makefile, which is ready to do basic common tasks.

```shell
~$ make
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
