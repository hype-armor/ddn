# https://forecast.weather.gov/MapClick.php?lat=36.0812&lon=-95.9234&FcstType=digitalDWML

import urllib.request
import xml.etree.ElementTree as ET 
import re
from PIL import Image, ImageDraw, ImageFont
  
def loadRSS(url, file): 
  
    # url of rss feed 
    #url = 'https://forecast.weather.gov/MapClick.php?lat=36.0812&lon=-95.9234&FcstType=digitalDWML'
    #url = 'https://forecast.weather.gov/MapClick.php?lat=36.1747&lon=-95.9398&unit=0&lg=english&FcstType=dwml'
    # creating HTTP response object from given url 
    resp = urllib.request.urlopen(url) 
  
    # saving the xml file 
    with open(file, 'wb') as f: 
        f.write(resp.read()) 
          

def GetFontSize(text, max_width, max_height, draw):
    font = ImageFont.truetype("arial.ttf", 12)
    w, h = draw.textsize(text, font=font)
    for i in range(13,200):
        if w < max_width and h < max_height:
            font = ImageFont.truetype("arial.ttf", i)
            w, h = draw.textsize(text, font=font)
    return w, h, font

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
                if len(item.attrib) > 0:
                    for name, value in item.attrib.items():
                        if name == '{http://www.w3.org/2001/XMLSchema-instance}nil':
                            print('{0} is null'.format(name))
                            text = None
                        else:
                            print('{0}={1}'.format(name,value))
                            text[item.text] = value
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

class datec:
    date_str = None
    date = None
    periodname = None
    def __init__(self, date, periodname):
        from datetime import datetime
        self.date_str = date
        self.date = datetime.strptime(self.date_str, "%Y-%m-%dT%H:%M:%S-06:00")
        self.periodname = periodname

class timeframes:
    dates = None
    layoutkey = None
    def __init__(self):
        self.dates = []
    def adddate(self, date, periodname):
        self.dates.append(datec(date, periodname))
    def addlayoutkey(self,layoutkey):
        self.layoutkey = layoutkey.decode()


class forecast:
    date = None
    layoutkey = None
    temperature = None
    weatherconditions = None
    probabilityofprecipitation = None
    icon = None

    def __init__(self,date,layoutkey):
        self.date = date
        self.layoutkey = layoutkey
     
def main(): 
    # load rss from web to update existing xml file 
    loadRSS('https://forecast.weather.gov/MapClick.php?lat=36.1747&lon=-95.9398&unit=0&lg=english&FcstType=dwml','forecast.xml') 
    
    # parse xml file 
    fulltimes = parseXML('forecast.xml', "./data[@type='forecast']/time-layout[1]/")
    daystimes = parseXML('forecast.xml', "./data[@type='forecast']/time-layout[2]/")
    nighttimes = parseXML('forecast.xml', "./data[@type='forecast']/time-layout[3]/")

    #periodname = parseXML('forecast.xml', "./data[@type='forecast']/time-layout[1]/start-valid-time[@period-name]")

    
    
    #conditionsicon = parseXML('forecast.xml', "./data[@type='forecast']/parameters/conditions-icon[@time-layout='k-p12h-n13-1']/")
    #hazards = parseXML('forecast.xml', "./data[@type='forecast']/parameters/hazards/")

    

    # create full day class
    fulls = timeframes()
    for times in fulltimes:
        for name, value in times.items():
            if name == 'layout-key':
                fulls.addlayoutkey(value)
            else:
                fulls.adddate(name, value)

    # create day class
    days = timeframes()
    for times in daystimes:
        for name, value in times.items():
            if name == 'layout-key':
                days.addlayoutkey(value)
            else:
                days.adddate(name, value)
    # create night class
    nights = timeframes()
    for times in nighttimes:
        for name, value in times.items():
            if name == 'layout-key':
                nights.addlayoutkey(value)
            else:
                nights.adddate(name, value)

    # populate forecast data into full days.
    forecasts = []
    probabilityofprecipitation = parseXML('forecast.xml', "./data[@type='forecast']/parameters/probability-of-precipitation[@time-layout='{0}']/".format(fulls.layoutkey))
    weather = parseXML('forecast.xml', "./data[@type='forecast']/parameters/weather[@time-layout='{0}']/".format(fulls.layoutkey))
    conditionsicon = parseXML('forecast.xml', "./data[@type='forecast']/parameters/conditions-icon[@time-layout='{0}']/".format(fulls.layoutkey))
    for i in range(1,len(fulls.dates)):
        if probabilityofprecipitation[i] == None:
            chance = str(probabilityofprecipitation[i])
        else:
            chance = [*probabilityofprecipitation[i].values()][0].decode()

        temperature = 'ERROR'
        for ii in range(len(days.dates)):
            if fulls.dates[i].date_str == days.dates[ii].date_str:
                maxtemp = parseXML('forecast.xml', "./data[@type='forecast']/parameters/temperature[@time-layout='{0}']/".format(days.layoutkey))
                temperature = [*maxtemp[ii+1].values()][0].decode()

        for ii in range(len(nights.dates)):
            if fulls.dates[i].date_str == nights.dates[ii].date_str:
                mintemp = parseXML('forecast.xml', "./data[@type='forecast']/parameters/temperature[@time-layout='{0}']/".format(nights.layoutkey))
                temperature = [*mintemp[ii+1].values()][0].decode()

        fc = forecast(fulls.dates[i],fulls.layoutkey)
        fc.temperature = temperature
        fc.probabilityofprecipitation = chance
        fc.weatherconditions = [*weather[i].values()][0]
        loadRSS([*conditionsicon[i].values()][0].decode(), str(i)+'.png')
        fc.icon = str(i)+'.png'
        forecasts.append(fc)


    buildgraphics(forecasts)

def buildgraphics(forecasts):
    
    # rest of today
    #images = [Image.open(x) for x in ['top-bottom.png', 'sides.png', 'middle.png']]
    #widths, heights = zip(*(i.size for i in images))
    bgimg = Image.open('ddnweatherpanel.png')
    max_width = 400
    max_height = 600
    for i in range(len(forecasts)):
        new_im = Image.new('RGB', (max_width, max_height))
        new_im.paste(bgimg, (0,0))
        d1 = ImageDraw.Draw(new_im)

        # title
        msg = forecasts[i].date.periodname
        w, h, font = GetFontSize(msg, max_width*.9, 50, d1)
        d1.text(((max_width-w)/2,max_height*.04), msg, fill=(255, 255, 255), font=font)
        #icon
        icon = Image.open(forecasts[i].icon)
        w,h = icon.size
        factor = 3
        tn_image = icon.resize((int(w * factor), int(h * factor)))
        new_im.paste(tn_image, (70, 180))

        # temp
        msg = forecasts[i].temperature + '°'
        w, h, font = GetFontSize(msg, max_width, 60, d1)
        #w, h = d1.textsize(msg, font=font2)
        d1.text((((max_width-w)/2)*0.1,max_height*.87), msg, fill=(255, 255, 255), font=font)

        # condition and chance
        msg = str(forecasts[i].weatherconditions)
        if msg == 'None':
            msg = 'Clear'
        else:
            msg + 'chance?'
        msg = msg.replace(' then ', '\n')
        w, h, font = GetFontSize(msg, max_width*.95, 50, d1)
        d1.text(((max_width-w)/2,max_height*.79), msg, fill=(255, 255, 255), font=font)
        new_im.save(str(i)+'_fc.png')
        new_im.close()
    
    # tomorrow

if __name__ == "__main__": 
  
    # calling main function 
    main()
