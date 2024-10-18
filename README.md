![Version 1.4](http://img.shields.io/badge/version-v1.4-green.svg)
![Python 3.8](http://img.shields.io/badge/python-3.8-blue.svg)
[![MIT License](http://img.shields.io/badge/license-MIT%20License-blue.svg)](https://github.com/sc0tfree/updog/blob/master/LICENSE)
[![sc0tfree Twitter](http://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Follow)](https://twitter.com/sc0tfree)

<p>
  <img src="https://sc0tfree.squarespace.com/s/updog.png" width=85px alt="updog"/>
</p>

Updog is a replacement for Python's `SimpleHTTPServer`. 
It allows uploading and downloading via HTTP/S, 
can set ad hoc SSL certificates and use HTTP basic auth.

<p align="center">
  <img src="https://sc0tfree.squarespace.com/s/updog-screenshot.png" alt="Updog screenshot"/>
</p>

## Installation

Install using pip:

`pip3 install updog`

### Install from source with pipenv

```bash
cd sc0tfree-updog
pipenv install 
pipenv shell
pipenv install .
```

After this, you do not use `python setup.py install` as it has some errors that prevents copying the Flask templates and the server will not run. Use `pipenv install .` instead to install updog as a module.

## Usage

`updog [-d DIRECTORY] [-p PORT] [--password PASSWORD] [--ssl] [--cert certificate.cer certificate.key]`

| Argument                            | Description                                      |
|-------------------------------------|--------------------------------------------------| 
| -d DIRECTORY, --directory DIRECTORY | Root directory [Default=.]                       | 
| -p PORT, --port PORT                | Port to serve [Default=9090]                     |
| --password PASSWORD                 | Use a password to access the page. (No username) |
| --ssl                               | Enable transport encryption via SSL              |
| --cert                              | Provide your own certificate and key             |
| --version                           | Show version                                     |
| -h, --help                          | Show help                                        |

## Examples

**Serve from your current directory:**

`updog`

**Serve from another directory:**

`updog -d /another/directory`

**Serve from port 1234:**

`updog -p 1234`

**Password protect the page:**

`updog --password examplePassword123!`

*Please note*: updog uses HTTP basic authentication.
To login, you should leave the username blank and just
enter the password in the password field.

**Use an SSL connection:**

`updog --ssl`

**Use an SSL connection with bespoke certificates:**

`updog --ssl --cert certificate.pem key.pem`

For a LetsEncrypt certificate, the files will be in /etc/letsencrypt/live/[domain]/cert.pem and /etc/letsencrypt/live/[domain]/privatekey.pem (careful, these are just links to ../../archive/ folder, so if you are copying those to another folder, ensure you copy the archive files.)

## Thanks

A special thank you to [Nicholas Smith](http://nixmith.com) for
designing the updog logo.
