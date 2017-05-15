# Purpose

The National Archives has a broad goal, stated in its Open Government Plan and elsewhere, of uploading its public domain digital assets from its catalog to Wikimedia Commons to make them available on Wikipedia and for other reuse. This tool consists of the script used to operate an approved bot account on Wikimedia Commons that performs automated uploads using medi and data from NARA's online catalog. 

# Technical explanation

This tool is a script written in Python 2.7. It interacts with the National Archives Catalog API, as the source of the media and data to be uploaded, as well as the Wikimedia Commons API in order to perform the uploads. Its workflow consists of:
1. Reading JSON data from the catalog
2. Running through a series of steps to parse the necessary metadata fields
3. Populating a template with the fields to generate the wiki page text for the Wikimedia Commons upload
4. Downloading the file from the catalog
5. Using mwclient to upload the media file and accompanying wiki page text
6. Repeating for each media file in the set, paginating as necessary, until complete

# Depdendencies

In addition to Python 2.7, the script requires the following two Python libraries:
* Requests (http://docs.python-requests.org/)
* mwclient (http://mwclient.readthedocs.io/)
