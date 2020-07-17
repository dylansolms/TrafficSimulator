






import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import rotate

from ..utils import rotate_all_coords,rotate_coord
from .pedestrian_crossing import PedestrianCrossing

#------------------------------------------------------------------------------


class PedestrianCrossingDisplay(object):
    
    '''Provides display for
    __basik__.PedestrianCrossingObject.pedestrian_crossing.PedestrianCrossing
    using matplotlib.pyplot and the Qt5Agg backend.
    '''
    
    DISPLAY = True
    
    
    # All coordinates are based on a standardised imaged where we set the
    # extent to [0,100,0,100] and read off the below positions from that plot.
    
    standard_car_length = 7 # length of car when extent is [0,100,0,100].
    standard_car_width = 3.5
    
    shrink = 1.0 # Further shrinking of the vehicle.
    extent0 = np.array([0,100,0,100])   # the image is based on this extent.
    origin0 = np.array([50,50]) # center of the standard image/extent
    
    # Pre-load umbrellas/pedestrians
    u1 = plt.imread('__basik__/Images/umbrella1.png')
    u2 = plt.imread('__basik__/Images/umbrella2.png')
    u3 = plt.imread('__basik__/Images/umbrella3.png')
    
    u_coords0 = np.array([[45,55],
                          [52,52],
                          [50,42],
                          [53.5,58],
                          [47.5,47.5],
                          [50,64],
                          [57,37]])
    u_image = [u1,u2,u3,u3,u2,u1,u1]
    u_size0 = 3
    
    
    
    W_to_E_track0 = np.array([[ 6. , 54.5],
                              [14. , 54.5],
                              [22. , 54.5],
                              [30. , 54.5],
                              [38. , 54.5],
                              [62. , 54.5],
                              [70. , 54.5],
                              [78. , 54.5],
                              [86. , 54.5],
                              [94. , 54.5]])
    
    E_to_W_track0 = np.array([[94. , 45.5],
                              [86. , 45.5],
                              [78. , 45.5],
                              [70. , 45.5],
                              [62. , 45.5],
                              [38. , 45.5],
                              [30. , 45.5],
                              [22. , 45.5],
                              [14. , 45.5],
                              [ 6. , 45.5]])
    
    W_to_E_bearings0 = 90
    E_to_W_bearings0 = 270


    pedestrian_crossing_image = plt.imread('__basik__/Images/pedestrian_crossing.jpg')
    
    #--------------------------------------------------------------------------
    
    def __init__(self,pedestrian_crossing_object,
                      axes=None,
                      car_length=10,car_width=5,
                      horizontal=True):
        
        '''
        Parameters:
        -----------
        pedestrian_crossing_object: __basik__.PedestrianCrossingObject.pedestrian_crossing.PedestrianCrossing
            The internal object that provides the mechanism for the
            simulation to follow. PedestrianCrossingDisplay object will display 
            the progress of this pedestrian_crossing_object.  
        axes: matplotlib.axes._subplots.AxesSubplot
            The matplotlib axes on which the display will be rendered. If set
            to None, one will be created along with self.figure.
        horizontal: bool
            The standard setting is horizontal. If set to False then we have a
            vertical setting that results from rotating the horizontal image by
            90 degrees in a clockwise direction about the center of the image.
            
        Raises:
        -------
        AssertionError:
            If pedestrian_crossing_object is not an instance of
            __basik__.PedestrianCrossingObject.pedestrian_crossing.PedestrianCrossing
        '''
        
        self.axes = axes
        
        assert isinstance(pedestrian_crossing_object,PedestrianCrossing)
        self.pedestrian_crossing_object = pedestrian_crossing_object
        
        self.car_length = car_length
        self.car_width = car_width
        
        if horizontal:
            self.rotate_90 = False
            self.horizontal = True
        else:
            self.rotate_90 = True  # rotate it 90 degrees clockwise.
            self.horizontal = False
        
        self.setup_image() # determine scale factor
        self.scale_all()   # apply the scale factor
        self.rotate_all()
        
        self.umbrella_display_objects = []
        self.turn_on_display()
        
            
    
    #--------------------------------------------------------------------------
    
    def turn_on_display(self):
        
        self.pedestrian_crossing_object.W_to_E_entrance.pedestrian_crossing_display = self
        self.pedestrian_crossing_object.E_to_W_entrance.pedestrian_crossing_display = self   
        self.pedestrian_crossing_object.display = self

        return None
    
    #--------------------------------------------------------------------------
    
    def turn_off_display(self):

        self.pedestrian_crossing_object.W_to_E_entrance.pedestrian_crossing_display = None
        self.pedestrian_crossing_object.E_to_W_entrance.pedestrian_crossing_display = None   
        self.pedestrian_crossing_object.display = None
        
        return None

    #--------------------------------------------------------------------------
    
    def setup_image(self):
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)
        self.axes.set_axis_off()

        self.image = self.pedestrian_crossing_image
        
        if self.rotate_90:
            # Rotate image 90 degrees clockwise around its center [50,50]
            self.image = rotate(self.image,-90)
        
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

        # West to East 
        self.W_to_E_track = self.W_to_E_track0*self.scale_factor
        self.W_to_E_entrance = self.W_to_E_track[0]
        self.W_to_E_exit = self.W_to_E_track[-1]
        self.W_to_E_before_crossing = self.W_to_E_track[4]
        self.W_to_E_after_crossing = self.W_to_E_track[5]
        
        # East to West
        self.E_to_W_track = self.E_to_W_track0*self.scale_factor
        self.E_to_W_entrance = self.E_to_W_track[0]
        self.E_to_W_exit = self.E_to_W_track[-1]
        self.E_to_W_before_crossing = self.E_to_W_track[4]
        self.E_to_W_after_crossing = self.E_to_W_track[5]
        
        # Umbrellas/pedestrians
        self.u_coords = self.u_coords0*self.scale_factor
        self.u_size = self.u_size0*self.scale_factor
        
        # Scale center/origin. Important for rotation purposes.
        self.origin = self.origin0*self.scale_factor

        return None
    
    #--------------------------------------------------------------------------
    
    def rotate_all(self):
        
        if self.rotate_90:
            
            # West to East
            self.W_to_E_track = rotate_all_coords(coords=self.W_to_E_track,
                                                  angle=90,
                                                  origin=self.origin)
            self.W_to_E_entrance = np.array(rotate_coord(coord=self.W_to_E_entrance,
                                                         angle=90,
                                                         origin=self.origin))
            self.W_to_E_exit = np.array(rotate_coord(coord=self.W_to_E_exit,
                                                         angle=90,
                                                         origin=self.origin))
            self.W_to_E_before_crossing = np.array(rotate_coord(coord=self.W_to_E_before_crossing,
                                                         angle=90,
                                                         origin=self.origin))
            self.W_to_E_after_crossing = np.array(rotate_coord(coord=self.W_to_E_after_crossing,
                                                         angle=90,
                                                         origin=self.origin))
            
            # East to West
            self.E_to_W_track = rotate_all_coords(coords=self.E_to_W_track,
                                                  angle=90,
                                                  origin=self.origin)
            self.E_to_W_entrance = np.array(rotate_coord(coord=self.E_to_W_entrance,
                                                         angle=90,
                                                         origin=self.origin))
            self.E_to_W_exit = np.array(rotate_coord(coord=self.E_to_W_exit,
                                                         angle=90,
                                                         origin=self.origin))
            self.E_to_W_before_crossing = np.array(rotate_coord(coord=self.E_to_W_before_crossing,
                                                         angle=90,
                                                         origin=self.origin))
            self.E_to_W_after_crossing = np.array(rotate_coord(coord=self.E_to_W_after_crossing,
                                                         angle=90,
                                                         origin=self.origin))
            
            # Umbrellas/pedestrians
            self.u_coords = rotate_all_coords(coords=self.u_coords,
                                              angle=90,
                                              origin=self.origin)
            
            # Bearings 
            self.W_to_E_bearings = self.W_to_E_bearings0 + 90
            self.E_to_W_bearings = self.E_to_W_bearings0 + 90
            
            
        else:
            self.W_to_E_bearings = self.W_to_E_bearings0
            self.E_to_W_bearings = self.E_to_W_bearings0
            
        return None
    
    #--------------------------------------------------------------------------
    
    def show_pedestrians(self):
        
        self.umbrella_display_objects.clear()
        
        for idx,umbrella in enumerate(self.u_image):
            umbrella_display_object = self.axes.imshow(umbrella,
                                      extent=self.get_extent(self.u_coords[idx]))
            self.umbrella_display_objects.append(umbrella_display_object)

        return None
    
    #--------------------------------------------------------------------------
    
    def hide_pedestrians(self):
        
        for umbrella_display_object in self.umbrella_display_objects:
            umbrella_display_object.remove()
            
        return None
        
    #--------------------------------------------------------------------------
    
    def get_extent(self,coord):
        out = np.zeros(4)
        out[0] = coord[0] - 0.5*self.u_size
        out[1] = coord[0] + 0.5*self.u_size
        out[2] = coord[1] - 0.5*self.u_size
        out[3] = coord[1] + 0.5*self.u_size
        return out
    

#------------------------------------------------------------------------------
    
    
    
    
    
    
    
    

    