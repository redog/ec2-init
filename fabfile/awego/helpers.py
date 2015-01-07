from __future__ import print_function
from fabric.api import settings, run, hide
from collections import namedtuple, Mapping
from UserDict import IterableUserDict
from itertools import chain
import json, pprint, yaml, boto

from color import red, turquoise


#===========#
#  Helpers  #
#===========#

def cset(b):# {{{
	with settings(warn_only=True):
		bv = raw_input("Enter the aws setting " + b + ":")
		br = run('aws configure set ' + b + ' ' + bv)
# }}}
def getregions():# {{{
	with settings(warn_only=True):
		with hide('stdout', 'stderr'):
			dj = json.loads(run('aws ec2 describe-regions --region=us-east-1'))
		num_regions = len(dj['Regions'])
		rl = []
		while num_regions > 0:
			rl.append(dj['Regions'][num_regions-1]['RegionName'])
			num_regions -= 1
		return(rl)
# }}}
def choose(list):# {{{
    """
    Semantics:  Prompts user to select from a list
    Arguments: A list
    Returns:    Returns the string selected
    """
    x = 0
    lrange = range(len(list))
    for each in list:
        print(turquoise("["+str(x)+"] ") + each)
        x = x + 1
    while True:
        choice = raw_input("Please select:")
        if int(choice) in lrange:
            answer = choice
            break
        else:
            print(red("That was not a valid choice!"))
    return answer
# }}}
class ddl(object):# {{{
	"""
	An object to convert a dictionary into a dot addressable object
	"""
	def __init__(self, d):
		for k in d:
			if isinstance(d[k], dict):
				self.__dict__[k] = ddl(d[k])
			elif isinstance(d[k], (list, tuple)):
				l = []
				for v in d[k]:
					if isinstance(v, dict):
						l.append(ddl(v))
					else:
						l.append(v)
				self.__dict__[k] = l
			else:
				self.__dict__[k] = d[k]
	def __getitem__(self, name):
		if name in self.__dict__:
			return self.__dict__[name]
	def __iter__(self):
		return iter(self.__dict__.keys())
	def __repr__(self):
		return pprint.pformat(self.__dict__)
	def __str__(self):
		return print(yaml.dump(self, default_flow_style=False))
# }}}

vpc_args = {'VpcId': '',
			'CidrBlock':'',
			'IsDefault':'',
			'DhcpOptionsId':'',
			'Tags':{'one':"two"},
			'InstanceTenancy':'',
			'State':''}
