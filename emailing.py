import smtplib
import creds
import imghdr
from email.message import EmailMessage

username = creds.getusername()
password = creds.get_password()
receiver = creds.get_receiver()


def send_email(image_path):
    message = EmailMessage()
    message["Subject"] = "Object Detected"
    message.set_content("Hey! Something moved in the cameras scope")

    with open(image_path, "rb") as file:
        content = file.read()

    message.add_attachment(content, maintype="image", subtype=imghdr.what(None, content))
    gmail = smtplib.SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(username, password)
    gmail.sendmail(username, receiver, message.as_string())
    gmail.quit
