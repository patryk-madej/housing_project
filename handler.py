import pymysql
import boto3
import json
from os import environ
 
# 1. Install pymysql to local directory
# pip install -t $PWD pymysql
 
# 2. (If Using Lambda) Write your code, then zip it all up 
# a) Mac/Linux --> zip -r9 ${PWD}/function.zip 
# b) Windows --> Via Windows Explorer
 
# Lambda Permissions:
# AWSLambdaVPCAccessExecutionRole
 
#Configuration Values as env variables


#Connection: outside of the function to keep the connection rather than keep connecting
connection = pymysql.connect(environ['endpoint'], user=environ['username'], passwd=environ['password'], db=environ['database'])



def lambda_handler(event, context):
	
	s3 = boto3.client('s3')
	response = s3.get_object(Bucket='housing-scraper',Key='housing_wroclaw.data')
	inp=list(json.loads(response['Body'].read()))
	print(len(inp),type(inp))
	
	# create a list of tuples from dictionary values
	values=[]
	for mydict in inp:
	    values.append(tuple(mydict.values()))
	
	# insert and commit
	sql = "INSERT INTO housing_wroclaw (`ID`, `Name`, `District`, `Price`, `Rooms`, `sqm`, `Price_sq`, `Link`, `Latitude`, `Longitude`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
	print(len(inp))
	
	cursor = connection.cursor()
	cursor.executemany(sql,values)
	connection.commit()
	connection.close()
	return 'this many was in input:', len(inp)
	'''
	#test connection
	cursor = connection.cursor()
	cursor.execute('SELECT * from test')
	rows = cursor.fetchall()
	for row in rows:
		print(row)'''