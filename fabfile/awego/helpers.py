from __future__ import print_function
from fabric.api import settings, run, hide, local
from collections import namedtuple, Mapping
from UserDict import IterableUserDict
from itertools import chain
import json, pprint, yaml, boto.ec2, boto.vpc

from color import red, turquoise


#===========#
#  Helpers  #
#===========#

def cset(b):  # {{{
	with settings(warn_only=True):
		bv = raw_input("Enter the aws setting " + b + ":")
		br = run('aws configure set ' + b + ' ' + bv)
# }}}
def getregions():  # {{{
	with settings(warn_only=True):
		with hide('stdout', 'stderr'):
			dj = json.loads(local('aws ec2 describe-regions --region=us-east-1', capture=True))
		num_regions = len(dj['Regions'])
		rl = []
		while num_regions > 0:
			rl.append(dj['Regions'][num_regions-1]['RegionName'])
			num_regions -= 1
		return(rl)
# }}}
def choose(list):  # {{{
	"""
	Semantics:	Prompts user to select from a list
	Arguments: A list
	Returns:	Returns the string selected
	"""
	x = 0
	if len(list) == 0:
		return
	elif len(list) == 1:
		return str(0)
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
def ask(prompt, retries=4):#{{{
    """
    Semantics:  Prompts for yes or no, complains and quits if neither given after retry limit.
    Arguements: Question prompt, Number of retries, Complaint
    Returns:    True or False
    """
    complaint='Yes or no, please!'
    while True:
        ok = raw_input(prompt)
        if ok in ('y', 'Y', 'ye',  'yes', 'Yes', 'YES' ): return True
        if ok in ('n', 'N', 'no', 'nop', 'nope', 'No', 'NO'): return False
        retries = retries - 1
        if retries < 0: raise IOError, red('luser error')
        print(complaint)
#}}}
class ddl(object):  # {{{
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
class DictDiffer(object):  #{{{
	"""
	Calculate the difference between two dictionaries as:
	(1) items added
	(2) items removed
	(3) keys same in both but changed values
	(4) keys same in both and unchanged values
	"""
	def __init__(self, current_dict, past_dict):
		self.current_dict, self.past_dict = current_dict, past_dict
		self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
		self.intersect = self.set_current.intersection(self.set_past)
	def added(self):
		return self.set_current - self.intersect
	def removed(self):
		return self.set_past - self.intersect
	def changed(self):
		return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
	def unchanged(self):
		return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])
#}}}
class Ego(object):  #{{{
	"""
	A reference object for extending
	overide self._d values in a child classes' __init__
	"""
	_d = {
		"my_default": "Mine",
		"somethingA": "Aye"
			}
	def __init__(self, **kwargs):
		self._d = Ego._d if not self._d else dict(list(Ego._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(Ego, self).__init__()
	def __str__(self):
		return str(self.__dict__)
	def __eq__(self, other):
		return self.__dict__ == other.__dict__
#}}}
class subego(Ego):  #{{{
	"""
	An example inherited subclass with overiding defaults
	"""
	def __init__(self, **kwargs):
		self._d = {
			"my_default": "No Mine",
			"somethingB": "Bee"
		}
		super(subego, self).__init__(**kwargs)
#}}}
# for easy copying  #{{{
class T(object):
	_d ={}
	def __init__(self, **kwargs):
		self._d = T._d if not self._d else dict(list(T._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(T, self).__init__()
#}}}
# Aws Objects
class BoCoEc(object):
	def __init__(self, region):
		self.key_id = local('aws configure get aws_access_key_id', capture=True)
		self.key_secret = local('aws configure get aws_secret_access_key', capture=True)
		self.bc = boto.ec2.connect_to_region(region, aws_access_key_id=self.key_id, aws_secret_access_key=self.key_secret )
		del self.key_id
		del self.key_secret

class BoCoVpc(object):
	def __init__(self, region):
		self.key_id = local('aws configure get aws_access_key_id', capture=True)
		self.key_secret = local('aws configure get aws_secret_access_key', capture=True)
		self.bc = boto.vpc.connect_to_region(region, aws_access_key_id=self.key_id, aws_secret_access_key=self.key_secret )
		del self.key_id
		del self.key_secret


class Instance(object):  #{{{
	_d = {
		"ImageId": "ami-3d50120d",
		"InstanceType": "t2.micro",
		}
	def __init__(self, **kwargs):
		self._d = Instance._d if not self._d else dict(list(Instance._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(Instance, self).__init__()
#}}}
class Tags(object):  #{{{
	_d ={}
	def __init__(self, **kwargs):
		self._d = Tags._d if not self._d else dict(list(Tags._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(Tags, self).__init__()
  #}}}
class NetIface(object):  #{{{
	_d ={}
	def __init__(self, **kwargs):
		self._d = NetIface._d if not self._d else dict(list(NetIface._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(NetIface, self).__init__()
#}}}
class Route(object):  #{{{
	_d ={}
	def __init__(self, **kwargs):
		self._d = Route._d if not self._d else dict(list(Route._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(Route, self).__init__()
  #}}}
class RouteTable(object):  #{{{
	_d ={}
	def __init__(self, **kwargs):
		self._d = RouteTable._d if not self._d else dict(list(RouteTable._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(RouteTable, self).__init__()
  #}}}
class InternetGateway(object):  #{{{
	_d ={}
	def __init__(self, **kwargs):
		self._d = InternetGateway._d if not self._d else dict(list(InternetGateway._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(InternetGateway, self).__init__()
  #}}}
class SubNet(object):  #{{{
	_d ={}
	def __init__(self, **kwargs):
		self._d = SubNet._d if not self._d else dict(list(SubNet._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(Subnet, self).__init__()
#}}}
class SecurityGroup(object):  #{{{
	_d ={}
	def __init__(self, **kwargs):
		self._d = SecurityGroup._d if not self._d else dict(list(SecurityGroup._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(SecurityGroup, self).__init__()
#}}}
class Vpc(object):  #{{{
	_d ={}
	def __init__(self, **kwargs):
		self._d = Vpc._d if not self._d else dict(list(Vpc._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(Vpc, self).__init__()
  #}}}
class KeyPair(object):  #{{{
	_d ={}
	def __init__(self, **kwargs):
		self._d = KeyPair._d if not self._d else dict(list(KeyPair._d.items())+list(self._d.items()))
		for (key, default) in self._d.iteritems():
			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(KeyPair, self).__init__()
  #}}}


vpc_args = {'VpcId': '',
			'CidrBlock':'',
			'IsDefault':'',
			'DhcpOptionsId':'',
			'Tags':{'one':"two"},
			'InstanceTenancy':'',
			'State':''}
