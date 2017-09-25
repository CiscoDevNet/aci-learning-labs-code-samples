#!usr/bin/env python

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
tenant_villains.delete()

config_request = cobra.mit.request.ConfigRequest()
config_request.addMo(tenant_villains)
session.commit(config_request)
