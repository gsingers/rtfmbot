import ConfigParser
import time
import json
from slackclient import SlackClient
from chatterbot import ChatBot
import os
from os import listdir
from os.path import isfile, join
import training

from chatterbot.trainers import ChatterBotCorpusTrainer


def get_channels_to_monitor(sc, channel_names):
    to_monitor = []
    chan_list = json.loads(sc.server.api_call("channels.list"))
    print "Getting channel list"
    #print chan_list
    for chan in chan_list["channels"]:
        if chan["name"] in channel_names:
            to_monitor.append(chan["id"])
    #print to_monitor
    return to_monitor


config = ConfigParser.RawConfigParser()
config.read('config.cfg')

token = config.get("Slack", "token")  # found at https://api.slack.com/web#authentication
channel_str = config.get("Slack", "channels")
channel_names = []
if channel_str:
    print (channel_str)
    channels = channel_str.split(",")
    for channel in channels:
        #print channel
        channel_names.append(channel)


storage = config.get("Chatterbot", "storage_dir")
if not os.path.exists(storage):
    os.makedirs(storage)

bot_name = config.get("Slack", "bot_name")
chatbot = ChatBot("RTFM Bot", storage_adapter="chatterbot.adapters.storage.JsonDatabaseAdapter",
      logic_adapters=[
        "chatterbot.adapters.logic.MathematicalEvaluation",
        "chatterbot.adapters.logic.TimeLogicAdapter",
        "chatterbot.adapters.logic.ClosestMeaningAdapter"
    ],
    output_adapter="chatterbot.adapters.output.OutputFormatAdapter",
    output_format='json',
    database=storage + "/database.json")
chatbot.set_trainer(ChatterBotCorpusTrainer)
training_dir = "training"
files = [f for f in listdir(training_dir) if isfile(join(training_dir, f)) and f.endswith(".json") and f.find("example.json") == -1]
for file in files:
    print "Training on " + file
    chatbot.train("training." + file.replace(".json", ""))
# Train based on english greetings corpus
#chatbot.train("chatterbot.corpus.english.greetings")

# Train based on the english conversations corpus
#chatbot.train("chatterbot.corpus.english.conversations")

sc = SlackClient(token)
# Look up the channels to monitor channel names
monitor = get_channels_to_monitor(sc, channel_names)
print "Starting Slack"
if sc.rtm_connect():
    while True:
        payload = sc.rtm_read()
        if payload:
            #print payload
            for item in payload:
                #print item
                #{u'text': u'hi', u'ts': u'1472181456.000131', u'user': u'U027M0MDZ', u'team': u'T027EHDJB', u'type': u'message', u'channel': u'C03U0R1MB'}
                if item["type"] == "message" and item["channel"] in monitor:
                    if "subtype" in item and item["subtype"] == "bot_message":
                        #don't reply to other bots, especially ourself!  Although it is somewhat amusing watching chatterbot have a convo w/ itself
                        continue
                    rtfm_rsp_json = chatbot.get_response(item["text"])
                    #print rtfm_rsp_json
                    if rtfm_rsp_json:
                        sc.api_call(
                            "chat.postMessage", channel=item["channel"], text=rtfm_rsp_json["text"],
                            username=bot_name)
                    #we have a message, let's see if we can reply via the bot

        time.sleep(1)
else:
    print "Connection Failed, invalid token?"


