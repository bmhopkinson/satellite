import urllib.request
import xml.etree.ElementTree as ET
from calendar import monthrange

station_id = '8675761'
year = 2021

def fetch_NOAA_tide_data(begin_date, begin_time, end_date, end_time, station_id):
    #max data that can be requested for 6 min tide data is 31 days
    #fetch xml data from NOAA - csv would probably be fine for this data, but use xml to keep more generally applicable
    url_template = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?' \
                   'begin_date={}%20{}&end_date={}%20{}&station={}' \
                   '&product=predictions&datum=mllw&units=metric&time_zone=gmt&application=web_services&format=xml'
    url = url_template.format(begin_date, begin_time, end_date, end_time, station_id)
    response = urllib.request.urlopen(url)
    data = response.read()

    #extract relavent info
    text = data.decode('utf-8')
    xmltree = ET.ElementTree(ET.fromstring(text))
    root = xmltree.getroot()
    preds = root.findall('pr')

    results = []
    for pred in preds:
        time = pred.attrib['t']
        height = pred.attrib['v']
        results.append([time, height])

    return results

def write_tide_data(filehandle, data):
    for datum in data:
        date, time = datum[0].split()
        datetime_rfc3339 = date + 'T' + time + ':00.00Z' #format to rfc 3339 including appending seconds and Z = GMT
        outstring = datetime_rfc3339 + ',' + datum[1] + '\n'
        filehandle.write(outstring)


outfile_name = 'tide_data_station_{}_year_{}.csv'.format(station_id, year)
outfile = open(outfile_name, 'w')
for month in range(1, 13):
    begin_date = str(year) + '{:02d}01'.format(month)
    begin_time = '00:00'

    days_in_month = monthrange(year, month)[1]
    end_date = str(year) + '{:02d}{:02d}'.format(month, days_in_month)
    end_time = '11:54'

    res = fetch_NOAA_tide_data(begin_date, begin_time, end_date, end_time, station_id)
    write_tide_data(outfile, res)

outfile.close()

print('hello')