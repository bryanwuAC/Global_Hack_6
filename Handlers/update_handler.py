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

class UpdateHandler(BaseHandler):

    @property
    def shelter_table(self):
        return Table('Shelter_Table', connection = self.dynamo)

    @property
    def user_table(self):
        return Table('User_Table',connection=self.dynamo)

    #update a column
    @gen.coroutine
    def post(self):
        if self.data['isShelter'] == "1":
            userid = self.data['userid']
            try:
                user = self.shelter_table.get_item(UserID = userid)
            except:
                self.write_json({'result':'fail','reason':'invalid userid'})
            user[self.data['key']] = self.data['value']
            yield gen.maybe_future(user.partial_save())
            self.write_json({'result' : 'success'})
        else:
            userid = self.data['userid']
            try:
                user = self.user_table.get_item(UserID = userid)
            except:
                self.write_json({'result':'fail','reason':'invalid userid'})
            user[self.data['key']] = self.data['value']
            yield gen.maybe_future(user.partial_save())
            self.write_json({'result' : 'success'})

    #get the userid and send all info of json
    def put(self):
        userid = self.data['userid']
        if self.data['isShelter'] == "1":
            try:
                user = self.shelter_table.get_item(UserID = userid)
            except:
                self.write_json({'result':'fail','reason':'invalid userid'})
            response = []
            cleaned_user = shelter_filter(user)
            response.append(cleaned_user)
            self.write_json({'result':'success', 'data':response})
        else:
            try:
                user = self.user_table.get_item(UserID = userid)
            except:
                self.write_json({'result':'fail','reason':'invalid userid'})
            response = []
            cleaned_user = user_private_filter(user)
            response.append(cleaned_user)
            self.write_json({'result':'success', 'data':response})

#shelter filter to filter out the only desired keys to be seen
def shelter_filter(Object):
    filters = ['ShelterName','AvailableSpace','SuggestedTime','Capacity','Lat','Long','Service','Hours','MinAge','MaxAge','BanGender','RequireVeteran']
    cleaned_shelter = {}
    for key, val in Object.items():
        if key in filters:
            cleaned_shelter[key] = str(val)
    return cleaned_shelter


#private level access filter for user data to filter out the data.
def user_private_filter(Object):
    filters = ['FirstName','LastName','Gender','Age','SSN','Veteran','Transportation','NeedJob','NeedEducation','Phone','DomesticViolence','Medical','Birthday','Ethnicity']
    cleaned_user = {}
    for key,val in Object.items():
        if key in filters:
            cleaned_user[key] = str(val)
    return cleaned_user