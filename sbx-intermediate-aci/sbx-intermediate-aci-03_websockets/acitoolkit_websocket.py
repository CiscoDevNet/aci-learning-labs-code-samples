#!/usr/bin/env python
from acitoolkit.acitoolkit import *
from credentials import *


def main():
    session = Session(URL, LOGIN, PASSWORD)
    session.login()

    subscribe_to_events(session)


def subscribe_to_events(apic_session):
    Tenant.subscribe(apic_session, only_new=True)
    AppProfile.subscribe(apic_session, only_new=True)
    
    print("\nListening for Events...\n")
    
    while True:
        if Tenant.has_events(apic_session):
            event = Tenant.get_event(apic_session)

            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            print("\n{} {}".format(event.dn, status))

        elif AppProfile.has_events(apic_session):
            event = AppProfile.get_event(apic_session)

            if event.is_deleted():
                status = "has been deleted"
            else:
                status = "has been created/modified"

            print("\n{} {}".format(event.dn, status))


if __name__ == '__main__':
    main()