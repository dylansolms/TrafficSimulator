

import numpy as np
from ..global_queue import Queue
#from ..current_queue import Queue

from copy import deepcopy

from .vehicle_display import VehicleDisplay

from ..RoadObject.road_display import RoadDisplay

from ..CircleObject import CircleDisplay

# Import these to extract default size information
#from Types import (Node,OffRamp,OnRamp,TrafficLight,StopStreet,
#                   FlaredTrafficLight,Intersection)
from ..node import Node
from ..CircleObject import Circle
from ..OffRampObject import OffRamp
from ..OnRampObject import OnRamp
from ..TrafficLightObject import TrafficLight
from ..StopStreetObject import StopStreet
#from source import Source
from ..FlaredTrafficLightObject import FlaredTrafficLight
from ..IntersectionObject import Intersection
#from pedestrian_crossing import PedestrianCrossing


#import matplotlib.pyplot as plt
#-------------------------------------------------------------------------------

# shake

class Vehicle(object):
    
    '''Vehicles move forward by occupying nodes and interact with eachother as
    well as other components in the simulation. The purpose of a simulation
    is to study the flow of vehicles through the specidied setting/environment.
    
    One can regard a vehicle as a basic agent that interacts with its immediate
    environment as is capable of some basic planning as to avoid collisions.
    
    Attributes:
    ------------
    delay_time: float
        A vehicle takes a certain amount of time to move from one node to 
        another. This time can be extracted from self.move_duration which gives
        the duration of the vehicle's last move. This duration depends 
        primarily on the velocity. However, a vehicle must be able to react to
        changes in its environment. This is usually delayed e.g. realising one
        can move again at a stop street after halting. Hence, a small delay 
        can be incurred. It is distributed as
        delay = numpy.random.uniform(1e-3,delay_time)
    std: float
        The current velocity of a vehicle is a Gaussian distributed random
        variable. This is the standard deviation that vehicles will experience
        in their velocity due to process noise.
    look_ahead: int
        A vehicle is a basic agent that interacts with its environment and other
        agents. As such, it needs to have a sense of planning.
        look_ahead will be defined as the maximum number of empty (unoccupied)
        nodes that a vehicle is willing to pass (look ahead at) until it 
        reaches an occupied node. It will then correct its speed/velocity 
        according to the first vehicle occupied in its look-ahead range.
        look_ahead is then analogous to how far a vehicle will look infront of 
        itself in order to spot another vehicle such that it can peform 
        planning to avoid bumping into it or moving slower than it would like
        to.
        In the case where a vehicle occupies the node infront and a move cannot
        be executed according to the time scheduled by the vehicles current
        velocity then we correct for this by calibrating the vehicles scheduled
        transition time. A further delay may also be added to this to account
        for driver reactions. We also correct for speed/velocity if it is found
        that the vehicle infront is moving at a slower speed on average.
        If look_ahead is set to None then a vehicle will only peform any form
        of planning if a vehicle is found occupying the node infront of it. It
        is by all means a greedy agent.
    velocity_correction: float 
        If the vehicle peforms planning and corrects its velocity then it does
        so according to some correction per move gradient. Following this
        gradient should allow the vehicle to reach its desired velocity when
        it reaches the point that it corrected for. However, this is not very
        realistic. Vehicles in reality do not like to correct fully if they
        do not have to. Hence, velocity correction is some value between zero 
        and one that specifies how much of the correction is performed
        i.e. actual_correction = velocity_correction*correction_per_move.
        Setting it to one results in a full correction while zero means that
        the vehicle will never correct its velocity.
    smooth: bool
        If a vehicle corrects its velocity then it can choose to do so smoothly
        over several moves or abruptly in a single move.
        It is reccommended to keep this as True.
    frames_per_move: int
        Intended for display purposes. This is how many frames of movement will
        be rendered for an actual node-to-node move.
    time: float
        This is the current time-stamp of when a vehicle will complete its
        scheduled manuver.
    move_type: str
        This is used for the vehicle to know what sort of display it should
        follow. It also serves as an interesting way to track what the vehicle
        has done it its history. See self.movement_record.
    arrival: bool
        This will be True if the vehicle is still in a __basik.source.Source
        object and not yet part of the simulation.
    wait: bool
        True if a vehicle has been delayed or halts.
    move_duration: float
        This is a value in seconds of how long the last manuver took.
    movement_record: dict
        This will be produced if record_movement is set to True.
        A dictionary that records various elements of the vehicles discrete
        event history can be found here.
        It is of the form:
        >>> movement_record = {'time':list,
        ...                    'distance':list,
        ...                    'nodes':list,
        ...                    'move type':list,
        ...                    'velocity':list}
    vehicle_display: __basik__.VehicleObject.vehicle_display.VehicleDisplay
        The vehicle display component.
    '''
    

    
    std = 0.1   
    delay_time = 0.1  # can't be  too small
    look_ahead = 3
    velocity_correction = 1
    smooth = True
    frames_per_move = 3
    is_vehicle = True
    
    INTERNAL = True
    
    #---------------------------------------------------------------------------
    
    def __init__(self,velocity,
                      global_time,
                      current_node,
                      source_ID,
                      color='blue',
                      swivel_when_delayed=False,
                      record_movement=False):
        
        '''
        Parameters:
        ------------
        velocity: float
            The average velocity of the vehicle in meters per second.
            The actual velocity is a Gaussian random variable:
            instantaneous_velocity = numpy.random.normal(velocity,std)
        global_time: float
            When this time is reached by the simulator (i.e. the 
            __basik__.global_queue.GlobalQueue in use) then the vehicle arrival
            will be complete. It is scheduled to be part of the simualtion at 
            this time. 
        current_node: __basik__.node.Node
            The node that the vehicle currently occupies.
        source_ID: int
            We can keep track from which source the vehicle was produced as an
            arrival.
        color: str
            If set to 'random' the the actual display color can still be 
            obtained by calling self.vehicle_display.color
        swivel_when_delayed: bool
            If set to True then the vehicle will swivel on its current display
            component if delayed.
        record_movement: bool
            If set to True then self.movement_record will be created and updated
            throughout the simulation.
        '''
                     
        assert velocity >= 0
        self.velocity = velocity
        self.record_movement = record_movement 
        # We must initialise a time of when it will reach the next node
        self.time = global_time 
        self.current_node = current_node
        self.current_node.vehicle = self
        self.source_ID = source_ID
        self.arrival = True
        self.wait = False
        self.designated_circle_exit = None
        self.do_exit_circle = False  # move to left instead of front
        self.last_time = None
        
        self.display_component = None # The component it is one
        
        self.color = color
        self.vehicle_display = VehicleDisplay(color=color)  # display component of the vehicle
        
        self.frames_per_move = 5
        
        # LIST types of moves here:
        self.move_type = None
        
        self.dispose = False
        
        
        
        # TESTING:
        self.within_circle = False
        
        
        # TODO: clean up the attributes a bit
        self.full_enter = False
        self.partial_enter = False
        self.waited_at_circle = False
        self.waited_outside_circle = False
        self.waited_at_circle_n_times = False
        self.first_circle_move = False
        
#        self.option = None
        
        
        
        
        self.swivel_when_delayed = swivel_when_delayed
        
        
        self.do_exit_traffic_light = False
        self.traffic_light_exit = None
    
        self.do_exit_stop_street = False
        self.stop_street_exit = None
        
        
        self.n_halts = 0
        
        self.moved_display_to_traffic_light_entrance = False
        
        # Choose one. This will be allocated when entering a buffer
        self.designated_traffic_light_exit = None
        self.designated_traffic_light_exit_idx = None
        
        # We do not want to re-choose exits if a scheduled move results
        # in a wait. This is not how reality works: one does not change your
        # destination based on whether you have to wait.
        # Furthermore, the sampling process will be corrected in terms of the
        # tpm but the observed counts should differ from the tpm in the long run
        # if exits are re-selected after a wait.
        self.exit_chosen = False
        
        
        # For the intersection component.
        self.has_waited = False
        self.waited_at_intersection = False # TODO: we need to reset this somewhere.
        self.wait_time_stamp = None
        
        
        self.has_been_recorded = False
        
        
    
    #---------------------------------------------------------------------------
         
        
    def schedule_move(self):
    
        
        current_node = self.current_node
        
        # Just an adjustment below
        if current_node.velocity_change:
            self.velocity = self.current_node.new_velocity
        
        
        ######  DISPOSE
        
#        if current_node.vehicle is None:
#            print(1)
#            self.move_type = 'dispose'
#            
#            return None        
        
        if current_node.front is None:
#            print(2)
                        
            # Abolish    
            self.move_type = 'dispose'
            self.dispose = True
            Queue.push(self)
            return None

        ######  OBSTRUCTION  ######
        
        if current_node.front.obstructed:
            
            if hasattr(current_node.front,'n_vehicles_obstructued'):
                
                if self is current_node.front.last_seen_vehicle:
                    # if the vehcile has already been obstructed then we do
                    # not obstruct it again
                    pass
                else:
                    current_node.front.count_obstruction(self)
                    self.move_type = 'wait'
#                    print('Obstruction Encountered')
                    self.wait = True
                    self.time = current_node.front.end_time + 1e-3
                    Queue.push(self)
                    return None
                
            else:
            
                self.move_type = 'wait'
#                print('Obstruction Encountered')
                self.wait = True
                self.time = current_node.front.end_time + 1e-3
                Queue.push(self)
                return None

        
        ######  STOP STREET  ######
        
        if current_node.front.stop_street_entrance:
#            print(4)
            
            if current_node.front.locked:
                
            
                self.move_type = 'wait at stop street entrance'
                # We do not move the vehicle to the next node.
                # However, on the display side of things, we make do make
                # it wait on the stop street display object instead
                
                self.wait = True
                stop_street = self.current_node.front.stop_street
                retry_request_time = stop_street.request_unlock_time()
                self.time = retry_request_time
                Queue.push(self)
                return None
                # The vehicle is at an entrance but has not yet been allocated
                # an exit at the stop street. This is done as schedule_stop_street_move()
                
            else:
                
                if isinstance(self.display_component,RoadDisplay):
                        self.vehicle_display.move_along_track(1,
                                                    frames_per_move=self.frames_per_move,
                                                    time_per_move=self.move_duration)
                
                previous_move_type = self.move_type
                self.schedule_stop_street_move()
                # The above function will have allocated an exit.
                if previous_move_type == 'wait at stop street entrance':
                    self.move_type = 'partial cross stop street'
                else:
                    self.move_type = 'full cross stop street'
                    
#                Queue.push(self)
                return None
                
        ######  TRAFFIC LIGHT  ######    
        
        elif current_node.front.traffic_light_entrance:
#            print(5)
            
            if current_node.front.occupied:
                self.wait = True
                self.move_type = 'wait'
                self.calibrate_backward(start_node=current_node.front,
                                        aranged_time=current_node.front.vehicle.time)
                Queue.push(self)
                return None
            
            if current_node.front.locked:
                
                
                if not self.moved_display_to_traffic_light_entrance:
                    self.move_display_to_wait_at_traffic_light_entrance()
                    self.moved_display_to_traffic_light_entrance = True
                    # # TODO: we will need to reset it to false soon
                    # perhaps do so at partial or full move
                

#                self.move_type = 'wait at traffic light entrance'
                self.move_type = 'wait'
                
                # We do not move it to the next node.
                # However, we do change things on the display side.
                # We make it wait at the traffic light.
                
                self.wait = True
                traffic_light = self.current_node.front.traffic_light
                retry_request_time = traffic_light.request_unlock_time()
                self.time = retry_request_time
                
                self.calibrate_backward(start_node=current_node,
                                        aranged_time=retry_request_time)
                
            
                
                Queue.push(self)
                return None

                
            else:
                
#                if isinstance(self.display_component,RoadDisplay):
#                        self.vehicle_display.move_along_track(1,
#                                                    frames_per_move=5,
#                                                    time_per_move=self.move_duration)
                
                
                if not self.moved_display_to_traffic_light_entrance:
                    self.move_display_to_wait_at_traffic_light_entrance()
                
                previous_move_type = self.move_type
                self.schedule_traffic_light_move()
                
                # current node is an entrance node now.
                # recall that schedule_traffic_light_move() moves the vehicle
                # from its node to an entrance node and leaves the old node
                # unoccupied. Hence current_node.behind.behind
        
                start_node = None
                if current_node.behind.vehicle is None:
                    start_node = current_node.behind.behind
                else:
                    # !!!! We do not expect this to ever happen.

                    start_node = current_node.behind
                aranged_time =self.time + np.random.uniform(1e-3,self.delay_time)
                
                if start_node.vehicle is not None:
                    self.calibrate_backward(start_node,
                                            aranged_time)
                
                # !!!!: questionable placement ????????????????????????????????????
                self.moved_display_to_traffic_light_entrance = False
                
                
                # schedule_traffic_light_move may have resulted in a yellow
                # light cut-off. We must check if the vehicle was successful
                # at crossing or not.
                if self.wait:
                    # It was cut-off by yellow light and did not cross.
                    # NOTE: this is exactly the same as if we had
                    # current_node.front.locked
                    # It starts at the node infront of an entrance,
                    # attempts to cross but a yellow light locks the crossing.
                    # Hence it remains to be displayed at the entrance.
                    # Internal node-wise, it is still at the node infront
                    # of the entrance node. This is for simplicity in the 
                    # move() function. However, it makes the internal node mechanism
                    # and the display behave slightly different.
                    
#                    self.move_type = 'wait at traffic light entrance'
                    self.move_type = 'wait'
                    

                    
                else:
                    if previous_move_type == 'wait at traffic light entrance':
                        self.move_type = 'partial cross traffic light'
                    elif previous_move_type == 'wait':
                        self.move_type = 'partial cross traffic light'
                    else:
                        self.move_type = 'full cross traffic light'
                        
                
                
        ######  CIRCLE  ######      
            
        elif current_node.front.circle_entrance:
#            print(6)
            
            # FRONT NODE IS AN ENTRANCE !!!
            entrance = current_node.front
            
        
            
            if entrance.occupied:
                # This event occurs if the vehicle infront has had a 
                # successful schedule_circle_entrance().
                # This means that it occupies the entrance.
                # self.move() will then allow it to enter one of the quarters
                # of the circle. 
            
#                print('ENTRANCE OCCUPIED')
#                print(self.vehicle_display.color)
#                print(self.vehicle_display.coords)
                # This is different from 'wait at circle entrance' because there
                # is currently a vehicle at the entrance waiting to enter the
                # circle (a vehicle that is halting).
                
                                
                self.move_type = 'wait'
                self.waited_at_circle = False # not in circle yet
                self.waited_outside_circle = True
                
                self.wait = True
                # This maybe needs a request_unlock_time
                retry_request_time = entrance.vehicle.time + 1e-3
                self.time = retry_request_time
                Queue.push(self)
                return None
            
            else:
                
                
                previous_move_type = deepcopy(self.move_type )
                
                self.previous_move_type = previous_move_type
                
                self.schedule_circle_entrance()
                
                
                if self.wait:
                    
                    if self.waited_at_circle:
                        self.move_type = 'wait'
                        self.waited_at_circle_n_times = True
                    else:
                        self.move_type = 'wait at circle entrance'
                    

                    
                else:
                    
                    # NB !!!!
                    # schedule_circle_entrance() has casued the node
                    # infront of the entrance to be open without 
                    # shifting the vehicle.
                    if isinstance(self.display_component,RoadDisplay):
                        self.vehicle_display.move_along_track(1,
                                                    frames_per_move=self.frames_per_move,
                                                    time_per_move=self.move_duration)
                    
                    
                    if self.waited_at_circle:
                        self.move_type = 'partial enter circle'
                        self.within_circle = True
                        self.option = 1
                        return None
                    elif self.waited_at_circle_n_times:
                        self.move_type = 'partial enter circle'
                        self.within_circle = True
                        self.option = 2
                        return None
                    elif self.waited_outside_circle:
                        self.move_type = 'full enter circle'
                        self.within_circle = True
                        self.option = 3
                        return None
                    else:
                        self.move_type = 'full enter circle'
                        self.within_circle = True
                        self.option = 4
#                        raise Exception('No cases were fulfilled!')
                        return None
                    
                    raise Exception('No cases were met!')


#                    if previous_move_type == 'wait at circle entrance':
#                        self.move_type = 'partial enter circle'
#                    elif previous_move_type == 'wait':
#                        if not self.waited_at_circle:
#                            self.move_type = 'full enter circle'
#                        else:
#                            self.move_type = 'partial enter circle'
#                    else:
#                        self.move_type = 'full enter circle'
                    
                
        elif self.within_circle:
#        elif current_node.front.circle_node:
#            print(7)

            previous_move_type = self.move_type
            self.schedule_circle_move_or_exit()
            
            if self.do_exit_circle:
                self.move_type = 'exit circle'
            else:

                
                self.move_type = 'move within circle'
                
            


        ######  OFF-RAMP  ######

            
        elif current_node.off_ramp_entrance:
#            print(8)
            # Note: we did not call for front as the entrance. Off ramp is not
            # a true component. It is simply a node that can have front chosen
            
            self.schedule_off_ramp_move()
            
#            if self.current_node.off_ramp.chosen_exit_key == 'OFF':
            if self.current_node.off_ramp.chosen_exit_idx == 0:
                self.move_type = 'off-ramp exit'
            else:
                self.move_type = 'off-ramp proceed forward'
                
        elif current_node.off_ramp_standard_entrance:
            # This is the lane that does not contain the off-ramp and just acts
            # as standard.
            self.schedule_standard_move()
            self.move_type = 'off-ramp standard'
            
            
        ######  ON-RAMP  ######
        
        elif current_node.on_ramp_node: 
            
            if current_node.sub_flow:
                
                previous_move_type = self.move_type
                
                self.schedule_on_ramp_move()
                if self.wait:
                    self.move_type = 'wait at on-ramp entrance'
                else:
                    if previous_move_type == 'wait at on-ramp entrance':
                        
                        self.move_type = 'partial enter on-ramp'
                    else:    
                        self.move_type = 'full enter on-ramp'
                
            else:
                # main flow.
                # It doesn't enter the on-ramp and continues on and passes it.
                self.move_type = 'pass on-ramp'
                self.schedule_standard_move()
                
        elif current_node.on_ramp_standard_node:
            
            self.schedule_standard_move()
            self.move_type = 'on-ramp standard'
            
            
        ######  FLARED TRAFFIC LIGHT ###### 
        
        elif current_node.flared_traffic_light_entrance:
            
            self.schedule_buffer_entrance()
            self.move_type = 'enter buffer'
            
        elif current_node.buffer_node:
            
            if current_node.buffer_end:
                self.schedule_buffer_exit()
                if self.wait:
                    self.move_type = 'wait'
                else:
                    self.move_type = 'exit buffer'
                
                
            else:
                self.schedule_buffer_move()
                self.move_type = 'move within buffer'
                
        ######  INTERSECTION ######
        
        elif current_node.intersection_entrance: 
            
            self.schedule_intersection_move()
            
            
            # schedule_intersection_move can result in:
            # 1) enter + wait
            # 2) wait again
            # 3) after n waits (n >= 1) move to exit
            # 4) enter + move to exit
            
            if self.wait:
                
                if self.has_waited:
                    # Has waited before and waits again.
                    # No entrance required
                    if self.move_type == 'partial cross intersection':
                        # a'partial cross intersection' was pre-assigned
                        # during schedule_intersection_move().
                        # We do not change this.
                        pass
                    else:
                        self.move_type = 'wait'
                    self.waited_n_times = True
                else:
                    # Waits for the first time.
                    # Entrance required and move to the wait zone.
                    self.move_type = 'wait at intersection'
                    self.has_waited = True
                    self.waited_once = True
            else:
                if self.has_waited:
                    # Has entered and moved to the wait zone.
                    # To exit, only the turn track must be traversed.
                    # We must move it to the next road/lane.
                    self.move_type = 'partial cross intersection'
                    self.has_waited = False
                else:
                    # Enters and traverses the entire track towards the exit.
                    # We must move it to the next road/lane.
                    self.move_type = 'full cross intersection'
                    # Reset the attributes for future use: if more intersections
                    # are encountered.
                    self.has_waited = False
                    
                    
        ######  PEDESTRIAN CROSSING  #######    
        
        elif current_node.pedestrian_crossing_entrance:
            
            self.schedule_pedestrian_crossing_entrance()
            self.move_type = 'enter pedestrian crossing'
            
        elif current_node.pedestrian_crossing_buffer_exit:
            
            self.schedule_exit_pedestrian_crossing()
            self.move_type = 'exit pedestrian crossing'

        elif current_node.pedestrian_crossing_buffer_node:
            
            self.schedule_move_within_pedestrian_crossing()
            if self.wait:
                # Pedestrians are crossing because node with index 5 is locked.
                # This prevents the vehicle at node with index 4 from crossing.
                self.move_type = 'wait'
            else:
                self.move_type = 'move withing pedestrian crossing'


        ######  NEW VEHICLE FROM SOURCE  ######
        
        elif self.current_node.front.source_attached: 
            self.schedule_source_arrival()
            self.move_type = 'source arrival'
            

            
        
        ######  STANDARD  ######
            
        else:
#            print('standard move scheduled')
            # TODO: this never picks up if a vehcile was delayed
            self.schedule_standard_move()
            self.move_type = 'standard'
            
        
        return None
    
    #--------------------------------------------------------------------------
    
    
    def move_display_to_wait_at_traffic_light_entrance(self):
        
        
        if isinstance(self.display_component,RoadDisplay):
            self.vehicle_display.move_along_track(1,
                                        frames_per_move=self.frames_per_move,
                                        time_per_move=self.move_duration)
            
        
        # Transition from road/lane to traffic light entrance.
        self.vehicle_display.hide()
        # The traffic light entrance is infront of it, hence use .front
        self.display_component = self.current_node.front.traffic_light_display
        
        if self.display_component is None:
            # No display component.
            self.vehicle_display.axes = None
        else:
            axes = self.display_component.axes
            self.vehicle_display.reset_axes(axes)
            entrance_idx = self.current_node.front.idx # front node is the entrance. 
            # Cannot use entrance_idx as schedule_traffic_light_move() was
            # either not called yet or did not call choose_exit() on the
            # traffic_light as a lock/wait was caused by a yellow light.
#                entrance_idx = self.current_node.entrance_idx  
            coords = self.display_component.entrances[entrance_idx]
            bearings = self.display_component.bearings[entrance_idx]
            self.vehicle_display.reset_coords(coords)
            self.vehicle_display.reset_bearings(bearings)
            self.vehicle_display.show()
            
            
            self.vehicle_display.flicker(5)
            self.vehicle_display.show()
        
        return None
    
    
    #--------------------------------------------------------------------------
    

    
    def move_display_back_to_road(self,Exit):
        # Helper function for move_display.
        self.display_component = Exit.road_display_object
#        print('----------------------------')
#        print('Move back to road')
#        print('display component: ',self.display_component)
#        print('idx',Exit.idx)
#        print('----------------------------')
        
        if self.display_component is None:
            self.vehicle_display.axes = None
        else:
            axes = self.display_component.axes
            if Exit.left_lane:
                coords = self.display_component.left_entrance
                bearings = self.display_component.left_bearings
                track = self.display_component.left_track
            else:
                coords = self.display_component.right_entrance
                bearings = self.display_component.right_bearings
                track = self.display_component.right_track
            # Setup the vehicle for display and show.
            self.vehicle_display.reset_axes(axes)
            self.vehicle_display.setup_track(track,current_track_idx=0)
            self.vehicle_display.reset_coords(coords)
            self.vehicle_display.reset_bearings(bearings)
            self.vehicle_display.show()
        return None
    

    
    #--------------------------------------------------------------------------
    
    def move_display(self):
        

        
        
        # NOTE: move_display is called after the move has been scheduled.
        # This means that current_time has been updated and that
        # self.move_duration has how long the move will take.
        
        #----------------------------------------------------------------------
        
        if self.move_type == 'standard':
            
            # NEW
            if self.do_exit_traffic_light:
                self.vehicle_display.hide()
                self.move_display_back_to_road(self.traffic_light_exit)
                self.do_exit_traffic_light = False
                self.traffic_light_exit = None
            
            # NEW
            if self.do_exit_stop_street:
                self.vehicle_display.hide()
                self.move_display_back_to_road(self.stop_street_exit)
                self.do_exit_stop_street = False
                self.stop_street_exit = None
            
            if self.vehicle_display.axes is None:
                pass
            else:
                self.vehicle_display.move_along_track(moves=1,
                                                      frames_per_move=self.frames_per_move,
                                                      time_per_move=self.move_duration)
        #----------------------------------------------------------------------
            
        elif self.move_type == 'wait':
            
            if self.swivel_when_delayed:
                if self.vehicle_display.axes is None:
                    # No display component.
                    pass
                else:
                    if self.swivel_when_delayed:
                        self.vehicle_display.swivel(n_swivels=3,time_per_swivel=0.05)
                    else:
                        pass
        
        #----------------------------------------------------------------------
        
        elif self.move_type == 'source arrival':
            

            # current_node is currently a temporary node embedded in the 
            # source. This node holds the vehicle unitl it can be released 
            # onto a road/lane at the scheduled time.
            # The exit of a source is the in_node of a road/lane object.
            source_exit = self.current_node.front
            # We use the modular function move_display_back_to_road().
            self.move_display_back_to_road(source_exit)
            
        #----------------------------------------------------------------------   
            
        elif self.move_type == 'dispose':
            
            if self.vehicle_display.axes is None:
                # No display component.
                pass
            else:
                self.vehicle_display.flicker(n_flickers=3,time_per_flicker=0.05)
                self.vehicle_display.axes = None
        #----------------------------------------------------------------------
        
        elif self.move_type == 'wait at stop street entrance':
            
            # Transition from road to stop street.
            # Hence we must change: 
            # 1) display component (if it has one)
            # 2) matplotlib axes
            # 3) track
            # 4) coords
            # 5) bearings
            
            if self.vehicle_display.axes is not None:
                # Hide a we will move it from road display onto stop street display.
                self.vehicle_display.hide()
                
            # Get new display component.
            self.display_component = self.current_node.front.stop_street_display
            
            if self.display_component is None:
                # No display component.
                self.vehicle_display.axes = None
            else:
                # Reset the Matplotlib axes.
                axes = self.display_component.axes
                self.vehicle_display.reset_axes(axes)
                # Get idx of the entrance.
                idx = self.current_node.front.idx # N,E,S,W ???
                # Now place at the correct entrance with appropriate bearings.
                coords = self.display_component.entrances[idx]
                bearings = self.display_component.bearings[idx]
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                # The vehicle can now be displayed.
                self.vehicle_display.show()
                # NOTE: track has not yet been changed as we have not chosen an exit
                # Swivel to show that it has halted
                if self.n_halts == 0:
                    self.vehicle_display.swivel(n_swivels=3,time_per_swivel=0.05)
                    self.n_halts += 1
                else:
                    # reset
                    self.n_halts = 0
                    pass
            
        #----------------------------------------------------------------------
        
        elif self.move_type == 'partial cross stop street':
            # This can only follow 'wait at stop street entrance'
            
            if self.vehicle_display.axes is None:
                pass
            else:
                # The vehicle is already displayed at the entrance. The vehicle 
                # will have a designated exit given by schedule_stop_street_move().
                # This means that we can allocate it a track to move along on the
                # display.
                # NOTE: after calling schedule_stop_street_move(), the current node
                # is now an entrance node.
                # Get entrances and exits
                entrance_idx = self.current_node.stop_street.entrance_idx  # preferred
#                entrance_idx = self.current_node.idx  # doesn't cohere with below 
                exit_idx = self.current_node.stop_street.exit_idx
                # Get the correct track moving from entrance to exit.
                display_track = self.display_component.tracks[entrance_idx,
                                                              exit_idx] 
                # Setup the track for the vehicle to follow.
                self.vehicle_display.setup_track(display_track,
                                                 current_track_idx=0)
                # Move accross the stop street
                self.vehicle_display.move(destination=display_track[1:],
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                # Once the maneouvre is completed, the vehicle must be removed from
                # the stop street display.
                
                # NEW
                self.do_exit_stop_street = True
                self.stop_street_exit = self.current_node.front
                
                # OLD
#                self.vehicle_display.hide()
#            Exit = self.current_node.front  # more simple than the above. 
#            self.move_display_back_to_road(Exit)

        
            
        #----------------------------------------------------------------------    
        
        elif self.move_type == 'full cross stop street':
            
            if self.vehicle_display.axes is not None:
                self.vehicle_display.hide()
            
            # A combination of 'wait at stop street entrance' and 
            #'partial cross stop street'. It performs both of those.
            
            # NOTE: schedule_stop_street_move() has been called. This means
            # that the current node is now the entrance node. Hence, part 1 
            # will differ from 'wait at stop street entrance' in that we do
            # not have to refer to current_node.front to get the entrance.
            
            ###  PART 1  ### 
            # Transition from road/lane to stop street entrance.
            
            self.display_component = self.current_node.stop_street_display
            
            if self.display_component is None:
                # No display component.
                self.vehicle_display.axes = None
            else:
                axes = self.display_component.axes
                self.vehicle_display.reset_axes(axes)
    #            entrance_idx = self.current_node.idx  # doesn't cohere well with exit_idx
                entrance_idx = self.current_node.stop_street.entrance_idx  # More readable than above
                coords = self.display_component.entrances[entrance_idx]
                bearings = self.display_component.bearings[entrance_idx]
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.show()
                # Swivel to show that it has halted.
                self.vehicle_display.swivel(n_swivels=3,time_per_swivel=0.05)
                    
                self.vehicle_display.swivel(n_swivels=3,time_per_swivel=0.05)
                
                ###  PART 2  ###
                # Move the vehicle across the stop street and transition onto
                # a new road/lane.
                
                # !!!! Check if this works. Is didn't for traffic light
                # There we used self.current_node.front.idx as front of entrance is an exit.
                exit_idx = self.current_node.stop_street.exit_idx
                
                
                # We use idxs as it is convenient to with tracks where a 2D
                # transitions probability matrix (tpm) must be used.
                display_track = self.display_component.tracks[entrance_idx,
                                                              exit_idx] 
                self.vehicle_display.setup_track(display_track,
                                                 current_track_idx=0)
                self.vehicle_display.move(destination=display_track[1:],
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                
                # NEW
                self.do_exit_stop_street = True
                self.stop_street_exit = self.current_node.front
                
                # OLD
#                self.vehicle_display.hide()
#            Exit = self.current_node.front  # More simple than the above.
#            self.move_display_back_to_road(Exit)
        
        #----------------------------------------------------------------------

        elif self.move_type == 'wait at traffic light entrance':
            
            # Transition from road/lane to traffic light entrance.
            self.vehicle_display.hide()
            # The traffic light entrance is infront of it, hence use .front
            self.display_component = self.current_node.front.traffic_light_display
            
            if self.display_component is None:
                # No display component.
                self.vehicle_display.axes = None
            else:
                axes = self.display_component.axes
                self.vehicle_display.reset_axes(axes)
                entrance_idx = self.current_node.front.idx # front node is the entrance. 
                # Cannot use entrance_idx as schedule_traffic_light_move() was
                # either not called yet or did not call choose_exit() on the
                # traffic_light as a lock/wait was caused by a yellow light.
#                entrance_idx = self.current_node.entrance_idx  
                coords = self.display_component.entrances[entrance_idx]
                bearings = self.display_component.bearings[entrance_idx]
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.show()

        #----------------------------------------------------------------------
        
        elif self.move_type == 'partial cross traffic light':
            
            if self.vehicle_display.axes is None:
                # This has been determined by 'wait at traffic light entrance'
                pass
            else:
                # schedule_traffic_light_move() has been called. We have
                # self.time < cut_off_time such that no yellow light ocurrs.
                # This means choose_exit has been called. Hence current_node
                # is now the entrance node
                entrance_idx = deepcopy(self.current_node.traffic_light.entrance_idx)   # (1)
                entrance_idx = self.current_node.idx  # (2)  Better option
                
                exit_idx = self.current_node.front.idx

                # Get the correct track moving from entrance to exit.
                display_track = self.display_component.tracks[entrance_idx][exit_idx] 
                # Setup the track for the vehicle to follow.
                self.vehicle_display.setup_track(display_track,
                                                 current_track_idx=0)
                # Move accross the stop street
                self.vehicle_display.move(destination=display_track[1:],
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                # Once the maneouvre is completed, the vehicle must be removed from
                # the stop street display.
                
                
                # NEW
                self.do_exit_traffic_light = True
                self.traffic_light_exit = self.current_node.front
                
                # OLD
#                self.vehicle_display.hide()
#            Exit = self.current_node.front
#            self.move_display_back_to_road(Exit)
            
        #----------------------------------------------------------------------
    
        elif self.move_type == 'full cross traffic light':
            
            # NOTE: current node is an entrance as we have called
            # schedule_traffic_light_move()
            
            ###  PART 1  ###
            self.vehicle_display.hide()
            self.display_component = self.current_node.traffic_light_display
            
            if self.display_component is None:
                # No display component.
                self.vehicle_display.axes = None
            else:
                axes = self.display_component.axes
                self.vehicle_display.reset_axes(axes)
                
#                entrance_idx = deepcopy(self.current_node.traffic_light.entrance_idx)        # (1)
                entrance_idx = self.current_node.idx  #  (2) better option
                
                coords = self.display_component.entrances[entrance_idx]
                bearings = self.display_component.bearings[entrance_idx]
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.show()
                
                ###  PART 2  ###
#                exit_idx = self.current_node.traffic_light.exit_idx  # doesn't work
                
                exit_idx = self.current_node.front.idx
                
                
                display_track = self.display_component.tracks[entrance_idx][exit_idx] 
                self.vehicle_display.setup_track(display_track,
                                                 current_track_idx=0)
                self.vehicle_display.move(destination=display_track[1:],
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                
                # NEW
                self.do_exit_traffic_light = True
                self.traffic_light_exit = self.current_node.front
                
                # OLD
#                self.vehicle_display.hide()
#            Exit = self.current_node.front
#            self.move_display_back_to_road(Exit)

        #----------------------------------------------------------------------
        
        elif self.move_type == 'wait at circle entrance':
            
            self.waited_at_circle = True
            
            
            # NOTE: current_node.front is an entrance node.
            
            # Procedure:
            # 1) Place vehicle display from road/lane to the circle entrance.
            # 2) Move vehcile from the entrance towards the halting zone
            # where it can wait to enter the circle once it has right of way.
            
            # Step 1: change placement and axes
            # Transition from road/lane to circle entrance.
            
            if self.vehicle_display.axes is not None:
                # Do we currently have a display.
                # If so then hide.
#                isinstance(self.display_component,RoadDisplay)
                self.vehicle_display.move_along_track(1,
                                                      frames_per_move=self.frames_per_move,
                                                      time_per_move=self.move_duration)
                self.vehicle_display.flicker(5)
#                print('wait at circle entrance')
                
                # NB: Below
                self.vehicle_display.hide()
            
            # The circle entrance is infront of it, hence use .front
            self.display_component = self.current_node.front.circle_display
            
    
            if self.display_component is None:
                # No display component.
                self.vehicle_display.axes = None
            else:
                axes = self.display_component.axes
                self.vehicle_display.reset_axes(axes)
                
                entrance_idx = self.current_node.front.idx # front node is the entrance. 
                
                if entrance_idx is None:
                    entrance_idx = self.current_node.idx
                
                if not isinstance(entrance_idx,int):
                    raise Exception('entrance_idx not int: {0}'.format(entrance_idx))
                    
                    
                coords = self.display_component.entrances[entrance_idx]
                bearings = self.display_component.bearings[entrance_idx]
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.show()
                
                # Step 2: move vehicle to halting zone.
                halt_zone = self.display_component.halt_zones[entrance_idx]
                self.vehicle_display.move(halt_zone,
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
            
        #----------------------------------------------------------------------

        elif self.move_type == 'partial enter circle':
            
            self.partial_enter = True
            
            assert self.waited_at_circle
            
            
            if isinstance(self.display_component,RoadDisplay):
                self.display_component = None
                self.vehicle_display.axes = None
            
            
            if self.vehicle_display.axes is None:
                
#                print('AXES is NONE!!!!')
#                print(self.vehicle_display.color)
#                print(self.vehicle_display.coords)
                # No display component.
                pass
            else:
                # We assume that on the display side of things that the vehicle
                # has been placed at a halt zone.
                # We notice that the circle track still has not been allocated
                # to the vehicle display.
                
                # NOTE: schedule_circle_entrance() has been called and has resulted
                # in allowing the vehicle to proceed to enter.
                # Hence, the current node is now a circle entrance.
                
                entrance_idx = self.current_node.idx
                circle_start = self.display_component.start_zones[entrance_idx]
                self.vehicle_display.move(circle_start,
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                
                
                
                # Allocate the track
                track = self.display_component.track
                start_idx = self.display_component.start_idxs[entrance_idx]
                # start_idx is required to know where on the track we are.
                # This is because track is just one long linear list/array that
                # is forced to behave like a circular object by controlling how
                # indices (idxs) progress forward.
                self.vehicle_display.setup_track(track,start_idx)

                assert self.vehicle_display.track is not None
                
                #########################################
                
                n_moves = self.display_component.frames_per_move - 1
                self.vehicle_display.move(n_moves,frames_per_move=self.frames_per_move,
                                          time_per_move=self.move_duration)
        
        #----------------------------------------------------------------------
        
        elif self.move_type == 'full enter circle':
            
            self.full_enter = True
            

            if self.vehicle_display.axes is not None:
                # Do we currently have a display.
                # If so then hide.
                self.vehicle_display.hide()
                
            
            
            # Get the next display component
            # The circle entrance is infront of it, hence use .front
            self.display_component = self.current_node.circle_display
            
            
            if self.display_component is None:
                # No display component.
                self.vehicle_display.axes = None
                
            else:
                # Combination of 'wait at circle entrance' and 'partial enter circle'.
                # NOTE: schedule_circle_entrance() has been called and has resulted
                # in proceed = True. This means that current node is an entrance
                # node.
                
                ###  PART 1  ###
                # Step 1: change placement and axes
                # Transition from road/lane to circle entrance.
                axes = self.display_component.axes
                self.vehicle_display.reset_axes(axes)
                entrance_idx = self.current_node.idx # front node is the entrance. 
                coords = self.display_component.entrances[entrance_idx]
                bearings = self.display_component.bearings[entrance_idx]
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.show()
                
                # Step 2: move vehicle to halting zone.
                halt_zone = self.display_component.halt_zones[entrance_idx]
                self.vehicle_display.move(halt_zone,
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                
                ###  PART 2  ###
                circle_start = self.display_component.start_zones[entrance_idx]
                
                
                self.vehicle_display.move(circle_start,
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                # Allocate the track
                track = self.display_component.track
                start_idx = self.display_component.start_idxs[entrance_idx]
                self.vehicle_display.setup_track(track,start_idx)
                
                
                
                
                n_moves = self.display_component.frames_per_move - 1
                self.vehicle_display.move(n_moves,
                                          frames_per_move=self.frames_per_move,
                                          time_per_move=self.move_duration)
        #----------------------------------------------------------------------
            
        elif self.move_type == 'exit circle':
            
            if self.vehicle_display.axes is None:
                # Currently no display to exit from.
                pass
            else:
                # Move to exit but also remove from circle display and place it
                # onto a road/lane display.
    
                ###  PART 1  ###
                # We move to the exit.
                # designated_circle_exit_idx was assigned during the call if
                # schedule_circle_entrance().
                
                # TODO: remove swivel
                self.vehicle_display.swivel(n_swivels=3,time_per_swivel=0.05)
                
                
                exit_idx = self.designated_circle_exit_idx 
                
                
                exit_coords = self.display_component.exits[exit_idx]
                self.vehicle_display.move(exit_coords,
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                # NOTE: the exit is actually an in_node (IN) from a road/lane.
                # It was given to Circle as one of the four out_nodes.
                # Hence it should contain the road_display object.
                # This is becuase road_display allocates itself to the two
                # in_nodes of its two lanes.
                # This will be used in PART 2.
                self.vehicle_display.hide()
            
            
            
            ###  PART 2  ###
            # We remove the vehicle from the circle_display and onto a road.
            
            Exit = self.designated_circle_exit
            self.move_display_back_to_road(Exit)
            
            
        #----------------------------------------------------------------------
        
        elif self.move_type == 'move within circle':
            
            if self.vehicle_display.axes is None:
                pass
            else:
                # the track has been allocated at either 'full enter circle' or
                # 'partial enter circle'. This means we can just move along the 
                # track.

                
                if not isinstance(self.display_component,CircleDisplay):
                    self.display_component = self.current_node.circle_display
                    self.vehicle_display.setup_track(self.display_component.track,
                                                     self.current_node.circle_track_idx)
                
                
                if self.first_circle_move:
                    n_moves = self.display_component.frames_per_move - 1
                    self.first_circle_move = False
                else:
                    n_moves = self.display_component.frames_per_move 
                    
                self.vehicle_display.move_along_track(moves=n_moves,
                                                      time_per_move=self.move_duration,
                                                      frames_per_move=1)

        #----------------------------------------------------------------------

        elif self.move_type == 'off-ramp exit':
            
            if self.vehicle_display.axes is not None:
                # If the road displays it then hide it.
                self.vehicle_display.hide()
            
            
            self.display_component = self.current_node.off_ramp_display
            
            if self.display_component is None:
                self.vehicle_display.axes = None
            else:
                # 1) Move from road/lane onto off_ramp display object.
                # 2) Move along the entire track.
                # 3) Remove vehicle from off_ramp and onto a new road/lane.
                
                # current_node is an off_ramp_entrance.
                # Recall that this is different from most of the other components.
                
                ###  PREPARATION  ###
                # Get all the neccessary information for the transition.
                
                coords = self.display_component.entrance
                bearings = self.display_component.entrance_bearings
#                bearings = self.display_component.bearings
                axes = self.display_component.axes
                track = self.display_component.off_track
                
                ### PART 1  ###
#                self.vehicle_display.hide()
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show()
                
                ###  PART 2  ###
                # Perform move: 2 options
                # Option 1
                self.vehicle_display.move(track[1:],
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                # Option 2
#                self.vehicle_display.setup_track(track)
#                n = len(track) - 1
#                self.vehicle_display.move_along_track(moves=n,
#                                                      time_per_move=self.move_duration,
#                                                      frames_per_move=3)
                self.vehicle_display.hide()
            
            ### PART 3  ###
            # We know the off-exit was chosen with idx = 0 and key = 'OFF'
            Exit = self.current_node.front
            self.move_display_back_to_road(Exit)
        
        
        #----------------------------------------------------------------------
        
        elif self.move_type == 'off-ramp proceed forward':
            
            if self.vehicle_display.axes is not None:
                # If the road displays it then hide it.
                self.vehicle_display.hide()
                
            self.display_component = self.current_node.off_ramp_display
            
            
            # 1) Move from road/lane onto off_ramp display object.
            # 2) Move along the entire track.
            # 3) Remove vehicle from off_ramp and onto a new road/lane.
            
            # current_node is an off_ramp_entrance.
            # Recall that this is different from most of the other components.
            
            ###  PREPARATION  ###
            # Get all the neccessary information for the transition.
            self.display_component = self.current_node.off_ramp_display
            
            if self.display_component is None:
                self.vehicle_display.axes = None
            else:
            
                coords = self.display_component.entrance
                bearings = self.display_component.entrance_bearings
#                bearings = self.display_component.bearings
                axes = self.display_component.axes
                track = self.display_component.on_track
                
                ### PART 1  ###
                self.vehicle_display.hide()
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show()
                
                ###  PART 2  ###
                # Perform move: 2 options
                # Option 1
                self.vehicle_display.move(track[1:],
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                # Option 2
#                self.vehicle_display.setup_track(track)
#                n = len(track) - 1
#                self.vehicle_display.move_along_track(moves=n,
#                                                      time_per_move=self.move_duration,
#                                                      frames_per_move=3)
                
                ### PART 3  ###
                self.vehicle_display.hide()
            
            # We know the off-exit was chosen with idx = 1 and key = 'ON'
            Exit = self.current_node.front
            self.move_display_back_to_road(Exit)
        
        #----------------------------------------------------------------------
        
        
        elif self.move_type == 'off-ramp standard':
            
            if self.vehicle_display.axes is not None:
                # If the road displays it then hide it.
                self.vehicle_display.hide()
                
            self.display_component = self.current_node.off_ramp_display
            
            if self.display_component is None:
                self.vehicle_display.axes = None
            else:
            
                coords = self.display_component.other_entrance
                bearings = self.display_component.other_entrance_bearings
#                bearings = self.display_component.bearings
                axes = self.display_component.axes
                
                ### PART 1  ###
                self.vehicle_display.hide()  
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show() # should now be shown on current display axes
                
                ### PART 2  ###
                exit_coords = self.display_component.other_exit
                self.vehicle_display.move(exit_coords,
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move*2) # more frames per move
                                          # as it is quite long.
                ### PART 3  ###
                # The focus is now on getting the vehicle to the next road display.                       
                self.vehicle_display.hide()
                
                
            Exit = self.current_node.front  # should have a road_display_object
            self.move_display_back_to_road(Exit)
            

        #----------------------------------------------------------------------
        
        elif self.move_type == 'wait at on-ramp entrance':
            
            if self.vehicle_display.axes is not None:
                # If the road displays it then hide it.
                self.vehicle_display.hide()
            
            # Transition from road/lane to on_ramp sub_entrance
            # NOTE: self.current_node is the entrance.
            
            # Get the neccessary information.
            self.display_component = self.current_node.on_ramp_display
            
            if self.display_component is None:
                self.vehicle_display.axes = None
            else:
                # We know that we are dealing with the sub-flow
                # key = 'SUB' and index = 1 of the entrances.
                coords = self.display_component.entrances[1]
                bearings = self.display_component.sub_entrance_bearings
#                bearings = self.display_component.sub_bearings
                axes = self.display_component.axes
                
            
                # Perform the actual transition to display the vehicle at the 
                # entrance where it waits/halts to join with the main flow.
                self.vehicle_display.hide()
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show()
        
        #----------------------------------------------------------------------
        
        elif self.move_type == 'partial enter on-ramp':
            
            
            if self.vehicle_display.axes is None:
                pass
            else:
                # Already at the entrance.
                # Needs to 1) traverse entire track until it reaches the exit.
                # 2) transition the display to a road/lane component.
                
                ###  PART 1  ###
                track = self.display_component.tracks[1]
                self.vehicle_display.move(track[1:],
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                
                ###  PART 2  ###
                self.vehicle_display.hide()
            
            
            Exit = self.current_node.on_ramp.exit # only one exit
            self.move_display_back_to_road(Exit)
            
        #----------------------------------------------------------------------    
            
        elif self.move_type == 'full enter on-ramp':
            
            if self.vehicle_display.axes is not None:
                self.vehicle_display.hide()
            
            # Combination of 'wait at on-ramp entrance' and 'partial enter on-ramp'.
            
            ###  PART 1  ### 
            # 'wait at on-ramp entrance'
            self.display_component = self.current_node.on_ramp_display
            
            if self.display_component is None:
                self.vehicle_display.axes = None
            else:
            
                coords = self.display_component.entrances[1]
                bearings = self.display_component.sub_entrance_bearings
                axes = self.display_component.axes
#                self.vehicle_display.hide()
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show()
                
                ###  PART 2  ###
                # 'partial enter on-ramp'
                track = self.display_component.tracks[1]
                self.vehicle_display.move(track[1:],
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                self.vehicle_display.hide()
                
                
            Exit = self.current_node.on_ramp.exit 
            self.move_display_back_to_road(Exit)
            
        #----------------------------------------------------------------------
        
        elif self.move_type == 'pass on-ramp':
            
            if self.vehicle_display.axes is not None:
                self.vehicle_display.hide()
            
            # Almost identical to 'full enter on-ramp'
            self.display_component = self.current_node.on_ramp_display
            if self.display_component is None:
                self.vehicle_display.axes = None
            else:
                    
                # We know than main flow has key = 'MAIN' and index of 0.
                coords = self.display_component.entrances[0]
                bearings = self.display_component.main_entrance_bearings
                axes = self.display_component.axes
#                self.vehicle_display.hide()
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show()
                
                
                track = self.display_component.tracks[0]
                self.vehicle_display.move(track[1:],
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                self.vehicle_display.hide()
                # Same exit as sub flow.
                # This is because sub-flow joins main flow and both exit at
                # the same node as one flow.
                
                
            Exit = self.current_node.on_ramp.exit 
            self.move_display_back_to_road(Exit)
        
        #----------------------------------------------------------------------
            
        elif self.move_type == 'on-ramp standard':
            
            
            if self.vehicle_display.axes is not None:
                # If the road displays it then hide it.
                self.vehicle_display.hide()
                
            self.display_component = self.current_node.on_ramp_display
            
            if self.display_component is None:
                
                self.vehicle_display.axes = None
                
            else:
                coords = self.display_component.other_entrance
                bearings = self.display_component.other_entrance_bearings
#                bearings = self.display_component.bearings
                axes = self.display_component.axes
                
                ### PART 1  ###
                self.vehicle_display.hide()  
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show() # should now be shown on current display axes
                
                ### PART 2  ###
                exit_coords = self.display_component.other_exit
                self.vehicle_display.move(exit_coords,
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move*2) # more frames per move
                                          # as it is quite long.
                ### PART 3  ###
                # The focus is now on getting the vehicle to the next road display.                       
                self.vehicle_display.hide()
                
                
            Exit = self.current_node.front  # should have a road_display_object
            self.move_display_back_to_road(Exit)
            
        
        #----------------------------------------------------------------------
        
        elif self.move_type == 'enter buffer':
            # This is called after schedule_buffer_entrance()
            
            # Extract the neccessary indices
            entrance_idx = deepcopy(self.current_node.idx) # deepcopy for safety
            exit_idx = self.designated_traffic_light_exit_idx
            # Let us create some temporary attributes for convenience.
            # These will be used in exit_buffer.
            self._exit_idx = exit_idx  
            self._entrance_idx = entrance_idx
            
            
            
            if self.vehicle_display.axes is not None:
                # If the road displays it then hide it.
                self.vehicle_display.hide()
                
                
                
            self.display_component = self.current_node.flared_traffic_light_display
            
            
            if self.display_component is None:
                self.vehicle_display.axes = None
                
            else:
                

                # Extract
                coords = self.display_component.entrances[entrance_idx]
                bearings = self.display_component.bearings[entrance_idx]
                axes = self.display_component.axes
                
                # Apply
                self.vehicle_display.hide()  
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show()
                
                # Setup Buffer Track. We need to know which buffer first
                if self.current_node.flared_traffic_light.allocate_left_buffer(
                        entrance_idx,
                        exit_idx):
                    buffer_track = self.display_component.buffers[entrance_idx,0]
                    moves = self.display_component.left_entrance_moves
                else:
                    buffer_track = self.display_component.buffers[entrance_idx,1]
                    moves = self.display_component.right_entrance_moves
                
                
                self.vehicle_display.setup_track(buffer_track,current_track_idx=0)
                # Each buffer track contains an initial entrance part.
                # We move along this initial part until finally in the buffer.
                self.vehicle_display.move_along_track(moves=moves,
                                                      time_per_move=self.move_duration,
                                                      frames_per_move=self.frames_per_move)
                

        #----------------------------------------------------------------------
        
        elif self.move_type == 'exit buffer':
            
            if self.vehicle_display.axes is None:
                pass
            else:
                
                turn = self.display_component.turns[self._entrance_idx,
                                                    self._exit_idx]
                self.vehicle_display.move(turn,
                                          time_per_move=self.move_duration,
                                          frames_per_move=1)
                
                self.vehicle_display.hide()
            
            # current_node is a buffer_end
#            Exit = self.current_node.front  
            Exit = self.current_node.flared_traffic_light.exits[self._exit_idx]
            self.move_display_back_to_road(Exit)
            
            delattr(self,'_entrance_idx')
            delattr(self,'_exit_idx')
        
        
        #----------------------------------------------------------------------
        
        elif self.move_type == 'move within buffer':

            if self.vehicle_display.axes is None:
                pass
            else:
                self.vehicle_display.move_along_track(moves=1,
                                                      time_per_move=self.move_duration,
                                                      frames_per_move=self.frames_per_move)
            
        
        #----------------------------------------------------------------------
        
        
        elif self.move_type == 'wait at intersection':
            
            
            if self.vehicle_display.axes is not None:
                # If the road displays it then hide it.
                self.vehicle_display.hide()
                
                
                
            self.display_component = self.current_node.intersection_display
            
            
            if self.display_component is None:
                self.vehicle_display.axes = None
                
            else:
                
                entrance_idx = self.current_node.idx
                exit_idx = self.current_node.front.idx
                # Extract
                coords = self.display_component.entrances[entrance_idx]
                bearings = self.display_component.bearings[entrance_idx]
                axes = self.display_component.axes
                
                # Apply
                self.vehicle_display.hide()  
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show()
                
                # Move to waiting zone
                waiting_zone = self.display_component.wait_zones[entrance_idx]
                self.vehicle_display.move(waiting_zone,
                                          time_per_move=self.move_duration,
                                          frames_per_move=self.frames_per_move)
                
            
        
        #----------------------------------------------------------------------
        
        elif self.move_type == 'partial cross intersection':
            
            if self.vehicle_display.axes is None:
                pass
            else:
                entrance_idx = self.current_node.idx
                exit_idx = self.current_node.front.idx
                turn_track = self.display_component.turns[entrance_idx,
                                                          exit_idx]
                self.vehicle_display.move(turn_track,
                                         time_per_move=self.move_duration,
                                         frames_per_move=self.frames_per_move)
                self.vehicle_display.hide()
                
            # We must now move the vehicle display to the next road/lane
            Exit = self.current_node.front
            self.move_display_back_to_road(Exit)
            
        
        #----------------------------------------------------------------------
        
        elif self.move_type == 'full cross intersection':
            
            if self.vehicle_display.axes is not None:
                # If the road displays it then hide it.
                self.vehicle_display.hide()
                
            self.display_component = self.current_node.intersection_display
            
            if self.display_component is None:
                self.vehicle_display.axes = None
                
            else:
                
                entrance_idx = self.current_node.idx
                exit_idx = self.current_node.front.idx
                # Extract
                coords = self.display_component.entrances[entrance_idx]
                bearings = self.display_component.bearings[entrance_idx]
                axes = self.display_component.axes
                
                # Apply
                self.vehicle_display.hide()  
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show()
                
#                # Move to waiting zone
#                waiting_zone = self.display_component.wait_zones[entrance_idx]
#                self.vehicle_display.move(waiting_zone,
#                                          time_per_move=self.move_duration,
#                                          frames_per_move=3)
                
                entrance_idx = self.current_node.idx
                exit_idx = self.current_node.front.idx
                turn_track = self.display_component.turns[entrance_idx,
                                                          exit_idx]
                self.vehicle_display.move(turn_track,
                                         time_per_move=self.move_duration,
                                         frames_per_move=self.frames_per_move)
                self.vehicle_display.hide()
                
            # We must now move the vehicle display to the next road/lane
            Exit = self.current_node.front
            
            
            self.move_display_back_to_road(Exit)
         
        #----------------------------------------------------------------------
        
        elif self.move_type == 'enter pedestrian crossing':
            
            
            if self.vehicle_display.axes is not None:
                # If the road displays it then hide it.
                self.vehicle_display.hide()

                
            self.display_component = self.current_node.pedestrian_crossing_display
            
            
            if self.display_component is None:
                
                self.vehicle_display.axes = None
                
            else:
                
                if self.current_node.idx == 0:  # W to E
                    coords = self.display_component.W_to_E_entrance
                    bearings = self.display_component.W_to_E_bearings
                    track = self.display_component.W_to_E_track
                else:  # idx == 1: E to W
                    coords = self.display_component.E_to_W_entrance
                    bearings = self.display_component.E_to_W_bearings
                    track = self.display_component.E_to_W_track
                    
                axes = self.display_component.axes
                
                self.vehicle_display.reset_coords(coords)
                self.vehicle_display.reset_bearings(bearings)
                self.vehicle_display.reset_axes(axes)
                self.vehicle_display.show()
                
                # Allocate the track to move along
                self.vehicle_display.setup_track(track,current_track_idx=0)

        
        #----------------------------------------------------------------------
        
        elif self.move_type == 'move withing pedestrian crossing':
            
            if self.vehicle_display.axes is None:
                pass
            else:
                self.vehicle_display.move_along_track(moves=1,
                                                      time_per_move=self.move_duration,
                                                      frames_per_move=self.frames_per_move)
        
        #----------------------------------------------------------------------
        
        
        elif self.move_type == 'exit pedestrian crossing':
            
            if self.vehicle_display.axes is None:
                pass
            else:
                
                self.vehicle_display.hide()

            Exit = self.current_node.front  
            self.move_display_back_to_road(Exit)
            
                
    
        #----------------------------------------------------------------------

        elif self.move_type is None:
            # Do nothing.
            pass
        
        #----------------------------------------------------------------------
        
        else:
            raise Exception('Undocumented case: {0}'.format(self.move_type))
    
        return None
    
    #--------------------------------------------------------------------------
    
    def schedule_pedestrian_crossing_entrance(self):
        
        # schedule_pedestrian_crossing_entrance() & schedule_exit_pedestrian_crossing
        # are the same and are identical to schedule_standard_move()
        
        self.last_time = self.time
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std)
        self.calibrate_forward(start_node=self.current_node,
                               aranged_time=aranged_time)
        Queue.push(self)

        self.n_nodes = 1
        
        return None
    
    #--------------------------------------------------------------------------
    
    def schedule_move_within_pedestrian_crossing(self):
        
        self.last_time = self.time
        
        if self.current_node.front.locked:
            pedestrian_crossing = self.current_node.front.pedestrian_crossing
            self.time = pedestrian_crossing.request_unlock_time() +\
                        np.random.uniform(1e-3,self.delay_time)
            self.wait = True
        
        else:
            aranged_time = self.time + np.random.normal(self.mean,
                                                        self.std)
            self.calibrate_forward(start_node=self.current_node,
                                   aranged_time=aranged_time)
            # calibrate_forward updates self.time within the function.
            
        Queue.push(self)
        
        self.n_nodes = 1
        
        return None
    
    #--------------------------------------------------------------------------
    
    def schedule_exit_pedestrian_crossing(self):
        
        self.last_time = self.time
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std)
        self.calibrate_forward(start_node=self.current_node,
                               aranged_time=aranged_time)
        Queue.push(self)
        
        
        self.n_nodes = 1
        
        return None
    
    
    #--------------------------------------------------------------------------
    
    def schedule_buffer_entrance(self):
        
        self.last_time = self.time
        
        entrance_idx = self.current_node.idx  # it is an entrance so this is allocated
        self.current_node.flared_traffic_light.choose_exit(entrance_idx)
        
        # choose_exit has allocate the current node (an entrance node) the
        # correct buffer as it front attribute such that it can move to it.
        exit_idx = deepcopy(self.current_node.flared_traffic_light.exit_idx)
        # deepcopy plays an important role to ensure the exit does
        # not change if another vehicle calls choose_exit from the same
        # flared traffic light.
        self.designated_traffic_light_exit_idx = exit_idx
        Exit = self.current_node.flared_traffic_light.exits[exit_idx]
        self.designated_traffic_light_exit = Exit
        # designated_traffic_light_exit_idx will be used if the vehicle is
        # to enter a large buffer.
        
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std)
        self.calibrate_forward(start_node=self.current_node,
                               aranged_time=aranged_time)

        Queue.push(self)
        
        
        self.n_nodes = 1
        
        return None
    
    
    #--------------------------------------------------------------------------
    
    def schedule_buffer_exit(self):
        
        if self.current_node.locked:
            
            self.time = self.current_node.flared_traffic_light.request_unlock_time()
            self.wait = True
        
        else:
        
            self.current_node.front = self.designated_traffic_light_exit
            aranged_time = self.time + np.random.normal(self.mean,
                                                        self.std,
                                                        size=FlaredTrafficLight.size).sum()
            self.calibrate_forward(start_node=self.current_node,
                                   aranged_time=aranged_time)

        Queue.push(self)
        
        self.n_nodes = FlaredTrafficLight.size
        
        return None
    
    #--------------------------------------------------------------------------
    
    def schedule_buffer_move(self):
        
        self.last_time = self.time
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std)
        self.calibrate_forward(start_node=self.current_node,
                               aranged_time=aranged_time)
        Queue.push(self)
        
        self.n_nodes = 1
        
        return None
    
    #--------------------------------------------------------------------------
    
    def schedule_source_arrival(self):
        
        if (self.current_node.front.overflow_protection and 
            self.current_node.front.lane.is_full):
            
            lane = self.current_node.front.lane
            
            raise Exception('{0} is full and cannot accommodate'.format(lane)+\
                            ' any further'+\
                            ' arrivals. To prevent the simulation from'+\
                            ' freezing the kernel, the simulation has been'+\
                            ' stopped. Consider lengthening the lane or '+\
                            'lowering the arrival rate. If one wishes, '+\
                            'set overflow_protection to False in {0}'.format(lane)+\
                            ' to prevent this message from appearing again.')
        
        self.last_time = self.time
        # Arange a time of when the vehicle moves to the next node.
        aranged_time = self.time
        # Compensate/calibrate times for the possibility of a delay caused by
        # the nodes infront remaining occupied at the aranged time.
        self.calibrate_forward(start_node=self.current_node,
                               aranged_time=aranged_time)
        # Put the scheduled request into the heap.
        Queue.push(self)
            
        self.n_nodes = 1
        
        return None
        

        
    #--------------------------------------------------------------------------
    
    def schedule_intersection_move(self):
        
        self.last_time = self.time
        
        entrance_idx = self.current_node.idx
        intersection = self.current_node.intersection
        
        if not self.exit_chosen:
            
            # We do not want to choose exits multiple times
            
            intersection.choose_exit(entrance_idx)
            exit_idx = deepcopy(intersection.current_exit_idx)  # just to be safe
            # Get ready for calibration by forming completely connected chain
            Exit = intersection.exits[exit_idx]
            self.current_node.front = Exit
            Exit.behind = self.current_node
            self.exit_chosen = True
        
        else:
            entrance_idx = self.current_node.idx
            exit_idx = self.current_node.front.idx
            
            
        # Get aranged time to be calibrated
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std,
                                                    size=Intersection.size).sum()
        # Calibrate time: it might change.
        self.calibrate_forward(self.current_node,aranged_time)
        
        
        

        
        # The special cases occur when two vehicles from the main flow both
        # attempt to perform a right turn. The two vehicles become locked
        # in a scenario of infinite "politeness" where the two keep waiting 
        # for each other. Ultimately, no vehicle ends up executing a move.
        # We base the decision one which vehicle moves first based in which
        # vehicle halted first.

        
        get_opposing_idx = lambda x: (x+2)%4
        opposing_idx = get_opposing_idx(entrance_idx)
        opposing_entrance = intersection.entrances[opposing_idx]
        
        if opposing_entrance.occupied:
            # We check occupied first as this means vehicle is not None.
            # If we did not do it this way then an AttributeError would be 
            # raised as NoneType does not have waited_at_intersection as an
            # attribute.
            if (opposing_entrance.vehicle.waited_at_intersection and 
                self.waited_at_intersection):

                other_vehicle = opposing_entrance.vehicle
                wait_times = [self.wait_time_stamp,
                              other_vehicle.wait_time_stamp]
                idx_to_move_first = np.argmin(wait_times)
                
                if idx_to_move_first == 0:
                    self.time = aranged_time 
                    other_vehicle.time = aranged_time +\
                                         np.random.uniform(1e-3,self.delay_time)
                else:
                    self.time = other_vehicle.time +\
                                np.random.uniform(1e-3,self.delay_time)
                                
                self.move_type = 'partial cross intersection'
                self.wait = False
                other_vehicle.wait = False
                other_vehicle.move_type = 'partial cross intersection'
                self.exit_chosen = False   # RESET for next intersection component
                other_vehicle.exit_chosen = False
                Queue.push(self)
                self.object_type = Intersection
                other_vehicle.object_type = Intersection
                
                Queue.heapify()
                Queue.push(self)
                
                return None
            else:
                # Allow it to pass to be assessed by right_of_way.
                # It will be give proceed as False along with a new time
                pass



        proceed,time = intersection.right_of_way(entrance_idx,
                                                 exit_idx,
                                                 aranged_time)
        
        if proceed:
            self.time = time 
            self.exit_chosen = False  # RESET for next intersection component
            
        else:
            self.wait = True
            self.time = time
            # FIXME: if we use wait then it will call schedule_intersection_move()
            # once more. In the process it will choose a new exit again.
            # if an exit has been chosen we must not let it choose again.
            # This holds for all schedule functions that have a wait element
            # to it. This must be corrected for.
        
        
        
        Queue.push(self)
        
        
        self.n_nodes = Intersection.size
        
        return None
    
    
    
    
    #--------------------------------------------------------------------------
    def schedule_on_ramp_move(self):
        
        self.last_time = self.time
        
        # The ideal time we expect
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std,
                                                    size=OnRamp.size).sum()
        entrance = self.current_node
        on_ramp = self.current_node.on_ramp
        Exit = on_ramp.exit
        # Do the below to make nodes ready for calibration.
        Exit.behind = entrance   

        self.calibrate_forward(entrance,aranged_time)
        # We now have a time that compensates for delays ahead. Only now can
        # we check if we have right of way.
        
        proceed,time = on_ramp.right_of_way(aranged_time)
        
        
        if proceed:
            self.time = time  
            
        else:
            self.wait = True
            self.time = time
            
       # Set the main-flow exit behind back to the main-flow entrance. 
       # It might have been altered. These main flow must remain connected
       # such that calibration works on nodes in the road object that is used
       # for the main-flow entrance
        on_ramp.exit.behind = on_ramp.main_flow_entrance
        
        Queue.push(self)
        
        self.n_nodes = OnRamp.size
        
        
        return None
    
    
    #--------------------------------------------------------------------------
    
    def schedule_off_ramp_move(self):
        

        self.last_time = self.time

        # A simple process. Just like a standard move except for the fact
        # That we have to choose an exit.
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std,
                                                    size=OffRamp.size).sum()


        chosen_exit = self.current_node.off_ramp.choose_exit()
        self.current_node.front = chosen_exit
        chosen_exit.behind = self.current_node  # Complete chain for calibration
            
        
        # NOTE: we put no wait option here. Off ramp just connects the out_node
        # of a road/lane object to the in_node of another road/lane object.
        # Hence, it connects a road to the chosen road (off or stay on) and just
        # keeps track of what passes it. We thus treat it like a standard_move().
        self.time = aranged_time
        self.calibrate_forward(self.current_node,aranged_time)
    
        Queue.push(self)
        
        self.n_nodes = OffRamp.size
        
        return None
        
    
    #--------------------------------------------------------------------------
    
    def schedule_circle_entrance(self):
        
        self.last_time = self.time
        
        
        
        
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std,
                                                    size=Circle.entrance_size).sum()
        
        entrance = self.current_node.front
        

        proceed,time = entrance.circle.right_of_way(entrance,aranged_time)
        

        
        if proceed:
            
            # NOTE: an exit is chosen once only.
            # We never have a scenario where an exit is to be chosen again and
            # hence replaces the old exit. This would violate the actual observed
            # probability/count of events.
            designated_exit,designated_exit_idx = entrance.circle.choose_exit(
                                                                  entrance.idx)

            self.designated_circle_exit_idx = deepcopy(designated_exit_idx)
            self.designated_circle_exit = entrance.circle.exits[self.designated_circle_exit_idx]
            
            

            
            # idx is universally understood by internal and display components.
            
            self.current_node.occupied = False
            self.current_node.vehicle = None 
            
            self.time = aranged_time
            
            self.current_node = entrance
            self.current_node.occupied = True
            self.current_node.vehicle = self
            # It is now sheculed to enter the circle at the aranged time
            # Nothing opposes or blocks its entry.
            
            # NOTE: during this time, it occupies the entrance.
            # DOES OCCUPY ENTRANCE
            
            # The vehicle has a different velocity in a circle
            self.original_velocity = self.velocity
            self.velocity = entrance.circle.within_velocity
            
            
        else:
            # Wait at entrance unitl it has right of way to proceed.
            self.current_node.occupied = True
            self.current_node.vehicle = self
            self.within_circle = False
            self.wait = True
            self.time = time + 1e-6
            # NOTE: DOES NOT OCCUPY ENTRANCE

        Queue.push(self)
        
        self.n_nodes = Circle.entrance_size
        
        return None
    
    #--------------------------------------------------------------------------
    
    
    def schedule_circle_move_or_exit(self):
        
        self.last_time = self.time
        
        # Similar to standard move. Just need to check if the current
        # node has a left that is its designated exit node.

        restore = False
        if self.current_node.left is not None:
            
            if self.current_node.left is self.designated_circle_exit:
#                print('AT EXIT !!!!!')
                original_front = self.current_node.front  # Store original to allow reset
                self.current_node.front = self.designated_circle_exit # temporary
                self.do_exit_circle = True
                self.within_circle = False
                restore = True

        # We have set front to the appropraite exit such that we can use calibrate_forward
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std)
        self.calibrate_forward(start_node=self.current_node,
                               aranged_time=aranged_time)
        # Now that calibrate_froward has been used, we can restore original front.
        if restore:
            self.current_node.front = original_front  # Loop of circle not broken anymore
        # Put the scheduled request into the heap.
        Queue.push(self)
        # NB: do_exit_circle means that move() will select left as the next node
        # and not front (as usual)
        
        
        # Restore old velocity if exiting
        if self.do_exit_circle:
            self.velocity = self.original_velocity
            delattr(self,'original_velocity')
            
        self.n_nodes = 1
        
        return None
        
    
    #--------------------------------------------------------------------------
    
    def schedule_traffic_light_move(self):
        
        self.last_time = self.time
        
        # This function is called only if the front node is known to not be occupied.
        entrance_node = self.current_node.front
        traffic_light = entrance_node.traffic_light
        
        if not self.exit_chosen:
            traffic_light.choose_exit(entrance_node.idx)
        
        
        
        
        exit_time = self.time +  np.random.normal(self.mean,
                                                  self.std,
                                                  size=TrafficLight.size).sum()
        
        # Set corrected self.time
        self.calibrate_forward(start_node=self.current_node,
                               aranged_time=exit_time)
        # Get the last allowed time for the vecicle to cross.
        accepted_distance = traffic_light.size/2 # If halfway accross then we allow it 
        max_violation_time = accepted_distance/self.velocity
        cut_off_time = traffic_light.unlock_time + max_violation_time
        # Vehicle may not cross
        if self.time > cut_off_time:
            self.time = cut_off_time 
            self.wait = True
        # Vehicle may cross
        else: 
            # We move to the front node which is an entrance node
            # This move is performed internally within this function.
            # We do not make use of .move() method.
            self.current_node.occupied = False
            self.current_node.vehicle = None
            entrance_node.occupied = True
            entrance_node.vehicle = self
            entrance_node.vehicle.time = exit_time
            self.current_node = entrance_node
            # Internal move to the entrance node is complete.
            # NOTE: in the stop street we locked it after a move was scheduled.
            # Here we do not do this. The Cycle object takes care of this.
            self.exit_chosen = False
        

        Queue.push(self)
        # By putting the vehicle into the heap, we are sheduling a move that
        # goes from the entrance to the exit.
        
        self.n_nodes = TrafficLight.size
        
        return None
    #--------------------------------------------------------------------------
    
    def schedule_stop_street_move(self):
        
        self.last_time = self.time
        
        # This function is called only if the front node is known to not be occupied.
        entrance_node = self.current_node.front
        stop_street = entrance_node.stop_street
        
        # Choose exit below 1) allocates the correct front node
        # 2) allocates the current node as behind node of the exit which is
        # important for calibrate_forward (backtracking)
        # 3) stop_street.exit_idx is created. This way we can check which exit
        # was chosen
        stop_street.choose_exit(entrance_node.idx)
        exit_time = self.time +  np.random.normal(self.mean,
                                                  self.std,
                                                  size=StopStreet.size).sum()
        self.calibrate_forward(start_node=self.current_node,
                               aranged_time=exit_time)
        self.current_node.occupied = False
        self.current_node.vehicle = None
        entrance_node.occupied = True
        entrance_node.vehicle = self
        entrance_node.vehicle.time = exit_time
        self.current_node = entrance_node
        # NOTE: we see that the current node is now an entrance node.
        # It will move to an exit node which is an out node.
        # This out node should be the in node of a Lane object.
        
        stop_street.lock()
        stop_street.update_unlock_time(self.time)
                
        Queue.push(self)
        
        self.n_nodes = StopStreet.size
        
        return None
        
    
    #---------------------------------------------------------------------------
    
    def schedule_standard_move(self):
        
        self.last_time = self.time
        
        # Arange a time of when the vehicle moves to the next node.
        aranged_time = self.time + np.random.normal(self.mean,
                                                    self.std)
        time_before_calibration = aranged_time
        # Compensate/calibrate times for the possibility of a delay caused by
        # the nodes infront remaining occupied at the aranged time.
        self.calibrate_forward(start_node=self.current_node,
                               aranged_time=aranged_time)
        # Put the scheduled request into the heap.
        if self.time > time_before_calibration:
            self.time_rescheduled = True
        
        Queue.push(self)
        
        self.n_nodes = 1
        
        return None
                    
    #---------------------------------------------------------------------------
            
    def calibrate_forward_time(self,start_node,
                                    aranged_time):
        '''
        Updates the time of the vehicle at start_node to either the
        aranged_time or a delayed version of it.
        At the end of this function expect self.time to be set to one of these
        values.
        '''
        
        current_node = start_node
        current_node.vehicle.time = aranged_time
        

        
        ######  Start procedure to check for traffic jams  #####
        while True:
            
            next_node = current_node.front
            
            
            if next_node.source_attached:
                # Specific to IN type nodes where behind is None
                # and calibration can lead to an error.
                next_node.behind = current_node
            
            if next_node is None:
                # We do schedule no time.
                # This is to allow it not to move to NoneType
                # The vehicle should go out of cicrculation.
                break
            # The node infront is occupied: 2 cases.
            if next_node.occupied:
                # Case 1: it will not be cleared when a move is to be made.

                if aranged_time <= next_node.vehicle.time:
                    current_node = next_node
#                    aranged_time = next_node.vehicle.time  # WRONG !!!!
                # Case 2: it will be cleared when a move is to be made.
                else:
#                    current_node.vehicle.time = aranged_time
                    break
            # The node infront is free.
            else:
#                current_node.vehicle.time = aranged_time
                break
        
        # Current node is the furthest front node causing the delay.
        
        # Backtrack: 
        while True:
            if current_node == start_node:
                break
            # Vehicles are to be delayed such that they do not clash with
            # the vehicle infront.
            # We will update their time. The heap also needs to be updated.
            # Note: the current vehicle is not in the heap
            behind_node = current_node.behind
            # !!!! : below
            if behind_node.vehicle is None:
#                print(current_node)
                break
            behind_node.vehicle.time = current_node.vehicle.time +\
                            np.random.uniform(1e-3,current_node.vehicle.delay_time)
            # heapify runs in O(N) to perform the update.
            Queue.heapify()
            # Heap needs to be updated because we have tampered with vehicles
            # in it.
            current_node = behind_node
        
        return None
    
    #---------------------------------------------------------------------------
    
    # Version 2 with look-ahead
    # look_ahead will be defined as the maximum number of empty (unoccupied)
    # nodes that a vehicle is willing to pass until it reaches an occupied node.
    # It will then correct its speed/velocity according to the first vehicle
    # occupied in its look-ahead range.
    
    # In the case where a vehicle occupies the node infront and the current node
    # and it does not move before this vehicle wants to move then we delay the
    # vehicle. We also correct for speed/velocity
    
    # If look_ahead is set to None then we calibrate as usual.
    # look_ahead = 1 means that we calibrate as usual BUT also correct the
    # speed/velocity
    
    # TODO: if a vehicle is obstructed then set its velocity to zero
    # for the period that it is obstructed. When the obstruction is over then
    # we need to restore the velocity to its original value.
    
    
    # velocity_correction is what fraction of the velocity difference is
    # corrected for 1 = 100%
    # TODO: should this be variable an change with the amount of nodes
    # looked ahead? Or should it have some random noise added to it.
    
    def calibrate_forward_velocity(self,start_node):
        # only looks ahead until a single vehicle is reached
        
        current_node = start_node.front
        count = 1
        
        # NOTE: we are correcting on the average velocity that is actually
        # just some hard-coded value. The actual velocity is normally
        # distributed about this. Do we perhaps base the correction on the
        # instantaneous velocity instead or some running mean????

        def get_delta(velocity,count):
            '''
            Helper function.
            '''
            if self.smooth:
                return (velocity - self.velocity)/count 
            return velocity - self.velocity


        while True:
            
            
            ### STANDARD START ###
            if current_node.occupied:
                # standard calibration
                velocity = current_node.vehicle.velocity
                delta = get_delta(velocity,count)
                self.velocity += self.velocity_correction*delta
                break
            else:
                current_node = current_node.front
                count += 1
            
            if count > self.look_ahead :
                break
            
            ### STANDARD END ###
            
            # We have selected the next node.
            # Before we process it via the STANDARD procedure, we would
            # like to check for special cases first.
            
            ### SPECIAL CASES START ###
            
            if current_node is None:
                break

            # STOP-STREET
            if current_node.stop_street_entrance:
                break
            
            # TRAFFIC LIGHT
            if current_node.traffic_light_entrance:
                
                if current_node.locked:
                    break
                else:
                    pass  # let it pass to standard calibration
                
            # CIRCLE
            if current_node.circle_entrance:
                
                if current_node.occupied:
                    pass # let it pass to standard calibration
                else:
                    break
            
            # ON-RAMP
            if current_node.on_ramp_node:
                if current_node.occupied:
                    pass # let it pass to standard calibration
                else:
                    break
                
            # OFF-RAMP
            if current_node.off_ramp_entrance:
                if current_node.occupied:
                    pass
                else:
                    break

            ### SPECIAL CASES END ###
                


        return None
            
      

    #---------------------------------------------------------------------------
    
    def calibrate_forward(self,start_node,
                               aranged_time):
        
        assert self.velocity_correction > 0 and self.velocity_correction <= 1
        assert isinstance(self.look_ahead,int)
        assert self.look_ahead >= 1 or self.look_ahead is None
        # Decide: where to put calibrate_forward_velocity
        
        # We are currently leaning toward calibrating velocity first 
        # and then calibrating the sheduled movement times.
        if self.look_ahead is not None:
            self.calibrate_forward_velocity(start_node)
        self.calibrate_forward_time(start_node,
                                    aranged_time)
        
        return None
    
    
    
    #---------------------------------------------------------------------------
    
    def calibrate_backward(self,start_node,
                                aranged_time):
        
        
        current_node = start_node
        time = aranged_time
        
        while True:
            
            
            current_node.vehicle.time = time
            # Select next node
            behind_node = current_node.behind
            # Update time with delay
            
            if behind_node is None:
                break
            
            if behind_node.vehicle is None:
                break
            
            time += np.random.uniform(1e-3,current_node.vehicle.delay_time)
            current_node = behind_node
        
        Queue.heapify()  # we have altered some times of vehicles already in
        # the heap. This must be amended.
        return None
            
    
    
    #---------------------------------------------------------------------------
    
    def place_movement_record(self):
        
        if not hasattr(self,'movement_record'):
            self.movement_record = {'time':[],
                                    'distance':[],
                                    'nodes':[],
                                    'move type':[],
                                    'velocity':[]}
            
        # TODO: can we perhaps provide a string label as well???
        
        if self.wait:
            # No movement was produced
            nodes = 0
            distance = 0
            velocity = 0
            
        nodes = self.n_nodes
        distance = Node.distance*nodes
        try:
            velocity = distance/self.move_duration
        except ZeroDivisionError:
            velocity = 0  
            
            
        self.movement_record['time'].append(self.time)
        self.movement_record['nodes'].append(nodes)
        self.movement_record['distance'].append(distance)
        self.movement_record['velocity'].append(velocity)
        self.movement_record['move type'].append(self.move_type)
        
        return None
    
    
    #---------------------------------------------------------------------------
    
    def move(self):
        

        if self.record_movement:
            self.place_movement_record()
        
        
#        print('--------------------------------------')
#        print('TIME: ',self.time)
##        print('move type: ',self.move_type)
#        print('--------------------------------------')
        
        
#        if (self.move_type == 'full cross traffic light' or
#            self.move_type == 'partial cross traffic light'):
#            
#            traffic_light = self.current_node.traffic_light
#            print('--------------------------------------')
#            print('Before Display')
#            print('Entrance: ',self.current_node.idx)
#            print('Exit (realised): ',traffic_light.current_exit.idx)
#            print('key: ',traffic_light.current_exit.key)
#            print('color: ',self.vehicle_display.color)
#            print('id: ',hex(id(self)))
#            print('traffic light: ',hex(id(traffic_light)))
#            print('time: ',self.time)
#            print('--------------------------------------')
            
        
        
        # TODO: should the below ever occur
        # The below ocurrs due to source arrivals
        # Officially a patch.
        

        
        try:

            if self.current_node.front.occupied:
                # FAILED MOVE: we will reschedule it.

                if self.move_type == 'full enter circle':
                    
                    self.waited_at_circle = True
                    self.waited_outside_circle = False
                    self.waited_at_circle_n_times = False
                    self.within_circle = True

                    
                    self.current_node.occupied = True
                    self.current_node.vehicle = self 
                    self.move_type = 'wait at circle entrance'
                    self.move_display()
                    # current node is a circle entrance
                    idx = self.current_node.idx
                    current_track_idx = self.display_component.start_idxs[idx]
                    track = self.current_node.circle_display.track
                    self.vehicle_display.setup_track(track,current_track_idx)
                    self.first_circle_move = True
                    
                    return None
                    
                elif self.move_type == 'partial enter circle':
                    
                    
                    self.waited_at_circle = False
                    self.waited_outside_circle = False
                    self.waited_at_circle_n_times = True
                    self.within_circle = True
                    
                    self.current_node.occupied = True
                    self.current_node.vehicle = self 
                    self.move_type = 'wait'
                    self.move_display()
                    
                    # current node is a circle entrance
                    idx = self.current_node.idx
                    current_track_idx = self.display_component.start_idxs[idx]
                    track = self.current_node.circle_display.track
                    self.vehicle_display.setup_track(track,current_track_idx)
                    self.first_circle_move = True
                    
                    return None
                elif self.move_type == 'exit circle':
                    # Be sure to reset the attibutes for if another circle
                    # is to be crossed in the future.
                    self.full_enter = False
                    self.partial_enter = False
                    self.waited_at_circle = False
                    self.waited_outside_circle = False
                    self.waited_at_circle_n_times = False
                    self.first_circle_move = False
                    
                elif self.move_type == 'wait at intersection':
                    pass
                
                else:

                    self.current_node.occupied = True
                    self.current_node.vehicle = self  # Is this neccessary ???????????? 
#                    new_time = self.current_node.front.vehicle.time +\
#                               np.random.uniform(1e-3,self.delay_time)
#                    self.time = new_time 
                    self.calibrate_forward(start_node=self.current_node,
                                           aranged_time=self.time)
                    self.move_type = 'wait'
                    self.move_display()
                    Queue.push(self)
                    Queue.heapify()
                    return None
                  
        except AttributeError:
            # self.current_node.front is None and None has not attribute occupied.
            pass
        
        # Check for exit
        if self.current_node.left is not None:
            
            if (self.current_node.left.occupied and
                self.move_type == 'exit circle'):
                    
                self.waited_at_circle = False
                self.waited_outside_circle = False
                self.waited_at_circle_n_times = False
                self.within_circle = True
                
                self.current_node.occupied = True
                self.current_node.vehicle = self 
                self.move_type = 'wait'
                self.move_display()
                return None
        
        # Display depends on the current settings determined by
        # schedule_move(). Hence we call it first.
        # Order: 1) schedule_move(), move_display(), move()
        self.move_display()

            
        if self.move_type == 'wait at intersection':
            self.waited_at_intersection = True
            self.wait_time_stamp = self.time
        
        
        # We reset the attribute to be used again.
        # If the code reaches this point then it will perform a successful
        # move and not be at a node where it must select an entrance anymore.
        # Hence, the placement here is accepteable.
#        if self.exit_chosen:
#            self.exit_chosen = False
        

        if self.dispose:
            
            if self.current_node.record:
                self.current_node.record_object.place_record(self)
                self.current_node.occupied = False
                self.current_node.vehicle = None
                self.has_been_recorded = True
                return None
            else:
                self.current_node.occupied = False
                self.current_node.vehicle = None
                return None
            
                
        # Component infront is not available
        if self.wait:
            
#            self.vehicle_display.swivel()
            self.wait = False
            return None
        
        # Move from entrance to exit
        # Upon exit, the stop street is unlocked
        if self.current_node.service_node:
            if self.current_node.stop_street_entrance:
                # it will move to the exit now
                self.current_node.stop_street.unlock()
            elif self.current_node.traffic_light_entrance:
                pass  # It just performs some normal move
        
        # This is intended for the temporary source nodes that
        # produce arrivals. Now move occurs.
        # One can reschedule a move.
        
        # REMOVE
        self.current_node.occupied = False
        self.current_node.vehicle = None
        
        
        if self.current_node.front is None:
                            
            return None    # Code stops here
    

        
        # SELECT NEXT NODE
        
        if self.do_exit_circle:
            # select left
#            print('PERFORM CIRCLE EXIT !!!!!!!!')
            self.current_node = self.current_node.left
            self.do_exit_circle = False
            
        else:
            # STANDARD MOVE
            # select front
            self.current_node = self.current_node.front

            
        # CARRY OVER  
        self.current_node.occupied = True
        self.current_node.vehicle = self
        

        if self.current_node.record:
            if self.has_been_recorded:
                self.current_node.record_object.place_record(self)
            
        
        return None
        
    #--------------------------------------------------------------------------- 
        
    @property
    def move_duration(self):
        assert self.last_time is not None
        return self.time - self.last_time
    
    #---------------------------------------------------------------------------
    
    @property
    def mean(self):
        # Use this in conjunction with self.std to get the aranged_time for 
        # scheduling a movement.
        return Node.distance/self.velocity
    
    #---------------------------------------------------------------------------
    
    def __eq__(self,other):
        return self.time == other.time
        
    #---------------------------------------------------------------------------
        
    def __lt__(self,other):
        return self.time < other.time
        
    #---------------------------------------------------------------------------
        
    def __gt__(self,other):
        return self.time > other.time
        
    #---------------------------------------------------------------------------
        
    def __repr__(self):
        if self.arrival:
            return 'Arrival ({0})'.format(round(self.time,4))
        return 'Vehicle ({0})'.format(round(self.time,4))
        
#-------------------------------------------------------------------------------












