# The MIT License (MIT)
#
# Copyright (c) 2013 Daigo Tanaka (@daigotanaka)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import datetime
import re
import pj_twilio

from plugins import Plugin
from pj_twilio import PjTwilio

def register(app):
    if not app.config.get("pj_twilio")["active"]:
        return
    global pj_twilio_plugin
    pj_twilio_plugin = PjTwilioPlugin(app)

    app.register_command(["answer the phone", "take the call"], "pj_take_call", pj_twilio_plugin.take_call)
    app.register_command(["make a phone call to"], "pj_make_call", pj_twilio_plugin.make_call)

class PjTwilioPlugin(Plugin):
    def __init__(self, app):
        my_number = app.config.get("pj_twilio")["my_number"]
        sip_domain = str(app.config.get("pj_twilio")["sip_domain"])
        sip_username = str(app.config.get("pj_twilio")["sip_username"])
        sip_password = str(app.config.get("pj_twilio")["sip_password"])
        twilio_account_sid = app.config.get("pj_twilio")["twilio_account_sid"]
        twilio_auth_token = app.config.get("pj_twilio")["twilio_auth_token"]
        twiml_url = app.config.get("pj_twilio")["twilml_url"]

        self.pj_twilio = PjTwilio(
            my_number,
            sip_domain,
            sip_username,
            sip_password,
            twilio_account_sid,
            twilio_auth_token,
            twiml_url,
            incoming_call_callback=self.incoming_call_callback)
        self.pj_twilio.on_hangup_callback = self.on_hangup
        self.pj_twilio.start()

        super(PjTwilioPlugin, self).__init__(app)

    def make_call(self, param):
        nickname = param
        to_ = self.app.addressbook.get_primary_phone(nickname.lower())
        if not to_:
            self.app.say("Sorry, I cannot find the contact")
            return
        self.app.logger.debug(to_)

        self.app.mute()
        self.pj_twilio.make_twilio_call(to_)

    def incoming_call_callback(self, from_):
        r = re.match(r".*sip:[+]*(\w+)@", from_)
        caller = r.group(1)

        try:
            int(caller)
            head = caller[:-10] if len(caller) > 10 else ""
            caller = (head + "-" + caller[-10:-7] + "-" + caller[-7:-4] + "-" +
                caller[-4:])
        except ValueError:
            pass
        self.app.say("Call from %s" % caller)

    def take_call(self):
        self.app.mute()
        self.pj_twilio.answer()

    def on_hangup(self):
        self.app.unmute()
