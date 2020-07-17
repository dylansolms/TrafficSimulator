
import numpy as np
import matplotlib.pyplot as plt

from .off_ramp import OffRamp

# Use these to rotate the off ramp
from ..utils import rotate_coord
import scipy.ndimage as im

#------------------------------------------------------------------------------

class OffRampDisplay(object):
    
    '''Provides display for
    __basik__.OffRampObject.off_ramp.OffRamp
    using matplotlib.pyplot and the Qt5Agg backend.
    '''
    
    DISPLAY = True
    
    # We provide below the points used for calculations.
    width_pt1 = [60,23.5]
    width_pt2 = [68.5,32]
    width0 = 12.020815 # This will be used for scaling purposes.
    bearing_pt1 = [80,11]
    bearing_pt2 = [60,32]
    bearings0 = 316.397181  # No 0 added as it will not be scaled or altered.
    
    entrance0 = np.array([80,11],dtype=np.float64)
    
    other_entrance0 = np.array([25,90],dtype=np.float64)
    other_exit0 = np.array([91.5,18.5],dtype=np.float64)
    other_bearings0 = 137.075026
    
    
    off_track0 = np.array([[80,11],
                           [50,43.5],
                           [43.5,48.5],
                           [35,52.5],
                           [27,52.5],
                           [11,52.5]],dtype=np.float64)
    
    on_track0 =np.array([[80,11],
                         [50,43.5],
                         [27,67],
                         [11.4,88.4]],dtype=np.float64)
    
    extent0 = np.array([0,100,0,100],dtype=np.float64)
    car_width = 5
    shrink = 0.9
    
    origin0 = np.array([50,50])   # in the center of extent0
    
    off_ramp_image = plt.imread('__basik__/Images/offramp.jpg')

    #--------------------------------------------------------------------------

    def __init__(self,off_ramp_object,
                      off_ramp_direction:'N,E,S or W'='W',
                      axes=None):
        
        '''
        Parameters:
        -----------
        off_ramp_object: __basik__.OffRampObject.off_ramp.OffRamp
            The internal object that provides the mechanism for the
            simulation to follow. OffRampDisplay object will display 
            the progress of this off_ramp_object.  
        axes: matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes on which the display will be rendered. If set
            to None, one will be created along with self.figure.
        off_ramp_direction: str
            Choose either N,E,S or W.
            An off-ramp always has the off-ramp exit between the main flow 
            entrance and exit when moving clockwise i.e.
            off_ramp_direction = West means the entrance is South and the main 
            flow exit is North.
        Raises:
        -------
        AssertionError:
            If off_ramp_object is not an instance of
            __basik__.OffRampObject.off_ramp.OffRamp
        '''
        
        # NOTE: off ramp always has the off ramp exit between the main flow 
        # entrance and exit when moving clockwise i.e.
        # off_ramp_direction = West means the entrance is South and the main flow
        # exit is North.
        # Note that West is the standard setting of the display.
        
        self.axes = axes
        
        assert isinstance(off_ramp_object,OffRamp)
        self.off_ramp_object = off_ramp_object
        
        self.setup_image()
        self.scale_all()
        self.allocate_bearings()
        self.setup_tracks()
    
        self.perform_rotation(off_ramp_direction)
        
        self.turn_on_display()
        
    #--------------------------------------------------------------------------
    
    def turn_on_display(self):
            
        self.off_ramp_object.entrance.off_ramp_display = self
        self.off_ramp_object.other_entrance.off_ramp_display = self

        return None
    
    #--------------------------------------------------------------------------
    
    def turn_off_display(self):

        self.off_ramp_object.entrance.off_ramp_display = None
        self.off_ramp_object.other_entrance.off_ramp_display = None
        
        return None
            
    #--------------------------------------------------------------------------
        
    def setup_image(self):
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)

        self.axes.set_axis_off()
        self.image = self.off_ramp_image
        
        assert self.shrink < 1
        
        self.scale_factor = self.car_width/(self.shrink*self.width0)
        self.extent = self.extent0*self.scale_factor
        self.xlim = self.extent[1]
        self.ylim = self.extent[3]
        
        self.show()
        
        return None
    
    #--------------------------------------------------------------------------
    
    def scale_all(self):
        
        # For the actual off ramp part
        self.off_track = self.off_track0*self.scale_factor
        self.on_track = self.on_track0*self.scale_factor
        self.entrance = self.entrance0*self.scale_factor
        
        # For the normal lane
        self.other_entrance = self.other_entrance0*self.scale_factor
        self.other_exit = self.other_exit0*self.scale_factor
        
        # For rotation purposes
        self.origin = self.origin0*self.scale_factor
        
        return None
    
    #--------------------------------------------------------------------------
    
    def allocate_bearings(self):
        
        self.bearings = self.bearings0  # No scaling
        self.entrance_bearings = self.bearings0  # obvious naming which allows
        # the class instance to be inspected via OffRampDisplay().__dict__
        self.other_bearings = self.other_bearings0
        self.other_entrance_bearings = self.other_bearings0
        
        return None
        
    #--------------------------------------------------------------------------
    
    def setup_tracks(self):
        
        self.tracks = [self.off_track,self.on_track]
        self.keys = ['OFF','ON']
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
        
        # For the off ramp part
        new_off_track = np.zeros(self.off_track.shape)
        new_on_track = np.zeros(self.on_track.shape)
        
        rot = lambda coord: rotate_coord(origin=self.origin,
                                         coord=coord,
                                         angle=degrees)
        
        for idx,coord in enumerate(self.off_track):
            new_off_track[idx] = rot(coord)
        for idx,coord in enumerate(self.on_track):
            new_on_track[idx] = rot(coord)
            
        self.entrance = np.array(rot(self.entrance))
        self.off_track = new_off_track
        self.on_track = new_on_track
        
        # For the other standard non-offramp part
        self.other_entrance = np.array(rot(self.other_entrance))
        self.other_exit = np.array(rot(self.other_exit))
        
        # Rotate the image about its center
        self.hide()
        self.image = im.rotate(self.image,-degrees,reshape=True)
        self.show()
        
        # Adjust the bearings
        self.bearings = (self.bearings + degrees)%360
        self.entrance_bearings = self.bearings
        self.other_bearings = (self.other_bearings + degrees)%360
        self.other_entrance_bearings = self.other_bearings
        
        return None
    
    #--------------------------------------------------------------------------
    
    def perform_rotation(self,off_ramp_direction):
        self.off_ramp_direction = off_ramp_direction
        
        if (off_ramp_direction == 'W' or
            off_ramp_direction == 'West'):
            # Standard setting results in no adjustment.
            pass
        elif (off_ramp_direction == 'N' or
             off_ramp_direction == 'North'):
            self.rotate(90)
        elif (off_ramp_direction == 'E' or
             off_ramp_direction == 'East'):
            self.rotate(180)
        elif (off_ramp_direction == 'S' or
             off_ramp_direction == 'South'):
            self.rotate(270)
        else:
            raise ValueError('off_ramp_direction must be either: '+
                             'N,E,S,W or North,East,South,West'+
                             ' as a string')
        
        return None
            
    
#------------------------------------------------------------------------------
  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    