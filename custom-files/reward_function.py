import math

class memory:
    is_in_corner = False
    next_corner = 9999
    prev_steps = None
    prev_speed = None

def reward_function(params):
    #all_wheels_on_track = params["all_wheels_on_track"]
    is_offtrack = params["is_offtrack"]
    closest_waypoints = params["closest_waypoints"]
    is_left_of_center = params["is_left_of_center"]
    progress = params["progress"]
    speed = params["speed"]
    steps = params["steps"]
    waypoints = params["waypoints"]
    x = params['x']
    y = params['y']

    #reinitialise memory going into a new episode
    if memory.prev_steps is None or steps < memory.prev_steps:
        memory.prev_speed = None
        memory.is_in_corner = False
        memory.next_corner = 9999

    reward = 1e-3

    #general speed/progress reward
    if steps > 0:
        reward = (( progress/ steps)*100) + (speed**2)

    #determine necessary waypoints
    next_waypoint_index = closest_waypoints[1]
    closest_prev_waypoint = waypoints[closest_waypoints[0]]
    #closest_next_waypoint = waypoints[closest_waypoints[1]]
    look_ahead_distance = 5  # for example, look ahead 5 waypoints
    look_ahead_index = (next_waypoint_index + look_ahead_distance) % len(waypoints)
    look_ahead_prev_waypoint = waypoints[look_ahead_index]
    look_ahead_next_waypoint = waypoints[look_ahead_index +1 % len(waypoints)]
    
    #get track headings
    def getHeading(prev_waypoint,next_waypoint):
        track_heading = math.atan2(next_waypoint[1] - prev_waypoint[0], next_waypoint[0] - prev_waypoint[0]) 
        track_heading = math.degrees(track_heading)
        return abs(track_heading)
    
    car_heading = getHeading([x,y],closest_prev_waypoint)
    future_track_heading = getHeading(look_ahead_prev_waypoint,look_ahead_next_waypoint)
    heading_diff = car_heading-future_track_heading

    #determine if a corner is coming up
    is_corner_upcoming = abs(heading_diff) >= 30

    has_speed_dropped = None
    if memory.prev_speed is not None:
        has_speed_dropped = memory.prev_speed > speed

    #update memory
    if is_corner_upcoming:
        memory.next_corner = look_ahead_index
    if next_waypoint_index >= memory.next_corner:
        memory.is_in_corner = True
    if next_waypoint_index-memory.next_corner >=20:
        memory.is_in_corner = False
    memory.prev_speed = speed
    memory.prev_steps = steps

    #creating variables for readability
    is_entering_corner = is_corner_upcoming and not memory.is_in_corner
    is_left_turn = is_corner_upcoming or memory.is_in_corner and heading_diff > 0
    is_right_turn = not is_left_turn
    is_right_of_center = not is_left_of_center

    #reward corner position
    if is_entering_corner:
        #reward slowing down going into a corner
        if has_speed_dropped:
            reward *= 1.3
        #you want to enter a corner wide
        if is_left_turn and is_right_of_center:
            reward *= 1.3
        elif is_right_turn and is_left_of_center:
            reward *= 1.3
    else:
        #otherwise, you want to be in a corner/exit wide
        if is_left_turn and is_left_of_center:
            reward *= 1.3
        elif is_right_turn and is_right_of_center:
            reward *= 1.3

    #final check that the car is not off track
    if is_offtrack or speed <=1:
        reward = 1e-3

    return float(reward)