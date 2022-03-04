import csv
import datetime as dt

infile = 'tide_data_station_8675761_year_2014.csv'

tide_data = []
with open(infile,'r') as csvfile:
    csv_in = csv.reader(csvfile)
    for row in csv_in:
        rfc3339string = row[0]
        dt_cur = dt.datetime.strptime(rfc3339string, '%Y-%m-%dT%H:%M:%S.%fZ')
        tide_data.append([dt_cur, float(row[1])])

print('hello')

