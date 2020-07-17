
import numpy as np
import matplotlib.pyplot as plt

from .obstruction import Obstruction
from .global_queue import Queue



#-------------------------------------------------------------------------------

class Node(object):
    
    '''Forms the discrete state-space along which vehicles move.
    
    Attributes:
    -----------
    occupied: bool
        Whether a node currently contains a vehicle. A node can only
        be occupied by one vehicle a time and a vehicle can only occupy one
        node at a time.
    vehicle: __basik__.VehicleObject.vehicle.Vehicle
        The vehicle that occupies the node.
    distance:
        The distance in meters between two successive, fully connected nodes.
    '''
    
    
    INTERNAL = True
    
    camera = plt.imread('__basik__/Images/camera.png')
    speedometer = plt.imread('__basik__/Images/speedometer.png')
    cone = plt.imread('__basik__/Images/cone.png')
    cone_round = plt.imread('__basik__/Images/cone_round.png')
    
    
    icon_shrink_factor = 0.95
    
    # Average length of a vehicle is 4.5 meter according to:
    # https://www.quora.com/What-is-the-average-length-of-a-car-in-feet
    # We place each vehicle with its center over the nodes. We would like
    # bumper-to-bumper vehicles (on adjacent nodes) to be 1 meter apart.
    # Hence, the distance between nodes will be this 1 meter plus half a car length
    distance = 4.5/2 + 1
    
    size = 1  # do not change this  !!!!!!!!!!!!!!!!!!!!
    
    def __init__(self,front=None,
                      behind=None,
                      left=None,
                      right=None):
        
        '''
        Parameters:
        -----------
        front: __basik__node.Node or None
            The next node that a vehicle will move to.
        behind: __basik__node.Node or None
            Previous node where a vehicle has been. This node can have its
            vehicle delayed by the vehicle of the current node.
        left: __basik__node.Node or None
            A circle exit is usually found here if the node is a circle exit
            node.
        right: __basik__node.Node or None
        
        NOTE: if a node is None and a vehicle moves onto it, then the vehicle
        will be disposed of after which it is no longer part of the simualtion.
        
        Raises:
        -------
        AssertionError:
            If front,behind,right or left is not either __basik__node.Node or None.
        '''
                          
        if self.size != 1:
            raise Exception('Do not change Node.size. Set Node.size = 1')
        
        
        if front is not None:
            assert isinstance(front,Node)
        if behind is not None:
            assert isinstance(behind,Node)
        if left is not None:
            assert isinstance(left,Node)
        if right is not None:
            assert isinstance(right,Node)
        
        self.front = front
        # NOTE: a node with front as None will act as a sink
        # Any vehicle on this Node will be propogated to None
        self.behind = behind
        self.left = left
        self.right = right
        # Occupied implies the node has a vehicle. 
        self.occupied = False
        self.vehicle = None
        # Out of service implies the node has no vehicle but can also not
        # be accessed to be occupied by a vehicle.
        # This allows for stop streets and various components to function.
        self.service_node = False
        self.locked = False  
        self.unlock_time = None
        
        self.road_display_object = None
        self.left_lane = False
        self.lane = None
        self.overflow_protection = False
        

        # Each component must be able to embed the display component into its nodes.
        self.stop_street = None
        self.stop_street_entrance = False
        self.stop_street_exit = False
        self.stop_street_display = None  # For vizualisation/display purposes
        
        self.source_attached = False
        self.source = None
        
        self.traffic_light = None
        self.traffic_light_entrance = False
        self.traffic_light_exit = False
        self.traffic_light_display = None  # For vizualisation/display purposes
        
        self.circle = None               # Circle object
        self.circle_entrance = False     # Performs entrance maneouvre
        self.circle_node = False         # Is part of internalc circle flow
        self.circle_exit = False         # Lies to the left of a circle_node
        self.circle_display = None
        self.circle_track_idx = None
        
        self.off_ramp = None
        self.off_ramp_entrance = False
        self.off_ramp_standard_entrance = False
        self.off_ramp_exit = False
        self.off_ramp_standard_exit = False
        self.off_ramp_display = None  # For vizualisation/display purposes
        
        self.on_ramp = None    # the on_ramp object itself
        self.on_ramp_node = False  # either main or sub flow entrance
        self.on_ramp_standard_node = False  # for the other lane which acts as standard
        self.sub_flow = False  # sub flow entrance which waits to join with main flow.
        self.on_ramp_exit = False
        self.on_ramp_display = None  # For vizualisation/display purposes
        
        self.obstruction = None
        self.obstructed = False
        self.contains_obstruction = False
        self.end_time = None
        
        self.record_object = None
        self.record = False
        
        self.idx = None   # the idx of entrance or exit that it might be
        
        self.velocity_change = False
        self.new_velocity = None
        
        
        
        # For displaying icons
        self.display_coord = None
        self.display_axes = None
        self.car_width = None
        self.car_length = None
        self.icon_image = None
        
        
        # Flared Traffic light
        self.flared_traffic_light = None
        self.flared_traffic_light_entrance = False
        self.flared_traffic_light_exit = False
        self.buffer_start = False
        self.buffer_end = False
        self.buffer_node = False
        self.flared_traffic_light_display = None
        
        
        # Intersection (Unstructured with main and subordinate flow)
        self.intersection = None
        self.intersection_entrance = False
        self.intersection_exit = False
        self.main_flow = False   # an entrance is either main flow 

        # Pedestrianc Crossing
        self.pedestrian_crossing = None
        self.pedestrian_crossing_entrance = False
        self.pedestrian_crossing_buffer_entrance = False
        self.pedestrian_crossing_exit = False
        self.pedestrian_crossing_buffer_exit = False
        self.pedestrian_crossing_display = None
        self.pedestrian_crossing_buffer_node = False
        

    #--------------------------------------------------------------------------
    
    def schedule_obstructions(self,start_times:list,durations:list,
                           duration_std=0.5):
        
        '''
        This obstructs a node and prevents any vehicle from entering it for
        the given duration scheduled. An example may include pedestrains or
        animals crossing a road.
        
        Parameters:
        -----------
        start_times: list
            Each nth obstruction in the list will start at this time.
        durations: list
            Each nth obstruction will continue for this duration approximately.
            The duration will be a Guassian distributed random variable with
            duration as its mean.
        durartion_std: float
            The standard deviation that will apply to the duration of all
            durations.
            
        Raises:
        AssertionError
            start_times and durations must be of the same length.
        TypeError:
            start_times and end_times are required to be lists.
            
        Returns:
        --------
        None
        '''
        if not isinstance(start_times,list):
            raise TypeError('start_times must be a list.')
        if not  isinstance(durations,list):
            raise TypeError('durations must be a list.')
        assert len(start_times) == len(durations)
        
        self.service_node = True
        self.contains_obstruction = True
        self.obstructed = False  # not obstructed yet
        self.icon_image = self.cone
        
        start_times.reverse()
        durations.reverse()
        
        while True:
            
            start_time = start_times.pop()
            duration = durations.pop()
            end_time = start_time + np.random.normal(duration,duration_std)
            # ensure that the end_time is indeed larger than the start_time
            while end_time <= start_time:
                end_time = start_time + np.random.normal(duration,duration_std)
            
            
            obstruction = Obstruction(start_time,end_time,
                                      obstruction_node=self)
            
            Queue.push(obstruction)
            
            if not bool(start_times):
                break
            
        return None
    
    #--------------------------------------------------------------------------
    
    def schedule_n_obstructions(self,n:int,
                                duration:float,
                                duration_std:float=0.1):
        '''
        This will obstruct n distinct vehicles for some given duration.
        An example may include each distinct vehicle briefly being obstructed
        by maneuvering around something such as a large pothole.
        
        Parameters:
        -----------
        n: int
            The amount of vehicles the obstruction will delay.
        duration: float
            Duration of the delay placed onto the vehicle.
        duration_std: float
            The duration of the delay/obstruction will be a Gaussian randomly
            distributed variable. This is the standard deviation.
            
        Raises:
        -------
        AssertionError
            n must be greater than 1 and the duration must be a positive value.
            
        Returns:
        --------
        None
        '''
        assert n >= 1
        assert duration > 0
        
        self.n_vehicles_obstructued = n
        self.count = 0
        self.service_node = True
        self.contains_obstruction = True
        self.obstructed = True
        self.last_seen_vehicle = None
        self.duration = duration 
        self.duration_std = duration_std
        
        if self.display_axes is not None:
            self.icon_image = self.cone_round
            self.display_icon()
        
        return None
    
    #--------------------------------------------------------------------------
    
    def count_obstruction(self,vehicle):
                
        self.count += 1
        self.last_seen_vehicle = vehicle
        self.end_time = vehicle.time + np.random.normal(self.duration,
                                                        self.duration_std)
        
        if self.count == self.n_vehicles_obstructued:
            self.service_node = False
            self.contains_obstruction = False
            self.obstructed = False
            delattr(self,'count')
            delattr(self,'n_vehicles_obstructued')
            delattr(self,'last_seen_vehicle')
            delattr(self,'duration')
            delattr(self,'duration_std')
            if self.display_axes is not None:
                self.hide_icon()
            
        
        return None
        

    #--------------------------------------------------------------------------
    
    def assign_velocity_change(self,velocity:'float (m/s)'):
        
        '''At this node, the average velocity of a vehicle will be changed.
        
        Parameters:
        -----------
        velocity: float
            The velocity that will be assigned to the vehicle that occupies the
            node. Units is in meters per second (m/s).
            
        Raises:
        -------
        AssertionError:
            velocity must be positive.
            
        Returns:
        --------
        None
        
        '''
        
        assert velocity > 0
        
        self.velocity_change = True
        self.new_velocity = velocity
        
        if self.display_axes is not None:
            self.icon_image = self.speedometer
            self.display_icon()
        
        return None
    
    
    #--------------------------------------------------------------------------
    
    @property
    def extent(self):
        
        return np.array([self.display_coord[0]-0.5*self.icon_shrink_factor*self.car_width,
                         self.display_coord[0]+0.5*self.icon_shrink_factor*self.car_width,
                         self.display_coord[1]-0.5*self.icon_shrink_factor*self.car_width,
                         self.display_coord[1]+0.5*self.icon_shrink_factor*self.car_width])
    
    #--------------------------------------------------------------------------
    
    def display_icon(self):
        
        self.icon_plot = self.display_axes.imshow(self.icon_image,
                                                  extent=self.extent)
        
        return None
    
    #--------------------------------------------------------------------------
        
    def hide_icon(self):
        
        # TODO: give flicker option
        if hasattr(self,'icon_plot'):
            self.icon_plot.remove()
        
        return None
    
    
    #--------------------------------------------------------------------------
        
        
    def __repr__(self):
        
        if hasattr(self,'n_vehicles_obstructued'):
            return 'Node with {0}/{1} vehicles obstructed ({2})'.format(
                    self.count,self.n_vehicles_obstructued,hex(id(self)))
        
        if (self.contains_obstruction and 
            not self.velocity_change):
            return 'Obstruction Node ({0})'.format(hex(id(self)))
        
        if (self.velocity_change and 
            not self.contains_obstruction):
            return 'Velocity Change Node ({0})'.format(hex(id(self)))
        
        if (self.velocity_change and 
            self.contains_obstruction):
            return 'Obstruction & Velocity Change Node ({0})'.format(hex(id(self)))
        
        
        
        return 'Node ({0})'.format(hex(id(self)))
        
#-------------------------------------------------------------------------------
