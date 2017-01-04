import simplejson as json
import random, string, csv, urllib, configparser, time, calendar
from datetime import datetime
import xml.etree.ElementTree as ET

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


r = requests.get(globalBaseURL + '/rest/usermanagement/1/group/membership', 
	auth=globalauth)

tree = ET.fromstring(r.text.decode('utf-8'))

userset = set()
groupset = set()
userDict = {}


fusergroup = open('groups-to-users.csv', 'w')

fusergroup.write('group,user\n')

for node in tree.findall('.//membership'):
    group = node.attrib.get('group')
    if group:
    	groupset |= set([group])
        for usernode in node.findall('.//user'):
        	user = usernode.attrib.get('name')
        	userset |= set([user])
        	fusergroup.write(group + ',' + user + '\n')
        	if userDict.has_key(user):
        		userDict[user] = [] + userDict[user] + [group]
        	else:
        		userDict[user] = [group]


fusergroup.close()

fuserattrs = open('user-details.csv', 'w')

fuserattrs.write('userid,firstname,lastname,displayname,email,active,lastactive,groups\n')

usernum = 0
activenum = 0
seenin7days = 0
weekagoseconds = (time.time() ) - (8 * 25 * 60 * 60)

for user in sorted(userset):
	r = requests.get(globalBaseURL + '/rest/usermanagement/1/user?username='+user+'&expand=attributes',
		auth=globalauth, stream=True)
	tree = ET.fromstring(unicode(r.content, errors='ignore'))
	#print r.text
	for node in tree.getiterator('user'):
		usernum = usernum + 1 
		print('found a user '+ user + " - %d" % usernum)
		firstname = node.find('.//first-name').text
		lastname = node.find('.//last-name').text
		displayname = node.find('.//display-name').text
		email = node.find('.//email').text
		active = node.find('.//active').text
		lastactivenodeiter = node.findall(".//attribute[@name='lastActive']")
		lastactivestr = ''
		for lastactivenode in lastactivenodeiter:
			epochtext = lastactivenode.find('.//value').text
			epochseconds = time.localtime(float(epochtext)/1000)
			#seenin7days += (float(epochtext)/1000 > weekagoseconds)
			#print epochtext
			lastactivestr = time.strftime('%Y-%m-%d %H:%M:%S', 
				epochseconds)
			if (float(epochtext)/1000 > weekagoseconds):
				print("### Seen in last ~7 days")
				seenin7days += 1
		fuserattrs.write(user + ',' 
			+ firstname + ',' 
			+ lastname + ',' 
			+ displayname + ',' 
			+ email + ','
			+ active + ','
			+ lastactivestr +','
			+ "\"" + ",".join(userDict[user]) + "\"" 
			+ '\n')
		if lastactivestr != '':
			activenum = activenum + 1
		fuserattrs.flush()

fuserattrs.close()
print("%d active users" % activenum)
print("%d active users in the past ~7 days" % seenin7days)
print("%d total users" % usernum)
