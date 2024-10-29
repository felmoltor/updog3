from setuptools import setup
from os import path
import updog3


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='updog3',
    version=updog3.version,
    url='https://github.com/felmoltor/updog3',
    # GitHub releases in format "updog-X.Y"
    download_url = 'https://github.com/felmoltor/updog3/archive/updog-' + updog3.version + '.tar.gz',
    license='MIT',
    author='felmoltor',
    author_email='me@felipemolina.com',
    description='updog3 is a fork of Sc0tfree\'s Updog tool, which was a replacement for Python\'s SimpleHTTPServer. '
                'It allows uploading and downloading via HTTP/S, can set ad hoc and custom SSL certificates, use HTTP basic auth, and disable upload and download functionality when required',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='HTTP server SimpleHTTPServer directory',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications :: File Sharing',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Security'
    ],
    packages=['updog3', 'updog3.utils'],
    entry_points={
        'console_scripts': 'updog3 = updog3.__main__:main'
    },
    include_package_data=True,
    install_requires=[
        'colorama',
        'flask',
        'flask_httpauth',
        'werkzeug',
        'pyopenssl'
    ],
)
