from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import ConfigRequest
from cobra.model import fabric, lldp  # Adjusted imports based on available modules
import urllib3
from credentials import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_existing_policies(md, dn_list):
    existing_policies = {}
    for dn in dn_list:
        try:
            mo = md.lookupByDn(dn)
            if mo:
                existing_policies[dn] = mo
                print(f"Found existing policy: {dn}")
            else:
                print(f"Policy not found: {dn}")
        except Exception as e:
            print(f"Error retrieving {dn}: {e}")
    return existing_policies


def create_or_update_fabric_node_ident(
    parent_mo, serial, node_id, name, existing_policies
):
    dn = f"uni/controller/nodeidentpol/nodep-{serial}"

    if dn in existing_policies:
        print(f"Updating existing policy: {name} with DN: {dn}")
        node_ident = existing_policies[dn]
        # Since nodeId and serial are create-only, we do not update them for existing nodes
        print(f"Existing Node Ident {name} found. Skipping serial and nodeId update.")
    else:
        print(f"Creating new Node Ident: {name} with DN: {dn}")
        try:
            node_ident = fabric.NodeIdentPol(
                parent_mo, serial=serial, nodeId=node_id, name=name
            )
        except AttributeError:
            print(f"NodeIdentPol not found. Check cobra library version or class name.")
            # Handle the situation or provide fallback logic
            node_ident = None  # or any other appropriate fallback
    return node_ident


def configure_apic():
    print("Baselining APIC Simulator for Learning Labs")

    # Log in to the APIC
    print("\nConfiguring APIC...\n")
    ls = LoginSession(URL, LOGIN, PASSWORD)
    md = MoDirectory(ls)
    md.login()

    # Fabric Node Setup
    print("Setting up Fabric Nodes")
    existing_policies_dn = [
        "uni/controller/nodeidentpol/nodep-TEP-1-101",
        "uni/controller/nodeidentpol/nodep-TEP-1-102",
        "uni/controller/nodeidentpol/nodep-TEP-1-103",
    ]
    existing_policies = get_existing_policies(md, existing_policies_dn)

    nodes = {
        "leaf-1": {"serial": "TEP-1-101", "nodeId": "101", "name": "leaf-1"},
        "leaf-2": {"serial": "TEP-1-102", "nodeId": "102", "name": "leaf-2"},
        "spine-1": {"serial": "TEP-1-103", "nodeId": "1001", "name": "spine-1"},
    }

    parent_dn = "uni/controller/nodeidentpol"
    parent_mo = md.lookupByDn(parent_dn)

    c = ConfigRequest()
    for key, attrs in nodes.items():
        node_mo = create_or_update_fabric_node_ident(
            parent_mo,
            attrs["serial"],
            attrs["nodeId"],
            attrs["name"],
            existing_policies,
        )
        if node_mo:
            c.addMo(node_mo)
            print(f"Added {attrs['name']} to ConfigRequest")

    if c.configMos:
        try:
            response = md.commit(c)
            print("\nConfiguration committed successfully.")
            print("Commit Response:", response)
        except Exception as e:
            print(f"Error committing configuration: {e}")
    else:
        print("No MOs to commit")

    # Fabric Policies Setup (Placeholder)
    print("\nConfiguring Fabric Policies")
    # Add logic for fabric policies here if needed

    # Tenant Setup (Placeholder)
    print("\nSetting up Common Tenant")
    # Add logic for Common Tenant setup here if needed

    print("Setting up Heroes Tenant")
    # Add logic for Heroes Tenant setup here if needed

    print("Setting up SnV Tenant")
    # Add logic for SnV Tenant setup here if needed

    print("\nAPIC setup complete.")


def main():
    configure_apic()


if __name__ == "__main__":
    main()
