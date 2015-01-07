from fabric.api import settings, run, env, task, hide, local
from helpers import *
from color import red, blue, green, turquoise
import json, boto.ec2

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
def lsregions():# {{{
	for r in boto.ec2.regions():
		print(green(r.name))
#	for r in getregions():
#		print(green(r))
# }}}
@task
def lskeys():# {{{
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			jr = json.loads(local('aws ec2 describe-key-pairs --region ' + region, capture=True))
			if jr.get('KeyPairs'):
				for pair in jr.get('KeyPairs'):
					print(green(region))
					print(turquoise(pair['KeyName'] + " => " + pair['KeyFingerprint']))
# }}}
@task
def lsvpc():
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			jr = json.loads(local('aws ec2 describe-vpcs --region ' + region, capture=True))
			dj = ddl(jr)
			print(green(region))
			print(str(dj.Vpcs))
