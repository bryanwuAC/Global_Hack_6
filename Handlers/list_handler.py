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

class ListHandler(BaseHandler):

    @property
    def shelter_table(self):
        return Table('Shelter_Table', connection = self.dynamo)

    @property
    def user_table(self):
        return Table('User_Table',connection=self.dynamo)

    @gen.coroutine
    def post(self):
    	#get all list of residence of tonight
        userid = self.data['userid']
        currentLocation = self.shelter_table.get_item(UserID = userid)
        #get everyone use scan from db
        everything = self.user_table.scan(CurrentLiving__eq = currentLocation['ShelterName'])
        response = []
        length = 0
        for res in everything:
            cleaned_user = user_private_filter(res)
            response.append(cleaned_user)
            length = length+1
        self.write_json({'result': 'success','data':response,'length':length})

#private level access filter for user data to filter out the data.
def user_private_filter(Object):
    filters = ['FirstName','LastName','Gender','Age','SSN','Veteran','Transportation','NeedJob','NeedEducation','Phone','DomesticViolence','Medical']
    cleaned_user = {}
    for key,val in Object.items():
        if key in filters:
            cleaned_user[key] = str(val)
    return cleaned_user