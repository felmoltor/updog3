![Version 1.0](http://img.shields.io/badge/version-v1.1-green.svg)
![Python 3.12](http://img.shields.io/badge/python-3.12-blue.svg)
[![MIT License](http://img.shields.io/badge/license-MIT%20License-blue.svg)](./LICENSE)
[![felmoltor Twitter](http://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Follow+Felmoltor)](https://twitter.com/felmoltor)
[![sc0tfree Twitter](http://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Follow+Sc0tfree)](https://twitter.com/sc0tfree)


updog3 is a for of Sc0tfree's Updog tool, which was a replacement for Python's `SimpleHTTPServer`. 
It allows uploading and downloading via HTTP/S, can set ad hoc and custom SSL certificates, use HTTP basic auth, and disable upload and download functionality when required.

<p align="center">
  <img src="updog3/static/images/Updog3.png" alt="updog3 Logo" width=150px/>
</p>


### Installation from source with pipenv

You need Python3.12.

```bash
git clone https://github.com/felmoltor/updog3
cd updog3
pipenv install .
pipenv shell
which updog3 # to verify you are using the module installed with pipenv
updog --version
```

After this, you do not use `python setup.py install` as it has some errors that prevents copying the Flask templates and the server will not run. Use `pipenv install .` instead to install updog as a module.

## Docker

Use docker:

```bash
# If you are not logged in:
docker login ghcr.io -u <youruser> 
# Pull latest
docker pull ghcr.io/felmoltor/updog3:latest
# If you are using Mac: 
# docker pull --platform linux/amd64 ghcr.io/felmoltor/updog3:latest
# Tag it as updog3:
docker tag ghcr.io/felmoltor/updog3:latest updog3
docker run updog3 -h

# Run from docker mapping port 443 and your domain's certificates
docker run  -v $(pwd)/transfer:/transfer -v /etc/letsencrypt/archive/yourdomain.com/:/certs/  updog3 -p 443 --ssl --cert /certs/cert1.pem /certs/privkey1.pem -d /transfer
```

## Usage

`updog3 [-d DIRECTORY] [-p PORT] [--password PASSWORD] [--ssl] [--cert certificate.pem key.pem] [--fullpath] [--upload [only, enabled, disabled]]`

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

`updog3`

**Serve from another directory:**

`updog3 -d /transfer`

**Serve from port 1234:**

`updog3 -p 1234`

**Password protect the page:**

`updog3 --password examplePassword123!`

*Please note*: updog uses HTTP basic authentication.
To login, you should leave the username blank and just
enter the password in the password field.

**Use an SSL connection:**

`updog3 --ssl`

**Use an SSL connection with custom certificates:**

`updog3 --ssl --cert /certs/certificate.pem /certs/key.pem`

For a LetsEncrypt certificate, the files will be in /etc/letsencrypt/live/[domain]/cert.pem and /etc/letsencrypt/live/[domain]/privatekey.pem (careful, these are just links to ../../archive/ folder, so if you are copying those to another folder, ensure you copy the archive files.)

**Modify upload/download functionality:**

To allow only uploads:

`updog3 --upload only`

To allow only downloads:
`updog3 --upload disabled`

To allow uploads and downloads:
`updog3 --upload enabled` (This is the default mode)


## Thanks

To Sc0tfree, the original writer of Updog (https://github.com/sc0tfree/updog).

A special thank you to [Nicholas Smith](http://nixmith.com) for designing the original updog logo. The updog3 logo is a poor attempt at updating it, sorry, Nicholas, I am not a designer 😭
