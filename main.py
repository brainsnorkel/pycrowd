import simplejson as json
import random, string, csv, urllib, configparser

# import the REST library

import requests
from requests.auth import HTTPBasicAuth

#
# Set up configuration from config.ini
#

config = configparser.ConfigParser()
config.read('config.ini')

globalauthuser = config.get('CROWDSERVER','BasicAuthUsername')
globalauthpassword = config.get('CROWDSERVER','BasicAuthPassword')

globalauth = HTTPBasicAuth(globalauthuser, globalauthpassword)
globalBaseURL = config.get('CROWDSERVER','baseUrl')

transactionFileName = config.get('CROWDSERVER','transactionFileName')


def randomword(length):
   return ''.join(random.choice(string.lowercase+'@ABCDEFGHIJKLMNOPQRSTUVWXYZ1.~,123456789-=_+') for i in range(length))

#r = requests.get('http://id.flatmapit.com:8095/crowd/rest/usermanagement/latest/user?username=admin&expand=attributes',
#                 auth=HTTPBasicAuth('directoryexport', 'r8nd0m'))

def makeUserJson(email, firstname, lastname):
	obj = {'name': email,
			'password': {'value': randomword(30)},
			'active': True,
			'first-name': firstname,
			'last-name': lastname,
			'display-name': firstname + ' ' + lastname,
			'email': email}
	returnJson = json.dumps(obj, sort_keys=True, indent=4 * ' ')
	#print(returnJson)
	return returnJson

def addUserToGroup(user, groupArray):

	for group in groupArray:
		headers = {'content-type': 'application/json'}
		parameters = {'groupname': group}
		userNameJson = {'name': user}
		thisUser = json.dumps(userNameJson, sort_keys=True, indent=4 * ' ')
		#print(parameters)
		r = requests.post(globalBaseURL + '/rest/usermanagement/1/group/user/direct', 
			data = thisUser,
			headers = headers,
			params=parameters,
	        auth=globalauth)
		print (str(r.status_code) + '= result of add user ' + user + ' to group ' + group)


def addUser(user, userJson, groupArray):
	headers = {'content-type': 'application/json'}
	r = requests.post(globalBaseURL + '/rest/usermanagement/1/user', 
		data=userJson,
		headers = headers,
        auth=globalauth)
	print (str(r.status_code) + '= result of add user ' + user)
	addUserToGroup(user, groupArray)


#
# csvfile structure = firstName, lastName, email, group1, group2, ..., groupN
#

with open(transactionFileName, 'rb') as csvfile:
	userreader = csv.reader(csvfile)
	for row in userreader:
		email = row[2]
		if email:
		  makeUserJson(email, row[0], row[1])
		  addUser(email, makeUserJson(email, row[0], row[1]), row[3:])



