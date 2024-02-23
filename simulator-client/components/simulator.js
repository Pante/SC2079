import React from "react";
import { useState, useEffect, useRef } from "react";
import CustomButton from "./custom-button";
import PathfindingApi from "../../openapi-simulator-client/src/api/PathfindingApi";
import PathfindingRequest from "../../openapi-simulator-client/src/model/PathfindingRequest";
import PathfindingRequestRobot from "../../openapi-simulator-client/src/model/PathfindingRequestRobot";
import ApiClient from "../../openapi-simulator-client/src/ApiClient";

const Direction = {
  NORTH: "NORTH",
  EAST: "EAST",
  SOUTH: "SOUTH",
  WEST: "WEST",
};

const Angle = {
  NORTH: 0,
  EAST: 90,
  SOUTH: 180,
  WEST: 270,
};

const FORWARD_TIME = 1;
const TURN_TIME = 1.5;

const transformCoord = (x, y) => {
  return { x: 39 - y, y: x };
};

export default function Simulator() {
  const [robotState, setRobotState] = useState({
    s: -1,
    direction: Direction.NORTH,
    "north_east": { x: 6, y: 6 },
    "south_west": { x: 0, y: 0 },
  });
  const [robotDir, setRobotDir] = useState("NORTH");
  const [obstacles, setObstacles] = useState([]);
  const [directionInput, setDirectionInput] = useState("NORTH");
  const [isGettingPath, setIsGettingPath] = useState(false);
  const [path, setPath] = useState([]);
  const [commands, setCommands] = useState([]);
  const [page, setPage] = useState(0);
  const [robotPos, setRobotPos] = useState({
    direction: Direction.NORTH,
    x: 200,
    y: 1645
  });
  const [time, setTime] = useState(0);

  const generateRandID = () => {
    while (true) {
      // generate random id
      let new_id = Math.floor(Math.random() * 10) + 1;
      let ok = true;
      for (const ob of obstacles) {
        if (ob.id === new_id) {
          ok = false;
          break;
        }
      }
      if (ok) {
        return new_id;
      }
    }
  };

  const generateRobotCells = () => {
    const robotCells = [];
    let markerSWX = 0;
    let markerSWY = 0;
    let markerNEX = 0;
    let markerNEY = 0;

    if (robotState.direction === Direction.NORTH) {
      markerSWY++;
      markerNEY++;
    } else if (robotState.direction === Direction.EAST) {
      markerSWX++;
      markerNEX++;
    } else if (robotState.direction === Direction.SOUTH) {
      markerSWY--;
      markerNEY--;
    } else if (robotState.direction === Direction.WEST) {
      markerSWX--;
      markerNEX--;
    }

    // Go from i = -1 to i = 1
    for (let i = -1; i < 2; i++) {
      // Go from j = -1 to j = 1
      for (let j = -1; j < 2; j++) {
        // Transform the coordinates to our coordinate system where (0, 0) is at the bottom left
        // console.log(robotState)
        const coordNE = transformCoord(
          robotState["north_east"]["x"] + i,
          robotState["north_east"]["y"] + j
        );
        const coordSW = transformCoord(
          robotState["south_west"]["x"] + i,
          robotState["south_west"]["y"] + j
        );
        // If the cell is the marker cell, add the robot state to the cell
        if ((markerSWX+markerNEX)/2 === i && (markerSWY+markerNEY)/2 === j) {
          robotCells.push({
            direction: robotState.direction,
            "north_east": coordNE,
            "south_west": coordSW,
            s: robotState.s,
          });
        } else {
          robotCells.push({
            direction: null,
            "north_east": coordNE,
            "south_west": coordSW,
            s: -1,
          });
        }
      }
    }

    return robotCells;
  };

  const onClickObstacle = (obSWX, obSWY, obNEX, obNEY) => {
    // If the input is not valid, return
    if (!obSWX && !obSWY && !obNEX && !obNEY) return;
    let exists = false;

    // this checks if obstacles already exist, if they do then clicking will change direction
    const newObstacles = obstacles.map((obstacle) => {
      if (
        obstacle["north_east"].x === obNEX &&
        obstacle["north_east"].y === obNEY &&
        obstacle["south_west"].x === obSWX &&
        obstacle["south_west"].y === obSWY
      ) {
        exists = true;
        if (obstacle.direction === Direction.WEST) {
          obstacle.direction = Direction.NORTH;
        } else if (obstacle.direction === Direction.NORTH) {
          obstacle.direction = Direction.EAST;
        } else if (obstacle.direction === Direction.EAST) {
          obstacle.direction = Direction.SOUTH;
        } else {
          obstacle.direction = Direction.WEST;
        }

        return {
          ...obstacle,
        };
      }
      return obstacle;
    });
    // adds to obstacles array
    if (exists === false) {
      newObstacles.push({
        direction: directionInput,
        "north_east": { x: obNEX, y: obNEY },
        "south_west": { x: obSWX, y: obSWY },
        image_id: generateRandID(),
      });
    }
    setObstacles(newObstacles);
    console.log(newObstacles);
  };

  const onResetAll = () => {
    setRobotDir(Direction.NORTH);
    setRobotState({
      direction: Direction.NORTH,
      "north_east": { x: 6, y: 6 },
      "south_west": { x: 0, y: 0 },
    });
    // setRobotPos({direction: Direction.NORTH,
    // x: 200,
    // y: 1645});
    setPath([]);
    setCommands([]);
    setPage(0);
    setObstacles([]);
    setIsGettingPath(false);
    setTime(0);
  };

  const onRemoveObstacle = (ob) => {
    // If the path is not empty or the algorithm is computing, return
    if (path.length > 0 || isGettingPath) return;
    // Create a new array of obstacles
    const newObstacles = [];
    // Add all the obstacles except the one to remove to the new array
    for (const o of obstacles) {
      if (
        o["north_east"].x === ob["north_east"].x &&
        o["north_east"].y === ob["north_east"].y &&
        o["south_west"].x === ob["south_west"].x &&
        o["south_west"].y === ob["south_west"].y
      )
        continue;
      newObstacles.push(o);
    }
    // Set the obstacles to the new array
    setObstacles(newObstacles);
  };

  const getTime = (commands) => {
    let newTime = time;

    for (let x of commands) {
      // let units = x.substring(2, 4);
      if (
        !x.contains("FORWARD_LEFT") &&
        !x.contains("FORWARD_RIGHT") &&
        !x.contains("BACKWARD_LEFT") &&
        !x.contains("BACKWARD_RIGHT")
      ) {
        newTime += FORWARD_TIME * x;
      } else {
        newTime += TURN_TIME;
      }
      // if (x.move === ("FORWARD") || x.move === ("BACKWARD")) {
      //   // console.log(x[2])
      //   newTime += FORWARD_TIME * x.amount;
      //   // console.log(newTime)
      // } else if (
      //   x.move === ||
      //   x.move === ||
      //   x.move === ||
      //   x.move ===
      // ) {
      //   newTime += TURN_TIME;
      //   // console.log(newTime)
      // } else {
      //   continue;
      // }
    }

    setTime(newTime);
  };

  const getPath = () => {
    setIsGettingPath(true);
    const apiClient = new ApiClient("http://localhost:5000");
    const pathfindingRequestRobot = new PathfindingRequestRobot(
      "NORTH",
      {
        x: 6,
        y: 6,
      },
      { x: 0, y: 0 }
    );
    const pathfindingRequest = new PathfindingRequest(
      obstacles,
      pathfindingRequestRobot
    );
    const pathfindingAPI = new PathfindingApi(apiClient);
    pathfindingAPI.pathfindingPost(
      pathfindingRequest,
      (error, data, response) => {
        console.log(response)
        response = JSON.parse(response.text);
        let pathArray = [{
          "direction": robotState.direction,
          "x": 0,
          "y": 0,
          "s" : -1
        }]
        for (const arr of response.segments){
          for (const pathObj of arr.path){
            pathObj['s'] = -1
            pathArray.push(pathObj)
          }
          console.log(pathArray[-1])
          pathArray[pathArray.length-1]['s'] = 1
        }
        setPath(pathArray);
        console.log(pathArray);
        setIsGettingPath(false);
      }
    );
  };

  const createGrid = () => {
    const rows = [];
    let ref_id = 0;
    const robotCells = generateRobotCells();

    // Generate the grid
    for (let i = 0; i < 40; i++) {
      const cells = [
        // Axis
        <td key={i} className="w-5 h-5 md:w-8 md:h-8">
          <span className="text-sky-900 font-bold text-[0.6rem] md:text-base ">
            {39 - i}
          </span>
        </td>,
      ];

      for (let j = 0; j < 40; j++) {
        let foundOb = null;
        let foundRobotCell = null;

        const transformedSW = transformCoord(j, i);
        const transformedNE = transformCoord(j + 2, i - 2);

        for (const ob of obstacles) {
          const obTransformedSW = transformCoord(
            ob["south_west"].x,
            ob["south_west"].y
          );
          const obTransformedNE = transformCoord(
            ob["north_east"].x,
            ob["north_east"].y
          );
          if (obTransformedSW.x >= i && i > obTransformedNE.x && obTransformedSW.y <= j && j < obTransformedNE.y) {
            foundOb = ob;
            break;
          }
        }

        if (!foundOb) {
          for (const cell of robotCells) {
            if ((cell["south_west"].x+cell["north_east"].x)/2 === i && (cell["south_west"].y+cell["north_east"].y)/2 === j) {
              foundRobotCell = cell;
              break;
            }
          }
        }

        if (foundOb) {
          if (foundOb.direction === Direction.WEST) {
            cells.push(
              <td className="border border-l-4 border-l-red-500 w-5 h-5 md:w-8 md:h-8 bg-blue-700">
                <CustomButton
                  onClick={() =>
                    onClickObstacle(
                      transformedSW.y,
                      transformedSW.x,
                      transformedNE.y,
                      transformedNE.x
                    )
                  }
                />
              </td>
            );
          } else if (foundOb.direction === Direction.EAST) {
            cells.push(
              <td className="border border-r-4 border-r-red-500 w-5 h-5 md:w-8 md:h-8 bg-blue-700">
                <CustomButton
                  onClick={() =>
                    onClickObstacle(
                      transformedSW.y,
                      transformedSW.x,
                      transformedNE.y,
                      transformedNE.x
                    )
                  }
                />
              </td>
            );
          } else if (foundOb.direction === Direction.NORTH) {
            cells.push(
              <td className="border border-t-4 border-t-red-500 w-5 h-5 md:w-8 md:h-8 bg-blue-700">
                <CustomButton
                  onClick={() =>
                    onClickObstacle(
                      transformedSW.y,
                      transformedSW.x,
                      transformedNE.y,
                      transformedNE.x
                    )
                  }
                />
              </td>
            );
          } else if (foundOb.direction === Direction.SOUTH) {
            cells.push(
              <td className="border border-b-4 border-b-red-500 w-5 h-5 md:w-8 md:h-8 bg-blue-700">
                <CustomButton
                  onClick={() =>
                    onClickObstacle(
                      transformedSW.y,
                      transformedSW.x,
                      transformedNE.y,
                      transformedNE.x
                    )
                  }
                />
              </td>
            );
          }
          // else if (foundOb.direction === Direction.SKIP) {
          //   cells.push(
          //     <td className="border w-5 h-5 md:w-8 md:h-8 bg-blue-700" />
          //   );
          // }
        } else if (foundRobotCell) {
          ref_id++;
          if (foundRobotCell.direction !== null) {
            cells.push(
              <td className="border-black border w-5 h-5 md:w-8 md:h-8" />
            );
          } else {
            if (ref_id == 5) {
              cells.push(
                <td
                  ref={elementToFollowRef}
                  className="border-black border w-5 h-5 md:w-8 md:h-8"
                />
              );
            } else {
              cells.push(
                <td className="border-black border w-5 h-5 md:w-8 md:h-8" />
              );
            }
          }
        } else {
          cells.push(
            <td className="border-black border w-5 h-5 md:w-8 md:h-8">
              <CustomButton
                onClick={() =>
                  onClickObstacle(
                    transformedSW.y,
                    transformedSW.x,
                    transformedNE.y,
                    transformedNE.x
                  )
                }
              />
            </td>
          );
        }
      }

      rows.push(<tr key={39 - i}>{cells}</tr>);
    }

    const xAxis = [<td key={0} />];
    for (let i = 0; i < 40; i++) {
      xAxis.push(
        <td className="w-5 h-5 md:w-8 md:h-8">
          <span className="text-sky-900 font-bold text-[0.6rem] md:text-base ">
            {i}
          </span>
        </td>
      );
    }
    rows.push(<tr key={40}>{xAxis}</tr>);
    return rows;
  };

  const elementToFollowRef = useRef(null);

  const updateRobotPosition = () => {
    if (elementToFollowRef.current) {
      console.log(elementToFollowRef.current)
      const rect = elementToFollowRef.current.getBoundingClientRect();
      console.log(rect);
      // Calculate the circle's position based on the element's bounding rectangle
      const circleSWX = rect.left + rect.width / 2;
      const circleNEX = rect.right;
      const circleSWY = rect.top + rect.height / 2;
      const circleNEY = rect.bottom;
      setRobotPos({
        direction: robotState.direction,
        x: rect.left,
        y: rect.bottom+rect.height*4,
      });
    }
  };

  useEffect(() => {
    updateRobotPosition();
  }, [robotState]);

  useEffect(() => {
    if (page >= path.length) return;
    setRobotState({
      direction: path[page]["direction"],
      "north_east": {
        x: path[page].x + 6,
        y: path[page].y + 6,
      },
      "south_west": {
        x: path[page].x,
        y: path[page].y,
      },
      s: path[page].s
    });
  }, [page, path]);

  return (
    <div className="px-10 py-10 inline-flex flex-row">
      {/* Generate grid and axis numbers */}

      <table className="border-collapse border-none border-black ">
        <tbody>{createGrid()}</tbody>
      </table>

      <div
        className="w-64 h-64 bg-blue-500 rounded-full absolute transition-transform duration-500 transform -translate-x-1/2 -translate-y-1/2"
        style={{
          // top: "1645px",
          // left: "200px",
          top: `${robotPos.y}px`, // Adjust as needed
          left: `${robotPos.x}px`, // Adjust as needed
          transform: `translate(-50%, -50%) rotate(${
            Angle[robotPos.direction]
          }deg)`,
          transition: "none",
        }}
      >
        <div
          className={`absolute w-11 h-6 ${
            robotState.s != -1 ? "bg-red-500" : "bg-yellow-300"
          } top-0 left-1/2 transform -translate-x-1/2`}
        ></div>
      </div>

      <div className="py-4 px-20 space-x-4" display="flex">
        {/* Reset button */}
        <button className="btn" onClick={onResetAll}>
          Reset All
        </button>
        <button className="btn" onClick={getPath}>
          Get Path
        </button>
        {/* Obstacle info popup */}
        <div className="py-4 grid grid-cols-4 gap-x-2 gap-y-4 items-center">
          {obstacles.map((ob) => {
            return (
              <div
                key={ob}
                className="badge flex flex-row text-black bg-sky-100 rounded-xl text-xs md:text-sm h-max w-max border-cyan-500"
              >
                <div flex flex-col>
                  <div>X: {ob["south_west"].x}</div>
                  <div>Y: {ob["south_west"].y}</div>
                  <div>D: {ob.direction}</div>
                </div>
                <button>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    className="w-4 h-4 mr-2"
                    onClick={() => onRemoveObstacle(ob)}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            );
          })}
        </div>
        {path.length > 0 && (
          <div className="flex flex-row items-center text-center bg-sky-200 p-4 rounded-xl shadow-xl my-8">
            <button
              className="btn btn-circle pt-2 pl-1"
              disabled={page === 0}
              onClick={() => {
                setPage(page - 1);
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"
                />
              </svg>
            </button>

            <span className="mx-5 text-black">
              Step: {page + 1} / {path.length}
            </span>
            <span className="mx-5 text-black">{commands[page]}</span>
            <button
              className="btn btn-circle pt-2 pl-2"
              disabled={page === path.length - 1}
              onClick={() => {
                setPage(page + 1);
              }}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"
                />
              </svg>
            </button>
          </div>
        )}
        <div className="badge flex flex-row text-black bg-sky-100 rounded-xl text-xs md:text-sm h-max w-max border-cyan-500">
          Time taken: {time} sec
        </div>
      </div>
    </div>
  );
}
