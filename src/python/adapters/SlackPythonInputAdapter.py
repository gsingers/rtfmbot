from chatterbot.adapters.input import InputAdapter
from slackclient import SlackClient
from slack import SlackUtil
import time
from chatterbot.conversation import Statement

class SlackPythonInputAdapter(InputAdapter):


    def __init__(self, **kwargs):
        super(SlackPythonInputAdapter, self).__init__(**kwargs)
        self.sc = kwargs.get("slack_client")
        channel_names = kwargs.get("slack_channels")
        self.bot_name = kwargs.get("slack_bot_name")
        self.monitor = SlackUtil.get_channels_to_monitor(self.sc, channel_names)
        if not self.sc.rtm_connect():
            raise AttributeError()

    def use_message(self, item):
        if "subtype" in item and item["subtype"] == "bot_message":
            return False
        return True

    def is_question(self, text):
        #look for some basic indicators that this is actually a question
        text = text.lower()
        if text.endswith("?") or text.startswith("how do i") or text.startswith("where are") or text.startswith("what"):
            return True
        return False

    def is_bot_ask(self, text):
        if text.startswith(self.bot_name):
            return True
        return False

    def process_input(self, *args, **kwargs):
        new_message = False
        result = None

        while not new_message:
            payload = self.sc.rtm_read()
            if payload:
                #print payload
                for item in payload:

                    #{u'text': u'hi', u'ts': u'1472181456.000131', u'user': u'U027M0MDZ', u'team': u'T027EHDJB', u'type': u'message', u'channel': u'C03U0R1MB'}
                    if "channel" in item and item["channel"] in self.monitor:
                        if item["type"] == "message":
                            if self.use_message(item) and "text" in item:
                                input_text = item["text"]
                                is_q = self.is_question(input_text)
                                is_bot_ask = self.is_bot_ask(input_text)
                                if is_bot_ask:
                                    input_text = input_text.replace(self.bot_name, "").strip()
                                #Create the statement
                                new_message = True
                                result = Statement(input_text)
                                result.add_extra_data("is_question", is_q)
                                result.add_extra_data("is_bot_ask", is_bot_ask)
                                result.add_extra_data("slack_channel", item["channel"])
                                result.add_extra_data("slack_team", item["team"])
                                result.add_extra_data("slack_user", item["user"])
                                result.add_extra_data("slack_time_stamp", item["ts"])
                                break
                    elif item["type"] == "reaction_added":
                        #{u'event_ts': u'1472227659.147767', u'item': {u'type': u'message', u'ts': u'1472227650.000003', u'channel': u'C2550PQD9'}, u'type': u'reaction_added', u'user': u'U027M0MDZ', u'reaction': u'+1'}
                        sub_item = item["item"]
                        new_message = False
                        if sub_item["channel"] in self.monitor:
                            #if we have a positive reaction, let's do something smart to save the message
                            print item
        #print "q: {0} data: {1}".format(result, result.extra_data)
        return result