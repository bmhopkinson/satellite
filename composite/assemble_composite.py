import os
import rasterio
import rasterio.merge
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.colors as colors
input_dir = './data/20210714_16/'#'./data/20210104/'
mosaic_name = 'mosaic.tif'
mask_baddata = True
write_mosaic = True

udm_suffix = '_udm2_clip.tif'
sr_img_re = re.compile('(.*)_AnalyticMS_SR_clip.tif')

class MidpointNormalize(colors.Normalize):
    """
    Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)
    e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
    Credit: Joe Kington, http://chris35wills.github.io/matplotlib_diverging_colorbar/
    """
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))

def save_geotiff(file_name, img_data, profile, transform):
    channels, rows, cols = img_data.shape
    with rasterio.Env():
        profile.update(
                        width=cols,
                        height=rows,
                        transform=transform
                        )

        with rasterio.open(file_name,'w', **profile) as dst:
            dst.write(img_data.astype(rasterio.uint16))

imgs_to_merge = {}
for file in os.listdir(input_dir):
    #base, ext = os.path.splitext(file)
    m = sr_img_re.match(file)
    #if ext == '.tif':
    if m:
        full_path = os.path.join(input_dir, file)
        fhandle = rasterio.open(full_path)
        imgs_to_merge[full_path] = fhandle

profile = imgs_to_merge[list(imgs_to_merge.keys())[0]].profile
if mask_baddata:
    for sr_img in imgs_to_merge.keys():
        m = sr_img_re.match(sr_img)
        if m:
            udm_file = m[1] + udm_suffix
            if os.path.exists(udm_file):
                print('found udm: {}'.format(udm_file))
                with rasterio.open(udm_file) as mask_handle:
                    cloud_mask = mask_handle.read(6)
                    with rasterio.open(sr_img) as src:
                        img = src.read()
                        #img_masked = np.where(mask==0,  img, 0)
                        transform = src.transform
                        masked = img.copy()
                        masked[:, cloud_mask] = 0  #this is horribly slow
                        save_geotiff('temp2.tif', masked, profile, transform)
                        print('hello')

#
# fhandles = list(imgs_to_merge.values())
# print('about to merge images')
# mosaic, transform = rasterio.merge.merge(fhandles)
# print('done merging images')
# band_data = mosaic[3, :, :]
# band_data = np.divide(band_data.astype(np.float32), 10000)
#
# mid = 0.1
# min_sr = np.nanmin(band_data)
# max_sr = np.nanmax(band_data)
# fig = plt.figure(figsize=(10,10))
# ax = fig.add_subplot(1, 1, 1)
# cmap = plt.cm.get_cmap('RdGy_r')
# cax = ax.imshow(band_data, cmap=cmap, clim=(min_sr, max_sr),
#                 norm=MidpointNormalize(midpoint=mid, vmin=min_sr, vmax=max_sr))
# cbar = fig.colorbar(cax, orientation='horizontal', shrink=0.65)
# #plt.show()
# channels, rows, cols = mosaic.shape
#
# if write_mosaic:
#     with rasterio.Env():
#         profile = imgs_to_merge[list(imgs_to_merge.keys())[0]].profile
#         profile.update(
#                         width=cols,
#                         height=rows,
#                         transform=transform
#                         )
#
#         with rasterio.open(mosaic_name,'w', **profile) as dst:
#             dst.write(mosaic.astype(rasterio.uint16))
#
# print('hello')