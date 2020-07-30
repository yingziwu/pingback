from flask import Flask, request
from flask_cors import CORS

from pingback import ping_urls

app = Flask(__name__)
cors = CORS(app, resources=r'/pingback/', methods=['POST'])


@app.route('/pingback/', methods=['GET', 'POST'])
def api():
    if request.method == 'POST':
        try:
            if request.is_json:
                return handle_request(request.get_json())
            else:
                return {"error": "Request not json"}, 400
        except ValueError:
            return {"error": "Bad Request"}, 400
    else:
        return {"error": "method don't support."}, 405


def handle_request(object):
    source_url = object["source_url"]
    target_url_list = object["target_url_list"]
    if isinstance(source_url, str) and isinstance(target_url_list, list):
        return ping_urls(source_url, target_url_list)
    else:
        raise ValueError


if __name__ == '__main__':
    app.run(debug=True)
