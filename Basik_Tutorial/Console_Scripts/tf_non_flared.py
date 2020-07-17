
'''
Produces non-flared traffic light in Tutorial 5
'''

import numpy as np
import __basik__ as bk
import __basik__.FlowFunctions.non_flared as nf

if __name__ == '__main__':
    
    
    #--------------------------------------------------------------------------
    # Build the grid
    
    bk.VehicleDisplay.SHOW = False # TURN OFF
    print('DISPLAY OFF')
    print('Setting up simulation...')
    np.random.seed(123)
    fig,ax = bk.axes_grid(3,3,scale=2.5)  
    end_time = 15
    lane_length= 5 
    bk.Queue.clear()
    # North:
    Nlane_in = bk.Lane(lane_length) 
    Nlane_out = bk.Lane(lane_length) 
    NDisplay = bk.RoadDisplay(left_lane=Nlane_out,
                              right_lane=Nlane_in,
                              axes=ax[0,1],
                              horizontal=False)
    Nrate = {end_time:bk.Rate(0.1)} 
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
    Erate = {end_time:bk.Rate(0.1)} 
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
    Srate = {end_time:bk.Rate(0.1)} 
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
    Wrate = {end_time:bk.Rate(0.1)} 
    Wsource = bk.Source(vehicle_velocity = 16.67,  # 60 km/h
                        target_node = Wlane_in.IN,
                        rate_schedule=Wrate)
    print('Scheduling Western arrivals...')
    Wsource.setup_arrivals(end_time)
    print('..done!')
    Wrecord = bk.Record(Wlane_out.OUT) 
    
    #--------------------------------------------------------------------------
    # Build the traffic light
    
    cycle = [
             nf.N_flow(10,0.1,0.8,0.1),
             nf.N_S_flow(10,0.8,0.8),
             nf.N_S_overwash(5),
             nf.S_flow(10,0.1,0.8,0.1),
             nf.E_flow(10,0.1,0.8,0.1),
             nf.W_E_flow(10,0.8,0.8),
             nf.W_E_overwash(6),
             nf.W_flow(2,0.1,0.8,0.1)
            ]
    
    in_nodes = {'N':Nlane_in.OUT,'E':Elane_in.OUT,'S':Slane_in.OUT,'W':Wlane_in.OUT}
    out_nodes = {'N':Nlane_out.IN,'E':Elane_out.IN,'S':Slane_out.IN,'W':Wlane_out.IN,}
    # Create the actual traffic light
    trafficlight = bk.TrafficLight(in_nodes=in_nodes,
                                   out_nodes=out_nodes,
                                   cycle_schedule=cycle)
    # NOTE: we need to setup cycles. These are events that are placed into the GlobalQueue or bk.Queue
    trafficlight.setup_cycles(end_time*2,fixed_cycle=True)
    trafficlightdisplay = bk.TrafficLightDisplay(trafficlight,
                                                 show=['N','E','S','W'],
                                                 axes=ax[1,1])
    
    #--------------------------------------------------------------------------
    # Run without display
    
    bk.Queue.run(end_time/2)
    
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
    
    