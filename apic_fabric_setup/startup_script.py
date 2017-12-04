# list of packages that should be imported for this code to work

import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.ip
import cobra.model.vz
import cobra.model.pol
import cobra.model.vpc
import cobra.model.fvns
import cobra.model.lacp
import cobra.model.phys
import cobra.model.infra
import cobra.model.l3ext
import cobra.model.fabric
from cobra.internal.codec.xmlcodec import toXMLStr
from credentials import *
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("Baselining APIC Simulator for Learning Labs")

print("Setting up Fabric Nodes")

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(URL, LOGIN, PASSWORD)
md = cobra.mit.access.MoDirectory(ls)
md.login()

# the top level object on which operations will be made
topMo = md.lookupByDn("uni/controller/nodeidentpol")

# build the request using cobra syntax
leaf1 = cobra.model.fabric.NodeIdentP(topMo, serial=u'TEP-1-101', nodeId=u'101', name=u'leaf-1')
leaf2 = cobra.model.fabric.NodeIdentP(topMo, serial=u'TEP-1-102', nodeId=u'102', name=u'leaf-2')
spine1 = cobra.model.fabric.NodeIdentP(topMo, serial=u'TEP-1-103', nodeId=u'201', name=u'spine-1')

# commit fabric initialization
c = cobra.mit.request.ConfigRequest()
c.addMo(topMo)
md.commit(c)

print("Configuring Fabric Policies")

# the top level object on which operations will be made
polUni = cobra.model.pol.Uni('')
infraInfra = cobra.model.infra.Infra(polUni)

# build the vlan pools
snv_pool = cobra.model.fvns.VlanInstP(infraInfra, name=u'SnV_general_pool', allocMode=u'static')
snv_range = cobra.model.fvns.EncapBlk(snv_pool, to=u'vlan-199', from_=u'vlan-100')

heroes_pool = cobra.model.fvns.VlanInstP(infraInfra, name=u'Heroes_general_pool', allocMode=u'static')
heroes_range = cobra.model.fvns.EncapBlk(heroes_pool, to=u'vlan-299', from_=u'vlan-200')

# build the phys domain
snv_phys_domain = cobra.model.phys.DomP(polUni, name=u'SnV_phys')
infraRsVlanNs = cobra.model.infra.RsVlanNs(snv_phys_domain, tDn=u'uni/infra/vlanns-[SnV_general_pool]-static')

heroes_phys_domain = cobra.model.phys.DomP(polUni, name=u'Heroes_phys')
infraRsVlanNs = cobra.model.infra.RsVlanNs(heroes_phys_domain, tDn=u'uni/infra/vlanns-[Heroes_general_pool]-static')

# build the l3ext domain
snv_l3ext_domain = cobra.model.l3ext.DomP(polUni, name=u'SnV_external_corporate')

heroes_l3ext_domain = cobra.model.l3ext.DomP(polUni, name=u'Heroes_external_corporate')

# build phys aaep
snv_aaep_phys = cobra.model.infra.AttEntityP(infraInfra, name=u'SnV_phys')
snv_aaep_phys_domain = cobra.model.infra.RsDomP(snv_aaep_phys, tDn=u'uni/phys-SnV_phys')
snv_aaep_phys_infra = cobra.model.infra.FuncP(infraInfra)

heroes_aaep_phys = cobra.model.infra.AttEntityP(infraInfra, name=u'Heroes_phys')
heroes_aaep_phys_domain = cobra.model.infra.RsDomP(heroes_aaep_phys, tDn=u'uni/phys-Heroes_phys')
heroes_aaep_phys_infra = cobra.model.infra.FuncP(infraInfra)

# build l3ext aaep
snv_aaep_l3ext = cobra.model.infra.AttEntityP(infraInfra, name=u'SnV_corporate_external')
snv_aaep_l3ext_domain = cobra.model.infra.RsDomP(snv_aaep_l3ext, tDn=u'uni/l3dom-SnV_external_corporate')
snv_aaep_l3ext_infra = cobra.model.infra.FuncP(infraInfra)

heroes_aaep_l3ext = cobra.model.infra.AttEntityP(infraInfra, name=u'Heroes_corporate_external')
heroes_aaep_l3ext_domain = cobra.model.infra.RsDomP(heroes_aaep_l3ext, tDn=u'uni/l3dom-Heroes_external_corporate')
heroes_aaep_l3ext_infra = cobra.model.infra.FuncP(infraInfra)

# build the lacp active policy
lacpLagPol = cobra.model.lacp.LagPol(infraInfra, name=u'lacp_active', ctrl=u'fast-sel-hot-stdby,graceful-conv,susp-individual', mode=u'active')

# build the interface policy groups
infraFuncP = cobra.model.infra.FuncP(infraInfra)

snv_standard_pg = cobra.model.infra.AccPortGrp(infraFuncP, name=u'SnV_standard_access')
snv_standard_aaep = cobra.model.infra.RsAttEntP(snv_standard_pg, tDn=u'uni/infra/attentp-SnV_phys')

heroes_standard_pg = cobra.model.infra.AccPortGrp(infraFuncP, name=u'Heroes_standard_access')
heroes_standard_aaep = cobra.model.infra.RsAttEntP(heroes_standard_pg, tDn=u'uni/infra/attentp-Heroes_phys')

snv_corp_ext_pg = cobra.model.infra.AccPortGrp(infraFuncP, name=u'SnV_corporate_external')
snv_corp_ext_aaep = cobra.model.infra.RsAttEntP(snv_corp_ext_pg, tDn=u'uni/infra/attentp-SnV_corporate_external')

heroes_corp_ext_pg = cobra.model.infra.AccPortGrp(infraFuncP, name=u'Heroes_corporate_external')
heroes_corp_ext_aaep = cobra.model.infra.RsAttEntP(heroes_corp_ext_pg, tDn=u'uni/infra/attentp-Heroes_corporate_external')

fi1a_bundle = cobra.model.infra.AccBndlGrp(infraFuncP, lagT=u'node', name=u'SnV_FI-1A')
fi1a_aaep = cobra.model.infra.RsAttEntP(fi1a_bundle, tDn=u'uni/infra/attentp-SnV_phys')
fi1a_lacp = cobra.model.infra.RsLacpPol(fi1a_bundle, tnLacpLagPolName=u'lacp_active')

fi1b_bundle = cobra.model.infra.AccBndlGrp(infraFuncP, lagT=u'node', name=u'SnV_FI-1B')
fi1b_aaep = cobra.model.infra.RsAttEntP(fi1b_bundle, tDn=u'uni/infra/attentp-SnV_phys')
fi1b_lacp = cobra.model.infra.RsLacpPol(fi1b_bundle, tnLacpLagPolName=u'lacp_active')

fi2a_bundle = cobra.model.infra.AccBndlGrp(infraFuncP, lagT=u'node', name=u'Heroes_FI-2A')
fi2a_aaep = cobra.model.infra.RsAttEntP(fi2a_bundle, tDn=u'uni/infra/attentp-Heroes_phys')
fi2a_lacp = cobra.model.infra.RsLacpPol(fi2a_bundle, tnLacpLagPolName=u'lacp_active')

fi2b_bundle = cobra.model.infra.AccBndlGrp(infraFuncP, lagT=u'node', name=u'Heroes_FI-2B')
fi2b_aaep = cobra.model.infra.RsAttEntP(fi2b_bundle, tDn=u'uni/infra/attentp-Heroes_phys')
fi2b_lacp = cobra.model.infra.RsLacpPol(fi2b_bundle, tnLacpLagPolName=u'lacp_active')

# build the interface profiles
snv_corp_ext_acc = cobra.model.infra.AccPortP(infraInfra, name=u'SnV_corporate_external')
snv_corp_ext_phys_port = cobra.model.infra.HPortS(snv_corp_ext_acc, name=u'ethernet1_48', type='range')
snv_corp_ext_port_range = cobra.model.infra.PortBlk(snv_corp_ext_phys_port, name=u'block2', fromPort=u'48', toPort=u'48')
snv_corp_ext_config = cobra.model.infra.RsAccBaseGrp(snv_corp_ext_phys_port, tDn=u'uni/infra/funcprof/accportgrp-SnV_corporate_external')

heroes_corp_ext_acc = cobra.model.infra.AccPortP(infraInfra, name=u'Heroes_corporate_external')
heroes_corp_ext_phys_port = cobra.model.infra.HPortS(heroes_corp_ext_acc, name=u'ethernet1_47', type='range')
heroes_corp_ext_port_range = cobra.model.infra.PortBlk(heroes_corp_ext_phys_port, name=u'block2', fromPort=u'47', toPort=u'47')
heroes_corp_ext_config = cobra.model.infra.RsAccBaseGrp(heroes_corp_ext_phys_port, tDn=u'uni/infra/funcprof/accportgrp-Heroes_corporate_external')

snv_server1_acc = cobra.model.infra.AccPortP(infraInfra, name=u'SnV_server1')
snv_server1_phys_port = cobra.model.infra.HPortS(snv_server1_acc, name=u'ethernet1_1', type='range')
snv_server1_port_range = cobra.model.infra.PortBlk(snv_server1_phys_port, name=u'block2', fromPort=u'1', toPort=u'1')
snv_server1_config = cobra.model.infra.RsAccBaseGrp(snv_server1_phys_port, tDn=u'uni/infra/funcprof/accportgrp-SnV_standard_access')

snv_server2_acc = cobra.model.infra.AccPortP(infraInfra, name=u'SnV_server2')
snv_server2_phys_port = cobra.model.infra.HPortS(snv_server2_acc, name=u'ethernet1_1', type='range')
snv_server2_port_range = cobra.model.infra.PortBlk(snv_server2_phys_port, name=u'block2', fromPort=u'1', toPort=u'1')
snv_server2_config = cobra.model.infra.RsAccBaseGrp(snv_server2_phys_port, tDn=u'uni/infra/funcprof/accportgrp-SnV_standard_access')

snv_act_pass_acc = cobra.model.infra.AccPortP(infraInfra, name=u'SnV_phys_act_pass')
snv_act_pass_phys_ports = cobra.model.infra.HPortS(snv_act_pass_acc, name=u'ethernet1_2-4', type='range')
snv_act_pass_port_range = cobra.model.infra.PortBlk(snv_act_pass_phys_ports, name=u'block2', fromPort=u'2', toPort=u'4')
snv_act_pass_config = cobra.model.infra.RsAccBaseGrp(snv_act_pass_phys_ports, tDn=u'uni/infra/funcprof/accportgrp-SnV_standard_access')

heroes_server1_acc = cobra.model.infra.AccPortP(infraInfra, name=u'Heroes_server1')
heroes_server1_phys_port = cobra.model.infra.HPortS(heroes_server1_acc, name=u'ethernet1_21', type='range')
heroes_server1_port_range = cobra.model.infra.PortBlk(heroes_server1_phys_port, name=u'block2', fromPort=u'21', toPort=u'21')
heroes_server1_config = cobra.model.infra.RsAccBaseGrp(heroes_server1_phys_port, tDn=u'uni/infra/funcprof/accportgrp-Heroes_standard_access')

heroes_server2_acc = cobra.model.infra.AccPortP(infraInfra, name=u'Heroes_server2')
heroes_server2_phys_port = cobra.model.infra.HPortS(heroes_server2_acc, name=u'ethernet1_21', type='range')
heroes_server2_port_range = cobra.model.infra.PortBlk(heroes_server2_phys_port, name=u'block2', fromPort=u'21', toPort=u'21')
heroes_server2_config = cobra.model.infra.RsAccBaseGrp(heroes_server2_phys_port, tDn=u'uni/infra/funcprof/accportgrp-Heroes_standard_access')

heroes_act_pass_acc = cobra.model.infra.AccPortP(infraInfra, name=u'Heroes_phys_act_pass')
heroes_act_pass_phys_ports = cobra.model.infra.HPortS(heroes_act_pass_acc, name=u'ethernet1_22-24', type='range')
heroes_act_pass_port_range = cobra.model.infra.PortBlk(heroes_act_pass_phys_ports, name=u'block2', fromPort=u'22', toPort=u'24')
heroes_act_pass_config = cobra.model.infra.RsAccBaseGrp(heroes_act_pass_phys_ports, tDn=u'uni/infra/funcprof/accportgrp-Heroes_standard_access')

fi1a_acc = cobra.model.infra.AccPortP(infraInfra, name=u'SnV_FI-1A')
fi1a_phys_ports = cobra.model.infra.HPortS(fi1a_acc, name=u'ethernet1_5-8', type='range')
fi1a_port_range = cobra.model.infra.PortBlk(fi1a_phys_ports, name=u'block2', fromPort=u'5', toPort=u'8')
fi1a_config = cobra.model.infra.RsAccBaseGrp(fi1a_phys_ports, tDn=u'uni/infra/funcprof/accbundle-SnV_FI-1A')

fi1b_acc = cobra.model.infra.AccPortP(infraInfra, name=u'SnV_FI-1B')
fi1b_phys_ports = cobra.model.infra.HPortS(fi1b_acc, name=u'ethernet1_9-12', type='range')
fi1b_port_range = cobra.model.infra.PortBlk(fi1b_phys_ports, name=u'block2', fromPort=u'9', toPort=u'12')
fi1b_confige = cobra.model.infra.RsAccBaseGrp(fi1b_phys_ports, tDn=u'uni/infra/funcprof/accbundle-SnV_FI-1B')

fi2a_acc = cobra.model.infra.AccPortP(infraInfra, name=u'Heroes_FI-2A')
fi2a_phys_ports = cobra.model.infra.HPortS(fi2a_acc, name=u'ethernet1_13-16', type='range')
fi2a_port_range = cobra.model.infra.PortBlk(fi2a_phys_ports, name=u'block2', fromPort=u'13', toPort=u'16')
fi2a_config = cobra.model.infra.RsAccBaseGrp(fi2a_phys_ports, tDn=u'uni/infra/funcprof/accbundle-Heroes_FI-2A')

fi2b_acc = cobra.model.infra.AccPortP(infraInfra, name=u'Heroes_FI-2B')
fi2b_phys_ports = cobra.model.infra.HPortS(fi2b_acc, name=u'ethernet1_17-20', type='range')
fi2b_port_range = cobra.model.infra.PortBlk(fi2b_phys_ports, name=u'block2', fromPort=u'17', toPort=u'20')
fi2b_confige = cobra.model.infra.RsAccBaseGrp(fi2b_phys_ports, tDn=u'uni/infra/funcprof/accbundle-Heroes_FI-2B')

# build the switch profiles and attach interfaces
leaf1 = cobra.model.infra.NodeP(infraInfra, name=u'leaf_1')
leaf1_name = cobra.model.infra.LeafS(leaf1, type=u'range', name=u'leaf_1')
leaf1_range = cobra.model.infra.NodeBlk(leaf1_name, to_=u'101', from_=u'101', name=u'b235d75799f7d020')
leaf1_intfc1 = cobra.model.infra.RsAccPortP(leaf1, tDn=u'uni/infra/accportprof-SnV_server1')
leaf1_intfc2 = cobra.model.infra.RsAccPortP(leaf1, tDn=u'uni/infra/accportprof-Heroes_server1')

leaf2 = cobra.model.infra.NodeP(infraInfra, name=u'leaf_2')
leaf2_name = cobra.model.infra.LeafS(leaf2, type=u'range', name=u'leaf_2')
leaf2_range = cobra.model.infra.NodeBlk(leaf2_name, to_=u'102', from_=u'102', name=u'9ebfdd3979c07bcf')
leaf2_intfc1 = cobra.model.infra.RsAccPortP(leaf2, tDn=u'uni/infra/accportprof-SnV_server2')
leaf2_intfc2 = cobra.model.infra.RsAccPortP(leaf2, tDn=u'uni/infra/accportprof-Heroes_server2')

leafs12 = cobra.model.infra.NodeP(infraInfra, name=u'leafs_1-2')
leafs12_name = cobra.model.infra.LeafS(leafs12, type=u'range', name=u'leafs_1-2')
leafs12_range = cobra.model.infra.NodeBlk(leafs12_name, to_=u'102', from_=u'101', name=u'50b60d7cf265710f')
leafs12_intfc1 = cobra.model.infra.RsAccPortP(leafs12, tDn=u'uni/infra/accportprof-SnV_FI-1A')
leafs12_intfc2 = cobra.model.infra.RsAccPortP(leafs12, tDn=u'uni/infra/accportprof-SnV_FI-1B')
leafs12_intfc3 = cobra.model.infra.RsAccPortP(leafs12, tDn=u'uni/infra/accportprof-SnV_corporate_external')
leafs12_intfc4 = cobra.model.infra.RsAccPortP(leafs12, tDn=u'uni/infra/accportprof-SnV_phys_act_pass')
leafs12_intfc5 = cobra.model.infra.RsAccPortP(leafs12, tDn=u'uni/infra/accportprof-Heroes_FI-2A')
leafs12_intfc6 = cobra.model.infra.RsAccPortP(leafs12, tDn=u'uni/infra/accportprof-Heroes_FI-2B')
leafs12_intfc7 = cobra.model.infra.RsAccPortP(leafs12, tDn=u'uni/infra/accportprof-Heroes_corporate_external')
leafs12_intfc8 = cobra.model.infra.RsAccPortP(leafs12, tDn=u'uni/infra/accportprof-Heroes_phys_act_pass')

# setup the vpc
fabricInst = cobra.model.fabric.Inst(polUni)
vpcInstPol = cobra.model.vpc.InstPol(fabricInst, name=u'leafs_1-2')

# build the vpc domain
fabricProtPol = cobra.model.fabric.ProtPol(fabricInst)
fabricExplicitGEp = cobra.model.fabric.ExplicitGEp(fabricProtPol, name=u'leafs_1-2', id=u'12')
fabricNodePEp = cobra.model.fabric.NodePEp(fabricExplicitGEp, id=u'101')
fabricNodePEp2 = cobra.model.fabric.NodePEp(fabricExplicitGEp, id=u'102')
fabricRsVpcInstPol = cobra.model.fabric.RsVpcInstPol(fabricExplicitGEp, tnVpcInstPolName=u'leafs_1-2')



# commit infraInfra
c = cobra.mit.request.ConfigRequest()
#c.addMo(polUni)
c.addMo(infraInfra)
md.commit(c)

# commit snv phys domain
c = cobra.mit.request.ConfigRequest()
c.addMo(snv_phys_domain)
md.commit(c)

# commit heroes phys domain
c = cobra.mit.request.ConfigRequest()
c.addMo(heroes_phys_domain)
md.commit(c)

# commit snv l3ext domain
c = cobra.mit.request.ConfigRequest()
c.addMo(snv_l3ext_domain)
md.commit(c)

# commit heroes l3ext domain
c = cobra.mit.request.ConfigRequest()
c.addMo(heroes_l3ext_domain)
md.commit(c)

# commit the vpc configs
c = cobra.mit.request.ConfigRequest()
c.addMo(fabricProtPol)
c.addMo(vpcInstPol)
md.commit(c)

print("Setting up Common Tenant")

# build the contracts and filters in common
common_tenant = cobra.model.fv.Tenant(polUni, ownerKey=u'', name=u'common', descr=u'', ownerTag=u'')

vzFilter = cobra.model.vz.Filter(common_tenant, ownerKey=u'', name=u'power_up', descr=u'', ownerTag=u'')
vzEntry = cobra.model.vz.Entry(vzFilter, tcpRules=u'', arpOpc=u'unspecified', applyToFrag=u'no', dToPort=u'9002', descr=u'', prot=u'tcp', icmpv4T=u'unspecified', sFromPort=u'unspecified', stateful=u'no', icmpv6T=u'unspecified', sToPort=u'unspecified', etherT=u'ip', dFromPort=u'9001', name=u'tcp_9001-9002')
vzFilter2 = cobra.model.vz.Filter(common_tenant, ownerKey=u'', name=u'http', descr=u'', ownerTag=u'')
vzEntry2 = cobra.model.vz.Entry(vzFilter2, tcpRules=u'', arpOpc=u'unspecified', applyToFrag=u'no', dToPort=u'http', descr=u'', prot=u'tcp', icmpv4T=u'unspecified', sFromPort=u'unspecified', stateful=u'no', icmpv6T=u'unspecified', sToPort=u'unspecified', etherT=u'ip', dFromPort=u'http', name=u'tcp-80')
vzFilter3 = cobra.model.vz.Filter(common_tenant, ownerKey=u'', name=u'https', descr=u'', ownerTag=u'')
vzEntry3 = cobra.model.vz.Entry(vzFilter3, tcpRules=u'', arpOpc=u'unspecified', applyToFrag=u'no', dToPort=u'https', descr=u'', prot=u'tcp', icmpv4T=u'unspecified', sFromPort=u'unspecified', stateful=u'no', icmpv6T=u'unspecified', sToPort=u'unspecified', etherT=u'ip', dFromPort=u'https', name=u'tcp-443')
vzFilter4 = cobra.model.vz.Filter(common_tenant, ownerKey=u'', name=u'sql_browser', descr=u'', ownerTag=u'')
vzEntry4 = cobra.model.vz.Entry(vzFilter4, tcpRules=u'', arpOpc=u'unspecified', applyToFrag=u'no', dToPort=u'1434', descr=u'', prot=u'udp', icmpv4T=u'unspecified', sFromPort=u'unspecified', stateful=u'no', icmpv6T=u'unspecified', sToPort=u'unspecified', etherT=u'ip', dFromPort=u'1434', name=u'udp-1434')
vzFilter5 = cobra.model.vz.Filter(common_tenant, ownerKey=u'', name=u'sql_server', descr=u'', ownerTag=u'')
vzEntry5 = cobra.model.vz.Entry(vzFilter5, tcpRules=u'', arpOpc=u'unspecified', applyToFrag=u'no', dToPort=u'1433', descr=u'', prot=u'tcp', icmpv4T=u'unspecified', sFromPort=u'unspecified', stateful=u'no', icmpv6T=u'unspecified', sToPort=u'unspecified', etherT=u'ip', dFromPort=u'1433', name=u'tcp-1433')

vzBrCP = cobra.model.vz.BrCP(common_tenant, ownerKey=u'', name=u'web', prio=u'unspecified', ownerTag=u'', descr=u'')
vzSubj = cobra.model.vz.Subj(vzBrCP, revFltPorts=u'yes', name=u'http', prio=u'unspecified', descr=u'', consMatchT=u'AtleastOne', provMatchT=u'AtleastOne')
vzRsSubjFiltAtt = cobra.model.vz.RsSubjFiltAtt(vzSubj, tnVzFilterName=u'http')
vzSubj2 = cobra.model.vz.Subj(vzBrCP, revFltPorts=u'yes', name=u'https', prio=u'unspecified', descr=u'', consMatchT=u'AtleastOne', provMatchT=u'AtleastOne')
vzRsSubjFiltAtt2 = cobra.model.vz.RsSubjFiltAtt(vzSubj2, tnVzFilterName=u'https')
vzBrCP2 = cobra.model.vz.BrCP(common_tenant, ownerKey=u'', name=u'power_up', prio=u'unspecified', ownerTag=u'', descr=u'')
vzSubj3 = cobra.model.vz.Subj(vzBrCP2, revFltPorts=u'yes', name=u'app_ports', prio=u'unspecified', descr=u'', consMatchT=u'AtleastOne', provMatchT=u'AtleastOne')
vzRsSubjFiltAtt3 = cobra.model.vz.RsSubjFiltAtt(vzSubj3, tnVzFilterName=u'power_up')
vzBrCP3 = cobra.model.vz.BrCP(common_tenant, ownerKey=u'', name=u'sql', prio=u'unspecified', ownerTag=u'', descr=u'', scope=u'application-profile')
vzSubj4 = cobra.model.vz.Subj(vzBrCP3, revFltPorts=u'yes', name=u'sql-server', prio=u'unspecified', descr=u'', consMatchT=u'AtleastOne', provMatchT=u'AtleastOne')
vzRsSubjFiltAtt4 = cobra.model.vz.RsSubjFiltAtt(vzSubj4, tnVzFilterName=u'sql_server')
vzSubj5 = cobra.model.vz.Subj(vzBrCP3, revFltPorts=u'yes', name=u'sql-browser', prio=u'unspecified', descr=u'', consMatchT=u'AtleastOne', provMatchT=u'AtleastOne')
vzRsSubjFiltAtt5 = cobra.model.vz.RsSubjFiltAtt(vzSubj5, tnVzFilterName=u'sql_browser')

print("Setting up Heroes Tenant")

# build the heroes tenant
fvTenant = cobra.model.fv.Tenant(polUni, ownerKey=u'', name=u'Heroes', descr=u'', ownerTag=u'')
fvCtx = cobra.model.fv.Ctx(fvTenant, ownerKey=u'', name=u'Heroes_Only', descr=u'', knwMcastAct=u'permit', pcEnfDir=u'ingress', ownerTag=u'', pcEnfPref=u'enforced')
fvRsCtxToExtRouteTagPol = cobra.model.fv.RsCtxToExtRouteTagPol(fvCtx, tnL3extRouteTagPolName=u'')
fvRsBgpCtxPol = cobra.model.fv.RsBgpCtxPol(fvCtx, tnBgpCtxPolName=u'')
vzAny = cobra.model.vz.Any(fvCtx, matchT=u'AtleastOne', name=u'', descr=u'')
fvRsOspfCtxPol = cobra.model.fv.RsOspfCtxPol(fvCtx, tnOspfCtxPolName=u'')
fvRsCtxToEpRet = cobra.model.fv.RsCtxToEpRet(fvCtx, tnFvEpRetPolName=u'')
fvBD = cobra.model.fv.BD(fvTenant, ownerKey=u'', vmac=u'not-applicable', name=u'Hero_Land', descr=u'', unkMacUcastAct=u'proxy', arpFlood=u'no', limitIpLearnToSubnets=u'yes', llAddr=u'::', mac=u'00:22:BD:F8:19:FF', epMoveDetectMode=u'', unicastRoute=u'yes', ownerTag=u'', multiDstPktAct=u'bd-flood', unkMcastAct=u'flood')
fvRsBDToNdP = cobra.model.fv.RsBDToNdP(fvBD, tnNdIfPolName=u'')
fvRsCtx = cobra.model.fv.RsCtx(fvBD, tnFvCtxName=u'Heroes_Only')
fvRsIgmpsn = cobra.model.fv.RsIgmpsn(fvBD, tnIgmpSnoopPolName=u'')
fvSubnet = cobra.model.fv.Subnet(fvBD, name=u'', descr=u'', ctrl=u'', ip=u'10.1.120.1/22', preferred=u'no', virtual=u'no', scope=u'public')
fvSubnet2 = cobra.model.fv.Subnet(fvBD, name=u'', descr=u'', ctrl=u'', ip=u'192.168.120.1/22', preferred=u'no', virtual=u'no')
fvRsBdToEpRet = cobra.model.fv.RsBdToEpRet(fvBD, resolveAct=u'resolve', tnFvEpRetPolName=u'')
fvRsTenantMonPol = cobra.model.fv.RsTenantMonPol(fvTenant, tnMonEPGPolName=u'')
fvAp = cobra.model.fv.Ap(fvTenant, ownerKey=u'', prio=u'unspecified', name=u'Save_The_Planet', descr=u'', ownerTag=u'')
fvAEPg1 = cobra.model.fv.AEPg(fvAp, isAttrBasedEPg=u'no', matchT=u'AtleastOne', prio=u'unspecified', name=u'web', descr=u'')
fvRsProv1 = cobra.model.fv.RsProv(fvAEPg1, tnVzBrCPName=u'web', matchT=u'AtleastOne', prio=u'unspecified')
fvRsCons1 = cobra.model.fv.RsCons(fvAEPg1, tnVzBrCPName=u'sql', prio=u'unspecified')
fvRsPathAtt1 = cobra.model.fv.RsPathAtt(fvAEPg1, tDn=u'topology/pod-1/protpaths-101-102/pathep-[Heroes_FI-2B]', instrImedcy=u'lazy', encap=u'vlan-200', descr=u'', mode=u'regular')
fvRsPathAtt4 = cobra.model.fv.RsPathAtt(fvAEPg1, tDn=u'topology/pod-1/protpaths-101-102/pathep-[Heroes_FI-2A]', instrImedcy=u'lazy', encap=u'vlan-200', descr=u'', mode=u'regular')
fvRsDomAtt1 = cobra.model.fv.RsDomAtt(fvAEPg1, instrImedcy=u'lazy', resImedcy=u'lazy', encap=u'unknown', tDn=u'uni/phys-Heroes_phys')
fvAEPg2 = cobra.model.fv.AEPg(fvAp, isAttrBasedEPg=u'no', matchT=u'AtleastOne', prio=u'unspecified', name=u'app', descr=u'')
fvRsProv2 = cobra.model.fv.RsProv(fvAEPg2, tnVzBrCPName=u'power_up', matchT=u'AtleastOne', prio=u'unspecified')
fvRsCons2 = cobra.model.fv.RsCons(fvAEPg2, tnVzBrCPName=u'sql', prio=u'unspecified')
fvRsPathAtt5 = cobra.model.fv.RsPathAtt(fvAEPg2, tDn=u'topology/pod-1/protpaths-101-102/pathep-[Heroes_FI-2B]', instrImedcy=u'lazy', encap=u'vlan-201', descr=u'', mode=u'regular')
fvRsPathAtt6 = cobra.model.fv.RsPathAtt(fvAEPg2, tDn=u'topology/pod-1/protpaths-101-102/pathep-[Heroes_FI-2A]', instrImedcy=u'lazy', encap=u'vlan-201', descr=u'', mode=u'regular')
fvRsDomAtt2 = cobra.model.fv.RsDomAtt(fvAEPg2, instrImedcy=u'lazy', resImedcy=u'lazy', encap=u'unknown', tDn=u'uni/phys-Heroes_phys')
fvAEPg3 = cobra.model.fv.AEPg(fvAp, isAttrBasedEPg=u'no', matchT=u'AtleastOne', prio=u'unspecified', name=u'db', descr=u'')
fvRsProv3 = cobra.model.fv.RsProv(fvAEPg3, tnVzBrCPName=u'sql', matchT=u'AtleastOne', prio=u'unspecified')
fvRsPathAtt5 = cobra.model.fv.RsPathAtt(fvAEPg3, tDn=u'topology/pod-1/protpaths-101-102/pathep-[Heroes_FI-2B]', instrImedcy=u'lazy', encap=u'vlan-202', descr=u'', mode=u'regular')
fvRsPathAtt6 = cobra.model.fv.RsPathAtt(fvAEPg3, tDn=u'topology/pod-1/protpaths-101-102/pathep-[Heroes_FI-2A]', instrImedcy=u'lazy', encap=u'vlan-202', descr=u'', mode=u'regular')
fvRsDomAtt3 = cobra.model.fv.RsDomAtt(fvAEPg3, instrImedcy=u'lazy', resImedcy=u'lazy', encap=u'unknown', tDn=u'uni/phys-Heroes_phys')
fvRsCustQosPol1 = cobra.model.fv.RsCustQosPol(fvAEPg1, tnQosCustomPolName=u'')
fvRsBd1 = cobra.model.fv.RsBd(fvAEPg1, tnFvBDName=u'Hero_Land')
fvRsCustQosPol2 = cobra.model.fv.RsCustQosPol(fvAEPg2, tnQosCustomPolName=u'')
fvRsBd2 = cobra.model.fv.RsBd(fvAEPg2, tnFvBDName=u'Hero_Land')
fvRsCustQosPol3 = cobra.model.fv.RsCustQosPol(fvAEPg3, tnQosCustomPolName=u'')
fvRsBd3 = cobra.model.fv.RsBd(fvAEPg3, tnFvBDName=u'Hero_Land')
l3extOut = cobra.model.l3ext.Out(fvTenant, ownerKey=u'', name=u'Heroes_external_corporate', descr=u'', targetDscp=u'unspecified', enforceRtctrl=u'export', ownerTag=u'')
l3extRsEctx = cobra.model.l3ext.RsEctx(l3extOut, tnFvCtxName=u'Heroes_Only')
l3extLNodeP = cobra.model.l3ext.LNodeP(l3extOut, ownerKey=u'', name=u'borderleaf_2_corporate', descr=u'', targetDscp=u'unspecified', tag=u'yellow-green', ownerTag=u'')
l3extRsNodeL3OutAtt = cobra.model.l3ext.RsNodeL3OutAtt(l3extLNodeP, rtrIdLoopBack=u'yes', rtrId=u'10.1.100.2', tDn=u'topology/pod-1/node-102')
ipRouteP = cobra.model.ip.RouteP(l3extRsNodeL3OutAtt, aggregate=u'no', ip=u'0.0.0.0/0', pref=u'1', name=u'', descr=u'')
ipNexthopP = cobra.model.ip.NexthopP(ipRouteP, nhAddr=u'10.1.2.2', pref=u'unspecified', name=u'', descr=u'')
l3extLIfP = cobra.model.l3ext.LIfP(l3extLNodeP, ownerKey=u'', tag=u'yellow-green', name=u'borderleaf_2', descr=u'', ownerTag=u'')
l3extRsNdIfPol = cobra.model.l3ext.RsNdIfPol(l3extLIfP, tnNdIfPolName=u'')
l3extRsPathL3OutAtt = cobra.model.l3ext.RsPathL3OutAtt(l3extLIfP, addr=u'10.1.200.3/31', descr=u'', encapScope=u'local', targetDscp=u'unspecified', llAddr=u'::', mac=u'00:22:BD:F8:19:FF', mode=u'regular', encap=u'unknown', ifInstT=u'l3-port', mtu=u'inherit', tDn=u'topology/pod-1/paths-102/pathep-[eth1/47]')
l3extLNodeP2 = cobra.model.l3ext.LNodeP(l3extOut, ownerKey=u'', name=u'borderleaf_1_corporate', descr=u'', targetDscp=u'unspecified', tag=u'yellow-green', ownerTag=u'')
l3extRsNodeL3OutAtt2 = cobra.model.l3ext.RsNodeL3OutAtt(l3extLNodeP2, rtrIdLoopBack=u'yes', rtrId=u'10.1.100.1', tDn=u'topology/pod-1/node-101')
ipRouteP2 = cobra.model.ip.RouteP(l3extRsNodeL3OutAtt2, aggregate=u'no', ip=u'0.0.0.0/0', pref=u'1', name=u'', descr=u'')
ipNexthopP2 = cobra.model.ip.NexthopP(ipRouteP2, nhAddr=u'10.1.200.0', pref=u'unspecified', name=u'', descr=u'')
l3extLIfP2 = cobra.model.l3ext.LIfP(l3extLNodeP2, ownerKey=u'', tag=u'yellow-green', name=u'borderleaf_1', descr=u'', ownerTag=u'')
l3extRsNdIfPol2 = cobra.model.l3ext.RsNdIfPol(l3extLIfP2, tnNdIfPolName=u'')
l3extRsPathL3OutAtt2 = cobra.model.l3ext.RsPathL3OutAtt(l3extLIfP2, addr=u'10.1.200.1/31', descr=u'', encapScope=u'local', targetDscp=u'unspecified', llAddr=u'::', mac=u'00:22:BD:F8:19:FF', mode=u'regular', encap=u'unknown', ifInstT=u'l3-port', mtu=u'inherit', tDn=u'topology/pod-1/paths-101/pathep-[eth1/47]')
l3extRsL3DomAtt = cobra.model.l3ext.RsL3DomAtt(l3extOut, tDn=u'uni/l3dom-Heroes_external_corporate')
l3extInstP = cobra.model.l3ext.InstP(l3extOut, prio=u'unspecified', matchT=u'AtleastOne', name=u'Heroes_default', descr=u'', targetDscp=u'unspecified')
fvRsCons4 = cobra.model.fv.RsCons(l3extInstP, tnVzBrCPName=u'power_up', prio=u'unspecified')
fvRsCons5 = cobra.model.fv.RsCons(l3extInstP, tnVzBrCPName=u'web', prio=u'unspecified')
l3extSubnet = cobra.model.l3ext.Subnet(l3extInstP, aggregate=u'', ip=u'0.0.0.0/0', name=u'', descr=u'')
fvRsCustQosPol5 = cobra.model.fv.RsCustQosPol(l3extInstP, tnQosCustomPolName=u'')


# commit the generated code to APIC
c = cobra.mit.request.ConfigRequest()
c.addMo(common_tenant)
md.commit(c)

c = cobra.mit.request.ConfigRequest()
c.addMo(fvTenant)
md.commit(c)
