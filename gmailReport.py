from email.mime.text import MIMEText

import smtplib
import config

def gmailReportSending(Titles, Msgs):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(config.gmailAccount, config.gmailAppPassword)

    title = Titles.value.decode("utf-8")
    message = Msgs.value.decode("utf-8")
    msg = MIMEText(message)
    msg['Subject'] = title

    s.sendmail("Kimchi Bot", "@gmail.com", msg.as_string())

    s.quit()
