
# TODO: 1) figure out how many nodes are actually in the lane i.e.
# does in and out nodes add two extra.
# 2) allow nodes to be accessed and viewed via an array/list.



import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import rotate

from ..node import Node

#------------------------------------------------------------------------------

class Lane(object):    
    '''Single lanes that allow for movement of vehicles in one direction.
    
    These are chains of __basik__.node.Node objects that are fully conncected.
    
    Attributes:
    -----------
    in_node: __basik__.node.Node 
        The first node found in the lane. A vehicle will enter a lane here.
        An in_node should be used as an exit node for a component such as
        a traffic light or stop street. Once might also attach a 
        __basik__,source.Source object here.
    out_node: __basik__.node.Node
        The last node found in the lane. A vehicle will exit a lane here.
        A out_node could be used as an entrance for a component such as 
        as traffic light or stop street. One might also attach a
        __basik__.record.Record object here.
    IN: __basik__.node.Node
        Refers to in_node.
    OUT: __basik__.node.Node
        Refers to out_node.
    nodes: list
        A list of all the nodes that the lane consists of. The nodes are in the
        order of in_node to out_node.
    is_full: bool
        True if all nodes are occupied by a vehicle.
    is_empty: tuple
        (bool:has at least one occupied node,
        list: a list of the occupation status of each node)
    distance: float
        The distance that the Lane spans. The formula for this is
        len(nodes)*__basik__.node.Node.distance
        Hence, altering __basik__.node.Node.distance changes the distance
        of lanes and roads.
    '''
    INTERNAL = True

    #--------------------------------------------------------------------------
    
    def __init__(self,length:int,
                      circle_node=False,
                      overflow_protection=True): 
        
        '''
        Parameters:
        -----------
        length: int
            The amount of nodes that can be found in the lane. This value
            should be two or greater to ensure that there is at least an 
            in_node and out_node.
        circle_node: bool
            This is intended to be used by __basik__.CircleObject.circle.Circle.
            Leave as is.
        overflow_protection: bool
            In the event that a scheduled arrivals attempts to be placed onto
            a Lane where all nodes are occupied, servere delays may occur until
            the point where it might seem that the simulation freezes. To avoid
            this, overflow_protection will stop the slow simulation if set to True.
            
        Raises:
            AssertionError:
                length must be two or greater to ensure the existence of at 
                least an in_node and an out_node.
        '''
        
        assert isinstance(length,int) and length >= 2
        
        self.length = length
        self.circle_node_status = circle_node
        self.build()
        self.allocate_lanes(overflow_protection)

    #--------------------------------------------------------------------------
        
    @property
    def distance(self):
        spaces = self.length - 1
        return spaces*Node.distance
    
    def build(self):

        count = 0
        self.in_node = Node()
        count += 1
        behind_node = self.in_node
#        while count <= self.length - 1:
        self.nodes = [self.in_node]
        while count <= self.length - 2:
            node = Node()
            node.circle_node = self.circle_node_status
            if count == 1:
                self.in_node.front = node
            behind_node.front = node
            node.behind = behind_node
            behind_node = node
            count += 1
            last_node = node # When the loop breaks, this will be the last node.
            self.nodes.append(node)
            
        self.out_node = Node()
        behind_node.front = self.out_node
        self.out_node.behind = last_node
        
        self.nodes.append(self.out_node)
        
        self.in_node.circle_node = self.circle_node_status
        self.out_node.circle_node = self.circle_node_status
        
        self.IN = self.in_node
        self.OUT = self.out_node        
        
        # OUT can be another road, an intersection or a measuring point
        return None
    #--------------------------------------------------------------------------
    
    def allocate_lanes(self,overflow_protection):
        
        for node in self.nodes:
            node.lane = self
            node.overflow_protection = overflow_protection
        
        return None
    
    #--------------------------------------------------------------------------
    
    @property
    def is_full(self):
        
        n_capacity = len(self.nodes)
        n_occupied = 0
        
        for node in self.nodes:
            if node.service_node:
                # Service nodes can be emptied
                n_capacity -= 1  # reduce capacity as we don't count service node
                continue
            if node.occupied:
                n_occupied += 1
        
        if n_capacity == n_occupied:
            return True
        else:
            return False
    
    #--------------------------------------------------------------------------
    
    @property
    def is_empty(self):
        
        occupied_list = []
        
        for node in self.nodes:
            occupied_list.append(node.occupied)
            
        if True in occupied_list:
            status = True
        else:
            status = False
        
        return status,occupied_list
        
        
    
    #--------------------------------------------------------------------------
    
    def __repr__(self):
        return 'Lane ({0})'.format(hex(id(self)))
    

#------------------------------------------------------------------------------
