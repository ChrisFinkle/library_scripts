#!python
import re

targets = ['alumaccess list.txt']

outputFields = ['prefix','givenName','middleName','familyName','suffix',
				'nickname','canSelfEdit','dateOfBirth','gender','institutionId',
				'barcode','idAtSource','sourceSystem','borrowerCategory',
				'circRegistrationDate','oclcExpirationDate','homeBranch',
				'primaryStreetAddressLine1','primaryStreetAddressLine2',
				'primaryCityOrLocality','primaryStateOrProvince','primaryPostalCode',
				'primaryCountry','primaryPhone','secondaryStreetAddressLine1',
				'secondaryStreetAddressLine2','secondaryCityOrLocality',
				'secondaryStateOrProvince','secondaryPostalCode','secondaryCountry',
				'secondaryPhone','emailAddress','mobilePhone','notificationEmail',
				'notificationTextPhone','patronNotes','photoURL','customdata1',
				'customdata2','customdata3','customdata4','username','illId',
				'illApprovalStatus','illPatronType','illPickupLocation']

simpleFields = ['id', 'Profile', 'created', 'priv expired', 'Email', 'group ID']
addressFields = ['Street', 'Zip', 'Home Phone', 'City, State']

namePattern = r'^\s?[\.\w\'-]+(?:\s[\w\.]+)?,\s.*'

def parseSimpleFields(line, patron):
	for field in simpleFields:
		result = re.findall(field + r':(.+?)\s', line)
		if result:
			patron[field] = result

def parseName(namestr, patron):
	patron['familyName'] = re.findall(r'^\s?([\.\w\'-]+)(?:\s[\w\.]+)?,\s.*', namestr)
	patron['givenName'] = re.findall(r',\s([\w\'-]+)', namestr)
	patron['middleName'] = re.findall(r',\s[\w\'-]+\s([\w\.\']+)', namestr)
	patron['prefix'] = re.findall(r'\(([\w\.]+)\)', namestr)
	patron['suffix'] = re.findall(r'^\s?[\.\w\'-]+\s([\w\.]+),', namestr)

def parseAddressFields(line, patron):
	for field in addressFields:
		result = re.findall(field + r':(.+)', line)
		if result:
			try: 
				patron[field]
				patron[field + '2'] = result
			except KeyError:
				patron[field] = result

noteMode = False

def checkForNoteMode(line):
	if re.search(r'Extended Information--', line):
		return True
	elif re.search(r'created:', line):
		return False
	else: return noteMode

def appendLineToNote(line, patron):
	try:
		patron['notes'] += re.sub(r'\s+', r' ', line)
	except KeyError:
		patron['notes'] = ''

#since output of findall is list, takes in list
def parseCity(s):
	if re.search(r'(.*?),?\s\w\w\s', s[0]):
		return re.findall(r'(.*?),?\s\w\w\s', s[0])
	elif re.search(r'(.*?),\s.*', s[0]):
		return re.findall(r'(.*?),\s.*', s[0])
	elif re.search(r'\d+$', s[0]):
		return [' '.join(s[0].split(' ')[:-2])]
	else: return s

def parseState(s):
	if re.search(r'.*?,?\s(\w\w)\s?', s[0]):
		return re.findall(r'.*?,?\s(\w\w)\s?', s[0])
	elif re.search(r'.*?,\s\D*', s[0]):
		return re.findall(r'.*?,\s(\D)*\s', s[0])
	elif re.search(r'\d+$', s[0]):
		return [' '.join(s[0].split(' ')[-1])]
	else: return s

def parseZip(s):
	zip = re.findall(r'[\d-]+', s[0])
	return zip

def postProcessPatron(patron):
	patron['barcode'] = patron['id']
	patron['borrowerCategory'] = patron['Profile']
	patron['circRegistrationDate'] = patron['created']
	patron['oclcExpirationDate'] = patron['priv expired']
	patron['primaryStreetAddressLine1'] = patron['Street']
	patron['primaryCityOrLocality'] = parseCity(patron['City, State'])
	patron['primaryStateOrProvince'] = parseState(patron['City, State'])
	patron['primaryPostalCode'] = patron['Zip'] if 'Zip' in patron\
							else parseZip(patron['City, State'])
	patron['primaryPhone'] = patron['Home Phone'] if 'Home Phone' in patron else []
	try:
		patron['secondaryStreetAddressLine1'] = patron['Street2']
		patron['secondaryCityOrLocality'] = parseCity(patron['City, State2'])
		patron['secondaryStateOrProvince'] = parseState(patron['City, State2'])
		patron['secondaryPostalCode'] = patron['Zip2'] if 'Zip2' in patron\
							else parseZip(patron['City, State2'])
		patron['secondaryPhone'] = patron['Phone2']
	except KeyError:
		pass
	patron['emailAddress'] = patron['Email'] if 'Email' in patron else []
	patron['patronNotes'] = patron['group ID'] if 'group ID' in patron else []
	patron['customdata1'] = [patron['notes']] if 'notes' in patron else []

def extractField(field, patron):
	if field in patron and patron[field]:
		return patron[field][0]
	else:
		return ''

for target in targets:
	file = open(target)
	patrons = [{}]

	for line in file:
		newName = re.findall(namePattern, line)
		if newName:
			patron = {}
			patrons.append(patron)
			parseName(newName[0], patron)
		else:
			patron = patrons[-1]
			parseSimpleFields(line,patron)
			parseAddressFields(line, patron)
			noteMode = checkForNoteMode(line)
			if noteMode: appendLineToNote(line, patron)

	file.close()

	out = open('tab delimited '+target, 'w+')
	out.write('	'.join(outputFields)+'\n')
	
	for patron in patrons[1:]:
		postProcessPatron(patron)
		out.write('	'.join([extractField(field, patron) for field in outputFields])+'\n')
		
	out.close()

