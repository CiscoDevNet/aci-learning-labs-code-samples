#!usr/bin/env python

import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.vz
import cobra.model.pol
from credentials import *


def main():
	auth = cobra.mit.session.LoginSession(URL, LOGIN, PASSWORD)
	session = cobra.mit.access.MoDirectory(auth)
	session.login()

	root = cobra.model.pol.Uni('')

	tenant_snv = cobra.model.fv.Tenant(root, 'SnV')
	vrf_snv = cobra.model.fv.Ctx(tenant_snv, name='Superverse')
	bd_snv = cobra.model.fv.BD(tenant_snv, name='antigravity')
	bd_snv_vrf = cobra.model.fv.RsCtx(bd_snv, tnFvCtxName='Superverse')
	bd_snv_subnet = cobra.model.fv.Subnet(bd_snv, ip='10.2.10.1/23')

	contracts = (('web', 'http', 'tcp', '80', 'context'), ('database', 'sql', 'tcp', '1433', 'application-profile'))
	for contract in contracts:
		create_contract(tenant_snv, contract[1], contract[2], contract[3], contract[0], contract[4])

	app_names = (('Evolution_X', 'vlan-121', 'vlan-122'), ('Rescue', 'vlan-123', 'vlan-124'),
		('Chaos', 'vlan-125', 'vlan-126'), ('Power_Up', 'vlan-127', 'vlan-128'))
	for app in app_names:
		create_app(tenant_snv, app[0], bd_snv, app[1], app[2])

	config_request = cobra.mit.request.ConfigRequest()
	config_request.addMo(tenant_snv)
	session.commit(config_request)


def create_app(tenant_obj, app_name, bd_object, vlan_web, vlan_db):
	app = cobra.model.fv.Ap(tenant_obj, app_name)

	epg_web = cobra.model.fv.AEPg(app, 'Web')
	epg_web_bd = cobra.model.fv.RsBd(epg_web, tnFvBDName='antigravity')
	epg_web_phys_domain = cobra.model.fv.RsDomAtt(epg_web, tDn='uni/phys-SnV_phys')
	epg_web_path_a = cobra.model.fv.RsPathAtt(epg_web, tDn='topology/pod-1/protpaths-101-102/pathep-[SnV_FI-1B]', encap=vlan_web)
	epg_web_path_b = cobra.model.fv.RsPathAtt(epg_web, tDn='topology/pod-1/protpaths-101-102/pathep-[SnV_FI-1A]', encap=vlan_web)
	epg_web_path_c = cobra.model.fv.RsPathAtt(epg_web, tDn='topology/pod-1/paths-101/pathep-[eth1/10]', encap="vlan-10")
	epg_web_provided = cobra.model.fv.RsProv(epg_web, tnVzBrCPName='web')
	epg_web_consumed = cobra.model.fv.RsCons(epg_web, tnVzBrCPName='database')

	epg_db = cobra.model.fv.AEPg(app, 'Database')
	epg_db_bd = cobra.model.fv.RsBd(epg_db, tnFvBDName='antigravity')
	epg_db_phys_domain = cobra.model.fv.RsDomAtt(epg_db, tDn='uni/phys-SnV_phys')
	epg_db_path_a = cobra.model.fv.RsPathAtt(epg_db, tDn='topology/pod-1/protpaths-101-102/pathep-[SnV_FI-1B]', encap=vlan_db)
	epg_db_path_b = cobra.model.fv.RsPathAtt(epg_db, tDn='topology/pod-1/protpaths-101-102/pathep-[SnV_FI-1A]', encap=vlan_db)
	epg_db_provided = cobra.model.fv.RsProv(epg_db, tnVzBrCPName='database')


def create_contract(tenant_obj, filter_name, protocol, port, contract_name, contract_scope):
	filter_obj = cobra.model.vz.Filter(tenant_obj, name=filter_name)
	filter_entry = cobra.model.vz.Entry(filter_obj, name='{}-{}'.format(protocol, port), etherT='ip', prot=protocol, dFromPort=port, dToPort=port)

	contract = cobra.model.vz.BrCP(tenant_obj, name=contract_name, scope=contract_scope)
	contract_subject = cobra.model.vz.Subj(contract, name=filter_name)
	subject_filter = cobra.model.vz.RsSubjFiltAtt(contract_subject, tnVzFilterName=filter_name)


if __name__ == '__main__':
	main()
