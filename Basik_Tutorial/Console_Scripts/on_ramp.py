

'''
Produces the on-ramp from Tutorial 8.
'''

import numpy as np
import __basik__ as bk


if __name__ == '__main__':
    
    
    #--------------------------------------------------------------------------
    # Without Display
    
    
    bk.VehicleDisplay.speed_up_factor = 10
    bk.Vehicle.frames_per_move = 2
    bk.VehicleDisplay.SHOW = False # TURN OFF
    print('DISPLAY OFF')
    print('Setting up simulation...')
    np.random.seed(123)
    fig,ax = bk.axes_grid(3,2,scale=2.5)  
    end_time = 11.5
    lane_length = 5 
    bk.Queue.clear()
    # North:
    Nlane_in = bk.Lane(lane_length) 
    Nlane_out = bk.Lane(lane_length) 
    NDisplay = bk.RoadDisplay(left_lane=Nlane_out,
                              right_lane=Nlane_in,
                              axes=ax[0,0],
                              horizontal=False)
    Nrate = {end_time:bk.Rate(1.0)} 
    Nsource = bk.Source(vehicle_velocity = 16.67,  
                        target_node = Nlane_in.IN,
                        rate_schedule=Nrate)
    print('Scheduling Northern arrivals...')
    Nsource.setup_arrivals(end_time)
    print('..done!')
    Nrecord = bk.Record(Nlane_out.OUT)
    # South
    Slane_in = bk.Lane(lane_length) 
    Slane_out = bk.Lane(lane_length) 
    SDisplay = bk.RoadDisplay(left_lane=Slane_in,
                              right_lane=Slane_out,
                              axes=ax[2,0],
                              horizontal=False)
    Srate = {end_time:bk.Rate(1.9)} 
    Ssource = bk.Source(vehicle_velocity = 16.67, 
                        target_node = Slane_in.IN,
                        rate_schedule=Srate)
    print('Scheduling Southern arrivals...')
    Ssource.setup_arrivals(end_time)
    print('..done!')
    Srecord = bk.Record(Slane_out.OUT)  
    # East
    
    Elane_in = bk.Lane(lane_length)
    SDisplay = bk.RoadDisplay(left_lane=None,
                              right_lane=Elane_in,
                              axes=ax[1,1],
                              horizontal=True)
    Erate = {end_time:bk.Rate(0.6)} 
    Esource = bk.Source(vehicle_velocity = 16.67, 
                        target_node = Elane_in.IN,
                        rate_schedule=Erate)
    print('Scheduling Eastern arrivals...')
    Esource.setup_arrivals(end_time)
    print('..done!')
    # On-ramp object
    onramp = bk.OnRamp(main_flow_entrance=Nlane_in.OUT,
                       sub_flow_entrance=Elane_in.OUT,   # on_ramp_direction
                       on_ramp_exit=Slane_out.IN,
                       standard_lane_entrance=Slane_in.OUT,
                       standard_lane_exit=Nlane_out.IN)
            
    onrampdisplay = bk.OnRampDisplay(onramp,
                                     on_ramp_direction='E',
                                     axes=ax[1,0])
    
    
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
    
    
    
    
    
    
    
    