

'''
A collection of functions intended to be put into a list to produce a 
schedule for a flared traffic light to follow.

Please consult __all__ for a list of all 8 available functions. Each functions
has documentation.
'''


from ..FlaredTrafficLightObject.flared_traffic_light_cycle import (N_S_flow,
                                                                   W_E_flow,
                                                                   N_S_overwash,
                                                                   W_E_overwash,
                                                                   N_flow,
                                                                   S_flow,
                                                                   E_flow,
                                                                   W_flow)


__all__ = ('N_S_flow',
           'W_E_flow',
           'N_S_overwash',
           'W_E_overwash',
           'N_flow',
           'S_flow',
           'E_flow',
           'W_flow')