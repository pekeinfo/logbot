from .common import publish, Message

from sleekxmpp import ClientXMPP

from datetime import datetime
from signal import signal, SIGINT


class LogBot(ClientXMPP):
    def __init__(self, jid, password, rooms):
        ClientXMPP.__init__(self, jid, password)
        self.rooms = rooms

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("groupchat_message", self.publish)

    def session_start(self, event):
        self.register_plugin('xep_0045')
        self.send_presence()
        self.get_roster()

        for room in self.rooms:
            self.plugin['xep_0045'].joinMUC(room, 'logbot', wait=True)

    def xmpp_user(self, xmpp_msg):
        return xmpp_msg['mucnick'] or xmpp_msg['from'].split('@', 1)[0]

    def publish(self, xmpp_msg):
        msg = Message(
            user=self.xmpp_user(xmpp_msg),
            message=xmpp_msg['body'],
            time=datetime.now(),
        )
        publish(msg)


def run(host, port, user, passwd, rooms):
    xmpp = LogBot(user, passwd, rooms)

    signal(SIGINT, lambda signum, frame: xmpp.disconnect())

    xmpp.connect((host, port))
    xmpp.process(block=True)