# rtfmbot

Disclaimer: This is _way_ early stage.  I don't recommend it for "production" just yet.

# Introduction

We're all tired of answering questions when the person asking clearly hasn't bothered to RTFM or put in any effort.  Perhaps that person is even
  you (I know I'm guilty of it, but dang, Slack makes it so easy to ask questions!) sometimes. Save your context switching for things that matter and deploy
the RTFMbot to your Slack network.  Slack is great for communication, but sometimes it is too good and people ask questions when
answers are easily found on the web or in your knowledge base. 

Building out on the Slack Python Client and [ChatterBot](https://github.com/gunthercox/ChatterBot), this little bot also can dynamically pull in answers from the Open Source community via
[SearchHub](http://searchhub.lucidworks.com) -- our community site built on [Lucidworks Fusion](http://lucidworks.com/products/fusion).  It can also be extended to pull in other sources with a little work.

# Getting Started

You'll need:

1. Python 2.7 (VirtualEnv recommended)
1. NLTK Data.  See http://www.nltk.org/data.html 
 
## Installing
 
1. virtualenv venv
1. source venv/bin/activate
1. pip install -r requirements.txt

## Configuring

1. In src/python, copy sample-config.cfg to config.cfg and fill in the appropriate values

## Running

1. cd src/python
1. python run.py


# Training

Chatterbot trains itself off of the json files located in ```src/python/training```.  Add in training files per https://github.com/gunthercox/ChatterBot/tree/master/chatterbot/corpus
as you see fit and Chatterbot will "learn" off of them, as well as learn as it goes.  See example.json for an example. 
NOTE: example.json is ignored by the trainer.


# TODO:

1. Make the adapters configurable
1. Fusion/Solr storage adapter implementation
1. Do something interesting with new questions
1. Better question parsing
1. Normalize scoring somehow for the SearchHubLogicAdapter so it the others have a chance.
1. Feedback from Slack reactions

# Contributing

Pull requests welcome.  Note, I don't always check on my personal projects every day, so you can expect some delay.
