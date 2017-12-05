#! /usr/bin/env python
"""
Reporting Critical Faults to Cisco Spark

This script will query the APIC for Faults and output
them to the Terminal.
"""

from acitoolkit.acitoolkit import Session
from acitoolkit import Faults
from credentials import URL, LOGIN, PASSWORD
import requests, json

requests.packages.urllib3.disable_warnings() # Disable warning message

fault_count = {"total": 0, "critical": 0}


session = Session(URL, LOGIN, PASSWORD)
resp = session.login()
if not resp.ok:
    print('%% Could not login to APIC')
    sys.exit(1)

# MISSION: Create an instance of the toolkit class representing ACI Faults
#   Hint: the class is called "Faults" and takes no parameters
faults_obj = Faults()

# Monitor the Faults on the APIC
faults_obj.subscribe_faults(session)
while faults_obj.has_faults(session):
    if faults_obj.has_faults(session):
        faults = faults_obj.get_faults(session)

        if faults is not None:
            for fault in faults:
                message = []
                fault_count["total"] += 1
                if fault is not None and fault.severity in ["critical"]:
                    fault_count["critical"] += 1
                    # MISSION: Each fault object has several properties describing the fault.
                    #          The properties are: type, severity, descr, rule, dn, & domain
                    #          Complete each line below with the correct property.
                    #          The first two are already complete.
                    message.append( "****************")
                    message.append( "    Description         : " + fault.descr)
                    message.append( "    Distinguished Name  : " + fault.dn)
                    message.append( "    Rule                : " + fault.rule)
                    message.append( "    Severity            : " + fault.severity)
                    message.append( "    Type                : " + fault.type)
                    message.append( "    Domain              : " + fault.domain)
                    print("\n".join(message))

# Print completion message
print("{} Faults were found.\n  {} listed above are critical".format(fault_count["total"],
                                                                             fault_count["critical"]))
