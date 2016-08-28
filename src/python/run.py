import ConfigParser
import sys, traceback
from slackclient import SlackClient
from chatterbot import ChatBot
import os
from os import listdir
from os.path import isfile, join


from chatterbot.trainers import ChatterBotCorpusTrainer




config = ConfigParser.SafeConfigParser({"host": "searchhub.lucidworks.com", "port":80})
config.read('config.cfg')

token = config.get("Slack", "token")  # found at https://api.slack.com/web#authentication
channel_str = config.get("Slack", "channels")
channel_names = []
if channel_str:
    #print (channel_str)
    channels = channel_str.split(",")
    for channel in channels:
        #print channel
        channel_names.append(channel)


storage = config.get("Chatterbot", "storage_dir")
if not os.path.exists(storage):
    os.makedirs(storage)

bot_name = config.get("Slack", "bot_name")
print "Starting Slack"
sc = SlackClient(token)
print "Starting Chatterbot"
chatbot = ChatBot(bot_name, storage_adapter="chatterbot.adapters.storage.JsonDatabaseAdapter",
                  logic_adapters=[
                    "chatterbot.adapters.logic.MathematicalEvaluation",
                    "chatterbot.adapters.logic.TimeLogicAdapter",
                    "chatterbot.adapters.logic.ClosestMeaningAdapter",
                    "adapters.SearchHubLogicAdapter"
                    ],
                  searchhub_host=config.get("SearchHub", "host"),
                  searchhub_port=config.get("SearchHub", "port"),
                  input_adapter="adapters.SlackPythonInputAdapter",
                  output_adapter="adapters.SlackPythonOutputAdapter",
                  database=storage + "/database.json",
                  slack_client=sc,
                  slack_channels=channel_names,
                  slack_output_channel=config.get("Slack", "output_channel"),
                  slack_bot_name=bot_name
                  )

chatbot.set_trainer(ChatterBotCorpusTrainer)
training_dir = "training"
files = [f for f in listdir(training_dir) if isfile(join(training_dir, f)) and f.endswith(".json") and f.find("example.json") == -1]
for file in files:
    print "Training on " + file
    chatbot.train("training." + file.replace(".json", ""))
# Train based on english greetings corpus
chatbot.train("chatterbot.corpus.english")

# Train based on the english conversations corpus
#chatbot.train("chatterbot.corpus.english.conversations")
print "Starting Chatbot"
while True:
    try:
        bot_input = chatbot.get_response(None)
    except(Exception):
        print "Exception"
        traceback.print_exc(Exception)


