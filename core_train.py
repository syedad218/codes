
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.agent import Agent

agent = Agent('domain.yml', policies=[KerasPolicy()])
training_data = agent.load_data('stories.md')
agent.train(
        training_data,
        validation_split=0.0,
        epochs=300
)

agent.persist('models/dialogue')