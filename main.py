from flask import Flask, request, render_template, current_app
import RPi.GPIO as GPIO
from gpiozero import LED
import dht11


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
data = {}

app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def index():
    
    #LED code
   status = "on"
   img="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftoppng.com%2Fpublic%2Fuploads%2Fthumbnail%2Flight-bulb-on-off-png-11553940286qu70eim67f.png&f=1&nofb=1&ipt=facc53d8572229607dd5fa070712f89f3b1d1cf7fd178a7609773a621cdfb2b8&ipo=images"
   if request.method == "POST":
         if "on" in request.form.get("status") :
            GPIO.output(LED, GPIO.HIGH) # turn on led code
            status = "off"
            img = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.clker.com%2Fcliparts%2FI%2Fs%2FH%2Fl%2Ft%2F7%2Foff-lightbulb-hi.png&f=1&nofb=1&ipt=2579432248a8ede6b5b48699a8521b2c91e9e870a3d6b344da5a60705f4d1d11&ipo=images"
         else:   
            GPIO.output(LED, GPIO.LOW) # turn off led code
            status = "on"
            img="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftoppng.com%2Fpublic%2Fuploads%2Fthumbnail%2Flight-bulb-on-off-png-11553940286qu70eim67f.png&f=1&nofb=1&ipt=facc53d8572229607dd5fa070712f89f3b1d1cf7fd178a7609773a621cdfb2b8&ipo=images"
   
         data['fans'] = request.json['fans']
               
        
   #DHT11 code (temperature and humidity)
   result = instance.read()
    
   while(result.humidity == 0 and result.temperature == 0):
       result = instance.read()
      
   if len(data) > 0:
       if "on" in data["fans"]:
           GPIO.output(Motor1,GPIO.HIGH)
           GPIO.output(Motor2,GPIO.HIGH)
           GPIO.output(Motor3,GPIO.LOW)
       
   #data to be sent on to the main page
   return render_template('index.html', value=status, imgval=img, tempval=result.temperature, humidval=result.humidity)
   

if __name__ == '__main__':
   app.run(debug = True)