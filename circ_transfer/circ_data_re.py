#!python

import os
import re

inputDir = 'data/test'

inputs = os.listdir(inputDir)

dateFormat = r'\d\d?/\d\d?/\d{4},\d\d?:\d{2}'

outputOrder = ['lendingInstitutionId', 'itemBarcode', 'borrowerInstitutionId',
				'borrowerBarcode', 'loanDate', 'dueDate', 'recallDate',
				'renewalDate', 'renewalCount', 'note']

records = [{}]

def makeTwoDigits(st):
	return '0' + st if len(st) == 1 else st

def fixDate(dateStr):
	[date, time] = dateStr.split(',')
	[M, D, Y] = date.split('/')
	[hour, minute] = time.split(':')
	dateTime = Y + '-' + makeTwoDigits(M) + '-' + makeTwoDigits(D)
	dateTime += 'T' + makeTwoDigits(hour) + ':' + minute + ':00'
	return dateTime

def retrieveIfExists(value, record):
	if value in record:
		return record[value]
	else:
		return ''

for file in inputs:
	data = open(inputDir + '/' + file)
	for line in data:
		if re.search('3436900', line):
			record = {'lendingInstitutionId':'648', 'borrowerInstitutionId':'648'}
			record['itemBarcode'] = re.findall(r'(3436900.*?)\s*$', line)[0]
			records.append(record)
		else:
			record = records[-1]
			if re.match(r'^  \w', line):
				info = re.split(r'\s{2,}', line)
				record['borrowerBarcode'] = info[-3]
				record['loanDate'] = fixDate(info[-2])
			elif re.match(r'^'+dateFormat, line):
				info = re.split(r'\s{2,}', line)
				record['dueDate'] = fixDate(info[0])
				record['renewalDate'] = fixDate(info[1]) if re.match(dateFormat, info[1]) else ''
				record['renewalCount'] = info[-5]
	data.close()

out = open('output/test_results.txt', 'w+')
out.write('	'.join(outputOrder)+'\n')
for record in records[1:]:
	out.write('	'.join([retrieveIfExists(value, record) for value in outputOrder]) + '\n')
out.close()