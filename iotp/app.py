from dash import Dash, dcc, html, Input, Output, DiskcacheManager, CeleryManager
import RPi.GPIO as GPIO
from gpiozero import LED
import dht11
import sqlite3
from paho.mqtt import client as mqtt_client
import paho.mqtt.client as mqttClient
import time
import bluetooth
import imaplib
import smtplib
import email
from email.header import decode_header
import webbrowser
import os
import datetime

app = Dash(__name__)

#for email
username = "IotDUmmy2022@outlook.com"
password = "IotProject"
today = datetime.datetime.now()

temp = ""
humid = ""
tempSent = False
times = 0

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

app.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href='/assets/typography.css'
    ),
    dcc.Interval(
            id='interval-component',
            interval=1 * 1000,
            n_intervals=0
    ),

    html.Div(
        id="user",
        children=[
            html.Img(src="https://th.bing.com/th/id/R.bae2d37c4317140a408aef6671346186?rik=X1vYbxH6nQxCcA&riu=http%3a%2f%2fcdn.onlinewebfonts.com%2fsvg%2fimg_218090.png&ehk=poXsiWmpbb3%2b%2bK%2blj8H9AQprCYsoz4kt%2bU4rFFKbOCo%3d&risl=&pid=ImgRaw&r=0", id="userpfp"),
            html.P('Username', id="username"),
            html.P('Favorites', className="favs"),
            html.Ul(
                    id="userfavs",
                    children=[
                        html.Li('Temperature: '),
                        html.Li('Humidity:'),
                        html.Li('Light Intensity:')
                    ]
                )
        
        ]
    ),

    html.Div(
        id="temp",
        children=[
            html.H2('temp'),
            html.Div( 
                id="gauges",
                children=[
                    html.Span('Temperature  |  Moisture'),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Meter( id="tempg"),
                    html.Meter( id="moistg"),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.P(id='vals',
                           children=["        num              |       num"]),
                    html.Div(
                        id="fans",
                        children=[
                        html.Div(
                            className="pic",
                            id="fanpic",
                            children=[
                                html.Img(id="fanstat",src="https://static.thenounproject.com/png/1703696-200.png")
                            ]
                            )
                            
                        ]
                        )
                ]
                )
        ]

        ),
    html.Div(
        id="light",
        children=html.Div([
            html.H2('LED'),
            html.Div(
                className="pic",
                id="LED",
                children=[
                    html.Button(
                        id="toggleBtn",
                        n_clicks=0,
                        children=[
                            html.Img(
                                id="ledtoggle",
                                src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.clker.com%2Fcliparts%2FI%2Fs%2FH%2Fl%2Ft%2F7%2Foff-lightbulb-hi.png&f=1&nofb=1&ipt=2579432248a8ede6b5b48699a8521b2c91e9e870a3d6b344da5a60705f4d1d11&ipo=images"
                                )
                        ])
                ]
                )
        ])
    ),
    html.Div(
        id="bluetoothCon",
        children=[
            html.H1("Bluetooth"),
            html.Div(
        id="bloo",
            children=[
                html.Button(
                    id="bluebutton",
                    n_clicks=0,
                    children=[
                        html.Img(src="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fwww.inktechnologies.com%2Fblog%2Fwp-content%2Fuploads%2F2011%2F07%2FBluetooth-Logo-150x150.png&f=1&nofb=1&ipt=a338e8e9f8d220c6990f171c62915f52da073bf9be31e854fb42dd8bfb6ab88e&ipo=images")
                        ]
                )
            ]
        )           
            ]
        ),
    html.Img(id="plz")
])


        
import diskcache
cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

# EMAILS------------------------------------------------------

imap_server = "outlook.office365.com"

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def readMail():
    # create an IMAP4 class with SSL 
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
                            elif ("the temperature is over 20C" in body):
                                tempSent = True     
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
                        elif ("the temperature is over 20C" in body):
                            tempSent = True
    # close the connection and logout
    imap.close()
    imap.logout()
# email actions ------------------------------
@app.callback(
    Output('fanstat', 'src'),
    Input(' ', ' ')
)
def fananim():
    return "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmedia2.giphy.com%2Fmedia%2Fl4vtUphl0Ui9VywVGT%2Fsource.gif&f=1&nofb=1&ipt=4de825703b5e2fc381082a5387088a67c8edde82ae143c04ffdd0b63dd446497&ipo=images"
  
def fanOn():
    conn = sqlite3.connect('../db/iotProj.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Users VALUES ('Raju', '7th', 'A')''')
    conn.commit()
    conn.close()
    
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

   GPIO.output(LED, GPIO.HIGH)    

def fanMail():
   with smtplib.SMTP('outlook.office365.com', 587) as smtp:
      smtp.ehlo()
      smtp.starttls()
      smtp.ehlo()

      smtp.login(username, password)

      subject = 'Fans'
      body = 'the temperature is over 20C \ndo you want to turn the fans on?'

      msg = f'subject: {subject}\n\n{body}'

      smtp.sendmail(username, username, msg)

#update the page ----------------------------------------------

@app.callback(
    Output('ledtoggle', 'src'),
    Input('toggleBtn', 'n_clicks')
)
def update_LED(n_clicks):
    if(n_clicks % 2):
        GPIO.output(LED, GPIO.HIGH)
        return "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.clker.com%2Fcliparts%2FI%2Fs%2FH%2Fl%2Ft%2F7%2Foff-lightbulb-hi.png&f=1&nofb=1&ipt=2579432248a8ede6b5b48699a8521b2c91e9e870a3d6b344da5a60705f4d1d11&ipo=images"    
    else:
        GPIO.output(LED, GPIO.LOW)
        return "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftoppng.com%2Fpublic%2Fuploads%2Fthumbnail%2Flight-bulb-on-off-png-11553940286qu70eim67f.png&f=1&nofb=1&ipt=facc53d8572229607dd5fa070712f89f3b1d1cf7fd178a7609773a621cdfb2b8&ipo=images"
    
@app.callback(
    Output('bloo', 'children'),
    Input('bluebutton', 'n_clicks'),
)
def update_Blue(n_clicks):
    devices = bluetooth.discover_devices(lookup_names = True, lookup_class = True)

    number_of_devices = len(devices)
    return f"{number_of_devices} bluetooth devices found" 



@app.callback(
    Output('tempg', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_Temp(n_clicks):
    result = instance.read()     
   
    #makes sure temperature and humidity aren't both 0 (dht just decides not to record temperature)
    while(result.temperature == 0):
        result = instance.read()
        
    temp = result.temperature
    
    
    
    if(result.temperature > 20 and tempSent == False):
        fanMail()
    readMail()
    return f"{result.temperature / 100}"

@app.callback(
    Output('moistg', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_Hum(n_clicks):
    result = instance.read()
    
    while(result.humidity == 0):
        result = instance.read()
    
    humid = result.humidity
        
    result = instance.read()
    return f"{result.humidity/ 100}"



@app.callback(
    Output('vals', 'children'),
    Input('interval-component', 'n_intervals')
)
def updateVals(n_clicks):
    result = instance.read()
    
    while(result.humidity == 0 and result.temperature == 0):
        result = instance.read()
    
    return f"{result.temperature}°C     |      {result.humidity}%"


#MQTT --------------------------------------------------------

def on_connect(client, userdata, flags, rc):
  
    if rc == 0:
  
        print("Connected to broker")
        client.on_message= on_message 
  
        global Connected                #Use global variable
        Connected = True                #Signal connection 
  
    else:
  
        print("Connection failed")
        
def on_message(client, userdata, message):
    output = message.payload.decode()
    print(f"Message received: {output}")
    if(message.topic == "IoTlab/ESP"): #photoresistor
        if(int(output) >= 400):
            lightsOn()  
    elif(message.topic == "/esp8266/data"): #rfid
        pass #insert in db code
        #if new to db add and sign in
        #else sign in
  
Connected = False   #global variable for the state of the connection
  
broker_address= "192.168.0.148"  #Broker address
port = 1883                        #Broker port
  
client = mqttClient.Client("Python")               #create new instance
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback
  
client.connect(broker_address, port=port)          #connect to broker
  
client.loop_start()        #start the loop
  
while Connected != True:    #Wait for connection
    time.sleep(0.1)
  
client.subscribe("IoTlab/ESP")
client.subscribe("/esp8266/data")





   
 

if __name__ == '__main__':
    app.run_server(debug=True)


 
