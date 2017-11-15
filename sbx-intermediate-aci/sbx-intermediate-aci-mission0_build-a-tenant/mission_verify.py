#! /usr/bin/env python
"""
DevNet Express for Data Center Infrastructure
Intermediate ACI Programmability Mission

Building a tenant application with WebArya

This script will query the APIC to verify that the
new tenant application was created.
"""

from acitoolkit.acitoolkit import Session
from acitoolkit import Tenant, AppProfile
from credentials import URL, LOGIN, PASSWORD
import requests, json, sys

requests.packages.urllib3.disable_warnings() # Disable warning message

# What to look for?
mission_tenant = "SnV"
mission_anp = "Evolution_X"
success_message = "I completed the WebArya Mission and added Application {} to Tenant {}!".format(mission_anp, mission_tenant)


session = Session(URL, LOGIN, PASSWORD)
resp = session.login()
if not resp.ok:
    print('%% Could not login to APIC')
    sys.exit(1)

# Query for ACI Tenants
tenants = Tenant.get(session)
for tenant in tenants:
    # Search for Mission Tenant
    if tenant.name == mission_tenant:
        # Get Apps in Tenant
        apps = AppProfile.get(session, tenant)
        for app in apps:
            # Search for mission app
            if app.name == mission_anp:
                print(success_message)
                print("Success!  Well done !")
                sys.exit()

# Tenant and/or App not found, exit
sys.exit("\nMission Failed: Application {} not found in Tenant {}\n".format(mission_anp, mission_tenant))
