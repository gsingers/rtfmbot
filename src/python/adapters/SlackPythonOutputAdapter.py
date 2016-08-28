from chatterbot.adapters.output import OutputAdapter
from slack import SlackUtil
from chatterbot.conversation import Statement

class SlackPythonOutputAdapter(OutputAdapter):


    def __init__(self, **kwargs):
        super(SlackPythonOutputAdapter, self).__init__(**kwargs)
        output_channel_name = kwargs.get("slack_output_channel")
        self.direct_to_user = False
        self.sc = kwargs.get("slack_client")
        #print "OCN: {0}".format(output_channel_name)
        if output_channel_name.strip() == "DIRECT_TO_USER":
            self.output_channel = None
            self.direct_to_user = True
        else:
            self.output_channel = SlackUtil.get_channel(self.sc, output_channel_name)
            self.direct_to_user = False
        self.bot_name = kwargs.get("slack_bot_name")


    def process_response(self, item):
        output = self.get_output_channel(self.output_channel, item)
        if output:
            self.sc.api_call(
                "chat.postMessage", channel=output, text=item.text,
                username=self.bot_name)
            #if we have a question answer pair, perhaps we want to do something with it?
        else:
            print "Unable to send output, no channel specified"


    def get_output_channel(self, output_channel, item):
        #print item.extra_data
        #print self.direct_to_user
        if self.direct_to_user and "slack_user" in item.extra_data:
            output = item.extra_data["slack_user"]
            print "Sending: {0}".format(output)
        elif output_channel:
            output = output_channel["id"]
        elif "channel" in item.extra_data:
            output = item.extra_data["channel"]
        else:
            output = None
        return output

