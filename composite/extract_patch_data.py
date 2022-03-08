import os
import rasterio
import numpy as np


base_folder = './data/composites/'

# patches = [
#             [995, 1005, 6995, 7005],
#             [985,  995, 6995, 7005]
#           ]

patches = [
            [480427, 3486209, 5, 5],     #patch center in EPSG:32167: lat, lon; followed by patch radius lat, lon, in pixels
            [480402, 3486209, 5, 5]
          ]

composite_id = []
patch_avgs = []
for file in os.listdir(base_folder):
    if os.path.splitext(file)[1] == '.tif':
        full_path = os.path.join(base_folder, file)
        with rasterio.open(full_path) as src:
            b, g, r, nir = (src.read(k) for k in (1, 2, 3, 4))
            print('read in geotiff')

            img = np.stack((b, g, r, nir), axis=2)
            img = np.divide(img.astype(np.float32), 10000)  # convert to reflectance

            patch_data = []
            composite_id.append(file)

            for i, patch in enumerate(patches):
                py, px = src.index(patch[0], patch[1])
                rady, radx = patch[2:]
                patch_cur = img[py-rady:py+rady, px-radx:px+radx]
                patch_data.append(patch_cur)

                if len(patch_avgs)-1 < i:
                    patch_avgs.append( [ np.average(patch_cur, axis=(0, 1)) ])
                else:
                    patch_avgs[i].append(np.average(patch_cur, axis=(0, 1)))

outfile_basename = './patch_avgs_{}.txt'
for i, patch_avg in enumerate(patch_avgs):
    with open(outfile_basename.format(i), 'w') as f:
        for comp_id, avg in zip(composite_id, patch_avg):
            line = '{}\t{}\t{}\t{}\t{}\n'.format(comp_id, *avg)
            f.write(line)



print('hello')


