#! /usr/bin/python
import re
import urllib
import os
import sys
import argparse
import os.path
from subprocess import Popen,PIPE

# https://nathangrigg.com/2012/04/send-emails-from-the-command-line

def escape(s):
    """Escape backslashes and quotes to appease AppleScript"""
    s = s.replace("\\","\\\\")
    s = s.replace('"','\\"')
    return s

def make_message(content,subject=None, to_addr=None, from_addr=None, send=False, cc_addr=None, bcc_addr=None, attach=None):
    """Use applescript to create a mail message"""
    if send:
        properties = ["visible:false"]
    else:
        properties = ["visible:true"]
    if subject:
        properties.append('subject:"%s"' % escape(subject))
    if from_addr:
        properties.append('sender:"%s"' % escape(from_addr))
    if len(content) > 0:
        properties.append('content:"%s"' % escape(content))

    properties_string = ",".join(properties)

    template = 'make new %s with properties {%s:"%s"}'
    make_new = []
    if to_addr:
        make_new.extend([template % ("to recipient","address", to_addr)])
    if cc_addr:
        make_new.extend([template % ("cc recipient","address",
        escape(addr)) for addr in cc_addr])
    if bcc_addr:
        make_new.extend([template % ("bcc recipient","address",
        escape(addr)) for addr in bcc_addr])
    if attach:
        make_new.extend([template % ("attachment","file name",
        escape(os.path.abspath(f))) for f in attach])
    if send:
        make_new.append('send')
    if len(make_new) > 0:
        make_new_string = "tell result\n" + "\n".join(make_new) + \
        "\nend tell\n"
    else:
        make_new_string = ""

    script = """tell application "Mail"
    make new outgoing message with properties {%s}
    %s end tell
    """ % (properties_string, make_new_string)

    # run applescript
    p = Popen('/usr/bin/osascript',stdin=PIPE,stdout=PIPE)
    p.communicate(script) # send script to stdin
    return p.returncode

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}" sound name "Submarine"'
              """.format(text, title))


email_address = ""
subject = ""
mail_text = ""
notification_text = ""

page = urllib.urlopen("https://www.davidrolo.com/product/stretch-weaver/").read()
testsentence = re.findall('Next restock will occur from the 5th to 6th of June', page)
if not testsentence:
    notify("WEB_CHECKER", notification_text)
    make_message(mail_text, subject, email_address, email_address, True)
