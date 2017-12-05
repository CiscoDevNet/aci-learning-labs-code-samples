#!/usr/bin/env python
import argparse
import requests
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.model.pol
import cobra.model.fv
from credentials import *

# use argparse to provide optional arguments and a help menu
cli_args = argparse.ArgumentParser("Create Tenant", "Creates a Tenant in the specified ACI fabric.",
                                   "Required: Tenant, VRF, Bridge Domain, Subnet")
cli_args.add_argument('-t', '--tenant', required=True,
                      help="The New Tenant's Name.")
cli_args.add_argument('-v', '--vrf', required=True,
                      help="The Tenant's VRF.")
cli_args.add_argument('-b', '--bd', required=True,
                      help="The Tenant's Bridge Domain.")
cli_args.add_argument('-g', '--gw', required=True,
                      help="The Bridge Domain's Gateway using CIDR.")
cli_args.add_argument('-s', '--scope', required=True,
                      help="The Subnet's Scope is 'private' or 'public'.")
cli_args.add_argument('-sn', '--subnetname', required=False,
                      help="The Subnet's name.")

# use argparse to parse arguments into variables
args = cli_args.parse_args()

TENANT = vars(args)['tenant']
VRF = vars(args)['vrf']
BRIDGEDOMAIN = vars(args)['bd']
GATEWAY = vars(args)['gw']
SCOPE = vars(args)['scope']
SUBNETNAME = vars(args)['subnetname']

def test_tenant(tenant_name, apic_session):
    """
    This function tests if the desired Tenant name is already in use.
    If the name is already in use, it will exit the script early.

    :param tenant_name: The new Tenant's name
    :param apic_session: An established session with the APIC
    """
    # build query for existing tenants
    tenant_query = cobra.mit.request.ClassQuery('fvTenant')
    tenant_query.propFilter = 'eq(fvTenant.name, "{}")'.format(tenant_name)

    # test for truthiness
    if apic_session.query(tenant_query):
        print("\nTenant {} has already been created on the APIC\n".format(tenant_name))
        exit(1)

def main():
    """
    This function creates the new Tenant with a VRF, Bridge Domain and Subnet.
    """
    # create a session and define the root
    requests.packages.urllib3.disable_warnings()
    auth = cobra.mit.session.LoginSession(URL, LOGIN, PASSWORD)
    session = cobra.mit.access.MoDirectory(auth)
    session.login()

    root = cobra.model.pol.Uni('')

    # test if tenant name is already in use
    test_tenant(TENANT, session)

    # model new tenant configuration
    tenant = cobra.model.fv.Tenant(root, name=TENANT)
    vrf = cobra.model.fv.Ctx(tenant, name=VRF)
    bridge_domain = cobra.model.fv.BD(tenant, name=BRIDGEDOMAIN)
    attached_vrf = cobra.model.fv.RsCtx(bridge_domain, tnFvCtxName=VRF)
    subnet = cobra.model.fv.Subnet(bridge_domain, ip=GATEWAY, scope=SCOPE, name=SUBNETNAME)

    #submit the configuration to the apic and print a success message
    config_request = cobra.mit.request.ConfigRequest()
    config_request.addMo(tenant)
    session.commit(config_request)

    print("\nNew Tenant, {}, has been created:\n\n{}\n".format(TENANT, config_request.data))


if __name__ == '__main__':
    main()
