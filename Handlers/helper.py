import hashlib
import re
from twilio.rest import TwilioRestClient 
 
#reserved for twilio message usage
def send_message(toNumber, fromNumber, message):
    ACCOUNT_SID = "ACd8318f430744846019d0f3dc4ab02d02" 
    AUTH_TOKEN = "1498f720aa4453ed3cf2068c37144d67" 
     
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
     
    client.messages.create(
        to=toNumber, 
        from_=fromNumber,
        body=message, 
    )


#md5 hash
def md5(s):
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()

