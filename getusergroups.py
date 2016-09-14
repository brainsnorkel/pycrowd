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

tree = ET.fromstring(r.text)

userset = set()
groupset = set()

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

fusergroup.close()

fuserattrs = open('user-details.csv', 'w')

fuserattrs.write('userid,firstname,lastname,displayname,email,active,lastactive\n')

for user in sorted(userset):
	r = requests.get(globalBaseURL + '/rest/usermanagement/1/user?username='+user+'&expand=attributes',
		auth=globalauth)
	tree = ET.fromstring(r.text)
	#print r.text
	for node in tree.getiterator('user'):
		print('found a user '+ user )
		firstname = node.find('.//first-name').text
		lastname = node.find('.//last-name').text
		displayname = node.find('.//display-name').text
		email = node.find('.//email').text
		active = node.find('.//active').text
		lastactivenodeiter = node.findall(".//attribute[@name='lastActive']")
		lastactivestr = ''
		for lastactivenode in lastactivenodeiter:
			epochtext = lastactivenode.find('.//value').text
			#print epochtext
			lastactivestr = time.strftime('%Y-%m-%d %H:%M:%S', 
				time.localtime(float(epochtext)/1000))
		fuserattrs.write(user + ',' 
			+ firstname + ',' 
			+ lastname + ',' 
			+ displayname + ',' 
			+ email + ','
			+ active + ','
			+ lastactivestr
			+ '\n')
		fuserattrs.flush()

fuserattrs.close()
