import json
from jprint import jprint
from BayesClassifier import junknotjunk


testemail = {
    "from": "ericparker4@live.com",
    "ts": "2023-01-18T11:49:20-08:00",
    "urls": ["https://query.ai"],
    "subject": "budget approval",
    "body": "I do realize that the proposed dues rate, per this draft, is showing a huge jump in dues.  The main reason is per the recommended reserve funding amount in the reserve study.  We are only legally allowed to increase the dues 20% from one year to the next, so this will likely be where we have to cut significantly to keep it under this level.",
    "junk": "notjunk"
}

testemail2 = {
    "eid": "9m98zqCJhodqEYcn7uyznp",
    "aid": "m23462113",
    "from": "no-reply@twitch.tv",
    "to": [
        "firewalleric@gmail.com"
    ],
    "replyto": [],
    "ts": "2023-02-27T18:16:25+00:00",
    "urls": [],
    "subject": "m4913223 dont miss stuff",
    "body": "",
}

testemail3 = {
    "eid": "f4trKwzS2cLvpY47kg2375",
    "aid": "m23462113",
    "from": "support@tripit.com",
    "to": [
        "firewalleric@gmail.com"
    ],
    "replyto": [
        "do-not-reply@tripit.com"
    ],
    "ts": "2022-12-12T16:21:49+00:00",
    "urls": [
        "https://www.tripit.com/trip/show/id/323717281?us=ti&um=txnemail&un=pretrip",
        "https://www.tripit.com/pro/upgrade?us=ti&um=txnemail&uc=2&un=pretrip",
        "https://www.tripit.com/web/traveler-resource-center?us=ti&um=txnemail&un=pretrip",
        "https://www.tripit.com/pro/upgrade?us=ti&um=txnemail&uc=2&un=sharetriptrypro",
        "https://www.facebook.com/tripitcom",
        "https://twitter.com/TripIt",
        "http://www.linkedin.com/company/tripit",
        "https://instagram.com/tripitcom/",
        "http://www.youtube.com/user/tripitvideos",
        "http://www.tripit.com/blog",
        "https://www.tripit.com/account/edit/section/email_settings?us=ti&um=txnemail&un=pretrip",
        "https://www.tripit.com/uhp/privacyPolicy?us=ti&um=txnemail&un=pretrip",
        "https://help.tripit.com"],
    "subject": "mobjack trip san jose starting soon",
    "body": "hello mobjack pack bags trip san jose starts thursday head itinerary check flight make updates share plans friends family httpswww tripit become pro traveler well keep eye status fare refund possibilities something changes youll first know tripits resource center helps better understand expect informed decisions happy travels try free get instant alerts cancellations refunds open seats facebook comtripitcom twitter httpstwitter comtripit linkedin httpwww comcompanytripit instagram httpsinstagram youtube comusertripitvideos blog comblog 601 108th ave suite 1000 bellevue 98004 20062022 concur technologies inc rights reserved registered trademark trademarks held respective owners unsubscribe privacy policy help httpshelp",
    "folder": "INBOX",
}


def main():
    jnj = junknotjunk('m23462113')
    is_isnot_junk = jnj.get_junk_stats(testemail)
    print(is_isnot_junk)


if __name__ == main():
    main()
