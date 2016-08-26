import ConfigParser
import time
import json
from slackclient import SlackClient
from chatterbot import ChatBot
import os
from os import listdir
from os.path import isfile, join
import training
from slack import SlackUtil
from adapters import SearchHubLogicAdapter

from chatterbot.trainers import ChatterBotCorpusTrainer

def process_message(item):
    if "subtype" in item and item["subtype"] == "bot_message":
        return False
    return True

def is_question(text):
        #look for some basic indicators that this is actually a question
    text = text.lower()
    if text.endswith("?") or text.startswith("how do i") or text.startswith("where are") or text.startswith("what"):
        return True
    return False

config = ConfigParser.SafeConfigParser({"host": "searchhub.lucidworks.com", "port":80})
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
                    "chatterbot.adapters.logic.ClosestMeaningAdapter",
                    "adapters.SearchHubLogicAdapter"
                    ],
                  searchhub_host=config.get("SearchHub", "host"),
                  searchhub_port=config.get("SearchHub", "port"),
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

output_channel = SlackUtil.get_channel(sc, config.get("Slack", "output_channel"))
#print output_channel
# Look up the channels to monitor channel names
monitor = SlackUtil.get_channels_to_monitor(sc, channel_names)
print "Starting Slack"


def get_output_channel(output_channel, item):
    output = None
    if output_channel:
        output = output_channel["id"]
    else:
        output = item["channel"]
    return output


if sc.rtm_connect():
    while True:
        payload = sc.rtm_read()
        if payload:
            #print payload
            for item in payload:

                #{u'text': u'hi', u'ts': u'1472181456.000131', u'user': u'U027M0MDZ', u'team': u'T027EHDJB', u'type': u'message', u'channel': u'C03U0R1MB'}
                if "channel" in item and item["channel"] in monitor:
                    if item["type"] == "message":
                        if process_message(item):
                            is_q = is_question(item["text"])
                            output = get_output_channel(output_channel, item)
                            sc.api_call(
                                    "chat.postMessage", channel=output, text="Thinking...",
                                    username=bot_name)
                            #print item
                            rtfm_rsp_json = chatbot.get_response(item["text"])
                            print "Chatterbot rsp: {0}".format(rtfm_rsp_json)
                            if rtfm_rsp_json:
                                #we have a message, let's see if we can reply via the bot

                                sc.api_call(
                                    "chat.postMessage", channel=output, text=rtfm_rsp_json["text"],
                                    username=bot_name)
                                #if we have a question answer pair, perhaps we want to do something with it?


                        #else:
                        #    print "Skipping"
                        #    print item
                elif item["type"] == "reaction_added":
                    #{u'event_ts': u'1472227659.147767', u'item': {u'type': u'message', u'ts': u'1472227650.000003', u'channel': u'C2550PQD9'}, u'type': u'reaction_added', u'user': u'U027M0MDZ', u'reaction': u'+1'}
                    sub_item = item["item"]
                    if sub_item["channel"] in monitor:
                        #if we have a positive reaction, let's do something smart to save the message
                        print item

        time.sleep(1)
else:
    print "Connection Failed, invalid token?"


