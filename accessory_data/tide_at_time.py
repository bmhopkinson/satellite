import math
import os
import re
import json
import pandas as pd


tide_data_file = 'tide_data_station_8675761_year_2021.csv'
#test_meta = '20210104_154923_0f4e_metadata.json'
#folder = '../data/Sapelo_2021/Sapelo_20210104_psscene4band_analytic_sr_udm2/files/'
base_folder = '../data/Sapelo_2021/'
data_subdir ='files'

dot_firstchar = re.compile(r'^\.')  #used to ignore hidden files

def load_tide_data(filename):
    tide_df = pd.read_csv(filename, names=['time', 'tide'])
    tide_df['time'] = pd.to_datetime(tide_df['time'])

    return tide_df

def find_metadata_time(json_filename):
    with open(json_filename, 'r') as f:
        data = json.load(f)

    time = data['properties']['acquired']
    return time


def find_nearest_time(target_time, time_data):
    #binary search, assumes time_data is monotonically increasing

    if target_time < time_data.iloc[0]:
        return time_data[0]
    if target_time > time_data.iloc[-1]:
        return time_data[-1]

    imin = 0
    imax = len(time_data)

    while imin <= imax:
        imid = math.floor((imin+imax)/2)

        if target_time < time_data.iloc[imid]:
            imax = imid - 1
        elif target_time > time_data.iloc[imid]:
            imin = imid + 1
        else:  #equal - this will never happen with non integers
            return [imid, time_data.iloc[imid]]

    # imin will be imax+1
    e_imin = abs(target_time - time_data.iloc[imin])
    e_imax = abs(target_time - time_data.iloc[imax])

    if e_imin < e_imax:
        return [imin, time_data.iloc[imin]]
    else:
        return [imax, time_data.iloc[imax]]


def load_and_match_planet_metadata(base_folder, data_subdir, tide_data):
    tides_to_satellite = []
    for entity in os.listdir(base_folder):
        if os.path.isdir(os.path.join(base_folder, entity)):
            dirpath = os.path.join(base_folder, entity, data_subdir)

            for file in os.listdir(dirpath):
                root, ext = os.path.splitext(file)
                if ext == '.json' and not dot_firstchar.search(file):
                    acquisition_time = find_metadata_time(os.path.join(dirpath, file))
                    acquisition_time = pd.to_datetime(acquisition_time)
                    idx, time = find_nearest_time(acquisition_time, tide_data['time'])
                    tide = tide_data['tide'].iloc[idx]

                    tides_to_satellite.append({'file': file,
                                               'acquisition_time': acquisition_time,
                                               'tide_time': time,
                                               'tide': tide
                                               })

    return tides_to_satellite


def write_matched_data(data, outfile):
    with open(outfile, 'w') as fout:
        for entry in data:
            line = '{}\t{}\t{}\t{}\n'.format(entry['file'], entry['acquisition_time'], entry['tide_time'], entry['tide'])
            fout.write(line)


if __name__ == "__main__":

    tide_data = load_tide_data(tide_data_file)
    tides_to_satellite = load_and_match_planet_metadata(base_folder, data_subdir, tide_data)

    sort_key = lambda x : pd.to_datetime(x['acquisition_time'])  #seemed to work without conversion to python's built in datetime but safer to do so
    tides_to_satellite.sort(key=sort_key)

    write_matched_data(tides_to_satellite,'tide_at_time_data.txt')

    print('hello')