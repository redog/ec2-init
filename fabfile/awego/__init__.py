from fabric.api import settings, run, env, task, hide
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
			key = run('aws configure get aws_access_key_id')
		if not secret:
			secret = run('aws configure get aws_secret_access_key')
		if not region:
			region = run('aws configure get region')
		if not key:
			key = lambda aws_access_key_id: run('aws configure set aws_access_key_id ' + aws_access_key_id)
			key(raw_input("Enter the aws_access_key_id: "))
		else:
			run('aws configure set aws_access_key_id ' + key)
		if not secret:
			secret = lambda aws_secret_access_key: run('aws configure set aws_secret_access_key ' + aws_secret_access_key)
			secret(raw_input("Enter the aws_secret_access_key: "))
		else:
			run('aws configure set aws_secret_access_key ' + secret)
		if not region:
			regions = getregions()
			run('aws configure set region ' + regions[int(choose(regions))])
		else:
			run('aws configure set region ' + region)

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
			jr = json.loads(run('aws ec2 describe-key-pairs --region ' + region))
			if jr.get('KeyPairs'):
				for pair in jr.get('KeyPairs'):
					print(green(region))
					print(turquoise(pair['KeyName'] + " => " + pair['KeyFingerprint']))
# }}}
@task
def lsvpc():
	with settings(warn_only=True), hide('stdout', 'stderr', 'running', 'warnings'):
		for region in getregions():
			jr = json.loads(run('aws ec2 describe-vpcs --region ' + region))
			dj = ddl(jr)
			print(green(region))
			print(str(dj.Vpcs))
