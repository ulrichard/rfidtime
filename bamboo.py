#! /usr/bin/python
# get the build status for PointLine from bamboo
# http://benoitc.github.com/restkit
# https://docs.atlassian.com/bamboo/REST/4.0/
# https://dev.cubx-software.com:8446/rest/api/latest/result/PLB-CIMAINDEV?max-results=5


import httplib2, getpass

class BambooState:
	def __init__(self, url, user, password):
		self.baseurl = url
		self.user = user
		self.passwd = password

	def latestBuildSuccessful(self):
		h = httplib2.Http(".cache")
		h.debuglevel = 2
		h.disable_ssl_certificate_validation = True
		h.add_credentials(self.user, self.passwd)
#		url = "https://%s:%s@%s/rest/api/latest/result/PLB-CIMAINDEV?max-result=5&os_authType=basic" % (self.user, self.passwd, self.baseurl)
		url = "https://%s/rest/api/latest/result/PLB-CIMAINDEV?max-result=5&os_authType=basic" % self.baseurl
#		resp, content = h.request(url, "GET", headers={'content-type':'text/json'} )
		resp, content = h.request(url, "GET")
		print content	
		return True


	
# test code
if __name__ == "__main__":
	passwd = getpass.getpass(prompt="Enter the password for ulr: ")
	bamb = BambooState('dev.cubx-software.com:8446', 'ulr', passwd)
	print bamb.latestBuildSuccessful()

