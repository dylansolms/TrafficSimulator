
import numpy as np
import matplotlib.pyplot as plt

from .on_ramp import OnRamp
from ..utils import rotate_coord
import scipy.ndimage as im

#------------------------------------------------------------------------------



class OnRampDisplay(object):
    
    '''Provides display for
    __basik__.OnRampObject.on_ramp.OnRamp
    using matplotlib.pyplot and the Qt5Agg backend.
    '''
    
    DISPLAY = True
    
    # We provide below the points used for calculations.

    width0 = 12.020815 # borrowed from OffRampDisplay.
    
    # We chose the below points to compute main_bearings
    bearing_pt1 = [89,89]
    bearing_pt2 = [82.7,76.6]
    
    main_bearings0 = 208.09768296743593
    sub_bearings0 = 270  # No 0 added as it will not be scaled or altered.
    
    main_entrance0 = np.array([89,89],dtype=np.float64)
    sub_entrance0 = np.array([88,52.5],dtype=np.float64)
    
    other_entrance0 = np.array([10.5,20],dtype=np.float64)
    other_exit0 = np.array([76.1,89.7],dtype=np.float64)
    other_bearings0 = 43.264295
    
    exit0 = np.array([20,11])
    
    sub_track0 = np.array([[88,52.5],
                           [71.4,52.5],
                           [65.2,51.5],
                           [58.6,49.8],
                           [54.5,46],
                           [36,28],
                           [20,11]],dtype=np.float64)
    
    main_track0 =np.array([[89,89],
                           [82.7,77.2],
                           [70,62],
                           [50,41],
                           [36,28],
                           [20,11]],dtype=np.float64)
    
    extent0 = np.array([0,100,0,100],dtype=np.float64)
    car_width = 5
    shrink = 0.9
    
    origin0 = np.array([50,50])   # in the center of extent0
    
    
    on_ramp_image = plt.imread('__basik__/Images/onramp.jpg')

    #--------------------------------------------------------------------------

    def __init__(self,on_ramp_object,
                      on_ramp_direction:'N,E,S or W'='E',
                      axes=None):
        
        '''
        Parameters:
        -----------
        on_ramp_object: __basik__.OnRampObject.on_ramp.OnRamp
            The internal object that provides the mechanism for the
            simulation to follow. OfnRampDisplay object will display 
            the progress of this off_ramp_object.  
        axes: matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes on which the display will be rendered. If set
            to None, one will be created along with self.figure.
        on_ramp_direction: str
            Choose either N,E,S or W.
            An on-ramp always has the sub-flow entrance between the main flow 
            entrance and the exit (which they both intend to use) when moving 
            clockwise i.e.
            on_ramp_direction = East means the sub-flow entrance is East, the
            main-flow entrance is North and that the exit which they both share
            would be South.

        Raises:
        -------
        AssertionError:
            If on_ramp_object is not an instance of
            __basik__.OnRampObject.on_ramp.OnRamp
        '''
        
        self.axes = axes
        
        assert isinstance(on_ramp_object,OnRamp)
        self.on_ramp_object = on_ramp_object
        
        self.setup_image()
        self.scale_all()
        self.allocate_bearings()
        self.setup_tracks()
        
        self.perform_rotation(on_ramp_direction)
        
        self.turn_on_display()
        
    #--------------------------------------------------------------------------
        
    def turn_on_display(self):
        
        for node in self.on_ramp_object.entrances:
            node.on_ramp_display = self
            
        self.on_ramp_object.other_entrance.on_ramp_display = self

        return None
    
    #--------------------------------------------------------------------------
    
    def turn_off_display(self):

        for node in self.on_ramp_object.entrances:
            node.on_ramp_display = None

        return None

            
    #--------------------------------------------------------------------------
        
    def setup_image(self):
        
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)
        
        self.axes.set_axis_off()
        self.image = self.on_ramp_image
        
        assert self.shrink < 1
        
        self.scale_factor = self.car_width/(self.shrink*self.width0)
        self.extent = self.extent0*self.scale_factor
        self.xlim = self.extent[1]
        self.ylim = self.extent[3]
        
        self.show()
        
        return None
    
    #--------------------------------------------------------------------------
    
    def scale_all(self):
        
        # On-ramp part
        self.main_track = self.main_track0*self.scale_factor
        self.sub_track = self.sub_track0*self.scale_factor
        self.main_entrance = self.main_entrance0*self.scale_factor
        self.sub_entrance = self.sub_entrance0*self.scale_factor
        self.exit = self.exit0*self.scale_factor
        
        # Standard lane
        self.other_entrance = self.other_entrance0*self.scale_factor
        self.other_exit = self.other_exit0*self.scale_factor
        
        # For rotation purposes
        self.origin = self.origin0*self.scale_factor
        
        return None
    
    #--------------------------------------------------------------------------
    
    def allocate_bearings(self):
        
        self.main_entrance_bearings = self.main_bearings0
        self.main_bearings = self.main_bearings0
        self.sub_entrance_bearings = self.sub_bearings0
        self.sub_bearings = self.sub_bearings0
        self.other_bearings = self.other_bearings0
        self.other_entrance_bearings = self.other_bearings0
        
        return None
        
    
    #--------------------------------------------------------------------------
    
    def setup_tracks(self):
        
        self.tracks = [self.main_track,self.sub_track]
        self.entrances = [self.main_entrance,self.sub_entrance]
        self.keys = ['MAIN','SUB']
        self.idxs = [0,1]
        
        return None
    
    #--------------------------------------------------------------------------
    
    def show(self):
        
        self.image_plot = self.axes.imshow(self.image,extent=self.extent)
        self.axes.set_xlim(0,self.xlim)
        self.axes.set_ylim(0,self.ylim)
        
        try:
            self.figure.show()
        except AttributeError:
            plt.show()

        return None
    
    #--------------------------------------------------------------------------
    
    def hide(self):
        
        if hasattr(self,'image_plot'):
            try:
                self.image_plot.remove()
            except ValueError:
                # ValueError: list.remove(x): x not in list
                pass

        return None
    
    #--------------------------------------------------------------------------
    
    def rotate(self,degrees:'clockwise'):
        
        # Rotate tracks about the middle of the extent/middle of the image.
        
        # NOTE: it rotates the current image. If you rotate it twice then the
        # second rotation uses the first rotated image as a reference

        new_sub_track = np.zeros(self.sub_track.shape)
        new_main_track = np.zeros(self.main_track.shape)
        
        rot = lambda coord: rotate_coord(origin=self.origin,
                                         coord=coord,
                                         angle=degrees)
        
        
        for idx,coord in enumerate(self.sub_track):
            new_sub_track[idx] = rot(coord)
        for idx,coord in enumerate(self.main_track):
            new_main_track[idx] = rot(coord)
            
        self.sub_entrance = np.array(rot(self.sub_entrance))
        self.main_entrance = np.array(rot(self.main_entrance))
        self.exit = np.array(rot(self.exit))
        self.sub_track = new_sub_track
        self.main_track = new_main_track
        
        self.other_entrance = np.array(rot(self.other_entrance))
        self.other_exit = np.array(rot(self.other_exit))
        
        # Rotate the image about its center
        self.hide()
        self.image = im.rotate(self.image,-degrees,reshape=True)
        self.show()
        
        # Adjust the bearings
        self.main_bearings = (self.main_bearings + degrees)%360
        self.main_entrance_bearings = self.main_bearings
        self.sub_bearings = (self.sub_bearings + degrees)%360
        self.sub_entrance_bearings = self.sub_bearings
        self.other_bearings = (self.other_bearings + degrees)%360
        self.other_entrance_bearings = self.other_bearings
        
        return None
    
    #--------------------------------------------------------------------------
    
    def perform_rotation(self,on_ramp_direction):
        self.on_ramp_direction = on_ramp_direction
        
        if (on_ramp_direction == 'E' or
            on_ramp_direction == 'East'):
            # Standard setting results in no adjustmenton_ramp_direction.
            pass
        elif (on_ramp_direction == 'S' or
             on_ramp_direction == 'South'):
            self.rotate(90)
        elif (on_ramp_direction == 'W' or
             on_ramp_direction == 'West'):
            self.rotate(180)
        elif (on_ramp_direction == 'N' or
             on_ramp_direction == 'North'):
            self.rotate(270)
        else:
            raise ValueError('off_ramp_direction must be either: '+
                             'N,E,S,W or North,East,South,West'+
                             ' as a string')
        
        return None
    
#------------------------------------------------------------------------------
  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    