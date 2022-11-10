import imaplib
import smtplib
import email
from email.header import decode_header
import webbrowser
import os
import datetime
from flask import Flask, request, render_template
import RPi.GPIO as GPIO
from gpiozero import LED
import dht11
import sqlite3
from paho.mqtt import client as mqtt_client

#for email
username = "iotDummy2022@outlook.com"
password = "IotProject"
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


global current_light_intensity
currentLightIntensity = "NaN"
global lightIntensity

#sends email and turns on lights when the light level is under 400
def lightsOn():
   with smtplib.SMTP('outlook.office365.com', 587) as smtp:
      smtp.ehlo()
      smtp.starttls()
      smtp.ehlo()

      smtp.login(username, password)

      subject = 'LEDs'
      body = f'The LED was turned on on {today.date()} at {today.time()}'

      msg = f'subject: {subject}\n\n{body}'

      smtp.sendmail(username, username, msg)

#mqtt
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        lightmsg = ""
        lightIntensity = 0
        lightmsg = int(msg.payload.decode())
        currentLightIntensity = lightmsg
        if(int(msg.payload.decode()) <= 400):
            lightsOn()
            GPIO.output(ledPin, GPIO.HIGH)
            
        else:
            GPIO.output(ledPin, GPIO.LOW)
            
            #emailSent = False
            
            
        global current_light_intensity
        current_light_intensity = msg.payload.decode()
        
            
        
    client.subscribe(topic)
    client.on_message = on_message
    return currentLightIntensity


#sends an email when the temperature is over 20C/68F
def fanOn():
   with smtplib.SMTP('outlook.office365.com', 587) as smtp:
      smtp.ehlo()
      smtp.starttls()
      smtp.ehlo()

      smtp.login(username, password)

      subject = 'Fans'
      body = 'the temperature is over 20C \ndo you want to turn the fans on?'

      msg = f'subject: {subject}\n\n{body}'

      smtp.sendmail(username, username, msg)

     

#method that's always running to read emails
def readEmail():
   imap = imaplib.IMAP4_SSL(imap_server)
# authenticate
   imap.login(username, password)

   status, messages = imap.select("INBOX")
   # number of top emails to fetch
   N = 1
   # total number of emails
   messages = int(messages[0])    

   for i in range(messages, messages-N, -1):
       # fetch the email message by ID
       res, msg = imap.fetch(str(i), "(RFC822)")
       for response in msg:
           if isinstance(response, tuple):
               # parse a bytes email into a message object
               msg = email.message_from_bytes(response[1])
               # decode the email subject
               subject, encoding = decode_header(msg["Subject"])[0]
               if isinstance(subject, bytes):
                   # if it's a bytes, decode to str
                   subject = subject.decode(encoding)
               # decode email sender
               From, encoding = decode_header(msg.get("From"))[0]
               if isinstance(From, bytes):
                   From = From.decode(encoding)
               # if the email message is multipart
               if msg.is_multipart():
                   # iterate over email parts
                   for part in msg.walk():
                       # extract content type of email
                       content_type = part.get_content_type()
                       content_disposition = str(part.get("Content-Disposition"))
                       try:
                           # get the email body
                           body = part.get_payload(decode=True).decode()
                       except:
                           pass
                       if content_type == "text/plain" and "attachment" not in content_disposition:
                           # print text/plain emails and skip attachments
                           print(body)
                           if("yes" in body):
                               print("balls2")
                               GPIO.output(Motor1,GPIO.HIGH)
                               GPIO.output(Motor2,GPIO.HIGH)
                               GPIO.output(Motor3,GPIO.LOW) 
               else:
                   # extract content type of email
                   content_type = msg.get_content_type()
                   # get the email body
                   body = msg.get_payload(decode=True).decode()
                   if content_type == "text/plain":
                       # print only text email parts
                       print(body)
                       if("yes" in body):
                           print("balls")
                           GPIO.output(Motor1,GPIO.HIGH)
                           GPIO.output(Motor2,GPIO.HIGH)
                           GPIO.output(Motor3,GPIO.LOW) 
   # close the connection and logout
   imap.close()
   imap.logout()

   #if "yes":
   
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

@app.callback(Output('light-intensity-value', 'value'),
              Input('interval-component', 'n_intervals'))
def update_light_intensity(n):
    return 'The current light intensity is:' + str(current_light_intensity) 


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
   while(result.humidity == 0 and result.temperature == 0):
       result = instance.read()

   if(result.temperature > 20):
       fanOn()



       #returns these values when the page reloads
   return render_template('index.html', value=status, imgval=img, tempval=result.temperature, humidval=result.humidity)

if __name__ == '__main__':
   app.run(debug = True)

def main():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()

while True:
   readEmail()