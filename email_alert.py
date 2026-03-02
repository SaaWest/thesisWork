import smtplib
import os
from email.message import EmailMessage
import ssl
from pathlib import Path

class Email_Alert():
    def __init__(self, dockID, email, filePath):
        self.message = dockID
        self.alert_staffList = [email]
        self.filePath = Path(filePath)
        self.password = os.environ.get("app_pass")
        #print(self.password)
        self.admin_email = os.environ.get("test_email")
        #print(self.admin_email)

    def send_alert(self):
        for recp in self.alert_staffList:
            msg = EmailMessage()
            msg["Subject"] = f"IDS Alert" 
            msg["To"] = recp
            msg["From"] = os.environ.get("test_email")
            msg.set_content(f"Attached file for: {self.message}")
            with open(self.filePath, 'rb') as f:
                file_data = f.read()
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=os.path.basename(self.filePath))
        
            context = ssl.create_default_context()

            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                    smtp.ehlo()
                    smtp.starttls(context=context)
                    smtp.ehlo()
                    smtp.login(self.admin_email, self.password)
                    smtp.send_message(msg)
            except Exception as e:
                print(f"Email Exception Occured: {e}")
            #finally:
                #smtp.quit()


    def add_to_list(self, staff_email):
        return self.alert_staffList.append(staff_email)
