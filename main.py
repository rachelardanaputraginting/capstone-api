import smtplib

smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "rachelardanaputraginting@gmail.com"
password = "hzfrkbchlxrgkznl"

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(username, "dindaindriana0911@gmail.com", "Test email from Flask")
        print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
