import smtplib
import logging
from email.mime.text import MIMEText

from django.conf import settings

LOG = logging.getLogger(__name__)

_MAIL = None


class Mailer(object):
    def __init__(self, mail_host, mail_user, mail_password, mail_postfix=None):
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_password = mail_password
        if not mail_postfix:
            # mail_postfix = gmail.com
            self.mail_postfix = '.'.join(mail_host.split('.')[1:])
        self.client = None

    def connect(self):
        LOG.debug("Connecting to email server: %s" % self.mail_host)
        try:
            self.client = smtplib.SMTP_SSL(self.mail_host)
        except smtplib.SMTPException:
            self.client = smtplib.SMTP(self.mail_host)

        self.client.login(self.mail_user, self.mail_password)

    def send_mail(self, to_list, sub, content):
        LOG.debug("Send email to %s" % to_list)
        if not self.client:
            self.connect()

        assert to_list
        me = "%s<%s@%s>" % (self.mail_user, self.mail_user, self.mail_postfix)
        msg = MIMEText(content)
        msg.set_charset('UTF-8')
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = ";".join(to_list)

        self.client.sendmail(me, to_list, msg.as_string())

    def close(self):
        self.client.close()


def send(subject, content):
    global _MAIL
    if not _MAIL:
        _MAIL = Mailer(settings.EMAIL_HOST,
                       settings.EMAIL_USER, settings.EMAIL_PASSWORD)

    receivers = settings.EMAIL_RECEIVERS
    _MAIL.send_mail(receivers, subject, content)
