#!/bin/env python2

d={'SourceDestCheck': True, 'Groups': [{'GroupName': 'MySSHOnlySecurityGroup', 'GroupId': 'sg-b70963d2'}], 'NetworkInterfaceId': 'eni-7221682b', 'PrivateIpAddresses': [{'Primary': True, 'PrivateIpAddress': '172.31.32.180'}], 'VpcId': 'vpc-8320f3e6', 'OwnerId': '696994748028', 'PrivateIpAddress': '172.31.32.180', 'Status': 'pending', 'MacAddress': '0a:82:ce:9c:4d:12', 'AvailabilityZone': 'us-west-2c', 'Description': 'My First vNIC', 'RequesterManaged': False, 'RequesterId': 'AIDAJ37JAXUYBR6NMRM2I', 'SubnetId': 'subnet-67b6593e', 'TagSet': []}

class A(object):
	_defaults = {
		"my_default": "Mine",
		"somethingA": "Aye"
	}
	def __init__(self, **kwargs):
		for k, v in self._defaults.iteritems():
			kwargs[k] = v
#		for (key, default) in self._defaults.iteritems():
#			setattr(self, key, kwargs.get(key, default))
		for (key, value) in kwargs.iteritems():
			setattr(self, key, kwargs.get(key, value))
		super(A, self).__init__()
	def __str__(self):
		return str(self.__dict__)
	def __eq__(self, other):
		return self.__dict__ == other.__dict__

class B(A):# {{{
	_defaults = {
		"my_default": "No Mine",
		"somethingB": "Bee"
	}
	def __init__(self, **kwargs):
		super(B, self).__init__(**kwargs)
# }}}

class C(A):# {{{
	_defaults = {
		"my_default": "Mine",
	}
	def __init__(self, **kwargs):
		super(C, self).__init__(**kwargs)
# }}}



class DictDiffer(object):#{{{
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


aI = A(**d)

bI = B(**d)

#cI = C(my_default="Mine", **d)
cI = C(**d)

diff = DictDiffer(aI.__dict__, bI.__dict__)

cdiff = DictDiffer(aI.__dict__, cI.__dict__)

#print("Added")
#print(diff.added())
#print("Removed")
#print(diff.removed())
#print("Changed")
#print(diff.changed())
#print("Unchanged")
#print(diff.unchanged())

print(cdiff.added())
print(cdiff.removed())
print(cdiff.changed())
print(cdiff.unchanged())

print(cI.somethingA)
