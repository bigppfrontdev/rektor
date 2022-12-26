from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import requests
import xmltodict
import math
from urllib.request import urlopen
import urllib.error
import json
import datetime;
import simplejson as json


app = Flask(__name__)
CORS(app)



offendingDrones = {}



@app.route("/", methods=['GET', 'POST'])
def main():
    offenderCheck()
    timecheck()
    return render_template("web.html", data=json.dumps(offendingDrones))



def offenderCheck():
    
    xml = getxml("https://assignments.reaktor.com/birdnest/drones")
    report = xml["report"]
    timestamp = report["capture"]["@snapshotTimestamp"]
    drones = report["capture"]["drone"]

    for i in range(len(drones)):
        droneSerialNum = drones[i]["serialNumber"]
        droneXpos = float(drones[i]["positionX"])
        droneYpos = float(drones[i]["positionY"])

        distance = math.sqrt((droneXpos-250000)**2 + (droneYpos-250000)**2)

        if distance < 100000:
            if droneSerialNum in offendingDrones:
    
                if distance < offendingDrones[droneSerialNum]["closestDistance"]:
                    setPilotInfoIntoDict(droneSerialNum, distance, timestamp)     
                else:
                    setPilotInfoIntoDict(droneSerialNum, offendingDrones[droneSerialNum]["closestDistance"], timestamp)

            else:   
                setPilotInfoIntoDict(droneSerialNum, distance, timestamp)


    

def timecheck():

    
    current = datetime.datetime.now()
    
    for i in offendingDrones.keys():
        times = offendingDrones[i]["time"].split(":")
        minute = int(times[1])
        minutediff = current.minute - minute

        if minutediff >= 10 or (minutediff >= -50 and minutediff < 0):
            offendingDrones.pop(0)
        else:
            break

    

def setPilotInfoIntoDict(serial, distance, time):
    
    pilot = getJson("https://assignments.reaktor.com/birdnest/pilots/"+serial)    
    pilotFullName = pilot["firstName"] + " " + pilot["lastName"]
    allinfo = {"name": pilotFullName, "email": pilot["email"], "number": pilot["phoneNumber"] ,
        "closestDistance": distance, "time": time}
        
    offendingDrones[serial] = allinfo
    



def getxml(url):

    response = requests.get(url)
    data = xmltodict.parse(response.content)

    return data


def getJson(url):

    try:
        response = urlopen(url)
    except urllib.error.HTTPError as e:
        print(e)
              
    data_json = json.loads(response.read())

    return data_json


if __name__ == "__main__":
  app.run(host="127.0.0.1")