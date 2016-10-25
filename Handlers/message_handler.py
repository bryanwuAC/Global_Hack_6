import tornado
import json
from tornado import gen
from .User import *
from .base_handler import *
import time
import re
from .config import *
import hashlib
from .helper import *
from boto.dynamodb2.table import Table

class MessageHandler(BaseHandler):

	@gen.coroutine
	def post(self):
		sendMessage(self.data['toNumber'], self.data['fromNumber'], self.data['message'])
