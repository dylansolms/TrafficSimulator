
'''
Produces the experiment from Tutorial 4.
'''

import numpy as np
import __basik__ as bk

if __name__ == '__main__':

    #--------------------------------------------------------------------------
    
    # WITHOUT DISPLAY
    
    bk.VehicleDisplay.SHOW = False # TURN OFF
    print('DISPLAY OFF')
    print('Setting up simulation...')
    np.random.seed(123)
    fig,ax = bk.axes_grid(3,3,scale=2.5)  
    end_time = 5
    lane_length = 5 
    bk.Queue.clear()
    # North:
    Nlane_in = bk.Lane(lane_length) 
    Nlane_out = bk.Lane(lane_length) 
    NDisplay = bk.RoadDisplay(left_lane=Nlane_out,
                              right_lane=Nlane_in,
                              axes=ax[0,1],
                              horizontal=False)
    Nrate = {end_time:bk.Rate(1.)} 
    Nsource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Nlane_in.IN,
                        rate_schedule=Nrate)
    print('Scheduling Northern arrivals...')
    Nsource.setup_arrivals(end_time)
    print('..done!')
    Nrecord = bk.Record(Nlane_out.OUT)
    # East 
    Elane_in = bk.Lane(lane_length) 
    Elane_out = bk.Lane(lane_length) 
    EDisplay = bk.RoadDisplay(left_lane=Elane_out,
                              right_lane=Elane_in,
                              axes=ax[1,2],
                              horizontal=True)
    Erate = {end_time:bk.Rate(1.)} 
    Esource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Elane_in.IN,
                        rate_schedule=Erate)
    print('Scheduling Eastern arrivals...')
    Esource.setup_arrivals(end_time)
    print('..done!')
    Erecord = bk.Record(Elane_out.OUT)  
    # South
    Slane_in = bk.Lane(lane_length) 
    Slane_out = bk.Lane(lane_length) 
    SDisplay = bk.RoadDisplay(left_lane=Slane_in,
                              right_lane=Slane_out,
                              axes=ax[2,1],
                              horizontal=False)
    Srate = {end_time:bk.Rate(1.)} 
    Ssource = bk.Source(vehicle_velocity = 16.67, 
                        target_node = Slane_in.IN,
                        rate_schedule=Srate)
    print('Scheduling Southern arrivals...')
    Ssource.setup_arrivals(end_time)
    print('..done!')
    Srecord = bk.Record(Slane_out.OUT)  
    # West
    Wlane_in = bk.Lane(lane_length) 
    Wlane_out = bk.Lane(lane_length)
    WDisplay = bk.RoadDisplay(left_lane=Wlane_in,
                              right_lane=Wlane_out,
                              axes=ax[1,0],
                              horizontal=True)
    Wrate = {end_time:bk.Rate(1.)} 
    Wsource = bk.Source(vehicle_velocity = 16.67,  # 60 km/h
                        target_node = Wlane_in.IN,
                        rate_schedule=Wrate)
    print('Scheduling Western arrivals...')
    Wsource.setup_arrivals(end_time)
    print('..done!')
    Wrecord = bk.Record(Wlane_out.OUT)  
    # Circle object
    in_nodes = {'N':Nlane_in.OUT,'E':Elane_in.OUT,'S':Slane_in.OUT,'W':Wlane_in.OUT}
    out_nodes = {'N':Nlane_out.IN,'E':Elane_out.IN,'S':Slane_out.IN,'W':Wlane_out.IN,}
    # We create a transition probability matrix. It must be row stochastic!
    transitions = {'N':{'N':0.25,'E':0.25,'S':0.25,'W':0.25},
                   'E':{'N':0.25,'E':0.25,'S':0.25,'W':0.25},
                   'S':{'N':0.25,'E':0.25,'S':0.25,'W':0.25},
                   'W':{'N':0.25,'E':0.25,'S':0.25,'W':0.25}}
    traffic_circle = bk.Circle(in_nodes=in_nodes,
                               out_nodes=out_nodes,
                               transitions=transitions,
                               size=3,  # small
                               right_of_way_count=2,
                               p_risk=0.3,
                               within_velocity=8.3) # 30 km/h
    traffic_circle_display = bk.CircleDisplay(circle_object=traffic_circle,
                                              axes=ax[1,1])
    print('Populating simulation until: {0} seconds...'.format(end_time/2))
    bk.Queue.run(end_time/2)
    print('...done!')
    
    #--------------------------------------------------------------------------
    
    # WITH DISPLAY
    print('Turning on display...')
    bk.VehicleDisplay.SHOW = True # TURN OFF
    for component in bk.Queue.content:
        if isinstance(component,bk.Vehicle):  
            display = component.vehicle_display      
            display.show()
    print('...done!')

    start_time = bk.Queue.current_time
    print('Performing simulation with display...')
    bk.Queue.run(end_time=end_time,
                 start_time=start_time)
    print('...done!')
    
    #--------------------------------------------------------------------------
           











