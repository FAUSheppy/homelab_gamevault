from flask import Flask, request, jsonify, send_file, abort
import os
import sys

from werkzeug.utils import secure_filename

app = Flask(__name__)

# Base directory constraint
BASE_DIR = os.path.abspath("./data")

@app.route('/get-path', methods=['GET'])
def get_path():

    # Get the "path" and "info" arguments from the URL
    path = request.args.get('path')

    # replace windows paths
    path = path.replace("\\", "/")
    if path.startswith("/"):
        path = path[1:]

    print("path", path, file=sys.stderr)

    info = request.args.get('info')

    if not path:
        return jsonify({"error": "Missing 'path' parameter."}), 400

    # Ensure the path is secure and resolve it within the BASE_DIR
    #secure_path = secure_filename(path)
    full_path = os.path.abspath(os.path.join(BASE_DIR, path))

    if not full_path.startswith(BASE_DIR):
        return jsonify({"error": "Access to the specified path is not allowed."}), 403

    print(full_path, file=sys.stderr)

    # Check if the path exists
    if not os.path.exists(full_path):
        print("missing file", file=sys.stderr)
        return jsonify({"contents": list()})

    # If the path is a directory, return a JSON list of its contents
    if os.path.isdir(full_path):
        contents = filter(lambda x: not x.startswith("."), os.listdir(full_path))
        return jsonify({"contents": list(contents)})

    # If the path is a file
    if os.path.isfile(full_path):
        if info == '1':
            # Return the file size if 'info=1' is specified
            file_size = os.path.getsize(full_path)
            return jsonify({"size": file_size})
        else:
            # Return the file as a download
            try:
                return send_file(full_path, as_attachment=True)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    # If the path is neither a file nor a directory, return an error
    return jsonify({"error": "Invalid path type."}), 400

def create_app():
    pass

if __name__ == '__main__':
    app.run(debug=True)
