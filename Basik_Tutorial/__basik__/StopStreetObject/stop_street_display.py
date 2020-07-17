

import numpy as np
import matplotlib.pyplot as plt

from ..utils import quarter_circle,dist

from .stop_street import StopStreet


class StopStreetDisplay(object):
    
    '''Provides display for
    __basik__.StopStreetObject.stop_street.StopStreet
    using matplotlib.pyplot and the Qt5Agg backend.
    '''
    
    DISPLAY = True

    standard_car_length = 21.5 # length of box when extent is [0,100,0,100].
    standard_car_width = 10
    

    shrink = 0.9  # how much smaller than the box the car is.
    extent0 = np.array([0,100,0,100])   # the image is based on this extent.
    # We plotted the image at this standard extent and read the desired 
    # coordinates of placement points from it. These are the so-called pt0
    # that we have below.
    
    N_entrance0 = np.array([57,89])
    N_exit0 = np.array([43,89])
    N_start_turn0 = np.array([57,66.5])
    N_end_turn0 = np.array([43,66.5])
    
    E_entrance0 = np.array([89,43])
    E_exit0 = np.array([89,58])
    E_start_turn0 = np.array([65.5,43])
    E_end_turn0 = np.array([65.5,58])
    
    S_entrance0 = np.array([43,11])
    S_exit0 = np.array([57,11])
    S_start_turn0 = np.array([43,34.5])
    S_end_turn0 = np.array([57,34.5])
    
    W_entrance0 = np.array([11,58])
    W_exit0 = np.array([11,44])
    W_start_turn0 = np.array([34.5,58])
    W_end_turn0 = np.array([34.5,44])
    
    pivot0_Q1 = np.array([65.5,66.5])
    pivot0_Q2 = np.array([34.5,66.5])
    pivot0_Q3 = np.array([34.4,34.5])
    pivot0_Q4 = np.array([65.5,34.5])
    
    short_turn_pts = 5
    long_turn_pts = 10
    
    
    
    # Images pre-loaded to block.
    
    # North
    block_N_image = plt.imread('__basik__/Images/stop_street/block_N.jpg')
    block_N_extent0 = np.array([24,67,64,100])
    
    # East
    block_E_image = plt.imread('__basik__/Images/stop_street/block_E.jpg')
    block_E_extent0 = np.array([63,100,24,68])
    
    # South
    block_S_image = plt.imread('__basik__/Images/stop_street/block_S.jpg')
    block_S_extent0 = np.array([33,67,0,36.5])

    # West
    block_W_image = plt.imread('__basik__/Images/stop_street/block_W.jpg')
    block_W_extent0 = np.array([0,36,32,68.3])
    
    stop_street_image = plt.imread('__basik__/Images/stop_street/all_entrances.png')

    
    #--------------------------------------------------------------------------
    
    def __init__(self,stop_street_object,
                      axes=None,
                      show=['N','E','S','W'],
                      car_length=10,car_width=5):
        
        '''
        Parameters:
        -----------
        stop_street_object: __basik__.StopStreetObject.stop_street.StopStreet
            The internal object that provides the mechanism for the
            simulation to follow. StopStreetDisplay object will display 
            the progress of this stop_street_object.  
        axes: matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes on which the display will be rendered. If set
            to None, one will be created along with self.figure.
        show: list
            In the stop_street_object not all entrances and exits exist
            i.e. they have been set to None. If this has been done then these
            directions should not be in the show list. 
            This list should not be empty.
            
        Raises:
        -------
        AssertionError:
            If stop_street_object is not an instance of
            __basik__.StopStreetObject.stop_street.StopStreet
        '''
        
        self.axes = axes
        
        assert isinstance(stop_street_object,StopStreet)
        
        self.stop_street_object = stop_street_object
        
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
        

    #--------------------------------------------------------------------------
    
    def turn_on_display(self):
        # All stop street entrances need to have a display object give.
        for node in self.stop_street_object.entrances:
            if node is not None and not isinstance(node,int):
                node.stop_street_display = self
        # Note that the exits must not contain the stop street as a display object.
        # They should have a Lane/Road as their display object.
        return None
    
    #--------------------------------------------------------------------------
    
    def turn_off_display(self):
        # All stop street entrance need to have display object as None.
        for node in self.stop_street_object.entrances:
            if node is not None:
                node.stop_street_display = None
        return None
    
    #--------------------------------------------------------------------------
    
    def setup_image(self):
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)
        self.axes.set_axis_off()
        self.image = self.stop_street_image
        
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
    
        self.tracks = np.array([[None,self.N_to_E,self.N_to_S,self.N_to_W],
                               [self.E_to_N,None,self.E_to_S,self.E_to_W],
                               [self.S_to_N,self.S_to_E,None,self.S_to_W],
                               [self.W_to_N,self.W_to_E,self.W_to_S,None]],
                     dtype = object)
        
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
    
    
    

#------------------------------------------------------------------------------
        
    


    
    
    
    
    
    
    
    
    
    