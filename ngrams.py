import pandas as pd 
from Levenshtein.StringMatcher import StringMatcher as SequenceMatcher
import re

global lookup_dictionary 
lookup_dictionary = {}
global columns 
columns = ['Name','Category','Subcategory','Brand']
global all_entities
all_entities = None

def prepare_articles_data():
	data_articles = pd.read_csv('articles.csv', header=0)
	data_heirarchy = pd.read_csv('hierarchy.csv', header=0)
	data_heirarchy.rename(columns={'article_id':'id'}, inplace=True)
	merged = pd.merge(data_articles, data_heirarchy, on='id', how='left')

	merged.rename(columns={
		'id':'ID',
		'category_name':'Category',
		'subcategory_name':'Subcategory',
		'brand_name':'Brand',
		'name':'Name'
		}, inplace=True)

	data = merged
	create_lookup(data)


def create_lookup(data):
    global lookup_dictionary
    global columns
    global all_entities

    for column in columns:
        lookup_dictionary.update(dict(zip(data[column].unique(),[column]*len(data[column].unique()))))
        if all_entities is None:
            all_entities = data[column]
        else:
            all_entities = all_entities.append(data[column], ignore_index=True)

    all_entities = pd.Series(all_entities.unique())
    length_series = all_entities.str.len()
    all_entities = all_entities.reindex(length_series.sort_values(ascending=False).index)
    # print(len(all_entities.unique()))
    # print(len(lookup_dictionary))


def preprocess_question(question):
    ### tokenize on whitespace #######
    words=question.split()
    return words
    # print(words)


def ngram(words):
    n=10
    final_set=set()
    for ngram_value in range(n):
        final_set = final_set.union(set(zip(*[words[i:] for i in range(ngram_value)])))
    return sorted(final_set, key=lambda x:len(x))


def similarity_function(word1,word2):
    similarity = SequenceMatcher(
        None,
        word1,
        word2
        )
    # Calculate a decimal percent of the similarity
    return round(similarity.ratio(), 2)


def find_entity_ngrams(question):
    words = preprocess_question(question)
    matches=find(words)
    return matches


def find(words):
    global all_entities
    final_set = ngram(words)
    matches=[]
    for article in all_entities:
        article_temp = re.sub(r'[^a-zA-Z0-9\s]', '', article)
        max_score=0.0
        match = None
        article_temp = ''.join(article_temp.split())
        for item in list(final_set):
            temp=''.join(item)
            temp = re.sub(r'[^a-zA-Z0-9\s]', '', temp)
            if abs(len(temp)-len(article_temp)) <= 10:
                score = similarity_function(temp,article_temp)
                if score>=0.81 and score > max_score and len(article)>=5 :
                    max_score = score
                    match = item
                elif score>=0.9 and score>max_score:
                    max_score=score
                    match = item
        if match is not None:       
            print(max_score)
            print(match)
            matches.append({'value': article, 'entity': lookup_dictionary[article]})
            words=list((' '.join(words).replace(' '.join(match),'')).split())
            print(article)
            final_set = ngram(words)
    
    return matches
