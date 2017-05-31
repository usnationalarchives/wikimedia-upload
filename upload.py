# -*- coding: utf-8 -*-

import json, requests, csv, re, os, mwclient, settings
from mwclient import Site

def metadata(record, level, objects):
	
	title = record['title']
	try:
		general_notes = record['generalRecordsTypeArray']['generalNote']['note']
	except KeyError:
		general_notes = ''
	try:
		scope_and_content = record['scopeAndContentNote']
	except KeyError:
		scope_and_content = ''
	naid = record['naId']
	try:
		author = '{{NARA-Author|' + record['personalContributorArray']['personalContributor']['contributor']['termName'] + '|' + record['personalContributorArray']['personalContributor']['contributor']['naId'] + '}}'
	except KeyError:
		author = ''
		author_naid = ''
	except TypeError:
		author = '{{NARA-Author|' + record['personalContributorArray']['personalContributor'][0]['contributor']['termName'] + '|' + record['personalContributorArray']['personalContributor'][0]['contributor']['naId'] + '}}'
	
	try:
		local_identifier = record['localIdentifier']
	except KeyError:
		local_identifier = ''
	
	try:
		date = '{{date|' + record['productionDateArray']['proposableQualifiableDate']['year'] + '|' + record['productionDateArray']['proposableQualifiableDate']['month'] + '|' + record['productionDateArray']['proposableQualifiableDate']['day'] + '}}'
	except KeyError as e:
		if e[0] == 'productionDateArray':
			try:
				date = '{{date|' + record['parentSeries']['inclusiveDates']['inclusiveStartDate']['year'] + '}} &ndash; {{date|' + record['parentSeries']['inclusiveDates']['inclusiveEndDate']['year'] + '}}'
			except:
				date = '{{date|' + record['parentFileUnit']['parentSeries']['inclusiveDates']['inclusiveStartDate']['year'] + '}} &ndash; {{date|' + record['parentFileUnit']['parentSeries']['inclusiveDates']['inclusiveEndDate']['year'] + '}}'
		if e[0] == 'day':
			date = '{{date|' + record['productionDateArray']['proposableQualifiableDate']['year'] + '|' + record['productionDateArray']['proposableQualifiableDate']['month'] + '|}}'
		if e[0] == 'month':
			date = '{{date|' + record['productionDateArray']['proposableQualifiableDate']['year'] + '||}}'
	try:
		variant_control_numbers = []
		for id in record['variantControlNumberArray']['variantControlNumber']:
			variant_control_numbers.append(id['type']['termName'] + ': ' + id['number'])
	except KeyError as e:
		variant_control_numbers = []
	except TypeError:
			variant_control_numbers.append(record['variantControlNumberArray']['variantControlNumber']['type']['termName'] + ': ' + record['variantControlNumberArray']['variantControlNumber']['number'])
	try:
		location = record['physicalOccurrenceArray'][level + 'PhysicalOccurrence']['locationArray']['location']['facility']['termName']
	except KeyError:
		location = record['physicalOccurrenceArray'][level + 'PhysicalOccurrence']['locationArray']['location'][0]['facility']['termName']
	except TypeError:
		try:
			location = record['physicalOccurrenceArray'][level + 'PhysicalOccurrence'][0]['locationArray']['location']['facility']['termName']
		except KeyError:
			location = record['physicalOccurrenceArray'][level + 'PhysicalOccurrence']['locationArray']['location'][0]['facility']['termName']
		except TypeError:
			location = record['physicalOccurrenceArray'][level + 'PhysicalOccurrence'][0]['locationArray']['location'][0]['facility']['termName']
	except KeyError:
		print naid
		print record['physicalOccurrenceArray']

	if 'parentSeries' in record.keys():
		series = record['parentSeries']['title']
		series_naid = record['parentSeries']['naId']
		try:
			record_group_number = record['parentSeries']['parentRecordGroup']['recordGroupNumber']
			record_group = 'Record Group ' + record_group_number + ': ' + record['parentSeries']['parentRecordGroup']['title']
			record_group_naid = record['parentSeries']['parentRecordGroup']['naId']
		except:
			record_group = 'Collection ' + record['parentSeries']['parentCollection']['collectionIdentifier'] + ': ' + record['parentSeries']['parentCollection']['title']
			record_group_naid = record['parentSeries']['parentCollection']['naId']
			
		try:
			creator = record['parentSeries']['creatingOrganizationArray']['creatingOrganization']['creator']['termName']
			creator_naid = record['parentSeries']['creatingOrganizationArray']['creatingOrganization']['creator']['naId']
		except KeyError:
			creator = record['parentFileUnit']['parentSeries']['creatingIndividualArray']['creatingIndividual']['creator']['termName']
			creator_naid = record['parentFileUnit']['parentSeries']['creatingIndividualArray']['creatingIndividual']['creator']['naId']
		except TypeError:
			creator = record['parentSeries']['creatingOrganizationArray']['creatingOrganization'][0]['creator']['termName']
			creator_naid = record['parentSeries']['creatingOrganizationArray']['creatingOrganization'][0]['creator']['naId']
		file_unit = ''
		file_unit_naid = ''
	
	if 'parentFileUnit' in record.keys():
		series = record['parentFileUnit']['parentSeries']['title']
		series_naid = record['parentFileUnit']['parentSeries']['naId']
		try:
			record_group_number = record['parentFileUnit']['parentSeries']['parentRecordGroup']['recordGroupNumber']
			record_group = 'Record Group ' + record_group_number + ': ' + record['parentFileUnit']['parentSeries']['parentRecordGroup']['title']
			record_group_naid = record['parentFileUnit']['parentSeries']['parentRecordGroup']['naId']
		except:
			record_group = 'Collection ' + record['parentFileUnit']['parentSeries']['parentCollection']['collectionIdentifier'] + ': ' + record['parentFileUnit']['parentSeries']['parentCollection']['title']
			record_group_naid = record['parentFileUnit']['parentSeries']['parentCollection']['naId']
		file_unit = record['parentFileUnit']['title']
		file_unit_naid = record['parentFileUnit']['naId']
		try:
			creator = record['parentFileUnit']['parentSeries']['creatingOrganizationArray']['creatingOrganization']['creator']['termName']
			creator_naid = record['parentFileUnit']['parentSeries']['creatingOrganizationArray']['creatingOrganization']['creator']['naId']
		except KeyError:
			creator = record['parentFileUnit']['parentSeries']['creatingIndividualArray']['creatingIndividual']['creator']['termName']
			creator_naid = record['parentFileUnit']['parentSeries']['creatingIndividualArray']['creatingIndividual']['creator']['naId']
		except TypeError:
			creator = record['parentFileUnit']['parentSeries']['creatingOrganizationArray']['creatingOrganization'][0]['creator']['termName']
			creator_naid = record['parentFileUnit']['parentSeries']['creatingOrganizationArray']['creatingOrganization'][0]['creator']['naId']

	other_pages = ''
	object_array = []
	try:
		if objects['object']['file']['@name'].split('.')[-1] != 'pdf':
			object_array.append((objects['object']['file']['@url'], objects['object']['file']['@name']))
	except:
		for object in objects['object']:
			if object['file']['@name'].split('.')[-1] != 'pdf':
				object_array.append((object['file']['@url'], object['file']['@name']))
	filename = []
	if len(object_array) == 1:
		fname = title + ' - NARA - ' + naid + '.' + object_array[0][1].split('.')[-1].lower()
		if len(fname) > 240:
			truncate = 234 - len(' - NARA - ' + naid + '.' + object_array[0][1].split('.')[-1])
			fname = title[:truncate] + '(...) - NARA - ' + naid + '.' + object_array[0][1].split('.')[-1].lower()
		filename.append(fname)
	if len(object_array) > 1:
		n = 1
		other_pages = '<gallery  caption="Other pages in this document">'
		for object in object_array:
			fname = title + ' - NARA - ' + naid + ' (page ' + str(n) + ').' + object[1].split('.')[-1].lower()
			if len(filename) > 240:
				truncate = 234 - len(' - NARA - ' + naid + ' (page ' + str(n) + ').' + object[1].split('.')[-1])
				fname = title[:truncate] + '(...) - NARA - ' + naid + ' (page ' + str(n) + ').' + object[1].split('.')[-1].lower()
			filename.append(fname)
			other_pages = other_pages + '\n' + fname + '|Page ' + str(n)
			n = n + 1
		other_pages = other_pages + '\n</gallery>'
	
	license = '{{PD-USGov}}'
	with open('record_groups.csv', 'r') as log :
		readlog = csv.reader(log, delimiter= '\t', quoting=csv.QUOTE_ALL)
		for row in readlog:
			if record_group_number == row[0]:
				if row[3]:
					license = '{{PD-USGov-' + row[3] + '}}'
	
	description = """== {{int:filedesc}} ==
{{NARA-image-full
 | Title                   = """ + title + """
 | Scope and content       = """ + scope_and_content + """
 | General notes           = 
 | NAID                    = """ + naid + """
 | Local identifier        = """ + local_identifier + """
 | Creator                 = """ + creator + """
 | Creator NAID            = """ + creator_naid + """
 | Author                  = """ + author + """
 | Location                = """ + location + """
 | Date                    = """ + date + """
 | Record group            = """ + record_group + """
 | Record group NAID       = """ + record_group_naid + """
 | Series                  = """ + series + """
 | Series NAID             = """ + series_naid + """
 | File unit               = """ + file_unit + """
 | File unit NAID          = """ + file_unit_naid + """
 | Variant control numbers = """ + '<br/>'.join(variant_control_numbers) + """
 | Other versions          =
 | Other pages             = """ + other_pages + """
}}

=={{int:license-header}}==

{{NARA-cooperation}}
""" + license + """

""" + settings.categories

	
	print description
	for file in filename:
		print file + ' (' + str(len(file)) + ')'

	site = mwclient.Site('commons.wikimedia.org')
	site.login(settings.user, settings.password)
	n = 0
	for object_tuple in object_array:
		r = requests.get(object_tuple[0], stream=True)
		with open(object_tuple[1], "wb") as image :
			image.write(r.content)
# 		site.upload(file=open(object_tuple[1]), filename=filename[n], description=description, ignore=False, comment='[[Commons:Bots/Requests/US National Archives bot|Bot-assisted upload]] of [[nara:' + naid + '|US National Archives Identifer ' + naid + ']].')
		os.remove(object_tuple[1])
		n = n + 1

cursormark = '*'

while cursormark:
	url = settings.api_query + cursormark
	text = requests.get(url).text
	try:
		s = json.loads(text)
	except ValueError:
		print url
		with open('error.txt', 'wb') as file:
			file.write(text.encode('utf-8'))

	cursormark = s['opaResponse']['results']['nextCursorMark']

	for result in s['opaResponse']['results']['result']:
	
		print '\n' + result['num']
		print result['naId']
		if result['description'].keys()[0] == 'item':
			record = result['description']['item']
			level = 'item'
		if result['description'].keys()[0] == 'fileUnit':
			record = result['description']['fileUnit']
			level = 'fileUnit'
		
		metadata(record, level, result['objects'])