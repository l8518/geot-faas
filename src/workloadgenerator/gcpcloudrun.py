import os
import subprocess
import json
from flask import Flask,request,jsonify

app = Flask(__name__)

@app.route("/", methods=['POST'])
def run_experiment():

    header={request.json['token-key']: request.json['token-value']}
    subprocess.call([f'/app/run_experiment.sh'], env=dict(os.environ, SAAF_ENDPOINT_HEADERS=json.dumps(header)))

    resp = jsonify(success=True)
    return resp

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))