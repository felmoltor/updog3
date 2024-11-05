import os
from os.path import basename
import signal
import argparse
import ipaddress
import socket
import zipfile
import tempfile

from flask import Flask, render_template, send_file, redirect, request, send_from_directory, url_for, abort, flash
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.serving import run_simple

from updog3.utils.path import is_valid_subpath, is_valid_upload_path, get_parent_directory, process_files
from updog3.utils.output import error, info, warn, success
from updog3 import version as VERSION

def validate_ip(ip):
    try:
        # Check if the IP address is valid
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return False, "Invalid IP address format."

    # Attempt to resolve the IP to verify it exists on the network
    try:
        socket.gethostbyaddr(str(ip_obj))
        return True, "IP address is reachable."
    except socket.herror:
        return False, "IP address is unreachable or does not exist."

def read_write_directory(directory):
    if os.path.exists(directory):
        if os.access(directory, os.W_OK and os.R_OK):
            return directory
        else:
            error('The output is not readable and/or writable')
    else:
        error('The specified directory does not exist')


def parse_arguments():
    parser = argparse.ArgumentParser(prog='updog')
    cwd = os.getcwd()
    parser.add_argument('-d', '--directory', metavar='DIRECTORY', type=read_write_directory, default=cwd,
                        help='Root directory\n'
                             '[Default=.]')
    parser.add_argument('-p', '--port', type=int, default=9090,
                        help='Port to serve [Default=9090]')
    parser.add_argument('--password', type=str, default='', help='Use a password to access the page. (No username)')
    parser.add_argument('-i', '--interface', type=str, default='0.0.0.0', help='IP address of the interface to listen')
    parser.add_argument('--ssl', action='store_true', help='Use an encrypted connection')
    parser.add_argument('-D','--createdir', action='store_true', help='Allow directory creation from the web interface',default=False)
    parser.add_argument('--fullpath', action='store_true', help='Display the full path of the folder uploading to',default=False)
    parser.add_argument('--upload', choices=['only','enabled','disabled'], help='Upload mode: only, enabled, disabled (default: enabled)', default='enabled')
    parser.add_argument('--version', action='version', version='%(prog)s v'+VERSION)
    parser.add_argument(
        '--cert', '-C',
        nargs=2,
        metavar=('CERT', 'KEY'),
        help="Provide your own certificate and key for TLS. Usage: --cert cert.pem key.pem"
    )

    args = parser.parse_args()

    # Check the interface exists
    valid, err = validate_ip(args.interface)
    if (not valid):
        print(f"Error. Interface {args.interface} - {err}. Using 0.0.0.0 instead.")
        args.interface = '0.0.0.0'

    # Normalize the path
    args.directory = os.path.abspath(args.directory)

    return args

import os

def get_folder_size(folder_path, size_limit_mb=100):
    size_limit = size_limit_mb * 1024 * 1024  # Convert MB to bytes
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
                # Break the loop if the size exceeds the limit
                if total_size >= size_limit:
                    return total_size
    return total_size

def create_zip_archive(folder_path):
    # Create a temporary file for the ZIP archive
    zip_path = tempfile.mktemp(suffix='.zip')  # Create a temp file path ending in .zip
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through the folder and add each file to the zip
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Add the file to the zip, with a path relative to `folder_path`
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))
    return zip_path

def main():
    args = parse_arguments()

    app = Flask(__name__)
    app.secret_key = b'LIknd8K44Q12`ks-0Iyh2[?hauid-dkLassLh]'

    auth = HTTPBasicAuth()

    global base_directory
    base_directory = args.directory

    # Deal with Favicon requests
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

    ############################################
    # File Browsing and Download Functionality #
    ############################################
    @app.route('/download-zip/<path:path>')
    @auth.login_required
    def download_zip(path):
        requested_path = os.path.join(base_directory, path) if path else base_directory
        if os.path.isdir(requested_path):
            zip_path = create_zip_archive(requested_path)  # Your function to create the ZIP file
            return send_file(zip_path, as_attachment=True)
        else:
            abort(403)

    @app.route('/', defaults={'path': None})
    @app.route('/<path:path>')
    @auth.login_required
    def home(path):
        big_folder_size_mb = 10
        # Ensure `displayed_path` and `requested_path` are initialized
        displayed_path = base_directory if path is None else path
        requested_path = os.path.join(base_directory, path) if path else base_directory

        # If path is provided and valid, normalize and verify existence
        if path and is_valid_subpath(path, base_directory):
            path = os.path.normpath(path)
            requested_path = os.path.join(base_directory, path)

            if os.path.exists(requested_path):
                # Check if the requested path is a directory
                if os.path.isdir(requested_path):
                    try:
                        # Process files in directory
                        directory_files = process_files(os.scandir(requested_path), base_directory)
                        displayed_path = requested_path if args.fullpath else path
                    
                    except PermissionError:
                        abort(403, 'Read Permission Denied: ' + requested_path)
                        
                    back_directory = get_parent_directory(requested_path, base_directory)
                    is_subdirectory = True

                    # Handle zip download prompt
                    if request.args.get('downloadzip') is not None:
                        show_download_prompt = False
                        download_folder=True
                        folder_size = get_folder_size(requested_path)
                        if (folder_size >= (big_folder_size_mb * 1024**2)):
                            show_download_prompt = True

                        # Render template with prompt
                        return render_template(
                            'home.html',
                            files=directory_files,
                            back=back_directory,
                            directory=requested_path,
                            displayed_directory=displayed_path,
                            is_subdirectory=is_subdirectory,
                            upload=args.upload,
                            version=VERSION,
                            download_folder=download_folder,
                            show_download_prompt=show_download_prompt,
                            folder_size=folder_size,
                            folder_size_mb=round((folder_size/1024**2),2),
                            createdir=args.createdir
                        )
                    else:
                        # User is navigating to a subdirectory
                        # Render template with prompt
                        return render_template(
                            'home.html',
                            files=directory_files,
                            back=back_directory,
                            directory=requested_path,
                            displayed_directory=displayed_path,
                            is_subdirectory=is_subdirectory,
                            upload=args.upload,
                            version=VERSION,
                            createdir=args.createdir
                        )

                # Handle file download
                elif os.path.isfile(requested_path):
                    send_as_attachment = request.args.get('view') is None
                    mimetype = 'text/plain' if os.path.splitext(requested_path)[1] == '' else None
                    if args.upload != 'only':
                        return send_file(requested_path, mimetype=mimetype, as_attachment=send_as_attachment)
                    else:
                        abort(403, 'Only Uploads Available')

            else:
                # Redirect to root if path does not exist
                return redirect('/')

        # Default behavior when accessing the root or invalid path
        try:
            directory_files = process_files(os.scandir(base_directory), base_directory)
        except PermissionError:
            abort(403, 'Read Permission Denied: ' + base_directory)

        # Render root directory template
        return render_template(
            'home.html',
            files=directory_files,
            back='',
            directory=base_directory,
            displayed_directory='[ROOT]' if path is None else path,
            is_subdirectory=False,
            upload=args.upload,
            version=VERSION,
            createdir=args.createdir
        )

    ##################################
    # Create Directory Functionality #
    ##################################
    @app.route('/createdir', methods=['POST'])
    @auth.login_required
    def createdir():
        if request.method == 'POST':
            path = request.form.get('path')
            dirname = request.form.get('dirname')

            if not dirname:
                flash("Please enter a directory name.", "error")
                return redirect(request.referrer)
            
            secure_dirname = secure_filename(dirname)
            secure_path = os.path.join(path, secure_dirname)
            full_path = os.path.join(base_directory, secure_path)

            # Prevent directory creation outside of base directory
            if not is_valid_subpath(full_path, base_directory):
                flash(f"Cannot create directory {dirname}: Invalid path.", "danger")
                return redirect(request.referrer)
            
            try:
                os.mkdir(full_path)
                # flash(f"Directory '{dirname}' created successfully.", "success")
            except FileExistsError:
                flash(f"Directory '{dirname}' already exists.", "danger")
            except PermissionError:
                flash(f"Permission denied to create directory '{dirname}'.", "danger")
            except Exception as e:
                flash(f"Failed to create directory '{dirname}': {str(e)}", "danger")

            return redirect(request.referrer)
        else:
            return abort(403)



    #############################
    # File Upload Functionality #
    #############################
    @app.route('/upload', methods=['POST'])
    @auth.login_required
    def upload():
        if request.method == 'POST':
            if  args.upload != 'disallowed':

                # No file part - needs to check before accessing the files['file']
                if 'file' not in request.files:
                    return redirect(request.referrer)

                path = request.form['path']
                # Prevent file upload to paths outside of base directory
                if not is_valid_upload_path(path, base_directory):
                    return redirect(request.referrer)

                for file in request.files.getlist('file'):

                    # No filename attached
                    if file.filename == '':
                        return redirect(request.referrer)

                    # Assuming all is good, process and save out the file
                    # TODO:
                    # - Add support for overwriting
                    if file:
                        filename = secure_filename(file.filename)
                        full_path = os.path.join(path, filename)
                        try:
                            file.save(full_path)
                        except PermissionError:
                            abort(403, 'Write Permission Denied: ' + full_path)

                return redirect(request.referrer)
            else:
                # Uploads are disallowed
                # TODO: Show some message about uploads disallowed
                return redirect(request.referrer)


    # Password functionality is without username
    users = {
        '': generate_password_hash(args.password)
    }

    @auth.verify_password
    def verify_password(username, password):
        if args.password:
            if username in users:
                return check_password_hash(users.get(username), password)
            return False
        else:
            return True

    # Inform user before server goes up
    success('Serving {}...'.format(args.directory, args.port))

    def handler(signal, frame):
        print()
        error('Exiting!')
    signal.signal(signal.SIGINT, handler)

    ssl_context = None
    # Check if cert argument is passed
    if args.ssl:
        # Use own certs if they are provided
        if args.cert:
            cert_path, key_path = args.cert
            ssl_context = (cert_path, key_path)
        else:
            # Default to 'adhoc' if no cert is provided
            ssl_context = 'adhoc'

    run_simple(args.interface, int(args.port), app, ssl_context=ssl_context)


if __name__ == '__main__':
    main()
