#! /usr/bin/env python 
"""
DevNet Express for Data Center Infrastructure
Intro to ACI Programmability Mission

Reporting Critical Faults to Cisco Spark

This script will query the APIC for Faults and report
them to Cisco Spark.
"""

from acitoolkit.acitoolkit import Session
from acitoolkit import Faults
from credentials import URL, LOGIN, PASSWORD
import requests, json

# MISSION: Provide your Spark Token and the Room ID into which to post
spark_token = ""
spark_room_id = ""

fault_count = {"total": 0, "critical": 0}

def post_to_spark(message):
    """
	Simple API Call to Post Message to Spark
	"""
    u = "https://api.ciscospark.com/v1/messages"
    headers = {"Content-type": "application/json; charset=utf-8", 
               "Authorization": "Bearer {}".format(spark_token)}
    body = {"roomId": spark_room_id, 
            "markdown": message}
    return requests.post(u, headers=headers, data=json.dumps(body))
	
	
# MISSION: Provide the proper ACI Toolkit code to create a Session 
# object and use it to login to the APIC.  
# NOTE: Variables URL, LOGIN, and PASSWORD were imported from 
#       the credentials file.  
session = 
resp = 
if not resp.ok:
    print('%% Could not login to APIC')
    sys.exit(1)

# MISSION: Create an instance of the toolkit class representing ACI Faults 
#   Hint: the class is called "Faults" and takes no parameters
faults_obj = 

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
                    message.append( "    Rule                : " + )
                    message.append( "    Severity            : " + )
                    message.append( "    Type                : " + )
                    message.append( "    Domain              : " + )
                    #print("\n".join(message))
                    
                    # Post message to Spark
                    spark = post_to_spark("\n".join(message))
                    if spark.status_code != 200: 
                        print("Problem posting to Spark, check token and ID")
                        exit(1)
                        
# Print completion message
print("{} Faults were found.\n  {} critical faults reported to Spark".format(fault_count["total"], 
                                                                             fault_count["critical"]))
