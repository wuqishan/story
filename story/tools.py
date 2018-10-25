import hashlib
from scrapy.mail import MailSender
from story.settings import *


def get_md5(string):
    m = hashlib.md5()
    m.update(string.encode("utf8"))

    return m.hexdigest()


def sendmail(settings, type, data):
    sendto = [
        "1174955828@qq.com"
    ]
    if type == 1:
        subject = "新增小说"
    else:
        subject = "新增章节"

    body = "<h1>{}</h1>".format(subject)
    for d in data:
        body += "<br />"
        for k in d:
            body += '<span>{}</span>：<span>{}</span><br />'.format(k, d[k])

    mailer = MailSender.from_settings(settings)
    mailer.send(to=sendto, subject=subject, body=body, mimetype="text/html")
