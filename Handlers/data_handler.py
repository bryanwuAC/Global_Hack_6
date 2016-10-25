import tornado
from .config import *
from tornado import gen
from .base_handler import *
from .User import *
import hashlib
from boto.dynamodb2.table import Table

class DataHandler(BaseHandler):

    @property
    def shelter_table(self):
        return Table('Shelter_Table', connection = self.dynamo)

    @property
    def user_table(self):
        return Table('User_Table',connection=self.dynamo)

    #filter out all the shelters that the current user don't meet requirement
    @gen.coroutine
    def post(self):
        userid = self.data['userid']
        user = self.user_table.get_item(UserID = userid)
        everything = self.shelter_table.scan(AvailableSpace__gte = int(self.data['beds']), 
                                                    MinAge__lte = user['Age'], 
                                                    MaxAge__gte = user['Age'], 
                                                    BanGender__ne = user['Gender'], 
                                                    RequireVeteran__lte = user['Veteran'])
        response = []
        length = 0
        for res in everything:
            cleaned_shelter = shelter_filter(res, float(self.data['lat']), float(self.data['long']))
            response.append(cleaned_shelter)
            length = length+1
        self.write_json({'result': 'success','data':response,'length':length})

    # as a shelter admin, get the entire data of a user using its phone number
    @gen.coroutine
    def put(self):
        userid = md5(self.data['phone'])
        shelterid = self.data['userid']
        try:
            shelter = self.shelter_table.get_item(UserID = shelterid)
        except:
            self.write_json({'result':'fail','reason':'invalid userid'})
        try:
            user = self.user_table.get_item(UserID = userid)
        except:
            self.write_json({'result':'fail','reason':'invalid cellphone'})
        response = []
        cleaned_user = user_private_filter(user)
        response.append(cleaned_user)
        self.write_json({'result':'success','data':response,'availableSpace':str(shelter['AvailableSpace'])})

        
#shelter filter to filter out the only desired keys to be seen
def shelter_filter(Object, lat, long):
    filters = ['ShelterName','AvailableSpace','SuggestedTime','Capacity','Lat','Long','Service','Hours','Address']
    cleaned_shelter = {}
    value = 0
    for key, val in Object.items():
        if key == 'Lat':
            value = value + (lat-float(val))*(lat-float(val))
        if key == 'Long':
            value = value + (long-float(val))*(long-float(val))
        if key in filters:
            cleaned_shelter[key] = str(val)
    cleaned_shelter['distance'] = value
    return cleaned_shelter

#public level user access
def user_filter(Object):
    filters = ['FirstName','LastName','Gender','Age','SSN','Veteran','Transportation','NeedJob','NeedEducation','Phone']
    cleaned_user = {}
    for key,val in Object.items():
        if key in filters:
            cleaned_user[key] = str(val)
    return cleaned_user

#private level user access
def user_private_filter(Object):
    filters = ['FirstName','LastName','Gender','Age','SSN','Veteran','Transportation','NeedJob','NeedEducation','Phone','DomesticViolence','Medical']
    cleaned_user = {}
    for key,val in Object.items():
        if key in filters:
            cleaned_user[key] = str(val)
    return cleaned_user

