#!usr/bin/env python

import time
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
from credentials import *

auth = cobra.mit.session.LoginSession(URL, LOGIN, PASSWORD)
session = cobra.mit.access.MoDirectory(auth)
session.login()

root = cobra.model.pol.Uni('')

tenant_villains = cobra.model.fv.Tenant(root, "Villains")
app_chaos = cobra.model.fv.Ap(tenant_villains, "Chaos")

config_request = cobra.mit.request.ConfigRequest()
config_request.addMo(tenant_villains)
session.commit(config_request)

time.sleep(5)

epg_web = cobra.model.fv.AEPg(app_chaos, "Web")
epg_db = cobra.model.fv.AEPg(app_chaos, "Database")

config_request = cobra.mit.request.ConfigRequest()
config_request.addMo(tenant_villains)
session.commit(config_request)
