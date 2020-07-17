

import numpy as np
import matplotlib.pyplot as plt
from .intersection import Intersection



class IntersectionDisplay(object):
    
    
    '''Provides display for
    __basik__.IntersectionObject.intersection.Intersection
    using matplotlib.pyplot and the Qt5Agg backend.
    '''
    
    DISPLAY = True
    
    standard_car_length = 20 # length of box when extent is [0,100,0,100].
    standard_car_width = 10
    

    shrink = 1.0  # how much smaller than the box the car is.
    extent0 = np.array([0,100,0,100])   # the image is based on this extent.
    # We plotted the image at this standard extent and read the desired 
    # coordinates of placement points from it. These are the so-called pt0
    # that we have below.
    
    
    ####  NORTH (MAIN FLOW)  ####
    N_entrance0 = np.array([60,89])
    N_wait0 = np.array([60,80])
    N_right_turn0 = np.array([[60.        , 60.00002   ],
                              [58.47759639, 52.34634521],
                              [54.14214269, 45.85787145],
                              [47.65367327, 41.52241126],
                              [40.        , 40.        ],
                              [30.        , 40.        ],
                              [11.        , 40.        ]])
    N_left_turn0 = np.array([[60.        , 72.        ],
                             [61.60769715, 65.99999654],
                             [66.00000693, 61.60769115],
                             [72.000012  , 60.        ],
                             [89.        , 60.        ]])
    N_forward0 = np.array([[60., 50.],
                           [60., 11.]])
    
    
    ####  EAST (SUB FLOW)  ####
    E_entrance0 = np.array([89,40])
    E_wait0 = np.array([80,40])
    E_right_turn0 = np.array([[60.00002   , 40.        ],
                              [52.34634521, 41.52240361],
                              [45.85787145, 45.85785731],
                              [41.52241126, 52.34632673],
                              [40.        , 60.        ],
                              [40.        , 89.        ]])
    E_left_turn0 = np.array([[70.        , 40.        ],
                             [64.99999711, 38.66025237],
                             [61.33974263, 34.99999423],
                             [60.        , 29.99999   ],
                             [60.        , 11.        ]])
    E_forward0 = np.array([[57., 40.],
                           [34., 40.],
                           [11., 40.]])
    
    ####  SOUTH (MAIN FLOW)  ####
    S_entrance0 = np.array([40,11])
    S_wait0 = np.array([40,20])
    S_right_turn0 = np.array([[40.        , 39.99998   ],
                              [41.52240361, 47.65365479],
                              [45.85785731, 54.14212855],
                              [52.34632673, 58.47758874],
                              [60.        , 60.        ],
                              [70.        , 60.        ],
                              [89.        , 60.        ]])
    S_left_turn0 = np.array([[40.        , 28.        ],
                             [38.39230285, 34.00000346],
                             [33.99999307, 38.39230885],
                             [27.999988  , 40.        ],
                             [11.        , 40.        ]])
    S_forward0 = np.array([[40, 50],
                           [40, 89]])
    
    
    ####  WEST (SUB FLOW)  ####
    W_entrance0 = np.array([11,60])
    W_wait0 = np.array([20,60])
    W_right_turn0 = np.array([[39.99998   , 60.        ],
                              [47.65365479, 58.47759639],
                              [54.14212855, 54.14214269],
                              [58.47758874, 47.65367327],
                              [60.        , 40.        ],
                              [60.        , 11.        ]])
    W_left_turn0 = np.array([[30.        , 60.        ],
                             [35.00000289, 61.33974763],
                             [38.66025737, 65.00000577],
                             [40.        , 70.00001   ],
                             [40.        , 89.        ]])
    W_forward0 = np.array([[43, 60],
                           [66, 60],
                           [89, 60]])
    
    
    
    # Images pre-loaded to block.
    
    # North
    block_N_image = plt.imread('__basik__/Images/intersection/block_N.jpg')
    block_N_extent0 = np.array([26,74,67.7,100])
    
    # East
    block_E_image = plt.imread('__basik__/Images/intersection/block_E.jpg')
    block_E_extent0 = np.array([68.5,100,27,74])
    
    # South
    block_S_image = plt.imread('__basik__/Images/intersection/block_S.jpg')
    block_S_extent0 = np.array([26,74,0,32.4])

    # West
    block_W_image = plt.imread('__basik__/Images/intersection/block_W.jpg')
    block_W_extent0 = np.array([0,31.5,26,74])
    

    intersection_image = plt.imread('__basik__/Images/intersection/all_entrances.png')
    
    
    #--------------------------------------------------------------------------
    
    def __init__(self,intersection_object,
                      axes=None,
                      show=['N','E','S','W'],
                      car_length=10,car_width=5):
        
        '''
        Parameters:
        -----------
        intersection_object: __basik__.IntersectionObject.intersection.Intersection
            The internal object that provides the mechanism for the
            simulation to follow. IntersectionDisplay object will display 
            the progress of this intersection_object.  
        axes: matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes on which the display will be rendered. If set
            to None, one will be created along with self.figure.
        show: list
            In the intersection_object not all entrances and exits exist
            i.e. they have been set to None. If this has been done then these
            directions should not be in the show list. 
            This list should not be empty.
            
        Raises:
        -------
        AssertionError:
            If intersection_object is not an instance of
            __basik__.IntersectionObject.intersection.Intersection
        '''
        
        self.axes = axes
        
        assert isinstance(intersection_object,Intersection)
        
        self.intersection_object = intersection_object
        
        self.car_length = car_length
        self.car_width = car_width
        
        self.setup_image() # determine scale factor
        self.scale_all()   # apply the scale factor
        self.hide_entrances(show)
        
        # The below corresponds to the traffic_light.py
        self.keys = ['N','E','S','W']
        self.idxs = [0,1,2,3]
        
        self.turn_on_display()
        

    #--------------------------------------------------------------------------
    
    def turn_on_display(self):
        # All stop street entrances need to have a display object give.
        for node in self.intersection_object.entrances:
            if node is not None:
                node.intersection_display = self
        # Note that the exits must not contain the stop street as a display object.
        # They should have a Lane/Road as their display object.
        return None
    
    #--------------------------------------------------------------------------
    
    def turn_off_display(self):
        # All stop street entrance need to have display object as None.
        for node in self.intersection_object.entrances:
            if node is not None:
                node.intersection_display = None
        return None
    
    #--------------------------------------------------------------------------
    
    def setup_image(self):
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)
        self.axes.set_axis_off()
        self.image = self.intersection_image
        
        assert self.shrink <= 1
        
        self.scale_factor = self.car_length/(self.shrink*self.standard_car_length)
        self.extent = self.extent0*self.scale_factor
        self.xlim = self.extent[1]
        self.ylim = self.extent[3]
        
        self.show()
        
        return None
    
    
    #--------------------------------------------------------------------------
    
    def hide_entrances(self,show):
        
        self.show = show
        all_entrances = set(['N','E','S','W'])
        self.hide = all_entrances.difference(set(self.show))
        
        to_hide = {'N':{'block':self.block_N_image,
                        'block extent':self.block_N_extent},
                   'E':{'block':self.block_E_image,
                        'block extent':self.block_E_extent},
                    'S':{'block':self.block_S_image,
                        'block extent':self.block_S_extent},
                    'W':{'block':self.block_W_image,
                        'block extent':self.block_W_extent}}
        
        for key in self.hide:
            
            self.axes.imshow(to_hide[key]['block'],
                             extent=to_hide[key]['block extent'])

        
        return None
        
    
    #--------------------------------------------------------------------------
    
    def show(self):
        
        self.axes.imshow(self.image,extent=self.extent)
        self.axes.set_xlim(0,self.xlim)
        self.axes.set_ylim(0,self.ylim)
        try:
            self.figure.show()
        except AttributeError:
            plt.show()

        return None
    

    #--------------------------------------------------------------------------
    
    def scale_all(self):
        
        ##### North  #####
        self.N_entrance = self.N_entrance0*self.scale_factor
        self.N_wait = self.N_wait0*self.scale_factor
        self.N_right_turn = self.N_right_turn0*self.scale_factor
        self.N_left_turn = self.N_left_turn0*self.scale_factor
        self.N_forward = self.N_forward0*self.scale_factor
        self.block_N_extent = self.block_N_extent0*self.scale_factor
        
        ##### East  #####
        self.E_entrance = self.E_entrance0*self.scale_factor
        self.E_wait = self.E_wait0*self.scale_factor
        self.E_right_turn = self.E_right_turn0*self.scale_factor
        self.E_left_turn = self.E_left_turn0*self.scale_factor
        self.E_forward = self.E_forward0*self.scale_factor
        self.block_E_extent = self.block_E_extent0*self.scale_factor
        
        ##### South  #####
        self.S_entrance = self.S_entrance0*self.scale_factor
        self.S_wait = self.S_wait0*self.scale_factor
        self.S_right_turn = self.S_right_turn0*self.scale_factor
        self.S_left_turn = self.S_left_turn0*self.scale_factor
        self.S_forward = self.S_forward0*self.scale_factor
        self.block_S_extent = self.block_S_extent0*self.scale_factor
        
        ##### West  #####
        self.W_entrance = self.W_entrance0*self.scale_factor
        self.W_wait = self.W_wait0*self.scale_factor
        self.W_right_turn = self.W_right_turn0*self.scale_factor
        self.W_left_turn = self.W_left_turn0*self.scale_factor
        self.W_forward = self.W_forward0*self.scale_factor
        self.block_W_extent = self.block_W_extent0*self.scale_factor
        
        
        # Entrances and exits
        self.entrances = [self.N_entrance,self.E_entrance,
                          self.S_entrance,self.W_entrance]
        
        self.wait_zones = [self.N_wait,self.E_wait,
                           self.S_wait,self.W_wait]
        

        
        
        self.bearings = [180,270,0,90]
        
        self.turns = np.array([[None,self.N_left_turn,self.N_forward,self.N_right_turn],
                               [self.E_right_turn,None,self.E_left_turn,self.E_forward],
                               [self.S_forward,self.S_right_turn,None,self.S_left_turn],
                               [self.W_left_turn,self.W_forward,self.W_right_turn,None]],
                    dtype=object)
        

    
        return None
    
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        return 'Intersection Display ({0})'.format(hex(id(self)))
            
    #--------------------------------------------------------------------------
    
    

    
    
    
    
    
    
    
    
    
    
    