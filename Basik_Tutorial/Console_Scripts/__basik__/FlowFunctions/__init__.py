
from . import flared
from . import non_flared


'''
This sub-package contains the flared module (flow-functions for
__basik__.FlaredTrafficLightObject) as well as the non_flared module (flow 
functions for __basik__.TrafficLightObject).

Each module contains eight flow-functions.
'''

__all__ = ['flared',
           'non_flared']