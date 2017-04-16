import shlex
import urllib
import uuid
from datetime import timedelta

from flask import Flask, request
from redis import Redis
from rq_scheduler import Scheduler
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

TWILIO_ACCOUNT_SID = "XXX" # your Twilio SID
TWILIO_AUTH_TOKEN = "XXX" # your Twilio token
TWILIO_NUMBER = "+44123456789" # your Twilio number


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
redis_server = Redis() # Open a connection to your Redis server.
scheduler = Scheduler(connection=redis_server) # Create a scheduler object with your Redis server.


USAGE = 'To set a timer: timer <time value> <time unit min/hour> "message"\nE.g "timer 5 min "Call mom!""\n' \
        'To cancel all timers: reset'


@app.route("/", methods=['GET', 'POST'])
def receive():
    """Handle incoming texts"""

    number = request.form['From']
    body = request.form['Body']

    resp = MessagingResponse()

    args = shlex.split(body)
    if len(args) == 4:
        action = args[0].lower()
        time = args[1]
        unit = args[2].lower()
        message = args[3]

        if action == 'timer' and time.isdigit() and int(time) >= 0 and unit in ['min','hour']:
            resp.message("Timer set for {} {}s with message {}".format(time, unit, message))

            job_id = str(uuid.uuid4()) # create an external job_id

            # add jobs to rq_scheduler queue
            if unit == 'hour':
                job = scheduler.enqueue_in(timedelta(hours=int(time)), 'run.alert', number, message, job_id)
            else:
                job = scheduler.enqueue_in(timedelta(minutes=int(time)), 'run.alert', number, message, job_id)

            internal_id = job.get_id()
            redis_server.hset(number, job_id, internal_id) # map the internal RQ job id to our job_id
        else:
            resp.message(USAGE)

    elif len(args) == 1 and args[0].lower().startswith('reset'):
        print "Cancelling all jobs for {}".format(number)
        job_ids = redis_server.hvals(number)

        for job_id in job_ids:
            scheduler.cancel(job_id)

        redis_server.delete(number)
        resp.message("{} timers cancelled.".format(len(job_ids)))

    else:
        resp.message(USAGE)

    return str(resp)


def alert(number, message, job_id):
    """Call and send SMS to user"""

    print "Alerting ", number

    redis_server.hdel(number, job_id) # delete the job from active jobs list

    client.api.account.calls.create(to=number,
                                    from_=TWILIO_NUMBER,
                                    url='https://twimlets.com/message?Message%5B0%5D=' + urllib.quote(message))

    client.api.account.messages.create(to=number,
                                       from_=TWILIO_NUMBER,
                                       body='Timer ended with message "{}"'.format(message))

    return None




if __name__ == "__main__":
    app.run(debug=True)
