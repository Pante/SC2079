from __future__ import annotations
import time
from flasgger import Swagger
from dataclasses import dataclass
from flask import Flask, jsonify, request
from pathfinding.pathfinding_controller import pathfinding_blueprint

app = Flask(__name__)
swagger = Swagger(app)

app.register_blueprint(pathfinding_blueprint)

@app.route('/status', methods=['GET'])
def status():
    """
    This is a health check endpoint to check if the server is running
    :return: a json object with a key "result" and value "ok"
    """
    return jsonify({"result": "ok"})

@app.route('/path', methods=['POST'])
def path_finding():
    """
    This is the main endpoint for the path finding algorithm
    :return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
    """
    # Get the json data from the request
    content = request.json

    # Get the obstacles, big_turn, retrying, robot_x, robot_y, and robot_direction from the json data
    obstacles = content['obstacles']
    # big_turn = int(content['big_turn'])
    retrying = content['retrying']
    robot_x, robot_y = content['robot_x'], content['robot_y']
    robot_direction = int(content['robot_dir'])

    # Initialize MazeSolver object with robot size of 20x20, bottom left corner of robot at (1,1), facing north, and whether to use a big turn or not.
    maze_solver = MazeSolver(20, 20, robot_x, robot_y, robot_direction, big_turn=None)

    # Add each obstacle into the MazeSolver. Each obstacle is defined by its x,y positions, its direction, and its id
    for ob in obstacles:
        maze_solver.add_obstacle(ob['x'], ob['y'], ob['d'], ob['id'])

    start = time.time()
    # Get shortest path
    optimal_path, distance = maze_solver.get_optimal_order_dp(retrying=retrying)
    print(f"Time taken to find shortest path using A* search: {time.time() - start}s")
    print(f"Distance to travel: {distance} units")
    
    # Get shortest path to return back for parking
    # start_position = optimal_path[0]  # Actual start position
    # end_position = optimal_path[-1]  # Actual end position
    # start_end = (end_position, start_position)
    # path_home = ""
    # if maze_solver.path_table.items():
    #     for key, value in maze_solver.path_table.items():
    #         if str(key) == str(start_end):
    #             path_home = value
    #     return_path = []
    #     for coord in range(1, len(path_home)):
    #         return_path.append(CellState(path_home[coord][0], path_home[coord][1], path_home[coord][2], -1))
    #     optimal_path.extend(return_path)
        
    # Based on the shortest path, generate commands for the robot
    commands = command_generator(optimal_path, obstacles)
    # print(commands)
    # print(len(optimal_path))
    # Get the starting location and add it to path_results
    path_results = [optimal_path[0].get_dict()]
    # Process each command individually and append the location the robot should be after executing that command to path_results
    i = 0
    for command in commands:
        if command.startswith("CAP"):
            continue
        if command.startswith("FIN"):
            continue
        elif command.startswith("SF") or command.startswith("FS"):
            i += int(command[2:]) // 10
            print(int(command[2:]))
        elif command.startswith("SB") or command.startswith("BS"):
            i += int(command[2:]) // 10
        else:
            i += 1
        path_results.append(optimal_path[i].get_dict())
        #print(path_results)
        #print(commands)
        
    return jsonify({
        "data": {
            'distance': distance,
            'path': path_results,
            'commands': commands
        },
        "error": None
    })

@app.route('/nav', methods=['POST'])
def nav_around_obstacle():
    """
    This is the endpoint to clear checklist item of navigating the robot around the obstacle. To demonstrate the task, just replace the api request endpoint from "path" to "nav".
    :return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
    """
    # Get the json data from the request
    content = request.json

    # Get the obstacles, big_turn, retrying, robot_x, robot_y, and robot_direction from the json data
    obstacles = content['obstacles']
    # big_turn = int(content['big_turn'])
    retrying = content['retrying']
    robot_x, robot_y = content['robot_x'], content['robot_y']
    robot_direction = int(content['robot_dir'])

    # Initialize MazeSolver object with robot size of 20x20, bottom left corner of robot at (1,1), facing north, and whether to use a big turn or not.
    maze_solver = MazeSolver(20, 20, robot_x, robot_y, robot_direction, big_turn=None)

    # Add each obstacle into the MazeSolver. Each obstacle is defined by its x,y positions, its direction, and its id
    obstacle = obstacles[0] #this is the single obstacle we are navigating around.. this is also the obstacle with the real target
    all_directions = {0, 2, 4, 6}
    non_target_directions = list(all_directions - {obstacle['d']}) #convert to list for consistent iteration
    for dir in non_target_directions:
        maze_solver.add_obstacle(obstacle['x'], obstacle['y'], dir, obstacle['id'])
    maze_solver.add_obstacle(obstacle['x'], obstacle['y'], obstacle['d'], obstacle['id']) #adding the target obstacle the last

    start = time.time()
    # Get shortest path
    optimal_path, distance = maze_solver.get_optimal_order_dp(retrying=retrying)
    print(f"Time taken to find shortest path using A* search: {time.time() - start}s")
    print(f"Distance to travel: {distance} units")
        
    # Based on the shortest path, generate commands for the robot
    commands = command_generator(optimal_path, obstacles)
    # print(commands)
    # print(len(optimal_path))
    # Get the starting location and add it to path_results
    path_results = [optimal_path[0].get_dict()]
    # Process each command individually and append the location the robot should be after executing that command to path_results
    i = 0
    for command in commands:
        if command.startswith("CAP"):
            continue
        if command.startswith("FIN"):
            continue
        elif command.startswith("SF") or command.startswith("FS"):
            i += int(command[2:]) // 10
            print(int(command[2:]))
        elif command.startswith("SB") or command.startswith("BS"):
            i += int(command[2:]) // 10
        else:
            i += 1
        path_results.append(optimal_path[i].get_dict())
        #print(path_results)
        #print(commands)
        
    return jsonify({
        "data": {
            'distance': distance,
            'path': path_results,
            'commands': commands
        },
        "error": None
    })

@app.route('/image/prediction/task-1', methods=['POST'])
def image_prediction_task1():
    file, obstacle_id, signal = __parse(request)

    ## TODO: Pass into model & return image id
    image_id = 'Foo'

    return jsonify({
        "obstacle_id": obstacle_id,
        "image_id": image_id
    })


@app.route('/image/prediction/task-2', methods=['POST'])
def image_prediction_task2():
    file, obstacle_id, signal = __parse(request)

    ## TODO: Pass into model & return image id
    image_id = 'Foo'

    return jsonify({
        "obstacle_id": obstacle_id,
        "image_id": image_id
    })


def __parse(request: Request) -> (str, str, str):
    file = request.files['file']
    file.save(os.path.join('uploads', file.filename))
    # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
    constituents = file.filename.split("_")
    obstacle_id = constituents[1]
    signal = constituents[2].strip(".jpg")

    return file.filename, obstacle_id, signal


@app.route('/image/stitch', methods=['GET'])
def image_stitch() -> None:
    # TODO: stitch images
    pass


if __name__ == '__main__':
    app.run()
