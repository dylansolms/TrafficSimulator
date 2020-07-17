import numpy as np
import __basik__ as bk


if __name__ == '__main__':
    
    
    
    bk.VehicleDisplay.speed_up_factor = 10
    bk.Vehicle.frames_per_move = 2
    np.random.seed(123)
    bk.Queue.clear()
    fig,ax = bk.axes_grid(1,1,scale=5)  
    end_time = 20
    # Let us create a single lane object
    lane = bk.Lane(20)
    lane_display = bk.RoadDisplay(left_lane=lane,
                                  right_lane=None,
                                  axes=ax[0,0],
                                  horizontal=True,
                                  square_image=False)  # removes some detail and gives a road strip
    rate = {end_time:bk.Rate(0.5)} 
    source = bk.Source(vehicle_velocity = 16.67,      # INITIAL VELOCITY is 60 km/h
                       target_node = lane.IN,
                       rate_schedule=rate)
    source.setup_arrivals(20)
    # Let us schedule three obstructions at some node
    lane.nodes[5].assign_velocity_change(5.55)            # change to about 20 km/h
    lane.nodes[10].assign_velocity_change(27.77)          # change to about 100 km/h  
    # Run
    plt.pause(4)
    bk.Queue.run(end_time)


