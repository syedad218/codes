from rasa_nlu.training_data import load_data
from rasa_nlu import config
from rasa_nlu.model import Trainer

training_data = load_data('nlu.md')
trainer = Trainer(config.load('nlu_config.yml'))
interpreter = trainer.train(training_data)
model_directory = trainer.persist('models/nlu', fixed_model_name="current")

print(model_directory)