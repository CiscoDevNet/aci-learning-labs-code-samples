from flask import render_template, redirect, abort, request, url_for, jsonify
from app import app
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
from credentials import *
import requests, json, sys

# MISSION: Provide your Spark Token and the Room ID into which to post
#          You can get it from https://developer.ciscospark.com 
#          The RoomId should have been provided by the instructors 
spark_token = ""
spark_room_id = ""

if spark_token == "" or spark_room_id == "": 
    print("\nError: Please edit the views.py file and provide your token and room id\n")
    sys.exit(1)


def get_healthscore():
    session = aci_login()

    app_query = cobra.mit.request.DnQuery('uni/tn-SnV')
    app_query.queryTarget = SET ME
    app_query.classFilter = SET ME
    app_query.subtreeInclude = SET ME

    apps = SET ME
    health_dict = {}

    for app in apps:
        for health in app.children:
            health_dict[app.name] = int(health.cur)

    return health_dict


def get_faults(app_name):
    session = aci_login()

    fault_query = cobra.mit.request.DnQuery('uni/tn-SnV/ap-{}'.format(app_name))
    fault_query.queryTarget = SET ME
    fault_query.subtreeInclude = SET ME
    fault_query.orderBy = 'faultInfo.severity|desc'
    fault_query.page = 0
    fault_query.pageSize = 15

    faults = SET ME
    faults_dict = {'faults': []}

    for fault in faults:
        if fault.lc == 'retaining':
            fault_dict = {
                'Acknowledged': fault.ack,
                'Affected': 'Issue No Longer Exists',
                'Description': fault.descr,
                'Time': fault.created,
                'Life Cycle': fault.lc
            }
        else:
            fault_dict = {
                'Acknowledged': fault.ack,
                'Affected': fault.affected,
                'Description': fault.descr,
                'Time': fault.created,
                'Life Cycle': fault.lc
            }

        faults_dict['faults'].append(fault_dict)

    return faults_dict


def aci_login():
    auth = cobra.mit.session.LoginSession(URL, LOGIN, PASSWORD)
    session = cobra.mit.access.MoDirectory(auth)
    session.login()

    return session


@app.route('/', methods=['GET', 'POST'])
def index():
    health_dict = get_healthscore()
    return render_template("index.html", health_dict=health_dict)


@app.route('/healthscore_update', methods=['POST'])
def healthscore_update():
    if request.method == 'POST':
        return jsonify(get_healthscore())


@app.route('/fault_update', methods=['POST'])
def fault_update():
    if request.method == 'POST':
        return jsonify(get_faults(request.form['app']))

        
@app.route('/verify_to_spark', methods=["GET"]) 
def verify_to_spark(): 
    message = "I completed the ACI Health Dashboard Mission Completed Successfully!" 
    post_to_spark(message) 
    return redirect("/")

        
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
    