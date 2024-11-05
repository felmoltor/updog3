import os

# Get the absolute path to the version file
version = '0.0'
root_dir = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(root_dir, 'version'), 'r') as f:
    version = f.read().strip()

base_directory = ''