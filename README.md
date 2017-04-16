# twilio-reminder-caller
This is a toy project to learn the basics of Twilio (and also Flask, redis, redis queue). It functions as a timer/reminder that is set up by the user by SMS and the reminder with the message is communicated to the user after the given time via a phone call and an SMS.

## Installing it
1. Use the following to install pip and virtualenv (https://www.twilio.com/docs/quickstart/python/devenvironment#installing-python)
2. Clone this project and cd into it
3. Install dependencies `pip install -r requirements.txt`
4. Install [redis](http://redis.io/download)
5. Install [ngrok](https://ngrok.com/) to be able to make a public tunnel to your localhost

## Running it
Start by setting up background services
1. Redis server `redis-server &`
2. RQ server and scheduler `rqworker &; rqscheduler -i 10 &` 
3. Edit run.py to have your Twilio account details and a Twilio number
4. Run run.py `python run.py`
5. Run ngrok in another terminal `./ngrok http 5000` to make a public tunnel to your localhost
6. Copy and paste the URL of your server into the "SMS" URL of a number on the [Numbers](https://www.twilio.com/user/account/phone-numbers/incoming) page of your Twilio Account.

## Using it
All commands must be sent as an SMS to the Twilio phone number. Currently 2 commands are supported "timer" and "reset".


**To set a timer send the following:**

`timer <time value> <time unit min/hour> "message"` 
e.g "timer 5 min "Call mom!"" 
or "timer 8 hour "Stop being lazy and wake the hell up!""

You should receive a confirmation SMS instantly and after the given time you will receive a phone call from the Twilio number hearing your message, SMS is also sent.


**To cancel all timers for the sender:**

`reset`

You should receive an SMS confirmation with how many timers were cancelled for you.


## TODO
* List current timers
* Move cancelling all messages into a RQ job to make it more scalable instead of doing it in the REST service

