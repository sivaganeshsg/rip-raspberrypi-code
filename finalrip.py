import time
import picamera
import json
import httplib
import urllib2
import compare_images as cm
import traceback
import RPi.GPIO as GPIO
from threading import Thread	
	
FILE_NAME="rip-image"

#Parse API urls are removed

APPLICATION_ID=""
REST_API_KEY=""

twitterId=""
photoUrl=""
encodedUrl=""

restart_trial=0
counter=0
mod=9

camera=None
prev_pic=None
enableCamera=True
timeout=5

def setPhotoUrl(purl):
	photoUrl=purl

def getPhotoUrl():
	return photoUrl


def getTwitterId():
	twitterId

def setEnableCamera(ec):
	print "Enabling/Disabling Camera forcefully... : " 
	enableCamera=ec

def sendImageToServer(filename):
	print "Sending the image to server ====> " + filename
	connection=None
	
	try:
		connection=httplib.HTTPSConnection('api.parse.com', 443)
		connection.connect()
		connection.request('POST', '/1/files/pic.jpg', open(filename, 'rb').read(), {
				"X-Parse-Application-Id": "I6BRmv3FgckULOOTK8hBqIOO1kUchoPfF34Gp88B",
				"X-Parse-REST-API-Key": "Jtvf6devu9LuSSFwwJ63SzxeMIUniqvXMSHVKZNc",
				"Content-Type": "image/jpeg"
			})
		
		rslt=json.loads(connection.getresponse().read())
		photoName=rslt['name']
		purl=rslt['url']
		print photoName
		print purl

		setPhotoUrl(purl)

		connection.request('POST', '/1/classes/Photos', json.dumps({
					"photosUploaded" : {
						"name" : photoName,
						"__type" : "File"
					}
				}), {
				"X-Parse-Application-Id": APPLICATION_ID,
				"X-Parse-REST-API-Key": REST_API_KEY,
				"Content-Type": "application/json"
			})
		connection.getresponse().read()
		
		notifyTwitter()
		
		
	finally:
		if(connection is not None):
			connection.close()



def isNone(var):
	return var is None
	
def setTimeout(to):
	timeout=to
	
def setTwitterId(twitId):
	twitterId=twitId	
	
def enableCamera():
	return enableCamera 
	
def initializeCamera():
	camera=picamera.PiCamera()
	camera.resolution = (1024, 768)
	return camera;

def getTimeout(): 
	return timeout

def getPhotoUrl():
	return photoUrl

def getTwitterId():
	return twitterId
	
	
def notifyTwitter():
	print "Notifying Twitter..."
	photoUrl = getPhotoUrl()
	twitterId = getTwitterId()
	encodedUrl=urllib2.quote(photoUrl.encode("utf8"))
	
	print "encoded Url : " + encodedUrl;

	connection=httplib.HTTPConnection("52.74.183.108", 80)
	connection.connect()
	connection.request("GET", '/send_sms', json.dumps({
			"parse_image_url" : encodedUrl,
			"twitter_id" : "gokulepiphany"
		}), {
			"Content-Type": "application/json"
		})
	connection.getresponse().read()


def tf2(arg):
	print "TF2 starting..."
	GPIO.setmode(GPIO.BOARD)
	PIR_PIN = 7
	GPIO.setup(PIR_PIN,GPIO.IN)
	try:
		print "PIR Module Test(ctrl+c to exit)"
		time.sleep(2)
		print "Ready"
		while True:
			print "I am waiting.."
			if GPIO.input(PIR_PIN):
				print "Motion Detected"
				notifyTwitter()
				#setEnableCamera(True)
				time.sleep(4)
			time.sleep(1)
	except KeyboardInterrupt:
		print "Quit"
		GPIO.cleanup()
		
		
print "Starting motion detetion in separate thread..."		
		
t2 = Thread(target = tf2,args = (10, ))
t2.start()


print "Proceeding with camera survailence ..."

#initing the camera
camera=initializeCamera()

#Continuosly taking photos	
while True:
	if(enableCamera()):
		try:
			camera.start_preview()
			time.sleep(2)
			counter+=1
			fname=FILE_NAME+"%d.jpg" % (counter%mod);
			camera.capture(fname)
			camera.stop_preview()

			#verify whether something has changed in the environment
			if(isNone(prev_pic)):
				#Sending the image to the parse server
				sendImageToServer(fname)
				prev_pic=fname	
			
			elif(not cm.compare(prev_pic, fname)):
				#Sending the image to the parse server
				sendImageToServer(fname)
				prev_pic=fname	
				
			else:
				print"not sending the file to the server, since no change in the environment : " + fname
		except:
			print "Exception occurred while running the camera, restarting the camera :%d" %restart_trial
			print(traceback.format_exc())
			restart_trial+=1
			if(restart_trial > 2):
				break
			else:
				camera.close()
				camera=initializeCamera()

	time.sleep(getTimeout())
