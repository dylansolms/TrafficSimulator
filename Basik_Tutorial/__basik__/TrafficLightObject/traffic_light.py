


import numpy as np
from .traffic_light_cycle import TrafficLightCycle,default_cycle
from ..utils import cycle_list,shuffle_list
from ..global_queue import Queue
from ..node import Node

from copy import deepcopy

#-------------------------------------------------------------------------------       

default_in = {'N':None,'E':None,'S':None,'W':None}

#-------------------------------------------------------------------------------       
 
default_out = {'N':None,'E':None,'S':None,'W':None} 

#------------------------------------------------------------------------------

class TrafficLight(object):
    
    
    '''A traffic light where a single lane exists for all vehicles whether
    they would like to turn right, left or proceed forward.
    
    Attributes:
    -----------
    entrances: np.ndarray(dtype=object)
        A numpy array containing all the __basik__.node.Nodes objects that form
        the entrances. Consult keys to see which index corresponds to which 
        entrance. Alternatively, the __basik__.node.Nodes.key will also reveal this.
    exits: np.ndarray(dtype=object)
        A numpy array containing all the __basik__.node.Nodes objects that form
        the exits. Consult keys to see which index corresponds to which exit. 
        Alternatively, the __basik__.node.Nodes.key will also reveal this.
    keys: list
        Allows one to check which index corresonds to which direction.
    tpm: numpy.ndarray
        A transition probability matrix. It is row stochastic.
    active_entrance: list
        A list that contains all the entrances which currently have a
        green light/right to proceed.
    
    '''
    
    INTERNAL = True
    SETUP_CYCLES = True
    
    size = 2  # 2 meters <==> two nodes
        
    #--------------------------------------------------------------------------
    
    def __init__(self,in_nodes=default_in,
                      out_nodes=default_out,
                      cycle_schedule=default_cycle):
        
        '''
        Parameters:
        -----------
        in_nodes: dict
            The out_node (OUT) of a __basik__.RoadObject.lane.Lane. should be
            in this dictionary. If set to None then an entrance for that
            direction will not exist. 
        out_nodes: dict
            The in_node (IN) of a __basik__.RoadObject.lane.Lane. should be
            in this dictionary. If set to None then an exit for that
            direction will not exist. 
        cycle_schedule: list
            A list containing a combination of "flow" functions that can be found
            in __basik__.FlowFunction.non_flared or 
            __basik__.TrafficLightObject.traffic_light_cycle.
        '''
        
        self.keys = ['N','E','S','W']
        self.idxs = [0,1,2,3]
        self._setup_entrances_and_exits(in_nodes,out_nodes)
        self.cycle_schedule = cycle_schedule
        self.tpm = None
        self.unlock_time = None
        self.n_requests = 0
        self.active_entrances = []
        self.display = None
        
    #--------------------------------------------------------------------------
          
    def setup_cycles(self,end_time,
                          start_time=0,
                          fixed_cycle=True):
        
        '''Use the provided cycle_schedule to schedule the various states that
        the traffic light will take through the simulation.
        
        __basik__.TrafficLightObject.traffic_light_cycle.TrafficLightCycle
        objects are placed in the current GlobalQueue used by __basik__.
        
        Parameters:
        -----------
        end_time: float
            The last allowed time for a transition in traffic light states to
            occur.
        start_time:
            Should be kept at zero or should correspond to the start_time of the
            simulation as a whole. This is to allow the traffic light to 
            actually set up a state. 
        fixed_cycle: bool
            If set to True it will follow the cycle specified by cycle_schedule.
            If makes this list cyclic.
            If set to False, it will draw with uniform probability a flow
            function from the cycle_schedule.
            
        Raises:
        -------
        AssertionError:
            end_time must be greater than start_time but also less than
            numpy.inf
            
        Returns:
        --------
        None
        '''
                
        # Initial time set to zero
        T = end_time
        t = start_time
        # Extract firsy cycle specification set given.
        # Later on we will use cycle_list instead
        cycle_specs = self.cycle_schedule[0]
        
        while True:
            # Create a sheduled cycle change/transition
            scheduled_cycle = TrafficLightCycle(t,cycle_specs,
                                                traffic_light=self) 
            # It is now in the heap along with vehicle that want to
            # arrive or execute moves.
            Queue.push(scheduled_cycle)
            # We need to know when this cycle is sheduled to end as this is
            # when the next cycle will take over.
            t = scheduled_cycle.end_time
            # Choose next cycle. This can be from a fixed cycle or we can
            # randomly choose another cycle that is not the current one.
            if t >= T:
                break
            
            if fixed_cycle:
                cycle_specs = cycle_list(self.cycle_schedule)
            else:
                cycle_specs = shuffle_list(self.cycle_schedule,
                                           repeats_allowed=False)
        return None
            
    
    #--------------------------------------------------------------------------
    
    def _setup_entrances_and_exits(self,in_nodes,out_nodes):
        
        self.in_nodes = in_nodes
        self.out_nodes = out_nodes
        
        self.entrances = np.zeros(4,dtype=object)
        self.exits = np.zeros(4,dtype=object)
        
        for idx in range(4):
            
            key = self.keys[idx]
            
            # Setup entrances
            entrance_node = self.in_nodes[key]
            
            if entrance_node is None:
                entrance_node = Node()
            
            entrance_node.service_node = True
            entrance_node.traffic_light_entrance=True
            entrance_node.traffic_light = self
            entrance_node.idx = idx
            entrance_node.key = key
            entrance_node.front = None
            self.entrances[idx] = entrance_node
            
            # Setup exits
            exit_node = self.out_nodes[key]
            
            if exit_node is None:
                exit_node = Node()
            
            exit_node.service_node = True
            exit_node.traffic_light_exit=True
            exit_node.traffic_light = self
            exit_node.idx = idx
            exit_node.key = key
            exit_node.behind = None
            self.exits[idx] = exit_node
            
        return None
            
    #--------------------------------------------------------------------------        
            
    def lock(self,to_lock):
        
        for idx in to_lock:
            self.entrances[idx].locked = True
        
        return None
    
    #--------------------------------------------------------------------------
    
    def unlock(self,to_unlock):
        self.active_entrances.clear()
        for idx in to_unlock:
            self.entrances[idx].locked = False
            self.active_entrances.append(self.keys[idx])
            
    #--------------------------------------------------------------------------

    def choose_exit(self,idx):
        
        
        chosen_entrance = self.entrances[idx]
        assert chosen_entrance.locked == False
        chosen_exit_idx = np.random.choice(a=self.idxs,p=self.tpm[idx])
        chosen_exit = self.exits[chosen_exit_idx]
        
        chosen_exit = np.random.choice(a=self.exits,p=self.tpm[idx])
        chosen_entrance.front = chosen_exit
        chosen_exit.behind = chosen_entrance
        
        self.entrance_idx = idx
        self.exit_idx = chosen_exit_idx
        
        self.current_entrance = chosen_entrance
        self.current_exit = chosen_exit
        
        return None
    
    #--------------------------------------------------------------------------
    
    def update_unlock_time(self,time):
        self.unlock_time = time
        self.n_requests = 0
        return None
    
    #--------------------------------------------------------------------------
    
    def request_unlock_time(self):
        self.n_requests += 1
        time =  self.unlock_time + self.n_requests*1e-3
        return deepcopy(time)
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        return 'Traffic Light ({0})'.format(hex(id(self)))
        
    
    
    
#------------------------------------------------------------------------------  