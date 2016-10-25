import tornado
from .config import *
from tornado import gen
from .base_handler import *
from .User import *
import hashlib
from boto.dynamodb2.table import Table

class AuthHandler(BaseHandler):
#user log in
    
    """
        PAYLOAD:{
                    "phone": "12345678",
                    "password":"zhoudiqiu",
                    "isShelter":"0"
                }
                or 
                {
                    "email": email,
                    "password": password,
                    "isShelter": 1
                }
    """
    @gen.coroutine
    def post(self):
        client_data = self.data
        if self.data['isShelter'] == "0":
            userid = yield verify_pwd(
                client_data['phone'], 
                client_data['password'],
                self.dynamo
                )
            
            # verify user logged in
            
            if not userid:
                self.write_json({
                    'result' : 'fail',
                    'message' : 'authantication failed'
                    })
                return

            if userid: 
                #get the user info
                user_table = Table('User_Table',connection=self.dynamo)
                userinfo = user_table.get_item(UserID=userid)
                self.write_json({
                'result' : 'success',
                'message' : 'successfully logged in',
                'userid': userid,
                'firstname': userinfo['FirstName'],
                'lastname': userinfo['LastName']
                })
        else:
            userid = yield verify_pwd_shelter(
                client_data['email'], 
                client_data['password'],
                self.dynamo
                )
            
            # verify user logged in
            
            if not userid:
                self.write_json({
                    'result' : 'fail',
                    'message' : 'authantication failed'
                    })
                return

            if userid: 
                #get the user info
                shelter_table = Table('Shelter_Table',connection=self.dynamo)
                userinfo = shelter_table.get_item(UserID=userid)
                self.write_json({
                'result' : 'success',
                'message' : 'successfully logged in',
                'userid': userid,
                })

#user log out


    @gen.coroutine
    def delete(self):
        data = self.data
        userid = data['userid']
        yield self.user_logout(userid)
        self.write_json({
            'result' : 'success',
            'message' : 'successfully logged out'
            })            


    @gen.coroutine
    def user_logout(self, userid):

        if not userid:
            self.write_json_with_status(403,{
                'result' : 'fail',
                'message' : 'authentication failed'
                })
            return

