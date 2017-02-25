import random, string, csv, urllib, configparser

userDict = {}

with open("CARRA_Members.csv", 'rb') as csvfile:
	userreader = csv.reader(csvfile)
	for row in userreader:
		email = row[2]
		if (email) and ("2016 CARRA Meeting Registrants" == row[1]):
		  userDict[email] = row[0]


def toLFName(lastnameCommaFirstname):
	return (lastnameCommaFirstname.split(","))


for email in userDict:
	nameList = toLFName(userDict.get(email))
	print email + "," + nameList[1].strip() + "," + \
	  nameList[0].strip() + ",confluence-users,jira-users"


