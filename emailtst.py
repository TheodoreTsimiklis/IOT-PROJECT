
import smtplib

email = ""
password = ""

with smtplib.SMTP('outlook.office365.com', 587) as smtp:
	smtp.ehlo()
	smtp.starttls()
	smtp.ehlo()

	smtp.login(email, password)

	subject = 'hello'
	body = 'this is a test'

	msg = f'subject: {subject}\n\n{body}'

	smtp.sendmail(email, email, msg)
