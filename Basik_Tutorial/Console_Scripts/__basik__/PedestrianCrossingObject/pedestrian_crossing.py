

import numpy as np
from .pedestrian_crossing_event import PedestrianCrossingEvent
from ..global_queue import Queue
from ..node import Node

from copy import deepcopy

#-------------------------------------------------------------------------------       


class PedestrianCrossing(object):
    
    '''Allows for the delay of vehicles due the crossing of pedestrians.
    
    The PedestrianCrossing is either in an on or off state. The on state refers
    to when pedestriancs are crossing and the PedestrianCrossing is hence 
    active/on. The transitions and durations of these two states are governed by
    a two-state continuous-time Markov Process. 
    '''
    
    size = 1  # 2 meters <==> two nodes
    INTERNAL = True
    SETUP_CYCLES = True
        
    #--------------------------------------------------------------------------
    
    def __init__(self,W_to_E_in_node,
                      E_to_W_in_node,
                      W_to_E_out_node,
                      E_to_W_out_node,
                      on_duration,
                      off_duration,
                      on_initial_probability):
        

        '''
        Parameters:
        -----------
        W_to_E_in_node: __basik__.node.Node
            out_node (OUT) of __basik__.RoadObject.lane.Lane
        E_to_W_in_node: __basik__.node.Node
            out_node (OUT) of __basik__.RoadObject.lane.Lane
        W_to_E_out_node: __basik__.node.Node
            in_node (IN) of __basik__.RoadObject.lane.Lane
        E_to_W_out_node: __basik__.node.Node
            in_node (IN) of __basik__.RoadObject.lane.Lane
        on_duration: float
            Th mean time taken for pedestrians to all fully cross the required
            lanes. This will also be the duration that vehicles cannot cross.
            This value is the mean of an Exponential Process and its reciprocal
            is the rate intensity of an Exponential Process.
        off_duration: float
            This is the average amount of time that the pedestrian crossing 
            remains clear and unobstructed. 
            This value is the mean of an Exponential Process and its reciprocal
            is the rate intensity of an Exponential Process.
        on_initial_probability: float
            The probability that the first state that the pedestrian crossing is
            found operaing in the on state at the start_time.
        '''
        
        
        self.on_duration = on_duration
        self.on_rate = 1./on_duration
        self.off_duration = off_duration
        self.off_rate = 1./off_duration
        assert (on_initial_probability <= 1 and
                on_initial_probability >= 0)
        self.on_initial_probability = on_initial_probability

        # These are the states of the continuous-time Markov chain.
        self.states = [0,1]
        self.keys = ['ON','OFF']
        
        # If all probability attributes neccessary for setup_cycles are correct
        # then we proceed to setup the entrances and exits of the component.
        # The buffers can also be constructed.
        self._setup_entrances_and_exits(W_to_E_in_node,
                                        E_to_W_in_node,
                                        W_to_E_out_node,
                                        E_to_W_out_node)
        self._build_buffers()

        self.unlock_time = None
        self.n_requests = 0
        
        self.display = None
        
    #--------------------------------------------------------------------------
          
    def setup_cycles(self,end_time,
                          start_time=0):
        
        '''
        Parameters:
        -----------
        end_time: float
            The last time at which a state change can occur i.e. a transition
            in the two-state continuous-time Markov Process.
        start_time: float
            The time at which an initial state for the pedestrian crossing
            is randomly selected.
            
        Raises:
        -------
        AssertionError:
            end_time must be greater than start_time and less than numpy.infty
        
        Returns:
        --------
        None
        '''
            
        assert end_time > start_time
        assert end_time < np.inf
        
        # Initial time set to zero
        T = end_time
        t = start_time
        # Uniformization
        self.ctmc = np.array([[-self.on_rate,self.on_rate],
                              [self.off_rate,-self.off_rate]])
        self.sample_rate = max([self.on_rate,self.off_rate])
        self.dtmc = np.eye(2) + self.ctmc/self.sample_rate
        
        
        pedestrian_crossing_starts = 0
        pedestrians_crossing_ends = 0
        

        state = np.random.choice(a=self.states,
                                 p=[self.on_initial_probability,
                                    1-self.on_initial_probability])
                
    
        while True:
            
            delta = np.random.exponential(scale=1/self.sample_rate)
            t += delta
            
            next_state = np.random.choice(a=self.states,
                                          p=self.dtmc[state])
            
            if state == next_state:
                # We remain in the state
                pass
            else:
                if (state == 0 and next_state == 1):
                    pedestrians_crossing_ends = t
                    event = PedestrianCrossingEvent(start_time=pedestrian_crossing_starts,
                                                    end_time=pedestrians_crossing_ends,
                                                    pedestrian_crossing=self)
                    Queue.push(event)
                    
                if (state == 1 and next_state == 0):
                    pedestrian_crossing_starts = t
                
            if t >= T:
                break
            
            state = next_state
        
        
        return None
            
    
    #--------------------------------------------------------------------------
    
    def _setup_entrances_and_exits(self,W_to_E_in_node,
                                        E_to_W_in_node,
                                        W_to_E_out_node,
                                        E_to_W_out_node):
        
        
        ##### East to West  ######
        
        # Entrance
        self.W_to_E_entrance = W_to_E_in_node
        self.W_to_E_entrance.service_node = True
        self.W_to_E_entrance.pedestrian_crossing_entrance = True
        self.W_to_E_entrance.pedestrian_crossing = self
        self.W_to_E_entrance.idx = 0
        self.W_to_E_entrance.key = 'W to E'
        
        # Exit
        self.W_to_E_exit = W_to_E_out_node
        self.W_to_E_exit.service_node = True
        self.W_to_E_exit.pedestrian_crossing_exit = True
        self.W_to_E_exit.pedestrian_crossing = self
        
        
        ##### East to West  ######
        
        # Entrance
        self.E_to_W_entrance = E_to_W_in_node
        self.E_to_W_entrance.service_node = True
        self.E_to_W_entrance.pedestrian_crossing_entrance = True
        self.E_to_W_entrance.pedestrian_crossing = self
        self.E_to_W_entrance.idx = 1
        self.E_to_W_entrance.key = 'E to W'
        
        # Exit
        self.E_to_W_exit = E_to_W_out_node
        self.E_to_W_exit.service_node = True
        self.E_to_W_exit.pedestrian_crossing_exit = True
        self.E_to_W_exit.pedestrian_crossing = self
        
        
        # Start partially constructing the buffers.
        self.W_to_E_buffer_entrance = Node()
        self.W_to_E_buffer_exit = Node()
        self.E_to_W_buffer_entrance = Node()
        self.E_to_W_buffer_exit = Node()
        
        ##### BUFFER ENTRANCES:  #####

        self.W_to_E_buffer_entrance.service_node = True
        self.W_to_E_buffer_entrance.pedestrian_crossing_buffer_entrance = True
        self.W_to_E_buffer_entrance.pedestrian_crossing = self
        self.W_to_E_buffer_entrance.pedestrian_crossing_buffer_node = True
        self.W_to_E_buffer_entrance.behind = W_to_E_in_node
        self.W_to_E_entrance.front = self.W_to_E_buffer_entrance
        # W_to_E_buffer_entrance still needs a front. This will be allocated during
        # _build_buffers()
        
        self.E_to_W_buffer_entrance.service_node = True
        self.E_to_W_buffer_entrance.pedestrian_crossing_buffer_entrance = True
        self.E_to_W_buffer_entrance.pedestrian_crossing = self
        self.E_to_W_buffer_entrance.pedestrian_crossing_buffer_node = True
        self.E_to_W_buffer_entrance.behind = E_to_W_in_node
        self.E_to_W_entrance.front = self.E_to_W_buffer_entrance
        # E_to_W_buffer_entrance still needs a front. This will be allocated during
        # _build_buffers()
        
        
        ##### BUFFER EXITS:  #####
        
        self.W_to_E_buffer_exit.service_node = True
        self.W_to_E_buffer_exit.pedestrian_crossing_buffer_exit = True
        self.W_to_E_buffer_exit.pedestrian_crossing = self
        self.W_to_E_buffer_exit.pedestrian_crossing_buffer_node = True
        self.W_to_E_buffer_exit.front = W_to_E_out_node
        self.W_to_E_exit.behind = self.W_to_E_buffer_exit
        # W_to_E_buffer_exit still needs a behind. This will be allocated during
        # _build_buffers()
        
        
        self.E_to_W_buffer_exit.service_node = True
        self.E_to_W_buffer_exit.pedestrian_crossing_buffer_exit = True
        self.E_to_W_buffer_exit.pedestrian_crossing = self
        self.W_to_E_buffer_exit.pedestrian_crossing_buffer_node = True
        self.E_to_W_buffer_exit.front = E_to_W_out_node
        self.E_to_W_exit.behind = self.E_to_W_buffer_exit
        # E_to_W_buffer_exit still needs a behind. This will be allocated during
        # _build_buffers()

            
        return None
    
    
    #--------------------------------------------------------------------------
    
    def _build_buffers(self):
        

        self.W_to_E_buffers = np.zeros(10,dtype=object)
        self.E_to_W_buffers = np.zeros(10,dtype=object)
        
        
        self.W_to_E_buffers[0] = self.W_to_E_buffer_entrance
        self.E_to_W_buffers[0] = self.E_to_W_buffer_entrance
        self.W_to_E_buffers[-1] = self.W_to_E_buffer_exit
        self.E_to_W_buffers[-1] = self.E_to_W_buffer_exit
        
        for idx in range(1,9):
            
            # We skip entrances. It has had its behind node
            # allocated in _setup_entrances_and_exits()
            
            self.W_to_E_buffers[idx] = Node()
            self.W_to_E_buffers[idx].pedestrian_crossing_buffer_node = True
            self.W_to_E_buffers[idx].behind = self.W_to_E_buffers[idx-1]
            self.W_to_E_buffers[idx-1].front = self.W_to_E_buffers[idx]
            
            self.E_to_W_buffers[idx] = Node()
            self.E_to_W_buffers[idx].pedestrian_crossing_buffer_node = True
            self.E_to_W_buffers[idx].behind = self.E_to_W_buffers[idx-1]
            self.E_to_W_buffers[idx-1].front = self.E_to_W_buffers[idx]
        
        # Connect buffer exits to the rest of the buffer
        self.W_to_E_buffers[-2].front = self.W_to_E_buffer_exit
        self.W_to_E_buffer_exit.behind = self.W_to_E_buffers[-2]
        self.E_to_W_buffers[-2].front = self.E_to_W_buffer_exit
        self.E_to_W_buffer_exit.behind = self.E_to_W_buffers[-2]
        
        
        # Extract the before and after crosswalk nodes. These wil be of interest.
        self.W_to_E_before_buffer = self.W_to_E_buffers[4]
        self.W_to_E_after_buffer = self.W_to_E_buffers[5]  # will be locked/unlocked
        self.W_to_E_after_buffer.pedestrian_crossing = self # Needs this
        
        self.E_to_W_before_buffer = self.E_to_W_buffers[4]
        self.E_to_W_after_buffer = self.E_to_W_buffers[5]  # will be locked/unlocked
        self.E_to_W_after_buffer.pedestrian_crossing = self
        
        return None
            
    #--------------------------------------------------------------------------        
            
    def lock(self):
        
        self.W_to_E_after_buffer.locked = True
        self.E_to_W_after_buffer.locked = True
        
        return None
    
    #--------------------------------------------------------------------------
    
    def unlock(self):
        
        self.W_to_E_after_buffer.locked = False
        self.E_to_W_after_buffer.locked = False
        
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
        return 'Pedestrian Crossing ({0})'.format(hex(id(self)))
        

    
#------------------------------------------------------------------------------  