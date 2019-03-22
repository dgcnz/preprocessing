import os
from collections import defaultdict
from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from preprocessing import SpanishPreprocessor

load_dotenv()
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

dic_path = 'resources/dictionaries'
context_dic_path = f"{dic_path}/context_specific.dic"
abbr_path = 'resources/abbreviations.json'
context_bigram_path = 'resources/bigram.json'

ppc = SpanishPreprocessor(
    lang_dic_path=dic_path,
    context_dics_paths=[context_dic_path],
    context_bigram_path=context_bigram_path,
    abbreviations_path=abbr_path)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.route('/api/preprocess', methods=['POST'])
def api_process():
    """
    Endpoint for preprocessing

    Takes Request JSON structured the following way:
        req = {
           "sentence" : str,
           "verbose" : bool
           "options" : list
        }

    DISCLAIMER: verbose and options attributes are optional.

    Returns JSON response structured the following way:
        res = {
            "processed" : str,
            "debug" : {
                "tokens" : [],
                "lower" : str,
                "abbreviations": str,
                ...
        }

    Debug attribute is only present when verbose is True in request.
    Debug attributes will contain at least "tokens", with list of tokens.
    Other debug attributes will depend on options list attribute in request.
        They will be of type str.
    """

    if request.headers['Content-Type'] == 'application/json' or request.headers[
            'Content-Type'] == 'application/json;charset=UTF-8':
        req = defaultdict(dict, request.json)
        res = ppc.return_best_sentence(req["sentence"], req["verbose"],
                                       req["options"])
        return (jsonify(res), 200)

    raise InvalidUsage('Unsupported media type.', status_code=415)


app.run(port=os.getenv('VUE_APP_BACKEND_PORT'))
app.run(debug=True)
