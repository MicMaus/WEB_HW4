from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import socket
import threading
import json
from datetime import datetime
from urllib.parse import parse_qs

home_page = "index.html"
error_page = "error.html"

host = "127.0.0.1"
socket_port = 5000
http_port = 3000


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Construct the file path dynamically
            path = self.path.lstrip("/")
            # for the 1st run open index.html:
            if not path:
                path = home_page
            file_path = os.path.join("files", path)
            # or to ensure the path is based on the location of the script use:
            # file_path = os.path.join(os.path.dirname(__file__), "files", path)

            with open(file_path, "rb") as file:
                content = file.read()
            self.send_response(200)

        # managing 404 error:
        except FileNotFoundError:
            file_path = os.path.join(os.path.dirname(__file__), "files", error_page)
            with open(file_path, "rb") as file:
                content = file.read()
            self.send_response(404)

        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        form_data = parse_qs(self.rfile.read(content_length).decode("utf-8"))

        # Extract the relevant form data
        message = form_data.get("message", [""])[0]
        username = form_data.get("username", [""])[0]

        # send the data to the server
        send_to_udp_server({"username": username, "message": message})

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Thank you for your message!")


def run():
    server_address = ("0.0.0.0", http_port)
    http = HTTPServer(server_address, RequestHandler)
    http.serve_forever()


# data send to udp server:
def send_to_udp_server(data_dict):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(json.dumps(data_dict).encode("utf-8"), (host, socket_port))


# data received by a server:
def udp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        while True:
            data, _ = s.recvfrom(1024)
            data_dict = json.loads(data.decode("utf-8"))
            save_to_json(data_dict)


# data saved to json
def save_to_json(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(os.path.dirname(__file__), "files", "storage", "data.json")

    # opening the dict and create it if doesn't exist:
    try:
        with open(file_path, "r") as json_file:
            existing_dict = json.load(json_file)
    except json.decoder.JSONDecodeError:
        existing_dict = {}

    # add the new data to the dictionary
    existing_dict[timestamp] = data

    # write the new dict to the json file:
    with open(file_path, "w") as json_file:
        json.dump(existing_dict, json_file, indent=2)
        json_file.write("\n")


# Creating 2 separate threads:
http_server_thread = threading.Thread(target=run)
udp_server_thread = threading.Thread(target=udp_server, args=(host, socket_port))


if __name__ == "__main__":
    print("server started")

    http_server_thread.start()
    udp_server_thread.start()

    http_server_thread.join()
    udp_server_thread.join()
