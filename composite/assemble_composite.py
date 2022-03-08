import os
import rasterio
import rasterio.merge
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.colors as colors
input_dir = '../data/Sapelo_2021_01-02_focus/Sapelo_20210104_psscene_analytic_sr_udm2/files/'#'./data/20210104/'
mosaic_name = 'mosaic.tif'
mask_baddata = True
write_mosaic = True

udm_suffix = '_udm2_clip.tif'
sr_img_re = re.compile('(.*)_AnalyticMS_SR_clip.tif|(.*)_AnalyticMS_SR_harmonized_clip.tif')
dot_firstchar = re.compile(r'^\.')  #used to ignore hidden files

temp_dir = './temp/'
if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)

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
    if m and not dot_firstchar.search(file):
        full_path = os.path.join(input_dir, file)
        fhandle = rasterio.open(full_path)
        imgs_to_merge[full_path] = fhandle

profile = imgs_to_merge[list(imgs_to_merge.keys())[0]].profile

if mask_baddata:
    temp_id = 0
    for sr_img in list(imgs_to_merge.keys()):  #need to create list of keys b/c we're going to modify the dict
        m = sr_img_re.search(sr_img)
        if m:
            for i in range(1, len(m.regs)):  #multiple possible match patterns, must find the correct one
                if m[i] is not None:
                    udm_file = m[i] + udm_suffix


            if os.path.exists(udm_file):
                print('found udm: {}'.format(udm_file))
                with rasterio.open(udm_file) as mask_handle:
                    mask_channel = mask_handle.read(1)
                    mask = np.invert(mask_channel.astype(bool))
                    with rasterio.open(sr_img) as src:

                        #mask source image and save masked version
                        img = src.read()
                        #img_masked = np.where(mask==0,  img, 0)
                        transform = src.transform
                        masked_img = img.copy()
                        masked_img[:, mask] = 0
                        temp_filename = temp_dir + 'temp_' + str(temp_id) + '.tif'
                        save_geotiff(temp_filename, masked_img, profile, transform)

                        #substitute masked version in imgs_to_merge dict
                        del imgs_to_merge[sr_img]
                        imgs_to_merge[temp_filename] = rasterio.open(temp_filename)

                        temp_id += 1


fhandles = list(imgs_to_merge.values())
print('about to merge images')
mosaic, transform = rasterio.merge.merge(fhandles, method='max')
print('done merging images')
band_data = mosaic[3, :, :]
band_data = np.divide(band_data.astype(np.float32), 10000)

mid = 0.15
min_sr = np.nanmin(band_data)
max_sr = np.nanmax(band_data)
min_manual = 0.0
max_manual = 0.7
fig = plt.figure(figsize=(6, 10))
ax = fig.add_subplot(1, 1, 1)
cmap = plt.cm.get_cmap('RdGy_r')
cax = ax.imshow(band_data, cmap=cmap, clim=(min_manual, max_manual),
                norm=MidpointNormalize(midpoint=mid, vmin=min_manual, vmax=max_manual))
cbar = fig.colorbar(cax, orientation='horizontal', shrink=0.65)
plt.savefig('mosaic_nir.png', dpi=300)
plt.show()
channels, rows, cols = mosaic.shape

if write_mosaic:
    with rasterio.Env():
        profile = imgs_to_merge[list(imgs_to_merge.keys())[0]].profile
        profile.update(
                        width=cols,
                        height=rows,
                        transform=transform
                        )

        with rasterio.open(mosaic_name,'w', **profile) as dst:
            dst.write(mosaic.astype(rasterio.uint16))

print('hello')