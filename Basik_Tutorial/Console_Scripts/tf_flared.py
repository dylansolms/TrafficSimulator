
'''
Produces flared traffic light in Tutorial 5
'''

import numpy as np
import __basik__ as bk
import __basik__.FlowFunctions.flared as fl


if __name__ == '__main__':
    
    
    
    bk.VehicleDisplay.speed_up_factor = 10
    bk.Vehicle.frames_per_move = 2 # don't change this at VehicleDisplay as one might expect
    
    #--------------------------------------------------------------------------
    # Build the grid
    
    bk.VehicleDisplay.SHOW = False # TURN OFF
    print('DISPLAY OFF')
    print('Setting up simulation...')
    np.random.seed(123)
    fig,ax = bk.axes_grid(3,3,scale=2.5)  
    end_time = 17
    lane_length= 5 
    bk.Queue.clear()
    # North:
    Nlane_in = bk.Lane(lane_length) 
    Nlane_out = bk.Lane(lane_length) 
    NDisplay = bk.RoadDisplay(left_lane=Nlane_out,
                              right_lane=Nlane_in,
                              axes=ax[0,1],
                              horizontal=False)
    Nrate = {end_time:bk.Rate(0.3)} 
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
    Srate = {end_time:bk.Rate(0.3)} 
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
         fl.N_flow(3),
         fl.N_S_flow(2),
         fl.N_S_overwash(1),
         fl.S_flow(2),
         fl.E_flow(2),
         fl.W_E_flow(2),
         fl.W_E_overwash(1),
         fl.W_flow(2)
        ]
              
    in_nodes = {'N':Nlane_in.OUT,'E':Elane_in.OUT,'S':Slane_in.OUT,'W':Wlane_in.OUT}
    out_nodes = {'N':Nlane_out.IN,'E':Elane_out.IN,'S':Slane_out.IN,'W':Wlane_out.IN,}
            
    flaredtrafficlight = bk.FlaredTrafficLight(in_nodes=in_nodes,
                                               out_nodes=out_nodes,
                                               cycle_schedule=cycle)
    flaredtrafficlight.setup_cycles(end_time*2,fixed_cycle=True)
    flaredtrafficlightdisplay = bk.FlaredTrafficLightDisplay(flaredtrafficlight,
                                                             show=['N','E','S','W'],
                                                             axes=ax[1,1])
    
    #--------------------------------------------------------------------------
    # Run without display
    
    bk.Queue.run(end_time/2)
    
    #--------------------------------------------------------------------------
    # WITH DISPLAY
    
    
    print('Turning on display...')
    # plt.pause(6)
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
    
    