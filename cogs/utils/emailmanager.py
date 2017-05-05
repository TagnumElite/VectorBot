import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Email():
    """Email Class for server email logins
    serverID Required: Server ID
    host default: 'localhost'
    port default:
    email default: ''
    password default: 'None'
    secure default: None"""

    #Universal Vars
    test = "test"

    def __init__(self, serverID, host="localhost", port=25, email="@", password="None", secure=None, keyfile=None, certfile=None):
        self.serverID = serverID
        self.host = host
        self.port = port
        self.email = email
        self.password = password
        self.secure = secure
        if secure == True:
            self.server = smtplib.SMTP_SSL(host, port, keyfile, certfile)
        else:
            self.server = smtplib.SMTP(host, port)
        self.loggedIn = False


    def __del__(self):
        return None

    def __repr__(self):
        return None

    def __str__(self):
        return self.email

    def __cmp__(self, x):
        return

    def __add__(self, x):
        return

    def login(self):
        """Login to the server"""
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.email, self.password)
        self.loggedIn = True

    def send(self, msg, recipient, subject):
        msg = MIMEText(msg)
        if self.loggedIn == False:
            self.login(self)
        msg['Subject'] = subject
        msg['From'] = self.email
        msg['To'] = recipient
        self.server.send_message(msg)

    def send_html(self, msg, recipient, subject):
        raise "NOT WORKING"
        return
        msg = MIMEText(msg)
        if self.loggedIn == False:
            self.login(self)
        msg['Subject'] = subject
        msg['From'] = self.email
        msg['To'] = recipient
        self.server.send_message(msg)

def main():
    server = smtplib.SMTP(".", port=25)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("@", password="")
    msg = MIMEMultipart()
    msg['Subject'] = 'TESTY TEST TEST'
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = ""
    msg['To'] = ""
    msg.preamble = 'Our family reunion'
    #server.sendmail("@", "@", "Test")
    server.send_message(msg)

if __name__ == "__main__":
    main()
