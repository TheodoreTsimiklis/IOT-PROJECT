import imaplib
import smtplib
import email
from email.header import decode_header
import webbrowser
import os
import datetime
import asyncio
from flask import Flask, request, render_template,jsonify
import RPi.GPIO as GPIO
from gpiozero import LED
import dht11
import sqlite3

#for email
email = ""
password = ""
today = datetime.datetime.now()

#for db
uid = 0
name = ""
Temp_tresh = 0
Hum_tresh = 0
Lgt_int_trsh = 0
pfp = 0
theme = None

#for physical parts (GPIO)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED = 17
instance = dht11.DHT11(pin = 26)
Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 10 # Input Pin (used to be 17)
GPIO.setup(LED, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)



async def asyncTrigger():
    while True:
        f1 = loop.create_task(refreshdata())
        f2 = loop.create_task(subscriber())
        await asyncio.wait([f1, f2])


#sends email and turns on lights when the light level is under 400
def lightsOn():
   with smtplib.SMTP('outlook.office365.com', 587) as smtp:
      smtp.ehlo()
      smtp.starttls()
      smtp.ehlo()

      smtp.login(email, password)

      subject = 'LEDs'
      body = f'The LED was turned on on {today.date()} at {today.time()}'

      msg = f'subject: {subject}\n\n{body}'

      smtp.sendmail(email, email, msg)

   GPIO.output(LED, GPIO.HIGH) 


#sends an email when the temperature is over 20C/68F
def fanOn():
   with smtplib.SMTP('outlook.office365.com', 587) as smtp:
      smtp.ehlo()
      smtp.starttls()
      smtp.ehlo()

      smtp.login(email, password)

      subject = 'Fans'
      body = 'the temperature is over 20C \ndo you want to turn the fans on?'

      msg = f'subject: {subject}\n\n{body}'

      smtp.sendmail(email, email, msg)

     

#method that's always running to read emails
async def readEmail():
   #code to read emails

   #if "yes":
   GPIO.output(Motor1,GPIO.HIGH)
   GPIO.output(Motor2,GPIO.HIGH)
   GPIO.output(Motor3,GPIO.LOW) 
   pass

#saves values to the db
def database():
   conn = sqlite3.connect('iotProj.db')
   print("Opened database successfully")

   cursor = conn.execute("SELECT * from main")
   for row in cursor:
      uid = row[0]
      name = row[1]
      Temp_tresh = row[2]
      Hum_tresh = row[3]
      Lgt_int_trsh = row[4]
      pfp = row[5]
      theme = row[6]

   print("Operation done successfully")
   conn.close()

#method that's always running to subscribe to the light topic
async def subscriber():
   #if light < 400:
   #lightsOn()

   pass



#flask
app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def index():

   #default
   status = "on"
   img="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftoppng.com%2Fpublic%2Fuploads%2Fthumbnail%2Flight-bulb-on-off-png-11553940286qu70eim67f.png&f=1&nofb=1&ipt=facc53d8572229607dd5fa070712f89f3b1d1cf7fd178a7609773a621cdfb2b8&ipo=images"
  
  #turn LED on/off
   if request.method == "POST":
         if "on" in request.form.get("status") :
            GPIO.output(LED, GPIO.HIGH)
            status = "off"
            img = f"https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.clker.com%2Fcliparts%2FI%2Fs%2FH%2Fl%2Ft%2F7%2Foff-lightbulb-hi.png&f=1&nofb=1&ipt=2579432248a8ede6b5b48699a8521b2c91e9e870a3d6b344da5a60705f4d1d11&ipo=images"
         else:   
            GPIO.output(LED, GPIO.LOW)
            status = "on"
            img=f"https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftoppng.com%2Fpublic%2Fuploads%2Fthumbnail%2Flight-bulb-on-off-png-11553940286qu70eim67f.png&f=1&nofb=1&ipt=facc53d8572229607dd5fa070712f89f3b1d1cf7fd178a7609773a621cdfb2b8&ipo=images"

   #DHT11 code (temperature and humidity)
   result = instance.read()     
   
   #makes sure temperature and humidity aren't both 0 (dht just decides not to record temperature)
   #while(result.humidity == 0 and result.temperature == 0):
       #result = instance.read()
    
    

       #returns these values when the page reloads
   return render_template('index.html', value=status, imgval=img, tempval=result.temperature, humidval=result.humidity)



if __name__ == '__main__':
   app.run(debug = True)


