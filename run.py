# https://forecast.weather.gov/MapClick.php?lat=36.0812&lon=-95.9234&FcstType=digitalDWML

import urllib.request
import xml.etree.ElementTree as ET 
  
def loadRSS(): 
  
    # url of rss feed 
    url = 'https://forecast.weather.gov/MapClick.php?lat=36.0812&lon=-95.9234&FcstType=digitalDWML'
  
    # creating HTTP response object from given url 
    resp = urllib.request.urlopen(url) 
  
    # saving the xml file 
    with open('forecast.xml', 'wb') as f: 
        f.write(resp.read()) 
          
  
def parseXML(xmlfile, xpath): 
  
    # create element tree object 
    tree = ET.parse(xmlfile) 
  
    # get root element 
    root = tree.getroot() 
  
    # create empty list for news items 
    timelayouts = [] 
  
    # iterate news items 
    for item in root.findall(xpath): 
  
        # empty news dictionary 
        text = {}
        # iterate child elements of item 
        
        if item.text != None and item.text.isspace() != True:
            if len(item) > 0:
                for child in item:
                    text[child.tag] = child.text.encode('utf8')
            else:
                text[item.tag] = item.text.encode('utf8')

        elif len(item.attrib) > 0:
            
            for name, value in item.attrib.items():
                if name == '{http://www.w3.org/2001/XMLSchema-instance}nil':
                    print('{0} is null'.format(name))
                    text = None
                else:
                    print('{0}={1}'.format(name,value))
                    text[name] = value
        else:
            for kid in item.getchildren():
                for name, value in kid.items():
                    if 'additive' not in text:
                        text[name] = value
                    else:
                        text[name] += ' ' + text['additive'] + ' ' + value

        timelayouts.append(text)
        
    # return news items list
    return timelayouts
  
class forecast:
    date = None
    dewpoint = None
    windchill = None
    temperature = None
    windspeed = None
    winddirection = None
    weatherconditions = None

    def __init__(self,date,dewpoint,windchill,temperature,windspeed,winddirection,weatherconditions):
        self.date = date
        self.dewpoint = dewpoint
        self.windchill = windchill
        self.temperature = temperature
        self.windspeed = windspeed
        self.winddirection = winddirection
        self.weatherconditions = weatherconditions
     
def main(): 
    # load rss from web to update existing xml file 
    #loadRSS() 
  
    # parse xml file 
    times = parseXML('forecast.xml', './data/time-layout/')
    dewpoint = parseXML('forecast.xml', "./data/parameters/temperature[@type='dew point']/")
    windchill = parseXML('forecast.xml', "./data/parameters/temperature[@type='wind chill']/")
    temperature = parseXML('forecast.xml', "./data/parameters/temperature[@type='hourly']/")
    windspeedsustained = parseXML('forecast.xml', "./data/parameters/wind-speed[@type='sustained']/")
    windspeedgust = parseXML('forecast.xml', "./data/parameters/wind-speed[@type='gust']/")
    winddirection = parseXML('forecast.xml', './data/parameters/direction/')
    weatherconditions = parseXML('forecast.xml', './data/parameters/weather/')

    from datetime import datetime
    times.remove(times[0])
    
    forecasts = []

    count = 0
    for time in times:
        if 'start-valid-time' in time:
            date_str = str(time['start-valid-time'])
            date = datetime.strptime(date_str, "b'%Y-%m-%dT%H:%M:%S-06:00'")
            forecasts.append(forecast(date, dewpoint[count],windchill[count],temperature[count],windspeedsustained[count],winddirection[count],weatherconditions[count]))
            count+=1

    print()
    
      
if __name__ == "__main__": 
  
    # calling main function 
    main()
    