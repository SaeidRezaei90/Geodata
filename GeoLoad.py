import sqlite3
import urllib.request, urllib.parse, urllib.error
import ssl
import sys
import json
import time


def Geoload():
  con = sqlite3.connect('Geoload.sqlite')
  cur=con.cursor()

  cur.execute('''create table if not exists Location ('Address' Text, 'Geodata' Text) ''')

  api_key = False
  #If you have a Google Place api key insert here
  # api_key = "Your api_key"

  if api_key==False:
    api_key = '42'
    serviceurl = 'http://py4e-data.dr-chuck.net/geojson?'
  else:
    serviceurl = 'https://maps.googleapis.com/maps/api/geocode/json?'

  #Ignore ssl cert errors
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode =ssl.CERT_NONE

  fname = input('Enter your file name: ')
  if len(fname) < 1: fname ='where.data'
  try:
   fhandle = open(fname)
  except:
    #print("The entered file is not correct.")
    sys.exit('The entered file is not correct')
    
  #print(fhandle.read())
  counter = 0
  for line in fhandle:
    if counter >= 200:
      print('You retreived 200 locations, restart to retreive more.')
      break
    
    address = line.strip()
    cur.execute(''' select Address from Location where Address = ? ''',(memoryview(address.encode()), ))

    try:
      add = cur.fetchone()[0]
      print(address,' is already exist in DataBase')
      continue
    except:
      pass
    
    value = dict()
    value['address'] = address
    if api_key is not False:
      value['key'] = api_key
    
    url = serviceurl + urllib.parse.urlencode(value)
    ur = urllib.request.urlopen(url, context = ctx)
    data = ur.read().decode()
    #print(data)
    print('Retrieved', len(data), 'characters', data[:20].replace('\n', ' '))
    counter = counter + 1

    #data is a json file included altitude and longtitude coordinator
    try:
      js = json.loads(data)
    except:
      print(data)
      continue
    
    #verify if the statues is correct or not
    if 'status' not in js or (js['status']!='OK' and js['status']!='ZERO_RESULTS'):
      print('----- Failure to retreive -----')
      continue
    
    altitude=str(js["results"][0]['geometry']['location']['lat'])
    longtitude=str(js["results"][0]['geometry']['location']['lng'])
    coordinate = altitude + ', ' + longtitude

    cur.execute(''' insert into Location(Address,Geodata) values (?,?)''',(address,coordinate))

    con.commit()

    #Sleep for a while after retreveing each 10 locations
    if counter % 10 == 0:
      print("Sleep for a few seconds")
      time.sleep(4)
  

  print("Run geodump.py to read the data from the database so you can vizualize it on a map.")



  




    
