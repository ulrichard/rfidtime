#! /usr/bin/python
# get the build status for PointLine from bamboo
# http://benoitc.github.com/restkit
# https://docs.atlassian.com/bamboo/REST/4.0/
# https://dev.cubx-software.com:8446/rest/api/latest/result/PLB-CIMAINDEV?max-results=5


from restkit import request, Resource, BasicAuth

class BambooRest:
	def __init__(self, url, user, password):
		self.url = url
		self.user = user
		self.passwd = password

	def check(self):
		auth = BasicAuth(self.user, self.passwd)
		res = Resource(self.url, filters=[auth])
		req = res.get('/rest/api/latest/result/PLB-CIMAINDEV?max-result=5')
		req.body_string()
		
		return True


	
# test code
if __name__ == "__main__":
	passwd = raw_input("Enter the password for ulr: ")
	bamb = BambooRest('https://dev.cubx-software.com:8446', 'ulr', passwd)
	print bamb.check()

