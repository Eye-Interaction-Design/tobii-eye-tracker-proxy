from dataclasses import asdict
import json
import socket
from threading import Event, Thread, Lock
from time import sleep

from talon import app, Module
from .eye_tracker import TobiiEyeTracker


# Set up the server to listen on all interfaces.
server_ip = 'localhost'
server_port = 12344

tracker = TobiiEyeTracker()

# Create a UDP socket and bind it to the specified IP and port.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

terminate_event = Event()

# A thread-safe set to keep track of registered clients (each as a tuple (IP, port)).
clients = set()
clients_lock = Lock()


def registration_listener():
    """
    Listen for registration messages from clients.
    When any message is received, add the sender's address to the clients set.
    """
    while not terminate_event.is_set():
        try:
            # Set a timeout so we can periodically check for termination.
            server_socket.settimeout(1.0)
            data, addr = server_socket.recvfrom(1024)
            # Simply register the client's address.
            with clients_lock:
                if addr not in clients:
                    print(f"Registered client: {addr}")
                    clients.add(addr)
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Error in registration listener: {e}")


def eye_tracker_listener(tracker: TobiiEyeTracker, sock: socket.socket, terminate_event: Event):
    """
    Subscribe to the Tobii eye tracker, filter gaze data,
    and send the JSON data via UDP to all registered clients.
    """

    while not terminate_event.is_set():
        frame = tracker.now

        if frame:
            try:
                # Construct the JSON data.
                data = json.dumps(asdict(frame))
                print(data)

                # Send the JSON data to all registered clients.
                with clients_lock:
                    for client_addr in clients:
                        try:
                            sock.sendto(data.encode(), client_addr)
                        except Exception as send_e:
                            print(f"Error sending to {client_addr}: {send_e}")
            except Exception as e:
                print(f"Error in subscribe_tobii: {e}")

        sleep(1 / 100)


registration_thread = Thread(target=registration_listener, daemon=True)
gaze_thread = Thread(target=eye_tracker_listener, args=(tracker, server_socket, terminate_event))


def on_ready():
    terminate_event.clear()
    # Start the registration listener thread (daemon thread so it stops with the main program).
    registration_thread.start()
    # Start the gaze data subscription and sending thread.
    gaze_thread.start()

app.register("ready", on_ready)


mod = Module()
@mod.action_class
class GazeActions:
    def start_listening() -> None:
        """Send the gaze point to the server"""
        on_ready()

    def stop_listening() -> None:
        """Stop sending the gaze point to the server"""
        terminate_event.set()
        gaze_thread.join()
        registration_thread.join()
