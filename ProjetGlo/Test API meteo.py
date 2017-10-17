import zeep
from lxml import etree
import xmltodict
import requests
import os
import googlemaps
import datetime
from CYA_meteo import Meteo

url = "http://www.infoclimat.fr/public-api/gfs/json?_ll=48.85341,2.3488&_auth=UUsAFwd5UnBWewM0VCJXfgdvAzYJfwQjBHhSMVo%2FAn8DaFAxBGQDZQVrA34EK1FnV3pQMwswCDgDaFIqWigDYlE7AGwHbFI1VjkDZlR7V3wHKQNiCSkEIwRmUjZaPwJ%2FA2FQPQRiA38FaANhBDFRe1dmUDULMQgvA39SNFoyA2BRNQBmB2RSOVY6A2NUZFd8BysDZgk%2FBGgEYVI2WjcCZwNoUDQEYANgBWMDMwQzUXtXY1A0CzAINwNmUjNaNgNoUS0AewcdUkNWJAMhVCZXNgdyA34JYwRiBDM%3D&_c=272acb338257c36795529d891a5b0a9d"
try:
    resp = requests.get(url)
except:
    print(" La connexion à l'API n'est pas disponible. Veuillez contrôler votre acces réseau")

doc = resp.json()
print("Doc de base" ,doc)
#Possibilité d'avoir le module erreur si jamais il y a une erreur de connexion

if type(doc['request_state'])==str:
    print('yolo')
else:
    os.system("pause")

testdate = datetime.datetime.now()

print(testdate)
for i in doc.keys():
    if type(doc[i]) == dict:
        datedict = datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
        diff = ((testdate - datedict).total_seconds()/60)
        if abs(diff) > 120:
            continue
        else:
            print(diff)
            print(i)
            tempK = round(float(doc[i]['temperature']['2m']),3)
            tempC = round(tempK - 273.15,2)
            print("Il fait {0} °C à Paris aujourd'hui".format(tempC))

test = Meteo()
temp = test.get_pluie('2017-10-17 14:20:00')
print('temp')