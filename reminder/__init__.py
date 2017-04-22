#
# Example of features:
# a) multi-thread: same skill can be different executions in parallel
# b) use of local stt with the possibility of switch between grammars
#

from adapt.intent import IntentBuilder
from mycroft.skills.multi_thread_skill import MultiThreadSkill, SkillSession
from mycroft.util.log import getLogger

logger = getLogger(__name__)

#
# Each time the intent is received, a new session is created.
# Session class must inherit from SkillSession
#
class RemainderSession(SkillSession):
    def __init__(self, id, skill):
        super(RemainderSession, self).__init__(id, skill)
        self.file_path = self.skill.config.get('filename')

    #
    # execution of command "graba un mensaje" 
    #
    def intent_record(self, msg):
        # send audio asking for the message to be recorded
        self.speak_dialog( 'audio.record.start',
                           context = {"session": self.id} )

        # wait until end of audio
        self.wait()

        # record message: grammar = False because this message 
        # doesn't need translation with STT.
        record message
        self.record( { 'grammar' : False,
                       'record_filename' : self.file_path } )

        # wait until end of record
        self.wait()

        # send final message
        self.speak_dialog( 'audio.record.stop',
                           context={ "session": self.id } )

class RemainderSkill(MultiThreadSkill):
    def __init__(self):
        # call super with the class used for the sessions
        super(RemainderSkill, self).__init__(
                   "RemainderSkill", RemainderSession)

    def initialize(self):
        super(RemainderSkill,self).initialize()

        # register intents in the usual way
        intent = IntentBuilder("RemainderSkillIntent").require(
            "RemainderSkillKeyword").build()
        self.register_intent(intent, RemainderSession.intent_record)

def create_skill():
    return RemainderSkill()
