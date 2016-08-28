from chatterbot.adapters.logic import LogicAdapter
from chatterbot.adapters.logic import ClosestMeaningAdapter
from chatterbot.conversation import Statement
import fusion
import requests
import json
import urllib


class SearchHubLogicAdapter(LogicAdapter):

    def __init__(self, **kwargs):
        super(SearchHubLogicAdapter, self).__init__(**kwargs)

        self.host = kwargs.get("searchhub_host")
        self.port = kwargs.get("searchhub_port")
        self.shub_url = "http://{0}:{1}/api/apollo/query-pipelines/lucidfind-default/collections/lucidfind/select".format(self.host, self.port)
        self.shub_display_url = "http://{0}:{1}/p:%20?{2}" #note the %20 is a hack around how shub handles the projects, eventually we'll pass in filters here
        print "URL: {0}".format(self.shub_url)
        self.closest = ClosestMeaningAdapter()


    def can_process(self, statement):
        #print statement.extra_data
        is_q = False
        is_bot_ask = False
        if "is_question" in statement.extra_data:
            is_q = statement.extra_data["is_question"]
        if "is_bot_ask" in statement.extra_data:
            is_bot_ask = statement.extra_data["is_bot_ask"]
        if statement.text.lower().startswith("shub:"):
            return True
        return is_q or is_bot_ask


    def process(self, statement):
        print "calculating: {0}, {1}".format(statement, statement.extra_data)
        result = None
        input_channel = statement.extra_data["slack_channel"]
        is_q = statement.extra_data["is_question"]
        is_bot_ask = statement.extra_data["is_bot_ask"]
        text = statement.text
        if statement.text.lower().startswith("shub:"):#If the user specifically asks for 'searchhub' (shub), then strip it off
            text = text[5:]
            is_bot_ask = True

        params = {
            "wt":"json",
            "q": text,
            "rows": 3,
            "fl": "id,title,subject,body,score",
            "fq":"isBot:false"
        }
        #TODO: filter projects based on channels
        print "Params: {0}".format(params)
        response = requests.get(self.shub_url, params)
        if response.status_code != 200:
            return 0, None
        rsp = response.json()
        #let's see if we have a decent response

        confidence = 0
        if "response" in rsp:
            #print rsp
            num_found = rsp["response"]["numFound"]
            print num_found
            if num_found > 0:
                url = self.shub_display_url.format(self.host, self.port, urllib.urlencode({"q": text}))
                response = "SearchHub says...\n\tSee full results: {0}\n\n".format(url)

                docs = rsp["response"]["docs"]
                #print "docs: {0}".format(docs[0])
                #confidence = docs[0]["score"]
                #Confidence is the average of the similarity scores, for now
                i = 0
                for doc in docs:
                    display = ""
                    if "title" in doc:
                        display = doc["title"]
                    elif "subject" in doc:
                        display = doc["subject"]
                    #see how similar the display value is to the original
                    similarity = self.closest.get_similarity(text, display)
                    print similarity
                    confidence += similarity#should we add here?  Probably not, but let's try it

                    response += "{0}:\n\t{1}\n\t{2}\n".format(i, doc["id"], display.encode('utf-8'))
                    i += 1
                result = Statement(response)
                #pass through the metadata, so we have channel info

                if i > 0:
                    confidence = confidence / i
                    if is_bot_ask: # boost confidence if the user specifically invoked the kraken
                        confidence += 10
            else:
                print "Couldn't find results for {0}".format(params)
                result = Statement("Shub no find answer.")
                confidence = 0
            #print "Conf: {0}, Res: {1}".format(confidence, result)
        else:
            #print "Couldn't find results for {0}".format(params)
            result = Statement("Shub no find answer.")
            confidence = 0
        result.extra_data = statement.extra_data
        return confidence, result

