import sys
from fabric.api import settings, env, task, hide, local
sys.path.append('..')
from fabfile.awego.helpers import *
from fabfile.awego.color import green, turquoise
import json, boto.ec2

env.use_ssh_config = True

#===========#
#	Tasks	#
#===========#
@task
def regions():# {{{
	for r in boto.ec2.regions():
		print(green(r.name))
#	for r in getregions():
#		print(green(r))
# }}}
@task
def keys():# {{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoVpc(region)
			keys = b.bc.get_all_key_pairs() if b.bc else ""
			for key in keys:
				print(turquoise(str(key.name) + " => " + str(key.fingerprint)))

# }}}
@task
def vpc():#{{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoVpc(region)
			vpcs = b.bc.get_all_vpcs() if b.bc else ""
			for vpc in vpcs:
				print("%s %s %s %s" % (vpc.id,vpc.state,vpc.is_default,vpc.cidr_block))
#			print(vpc.__dict__)
#}}}
@task
def sg():  #{{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoEc(region)
			sgs = b.bc.get_all_security_groups() if b.bc else ""
			for sg in sgs:
				print("%s %s %s" % (sg.id, sg.name, sg.description))
  #}}}
@task
def subnet():  #{{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoVpc(region)
			sns = b.bc.get_all_subnets() if b.bc else ""
			for sn in sns:
				print("%s %s %s %s" % (sn.id, sn.cidr_block, sn.vpc_id, sn.state))
  #}}}
@task
def netgw():  #{{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoVpc(region)
			igws = b.bc.get_all_internet_gateways() if b.bc else ""
			for igw in igws:
				#print("%s " % (sn.__dict__))
				print("%s" % (igw.id))
  #}}}
@task
def routetbl():  #{{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoVpc(region)
			rtbls = b.bc.get_all_route_tables() if b.bc else ""
			for rtbl in rtbls:
				#print("%s " % (sn.__dict__))
				print("%s %s %s" % (rtbl.id, rtbl.routes, rtbl.vpc_id))
  #}}}
@task
def route():  #{{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoVpc(region)
			routes = b.bc.get_all_routes() if b.bc else ""
			for route in routess:
				print("%s " % (route.__dict__))
  #}}}
@task
def nic():	#{{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoEc(region)
			ifaces = b.bc.get_all_network_interfaces() if b.bc else ""
			for iface in ifaces:
				print("%s %s %s %s" % (iface.id, iface.status, iface.mac_address, iface.private_ip_address))
  #}}}
@task
def eip():	#{{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoEc(region)
			eips = b.bc.get_all_addresses() if b.bc else ""
			for eip in eips:
				print("%s %s %s" % (eip.public_ip, eip.allocation_id, eip.association_id))
  #}}}
@task
def instances():  #{{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoEc(region)
# kw arg not included in installed version
#			instances = b.bc.get_all_instances(include_all_instances="True") if b.bc else ""
			reservations = b.bc.get_all_instances() if b.bc else ""
			for reservation in reservations:
				for instance in reservation.instances:
					print("%s" % (instance.id))
  #}}}
@task(alias="lsi")
def instance(instanceid, attribute=""):  #{{{
	#TODO: better attrubute display, remove loops to all regions
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoEc(region)
			all_attr=["instanceType",
					"kernel",
					"ramdisk",
					"userData",
					"disableApiTermination",
					"instanceInitiatedShutdownBehavior",
					"rootDeviceName",
					"blockDeviceMapping",
					"productCodes",
					"sourceDestCheck",
					"groupSet",
					"ebsOptimized",
					"sriovNetSupport" ]
			if not attribute == "All":
				attribute = "instanceType" if not attribute else attribute
				try:
					attribs = b.bc.get_instance_attribute(instanceid, attribute)
					print("%s" % attribs._current_value)
				except:
					pass
			else:
				for a in all_attr:
					try:
						attribs = b.bc.get_instance_attribute(instanceid, a)
						print("%s %s" % (a, attribs._current_value))
					except:
						pass
  #}}}
@task
def vol():	#{{{
	#TODO: better attrubute display, remove loops to all regions
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			print(green(region))
			b = BoCoEc(region)
			volumes = b.bc.get_all_volumes() if b.bc else ""
			for volume in volumes:
				print("%s %s %s %s" % (volume.id, volume.status, volume.attach_data.status, volume.attach_data.instance_id))
#				print("%s" % (volume.__dict__))
  #}}}
