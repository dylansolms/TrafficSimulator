

from .global_queue import Queue

__all__ = ['Obstruction']#,'ObstructionNode','convert_to_obstruction_node']



class Obstruction(object):
    
    is_obstruction = True
    
    
    '''An event that allows a __basik__.node.Node to not be occupied by a 
    __basik__.VehicleObject.vehicle.Vehicle
    '''
    
    def __init__(self,start_time:float,
                      end_time:float,
                      obstruction_node):
        
        '''
        Parameters:
        -----------
        start_time: float
            When the selected node will become obstructed.
        end_time: float
            When the selected node will cease to be obstructed. This can be
            set to numpy.inf if one wishes to keep a node obstructed until the
            end of a simualtion.
            
        Raises:
        -------
        AssertionError:
            end_time must be greater than start_time
        '''
        assert end_time > start_time
        
        self.start_time = start_time
        self.end_time = end_time
        self.do_activate = True
        self.do_deactivate = False 
        self.time = start_time
        self.obstruction_node = obstruction_node
        self.obstruction_node.obstruction = self
        
    #--------------------------------------------------------------------------
    
    def activate(self):
        self.obstruction_node.obstructed = True
        self.obstruction_node.end_time = self.end_time
        
        if self.obstruction_node.display_axes is not None:
            self.obstruction_node.display_icon()
        
        self.do_activate = False
        self.do_deactivate = True
        self.time = self.end_time
        Queue.push(self)
        return None
    
    #--------------------------------------------------------------------------
    
    def deactivate(self):
        self.obstruction_node.obstructed = False
        self.do_deactivate = False
        
        if self.obstruction_node.display_axes is not None:
            self.obstruction_node.hide_icon()
        
        return None
    
    #--------------------------------------------------------------------------
    
    def __lt__(self,other):
        return self.time < other.time
    
    #--------------------------------------------------------------------------
    
    def __eq__(self,other):
        return self.time == other.time
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        
        if self.do_activate:
            label = 'activate at {0}'.format(self.time)
        else:
            label = 'de-activate at {0}'.format(self.time)
        
        return 'Obstruction ({0})'.format(label)



################   OLD   (deprecated)      ####################################


#class Obstruction(object):
#    
#    def __init__(self,start_time,end_time,
#                      obstruction_node):
#        self.start_time = start_time
#        self.end_time = end_time
#        self.do_activate = True
#        self.do_deactivate = False 
#        self.time = start_time
#        self.obstruction_node = obstruction_node
#        self.is_obstruction = True
#        
#    #--------------------------------------------------------------------------
#    
#    def activate(self):
#        self.obstruction_node.intermediate.obstructed = True
#        self.obstruction_node.intermediate.end_time = self.end_time
#        self.do_activate = False
#        self.do_deactivate = True
#        self.time = self.end_time
#        Queue.push(self)
#        return None
#    
#    #--------------------------------------------------------------------------
#    
#    def deactivate(self):
#        self.obstruction_node.intermediate.obstructed = False
#        self.do_deactivate = False
#        return None
#    
#    #--------------------------------------------------------------------------
#    
#    def __lt__(self,other):
#        return self.time < other.time
#    
#    #--------------------------------------------------------------------------
#    
#    def __eq__(self,other):
#        return self.time == other.time
#    
#    #--------------------------------------------------------------------------
#    
#    def __repr__(self):
#        
#        if self.do_activate:
#            label = 'activate at {0}'.format(self.time)
#        else:
#            label = 'de-activate at {0}'.format(self.time)
#        
#        return 'Obstruction ({0})'.format(label)

#------------------------------------------------------------------------------

#class ObstructionNode(object):
#    
#    
#    std = 0.5
#    
#   #-------------------------------------------------------------------------- 
#    
#    def __init__(self,in_node,out_node):
#        
#        self._setup_entrance_and_exit(in_node,out_node)
#        self.end_time = None
#        
#        
#    #--------------------------------------------------------------------------
#        
#    def _setup_entrance_and_exit(self,in_node,out_node):
#        self.in_node = in_node
#        self.out_node = out_node
#        self.intermediate = Node(front=out_node,
#                                 behind=in_node)
#        self.in_node.front = self.intermediate
#        self.out_node.behind = self.intermediate
#        
#        self.intermediate.service_node = True
#        self.intermediate.contains_obstruction = True
#        self.intermediate.obstructed = False  # not obstructed yet
#        self.intermediate.obstruction = self
#        
#        return None
#    
#    
#    #--------------------------------------------------------------------------
#    
#    def setup_obstructions(self,start_times:list,durations:list):
#        assert isinstance(start_times,list)
#        assert isinstance(durations,list)
#        assert len(start_times) == len(durations)
#        start_times.reverse()
#        durations.reverse()
#        
#        while True:
#            
#            start_time = start_times.pop()
#            duration = durations.pop()
#            end_time = start_time + np.random.normal(duration,self.std)
#            
#            obstruction = Obstruction(start_time,end_time,self)
#            
#            Queue.push(obstruction)
#            
#            if not bool(start_times):
#                break
#            
#        return None
#            
#    
#    #--------------------------------------------------------------------------
#    
#    
#    def __repr__(self):
#        return 'Obstruction Node ({0})'.format(hex(id(self)))
#    
#
##------------------------------------------------------------------------------
#        
#    
#    
#def convert_to_obstruction_node(node:Node,
#                                start_times:list,
#                                durations:list)->ObstructionNode:
#    
#    '''
#    Converts a non-service node into a node with scheduled obstructions.
#    '''
#
#    assert Node.service_node == False
#    obs_node = ObstructionNode(in_node=Node.behind,
#                               out_node=Node.front)
#    obs_node.setup_obstructions(start_times,durations)
#    return obs_node
#    
##------------------------------------------------------------------------------

































        
        
        
    
        