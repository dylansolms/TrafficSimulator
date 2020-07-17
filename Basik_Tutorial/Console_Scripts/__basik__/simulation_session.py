
try:
    import cPickle as pickle
except ImportError or ModuleNotFoundError:
    import pickle
    
    
from .global_queue import GlobalQueue
from numpy import inf
import matplotlib.pyplot as plt

from. VehicleObject import Vehicle,VehicleDisplay

import heapq

import warnings
import os

import numpy as np

#------------------------------------------------------------------------------
    
class Session(object):
    
    '''This allows for additional convenience features to be added to a simulation.
    
    Sessions are intended to mainly fulfill two purposes:
        1) Fill the simulation space and objects with vehicles such that
           it represents reality before recording data. 
        2) To save and re-use simulations.
    
    Point 1 is of particular interest. Many systems seem to behave according
    to some steady state. Hence, we would like to study that state. Furthermore,
    simulation Display components would be computationally wasteful on an
    empty system where vehicles only start arriving from sources.
    
    
    Attributes:
    -----------
    simulation_objects: dict
        Any __basik__ simulation object (whether internal or display) will
        be added to this dictionary alongside their name (string).
    internal_objects: dict
        All __basik__objects that provide the underlying internal mechanism
        of the simulation will be found here.
    display_objects: dict
        All __basik__display objects will be found here. These objects typically
        have Display as a suffix:
        e.g. __basik__.VehicleObjects.vehicle_display.VehicleDisplay.
    source_objects: dict
        All __basik__.source.Source objects will be found here. This allows
        for sources to be altered easily.
    record_objects: dict
        All __basik__.record.Record objects will be found here. This allows for
        easy probing of simulated records. Records can easily be converted to 
        sources for another round of a session as well, given that they are
        manually transferred from record_objects to source_objects and have a
        target_node given.
    cycle_objects: dict
        These are objects that give traffic lights and pedestrian crossings
        their behaviour. They produce events that are placed into the current
        __basik__.global_queue.GlobalQueue object (i.e. self.sim_queue or
        self.Queue or __basik__.Queue).
    figure: matplotlib.figure.Figure or None
        The figure on which the simulation display will appear given that the
        simulation has display components.
    display_on: bool
        A simulation can have display components but one can still run the 
        simulation without producing the display. This done by the populate
        method. Simulations with no display are fast whereas simulations with
        display are slow.
    sim_queue: __basik__.global_queue.GlobalQueue
        The __basik__.global_queue.GlobalQueue object in use to peform/run
        the simulation.
    Queue: __basik__.global_queue.GlobalQueue
        A pointer to the sim_queue attribute.
        
        
    
    '''
    
    #--------------------------------------------------------------------------
    
    def load(file_name,activate=True):
        
        '''Loads a saved/pickled/serialised session.
        
        Parameters:
        -----------
        file_name: str
            A valid path name of a .pkl file.
        activate: bool
            Once the __basik__.simulation_session.Session object has been 
            unserialised once can choose to activate it. This will take the 
            object sim_queue and set it to the current queue used by __basik__.
            This means __basik__.Queue will be a pointer to the sim_queue object
            in the unserialised object.
            Furthermore, all modules that make use of __basik__.Queue will 
            use the new sim_queue object. This allows the loaded simulations 
            session to be extended with new simulation objects.
            
        Returns:
        --------
        __basik__.simulation_session.Session
        
        Raises:
        -------
        FileNotFoundError:
            The file_name is not valid.
        '''
    
        with open(file_name,'rb') as file:
            pickled_object = pickle.load(file)
            
        if activate:
            pickled_object.activate()
            
        return pickled_object
    
    
    #--------------------------------------------------------------------------
    
    def __init__(self,name,
                      Queue=None):
        
        
        '''
        
        Parameters:
        -----------
        name: str
            The name of the session. If no custom file_name is give to the
            save method then this name will be saved to /__basik__/SavedSessions
            as /__basik__/SavedSessions/name.pkl
            If the name already contains the .pkl extension then it will not be
            added a second time. In fact, if the user does not add the .pkl
            extension a notification will be provided that the extension was
            added using the warnings module.
        Queue: __basik__.global_queue.GlobalQueue or None
            This object schedules the events of the simulation in the correct
            order. Setting it to None means that a new GlobalQueue object will
            be made for this session. This is the default and preferred setting
            as it avoids complications of multipl simulation sessions filling
            up the same GlobalQueue.
            
        '''
        
        
        if name[-4:] != '.pkl':
            name += '.pkl'
            message = 'A \'.pkl\' extension was added to name.'
            warnings.warn(message)
        self.name = name
        self.simulation_objects = dict()
        self.internal_objects = dict()
        self.display_objects = dict()
        self.source_objects = dict()
        self.record_objects = dict()
        self.cycle_objects = dict()
        self.figure = None
        
        if Queue is None:
            self.sim_queue = GlobalQueue.new()
#        else:
#            assert isinstance(Queue,GlobalQueue)
#            self.sim_queue = Queue
            
            
        self.display_on = False
    
    
    #--------------------------------------------------------------------------
    
    @property
    def Queue(self):
        return self.sim_queue
    
    #--------------------------------------------------------------------------
            
    def turn_on_display(self):
        
        '''If display components exist then calling this method will allow
        the simulation to run with display.
        '''
        
        if not bool(self.display_objects):
            return None
        
        
        self.figure.show()
        
        if self.display_on:
            return None  # Do not turn it on more than once as this creates
                         # a multi-layer plot where only one layer is
                         # functional.
        
        self.display_on = True
        
        if self.figure is None:
            error = 'self.figure is None\nA matplotlib figure is required.'
            raise Exception(error)
        
        
        
        VehicleDisplay.SHOW = True
        
        for component in self.sim_queue.Q:
            
            if isinstance(component,Vehicle):
                
                display = component.vehicle_display
            
                display.show()
            
        return None
    
    #--------------------------------------------------------------------------
    
    def turn_off_display(self):
        
        '''All display components (if any are present) will be de-acrtivated.
        '''
        
        if not bool(self.display_objects):
            return None
        
#        if not self.display_on:
#            return None   # skip as it is already off.
        
        self.display_on = False
        
        if self.figure is None:
            error = 'self.figure is None\nA matplotlib figure is required.'
            raise Exception(error)
        
        
        
        
        for component in self.sim_queue.Q:
            
            if isinstance(component,Vehicle):
                
                display = component.vehicle_display

                display.hide()
        
        
        VehicleDisplay.SHOW = False
        
        return None
        
         
    
    #--------------------------------------------------------------------------
    
    def __sort(self,sim_object,sim_object_name):
        
        self.simulation_objects[sim_object_name] = sim_object
        
        if isinstance(sim_object,plt.Figure):
            self.figure = sim_object
        
        if hasattr(sim_object,'INTERNAL'):
            self.internal_objects[sim_object_name] = sim_object
            
        if hasattr(sim_object,'DISPLAY'):
            self.display_objects[sim_object_name] = sim_object
            
        if hasattr(sim_object,'SETUP_CYCLES'):
            self.cycle_objects[sim_object_name] = sim_object
            
#        if hasattr(sim_object,'is_obstruction'):
#            self.obstruction_objects[sim_object_name] = sim_object
            
        if hasattr(sim_object,'RECORD'):
            self.record_objects[sim_object_name] = sim_object
            
        if hasattr(sim_object,'SOURCE'):
            self.source_objects[sim_object_name] = sim_object
        
        return None
        
    
    #--------------------------------------------------------------------------
    
    def add(self,sim_objects_dict:dict):
        '''Adds all simulation objects to the session. 
        
        These objects will be sorted into internal_objects, display_objects, 
        source_objects, record_objects and/or cycle_objects.
        
        
        Parameters:
        -----------
        sim_objects_dict: dict
            A dictionary where the keys are the names (string) assigned to the
            object and the values are the actual simulation objects that will
            participate in the simulation
        
        Example:
        --------
        >>> import __basik__ as bk
        >>> T  = 20
        >>> road = bk.Lane(10)
        >>> Q = np.array([[-0.1,0.05,0.05],
        ...               [0.05,-0.1,0.05],
        ...               [0.05,0.05,-0.1]])
        >>> Rates = np.array([0.1,0.4,0.9])
        >>> schedule = bk.MMPP_rate_schedule(Q=Q,
        ...                                  Rates=Rates,
        ...                                  end_time=T,
        ....                                 pi=None)  # will use stationary distribution
        >>> source = bk.Source(vehicle_velocity=16.67,
        ...                    target_node=road.IN,
        ...                    rate_schedule=schedule)
        >>> source.setup_arrivals(T)
        >>> record = bk.Record(node=road.OUT)
        >>> session = bk.Session(name='example_session.pkl',Queue=None)
        >>> session.add({'Beach Rd':road,
        ...              'Beach Rd source':source,
        ...              'Beach Rd record':record})
        
        Returns:
        --------
        None
    
        '''
        
        for sim_object_name,sim_object in sim_objects_dict.items():
            self.__sort(sim_object,sim_object_name)
        
        return None
    
    #--------------------------------------------------------------------------
    
    def remove(self,sim_object_names:iter):
        
        '''Removes simulation objects from the session.
        
        If the name of the object exists then it will be removed entirely
        from the simulation. This is in contrast to removing it manually.
        Removing it manually would require it to be removed from various 
        attributes in the session. 
        
        Parameters:
        -----------
        sim_object_names: iterable such as list,tuple or numpy.ndarray
            It should only contain the names of simulation objects to be 
            removed. These names are strings.
        
        Raises:
        -------
        KeyError
            The name of the object one is attempting to remove does not exist.
        AssertionError:
            If the name is not a string.
        TypeError:
            If sim_object_names is not an iterable.
            
        Returns:
        --------
        None
        '''

        for name in sim_object_names:
            removed = False
            
            assert isinstance(name,str)
            
            try:
                del self.simulation_objects[name]
                removed = True
            except KeyError:
                pass
            
            try:
                del self.internal_objects[name]
                removed = True
            except KeyError:
                pass
            
            try:
                del self.display_objects[name]
                removed = True
            except KeyError:
                pass
            
            try:
                del self.record_objects[name]
                removed = True
            except KeyError:
                pass
            
            try:
                del self.source_objects[name]
                removed = True
            except KeyError:
                pass
            
            try:
                del self.cycle_objects[name]
                removed = True
            except KeyError:
                pass
            
            if not removed:
                message = '{0} was not removed as it could not be found!'.format(name)
                warnings.warn(message)
                
        return None
            
    
    #--------------------------------------------------------------------------
    
    def run(self,end_time=None,
                 start_time=0,
                 clear_queue=False,
                 display_vehicles=True,
                 schedule_sources=True,
                 schedule_cycles=True,
                 reset_records=True,
                 ensure_unique=True):
        
        '''Runs the session as a simulation.
        
        Parameters:
        -----------
        end_time: float or None
            If set to None then the simulation will run until sim_queue is
            empty. The simulation will also run until empty of one sets 
            end_time = numpy.inf 
        start_time: float
            The time at which the simulation starts.
        clear_queue: bool
            It ensures that sim_queue is empty. The simulation will hence be empty
            and start from scratch. This is not actually desireable and hence 
            the default setting is False. This exists to be used but populate.
        display_vehicles: bool
            Provided that the session has been set up with Display components,
            the simulation will display vehicles on these components. This
            essentially is equivalent to using the method turn_on_display.
        schedule_sources: bool
            If sources have not already had arrivals scheduled using the
            setup_arrivals method in __basik__.source.Source then setting this
            to True will do so. 
            Note: care should be taken when setting this to True in order to 
            prevent the scenario of scheduling arrivals twice
            i.e. setting this to True and having called setup_arrivals.
            If set to True, it will be attempted to schedule arrivals until
            end_time. Hence, it should be ensured that the rate_schedule of the
            source can produce arrival until this end_time.
        schedule_cycles: bool
            Similar to schedule_sources except that it will set up traffic light
            cycles an pedestrian crossing events using their setup_cycles method.
            Care should also be taken not to schedule/set up cycles twice.
        reset_records: bool
            Clears any existing content in a __basik__.record.Record object.
            
            
        Raises:
        -------
        AssertionError
            If end_time is not None then it must be greater than start_time.
            
        Returns:
        --------
        None
        
        See Also:
        ---------
        __basik__.global_queue.GlobalQueue.run
        '''
        
        self.start_time = start_time
        self.end_time = end_time
        
        if clear_queue:
            self.sim_queue.clear()
        
        
        if start_time is not None:
            if end_time is not None:
                assert end_time > start_time
            self.reset_time(lower_bound=start_time)
        
        
        
        
        if schedule_sources:
            self.schedule_sources(end_time,start_time)
            
        if schedule_cycles:
            self.schedule_cycles(end_time,start_time)
        
        if reset_records:
            self.reset_records()
        
        if bool(self.display_objects):
            # Only do this is display objects exist
            
            if display_vehicles:
                self.turn_on_display()
            else:
                if not self.display_on:
                    self.turn_off_display()
        

#        if ensure_unique:
#            self.sim_queue.Q = (np.unique(self.sim_queue.Q)).tolist()
            

        if end_time is None:
            # Run until the queue is empty
            self.sim_queue.run()
        else:
            self.sim_queue.run(end_time)
            
        return None
            
    #--------------------------------------------------------------------------
    
    def populate(self,end_time,
                      clear_queue=True,
                      schedule_sources=True,
                      schedule_cycles=True,
                      reset_records=True):
#                 ensure_unique=False):
        
        
        '''Allows an empty simulation to be populated.
        
        This method is both convenient for a simulaion with and without a
        display. Monitoring a simulation as it starts from empty is rather
        pointless. Hence, populate seeks to eliminate this.
        
        It is particularly useful in a simulation with display. This is because
        it populates the simulation while updating the neccessary display 
        information. It, however, does not render the display which is very time
        consuming. The end result is that one attains a populated simulation that 
        can be displayed without having animate this process. This allows the
        user to focus on/only view the animation of a populated simualtion.
        
        It should be noted that this method if just a wrapper for the run method
        where it insists on vehicle_display being set to False and the start_time
        being zero.
        
        Parameters:
        -----------
        end_time: float or None
            If set to None then the simulation will run until sim_queue is
            empty. The simulation will also run until empty of one sets 
            end_time = numpy.inf 
        clear_queue: bool
            Ensures the sim_queue is empty to allow a simulation to be populated
            from scratch. If set to False, it will populate an exising simulation.
        schedule_sources: bool
            If sources have not already had arrivals scheduled using the
            setup_arrivals method in __basik__.source.Source then setting this
            to True will do so. 
            Note: care should be taken when setting this to True in order to 
            prevent the scenario of scheduling arrivals twice
            i.e. setting this to True and having called setup_arrivals.
            If set to True, it will be attempted to schedule arrivals until
            end_time. Hence, it should be ensured that the rate_schedule of the
            source can produce arrival until this end_time.
        schedule_cycles: bool
            Similar to schedule_sources except that it will set up traffic light
            cycles an pedestrian crossing events using their setup_cycles method.
            Care should also be taken not to schedule/set up cycles twice.
        reset_records: bool
            Clears any existing content in a __basik__.record.Record object.
        
        Raises:
        -------
        AssertionError
            If end_time is not None then it must be greater than start_time.
            Time can also not be set to None or numpy.inf as in the run method.
            The reasoning for this is that we cannot allow populate to run for 
            as long as a whole simualtion. That would be rather pointless.
            
        Returns:
        --------
        None
        '''

        assert end_time >= 0 and end_time != inf
        # Populate is basically running the simulation without a display for 
        # some amount of time. The idea is to get existing vehicles placed
        # onto the simulation.
        # We do not allow end_time to equal inf as this means that the simulation
        # runs until the queue is empty. This means that all the vehicles
        # have been removed from the simaultion. This would beat the purpose
        # of a populate function.
#        if bool(self.sim_queue.Q):
        if clear_queue:
            self.sim_queue.clear()
            # We want the queue to be clear
        self.run(end_time,
                 start_time=0,
                 clear_queue=clear_queue,
                 schedule_sources=schedule_sources,
                 schedule_cycles=schedule_cycles,
                 reset_records=reset_records,
#                 ensure_unique=ensure_unique,
                 display_vehicles=False)
        
        return None
        

    #--------------------------------------------------------------------------
    
    def reset_time(self,lower_bound=0):
        
        '''Resets the time of all objects in the sim_queue attribute such that
        the first event will occur at the lower_bound.
        
        
        Parameters:
        -----------
        lower_bound: float
            Time when the first event in the sim_queue will occur.
        
        Raises:
        -------
        IndexError:
            If the sim_queue does not contain any events. There is nothing
            to reset.
            
        Returns:
        --------
        None
        '''

        try:
            earliest_time = self.sim_queue.Q[0].time
        except IndexError:
            return None  # Empty Queue: nothing to reset.
        
        # earliest_time + delta = lower_bound
        delta  = lower_bound - earliest_time
        # Now correct all vehicle time-stamps with the same delta
        for sim_object in self.sim_queue.Q:
            sim_object.time += delta
            
        heapq.heapify(self.sim_queue.Q)
        # NOTE: we refer to objects in the Queue as sim_objects. They are
        # mostly vehicles. However, their are traffic light cycles and 
        # scheduled obstructions in it as well.
        
        return None
    
    #--------------------------------------------------------------------------
    
    def save(self,file_name=None,verbal=True):
        
        '''Saves the entire session and its progress by serialising it through
        the use of either cPickle (preferred) or pickle.
        
        Parameters:
        -----------
        file_name: str or None
            A given valid path name. If set to None then the session will be 
            saved according to the path name /__basik__/SavedSession/name.pkl
            i.e. path = os.getcwd() + '/SavedSession/' + self.name
        verbal: bool
            Prints a notidication when the session has been saved along with
            the path/file name under which it can be found.
            
        Returns:
        --------
        None
        '''
        
        if file_name is None:
            path = os.getcwd() + '/SavedSession/' + self.name
        else:
            path = file_name
        
        with open(path,'wb') as file:
            
            pickle.dump(self,file,
                        protocol=4)
            # Protocol 4 is for large data
            # See : https://stackoverflow.com/questions/29704139/
            #       pickle-in-python3-doesnt-work-for-large-data-saving
        
        if verbal:
            print('Session saved as:\n{0}'.format(path))
            
        return None
            
    
    #--------------------------------------------------------------------------
    
    
    def vehicles_only(self):
        
        '''Removes all events from the sim_queue except for the scheduled 
        movement of vehicles.
        
        Returns:
        --------
        None
        '''
        
        for idx,component in enumerate(self.sim_queue):
            
            if not hasattr(component,'is_vehicle'):
                del self.sim_queue[idx]
            
            else:
                
                if hasattr(component,'arrival'):
                    del self.sim_queue[idx]
        
        self.sim_queue.heapify()
        
        return None
                
    #--------------------------------------------------------------------------

    def activate(self):
        
        
        '''Activates an unserialised/unpickled session. 
        
        Once the __basik__.simulation_session.Session object has been 
        unserialised once can choose to activate it. This will take the 
        object sim_queue and set it to the current queue used by __basik__.
        This means __basik__.Queue will be a pointer to the sim_queue object
        in the unserialised object.
        Furthermore, all modules that make use of __basik__.Queue will 
        use the new sim_queue object. This allows the loaded simulations 
        session to be extended with new simulation objects.
            
        Returns:
        --------
        None
        
        See Also:
        ---------
        __basik__.simulation_session.Session.load
        
        '''
        
        # Not sure if we need this.
        # Intention: replace Queue in global_queue with self.sim_queue
        GlobalQueue.new(self.sim_queue)
        
        return None

    #--------------------------------------------------------------------------
    
    
    def reset_records(self):
        
        '''Clears all __basik__.record.Record objects.
        '''
        
        for record_object in self.record_objects.values():
            record_object.clear()
            
        return None
    
    #--------------------------------------------------------------------------
    
    def schedule_cycles(self,end_time,
                             start_time=0,
                             fixed_cycle=True):
        
        '''Schedules all objects in self.cycle_objects.
        
        Parameters:
        -----------
        end_time: float or None
            The time at which cycles will end
        start_time: float
            The time at which cycles will start.
        fixed_cycle: bool
            Traffic lights can follow a fixed cycle from the given cycle
            schedule or it can randomise its cycle by shuffling this
            given cycle schedule.
            
        See Also:
        ---------
        __basik__.TrafficLightObject.traffic_light.TrafficLight.setup_cycles
        __basik__.FlaredTrafficLightObject.flared_traffic_light.FlaredTrafficLight.setup_cycles
        
        Raises:
        --------
        AssertionError:
            end_time must be greater than start_time.
            end_time must be less than numpy.inf
        
        Returns:
        --------
        None
        '''
        
        assert end_time > start_time
        assert end_time < np.inf
        
        for cycle_object in self.cycle_objects.values():
            cycle_object.setup_cycles(end_time,start_time,fixed_cycle)
            
        return None
    
    #--------------------------------------------------------------------------
    
    def schedule_sources(self,end_time,
                              start_time=0):
        
        '''Schedules all objects in self.source_objects.
        
         Parameters:
        -----------
        end_time: float or None
            The time at which cycles will end
        start_time: float
            The time at which cycles will start.
               
        See Also:
        ---------
        __basik__.source.Source.setup_arrivals
            
        Raises:
        --------
        AssertionError:
            end_time must be greater than start_time.
            end_time must be less than numpy.inf
        
        Returns:
        --------
        None
        '''
        
        assert end_time > start_time
        assert end_time < np.inf
        
        for source_object in self.source_objects.values():
            source_object.setup_arrivals(end_time,start_time)
        
        return None
    
    #--------------------------------------------------------------------------
    
    
    def __repr__(self):
        return '\tSession\n>>> name: {0}\n>>> id: {1}'.format(self.name,
                                                          hex(id(self)))


#------------------------------------------------------------------------------

def load_session(file_name,activate=True)->Session:
    
    '''Unserialises/unpickles a serialised __basik__.session.Session object.
    
    This is a wrapper function for __basik__.session.Session.load
    
    Parameters:
    -----------
    file_name: str
            A valid path name of a .pkl file.
    activate: bool
        Once the __basik__.simulation_session.Session object has been 
        unserialised once can choose to activate it. This will take the 
        object sim_queue and set it to the current queue used by __basik__.
        This means __basik__.Queue will be a pointer to the sim_queue object
        in the unserialised object.
        Furthermore, all modules that make use of __basik__.Queue will 
        use the new sim_queue object. This allows the loaded simulations 
        session to be extended with new simulation objects.
            
    Returns:
    --------
    __basik__.simulation_session.Session
    
    See Also:
    ---------
    __basik__.session.Session.load
    
    '''
    
    return Session.load(file_name,activate)


#------------------------------------------------------------------------------





