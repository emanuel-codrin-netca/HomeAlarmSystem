# Libraries
import thread
import RPi.GPIO as GPIO
import time
import smtplib

# Email variables
SMTP_SERVER = 'smtp.gmail.com' # Email server
SMTP_PORT = 587 # Server port
GMAIL_USERNAME = 'proiectsm2021emanuelnetca@gmail.com'
GMAIL_PASSWORD = 'Proiect2021!@'
GMAIL_SENDTO = 'emanuel-codrin.netca@student.tuiasi.ro'
GMAIL_SUBJECT = 'Home Alarm System'
GMAIL_CONTENT_IN_FRONT = 'Someone is in front of the door!!!'
GMAIL_CONTENT_LEFT = 'The person in front of the door left!!!'
emailSent = False

class Emailer:
	def sendmail(self, recipient, subject, content):
		# Create headers
		headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient, "MIME-Version: 1.0", "Content-Type: text/html"]
		headers = "\r\n".join(headers)

		# Connect to gmail server
		session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
		session.ehlo()
		session.starttls()
		session.ehlo()

		# Login to gmail
		session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

		# Send email & exit
		session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
		session.quit

sender = Emailer()

# Set GPIO Mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set GPIO pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24
GPIO_BUZZER = 18

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_BUZZER, GPIO.OUT)

# Set TRIGGER and BUZZER to LOW
GPIO.output(GPIO_TRIGGER, False)
GPIO.output(GPIO_BUZZER, False)

keepRunning = True
distance = 0

def measureDistance():
	# Set TRIGGER after 0.5 sec to LOW
	GPIO.output(GPIO_TRIGGER, False)
	time.sleep(0.5)

	# Set TRIGGER afeter 0.01 ms to HIGH
	GPIO.output(GPIO_TRIGGER, True)
	time.sleep(0.00001)

	# Set TRIGGER to HIGH
	GPIO.output(GPIO_TRIGGER, False)

	start = time.time()

	# Save START TIME
	while GPIO.input(GPIO_ECHO) == 0:
		start = time.time()

	# Save STOP TIME
	while GPIO.input(GPIO_ECHO) == 1:
		stop = time.time()

	# Time difference between start and arrival
	elapsed = stop - start

	# Multiply by sonic speed (340300 cm/s) and divide by 2, because, there and back
	distance = elapsed * 17150
	return distance

def playSound(threadName, delay):
	keepRunning
	distance
	while keepRunning:
		if distance <= 30:
			# Set BUZZER, after a period of time, to HIGH
			GPIO.output(GPIO_BUZZER, True)
			time.sleep(0.01 * distance)

			# Set BUZZER, after some a period of time, to LOW
			GPIO.output(GPIO_BUZZER, False)
			time.sleep(0.05 * distance)

		time.sleep(delay)

try:
	distance = measureDistance()
	thread.start_new_thread(playSound, ("BuzzerThread", 0.01))

	while True:
		print ("The distance is: %.2f" % distance)

		if distance >= 30 and emailSent == True:
			# Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
			sender.sendmail(GMAIL_SENDTO, GMAIL_SUBJECT, GMAIL_CONTENT_LEFT)
			print('An email was sent - SUBJECT: ' + GMAIL_SUBJECT + ', CONTENT: ' + GMAIL_CONTENT_LEFT)
			emailSent = False

		if distance < 30 and emailSent == False:
			# Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
			sender.sendmail(GMAIL_SENDTO, GMAIL_SUBJECT, GMAIL_CONTENT_IN_FRONT)
			print('An email was sent - SUBJECT: ' + GMAIL_SUBJECT + ', CONTENT: ' + GMAIL_CONTENT_IN_FRONT)
			emailSent = True

		time.sleep(0.1)
		distance = measureDistance()
except:
	keepRunning = False
	time.sleep(1)
	GPIO.cleanup()
