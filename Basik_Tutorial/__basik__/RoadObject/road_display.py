


import numpy as np
from scipy.ndimage import rotate
import matplotlib.pyplot as plt
from copy import deepcopy

from .lane import Lane


#------------------------------------------------------------------------------

class RoadDisplay(object):
    
    '''Displays a road with two lanes travelling in opposite directions.
    '''
    
    DISPLAY = True
    
    spacing = 1.5  # space between nodes and/or vehicles.
    car_len = 10
    car_width = 5
    edges = 2   # space between car's rear or front as it nears the beginning 
                # or end of the road.
    middle_space = 0.5  # space between cars as the pass
    side_space = 0.5   # space between vehicle and side-border of road
    
    prob_trees = 0.7  # probability of displaying trees
    
    
    road_image = plt.imread('__basik__/Images/road.jpg')
    trees_image = plt.imread('__basik__/Images/road_side_trees.jpg')
    buildings_image = plt.imread('__basik__/Images/road_side_buildings.jpg')
    field = plt.imread('__basik__/Images/farm_field.jpg')
    
    #--------------------------------------------------------------------------

    
    def __init__(self,left_lane=None,right_lane=None,
                      axes=None,
                      horizontal=True,
                      square_image=True):
        
        '''
        Parameters:
        -----------
        left_lane: __basik__.RoadObject.lane.Lane or None
            If horizontal is True then this lane moves from West to East.
            If False, then it moves from South to North.
            If set to None, then a __basik__.RoadObject.lane.Lane will be
            created with the same length as the provided lane.
        right_lane: __basik__.RoadObject.lane.Lane or None
            If horizontal is True then this lane moves from East to West.
            If False, then it moves from North to South.
            If set to None, then a __basik__.RoadObject.lane.Lane will be
            created with the same length as the provided lane.
        horizontal: bool
            Orientation setting of the display.
        axes: matplotlib.axes._subplots.AxesSubplot
            The axes on which the display will be rendered.
        square_image: bool
            If set to True, then the display will have an extent of square
            proportions. This makes tiling components (all of which are square)
            convenient in order to build a basic simulation display. Setting it
            to False results in a display which may be slender.
        Raises:
        -------
        ValueError:
            At least on lane must not be None.
            
        '''
        
        self.axes = axes
        
        if left_lane is not None and right_lane is not None:
            left_lane.length == right_lane.length
        elif left_lane is not None and right_lane is None:
            right_lane = Lane(left_lane.length)
        elif left_lane is None and right_lane is not None:
            left_lane = Lane(right_lane.length)
        else:
            raise ValueError('At least one lane as to be specified')
       
        self.length = left_lane.length
        
        self.left_lane = left_lane
        self.right_lane = right_lane
        self.horizontal = horizontal
        
        self.setup_image()
        self.setup_left_lane()
        self.setup_right_lane()
        self.build_track()
        self.give_lanes_track_coords()
        
        if square_image:
            self.make_image_square()
        
        
        
    #--------------------------------------------------------------------------

    
    def make_image_square(self):
        
        n_nodes = self.length
        n_images = n_nodes//10 + 1  # for every multiple of 10 we have an image break
        delta = self.road_length/n_images
        


        # This needs to be implemented to allow for the image to be tiled
        # instead of stretched.
        
        if self.horizontal:
            x = self.extent[3]  # width
            y = self.extent[1]  # length
            z = (y-3*x)/2
            extent1 = np.array([0,delta,2*x,2*x+z])
            extent2 = np.array([0,delta,-x-z,-x])
            xlim = [0,y]
            ylim = [-x-z,2*x+z]
            image = self.field
            for nth_image in range(n_images):
                self.axes.imshow(image,extent=list(extent1))
                self.axes.imshow(image,extent=list(extent2))
                extent1[0] += delta
                extent1[1] += delta
                extent2[0] += delta
                extent2[1] += delta
            
        else:
            x = self.extent[1]  # width
            y = self.extent[3]  # length
            z = (y-3*x)/2
            extent1 = np.array([2*x,2*x+z,0,delta])
            extent2 = np.array([-x-z,-x,0,delta])
            xlim = [-x-z,2*x+z]
            ylim = [0,y]
            image = rotate(self.field,90)
            for nth_image in range(n_images):
                self.axes.imshow(image,extent=list(extent1))
                self.axes.imshow(image,extent=list(extent2))
                extent1[2] += delta
                extent1[3] += delta
                extent2[2] += delta
                extent2[3] += delta

                
        self.axes.set_xlim(*xlim)
        self.axes.set_ylim(*ylim)
        
        
        return None
            
    #--------------------------------------------------------------------------
        
        
    
    def setup_image(self):
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)
        self.axes.set_axis_off()
        
        
        self.space_between_vehicles = self.spacing + self.car_len
        
#        self.road_len = (self.length-1)*self.spacing + self.car_len + 2*self.edges
        
        self.road_len = (self.length-1)*self.space_between_vehicles +\
                        self.car_len + 2*self.edges
        self.road_width = 2*self.car_width + self.middle_space +\
                          2*self.side_space
        
        image = self.road_image
        
        trees = self.trees_image
        buildings = self.buildings_image
        
        if self.horizontal:
            self.image = image
            self.extent = [0,self.road_len,0,self.road_width]
            self.xlim = [0,self.road_len]
            self.ylim = [-2*self.road_width,2*self.road_width]
            self.trees_left = trees  # top
            self.trees_right = rotate(trees,180)  # bottom
            self.buildings_left = rotate(buildings,180) # top
            self.buildings_right = buildings # bottom
            
        else:
            self.image = rotate(image,90)
            self.extent = [0,self.road_width,0,self.road_len]
            self.xlim = [-2*self.road_width,2*self.road_width]
            self.ylim = [0,self.road_len]
            self.trees_left = rotate(trees,90)
            self.trees_right = rotate(trees,270)
            self.buildings_left = rotate(buildings,270)
            self.buildings_right = rotate(buildings,90)
            
        
        # One can close it again.
        # !!!!:
        # See below for how to hide an entire plot
        # https://stackoverflow.com/questions/14629438/hide-invisible-matplotlib-figure/43520985#43520985
        
        self.road_length = self.road_len  # for convenience.
        self.show()
        
        return None
    
    #--------------------------------------------------------------------------
    
    def setup_left_lane(self):
        
        # Below we use 0.5 as we are interested in the center of the car.
        # Note: we also want the vehicle to be in the left lane.
        delta1 = self.edges + 0.5*self.car_len
        delta2 = self.side_space + 0.5*self.car_width
        
        if self.horizontal:
            self.left_entrance = np.array([delta1,
                                           self.road_width-delta2])
            self.left_exit = np.array([self.road_len-delta1,
                                       self.road_width-delta2])
#            self.left_lane.bearings = 90
            self.left_bearings = 90
        else:
            self.left_entrance = np.array([delta2,
                                           delta1])
            self.left_exit = np.array([delta2,
                                       self.road_len-delta1])
#            self.left_lane.bearings = 0
            self.left_bearings = 0
    
        # FOR DISPLAY
        self.left_lane.in_node.road_display_object = self
        self.left_lane.in_node.left_lane = True
        
        return None
    
    #--------------------------------------------------------------------------
    
    def setup_right_lane(self):
        
        # Below we use 0.5 as we are interested in the center of the car.
        # Note: we also want the vehicle to be in the left lane.
        delta1 = self.edges + 0.5*self.car_len
        delta2 = self.side_space + 0.5*self.car_width
        
        if self.horizontal:
            self.right_entrance = np.array([self.road_len-delta1,
                                            delta2])
            self.right_exit = np.array([delta1,
                                        delta2])
#            self.right_lane.bearings = 270
            self.right_bearings = 270
            
        else:
            self.right_entrance = np.array([self.road_width-delta2,
                                            self.road_len-delta1])
            self.right_exit = np.array([delta2,
                                        delta1])
#            self.right_lane.bearings = 180
            self.right_bearings = 180
        
        # FOR DISPLAY
        self.right_lane.in_node.road_display_object = self
        self.right_lane.in_node.left_lane = False

        return None
        
    
    #--------------------------------------------------------------------------
    
    def show(self):
        
        #NEW: we attach images instead if stretching a single image.
        n_nodes = self.length
        n_images = n_nodes//10 + 1  # for every multiple of 10 we have an image break
        
        x0 = 0
        delta = self.road_length/n_images
        x1 = delta
        
        if self.horizontal:
            idx0 = 0   
            idx1 = 1
            idx0_ = 2  
            idx1_ = 3  
            shift = self.road_width
        else:
            idx0 = 2
            idx1 = 3
            idx0_ = 0  
            idx1_ = 1
            shift = - self.road_width
        
        for nth_image in range(n_images):
            # Plot road image
            scaled_extent = deepcopy(self.extent)
            scaled_extent[idx0] = x0
            scaled_extent[idx1] = x1
            self.axes.imshow(self.image,extent=scaled_extent)
            
            left_choice1 = np.random.choice(a=['trees','buildings'],
                                            p=[self.prob_trees,1-self.prob_trees])
            
            
            left_extent1 = deepcopy(scaled_extent)
            
            # Shift the extent up
            left_extent1[idx0_] += shift
            left_extent1[idx1_] += shift
            left_extent1[idx1] -= 0.5*delta 
            
            if left_choice1 == 'trees':
                self.axes.imshow(self.trees_left,extent=left_extent1)
            else:
                self.axes.imshow(self.buildings_left,extent=left_extent1)
            
            
            left_choice2 = np.random.choice(a=['trees','buildings'],
                                            p=[self.prob_trees,1-self.prob_trees])
            
            left_extent2 = deepcopy(scaled_extent)
            left_extent2[idx0_] += shift
            left_extent2[idx1_] += shift
            left_extent2[idx0] += 0.5*delta
            
            if left_choice2 == 'trees':
                self.axes.imshow(self.trees_left,extent=left_extent2)
            else:
                self.axes.imshow(self.buildings_left,extent=left_extent2)
            
            
            right_choice1 = np.random.choice(a=['trees','buildings'],
                                             p=[self.prob_trees,1-self.prob_trees])
            
            right_extent1 = deepcopy(scaled_extent)
            # Shift the extent down
            right_extent1[idx0_] -= shift
            right_extent1[idx1_] -= shift
            right_extent1[idx1]  -= 0.5*delta 
            
            if right_choice1 == 'trees':
                self.axes.imshow(self.trees_right,extent=right_extent1)
            else:
                self.axes.imshow(self.buildings_right,extent=right_extent1)
            
            right_choice2 = np.random.choice(a=['trees','buildings'],
                                             p=[self.prob_trees,1-self.prob_trees])
            
            right_extent2 = deepcopy(scaled_extent)
            right_extent2[idx0_] -= shift
            right_extent2[idx1_] -= shift
            right_extent2[idx0] += 0.5*delta
            
            if right_choice2 == 'trees':
                self.axes.imshow(self.trees_right,extent=right_extent2)
            else:
                self.axes.imshow(self.buildings_right,extent=right_extent2)
            

            x0 += delta
            x1 += delta
            

        # OLD: simply stretched a single image.
#        self.axes.imshow(self.image,extent=self.extent)
        
        
        self.axes.set_xlim(*self.xlim)
        self.axes.set_ylim(*self.ylim)
        
        try:
            self.figure.show()
        except AttributeError:
            plt.show()
    
        
        return None
        
        
    #--------------------------------------------------------------------------
    
    
    def build_track(self):
        
        left_coord = self.left_entrance.tolist()
        right_coord = self.right_entrance.tolist()
        
        self.left_track = [left_coord]
        self.right_track = [right_coord]
        
        if self.horizontal:
#            delta = [self.spacing,0]
            delta = [self.space_between_vehicles,0]
        else:
#            delta = [0,self.spacing]
            delta = [0,self.space_between_vehicles]
            
        for n in range(self.length):
#        for n in range(self.length-1):
            # We use add and subtract as we would like to maintain
            # left_coord and right_coord as lists but still want matrix
            # arithmetic.
            left_coord = np.add(left_coord,delta).tolist() 
            self.left_track.append(left_coord)
            right_coord = np.subtract(right_coord,delta).tolist()
            self.right_track.append(right_coord)
            
        # Append None to notify that simulator that the end of the track has
        # been reached.
#        self.left_track.append(None)
#        self.right_track.append(None)
            
        return None
    
    
    
    #--------------------------------------------------------------------------
    
    def give_lanes_track_coords(self):
        
        for idx in range(len(self.left_lane.nodes)):
            
            self.left_lane.nodes[idx].display_coord = self.left_track[idx]
            self.left_lane.nodes[idx].display_axes = self.axes
            self.left_lane.nodes[idx].car_width = self.car_width
            self.left_lane.nodes[idx].car_length = self.car_len
            
            self.right_lane.nodes[idx].display_coord = self.right_track[idx]
            self.right_lane.nodes[idx].display_axes = self.axes
            self.right_lane.nodes[idx].car_width = self.car_width
            self.right_lane.nodes[idx].car_length = self.car_len
            
        return None
    

            
    #--------------------------------------------------------------------------
    
    

        
#------------------------------------------------------------------------------
