import tornado
import json
from tornado import gen
from .User import *
from functools import wraps
import hashlib
from tornado.escape import json_encode
from .helper import *


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", 'Content-Type')
        self.set_header("Access-Control-Allow-Methods", "*")


    @property
    def sqs(self):
        return self.settings['sqs']

    @property 
    def sns(self):
        return self.settings['sns']

    @property 
    def ses(self):
        return self.settings['ses']

    @property 
    def dynamo(self):
        return self.settings['dynamo']

    @property
    def data(self):
        return json.loads(self.request.body.decode('utf-8'))

   

   #helper functions
    def write_json(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json_encode(data))
        self.finish()

    def write_json_with_status(self, status, data):
        self.set_status(status)
        self.write_json(data)

