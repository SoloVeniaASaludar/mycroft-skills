#
# Disclaimer: no relation with LG, use absolutely at your risks.
# Based on: github.com/ubaransel/lgcommander/blob/master/lgcommander.py
#

# configuration example:
#   "LgSmartTvSkill": {
#  }

import httplib as http
import xml.etree.ElementTree as etree

from adapt.intent import IntentBuilder
from mycroft.skills.multi_thread_skill import MultiThreadSkill, SkillSession
from mycroft.util.log import getLogger

logger = getLogger(__name__)

headers = {"Content-Type": "application/atom+xml"}

class LgSmartTvSession(SkillSession):

    def __init__(self, id, skill):
        super(LgSmartTvSession, self).__init__(id, skill)
        self.ip_address = self.skill.config.get('ip_address', '192.168.1.36')
        self.conn = http.HTTPConnection(self.ip_address, port=8080)
        self.session_id = None

    def display_pairing_key(self):
        xml = '<?xml version="1.0" encoding="utf-8"?><auth><type>AuthKeyReq</type></auth>'
        self.conn.request("POST", "/roap/api/auth", xml, headers=headers)
        self.conn.getresponse()

    def open_session(self):
        pairing_key = self.skill.config.get('pairing_key')
        if not pairing_key:
            self.display_pairing_key()
            self.speak_dialog('configure_pairing_key')
            return

        xml = '<?xml version="1.0" encoding="utf-8"?><auth><type>AuthReq</type><value>%s</value></auth>'%pairing_key
        self.conn.request("POST", "/roap/api/auth", xml, headers=headers)
        response = self.conn.getresponse().read()
        tree = etree.XML(response)
        self.session_id = tree.find('session').text
        logger.debug("session_id=%s", self.session_id)

    def send_command(self, cmnd):
        xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?><command><session>%s</session><type>HandleKeyInput</type><value>%s</value></command>"%(self.session_id,cmnd)
        self.conn.request("POST", "/roap/api/command", xml, headers=headers)
        response = self.conn.getresponse().read()

    #
    # execution of command "pon canal ..."
    #
    def change_tv_channel(self, msg):
        # send audio asking for the message to be recorded
        if not self.session_id:
            self.open_session()
        if self.session_id:
            self.send_command(6)

class LgSmartTvSkill(MultiThreadSkill):
    def __init__(self):
        # call super with the class used for the sessions
        super(LgSmartTvSkill, self).__init__(
                   "LgSmartTvSkill", LgSmartTvSession)

    def initialize(self):
        super(LgSmartTvSkill,self).initialize()

        # register intents in the usual way
        intent = IntentBuilder("ChangeTvChannelIntent").require(
            "ChangeTvChannel").build()
        self.register_intent(intent, LgSmartTvSession.change_tv_channel)

def create_skill():
    return LgSmartTvSkill()
