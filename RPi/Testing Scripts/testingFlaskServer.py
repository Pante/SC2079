from flask import Flask, request
from flasgger import Swagger, swag_from


app = Flask(__name__)
swagger = Swagger(app)

@app.route('/rpi', methods=['GET', 'POST'])
@swag_from({
    'parameters': [
        {
            'name': 'Param1',
            'description': 'Description of Param1',
            'in': 'body',
            'type': 'string',
            'required': 'true',
        },
        {
            'name': 'Param2',
            'description': 'Description of Param2',
            'in': 'body',
            'type': 'string',
            'required': 'true',
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful response',
        },
        '400': {
            'description': 'Bad request',
        }
    }
})
def rpi():
    """
    Endpoint to perform an action on Raspberry Pi.
    ---
    parameters:
      - name: action
        in: formData
        type: string
        required: true
        description: The action to perform on Raspberry Pi.
      - name: description
        in: formData
        type: string
        required: true
        description: Description of the action.
    responses:
      200:
        description: Action performed successfully.
    """
    
    data = request.get_json()
    action = data.get('action')
    description = data.get('description')

    # Perform action on Raspberry Pi based on the provided parameters
    if request.method == 'POST':
      return "Successful POST request, The action is: " + action + " and the description is: " + description + "."
      # return "Ths is a response to the POST request."
    elif request.method == 'GET':
      return "Successful GET request, The action is: " + action + " and the description is: " + description + "."

    return 'Action performed successfully'

if __name__ == '__main__':
    app.run()

