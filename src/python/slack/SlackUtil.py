import json

def get_channel(sc, channel_name):
    chan_list = get_channel_list(sc)
    for chan in chan_list["channels"]:
        if chan["name"] == channel_name:
            return chan
    return None


def get_channels_to_monitor(sc, channel_names):
    to_monitor = []
    chan_list = get_channel_list(sc)
    # print chan_list
    for chan in chan_list["channels"]:
        if chan["name"] in channel_names:
            to_monitor.append(chan["id"])
    # print to_monitor
    return to_monitor


def get_channel_list(sc):
    chan_list = json.loads(sc.server.api_call("channels.list"))
    #print "Getting channel list"
    return chan_list
