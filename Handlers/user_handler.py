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

class UserHandler(BaseHandler):

    @property
    def shelter_table(self):
        return Table('Shelter_Table', connection = self.dynamo)

    @property
    def user_table(self):
        return Table('User_Table',connection=self.dynamo)


    @gen.coroutine
    def post(self):
        '''
            Register for the app as shelters
        '''


        if self.data["isShelter"] == "1":

            # Get email from client

            password = self.data['password']
            email = self.data['email'].strip()

            # Hash the username to get an email

            hashed_userid = md5(email)

            # Check if this email has been registered
                   
            user_exist = yield gen.maybe_future(self.shelter_table.has_item(UserID=hashed_userid))

            if user_exist == True:

                # tell client and stop processing this request
                self.write_json({
                    'result' : 'fail',
                    'reason' : 'email already used'
                    })

                return

            hashed_password = md5(password)
            
         
            # Create new user item and upload it to database
            yield gen.maybe_future(self.shelter_table.put_item(data={
                    "UserID"        : hashed_userid,
                    "Email"         : self.data["email"],
                    "ShelterName"   : self.data['shelterName'],
                    "AccountActive" : True,
                    "Password"      : hashed_password,
                    "Service"       : self.data['service'],
                    "Capacity"      : int(self.data['capacity']),
                    "AvailableSpace": int(self.data['availableSpace']),
                    "Waitlist"      : int(self.data['waitlist']),
                    "Time1"         : 0,
                    "Time2"         : 1,
                    "Time3"         : 2,
                    "Time4"         : 3,
                    "Time5"         : 4,
                    "Time6"         : 5,
                    "Time7"         : 6, 
                    "SuggestedTime" : 0,
                    "Address"       : self.data['address'],
                    "Lat"           : self.data['lat'],
                    "Long"          : self.data['long'],
                    "MinAge"        : int(self.data['minAge']),
                    "MaxAge"        : int(self.data['maxAge']),
                    "BanGender"     : self.data['banGender'],
                    "RequireVeteran": int(self.data['requireVeteran']),
                    "Hours"         : self.data['hours']
                }
            ))

            # send userid back to the client

            self.write_json({
                'result': 'success',
                'userid': hashed_userid
            })

        else:
            # Get phone from client

            password = self.data['password']
            phone = self.data['phone'].strip()

            # Hash the phone number to get the userid

            hashed_userid = md5(phone)

            # Check if this phone number has been registered
                   
            user_exist = yield gen.maybe_future(self.user_table.has_item(UserID=hashed_userid))

            if user_exist == True:

                # tell client and stop processing this request
                self.write_json({
                    'result' : 'fail',
                    'reason' : 'cellphone already used'
                    })

                return

            hashed_password = md5(password)
            
         
            # upload the item to the database
            yield gen.maybe_future(self.user_table.put_item(data={
                    "UserID"        : hashed_userid,
                    "Phone"         : self.data['phone'],
                    "SSN"           : self.data["ssn"],
                    "FirstName"     : self.data['firstname'],
                    "LastName"      : self.data['lastname'],
                    "AccountActive" : True,
                    "Password"      : hashed_password,
                    "Birthday"      : self.data['birthday'],
                    "Gender"        : self.data['gender'],
                    "Veteran"       : int(self.data['veteran']),
                    "BedNumber"     : 1,
                    "Age"           : int(self.data['age']),
                    "Transportation": self.data['transportation'],
                    "LastCheckIn"   : "Not available",
                    "Ethnicity"     : self.data['ethnicity'],
                    "NeedJob"       : int(self.data['needJob']),
                    "NeedEducation" : int(self.data['needEducation']),
                    "CellPhone"     : self.data['cellPhone'],
                    "DomesticViolence":self.data['domesticViolence'],
                    "Medical"       : self.data['medical'],
                    "CurrentLiving" : "None",
                    "LastLiving"    : "None",
                    "SinceLastTime" : 0,
                }
            ))

            # send userid back to the client

            self.write_json({
                'result': 'success',
                'userid': hashed_userid
            })