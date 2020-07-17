


import numpy as np
import matplotlib.pyplot as plt

from .flared_traffic_light import FlaredTrafficLight

#------------------------------------------------------------------------------


class FlaredTrafficLightDisplay(object):
    
    '''Provides display for
    __basik__.FlaredTrafficLightObject.flared_traffic_light.FlaredTrafficLight
    using matplotlib.pyplot and the Qt5Agg backend.
    '''
    
    DISPLAY = True
    
    
    # All coordinates are based on a standardised imaged where we set the
    # extent to [0,100,0,100] and read off the below positions from that plot.
    
    standard_car_length = 6 # length of car when extent is [0,100,0,100].
    standard_car_width = 3
    
    shrink = 1.0 # Further shrinking of the vehicle.
    extent0 = np.array([0,100,0,100])   # the image is based on this extent.
    
    
    left_entrance_moves = 2
    right_entrance_moves = 3
    
    
    ##### NORTH  #####
    # Entraces & exits.
    N_entrance0 = np.array([62.5, 97.0])
    N_exit0 = np.array([39.5,97.])
    # The two buffers.
    N_left_buffer0 = np.array([[62.5, 97. ],
                               [62.5, 95. ],
                               [62.5, 88. ],
                               [62.5, 81. ],
                               [62.5, 74. ]])
    N_right_buffer0 = np.array([[62.5 , 97.  ],
                                [60.  , 94.58],
                                [54.5 , 89.9 ],
                                [54.5 , 88.  ],
                                [54.5 , 81.  ],
                                [54.5 , 74.  ]])
    # Three types of turns.
    # Right turn can only be performed from the right buffer/.
    N_right_turn0 = np.array([[54.6       , 67.        ],
                              [47.5       , 58.7       ],
                              [47.5       , 47.500008  ],
                              [47.29942482, 45.71983921],
                              [46.70775342, 44.02893524],
                              [45.75465471, 42.51208516],
                              [44.4879211 , 41.24535028],
                              [42.97107197, 40.29225005],
                              [41.28016859, 39.70057696],
                              [39.5       , 39.5       ],
                              [26.        , 39.5       ],
                              [ 3.        , 39.5       ]])
    # Straight ahead and left turn can only be perfomed by the left buffer.
    N_straight0 = np.array([[62.5 , 67.  ],
                            [62.  , 57.87],
                            [61.  , 48.74],
                            [60.5 , 39.5 ],
                            [60.5 , 30.37],
                            [60.5 , 21.24],
                            [60.5 , 12.11],
                            [60.5 ,  3.  ]])
    N_left_turn0 = np.array([[63.37538648, 69.59913787],
                             [65.86827608, 65.86826795],
                             [69.5991485 , 63.37538208],
                             [74.0000115 , 62.5       ],
                             [78.6       , 62.        ],
                             [83.2       , 61.5       ],
                             [87.8       , 61.        ],
                             [92.4       , 60.5       ],
                             [97.        , 60.5       ]])
    
    N_block0 = np.array([29,72,66,100])
    N_feeding_buffer0 = np.array([70,100,41,51])
    
    
    ##### EAST  #####
    E_entrance0 = np.array([97.  , 37.5 ])
    E_exit0 = np.array([97.,60.5])
    E_left_buffer0 = np.array([[97. , 37.5],
                               [95. , 37.5],
                               [88. , 37.5],
                               [81. , 37.5],
                               [74. , 37.5]])
    E_right_buffer0 = np.array([[97.  , 37.5 ],
                               [94.58, 40.  ],
                               [89.9 , 45.5 ],
                               [88.  , 45.5 ],
                               [81.  , 45.5 ],
                               [74.  , 45.5 ]])
    E_right_turn0 = np.array([[67.        , 45.4       ],
                              [58.7       , 52.5       ],
                              [47.500008  , 52.5       ],
                              [45.71983921, 52.70057518],
                              [44.02893524, 53.29224658],
                              [42.51208516, 54.24534529],
                              [41.24535028, 55.5120789 ],
                              [40.29225005, 57.02892803],
                              [39.70057696, 58.71983141],
                              [39.5       , 60.5       ],
                              [39.5       , 74.        ],
                              [39.5       , 97.        ]])
    E_straight0 = np.array([[67.  , 37.5 ],
                            [57.87, 38.  ],
                            [48.74, 39.  ],
                            [39.5 , 39.5 ],
                            [30.37, 39.5 ],
                            [21.24, 39.5 ],
                            [12.11, 39.5 ],
                            [ 3.  , 39.5 ]])
    E_left_turn0 = np.array([[69.59913787, 36.62461352],
                             [65.86826795, 34.13172392],
                             [63.37538208, 30.4008515 ],
                             [62.5       , 25.9999885 ],
                             [62.        , 21.4       ],
                             [61.5       , 16.8       ],
                             [61.        , 12.2       ],
                             [60.5       ,  7.6       ],
                             [60.5       ,  3.        ]])
    
    
    E_block0 = np.array([66,100,29,72])
    E_feeding_buffer0 = np.array([41,51,0,30])
    
    

    ##### SOUTH  #####
    S_entrance0 = np.array([37.5,3])
    S_exit0 = np.array([60.5,3.])
    S_left_buffer0 = np.array([[37.5,3],
                               [37.5,5],
                               [37.5,12],
                               [37.5,19],
                               [37.5,26]])
    S_right_buffer0 = np.array([[37.5,3],
                                [40,5.42],
                                [45.5,10.1],
                                [45.5,12],
                                [45.5,19],
                                [45.5,26]])
    S_right_turn0 = np.array([[45.4       , 33.        ],
                              [52.5       , 41.3       ],
                              [52.5       , 52.499992  ],
                              [52.70057518, 54.28016079],
                              [53.29224658, 55.97106476],
                              [54.24534529, 57.48791484],
                              [55.5120789 , 58.75464972],
                              [57.02892803, 59.70774995],
                              [58.71983141, 60.29942304],
                              [60.5       , 60.5       ],
                              [74.        , 60.5       ],
                              [97.        , 60.5       ]])
    S_straight0 = np.array([[37.5 , 33.  ],
                            [38.  , 42.13],
                            [39.  , 51.26],
                            [39.5 , 60.5 ],
                            [39.5 , 69.63],
                            [39.5 , 78.76],
                            [39.5 , 87.89],
                            [39.5 , 97.  ]])
    S_left_turn0 = np.array([[36.62461352, 30.40086213],
                             [34.13172392, 34.13173205],
                             [30.4008515 , 36.62461792],
                             [25.9999885 , 37.5       ],
                             [21.4       , 38.        ],
                             [16.8       , 38.5       ],
                             [12.2       , 39.        ],
                             [ 7.6       , 39.5       ],
                             [ 3.        , 39.5       ]])
    
    S_block0 = np.array([29,72,0,34])
    S_feeding_buffer0 = np.array([0,30,49,59.5])
    
    ##### WEST  #####
    W_entrance0 = np.array([3.,62.5])
    W_exit0 = np.array([3.,39.5])
    W_left_buffer0 = np.array([[ 3. , 62.5],
                              [ 5. , 62.5],
                              [12. , 62.5],
                              [19. , 62.5],
                              [26. , 62.5]])
    W_right_buffer0 = np.array([[ 3.  , 62.5 ],
                                [ 5.42, 60.  ],
                                [10.1 , 54.5 ],
                                [12.  , 54.5 ],
                                [19.  , 54.5 ],
                                [26.  , 54.5 ]])
    W_right_turn0 = np.array([[33.        , 54.6       ],
                              [41.3       , 47.5       ],
                              [52.499992  , 47.5       ],
                              [54.28016079, 47.29942482],
                              [55.97106476, 46.70775342],
                              [57.48791484, 45.75465471],
                              [58.75464972, 44.4879211 ],
                              [59.70774995, 42.97107197],
                              [60.29942304, 41.28016859],
                              [60.5       , 39.5       ],
                              [60.5       , 26.        ],
                              [60.5       ,  3.        ]])
    W_straight0 = np.array([[33.  , 62.5 ],
                            [42.13, 62.  ],
                            [51.26, 61.  ],
                            [60.5 , 60.5 ],
                            [69.63, 60.5 ],
                            [78.76, 60.5 ],
                            [87.89, 60.5 ],
                            [97.  , 60.5 ]])
    W_left_turn0 = np.array([[30.40086213, 63.37538648],
                             [34.13173205, 65.86827608],
                             [36.62461792, 69.5991485 ],
                             [37.5       , 74.0000115 ],
                             [38.        , 78.6       ],
                             [38.5       , 83.2       ],
                             [39.        , 87.8       ],
                             [39.5       , 92.4       ],
                             [39.5       , 97.        ]])
    
    W_block0 = np.array([0,34,29,72])
    W_feeding_buffer0 = np.array([49,59,70,100])
    
    
    
    
    N_text0 = np.array([73,90])
    E_text0 = np.array([83,27])
    S_text0 = np.array([13,8])
    W_text0 = np.array([3.5,72])
    font_size0 = 5
    
    # Preload images for blocking of entrances. This means that all
    # class instances make use of the same images instead of creating their
    # own each time. This would be wasteful in terms of memory.
    
    # N
    block_N_image = plt.imread('__basik__/Images/flared_traffic_light/block_N.jpg')
    block_N_buffer_image = plt.imread('__basik__/Images/flared_traffic_light/block_N_turn.jpg')
    
    # E
    block_E_image = plt.imread('__basik__/Images/flared_traffic_light/block_E.jpg')
    block_E_buffer_image = plt.imread('__basik__/Images/flared_traffic_light/block_E_turn.jpg')
    
    # S
    block_S_image = plt.imread('__basik__/Images/flared_traffic_light/block_S.jpg')
    block_S_buffer_image = plt.imread('__basik__/Images/flared_traffic_light/block_S_turn.jpg')
    
    # 
    block_W_image = plt.imread('__basik__/Images/flared_traffic_light/block_W.jpg')
    block_W_buffer_image = plt.imread('__basik__/Images/flared_traffic_light/block_W_turn.jpg')
    
    
    flared_traffic_light_image = plt.imread('__basik__/Images/flared_traffic_light/all_entrances.jpg')
    
    
    #--------------------------------------------------------------------------
    
    def __init__(self,flared_traffic_light_object,
                      axes=None,
                      show=['N','E','S','W'],
                      car_length=10,car_width=5):
        
        '''
        Parameters:
        -----------
        flared_traffic_light_object: __basik__.FlaredTrafficLightObject.flared_traffic_light.FlaredTrafficLight
            The internal object that provides the mechanism for the
            simulation to follow. FlaredTrafficLightDisplay object will display 
            the progress of this flared_traffic_light_object.  
        axes: matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes on which the display will be rendered. If set
            to None, one will be created along with self.figure.
        show: list
            In the flared_traffic_light_object not all entrances and exits exist
            i.e. they have been set to None. If this has been done then these
            directions should not be in the show list. 
            E.g. a traffic light only has entrances and exits at N and S (this
            is typical of a traffic light for pedestrians) then we would have
            show = ['N',S'].
            This list should not be empty.
            
        Raises:
        -------
        AssertionError:
            If flared_traffic_light_object is not an instance of
            __basik__.FlaredTrafficLightObject.flared_traffic_light.FlaredTrafficLight
        '''
        
        self.axes = axes
        
        assert isinstance(flared_traffic_light_object,FlaredTrafficLight)
        self.flared_traffic_light_object = flared_traffic_light_object
        
        self.car_length = car_length
        self.car_width = car_width
        
        self.setup_image() # determine scale factor
        self.scale_all()   # apply the scale factor
        self.hide_entrances(show)  # hide entrances not in show
        
        # The below corresponds to the traffic_light.py
        self.keys = ['N','E','S','W']
        self.idxs = [0,1,2,3]
        
        
        self.turn_on_display()
        
#        self.signals = None
        
        
    #--------------------------------------------------------------------------
    
    
    def hide_entrances(self,show):
        
        self.show = show
        all_entrances = set(['N','E','S','W'])
        self.hide = all_entrances.difference(set(self.show))
        
        to_hide = {'N':{'block':self.block_N_image,
                        'block extent':self.N_block,
                        'buffer':self.block_N_buffer_image,
                        'buffer extent':self.N_feeding_buffer},
                   'E':{'block':self.block_E_image,
                        'block extent':self.E_block,
                        'buffer':self.block_E_buffer_image,
                        'buffer extent':self.E_feeding_buffer},
                    'S':{'block':self.block_S_image,
                        'block extent':self.S_block,
                        'buffer':self.block_S_buffer_image,
                        'buffer extent':self.S_feeding_buffer},
                    'W':{'block':self.block_W_image,
                        'block extent':self.W_block,
                        'buffer':self.block_W_buffer_image,
                        'buffer extent':self.W_feeding_buffer}}
        
        for key in self.hide:
            
            self.axes.imshow(to_hide[key]['block'],
                             extent=to_hide[key]['block extent'])
            self.axes.imshow(to_hide[key]['buffer'],
                             extent=to_hide[key]['buffer extent'])
        
        return None
        
        
    
    #--------------------------------------------------------------------------
    
    def turn_on_display(self):
        
        for node in self.flared_traffic_light_object.entrances:
            node.flared_traffic_light_display = self
            
        self.flared_traffic_light_object.display = self

        return None
    
    #--------------------------------------------------------------------------
    
    def turn_off_display(self):

        for node in self.flared_traffic_light_object.entrances:
            node.flared_traffic_light_display = None
            
        self.flared_traffic_light_object.display = None
        
        return None

    #--------------------------------------------------------------------------
    
    def setup_image(self):
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)
        self.axes.set_axis_off()
        self.image = self.flared_traffic_light_image
        
        assert self.shrink <= 1
        
        self.scale_factor = self.car_length/(self.shrink*self.standard_car_length)
        self.extent = self.extent0*self.scale_factor
        self.xlim = self.extent[1]
        self.ylim = self.extent[3]
        
        self.show()
        
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
        
        
        ####  NORTH  ####
        self.N_entrance = self.N_entrance0*self.scale_factor
        self.N_exit = self.N_exit0*self.scale_factor
        self.N_right_buffer = self.N_right_buffer0*self.scale_factor
        self.N_left_buffer = self.N_left_buffer0*self.scale_factor
        self.N_right_turn = self.N_right_turn0*self.scale_factor
        self.N_straight = self.N_straight0*self.scale_factor
        self.N_left_turn = self.N_left_turn0*self.scale_factor
        self.N_bearings = 180
        self.N_block = self.N_block0*self.scale_factor
        self.N_feeding_buffer = self.N_feeding_buffer0*self.scale_factor
        
        
        #### EAST  ####
        self.E_entrance = self.E_entrance0*self.scale_factor
        self.E_exit = self.E_exit0*self.scale_factor
        self.E_right_buffer = self.E_right_buffer0*self.scale_factor
        self.E_left_buffer = self.E_left_buffer0*self.scale_factor
        self.E_right_turn = self.E_right_turn0*self.scale_factor
        self.E_straight = self.E_straight0*self.scale_factor
        self.E_left_turn = self.E_left_turn0*self.scale_factor
        self.E_bearings = 270
        self.E_block = self.E_block0*self.scale_factor
        self.E_feeding_buffer = self.E_feeding_buffer0*self.scale_factor
        
        ####  SOUTH  ####
        self.S_entrance = self.S_entrance0*self.scale_factor
        self.S_exit = self.S_exit0*self.scale_factor
        self.S_right_buffer = self.S_right_buffer0*self.scale_factor
        self.S_left_buffer = self.S_left_buffer0*self.scale_factor
        self.S_right_turn = self.S_right_turn0*self.scale_factor
        self.S_straight = self.S_straight0*self.scale_factor
        self.S_left_turn = self.S_left_turn0*self.scale_factor
        self.S_bearings = 0
        self.S_block = self.S_block0*self.scale_factor
        self.S_feeding_buffer = self.S_feeding_buffer0*self.scale_factor
        
        #### WEST  ####
        self.W_entrance = self.W_entrance0*self.scale_factor
        self.W_exit = self.W_exit0*self.scale_factor
        self.W_right_buffer = self.W_right_buffer0*self.scale_factor
        self.W_left_buffer = self.W_left_buffer0*self.scale_factor
        self.W_right_turn = self.W_right_turn0*self.scale_factor
        self.W_straight = self.W_straight0*self.scale_factor
        self.W_left_turn = self.W_left_turn0*self.scale_factor
        self.W_bearings = 90
        self.W_block = self.W_block0*self.scale_factor
        self.W_feeding_buffer = self.W_feeding_buffer0*self.scale_factor
        
        
        # Text to show what state the traffic signals are in
        self.N_text = self.N_text0*self.scale_factor
        self.E_text = self.E_text0*self.scale_factor
        self.S_text = self.S_text0*self.scale_factor
        self.W_text = self.W_text0*self.scale_factor
        self.font_size = self.font_size0*self.scale_factor
        
        self.text = [self.N_text,self.E_text,
                     self.S_text,self.W_text]
        
        
        # Entrances and exits
        self.entrances = [self.N_entrance,self.E_entrance,
                          self.S_entrance,self.W_entrance]
        
        self.exits = [self.N_exit,self.E_exit,
                      self.S_exit,self.W_exit]
        
        # All bearings at entrances
        self.bearings = [self.N_bearings,self.E_bearings,
                         self.S_bearings,self.W_bearings]
        
        
        self.buffers = np.array([[self.N_left_buffer,self.N_right_buffer],
                                 [self.E_left_buffer,self.E_right_buffer],
                                 [self.S_left_buffer,self.S_right_buffer],
                                 [self.W_left_buffer,self.W_right_buffer]],
                          dtype=object)
        
        
        self.turns = np.array([[None,self.N_left_turn,self.N_straight,self.N_right_turn],
                               [self.E_right_turn,None,self.E_left_turn,self.E_straight],
                               [self.S_straight,self.S_right_turn,None,self.S_left_turn],
                               [self.W_left_turn,self.W_straight,self.W_right_turn,None]],
                        dtype=object)
        
        return None
    
    #--------------------------------------------------------------------------
    
#    def build_tracks(self):
#         We have hard-coded the tracks in 
#         build_flared_traffic_light_tracks.py
      
    #--------------------------------------------------------------------------
    
    def setup_traffic_light_signals(self,specs):
        
        self.signals = np.zeros(4,dtype=object)
        for idx in range(4):
            
            key = self.keys[idx]
            
            if key in self.show:
            
                spec = specs[idx]
                # Display the first/opening signals
                signal = self.axes.text(*self.text[idx],
                                        s=spec['message'],
                                        fontsize=self.font_size,
                                        color='white',
                                        bbox=dict(boxstyle='round',
                                                  facecolor=spec['color'],
                                                  edgecolor='white'))
                self.signals[idx] = signal
            
        return None
    
    #--------------------------------------------------------------------------
    
    def change_traffic_light_signals(self,specs):
        
        # self.signals already exist. 
        
        for idx in range(4):
            
            key = self.keys[idx]
            
            if key in self.show:
            
                self.signals[idx].remove()
                spec = specs[idx]
                # Display new signal.
                signal = self.axes.text(*self.text[idx],
                                        s=spec['message'],
                                        fontsize=self.font_size,
                                        color='white',
                                        bbox=dict(boxstyle='round',
                                                  facecolor=spec['color'],
                                                  edgecolor='white'))
                self.signals[idx] = signal
            
        return None
    
    #--------------------------------------------------------------------------
    
    def show_signals(self,specs):
        
        
        if hasattr(self,'signals'):
            print(1)
            self.change_traffic_light_signals(specs)
        else:
            print(2)
            self.setup_traffic_light_signals(specs)
            
#        if self.signals is None:
#            print(1)
#            self.setup_traffic_light_signals(specs)
#        else:
#            print(2)
#            self.change_traffic_light_signals(specs)
            
        return None
        
    #--------------------------------------------------------------------------
    
    
    

#------------------------------------------------------------------------------
    
    
    
    

    
    

    