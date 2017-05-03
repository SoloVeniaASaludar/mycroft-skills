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
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.util.parse import normalize

logger = getLogger(__name__)

headers = {"Content-Type": "application/atom+xml"}

class LgSmartTvSkill(MycroftSkill):

    def __init__(self):
        super(LgSmartTvSkill, self).__init__("LgSmartTvSkill")
        self.conn = None
        self.session_id = None

    def initialize(self):
        ip_address = self.config.get('ip_address')
        if not ip_address:
            self.speak_dialog('configure_ip_address')
            return
        self.conn = http.HTTPConnection(ip_address, port=8080)

        intent = IntentBuilder("ChangeTvChannelIntent").require(
            "ChangeTvChannel").require("ChannelId").build()
        self.register_intent(intent, self.change_tv_channel)

    def send_get(self, urn):
        self.conn.request("GET", urn, None, headers=headers)
        resp = self.conn.getresponse().read()
        logger.debug(resp)
        return etree.XML(resp)

    def send_post(self, urn, xml=None):
        self.conn.request("POST", urn, xml, headers=headers)
        resp = self.conn.getresponse().read()
        logger.debug(resp)
        return etree.XML(resp)

    def display_pairing_key(self):
        xml = '<?xml version="1.0" encoding="utf-8"?><auth><type>AuthKeyReq</type></auth>'
        self.send_post("/roap/api/auth", xml)

    def open_session(self):
        pairing_key = self.config.get('pairing_key')
        if not pairing_key:
            self.display_pairing_key()
            self.speak_dialog('configure_pairing_key')
            return

        xml = '<?xml version="1.0" encoding="utf-8"?><auth><type>AuthReq</type><value>%s</value></auth>'%pairing_key
        tree = self.send_post("/roap/api/auth", xml)
        self.session_id = tree.find('session').text
        logger.debug("session_id=%s", self.session_id)

    def send_handle_key_input(self, cmnd):
        xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?><command><session>%s</session><type>HandleKeyInput</type><value>%s</value></command>"%(self.session_id,cmnd)
        self.send_post("/roap/api/command", xml)

    def query_volume_info(self):
        tree = self.send_get("/udap/api/data?target=volume_info")
        level = tree.find('data/level').text
        logger.debug("level=%s",level)

    #
    # execution of command "pon canal ..."
    #
    def change_tv_channel(self, msg):
        # logger.debug("msg.data=%s",msg.data)
        # logger.debug("normalize utterance=%s",normalize(msg.data['utterance'],"es"))

        # send audio asking for the message to be recorded
        if not self.session_id:
            self.open_session()
        if self.session_id:
            self.send_handle_key_input(6)
            self.query_volume_info()

def create_skill():
    return LgSmartTvSkill()

