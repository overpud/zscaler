from flask import Flask, render_template
from flask_restful import Api
from requests_count import RandomNumberAPI
app = Flask(__name__)
api = Api(app)


api.add_resource(RandomNumberAPI, '/api/requestscount', endpoint='randomnumber')

if __name__ == '__main__':
    app.debug = True
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('', 8888), app)
    http_server.serve_forever()