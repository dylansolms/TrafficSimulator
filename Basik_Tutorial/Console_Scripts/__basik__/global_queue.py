
#NB : Philosophy: MOVE first and then SCHEDULE. This allows a vehicle that
# occupies a given node to always have plans set in the future. This avoids
# scenarios such as an occupied node being queried about its vehicle move
# time but this time then happens to be in the past. This means that the node
# That queries it would not know when the occupied node might be unoccupied.



import heapq
import importlib
import sys
#import .global_queue  # import itself

import numpy as np
import warnings





#------------------------------------------------------------------------------

#__all__ = ['Queue']

# TODO update the below
modules_using_Queue = ('__basik__.FlaredTrafficLightObject.flared_traffic_light',
                       '__basik__.node',
                       '__basik__.obstruction',
                       '__basik__.PedestrianCrossingObject.pedestrian_crossing_event',
                       '__basik__.PedestrianCrossingObject.pedestrian_crossing',
                       '__basik__.TrafficLightObject.traffic_light',
                       '__basik__.VehicleObject.vehicle',
                       '__basik__.global_queue',# put itself in there as well,
                       '__main__')  # put itself in there as well.

Queue = None
AllQueues = []

#------------------------------------------------------------------------------

class GlobalQueue(object):
    
    '''A Priority Queue/Heap that allows simulation events to occur in the
    correct order. It is the GlobalQueue that drives the discrete-event
    system.
    
    
    Attributes:
    -----------
    Q: list (heapq heap)
        The heapq module in Python uses lists. This data-structure allows
        for O(1) access to the smnallest element i.e. the earliest event to
        occur.
    content: list (heapq heap)
        This is the same as Q. The name is more intuitive.
    t: float
        Time of the last heap element retrieved using the pop method.
    current_component: object
        This is the last object retrieved from the heap using the pop method.
        It can be a vehicle, an arrival, traffic light signal change or a
        pedestrian crossing event.
    start_time: float
        The time that the simulation started. This is specified by the user
        in the run method.
    end_time: float
        The time that the simualtion ended. This is specified by the user
        in the run method.
    current_time: float
        Refers to self.t
    time: float
        Refers to self.t
    latest_event: object (__basik__ object)
        The object in the heap with the largest scheduled time-stamp.
    latest_time: float
        The largest time-stamp present in the heap/global_queue.
    latest_arrival_time: float
        The time of the last arrival scheduled. If there are not any more
        arrivals in the heap then it returns the time of the last arrival that
        ocurred (see last_arrival).
    last_arrival_time: float
        The time of the last arrival that occurred.
    '''
    

    #--------------------------------------------------------------------------
    
    def __init__(self):
        self.Q = []
        GlobalQueue.new(self)
        
    #--------------------------------------------------------------------------
    
    def push(self,object_:object):
        '''Push the value item onto the heap, maintaining the heap invariant
        
        The above description comes directly from the heapq documentation. 
        This method is just a wrapper for heap.heappush
        
        Parameters:
        -----------
        object_ : object
            Either:
                1) __basik__.VehicleObject.vehicle.Vehicle (can be in arrival state)
                2) __basik__.TrafficLightObject.traffic_light_cycle.TrafficLightCycle
                3) __basik__.FlaredTrafficLightObject.flared_traffic_light_cycle.FlaredTrafficLightCycle
                4) __basik__.PedestrianCrossingObject.pedestrian_crossing_event.PedestrianCrossingEvent
                5) __basik__.obstruction.Obstruction
    
        Returns:
        --------
        None
        
        See Also:
        ---------
        heapq.heappush
        '''
        heapq.heappush(self.Q,object_)
        return None
    
    #--------------------------------------------------------------------------
    
    def pop(self):
        '''Pop and return the smallest item from the heap, maintaining the heap invariant.
        
        The above description comes directly from the heapq documentation. 
        This method is just a wrapper for heap.heappop
        
        Returns:
        -------
        Either:
            1) __basik__.VehicleObject.vehicle.Vehicle (can be in arrival state)
            2) __basik__.TrafficLightObject.traffic_light_cycle.TrafficLightCycle
            3) __basik__.FlaredTrafficLightObject.flared_traffic_light_cycle.FlaredTrafficLightCycle
            4) __basik__.PedestrianCrossingObject.pedestrian_crossing_event.PedestrianCrossingEvent
            5) __basik__.obstruction.Obstruction
    
        Raises:
        --------
        IndexError:
            self.Q is empty.
        '''
        return heapq.heappop(self.Q)
    
    #--------------------------------------------------------------------------
    
    def unique(self):
        '''Ensures that no duplicate of an event exists.
        '''
        self.Q = (np.unique(self.Q)).tolist()
    
    #--------------------------------------------------------------------------
    
    def heapify(self):
        '''Transform list x into a heap, in-place, in linear time.
        
        The above description comes directly from the heapq documentation. 
        This method is just a wrapper for heap.heapify
        
        Returns:
        --------
        None
        '''
        heapq.heapify(self.Q)
        
        return None
    
    #--------------------------------------------------------------------------
    
    def clear(self):
        '''Makes self.Q (as a result self.content) into an empty list.
        
        Returns:
        --------
        None
        '''
        # Remove all vehicles from the system.
        # These are physical objects and not events.
        for event in self.Q:
            if hasattr(event,'is_vehicle'):
                node = event.current_node
                node.occupied = False
                node.vehicle = None
        # Remove all events. This includes scheduled vehicle moves.
        self.Q.clear()
        
        return None
    
    #--------------------------------------------------------------------------
    
    @property
    def current_time(self):
        return self.t
    
    #--------------------------------------------------------------------------
    
    @property
    def time(self):
        return self.t
    
    #--------------------------------------------------------------------------
    
    @property
    def content(self):
        return self.Q
    
    #--------------------------------------------------------------------------
    
    @property
    def latest_time(self):
        return max(self.Q).time
    
    #--------------------------------------------------------------------------
    
    @property
    def latest_event(self):
        return max(self.Q)
    
    #--------------------------------------------------------------------------
    
    @property
    def latest_arrival_time(self):
        latest = -np.inf  # very small value
        for event in self.Q:
            if hasattr(event,'is_vehicle'):
                if event.arrival:
                    if event.time > latest:
                        latest = event.time
        if latest == -np.inf:
            # No arrivals were found
            return self.last_arrival_time
        
        return latest
                    
    
    #--------------------------------------------------------------------------
    
    def run_single_event(self):
        
        '''Extracts an object from the heap, performs the event scheduled for 
        this object and then schedules a future event for the object. At this
        point, the object will be placed back into the heap using the push
        method.
        
        Notes:
        ------
        This function serves as the workhorse for the run method. The run method 
        could be written without using run_single_event. The convenience of
        run_single_event lies in the fact that it allows for the simulator to 
        be run in such a way as to faciliate Temporal Difference Reinforcement
        Learning methods such as Q-learning and TD(0). These methods require
        a single step of a simualtion to be run in order to update the relevant
        action-state value pairs Q(s,a).
        
        Returns:
        --------
        bool
            The status of whether the simulation will continue or not.
        
        '''
        
        if not bool(self.Q):
            message = 'Simulation ended!'+\
            'self.Q is empty. No more events exist in this simulation.'
            warnings.warn(message)
            return False  # empty queue
        
        self.unique()   # FIXME:
        self.heapify()  # FIXME:
        component = self.pop()
        self.current_component = component

        
        if hasattr(component,'is_obstruction'):
            # Introduction and removal of obstruction events as well
            # as pedestrian crossing events.
            
            if component.do_activate:
                component.activate()
                self.t = component.start_time
            else:
                component.deactivate()
                self.t = component.end_time
            return True
        

        elif hasattr(component,'is_cycle'):
            # Traffic light and flared traffic light cycle transitions.
            component.activate()
            self.t = component.start_time
            return True
            
        else:
            vehicle = component
            
            
        if vehicle.arrival:
            self.last_arrival_time = vehicle.time
            vehicle.arrival = False
            
        self.t = vehicle.time
        
#        if self.t > self.end_time:
#            return False
        
        vehicle.move()
        if not vehicle.dispose:
            vehicle.schedule_move()
        
        # NOTE: we have moved the below snippet of code. There is a good reason.
        # In original placement we have the scenario where not all the vehicles
        # placed on the simulation can be found in the global queue. This leads
        # to "dead" vehicles. The result is that certain nodes remain occupied
        # indefinitely. This makes running another simulation on the same
        # setup impossible.
        if self.t > self.end_time:
            return False
        
        return True  # do we continue with the simualtion or not
    
    #--------------------------------------------------------------------------
    
    def run(self,end_time=np.inf,
                 start_time=0,
                 print_time=False,
                 print_count=1):
        
        '''Runs the simualtion from the start time until either the end_time
        is reached or the heap (self.Q) becomes empty and no further events
        exist. Note that a warning will be raised, using the warnings module, to
        notify the user if the simulation had ended pre-maturely due to a the
        heap being empty.
        
        Parameters:
        -----------
        end_time: float
            Time at which a non-empty simulation will end. If set to numpy.inf
            then the simulation will run until the queue is empty.
        start_time: float
            Time at which a simulation will start.
        print_time: bool
            If True, it will print the time of each extracted event.
        print_count: int
            If print_time is set to True, then the time will print every nth
            event.
            
        Raises:
        --------
        AssertionError
            end_time must be greater than start_time.
        TypeError:
            print_count must be an int
        ValueError:
            print_count >= 1
        
        Returns:
        --------
        None
        
        '''
        
        assert end_time > start_time
        if print_time:
            if not isinstance(print_count,int):
                raise TypeError('print_count must be an int')
            if print_count < 1:
                raise ValueError('print_count >= 1')
        
        # if time = inf then it will run until the heap is empty.
        
        self.t = start_time
        
        self.start_time = start_time
        self.end_time = end_time
        
        
        continue_simulation = True
        
        count = 0  # for 
        
        while continue_simulation:
            
            continue_simulation = self.run_single_event()
            if print_time:
                count += 1
                if count%print_count == 0:
                    print('Time: ',self.t)
        
        return None
    
    #--------------------------------------------------------------------------

    def __run(self,end_time=np.inf,
                 start_time=0):
        
        '''Deprecated
        '''
        
        # Deprecated
        
        # if time = inf then it will run until the heap is empty.
        
        self.t = start_time
        
        self.start_time = start_time
        self.end_time = end_time

        while True:
            
            if not bool(self.Q):
                break
            
            self.unique()   # FIXME:
            self.heapify()  # FIXME:
            component = self.pop()
            self.current_component = component

            
            if hasattr(component,'is_obstruction'):
                # Introduction and removal of obstruction events as well
                # as pedestrian crossing events.
                
                if component.do_activate:
                    component.activate()
                    self.t = component.start_time
                else:
                    component.deactivate()
                    self.t = component.end_time
                continue
            

            elif hasattr(component,'is_cycle'):
                # Traffic light and flared traffic light cycle transitions.
                component.activate()
                self.t = component.start_time
                continue
                
            else:
                vehicle = component
                
                
            if vehicle.arrival:
                vehicle.arrival = False
                
            self.t = vehicle.time
            
            if self.t > end_time:
                break
            
            vehicle.move()
            if not vehicle.dispose:
                vehicle.schedule_move() 

        return None
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        return 'Queue ({0})'.format(hex(id(self)))
    
    #--------------------------------------------------------------------------
    
    def reload(Queue):
        
        '''Takes an existing Queue and makes it the designated GlobalQueue to
        be used by __basik__. The user should expect to find thus Queue in the
        global namespace (globals()) of __main__ and __basik__ modules that make
        use of the GlobalQueue such as __basik__.VehicleObject.vehicle.
        
        Raises:
        -------
        AssertionError:
            The Queue is not a class instance of __basik__.global_queue.GlobalQueue.
        
        Returns:
        --------
        None
        '''
        
        # Make sure we have a GlobalQueue object
        assert isinstance(Queue,GlobalQueue)

        if Queue not in AllQueues:
            AllQueues.append(Queue)
         
        for module_name in modules_using_Queue:
            
            # Manually put it into the global namespace if not already there.
            
            
            if module_name not in sys.modules:
                module = importlib.__import__(module_name)
                sys.modules[module_name] = module
            else:
                module = sys.modules[module_name]
                
            # These modules have the same Queue attribute now.
            # This means they all make use of the same Queue.
            # Hence, the Queue truly is global.

            setattr(module,'Queue',Queue)
            setattr(module,'AllQueues',AllQueues)

            
        return None
        
    #--------------------------------------------------------------------------
    
    def new(new_Queue=None):
        
        '''A function that creates a new GlobalQueue to be used by __basik__
        
        Parameters:
        ------------
        new_Queue: __basik__.global_queue.GlobalQueue or None
            If None is provided a brand new GlobalQueue will be made and 
            activated using the reload method. If an existing GlobalQueue object
            is provided then this /method will only seek to activate it via
            the reload method.
        
        Returns:
        --------
        __basik__.global_queue.GlobalQueue
        '''
        
        if new_Queue is None:
            new_Queue = GlobalQueue()
        
        GlobalQueue.reload(new_Queue)
        
        return new_Queue
        
    #--------------------------------------------------------------------------
    
    @property
    def existing():
        '''Returns a list of all existing GlobalQueue objects in the globals namespace.
        '''
        return AllQueues
    
    #--------------------------------------------------------------------------
    
    @property
    def current():
        '''Returns the current GlobalQueue in use by __basik__.
        '''
        return globals()['Queue']
    
    #--------------------------------------------------------------------------
    
    def clear_existing():
        '''Removes all existing GlobalQueue objects from the Python 
        namespace and populates it with a single new GlobalQueue that will 
        be used by __basik__.
        
        Returns:
        --------
        None
        '''
        
        try:
            globals()['AllQueues'].clear()
        except KeyError:
            pass
        
        # Re-populate the name-space with new unused Queue
        GlobalQueue.new()
        
        return None
    
    #--------------------------------------------------------------------------


    

#------------------------------------------------------------------------------

# Create a new Queue if there is not one already.
#try:
#    Queue = globals()['Queue']
#except KeyError:
#    GlobalQueue.new()
    
    







