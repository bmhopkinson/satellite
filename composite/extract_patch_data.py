import os
import rasterio
import numpy as np


base_folder = './data/composites/'

class PatchExtractor():
    def __init__(self):
        self.patches = []  # list of patches each of which is defined by lat_pos, lon_pos, lat_patch_radius (pixels), lon_patch_radius (pixels)

    def set_patches(self, patches):  #user defined patches
        self.patches = patches

    def define_patch_grid(self, lat_bounds, lon_bounds, lat_spacing, lon_spacing, lat_patch_radius, lon_patch_radius):
        #generate patch grid using input parameters

        patches = []
        for lat_pos in range(lat_bounds[0] + lat_spacing, lat_bounds[1] - lat_spacing, lat_spacing):
            for lon_pos in range(lon_bounds[0] + lon_spacing, lon_bounds[1] - lon_spacing, lon_spacing):
                patches.append( [lat_pos, lon_pos, lat_patch_radius, lon_patch_radius] )

        self.patches = patches

    def extract_patch_avgs(self, img, src):
        # determines average values within a channel for each patch from image data in img (a numpy array), and
        # a rasterio source (src) that can transform from lat, lon to pixel location
        results = {}
        for patch in self.patches:
            lat_pos, lon_pos = patch[0:2]
            dx, dy = patch[2:]

            key = (lat_pos, lon_pos)
            py, px = src.index(lon_pos, lat_pos)

            patch_cur = img[py - dy:py + dy, px - dx:px + dx]
            patch_avg = np.average(patch_cur, axis=(0, 1))
            patch_avg[patch_avg < 1E-10] = np.nan

            results[key] = patch_avg

        return results


# patches = [  #patch centers in EPSG:32167: lat, lon; followed by patch radius lat, lon, in pixels
#             [481116, 3487026, 5, 5],   # forest
#             [470766, 3475026, 5, 5],   # water
#             [469416, 3472026, 5, 5],   # marsh 1
#             [473016, 3482526, 5, 5],   # marsh 2
#             [467016, 3478026, 5, 5],   # marsh 3
#           ]

lat_bounds = [3464775, 3490026]  # EPSG:32167 coordinates, meters
lon_bounds = [459516, 483600]  # EPSG:32167 coordinates, meters
lat_patch_radius = 2  # pixels NOT meters
lon_patch_radius = 2  # pixels NOT meters
lat_spacing = 30  # meters
lon_spacing = 30  # meters

patch_extractor = PatchExtractor()
patch_extractor.define_patch_grid(lat_bounds, lon_bounds, lat_spacing, lon_spacing, lat_patch_radius, lon_patch_radius)

composite_id = []
patch_avg_ts = {}
for file in os.listdir(base_folder):
    if os.path.splitext(file)[1] == '.tif':
        full_path = os.path.join(base_folder, file)
        with rasterio.open(full_path) as src:
            b, g, r, nir = (src.read(k) for k in (1, 2, 3, 4))
            print('read in geotiff')

            img = np.stack((b, g, r, nir), axis=2)
            img = np.divide(img.astype(np.float32), 10000)  # convert to reflectance

           # patch_data = []
            composite_id.append(file)
            patch_avgs = patch_extractor.extract_patch_avgs(img, src)

            for key in patch_avgs:
                if key in patch_avg_ts:
                    patch_avg_ts[key] = np.append(patch_avg_ts[key], patch_avgs[key])
                else: #setup datastructure
                    patch_avg_ts[key] = patch_avgs[key]


outfile_basename = './patch_avgs_{}.txt'

with open('patch_average_ts.txt', 'w') as f:
    for key in patch_avg_ts:
        position = '{}\t{}\t'.format(key[0], key[1])
        data_str = [str(x) for x in patch_avg_ts[key].tolist()]
        values = "\t".join(data_str)
        line = position + values + "\n"
        f.write(line)


print('hello')


