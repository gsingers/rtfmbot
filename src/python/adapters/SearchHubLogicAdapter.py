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
        print "can process!"
        print statement
        return True

    def process(self, statement):
        print "calculating: {0}".format(statement)
        result = Statement("Hi")
        params = {
            "wt":"json",
            "q": statement.text,
            "rows": 3,
            "fl": "id,title,subject,body,score",
            "fq":"isBot:false"
        }
        print "params: {0}".format(params)
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
                url = self.shub_display_url.format(self.host, self.port, urllib.urlencode({"q": statement.text}))
                response = "SearchHub says...\n\tSee full results: {0}\n\n".format(url)

                docs = rsp["response"]["docs"]
                print "docs: {0}".format(docs[0])
                #confidence = docs[0]["score"]
                #should we put a score threshold or normalize?
                i = 0
                for doc in docs:
                    display = ""
                    if "title" in doc:
                        display = doc["title"]
                    elif "subject" in doc:
                        display = doc["subject"]
                    #see how similar the display value is to the original
                    similarity = self.closest.get_similarity(statement.text, display)
                    print similarity
                    confidence += similarity#should we add here?  Probably not, but let's try it

                    response += "{0}:\n\t{1}\n\t{2}\n".format(i, doc["id"], display)
                    i += 1
                result = Statement(response)

        print "Conf: {0}, Res: {1}".format(confidence, result)
        return confidence, result

