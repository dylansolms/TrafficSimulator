'''
Produces the pedestrian crossing from Tutorial 7.
'''

import numpy as np
import __basik__ as bk


if __name__ == '__main__':
    
    #--------------------------------------------------------------------------
    # No display
    
    bk.VehicleDisplay.speed_up_factor = 10
    bk.Vehicle.frames_per_move = 2
    bk.VehicleDisplay.SHOW = False # TURN OFF
    print('DISPLAY OFF')
    print('Setting up simulation...')
    np.random.seed(123)
    fig,ax = bk.axes_grid(3,3,scale=2.5)  
    end_time = 21
    lane_length = 5 
    bk.Queue.clear()
    # East 
    Elane_in = bk.Lane(lane_length) 
    Elane_out = bk.Lane(lane_length) 
    EDisplay = bk.RoadDisplay(left_lane=Elane_out,
                              right_lane=Elane_in,
                              axes=ax[1,2],
                              horizontal=True)
    Erate = {end_time:bk.Rate(0.3)} 
    Esource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Elane_in.IN,
                        rate_schedule=Erate)
    print('Scheduling Eastern arrivals...')
    Esource.setup_arrivals(end_time)
    print('..done!')
    Erecord = bk.Record(Elane_out.OUT)   
    # West
    Wlane_in = bk.Lane(lane_length) 
    Wlane_out = bk.Lane(lane_length)
    WDisplay = bk.RoadDisplay(left_lane=Wlane_in,
                              right_lane=Wlane_out,
                              axes=ax[1,0],
                              horizontal=True)
    Wrate = {end_time:bk.Rate(0.5)} 
    Wsource = bk.Source(vehicle_velocity = 16.67,  # 60 km/h
                        target_node = Wlane_in.IN,
                        rate_schedule=Wrate)
    print('Scheduling Western arrivals...')
    Wsource.setup_arrivals(end_time)
    print('..done!')
    Wrecord = bk.Record(Wlane_out.OUT)
    # Pedestrian Crossing
    cross = bk.PedestrianCrossing(W_to_E_in_node=Wlane_in.OUT,
                                       E_to_W_in_node=Elane_in.OUT,
                                       W_to_E_out_node=Elane_out.IN,
                                       E_to_W_out_node=Wlane_out.IN,
                                       on_duration=2,
                                       off_duration=2,
                                       on_initial_probability=0.99)
    cross.setup_cycles(end_time*2)
    cross_display = bk.PedestrianCrossingDisplay(cross,
                                              horizontal=True,
                                              axes=ax[1,1])
    print('Populating simulation...')
    bk.Queue.run(end_time/2)
    print('...done!')
    
    #--------------------------------------------------------------------------
    # With display
    
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