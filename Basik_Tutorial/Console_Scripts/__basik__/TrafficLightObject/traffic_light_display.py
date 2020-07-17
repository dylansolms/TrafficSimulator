
import numpy as np
import matplotlib.pyplot as plt
from ..utils import quarter_circle,dist

from .traffic_light import TrafficLight

#------------------------------------------------------------------------------


class TrafficLightDisplay(object):
    
    '''Provides display for
    __basik__.TrafficLightObject.traffic_light.TrafficLight
    using matplotlib.pyplot and the Qt5Agg backend.
    '''
    
    
    DISPLAY = True
    
    # All coordinates are based on a standardised imaged where we set the
    # extent to [0,100,0,100] and read off the below positions from that plot.
    
    standard_car_length = 20 # length of box when extent is [0,100,0,100].
    standard_car_width = 10
    
    shrink = 0.8  # how much smaller than the box the car is.
    extent0 = np.array([0,100,0,100])   # the image is based on this extent.
    
    N_entrance0 = np.array([55,90])
    N_exit0 = np.array([45,90])
    N_start_turn0 = np.array([55,60])
    N_end_turn0 = np.array([45,60])
    
    E_entrance0 = np.array([90,46])
    E_exit0 = np.array([90,55])
    E_start_turn0 = np.array([60,46])
    E_end_turn0 = np.array([60,55])
    
    S_entrance0 = np.array([45,10])
    S_exit0 = np.array([55,10])
    S_start_turn0 = np.array([45,40])
    S_end_turn0 = np.array([55,40])
    
    W_entrance0 = np.array([10,55])
    W_exit0 = np.array([10,46])
    W_start_turn0 = np.array([40,55])
    W_end_turn0 = np.array([40,46])
    
    pivot0_Q1 = np.array([60,60])
    pivot0_Q2 = np.array([40,60])
    pivot0_Q3 = np.array([40,40])
    pivot0_Q4 = np.array([60,40])
    
    
    N_text0 = np.array([65,90])
    E_text0 = np.array([77,32])
    S_text0 = np.array([15,5])
    W_text0 = np.array([4,65])
    font_size0 = 15
    
    
    short_turn_pts = 5
    long_turn_pts = 10
    
    
    # Images pre-loaded to block.
    
    # North
    block_N_image = plt.imread('__basik__/Images/traffic_light/block_N.jpg')
    block_N_extent0 = np.array([32,62,58.7,100])
    
    # East
    block_E_image = plt.imread('__basik__/Images/traffic_light/block_E.jpg')
    block_E_extent0 = np.array([58.5,100,38,62])
    
    # South
    block_S_image = plt.imread('__basik__/Images/traffic_light/block_S.jpg')
    block_S_extent0 = np.array([38.6,62,0,42])


    # West
    block_W_image = plt.imread('__basik__/Images/traffic_light/block_W.jpg')
    block_W_extent0 = np.array([0,41.7,37.8,62])


    traffic_light_image = plt.imread('__basik__/Images/traffic_light/all_entrances.png')
    
    
    #--------------------------------------------------------------------------
    
    def __init__(self,traffic_light_object,
                      axes=None,
                      show=['N','E','S','W'],
                      car_length=10,car_width=5):
        
        '''
        Parameters:
        -----------
        traffic_light_object: __basik__.TrafficLightObject.traffic_light.TrafficLight
            The internal object that provides the mechanism for the
            simulation to follow. TrafficLightDisplay object will display 
            the progress of this traffic_light_object.  
        axes: matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes on which the display will be rendered. If set
            to None, one will be created along with self.figure.
        show: list
            In the traffic_light_object not all entrances and exits exist
            i.e. they have been set to None. If this has been done then these
            directions should not be in the show list. 
            E.g. a traffic light only has entrances and exits at N and S (this
            is typical of a traffic light for pedestrians) then we would have
            show = ['N',S'].
            This list should not be empty.
            
        Raises:
        -------
        AssertionError:
            If traffic_light_object is not an instance of
            __basik__.TrafficLightObject.traffic_light.TrafficLight
        '''
        
        self.axes = axes
        
        assert isinstance(traffic_light_object,TrafficLight)
        self.traffic_light_object = traffic_light_object
        
        self.car_length = car_length
        self.car_width = car_width
        
        self.setup_image() # determine scale factor
        self.scale_all()   # apply the scale factor
        self.build_tracks()
        self.hide_entrances(show)
        
        # The below corresponds to the traffic_light.py
        self.keys = ['N','E','S','W']
        self.idxs = [0,1,2,3]
        
        
        self.turn_on_display()
        
#        self.signals = None
    
    
    #--------------------------------------------------------------------------
    
    def turn_on_display(self):
        
        for node in self.traffic_light_object.entrances:
            node.traffic_light_display = self
            
        self.traffic_light_object.display = self

        return None
    
    #--------------------------------------------------------------------------
    
    def turn_off_display(self):

        for node in self.traffic_light_object.entrances:
            node.traffic_light_display = None
            
        self.traffic_light_object.display = None
        
        return None

    #--------------------------------------------------------------------------
    
    def setup_image(self):
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)
        self.axes.set_axis_off()
        self.image = self.traffic_light_image
        
        assert self.shrink < 1
        
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
    

    def build_turn_track(self,center,start_pt,Q='Q1',clockwise=False,n_pts=5):
        radius = dist(center,start_pt)
        x,y = quarter_circle(center,radius,Q,clockwise,n_pts)
        track = np.zeros((n_pts,2))
        track[:,0] = x
        track[:,1] = y
        return track.tolist()

    #--------------------------------------------------------------------------
    
    def scale_all(self):
        
        ##### North  #####
        self.N_entrance = self.N_entrance0*self.scale_factor
        self.N_exit = self.N_exit0*self.scale_factor
        self.N_start_turn = self.N_start_turn0*self.scale_factor
        self.N_end_turn = self.N_end_turn0*self.scale_factor
        self.block_N_extent = self.block_N_extent0*self.scale_factor
        
        ##### East  #####
        self.E_entrance = self.E_entrance0*self.scale_factor
        self.E_exit = self.E_exit0*self.scale_factor
        self.E_start_turn = self.E_start_turn0*self.scale_factor
        self.E_end_turn = self.E_end_turn0*self.scale_factor 
        self.block_E_extent = self.block_E_extent0*self.scale_factor
        
        ##### South  #####
        self.S_entrance = self.S_entrance0*self.scale_factor 
        self.S_exit = self.S_exit0*self.scale_factor 
        self.S_start_turn = self.S_start_turn0*self.scale_factor
        self.S_end_turn = self.S_end_turn0*self.scale_factor
        self.block_S_extent = self.block_S_extent0*self.scale_factor
        
        ##### West  #####
        self.W_entrance = self.W_entrance0*self.scale_factor
        self.W_exit = self.W_exit0*self.scale_factor
        self.W_start_turn = self.W_start_turn0*self.scale_factor
        self.W_end_turn = self.W_end_turn0*self.scale_factor
        self.block_W_extent = self.block_W_extent0*self.scale_factor
        
        # Pivots to serve as center of turn
        self.pivot_Q1 = self.pivot0_Q1*self.scale_factor
        self.pivot_Q2 = self.pivot0_Q2*self.scale_factor
        self.pivot_Q3 = self.pivot0_Q3*self.scale_factor
        self.pivot_Q4 = self.pivot0_Q4*self.scale_factor 
        
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
        
        return None
    
    #--------------------------------------------------------------------------
    
    def build_tracks(self):
        
        # STEP 1: produce track for a turn. That is from some start_turn
        # to some end_turn
        
        ##### North  #####
        self.N_bearings = 180
        # Short turn
        self.N_to_E = self.build_turn_track(self.pivot_Q1,self.N_start_turn,
                                            'Q3',False,
                                            self.short_turn_pts)
        # Straight ahead
        self.N_to_S = [self.N_start_turn.tolist(),self.S_end_turn.tolist()]
        # Long turn
        self.N_to_W = self.build_turn_track(self.pivot_Q2,self.N_start_turn,
                                            'Q4',True,
                                            self.long_turn_pts)
        
        ##### East  #####
        self.E_bearings = 270
        # Short turn
        self.E_to_S = self.build_turn_track(self.pivot_Q4,self.E_start_turn,
                                            'Q2',False,
                                            self.short_turn_pts)
        # Straight ahead
        self.E_to_W = [self.E_start_turn.tolist(),self.W_end_turn.tolist()]
        # Long turn
        self.E_to_N = self.build_turn_track(self.pivot_Q1,self.E_start_turn,
                                            'Q3',True,
                                            self.long_turn_pts)
        
        ##### South  #####
        self.S_bearings = 0
        # Short turn
        self.S_to_W = self.build_turn_track(self.pivot_Q3,self.S_start_turn,
                                            'Q1',False,
                                            self.short_turn_pts)
        # Straight ahead
        self.S_to_N = [self.S_start_turn.tolist(),self.N_end_turn.tolist()]
        # Long turn 
        self.S_to_E = self.build_turn_track(self.pivot_Q4,self.S_start_turn,
                                            'Q2',True,
                                            self.long_turn_pts)
        
        ##### West  #####
        self.W_bearings = 90
        # Short turn
        self.W_to_N = self.build_turn_track(self.pivot_Q2,self.W_start_turn,
                                            'Q4',False,
                                            self.short_turn_pts)
        # Straight ahead
        self.W_to_E = [self.W_start_turn.tolist(),self.E_end_turn.tolist()]
        # Long turn
        self.W_to_S = self.build_turn_track(self.pivot_Q3,self.W_start_turn,
                                            'Q1',True,
                                            self.long_turn_pts)
        
        # STEP 2: We have a transition matrix that contains all the turns
        # Note that matrix indices (self.idxs) correspond to some direction
        # which is self.keys .
    
        self.tracks = [[None,self.N_to_E,self.N_to_S,self.N_to_W],
                       [self.E_to_N,None,self.E_to_S,self.E_to_W],
                       [self.S_to_N,self.S_to_E,None,self.S_to_W],
                       [self.W_to_N,self.W_to_E,self.W_to_S,None]]
        
        # STEP 3: we would like the vehicle to perform a turn or crossing
        # but also to then move to the exit point of the traffic light.
        # Hence, we update it below. Note that this also updates the original
        # object i.e. self.N_exit. This is because self.tracks contains pointers
        # to the original object. Once can assess that they are all indeed 
        # the same object i.e. id(self.tracks[0][1]) == id(self.N_to_E) even
        # after we run the loops below. 
        

        for i in range(4):
            entrance = self.entrances[i].tolist()
            for j in range(4):
                if i == j:
                    continue
                exit_ = self.exits[j].tolist()
                self.tracks[i][j].insert(0,entrance)
                self.tracks[i][j].append(exit_)
                # The track now contains all elements to enter, turn and exit.

        # Create a vector of bearings as well. The idxs correspond to self.keys
        self.bearings = [self.N_bearings,self.E_bearings,
                         self.S_bearings,self.W_bearings]
        
        return None
    
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
    
    
    

    
    
    
    

    