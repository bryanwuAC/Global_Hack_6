import tornado
import json
from tornado import gen
from .User import *
from .base_handler import *
import datetime
import re
from .config import *
import hashlib
from .helper import *
from boto.dynamodb2.table import Table


#main handler for shelter administrators 
class CenterHandler(BaseHandler):

    @property
    def shelter_table(self):
        return Table('Shelter_Table', connection = self.dynamo)

    @property
    def user_table(self):
        return Table('User_Table',connection=self.dynamo)

    '''
        Register a person sleeping in shelter
    '''
    @gen.coroutine
    def post(self):
        #check a user in
        userid = self.data['userid']
        #get the tables
        try:
            userinfo = self.shelter_table.get_item(UserID=userid)
        except:
            self.write_json({'result':'fail', 'reason':'Invalid userid'})
        try:
            realUser = self.user_table.get_item(UserID = md5(self.data['phone']))
        except:
            self.write_json({'result':'fail', 'reason':'Not a registered cellphone number'})
        temp = userinfo['AvailableSpace']
        #boolean to indicate if customize of the bed number requested
        if self.data['customize'] == False:
            #case in which administrator thinks the number of bed requested is reasonable
            #check if there's still enough bed left
            if temp < int(self.data['bedNumber']):
                self.write_json({'result':'fail', 'reason':'Not enough space'})
            userinfo['AvailableSpace'] = int(temp)-int(self.data['bedNumber'])
            yield gen.maybe_future(userinfo.partial_save())
            #if we are running out of space, record its time to database
            if userinfo['AvailableSpace'] == 0:
                userinfo['Time1'] = userinfo['Time2']
                userinfo['Time2'] = userinfo['Time3']
                userinfo['Time3'] = userinfo['Time4']
                userinfo['Time4'] = userinfo['Time5']
                userinfo['Time5'] = userinfo['Time6']
                userinfo['Time6'] = userinfo['Time7']
                userinfo['Time7'] = int(self.data['time'])
                yield gen.maybe_future(userinfo.partial_save())
                # compute suggested time
                timelist = [userinfo['Time1'],userinfo['Time2'],userinfo['Time3'],userinfo['Time4'],userinfo['Time5'],userinfo['Time6'],userinfo['Time7']]
                reco = computeTime(timelist)
                userinfo['RecommendedTime'] = reco
                yield gen.maybe_future(userinfo.partial_save())
            #update info in user database
            realUser['CurrentLiving'] = userinfo['ShelterName']
            realUser['BedNumber'] = self.data['bedNumber']
            yield gen.maybe_future(realUser.partial_save())
            self.write_json({'result' : 'success'})
        else:
            #another space for custom enter of data
            if userinfo['AvailableSpace'] < int(self.data['number']):
                self.write_json({'result':'fail', 'reason':'Not enough space'})
            userinfo['AvailableSpace'] = userinfo['AvailableSpace']-int(self.data['number'])
            realUser['CurrentLiving'] = userinfo['ShelterName']
            realUser['BedNumber'] = int(self.data['number'])
            yield gen.maybe_future(realUser.partial_save())
            #still, if full
            if userinfo['AvailableSpace'] == 0:
                userinfo['Time1'] = userinfo['Time2']
                userinfo['Time2'] = userinfo['Time3']
                userinfo['Time3'] = userinfo['Time4']
                userinfo['Time4'] = userinfo['Time5']
                userinfo['Time5'] = userinfo['Time6']
                userinfo['Time6'] = userinfo['Time7']
                userinfo['Time7'] = self.data['time']
                yield gen.maybe_future(userinfo.partial_save())
                # compute suggested time
                timelist = [userinfo['Time1'],userinfo['Time2'],userinfo['Time3'],userinfo['Time4'],userinfo['Time5'],userinfo['Time6'],userinfo['Time7']]
                reco = computeTime(timelist)
                userinfo['RecommendedTime'] = reco
                yield gen.maybe_future(userinfo.partial_save())
            yield gen.maybe_future(userinfo.partial_save())
            self.write_json({'result' : 'success'})

    @gen.coroutine
    def put(self):
        userid = self.data['userid']
        try:
            userinfo = self.shelter_table.get_item(UserID=userid)
        except:
            self.write_json({'result':'fail', 'reason':'Invalid userid'})
        #boolean to decide if we check everyone out
        if self.data['checkAll'] == "0":
            #check a user out
            try:
                realUser = self.user_table.get_item(UserID = md5(self.data['phone']))
            except:
                self.write_json({'result':'fail', 'reason':'Not a registered cellphone number'})
            userinfo['AvailableSpace'] = userinfo['AvailableSpace'] + realUser['BedNumber']
            realUser['SinceLastTime'] = 0
            realUser['LastLiving'] = realUser['CurrentLiving']
            realUser['CurrentLiving'] = "None"
            yield gen.maybe_future(userinfo.partial_save())
            yield gen.maybe_future(realUser.partial_save())
            self.write_json({'result' : 'success'})
        else:
            #check everyone out by one button
            #increase everyone's 
            userinfo['AvailableSpace'] = userinfo['Capacity']
            userinfo['Waitlist'] = 0
            #increase the old users' counter
            oldUsers = self.user_table.scan(LastLiving__eq = userinfo['ShelterName'])
            for user in oldUsers:
                user['SinceLastTime'] = user['SinceLastTime'] + 1
                yield gen.maybe_future(user.partial_save())
            #update user info
            users = self.user_table.scan(CurrentLiving__eq = userinfo['ShelterName'])
            for user in users:
                user['LastLiving'] = user['CurrentLiving']
                user['SinceLastTime'] = 0
                user['CurrentLiving'] = "None"
                yield gen.maybe_future(user.partial_save())
            #get the users that was here 3 days ago and hasn't settled in any shelter since. 
            contactUsers = self.user_table.scan(SinceLastTime__eq = 3)
            response = []
            length = 0
            for res in contactUsers:
                cleaned_user = user_filter(res)
                response.append(cleaned_user)
                length = length+1
            yield gen.maybe_future(userinfo.partial_save())
            #write the json
            self.write_json({'result' : 'success', 'data':response, 'length':length})


def user_filter(Object):
    filters = ['FirstName','LastName','Gender','Age','SSN','Veteran','Transportation','NeedJob','NeedEducation','Phone']
    cleaned_user = {}
    for key,val in Object.items():
        if key in filters:
            cleaned_user[key] = str(val)
    return cleaned_user


def computeTime(list):
    hour = 0
    minute = 0
    for item in list:
        string = str(item)
        hour = hour + int(string[:2])
        minute = minute + int(string[-2:])
    print (hour)
    print (minute)
    rsh = math.floor(hour/7)
    rsm = math.floor(minute/7)
    if rsm > 60:
        rsm = rsm - 60
        rsh = rsh + 1
    if rsh < 10:
        rsh = "0"+str(rsh)
    if rsm < 10:
        rsm = "0"+str(rsm)
    return int(str(rsh)+str(rsm))

