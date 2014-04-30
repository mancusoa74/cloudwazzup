cloudwazzup 0.2
===============

This is a simple REST web service providing API to send whatsapp messages

It is based on the great **Yowsup** library provided by tgalal [https://github.com/tgalal/yowsup].

This service is hosted on the great RedHat openshift [https://www.openshift.com]

This service is available here: **https://cloudwazzup-osft.rhcloud.com**

<br>
*
This Web Service is not ment to be used/abused for any spamming/advertising etc. 
For this reason limitation on max number of messages per day is implemented
You should behave exactly as you do on your mobile WhatsApp application. 
Be reponsible for what you send :)
*

---

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
```







---
License
----
MIT
