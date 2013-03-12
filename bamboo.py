#! /usr/bin/python
# get the build status for PointLine from bamboo
# http://benoitc.github.com/restkit
# https://docs.atlassian.com/bamboo/REST/4.0/
# https://dev.cubx-software.com:8446/rest/api/latest/result/PLB-CIMAINDEV?max-results=5


from restkit import request, Resource, BasicAuth

class BambooRest(Resource):
	def __init__(self, url, user, password, **kwargs):
		self.baseurl = url
		self.auth = BasicAuth(user, password)
		Resource.__init__(self, self.baseurl, follow_redirect=True, max_follow_redirect=10, filters=[self.auth], **kwargs)

	def request(self, *args, **kwargs):
		resp = Resource.request(self, *args, **kwargs)
		data_body = resp.body_string()

	def latestBuildSuccessful(self):
		
		req = self.get('/rest/api/latest/result/PLB-CIMAINDEV?max-result=5&os_authType=basic')
		req.body_string()
		
		return True


	
# test code
if __name__ == "__main__":
	passwd = raw_input("Enter the password for ulr: ")
	bamb = BambooRest('https://dev.cubx-software.com:8446', 'ulr', passwd)
	print bamb.latestBuildSuccessful()

