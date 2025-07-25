import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content("Test email")
msg["Subject"] = "Test"
msg["From"] = "studentrecognition971@gmail.com"  # Changed to match login email
msg["To"] = "danielamoakokodua698@gmail.com"

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login("studentrecognition971@gmail.com", "ogzi esuy jdab ftjh")
    server.send_message(msg)
    
print("Email sent")
