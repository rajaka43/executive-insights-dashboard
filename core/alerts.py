import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from twilio.rest import Client

class NotificationManager:
    def __init__(self):
        self.enabled = True
        
        # 1. Email Credentials (ඔයා කලින් හදාගත්ත ටික මෙතනට දාන්න)
        self.sender_email = os.getenv('SENDER_EMAIL', 'virajrajaka8@gmail.com')
        self.sender_app_password = os.getenv('SENDER_PASSWORD', 'psiz pnxd vwbp xnaod')

        # 2. Twilio WhatsApp Credentials
        # ⚠️ Twilio එකවුන්ට් එකක් හදලා ලැබෙන ඇත්තම SID සහ Token එක මෙතනට දාන්න මචන්
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'YOUR_TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'YOUR_TWILIO_AUTH_TOKEN')
        self.whatsapp_from = 'whatsapp:+14155238886' # Twilio Sandbox සයිට් එකෙන් දෙන නම්බර් එක

        # Twilio Client එක සක්‍රීය කිරීම
        if self.account_sid != 'YOUR_TWILIO_ACCOUNT_SID':
            self.twilio_client = Client(self.account_sid, self.auth_token)
        else:
            self.twilio_client = None

    def send_email_report(self, to_email: str, subject: str, html_content: str):
        """Gmail SMTP හරහා Executive Report එක Email කිරීම"""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_app_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"[ERROR] Email Failed: {e}")
            return False

    def send_whatsapp_report(self, to_number: str, message_body: str):
        """Twilio Sandbox හරහා WhatsApp වාර්තාවක් සජීවීව යැවීම"""
        if not self.twilio_client:
            print("[WARNING] Twilio client not configured. Skipping WhatsApp send.")
            return False

        try:
            # නම්බර් එක ඉස්සරහට whatsapp: කෑල්ල නැත්නම් ඒක එකතු කරනවා
            formatted_to = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
            
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=self.whatsapp_from,
                to=formatted_to
            )
            print(f"[SUCCESS] WhatsApp sent! SID: {message.sid}")
            return True
        except Exception as e:
            print(f"[ERROR] WhatsApp Failed: {e}")
            return False