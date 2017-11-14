#!python
import os
import re

inputs = os.listdir('data')

def extractIfExists(findallResult):
	if findallResult:
		return findallResult[0]
	else:
		return ''

institutionid = '648'

colNameList = ['institutionId', 'itemBarcode', 'loanCount', 'loanCountYTD', 'lastLoanDate',
				'lastBorrowerBarcode', 'lastBorrowerInstitutionId', 'softLoanCount',
				'softLoanCountYTD', 'lastSoftLoanDate', 'inventoriedCount', 'lastInventoriedDate']

out = open('output/Tab-delimited_Item_Stats.txt', 'w+')

out.write('	'.join(colNameList))

for file in inputs:
	data = open('data/' + file)
	for line in data:
		if re.match(r'=999', line):
			barcode = extractIfExists(re.findall(r'\$i(.*?)\$', line))
			lastLoanDate = extractIfExists(re.findall(r'\$e(.*?)\$', line))
			loanCount = extractIfExists(re.findall(r'\$n(.*?)\$', line))
			fieldList = [institutionid, barcode, loanCount, '', lastLoanDate] + ['']*7
			out.write('\n'+'	'.join(fieldList))
	data.close()