import numpy as np
import matplotlib.pyplot as plt


class DataDisplayDownsampler(object):
    def __init__(self, data_list, delta, max_points=1000):
        if max_points < 1:
            self.max_points = 1000
        else:
            self.max_points = int(max_points)

        self.delta = delta
        self.data = data_list
        self.lines = []

    def downsample(self, data, xstart, xend):
        # get the points in the view range
        # mask = (self.origXData > xstart) & (self.origXData < xend)
        mask = (data.time > xstart) & (data.time < xend)

        # dilate the mask by one to catch the points just outside
        # of the view range to not truncate the line
        mask = np.convolve([1, 1], mask, mode='same').astype(bool)
        # sort out how many points to drop
        ratio = max(np.sum(mask) // self.max_points, 1)

        # mask data
        # xdata = self.origXData[mask]
        # ydata = self.origYData[mask]
        xdata = data.time[mask]
        ydata = data.data[mask]

        # downsample data
        xdata = xdata[::ratio]
        ydata = ydata[::ratio]

        # print("using {} of {} visible points".format(
        #     len(ydata), np.sum(mask)))

        return xdata, ydata

    def update(self, ax):
        lims = ax.viewLim
        if np.abs(lims.width - self.delta) > 1e-8:
            self.delta = lims.width
            xstart, xend = lims.intervalx
            for idx, line in enumerate(self.lines):
                line.set_data(*self.downsample(self.data[idx], xstart, xend))
