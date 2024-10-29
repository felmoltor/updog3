import os
from os.path import basename
import signal
import argparse

from flask import Flask, render_template, send_file, redirect, request, send_from_directory, url_for, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.serving import run_simple

from updog3.utils.path import is_valid_subpath, is_valid_upload_path, get_parent_directory, process_files
from updog3.utils.output import error, info, warn, success
from updog3 import version as VERSION


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
    parser.add_argument('--ssl', action='store_true', help='Use an encrypted connection')
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

    # Normalize the path
    args.directory = os.path.abspath(args.directory)

    return args


def main():
    args = parse_arguments()

    app = Flask(__name__)
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
    @app.route('/', defaults={'path': None})
    @app.route('/<path:path>')
    @auth.login_required
    def home(path):
        # If there is a path parameter and it is valid
        displayed_path = None
        if path and is_valid_subpath(path, base_directory):
            # Take off the trailing '/'
            path = os.path.normpath(path)
            requested_path = os.path.join(base_directory, path)
            if (args.fullpath):
                displayed_path = requested_path
            else:
                displayed_path = path

            # If directory
            if os.path.isdir(requested_path):
                back = get_parent_directory(requested_path, base_directory)
                is_subdirectory = True

            # If file
            elif os.path.isfile(requested_path):

                # Check if the view flag is set
                if request.args.get('view') is None:
                    send_as_attachment = True
                else:
                    send_as_attachment = False

                # Check if file extension
                (filename, extension) = os.path.splitext(requested_path)
                if extension == '':
                    mimetype = 'text/plain'
                else:
                    mimetype = None

                try:
                    if (args.upload != 'only'):
                        return send_file(requested_path, mimetype=mimetype, as_attachment=send_as_attachment)
                    else:
                        abort(403, 'Only Uploads Available')
                except PermissionError:
                    abort(403, 'Read Permission Denied: ' + path)

        else:
            # update displayed path:
            if (args.fullpath):
                displayed_path = base_directory
            else:
                displayed_path = path if path is not None else "[ROOT]"
            # Root home configuration
            is_subdirectory = False
            requested_path = base_directory
            back = ''

        if os.path.exists(requested_path):
            # Read the files
            try:
                directory_files = process_files(os.scandir(requested_path), base_directory)
            except PermissionError:
                abort(403, 'Read Permission Denied: ' + requested_path)

            print("Upload: "+ args.upload)
            return render_template('home.html', 
                                   files=directory_files, 
                                   back=back,
                                   directory=requested_path, 
                                   displayed_directory=displayed_path, 
                                   is_subdirectory=is_subdirectory, 
                                   upload=args.upload,
                                   version=VERSION)
        else:
            return redirect('/')

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

    run_simple("0.0.0.0", int(args.port), app, ssl_context=ssl_context)


if __name__ == '__main__':
    main()
