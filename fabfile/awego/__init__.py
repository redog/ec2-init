from fabric.api import settings, run, env, task, hide, local
from helpers import *
from color import red, blue, green, turquoise
import json, boto.ec2
import ls, rm, mk

env.use_ssh_config = True

#===========#
#	Tasks	#
#===========#
@task
def initaws(key=None,secret=None,region=None):# {{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		if not key:
			key = local('aws configure get aws_access_key_id', capture=True)
		if not secret:
			secret = local('aws configure get aws_secret_access_key', capture=True)
		if not region:
			region = local('aws configure get region', capture=True)
		if not key:
			key = lambda aws_access_key_id: local('aws configure set aws_access_key_id ' + aws_access_key_id, capture=True)
			key(raw_input("Enter the aws_access_key_id: "))
		else:
			local('aws configure set aws_access_key_id ' + key, capture=True)
		if not secret:
			secret = lambda aws_secret_access_key: local('aws configure set aws_secret_access_key ' + aws_secret_access_key, capture=True)
			secret(raw_input("Enter the aws_secret_access_key: "))
		else:
			local('aws configure set aws_secret_access_key ' + secret)
		if not region:
			regions = getregions()
			local('aws configure set region ' + regions[int(choose(regions))])
		else:
			local('aws configure set region ' + region)

# }}}
@task
def deploy(instance, states=False):
	pass

