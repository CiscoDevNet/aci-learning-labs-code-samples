""" Push Notifications to Webex Teams """

# pylint: disable=unused-wildcard-import, wildcard-import, redefined-builtin

import argparse
import requests
import urllib3
from acitoolkit.acitoolkit import *
from credentials import *

urllib3.disable_warnings() # Disable warning message

CLI_ARGS = argparse.ArgumentParser(
    "Post to Webex Teams",
    "Collects an Access Token to connect to Webex Teams Room"
)
CLI_ARGS.add_argument(
    '-t', '--token', required=True,
    help="The Access Token provided by https://developer.webex.com/ after login."
)
CLI_ARGS.add_argument(
    '-r', '--roomid', required=True,
    help="The Room ID associated with the room used for messages"
)

ARGS = CLI_ARGS.parse_args()
TOKEN = "Bearer {}".format(vars(ARGS)["token"])
ROOM_ID = vars(ARGS)["roomid"]


def main():
    """ Run the Script """
    session = Session(URL, LOGIN, PASSWORD)
    session.login()

    subscribe_to_events(session)


def subscribe_to_events(session):
    """ Subscribe to Events """
    
    ## SUBSCRIBE TO TENANT CLASS, ONLY NEW EVENTS
    ## SUBSCRIBE TO APPLICATION PROFILE CLASS, ONLY NEW EVENTS
    ## SUBSCRIBE TO EPG CLASS, ONLY NEW EVENTS

    while True:
        if ## CHECK IF TENANT SUBSCRIPTION HAS ANY EVENTS:
            event = ## GET TENANT EVENT
            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            post_message_to_webex_teams("{} {}".format(event.dn, status))

        elif ## CHECK IF APPLICATION PROFILE SUBSCRIPTION HAS ANY EVENTS:
            event = ## GET APPLICATION PROFILE EVENT
            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            post_message_to_webex_teams("{} {}".format(event.dn, status))

        elif ## CHECK IF EPG SUBSCRIPTION HAS ANY EVENTS:
            event = ## GET EPG EVENT
            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            post_message_to_webex_teams("{} {}".format(event.dn, status))


def post_message_to_webex_teams(message):
    """ Send Webex Teams Message """
    header = {"Authorization": TOKEN, "Content-Type": "application/json"}
    message_url = "https://api.ciscospark.com/v1/messages"

    request_body = {"roomId": ROOM_ID, "text": message}
    response = requests.post(message_url, json=request_body, headers=header)

    if not response.ok:
        print("FAILED TO SEND {} TO WEBEX TEAMS".format(message))


if __name__ == "__main__":
    main()
