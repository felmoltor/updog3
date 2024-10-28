![Version 1.0](http://img.shields.io/badge/version-v1.1-green.svg)
![Python 3.12](http://img.shields.io/badge/python-3.12-blue.svg)
[![MIT License](http://img.shields.io/badge/license-MIT%20License-blue.svg)](./LICENSE)
[![felmoltor Twitter](http://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Follow+Felmoltor)](https://twitter.com/felmoltor)
[![sc0tfree Twitter](http://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Follow+Sc0tfree)](https://twitter.com/sc0tfree)


Updog2 is a for of Sc0tfree's Updog tool, which was a replacement for Python's `SimpleHTTPServer`. 
It allows uploading and downloading via HTTP/S, can set ad hoc and custom SSL certificates, use HTTP basic auth, and disable upload and download functionality when required.

<p align="center">
  <img src="updog2/static/images/updog2.png" alt="Updog2 Logo" width=150px/>
</p>


### Installation from source with pipenv

You need Python3.12.

```bash
git clone https://github.com/felmoltor/updog2
cd updog
pipenv install .
pipenv shell
which updog # to verify you are using the module installed with pipenv
updog --version
```

After this, you do not use `python setup.py install` as it has some errors that prevents copying the Flask templates and the server will not run. Use `pipenv install .` instead to install updog as a module.

## Docker

Install using pip:

`pip3 install updog2`


## Usage

`updog2 [-d DIRECTORY] [-p PORT] [--password PASSWORD] [--ssl] [--cert certificate.pem key.pem] [--fullpath] [--upload [only, enabled, disabled]]`

| Argument                            | Description                                      |
|-------------------------------------|--------------------------------------------------| 
| -d DIRECTORY, --directory DIRECTORY | Root directory [Default=.]                       | 
| -p PORT, --port PORT                | Port to serve [Default=9090]                     |
| --password PASSWORD                 | Use a password to access the page. (No username) |
| --ssl                               | Enable transport encryption via SSL              |
| --cert                              | Provide your own certificate and key             |
| --upload                            | Select: only, enabled, disabled                  |
| --fullpath                          | Display the full path of the folder uploading to |
| --version                           | Show version                                     |
| -h, --help                          | Show help                                        |

## Examples

**Serve from your current directory:**

`updog2`

**Serve from another directory:**

`updog2 -d /another/directory`

**Serve from port 1234:**

`updog2 -p 1234`

**Password protect the page:**

`updog2 --password examplePassword123!`

*Please note*: updog uses HTTP basic authentication.
To login, you should leave the username blank and just
enter the password in the password field.

**Use an SSL connection:**

`updog2 --ssl`

**Use an SSL connection with custom certificates:**

`updog2 --ssl --cert certificate.pem key.pem`

For a LetsEncrypt certificate, the files will be in /etc/letsencrypt/live/[domain]/cert.pem and /etc/letsencrypt/live/[domain]/privatekey.pem (careful, these are just links to ../../archive/ folder, so if you are copying those to another folder, ensure you copy the archive files.)

**Modify upload/download functionality:**

To allow only uploads:

`updog2 --upload only`

To allow only downloads:
`updog2 --upload disabled`

To allow uploads and downloads:
`updog2 --upload enabled` (This is the default mode)


## Thanks

To Sc0tfree, the original writer of Updog (https://github.com/sc0tfree/updog).
A special thank you to [Nicholas Smith](http://nixmith.com) for designing the original updog logo. The Updog2 logo is a poor attempt at updating it, sorry, Nicholas, I am not a designer 😭
