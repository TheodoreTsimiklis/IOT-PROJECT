from flask import Flask, request, render_template
import RPi.GPIO as GPIO
from gpiozero import LED

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED = 17
GPIO.setup(LED, GPIO.OUT, initial=GPIO.LOW)

app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def index():
   if request.method == "POST":
         if "on" in request.form.get("status") :
            GPIO.output(LED, GPIO.HIGH) # turn on led code
         else:   
            GPIO.output(LED, GPIO.LOW) # turn off led code
       
   return render_template('index.html')

if __name__ == '__main__':
   app.run(debug = True)