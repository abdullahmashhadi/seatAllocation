from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

client = MongoClient("mongodb+srv://abdullah6blue:RFMv0wxcMsCddGj8@cluster0.2cjvid1.mongodb.net/")
db = client.seat_booking
seats_collection = db.seats

# Dictionary to store session data
user_sessions = {}

# Initialize seats
def initialize_seats():
    seats_collection.delete_many({})  # Clear existing data
    seats = []
    for i in range(1, 46):
        seats.append({"seat_number": i, "status": "available", "gender": None})
    seats_collection.insert_many(seats)

# Uncomment this to initialize seats once
# initialize_seats()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_seats', methods=['GET'])
def get_seats():
    seats = list(seats_collection.find())
    for seat in seats:
        seat['_id'] = str(seat['_id'])  # Convert ObjectId to string
    return jsonify(seats)

@socketio.on('connect')
def handle_connect():
    emit('bot_response', "Welcome to the seat booking system. Please specify your gender: male or female.")

@socketio.on('chat_message')
def handle_chat_message(data):
    session_id = request.sid
    message = data.get('message')

    # Initialize session if not present
    if session_id not in user_sessions:
        user_sessions[session_id] = {}

    user_session = user_sessions[session_id]

    if 'gender' not in user_session:
        if message.lower() in ["male", "female"]:
            user_session['gender'] = message.lower()
            emit('bot_response', "Please enter the seat number you want to book in the format 'book 23'.")
        else:
            emit('bot_response', "Please specify your gender: male or female.")
        return

    gender = user_session['gender']

    if message.lower().startswith("book "):
        try:
            seat_number = int(message.split(" ")[1])
        except (IndexError, ValueError):
            emit('bot_response', "Invalid format. Please use 'book 23'.")
            return

        seat = seats_collection.find_one({"seat_number": seat_number})
        if not seat:
            emit('bot_response', "Invalid seat number.")
            return

        if seat['status'] != "available":
            emit('bot_response', f"Seat number {seat_number} is already booked.")
            return

        # Check adjacent seats for gender clash
        seat_map = {
            1: [2], 2: [1], 3: [4], 4: [3], 5: [6], 6: [5], 7: [8], 8: [7], 9: [10], 10: [9], 
            11: [12], 12: [11], 13: [14], 14: [13], 15: [16], 16: [15], 
            17: [18], 18: [17], 19: [20], 20: [19], 21: [22], 22: [21], 
            23: [24], 24: [23], 25: [26], 26: [25], 27: [28], 28: [27], 
            29: [30], 30: [29], 31: [32], 32: [31], 33: [34], 34: [33], 
            35: [36], 36: [35], 37: [38], 38: [37], 39: [40], 40: [39], 
            41: [42], 42: [41,43], 43: [42,44], 44: [43,45], 45: [44]
        }

        adjacent_seats = seat_map.get(seat_number, [])
        for adj_seat in adjacent_seats:
            adj_seat_data = seats_collection.find_one({"seat_number": adj_seat})
            if adj_seat_data and adj_seat_data['status'] != "available" and adj_seat_data['gender'] != gender:
                emit('bot_response', f"Adjacent seat conflict with seat number {adj_seat}.")
                return

        # Mark the seat as temporarily booked
        seat['status'] = "selected"
        seat['gender'] = gender
        seats_collection.update_one({"seat_number": seat_number}, {"$set": seat})

        # Convert ObjectId to string for emitting
        seat['_id'] = str(seat['_id'])
        emit('update_seat', seat)
        emit('bot_response', f"Seat {seat_number} is temporarily booked for you. Type 'confirm {seat_number}' to confirm.")
        return

    if message.lower().startswith("confirm "):
        try:
            seat_number = int(message.split(" ")[1])
        except (IndexError, ValueError):
            emit('bot_response', "Invalid format. Please use 'confirm 23'.")
            return

        seat = seats_collection.find_one({"seat_number": seat_number})
        if not seat or seat['status'] != "selected" or seat['gender'] != gender:
            emit('bot_response', f"Seat number {seat_number} is not temporarily booked by you.")
            return
        
        # Change the status to the user's gender
        seat['status'] = gender
        seats_collection.update_one({"seat_number": seat_number}, {"$set": seat})

        # Convert ObjectId to string for emitting
        seat['_id'] = str(seat['_id'])
        emit('update_seat', seat)
        emit('bot_response', f"Seat {seat_number} is now confirmed for you.")
        return

    # If the message doesn't match any command
    emit('bot_response', "Sorry, I didn't understand that. Please use 'book <seat_number>' or 'confirm <seat_number>'.")

if __name__ == '__main__':
    socketio.run(app, debug=True)
