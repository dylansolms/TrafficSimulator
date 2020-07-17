import numpy as np
from .flared_traffic_light_cycle import FlaredTrafficLightCycle,default_cycle
from ..utils import cycle_list,shuffle_list
from ..global_queue import Queue
#from ..__init__ import Queue


from ..node import Node



from copy import deepcopy

#-------------------------------------------------------------------------------       

default_in = {'N':None,'E':None,'S':None,'W':None}

#-------------------------------------------------------------------------------       
 
default_out = {'N':None,'E':None,'S':None,'W':None} 

#------------------------------------------------------------------------------

class FlaredTrafficLight(object):
    
    '''A Flared Traffic Light allows for each entrance side to have a lane
    designated for right turns (these manuvers are typically halted) only while 
    the other lane handles vehicles that turn left and cross ahead.
    
    
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
    
    size = 2  
    
    large_buffer_size = 3
    small_buffer_size = 3  # for right turn only
    
    
    truth = np.array([[None,True,True,False],
                      [False,None,True,True],
                      [True,False,None,True],
                      [True,True,False,None]],dtype=object)
        
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
            in __basik__.FlowFunction.flared or 
            __basik__.FlaredTrafficLightObject.flared_traffic_light_cycle.
        '''
        
        self.keys = ['N','E','S','W']
        self.idxs = [0,1,2,3]
        self._setup_entrances_and_exits(in_nodes,out_nodes)
        self._build_buffers()
        
        
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
        
        __basik__.FlaredTrafficLightObject.flared_traffic_light_cycle.FlaredTrafficLightCycle
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
        
        
        assert end_time > start_time
        assert end_time < np.inf
        
        # Initial time set to zero
        T = end_time
        t = start_time
        # Extract firsy cycle specification set given.
        # Later on we will use cycle_list instead
        cycle_specs = self.cycle_schedule[0]
        
        while True:
            # Create a sheduled cycle change/transition
            scheduled_cycle = FlaredTrafficLightCycle(t,cycle_specs,
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
            entrance_node.flared_traffic_light_entrance=True
            entrance_node.flared_traffic_light = self
            entrance_node.idx = idx
            entrance_node.key = key
            entrance_node.front = None  # Will be allocated in build buffers
            self.entrances[idx] = entrance_node
            
            # Setup exits
            exit_node = self.out_nodes[key]
            
            if exit_node is None:
                exit_node = Node()
            
            exit_node.service_node = True
            exit_node.flared_traffic_light_exit=True
            exit_node.flared_traffic_light = self
            exit_node.idx = idx
            exit_node.key = key
            exit_node.behind = None
            self.exits[idx] = exit_node
            
        return None
            
    #--------------------------------------------------------------------------  


    def _build_buffers(self):
        
        self.left_buffers = np.zeros((4,self.large_buffer_size),dtype=object)
        self.right_buffers = np.zeros((4,self.small_buffer_size),dtype=object)
        
        for i in range(4):
            
            # Large Buffer
            self.left_buffers[i,0] = Node(behind=self.entrances[i])
            self.left_buffers[i,0].buffer_start = True
            self.left_buffers[i,0].buffer_node = True
            
            for j in range(1,self.large_buffer_size):
                self.left_buffers[i,j] = Node(behind=self.left_buffers[i,j-1])
                self.left_buffers[i,j-1].front = self.left_buffers[i,j]
                self.left_buffers[i,j].buffer_node = True

            # Small Buffer
            self.right_buffers[i,0] = Node(behind=self.entrances[i])
            self.right_buffers[i,0].buffer_start = True
            self.right_buffers[i,0].buffer_node = True
            
            for j in range(1,self.small_buffer_size):
                self.right_buffers[i,j] = Node(behind=self.right_buffers[i,j-1])
                self.right_buffers[i,j-1].front = self.right_buffers[i,j]
                self.right_buffers[i,j].buffer_node = True
                
            # Entrances need a front and right
            # !!!! Below might not be neccessay=ry of we allocate front at 
            # choose_exit()
            self.entrances[i].front = self.left_buffers[i,0]  # temporary
            
        

        
        # The last nodes of each buffer need an assigned exit.
        
        # Small buffers have permanent exits as they can only permit a right turn
        # Large buffers have variable exits. These will be allocated to vehicles.
        # Hoever, initially we just set the opposite side exit as front to 
        # avoid calibration issues.
        buffer_idx = range(4)
        small_buffer_exit_idx = iter(np.roll(range(4),shift=1))
        large_buffer_exit_idx = iter(np.roll(range(4),shift=2))
        
        for i,j,k in zip(buffer_idx,small_buffer_exit_idx,large_buffer_exit_idx):
            
            # Permanent allocation
            self.right_buffers[i,-1].front = self.exits[j]
            self.exits[j].behind = self.right_buffers[i,-1]
            self.right_buffers[i,-1].buffer_end = True
            # Need flared_traffic_light object
            self.right_buffers[i,-1].flared_traffic_light = self
            
            # Temporary allocation
            self.left_buffers[i,-1].front = self.exits[k]
            self.exits[k].behind = self.left_buffers[i,-1]
            self.left_buffers[i,-1].buffer_end = True
            # Need flared_traffic_light object
            self.left_buffers[i,-1].flared_traffic_light = self
            
        
    
        return None

        
    
    #--------------------------------------------------------------------------
            
    def lock(self,to_lock):
        
        for idx in to_lock:
            
            self.left_buffers[idx,-1].locked = True
            self.right_buffers[idx,-1].locked = True

        return None
    
    #--------------------------------------------------------------------------
    
    def unlock(self,to_unlock):
        self.active_entrances.clear()  # for debugging and display purposes
        for idx in to_unlock:
            self.left_buffers[idx,-1].locked = False
            self.right_buffers[idx,-1].locked = False
            self.active_entrances.append(self.keys[idx])
            
    #--------------------------------------------------------------------------
    
    
    def allocate_left_buffer(self,entrance_idx,exit_idx):
        assert entrance_idx != exit_idx
        return self.truth[entrance_idx,exit_idx]
        
                 
    #--------------------------------------------------------------------------

    def choose_exit(self,idx):
        
        
        chosen_entrance = self.entrances[idx]
        print('TPM: ',self.tpm[idx])
        chosen_exit_idx = np.random.choice(a=self.idxs,p=self.tpm[idx])
        
        if self.allocate_left_buffer(idx,chosen_exit_idx):

            chosen_entrance.front = self.left_buffers[idx,0]
            
        else:
            
            chosen_entrance.front = self.right_buffers[idx,0]
            

        chosen_exit = self.exits[chosen_exit_idx]
        
        
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
        return 'Flared Traffic Light ({0})'.format(hex(id(self)))
        
    
    
    
#------------------------------------------------------------------------------  



