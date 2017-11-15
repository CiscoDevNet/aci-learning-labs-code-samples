import requests
import argparse
from acitoolkit.acitoolkit import *
from credentials import *

requests.packages.urllib3.disable_warnings() # Disable warning message

cli_args = argparse.ArgumentParser("Post to Spark", "Collects an Access Token to connect to Spark Chatroom")
cli_args.add_argument('-t', '--token', required=True,
                      help="The Access Token provided by https://developer.ciscospark.com/ after login.")
cli_args.add_argument('-r', '--roomid', required=True,
                      help="The Room ID associated with the chatroom used for messages")

args = cli_args.parse_args()
TOKEN = "Bearer {}".format(vars(args)["token"])
ROOM_ID = vars(args)["roomid"]

def main():
    session = Session(URL, LOGIN, PASSWORD)
    session.login()

    subscribe_to_events(session)


def subscribe_to_events(session):
    Tenant.subscribe(session, only_new=True)
    AppProfile.subscribe(session, only_new=True)
    EPG.subscribe(session, only_new=True)

    while True:
        if Tenant.has_events(session):
            event = Tenant.get_event(session)
            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            post_message_to_spark("{} {}".format(event.dn, status))

        elif AppProfile.has_events(session):
            event = AppProfile.get_event(session)
            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            post_message_to_spark("{} {}".format(event.dn, status))

        elif EPG.has_events(session):
            event = EPG.get_event(session)
            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            post_message_to_spark("{} {}".format(event.dn, status))


def post_message_to_spark(message):
    header = {"Authorization": TOKEN, "Content-Type": "application/json"}
    message_url = "https://api.ciscospark.com/v1/messages"

    request_body = {"roomId": ROOM_ID, "text": message}
    response = requests.post(message_url, json=request_body, headers=header)

    if not response.ok:
        print("FAILED TO SEND {} TO SPARK".format(message))


if __name__ == "__main__":
    main()