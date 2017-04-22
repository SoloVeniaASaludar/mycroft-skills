import threading

from adapt.intent import IntentBuilder

from mycroft.skills.multi_thread_skill import MultiThreadSkill, SkillSession
from mycroft.util.log import getLogger

logger = getLogger(__name__)
__author__ = 'seanfitz'

class RemainderSession(SkillSession):
    def __init__(self, id, skill):
        super(RemainderSession, self).__init__(id, skill)
        self.file_path = self.skill.config.get('filename')

    def intent_record(self, msg):
        self.speak_dialog( 'audio.record.start',
                           context = {"session": self.id} )
        self.wait()

        self.record( { 'grammar' : False,
                       'record_filename' : self.file_path } )
        self.wait()

        self.speak_dialog( 'audio.record.stop',
                           context={ "session": self.id } )

class RemainderSkill(MultiThreadSkill):
    def __init__(self):
        super(RemainderSkill, self).__init__(
                   "RemainderSkill", RemainderSession)

    def initialize(self):
        super(RemainderSkill,self).initialize()

        intent = IntentBuilder("RemainderSkillIntent").require(
            "RemainderSkillKeyword").build()
        self.register_intent(intent, RemainderSession.intent_record)

def create_skill():
    return RemainderSkill()
