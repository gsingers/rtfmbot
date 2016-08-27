from chatterbot.adapters.output import OutputAdapter
from slack import SlackUtil
from chatterbot.conversation import Statement

class SlackPythonOutputAdapter(OutputAdapter):


    def __init__(self, **kwargs):
        super(SlackPythonOutputAdapter, self).__init__(**kwargs)
        output_channel_name = kwargs.get("slack_output_channel")
        self.sc = kwargs.get("slack_client")
        self.output_channel = SlackUtil.get_channel(self.sc, output_channel_name)
        self.bot_name = kwargs.get("slack_bot_name")


    def process_response(self, item):
        output = self.get_output_channel(self.output_channel, item)
        text = item.text
        self.sc.api_call(
            "chat.postMessage", channel=output, text=text,
            username=self.bot_name)
            #if we have a question answer pair, perhaps we want to do something with it?


    #else:
    #    print "Skipping"
    #    print item

    def get_output_channel(self, output_channel, item):
        if output_channel:
            output = output_channel["id"]
        else:
            output = item["channel"]
        return output

