
import numpy as np
from ..node import Node

#-------------------------------------------------------------------------------       

default_transitions = {'N':{'E':0.2,'S':0.6,'W':0.2},
                       'E':{'S':0.2,'W':0.6,'N':0.2},
                       'S':{'W':0.2,'N':0.6,'E':0.2},
                       'W':{'N':0.2,'E':0.6,'S':0.2}}
           
#-------------------------------------------------------------------------------       

default_in = {'N':None,'E':None,'S':None,'W':None}

#-------------------------------------------------------------------------------       
 
default_out = {'N':None,'E':None,'S':None,'W':None} 

#-------------------------------------------------------------------------------       

class StopStreet(object):
    
    '''A point where vehicle flows meet (maximum of four) and all flows have
    equal priority. This results in the service rule/policy where a vehicle 
    must halt at a stop street as it will be served on a first come first serve
    basis determined by the time-stamp at which it halted.
    
    
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
    '''
    
    INTERNAL = True
    
    size = 2
    
    #---------------------------------------------------------------------------
    
    def __init__(self,in_nodes=default_in,
                      out_nodes=default_out,
                      transitions=default_transitions):
        
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
        transitions: dict or numpy.ndarray
            A transition probability matrix. It is row stochastic.
            See __basik__.StopStreetObject.stop_street.StopStreet.default_transitions
            for an example.
        '''
        
        # Asses that all transition probabilties sum up to one
        self._check_transitions(transitions)
        # Convert the use-friendly dictionary into a transition probability matrix
        self._create_tpm()
        # Connect in nodes to decision nodes which connect to choice nodes
        # which can be chosen. These are conncected to out nodes.
        self._setup_entrances_and_exits(in_nodes,out_nodes)
        self.unlock_time = None
        self.n_requests = 0
        
        # For display purposes
        self.display = False
        self.axes = None
        
    #---------------------------------------------------------------------------
                
    def _check_transitions(self,transitions):
        '''
        Checks that all transition probabilties sum up to one.
        Also creates self.transitions
        '''
        self.keys = ['N','E','S','W']
        self.present_keys = transitions.keys()
        # for key in self.keys:
        for key in self.present_keys:
            sum_ = sum(list(transitions[key].values()))
            if sum_ != 1:
                raise ValueError('transitions at {0} does not sum up to one.'
                                                                   .format(key))
        self.transitions = transitions
        return None
        
    #---------------------------------------------------------------------------
        
    def _create_tpm(self):
        '''
        Converts the dictionary into a numoy array.
        Creates self.tpm
        '''
        self.tpm = np.zeros((4,4))
        self.idx = {'N':0,'E':1,'S':2,'W':3}
        self.idxs = [0,1,2,3]
        for key1 in self.present_keys:
            idx1 = self.idx[key1]
            for key2 in self.transitions[key1].keys():
                try:
                    idx2 = self.idx[key2]
                    self.tpm[idx1,idx2] = self.transitions[key1][key2]
                except KeyError:
                    pass
        return None
        
    #---------------------------------------------------------------------------
        
    def _setup_entrances_and_exits(self,in_nodes,out_nodes):
        
        self.entrances = np.zeros(4,dtype=object)
        self.exits = np.zeros(4,dtype=object)
        
        for key in self.present_keys:
            
            idx = self.idx[key]

            entrance_node = in_nodes[key]
            if entrance_node is not None:
                entrance_node.front = None
                entrance_node.service_node = True
                entrance_node.stop_street_entrance = True
                entrance_node.idx = idx
                entrance_node.stop_street = self
                self.entrances[idx] = entrance_node
            else:
                self.entrances[idx] = None
            
            exit_node = out_nodes[key]
            if exit_node is None:
                exit_node = Node()
            
            exit_node.behind = None
            exit_node.service_node = True
            exit_node.stop_street_exit = True
            exit_node.idx = idx
            exit_node.stop_street = self
            self.exits[idx] = exit_node
            
                
        return None
        
    #---------------------------------------------------------------------------
        
    def lock(self):
        # Once a vehicle enters then we can lock the stop street.
        # Other vehicle cannot enter it.
        for node in self.entrances:
            if node is not None:
                node.locked = True
        self.n_requests = 0  
        return None
        
    #---------------------------------------------------------------------------
        
    def unlock(self):
        for node in self.entrances:
            if node is not None:
                node.locked = False
        return None
        
    #---------------------------------------------------------------------------
    
    def choose_exit(self,idx):
        # Choose a choice node that leads to an exit/out-node
        chosen_entrance = self.entrances[idx]
        chosen_exit_idx = int(np.random.choice(a=self.idxs,p=self.tpm[idx]))
        chosen_exit = self.exits[chosen_exit_idx]
#        chosen_exit = np.random.choice(a=self.exits,p=self.tpm[idx])
        chosen_entrance.front = chosen_exit
        chosen_exit.behind = chosen_entrance
        assert chosen_entrance.locked == False
        
        # This way we can query the stop street on which exit was chosen.
        # This is helpful in coordinating the display of the vehicles along
        # the stop street.
        self.entrance_idx = idx
        self.exit_idx = chosen_exit_idx
        self.current_entrance = chosen_entrance
        self.current_exit = chosen_exit
        
        return None
        
    #---------------------------------------------------------------------------
        
    def update_unlock_time(self,time):
        self.unlock_time = time
        self.n_requests = 0
        return None
    
    #---------------------------------------------------------------------------
    
    def request_unlock_time(self):
        self.n_requests += 1
        return self.unlock_time + self.n_requests*1e-3
                    
                
#-------------------------------------------------------------------------------       
 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    