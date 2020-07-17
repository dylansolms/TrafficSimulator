
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .node import Node
from .source import Source
from .VehicleObject.vehicle import Vehicle
import warnings
from .utils import unique_legend

try:
    import cPickle as pickle
except ImportError or ModuleNotFoundError:
    import pickle


#------------------------------------------------------------------------------

class Record(object):
    
    '''Records the time-stamps of vehicle arrival times.
    
    Attributes
    -----------
    time_stamps: list
        A list of the times that vehicles passed the node with a Record object.
    source_IDs: list
        Each source that generates vehicle arrivals has an ID. This way we can
        determine which source a recorded vehicle may have come from.
    colors: list
        Just as each source has an ID associated with it, so does it have a
        unique color as well. This helps with the stem_plot method.
    data: Pandas DataFrame
        If we are recording either time-stamps or inter-arrival times to a 
        csv file then we produces this DataFrame as to make use of the 
        Pandas.DataFrame.to_csv method.
    current_time: float
        The last time the record object was activate i.e. it recorded a vehicle.
    vehicles: list
        A list of the actual vehicles that passed will be
        kept in addition to the time-stamps. This means that the vehicles
        can be probed for additional information.
    '''
    
    is_record  = True
    RECORD = True
    
    color_list = ['royalblue','orchid','coral','cyan','palegreen','firebrick',
                  'orange','olive','thistle','grey','tomato','teal','maroon',
                  'plum','wheat','turquoise']
    
    #--------------------------------------------------------------------------
    
    def __init__(self,node:'__basik__.node.Node',axes=None):
        '''
        Parameters
        ----------
        node: __basik__.node.Node
            This is the node that will record vehicles.
        axes: matplotlib.axes._subplots.AxesSubplot
            The stem_plot method makes use of this. If is left as None, then
            a new axes object will be produced. This object can be accessed as
            a class attribute.
            
        Raises:
        -------
        AssertionError
            If the node parameter is not an instance of __basik__.node.Node
        '''

        assert isinstance(node,Node)
        self.time_stamps = []
        self.source_IDs = []
        self.colors = []
        self.data = None
        self.axes = axes
        self.vehicles = []
        self.__setup(node)
        self.current_time = 0
                
    #--------------------------------------------------------------------------
        
    def place_record(self,vehicle):
        '''Record the actual vehicle.
        
        The vehicle object will be appended to the vehicles list, its arrival
        time will be appended to the time_stamps and its source ID and color
        will be recorded as well. The current_time of the record object will
        be updated to match that of the current vehicle being recorded.
        
        Parameters:
        -----------
        vehicle:  __basik__.VehicleObject.vehicle.Vehicle
            A vehicle being recorded.
            
        Raises:
        -------
        AssertionError
            If the node parameter is not an instance of 
            __basik__.VehicleObject.vehicle.Vehicle
            
        Returns:
        -------
        None
        '''
        
        assert isinstance(vehicle,Vehicle)
        self.vehicles.append(vehicle)
        self.current_time = vehicle.time
        self.time_stamps.append(vehicle.time)
        self.source_IDs.append(vehicle.source_ID)
        self.colors.append(self.color_list[vehicle.source_ID])
                
        
        return None
    
    #--------------------------------------------------------------------------
    
    def process_records(self,start_time:'float or None'=None):
        '''Processes time-stamp into intervals.
        
        Parameters:
        -----------
        start_time: None or float or int
            If set to None then the first recorded time-stamp will serve as 
            as the starting point for producing intervals/vehicle inter-arrival
            times. Hence N time-stamps give rise to (N-1) intervals. 
            If star_time is provided then N intervals are produced.
            
        Raises:
        -------
        AssertionError:
            If start_time is not None then it must be smnaller than the first
            recorded time-stamp.
            
        Returns:
        -------
        None
        '''
        
        if not bool(self.vehicles):
            raise Exception('No vehicles were recorded.')
            
#        for vehicle in self.vehicles:
#            self.place_record(vehicle)
    
        
        if start_time is None:
            x = np.array(self.time_stamps)
        else:
            assert start_time < self.time_stamps[0]
            x = np.array([start_time] + self.time_stamps)
        
        self.intervals = x[1:] - x[:-1]
        
        return None
    
    #--------------------------------------------------------------------------
    
    def clear(self,current_time:float=0):
        '''Clears all recordings and resets current_time.
        
        Parameters:
        -----------
        current_time: float or int
        
        
        Returns:
        -------
        None
        '''
        
        self.time_stamps = []
        self.source_IDs = []
        self.colors = []
        self.current_time = current_time
        self.vehicles = []
        self.intervals = None
        
        self.node.record_object = self
        self.node.record = True
        
        if self.axes is not None:
            self.axes.cla()
            
        
        return None
        
        
    #--------------------------------------------------------------------------
        
    def __setup(self,node):
        node.record_object = self
        node.record = True
        
        if node.display_axes is not None:
            node.icon_image = Node.camera
            node.display_icon()
        
        self.node = node
        
        return None
    
    #--------------------------------------------------------------------------
        
    def _read(self,file_name):
        self.data = pd.read_csv(file_name)
        return None
    
    #--------------------------------------------------------------------------
        
    def _write(self,file_name,intervals=True):
        
        if intervals:
            x = np.array([0] + self.time_stamps)
            x = x[1:] - x[:-1]
            self.data = pd.DataFrame(data=x,
                                     columns=['intervals'])
        else:
            self.data = pd.DataFrame(data=self.time_stamps,
                                     columns=['time-stamps'])
        
        if file_name[-4:] != '.csv':
            file_name += '.csv'
            warnings.warn('.csv extension was added.')
            
        self.data.to_csv(file_name,index=False)
        
        return None
    
    #--------------------------------------------------------------------------
    
    def _save_as_csv(self,file_name,intervals=True):
        self._write(file_name,intervals)
        return None
        
    
    #--------------------------------------------------------------------------
    
    def _save_as_pickle(self,file_name:'name.pkl'):
        
        if file_name[-4:] != '.pkl':
            file_name += '.pkl'
            warnings.warn('.pkl extentsion was added.')
        
        with open(file_name,'wb') as file:

            pickle.dump(self,  # it pickles the actual Source class instance.
                        file,
                        protocol=4)  # allows for large data.
        
        return None
    
    
    #--------------------------------------------------------------------------
    
    def save(self,file_name:str,
                  method:'\'csv\', \'pickle\' or \'pkl\''='csv',
                  intervals:bool=True,
                  start_time:'float or None'=None):
        
        '''Saves recorded information to a file of choice.
        
        Parameters:
        -----------
        file_name: str
            This should be a valid path name.
        method: 'csv', 'pickle' or 'pkl'
            If the csv method is chosen then only the time-stamps or intervals/
            vehicle inter-arrival times will be recorded. Choose interval as True
            if vehicle inter-arrival times are required.
            If the pickle method is chosen then the enitre object with all its
            data will be serialised.
        intervals: bool
            If set to True then inter-arrival times will saved as a csv with 
            the header 'intervals'. Otherwise, time-stamps are saved under the
            header 'time-stamps'.
        start_time: None or float or int
            If set to None then the first recorded time-stamp will serve as 
            as the starting point for producing intervals/vehicle inter-arrival
            times. Hence N time-stamps give rise to (N-1) intervals. 
            If star_time is provided then N intervals are produced.
        
        Raises:
        -------
        ValueError
            If an invalid method is given. See method under Parameters.
            
        Notes:
        ------
        If a valid method is chosen but the file_name does not contain the
        correct extension then the extension will be added. A warning will be
        produced via the warnings module to notify the user that this has been
        performed.
        
        Returns:
        --------
        None
        '''
        
        # Intervals = True is only applicable to the csv file
        
        if method == 'csv':
            self._save_as_csv(file_name,intervals)
        elif method == 'pickle' or method == 'pkl':
            self._save_as_pickle(file_name)
        else:
            raise ValueError('method must be either \'csv\', \'pickle\' or \'pkl\' ')
            
        return None
    
    
    #--------------------------------------------------------------------------
    
    def to_source(self,vehicle_velocity:'float m/s',
                       target_node:'__basik__.node.Node',
                       vehicle_color:str='random',
                       record_movement:bool=False):
        
        '''Converts a __basik__.source.Record object to a __basik__.source.Source object.
        
        The record object and all its recorded time-stamps are converted to
        a source object. This means that one can convert a recorded section
        of a simulation and use it as a source in a separate simulation. Hence,
        a larger simualtion can be broken down into smaller ones. 
        Note: this method does not save the new source object. A pickled (serialised)
        record object can always be converted to a source object. 
        
        Parameters:
        -----------
        vehicle_velocity: float
            A value in meters per second. All vehicle will move at this
            velocity on average.
        target_node: __basik__.node.Node
            The node at which new vehicles will arrive/appear/be introduced to
            interact in the simulation.
        vehicle_color: str
            This is the color setting of the vehicle. Note that if the color has
            been set to 'random' then the randomly selected color can be accessed
            via Vehicle.vehicle_display.color
        record_movement: bool
            A vehicle can be produced by the source with the setting/instructions
            that it record its movement across the simulation. A recorded vehicle
            can then be probed for this information from the vehicles list.
                
        Raises:
        -------
        AssetionError:
            If the target_node is not an instance of __basik__.node.Node
            
        Returns:
        --------
        None
        
        Notes:
        ------
        While this method converts a record object to a source object, it does
        not create a saved source object. This is because any saved record object
        can be converted to a source object. 
        '''
        assert isinstance(target_node,Node)
        
        rate_schedule = {0:self}
        
        source = Source(vehicle_velocity=vehicle_velocity,
                        target_node=target_node,
                        rate_schedule=rate_schedule,
                        vehicle_color=vehicle_color,
                        record_movement=record_movement)
        
        # NOTE: look at source.py
        # one will notice that Source.schedule_arrivals() can handle 
        # the rate_schedule given.
        
        return source

    #--------------------------------------------------------------------------
    
    def stem_plot(self,start_time:'float or None'=None,
                       legend:bool=True):
        '''Creates a stem-plot of the inter-arrival times (intervals).
        
        Parameters:
        -----------
        start_time: None or float or int
            If set to None then the first recorded time-stamp will serve as 
            as the starting point for producing intervals/vehicle inter-arrival
            times. Hence N time-stamps give rise to (N-1) intervals. 
            If star_time is provided then N intervals are produced.
        legend: bool
            Creates a legend to indicte which source a recorded vehicle 
            originates from.
        
        Returns:
        --------
        None
        '''
        
        
        if self.axes is None:
            self.figure,self.axes = plt.subplots(1,1)
        
        if start_time is None:
            X = np.array(self.time_stamps)
        else:
            X = np.array([start_time] + self.time_stamps)
            
            
        X = X[1:] - X[:-1]
        seen_ids = []
        for idx,x in enumerate(X):
            
            self.axes.vlines(idx,0,x,colors=self.colors[idx],
                             alpha=0.5,linestyle='--')
            source_id = self.source_IDs[idx]
            if source_id in seen_ids:
                self.axes.scatter([idx],[x],color=self.colors[idx])
            else:
                seen_ids.append(source_id)
                self.axes.scatter([idx],[x],color=self.colors[idx],
                                   label='Source (ID:{0})'.format(source_id))
                
        if legend:
            # self.axes.legend(loc='best')
            
            self.legend = unique_legend(axes=self.axes,
                                        loc='best')
            
        self.axes.set_xlabel('$n^{th}$ arrival')
        self.axes.set_ylabel('inter-arrival times')
        self.axes.set_title('Inter-arrival time stem plot')
        # if hasattr(self, 'figure'):
        #     self.figure.show()
        # else:
        #     plt.show()
        
        return None
    

    #--------------------------------------------------------------------------
    
    def __repr__(self):
        return 'Record ({0}) at {1}'.format(hex(id(self)),
                                            self.node)
    
    #--------------------------------------------------------------------------
        
        
        
        
        
    