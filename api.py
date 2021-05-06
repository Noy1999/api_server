from flask import Flask, request, jsonify, abort
from logic import Query
from flask_httpauth import HTTPTokenAuth


app = Flask(__name__)
new_query = Query()
auth = HTTPTokenAuth(scheme='Bearer')  # This is the authentication of the server including tokens for users
tokens = {"1234": "Noy",
          "5678": "Yuval",
          "9101": "Naama",
          "1213": "Noa"}
@auth.verify_token
def verify_token(token):
    """
    :param token: the function gets a token
    :return: returns the relevant user for the token (by checking tokens)
    """
    if token in tokens:
        return tokens[token]


@app.route('/send_message', methods=['POST'])
def send_message():
    """
    :return: the function uses the data of a new message for sending that it gets from the request and returns the
    inserted details to the user (as json) unless there are errors and the user will get an error message
    """
    try:
        data = request.get_json()
        if data:
            errors = new_query.input_checking(data)
            if not errors:
                new_query.connection()
                new_query.insert(**data)
                new_query.disconnection()
                return jsonify(data)
            return jsonify(f"Please insert data in the following fields: {','.join(errors)}")
        else:
            return jsonify("Please insert data")
    except Exception as error:
        abort(400, f'An error occurred!!! {str(error)}')


@app.route('/get_message', methods=['GET'])
@auth.login_required
def get_one_message():
    """
    :return: the function uses the data from the request - an id of a specific message (int) and a username (str) by
    authentication token and returns the relevant message for the user (as json)
    """
    try:
        id = request.args.get("id")
        user = auth.current_user()
        new_query.connection()
        message = new_query.get_specific_message(id)
        new_query.update_one_reading_status(id, user)
        new_query.disconnection()
        if message:
            return jsonify(f"The message for id: {id} is: {message}")
        return jsonify(f"No messages for {id} id")
    except Exception as error:
        abort(400, f'An error occurred!!! {str(error)}')


@app.route('/get_messages', methods=['GET'])
@auth.login_required
def get_messages_for_user():
    """
    :return: the function uses the data from the request - a username (str) by authentication token and returns
    all messages for the user (as json)
    """
    try:
        user = auth.current_user()
        new_query.connection()
        messages = new_query.get_messages_for_user(user)
        new_query.update_reading_status(user)
        new_query.disconnection()
        return jsonify(f"The messages for {user} are: {messages}") if messages else jsonify(f"No messages for {user}")
    except Exception as error:
        abort(400, f'An error occurred!!! {str(error)}')


@app.route('/get_unread_messages', methods=['GET'])
@auth.login_required
def get_unread_messages():
    """
    :return: the function uses the data from the request - a username (str) by authentication token and returns
    all unread messages for the user (as json)
    """
    try:
        user = auth.current_user()
        new_query.connection()
        messages = new_query.get_unread_messages_for_user(user)
        new_query.update_reading_status(user)
        new_query.disconnection()
        return jsonify(f"The messages for {user} are: {messages}") if messages else jsonify(
            f"No unread messages for {user}")
    except Exception as error:
        abort(400, f'An error occurred!!! {str(error)}')


@app.route('/delete_message', methods=['POST'])
@auth.login_required
def delete_message():
    """
    :return: the function uses the data from the request - a username (str) by authentication token, an id (int) and a
    type of user - sender|receiver and username) and returns a success\fail delete message accordingly
    """
    try:
        user = auth.current_user()
        data = request.get_json()
        data.update({"user": user})
        errors = new_query.input_checking(data)
        if not errors:
            new_query.connection()
            new_query.delete(**data)
            new_query.disconnection()
            return jsonify(f"successfully deleted")
        return jsonify(f"Please insert data in the following fields: {','.join(errors)}")
    except Exception as error:
        abort(400, f'An error occurred!!! {str(error)}')


if __name__ == '__main__':
    app.run(debug=True)
