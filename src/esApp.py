from elasticsearch import Elasticsearch
import json
from pprint import pprint
from utils import get_parsed_alias, get_parsed_main_result
from flask import Flask, jsonify, abort, make_response
from flask_httpauth import HTTPBasicAuth
import time

app = Flask(__name__)
@app.route('/')
def index():
    return "Welcome to WikiSearch powered by elasticsearch"
# authentication
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'marvin':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

@app.route("/search/<category>/<keywords>", methods=["GET"])
# @auth.login_required
def search(category, keywords):
    es_url = "http://127.0.0.1:9200"    # change IP if necessary
    es = Elasticsearch(es_url)
    num_limits = 20

    query_body = {"query":{
  "multi_match": {
    "query": keywords,
      "fields": ["label", "description"]
  }
},
  "highlight": {
    "pre_tags":["<span style='color:red;'>"],
    "post_tags":["</span>"],
    "fields":{
      "*":{}
    }
  }
}

    query_alias = {"query": {
        "multi_match": {
            "query": keywords,
            "fields": ["alias"]
        }
    },
        "highlight": {
            "pre_tags": ["<span style='color:red;'>"],
            "post_tags": ["</span>"],
            "fields": {
                "*": {}
            }
        }
    }
    if category == "property":
        outputs = get_parsed_main_result(es, query_body, 'property')

        if len(set(outputs['id_set'])) > num_limits:
            pass
        else:
            outputs = get_parsed_alias(es, query_alias, 'propertyalias', **outputs)
    elif category == "entity":
        outputs = get_parsed_main_result(es, query_body, 'entity')

        if len(set(outputs['id_set'])) > num_limits:
            pass
        else:
            outputs = get_parsed_alias(es, query_alias, 'entityalias', **outputs)
    else:
        raise NotImplementedError
    # with open("results/clubManager.json", "w") as f:
    #     json.dump(outputs, f)
    # pprint(outputs)
    return jsonify({"results":outputs})


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # auto reload when the template is modified
    app.run(debug=True)
