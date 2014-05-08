cloudwazzup 0.2
===============

This is a simple REST web service providing API to send whatsapp messages

It is based on the great **Yowsup** library provided by tgalal [https://github.com/tgalal/yowsup].

This service is hosted on the great RedHat openshift [https://www.openshift.com]

This service is available here: **https://cloudwazzup-osft.rhcloud.com**

Also available here: **http://mancusoa74.blogspot.com/** (In Italian, if there is interest I can translate to English as well)

<br>

*This Web Service is not ment to be used/abused for any spamming/advertising etc. 
For this reason limitation on max number of messages per day is implemented
You should behave exactly as you do on your mobile WhatsApp application. 
Be reponsible for what you send :)*

##APIs
<br>
These are the provided APIs:

####/cwuser/u_uid [GET]
```
Retrieve information related to a cloudwazzup user
--------------------------------------------------

example:

curl -u monk74:1234 https://cloudwazzup-osft.rhcloud.com/cwuser/891e51de206c4597be2e16f6869c32dc

returns:

{
  "api_version": "0.2.2",
  "u_created_at": "Wed, 30 Apr 2014 08:11:10 GMT",
  "u_email": "mancusoa74@gmail.com",
  "u_name": "monk74",
  "u_uid": "891e51de206c4597be2e16f6869c32dc",
  "wu_avail_mex_day": 100,
  "wu_cc": "39",
  "wu_max_mex_day": 100,
  "wu_passwd": "A/qgXnDiss+0kb1pqOFc07mKJrt=",
  "wu_phone_number": "1234567890"
}
```

<br>
####/cwuser [POST]
```
Register a cloudwazzup user
---------------------------
Note this is the only API which does not require BASIC authentication. Please don't abuse it

example:

curl -H "Content-type: application/json" -X POST  -d '{"u_name": "monk74", "u_passwd": "1234","u_email": "mancusoa74@gmail.com","wu_cc": "39","wu_phone_number": "1234567890","wu_passwd": "A/qgXnDiss+0kb1pqOFc07mKJrt="}'  https://cloudwazzup-osft.rhcloud.com/cwuser

returns:

{
  "username": "monk74",
  "uuid": "891e51de206c4597be2e16f6869c32dc"
}

Please note that wu_passwd can be empty if you first need to register a phone to Whatsapp service.
```

<br>
####/cwuser/u_uid [PUT]
```
Update a cloud wazzup user
---------------------------

example:

curl -u monk74:1234 -H "Content-type: application/json" -X PUT -d '{"u_passwd": "12345","u_email": "user_name@domain.com","wu_cc": "39","wu_phone_number": "0987654321","wu_passwd": "khfkwhfioweffhenckjwsdcihj="}'  https://cloudwazzup-osft.rhcloud.com/cwuser/891e51de206c4597be2e16f6869c32dc

returns:

{
  "api_version": "0.2.2",
  "u_created_at": "Wed, 30 Apr 2014 08:11:10 GMT",
  "u_email": "user_name@domain.com",
  "u_name": "monk74",
  "u_uid": "891e51de206c4597be2e16f6869c32dc",
  "wu_avail_mex_day": 100,
  "wu_cc": "39",
  "wu_max_mex_day": 100,
  "wu_passwd": "khfkwhfioweffhenckjwsdcihj=",
  "wu_phone_number": "0987654321"
}
```

<br>
####/cwuser/u_uid [DELETE]
```
Delete a cloud wazzup user
---------------------------

example:

curl -u monk74:12344 -X DELETE https://cloudwazzup-osft.rhcloud.com/cwuser/891e51de206c4597be2e16f6869c32dc

returns:

{
  "891e51de206c4597be2e16f6869c32dc": "deleted"
}
```

<br>
####/requestcode [GET]
```
Request a Whatsapp SMS code
---------------------------

example:

curl  -u monk74:1234 https://cloudwazzup-osft.rhcloud.com/requestcode/891e51de206c4597be2e16f6869c32dc

returns:

{
  "result": "status: ok\nkind: free\npw: aN7owet4z5WMSTFK+mOFi+Pq4tU=\nprice: \u20ac 0,89\nprice_expiration: 1401905090\ncurrency: EUR\ncost: 0.89\nlogin: 393316835779\ntype: existing\nexpiration: 1427206874"
}

Please note that this will instruct Whatsapp server to send a SMS message to the registered phone number which is useful for trhe registration.

Please note that if the phone number is already registered you will not get a SMS code. The password in the result of this call is the new generated password by Whatsapp. Update you user object with this passowrd and you can then send messages
```

<br>
####/registercode [POST]
```
Register the Whatsapp user (phone numner) by providing the SMS code
-------------------------------------------------------------------

example:

curl  -u monk74:1234 -H "Content-type: application/json" -X POST  -d '{"u_uid": "891e51de206c4597be2e16f6869c32dc", "sms_code": "857-401"}' https://cloudwazzup-osft.rhcloud.com/registercode

returns:

{
  "result": "status: ok\nkind: free\npw: u6kgSp2cwDmw0z1kewB9iG1C+fM=\nprice: \u20ac 0,89\nprice_expiration: 1401892268\ncurrency: EUR\ncost: 0.89\nexpiration: 1427206874\nlogin: 390123456789\ntype: existing"
}

This call also return the Whatsapp password (u6kgSp2cwDmw0z1kewB9iG1C+fM=) which should be part of the cwuser object (update)
```

<br>
####/cwmex [POST]
```
Send a Whatsapp message to a given number
-----------------------------------------

example:

curl  -u monk74:1234 -H "Content-type: application/json"   -X POST  -d '{"u_uid": "891e51de206c4597be2e16f6869c32dc", "dst_phone": "3901234987654","body_mex": "this is a test message"}' https://cloudwazzup-osft.rhcloud.com/cwmex

returns:

{
  "mex_status": "sent",
  "remaining_mex_for_today": 97
}
```

---
License
----
MIT
