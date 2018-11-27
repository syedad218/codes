from rasa_nlu.model import Interpreter
import json
import ngrams
import pandas as pd

def prepare_data():

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
    return data

# where model_directory points to the model folder
interpreter = Interpreter.load('models/nlu/default/current')
data=prepare_data()
# result = interpreter.parse("sales of nestle in this week".lower())
matches = ngrams.find_entity_ngrams(data, "sale of pacha pairu yellow in this week")
for index,match in enumerate(matches):
    print("{} match: {}".format(index+1,match))
    print()

# print(json.dumps(result, indent=2))