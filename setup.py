import threading
import sys
from pathlib import Path
from time import time, sleep
import socket

from .gaze_filter import OneEuroFilter, IvtFilter

from talon import Module

subtree_dir = Path(__file__).parent / ".subtrees"
package_paths = [
    str(subtree_dir / "gaze-ocr"),
    str(subtree_dir / "screen-ocr"),
    str(subtree_dir / "rapidfuzz/src"),
    str(subtree_dir / "jarowinkler/src"),
]
saved_path = sys.path.copy()
try:
    sys.path.extend([path for path in package_paths if path not in sys.path])
    import gaze_ocr
    import gaze_ocr.talon
finally:
    sys.path = saved_path.copy()

mod = Module()

stop_event = threading.Event()
gaze_thread = None

client_socket = None
server_ip = '127.0.0.1'
server_port = 12345

[oe_filter_x, oe_filter_y, ivt_filter] = [OneEuroFilter(), OneEuroFilter(), IvtFilter(v_threshold=3)]

def on_ready():
    global tracker, client_socket
    tracker = gaze_ocr.talon.TalonEyeTracker()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


@mod.action_class
class GazeActions:
    def send_gaze_point(offset_right: int = 0, offset_down: int = 0):
        """Send the gaze point to the server"""
        on_ready()
        global gaze_thread, stop_event, client_socket

        def run_gaze_loop():
            """Run the loop in a separate thread"""
            count = 0
            start_time = time()

            while not stop_event.is_set():
                gaze_point = tracker.get_gaze_point()

                if not gaze_point:
                    continue

                timestamp = time()
                print(f"Tobii Eye Tracker ({timestampe}): ({int(gaze_point[0])},{int(gaze_point[1])})")

                # Send to socket
                if client_socket:
                    try:
                        x0 = oe_filter_x(timestamp, gaze_point[0])
                        y0 = oe_filter_y(timestamp, gaze_point[1])
                        fp = ivt_filter(timestamp, x0, y0)

                        t = int(timestamp * 1000)
                        x = int(fp[0])
                        y = int(fp[1])

                        data = f"{t},1,{x},{y}"
                        client_socket.sendto(data.encode(), (server_ip, server_port))

                    except Exception as e:
                        print(f"Error sending data: {e}")

                sleep(1/110)
                count += 1

            end_time = time()
            elapsed_time = end_time - start_time

            if elapsed_time > 0:
                sampling_frequency = count / elapsed_time
                print(f"Loop count: {count}")
                print(f"Elapsed time: {elapsed_time:.2f} seconds")
                print(f"Sampling frequency: {sampling_frequency:.2f} loops/sec")
            else:
                print("The elapsed time was too short to calculate the sampling frequency.")

            # Close the socket connection
            if client_socket:
                client_socket.close()

        # Create and start the thread
        stop_event.clear()
        gaze_thread = threading.Thread(target=run_gaze_loop)
        gaze_thread.start()

    def stop_sending_gaze_point():
        """Stop sending the gaze point to the server"""
        global gaze_thread, stop_event

        if gaze_thread is not None and gaze_thread.is_alive():
            print("Stop request")
            stop_event.set()
            gaze_thread.join()
            print("Tracking completely stopped")
        else:
            print("Thread is not running.")
