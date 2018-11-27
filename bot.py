import core_test
import dateparser
import numpy as np
from datetime import timedelta
from dateutil.parser import parse
from datetime import datetime
import json
import ngrams
import pandas as pd
import pandasql as ps

global data
global categorisation_level
categorisation_level = ['Brand','Name','Category','Subcategory']
global sql_intents
sql_intents = ["Sales_one_line", "Structured_response"]


def date_preprocessing():
	global data
	new_dates=[]

	unique_dates = data.Date.unique()
	unique_dates.sort()
	unique_dates = unique_dates[::-1]
	
	for index,item in enumerate(unique_dates):
		if index == 0:
			new_dates.append((datetime.now() - timedelta(0)).strftime('%Y-%m-%d'))
		else:
			new_dates.append((datetime.now() - (parse(unique_dates[0]) - parse(unique_dates[index]))).strftime('%Y-%m-%d'))
    
	new_dates = np.array(new_dates)
	data.Date = data.Date.replace(unique_dates, new_dates)
	# print("##################################################")
	# print(data.head())
	# print("##################################################")
	# data.sale_date = pd.to_datetime(data.D)
	# array = data.Date.unique()
	# array.sort()
	# print(array[::-1])    


def date_range_finder(string_date):
	date = parse(dateparser.parse(string_date).strftime('%Y-%m-%d'))

	date_range = []
	if date is None:
		raise Exception("No date could be extracted from the entity")
	else:
		if 'month' in string_date:
			start_date = date.replace(day=1)
			end_date = start_date.replace(month = date.month+1 ) - timedelta(days=1)
			
		elif 'week' in string_date:
			start_date = date.replace(day = date.day - date.weekday() )
			end_date = start_date.replace(day = start_date.day + 6 )
		
		elif 'year' in string_date:
			start_date = date.replace(day=1, month=1)
			end_date = start_date.replace(year = start_date.year+1) - timedelta(days=1)

		else:
			start_date = date 
			end_date = date 

	date_range = [start_date, end_date]
	print(date_range)
	return date_range



def prepare_data():
	global data

	data_bills = pd.read_csv('bills.csv', header=0)
	data_articles = pd.read_csv('articles.csv', header=0)
	data_bills.rename(columns={'article_id':'id'}, inplace=True)
	merged = pd.merge(data_bills,data_articles, on='id', how='left')
	data_heirarchy = pd.read_csv('hierarchy.csv', header=0)
	data_heirarchy.rename(columns={'article_id':'id'}, inplace=True)
	merged = pd.merge(merged, data_heirarchy, on='id', how='left')
	merged.rename(columns={
		'id':'ID',
		'sale_date':'Date',
		'total_price':'Total_Price',
		'category_name':'Category',
		'subcategory_name':'Subcategory',
		'brand_name':'Brand',
		'name':'Name'
		}, inplace=True)

	data = merged
	# ngrams.create_lookup(data) 
	# df = data.copy(deep=True)
	# print(df.head())
	# pysqldf = lambda q: sqldf(q, locals())
	# df = ps.sqldf(" select ID from df ", locals())
	# print("###############################")
	# print(df.head())
	# print("###############################")



def bot():
	
	while(1):
		# print()
		print("######### Hi! Enter your question.. Type stop to Stop ##########")
		question=input('User: ')
		if question == 'stop':
			print(" Bye!..")
			break
		query,nlu_json = core_test.core_message(question)
		result=preprocessing_query(query,nlu_json)
		# print()
		print("Bot: ", result)
		print()


def preprocessing_query(query,nlu_json):
	global data
	global categorisation_level
	df=data.copy(deep=True)
	# pysqldf = lambda q: sqldf(q, locals())
	
	for item in nlu_json["entities"]:
		if item["entity"] in categorisation_level:
			df=df[df[item["entity"]] == item["value"]]

		elif item["entity"] == "Hierarchy":
			query = query.replace('None', item["value"])
			# df = df.loc[:,['ID',item["value"],'Total_Price']]
		
		elif item["entity"] == "DATE":
			date_range = date_range_finder(item["value"])
			df.Date = pd.to_datetime(df.Date, errors = 'coerce')
			filter1 = df.Date >= date_range[0]
			filter2 = df.Date <= date_range[1]
			df = df[filter1 & filter2]
			# date = dateparser.parse(item["value"])
	# print(nlu_json["intent"])
	# if nlu_json["intent"]["name"] == "greet":
	# 	return query

	if nlu_json["intent"]["name"] in sql_intents:
		query = query.replace('None','Name')
		print("---------UNIQUE DATES-----------")
		# print(df.Date.unique())
		print(nlu_json["intent"]["name"])
		print(df)
		print("---------UNIQUE DATES-----------")
		df = ps.sqldf(query, locals())
		if nlu_json["intent"]["name"] == "Sales_one_line":
			try:
				query = " Rs. {:.2f} ".format(df.SalesValue[0])
			except Exception as e:
				print("Sorry empty Dataframe after filtering on entities extracted...")
		else:
			df.SalesValue = df.SalesValue.round(2)
			return df.head(10)
		
	return query


if __name__ == "__main__":

	prepare_data()
	ngrams.prepare_articles_data()
	date_preprocessing()
	# date_range_finder("2 days ago")
	bot()
