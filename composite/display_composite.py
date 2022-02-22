import os
import rasterio
import rasterio.merge
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

mosaic_file = 'temp2.tif' #"./data/20210714_16/20210714_151559_25_241f_3B_udm2_clip.tif"#

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
with rasterio.open(mosaic_file) as src:
    mosaic = src.read()

band_data = mosaic[3, :, :]
band_data = np.divide(band_data.astype(np.float32), 10000)

mid = 0.1
min_sr = np.nanmin(band_data)
max_sr = np.nanmax(band_data)
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(1, 1, 1)
cmap = plt.cm.get_cmap('RdGy_r')
cax = ax.imshow(band_data, cmap=cmap, clim=(min_sr, max_sr),
                norm=MidpointNormalize(midpoint=mid, vmin=min_sr, vmax=max_sr))
cbar = fig.colorbar(cax, orientation='horizontal', shrink=0.65)
plt.show()