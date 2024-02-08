class CustomError extends Error {
  constructor(message, content) {
    super(message);

    // Add a custom property to store content
    this.content = content;

    // Set the name for the error
    this.name = 'CustomError';

    // Ensure that the custom error class captures a stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, CustomError);
    }
  }
}

export var methodType = {get : 'GET', post : 'POST', put : 'PUT', delete : 'DELETE'}

export default class QueryAPI {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async _get(path, headers = {}) {
    return this._request(path, "GET", null, headers);
  }

  async _post(path, data = null, headers = {}) {
    return this._request(path, "POST", data, headers);
  }

  async _put(path, data = null, headers = {}) {
    return this._request(path, "PUT", data, headers);
  }

  async _delete(path, headers = {}) {
    return this._request(path, "DELETE", null, headers);
  }

  async _request(path, method, data, headers) {
    try {
      const url = `${this.baseUrl}/${path}`;

      const requestOptions = {
        method,
        headers: {
          "Content-Type": "application/json",
          ...headers,
        },
      };

      if (data) {
        requestOptions.body = JSON.stringify(data);
      }

      const response = await fetch(url, requestOptions);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const responseData = await response.json();
      return responseData;
    } catch (error) {
      console.error("Request error:", error.message);
      return null;
    }
  }

  async query(obstacles, robotX, robotY, robotDir, callback) {
    const data = {
      obstacles: obstacles,
      robot_x: robotX,
      robot_y: robotY,
      robot_dir: robotDir,
      retrying: false,
    }

    this._post("path", data, {})
      .then(responseData => {
        if (callback) {
          console.log("POST Response:", responseData)
          callback({
            data: responseData,
            error: null,
          })
        }
      })
      .catch(error => {
        console.error("POST Request error:", error)
        if (callback) {
          callback({
            data: data,
            error: error
          })
        }
      })
  }
}