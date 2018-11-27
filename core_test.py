
from rasa_core.agent import Agent
from rasa_nlu.model import Interpreter
import json
import ngrams
import warnings
import ruamel
import pandas as pd 

warnings.simplefilter('ignore', ruamel.yaml.error.UnsafeLoaderWarning)

interpreter = Interpreter.load('models/nlu/default/current')

agent = Agent.load('models/dialogue', interpreter='models/nlu/default/current')

def core_message(message):
	
	result = interpreter.parse(message.lower())
	matches=ngrams.find_entity_ngrams(message.lower())
	for match in matches:
		result["entities"].append(match)
	print("####################################")
	print(json.dumps(result, indent=2))
	print("####################################")

	responses=agent.handle_text(message.lower())
	answer_query = ""
	for response in responses:
		answer_query = response.get('text')
		# print("Bot: ", response.get('text'))

	return answer_query,result

# core_message("sale of vermicilli on 12-11-2018")