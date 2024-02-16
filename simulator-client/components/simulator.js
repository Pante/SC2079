import React from "react";
import { useState, useEffect, useRef } from "react";
import CustomButton from "./custom-button";
import QueryAPI from "./query-api";

//change accordingly to what we set in our algo
const Direction = {
  NORTH: 0,
  EAST: 2,
  SOUTH: 4,
  WEST: 6,
  NONE: 8,
};

const DirectionToString = {
  0: "Up",
  2: "Right",
  4: "Down",
  6: "Left",
  8: "None",
};

const FORWARD_TIME = 1;
const TURN_TIME = 1.5;

const transformCoord = (x, y) => {
  return { x: 19 - y, y: x };
};

export default function Simulator() {
  const [robotState, setRobotState] = useState({
    x: 1,
    y: 1,
    d: Direction.NORTH,
    s: -1,
  });
  const [robotX, setRobotX] = useState(1);
  const [robotY, setRobotY] = useState(1);
  const [robotDir, setRobotDir] = useState(0);
  const [obstacles, setObstacles] = useState([]);
  const [directionInput, setDirectionInput] = useState(Direction.NORTH);
  const [isGettingPath, setIsGettingPath] = useState(false);
  const [path, setPath] = useState([]);
  const [commands, setCommands] = useState([]);
  const [page, setPage] = useState(0);
  const [robotPos, setRobotPos] = useState({ x: 1, y: 1, angle: 0 });
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
    let markerX = 0;
    let markerY = 0;

    if (Number(robotState.d) === Direction.NORTH) {
      markerY++;
    } else if (Number(robotState.d) === Direction.EAST) {
      markerX++;
    } else if (Number(robotState.d) === Direction.SOUTH) {
      markerY--;
    } else if (Number(robotState.d) === Direction.WEST) {
      markerX--;
    }

    // Go from i = -1 to i = 1
    for (let i = -1; i < 2; i++) {
      // Go from j = -1 to j = 1
      for (let j = -1; j < 2; j++) {
        // Transform the coordinates to our coordinate system where (0, 0) is at the bottom left
        const coord = transformCoord(robotState.x + i, robotState.y + j);
        // If the cell is the marker cell, add the robot state to the cell
        if (markerX === i && markerY === j) {
          robotCells.push({
            x: coord.x,
            y: coord.y,
            d: robotState.d,
            s: robotState.s,
          });
        } else {
          robotCells.push({
            x: coord.x,
            y: coord.y,
            d: null,
            s: -1,
          });
        }
      }
    }

    return robotCells;
  };

  const onClickObstacle = (obX, obY) => {
    // If the input is not valid, return
    if (!obX && !obY) return;
    let exists = false;

    const newObstacles = obstacles.map((obstacle) => {
      if (obstacle.x === obX && obstacle.y === obY) {
        exists = true;
        if (obstacle.d === 6) {
          obstacle.d = 0;
        } else {
          obstacle.d += 2;
        }
        return {
          ...obstacle,
        };
      }
      return obstacle;
    });

    if (exists === false) {
      newObstacles.push({
        x: obX,
        y: obY,
        d: directionInput,
        id: generateRandID(),
      });
    }

    setObstacles(newObstacles);
    console.log(newObstacles);
  };

  const onResetAll = () => {
    setRobotX(1);
    setRobotDir(0);
    setRobotY(1);
    setRobotState({ x: 1, y: 1, d: Direction.NORTH, s: -1 });
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
      if (o.x === ob.x && o.y === ob.y) continue;
      newObstacles.push(o);
    }
    // Set the obstacles to the new array
    setObstacles(newObstacles);
  };

  const getTime = (commands) => {
    let newTime = time;

    for (let x of commands) {
      let units = x.substring(2, 4);

      if (x.startsWith("SF") || x.startsWith("SB")) {
        // console.log(x[2])
        newTime += FORWARD_TIME * units;
        // console.log(newTime)
      } else if (
        x.startsWith("RB") ||
        x.startsWith("LB") ||
        x.startsWith("RF") ||
        x.startsWith("LF")
      ) {
        newTime += TURN_TIME;
        // console.log(newTime)
      } else {
        continue;
      }
    }

    setTime(newTime);
  };

  const getPath = () => {
    setIsGettingPath(true);

    const api = new QueryAPI("http://localhost:5000");
    api.query(obstacles, robotX, robotY, robotDir, (data, err) => {
      if (data) {
        setPath(data.data.data.path);

        const commands = [];
        for (let x of data.data.data.commands) {
          if (x.startsWith("CAP")) {
            continue;
          }
          commands.push(x);
        }
        setCommands(commands);
        getTime(commands);
        console.log(commands);
      }

      setIsGettingPath(false);
    });
  };

  const createGrid = () => {
    const rows = [];
    let ref_id = 0;
    const robotCells = generateRobotCells();

    // Generate the grid
    for (let i = 0; i < 20; i++) {
      const cells = [
        // Axis
        <td key={i} className="w-5 h-5 md:w-8 md:h-8">
          <span className="text-sky-900 font-bold text-[0.6rem] md:text-base ">
            {19 - i}
          </span>
        </td>,
      ];

      for (let j = 0; j < 20; j++) {
        let foundOb = null;
        let foundRobotCell = null;

        const transformed = transformCoord(j, i);

        for (const ob of obstacles) {
          const obTransformed = transformCoord(ob.x, ob.y);
          if (obTransformed.x === i && obTransformed.y === j) {
            foundOb = ob;
            break;
          }
        }

        if (!foundOb) {
          for (const cell of robotCells) {
            if (cell.x === i && cell.y === j) {
              foundRobotCell = cell;
              break;
            }
          }
        }

        if (foundOb) {
          if (foundOb.d === Direction.WEST) {
            cells.push(
              <td className="border border-l-4 border-l-red-500 w-5 h-5 md:w-8 md:h-8 bg-blue-700">
                <CustomButton
                  onClick={() => onClickObstacle(transformed.y, transformed.x)}
                />
              </td>
            );
          } else if (foundOb.d === Direction.EAST) {
            cells.push(
              <td className="border border-r-4 border-r-red-500 w-5 h-5 md:w-8 md:h-8 bg-blue-700">
                <CustomButton
                  onClick={() => onClickObstacle(transformed.y, transformed.x)}
                />
              </td>
            );
          } else if (foundOb.d === Direction.NORTH) {
            cells.push(
              <td className="border border-t-4 border-t-red-500 w-5 h-5 md:w-8 md:h-8 bg-blue-700">
                <CustomButton
                  onClick={() => onClickObstacle(transformed.y, transformed.x)}
                />
              </td>
            );
          } else if (foundOb.d === Direction.SOUTH) {
            cells.push(
              <td className="border border-b-4 border-b-red-500 w-5 h-5 md:w-8 md:h-8 bg-blue-700">
                <CustomButton
                  onClick={() => onClickObstacle(transformed.y, transformed.x)}
                />
              </td>
            );
          } else if (foundOb.d === Direction.SKIP) {
            cells.push(
              <td className="border w-5 h-5 md:w-8 md:h-8 bg-blue-700" />
            );
          }
        } else if (foundRobotCell) {
          ref_id++;
          if (foundRobotCell.d !== null) {
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
                onClick={() => onClickObstacle(transformed.y, transformed.x)}
              />
            </td>
          );
        }
      }

      rows.push(<tr key={19 - i}>{cells}</tr>);
    }

    const xAxis = [<td key={0} />];
    for (let i = 0; i < 20; i++) {
      xAxis.push(
        <td className="w-5 h-5 md:w-8 md:h-8">
          <span className="text-sky-900 font-bold text-[0.6rem] md:text-base ">
            {i}
          </span>
        </td>
      );
    }
    rows.push(<tr key={20}>{xAxis}</tr>);
    return rows;
  };

  const elementToFollowRef = useRef(null);

  const updateRobotPosition = () => {
    if (elementToFollowRef.current) {
      const rect = elementToFollowRef.current.getBoundingClientRect();
      // Calculate the circle's position based on the element's bounding rectangle
      const circleX = rect.left + rect.width / 2;
      const circleY = rect.top + rect.height / 2;
      // Update the robotState or position of the circle
      let angle = 0;
      if (robotState["d"] == 0) {
        angle = 0;
      } else if (robotState["d"] == 2) {
        angle = 90;
      } else if (robotState["d"] == 4) {
        angle = 180;
      } else if (robotState["d"] == 6) {
        angle = 270;
      }
      setRobotPos({
        x: circleX,
        y: circleY,
        angle: angle,
      });
    }
  };

  useEffect(() => {
    updateRobotPosition();
  }, [robotState]);

  useEffect(() => {
    if (page >= path.length) return;
    setRobotState(path[page]);
  }, [page, path]);

  return (
    <div className="px-10 py-10 inline-flex flex-row">
      {/* Generate grid and axis numbers */}

      <table className="border-collapse border-none border-black ">
        <tbody>{createGrid()}</tbody>
      </table>

      <div
        className="w-32 h-32 bg-blue-500 rounded-full absolute transition-transform duration-500 transform -translate-x-1/2 -translate-y-1/2"
        style={{
          top: `${robotPos.y}px`, // Adjust as needed
          left: `${robotPos.x}px`, // Adjust as needed
          transform: `translate(-50%, -50%) rotate(${robotPos.angle}deg)`,
          transition: "none",
        }}
      >
        <div
          className={`absolute w-11 h-6 ${
            robotState.s != -1 ? "bg-red-500" : "bg-yellow-300"
          } top-0 left-1/2 transform -translate-x-1/2`}
        ></div>
      </div>

      <div className="py-4 px-20 space-x-4">
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
                  <div>X: {ob.x}</div>
                  <div>Y: {ob.y}</div>
                  <div>D: {DirectionToString[ob.d]}</div>
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
