#! /usr/bin/python
# get the build status for PointLine from bamboo
# http://benoitc.github.com/restkit
# https://docs.atlassian.com/bamboo/REST/4.0/
# https://dev.cubx-software.com:8446/rest/api/latest/result/PLB-CIMAINDEV?max-results=5


import httplib2, getpass
from xml.dom.minidom import parseString

class BambooState:
	def __init__(self, url, user, password):
		self.baseurl = url
		self.user = user
		self.passwd = password

	def latestBuildSuccessful(self, job):
		h = httplib2.Http(".cache")
		h.debuglevel = 2
		h.disable_ssl_certificate_validation = True
		h.add_credentials(self.user, self.passwd)
		url = "https://%s/rest/api/latest/result/%s?max-result=1&os_authType=basic" % (self.baseurl, job)
		resp, content = h.request(url, "GET")
#		print content	

		dom = parseString(content)
		result = dom.getElementsByTagName('result')[0].toxml()
#		print result

		return result.find('state="Successful"') > 0


	
# test code
if __name__ == "__main__":
	passwd = getpass.getpass(prompt="Enter the password for ulr: ")
	bamb = BambooState('dev.cubx-software.com:8446', 'ulr', passwd)
	print bamb.latestBuildSuccessful('PLB-CIMAINDEV')

