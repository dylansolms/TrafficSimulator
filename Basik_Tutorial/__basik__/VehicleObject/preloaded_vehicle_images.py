


import matplotlib.pyplot as plt
from .vehicle_colors import color_list
from ..utils import scale255

vehicle_image_arrays = dict()

for color in color_list:
    if color == 'random':
        continue
    path = '__basik__/Images/cars/{0}.png'.format(color)
    vehicle_image_arrays[color] = scale255(plt.imread(path))


