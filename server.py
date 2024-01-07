import socket
import os
import json
import flipdot
import traceback

import flipdot.flipdot


class Server(socket.socket):
    contentTypes = {
        "": "text/plain",
        "html": "text/html",
        "js": "text/javascript",
        "css": "text/css",
        "txt": "text/plain",
        "json": "application/json",
        "ico": "image/x-icon",
    }

    def __init__(self, displayobj: flipdot.flipdot.FlipDot):
        self.display = displayobj  # display driver object
        self.path = "/home/qetesh/flipdot/www/"  # path to www files in on-device filesystem

        # configure socket
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse address and port in case of script restart
        self.bind(('localhost', 8080))  # http port 80 on localhost
        self.listen()  # start to listen for connections
        self.settimeout(0)  # set socket to non-blocking
        self.conn = None  # used to store current connection handler

    def send_pixels(self):
        self.send_header(filename="status.txt")
        for y in range(self.display.height):
            row = ""
            for x in range(self.display.width):
                row += str(self.display.pixel(x, y))
            if y < self.display.height - 1:
                row += "\n"
            self.conn_send(row)

    def send_file(self, filename: str):
        # send file from filesystem
        print("Send file", filename)
        ext = filename.split(".")[-1]
        readmode = "rb"
        if ext in self.contentTypes:
            if self.contentTypes[ext].split("/")[0] == "text":
                readmode = "r"
        self.send_header(filename=filename)
        with open(filename, readmode) as f:
            file = f.read()
            if readmode == "r":
                file = file.encode()
            self.conn.send(file)

    def send_header(self, filename: str = ""):
        ext = filename.split(".")[-1]
        if ext not in self.contentTypes:
            ext = ""
        self.conn_send('HTTP/1.1 200 OK\n')
        self.conn_send(f'Content-Type: {self.contentTypes.get(ext)}\n')
        self.conn_send('Connection: close\n\n')

    def send_rcode(self, code: int, text: str):
        # send HTTP code to client
        self.conn_send(f'HTTP/1.1 {code}\n')
        self.conn_send('Content-Type: text/html\n')
        self.conn_send('Connection: close\n\n')
        self.conn_send(f'{code}: {text}\n')

    def send_json(self, data: dict):
        # send JSON string to client
        self.send_header("json")
        self.conn_send(json.dumps(data))

    def conn_send(self, data: str) -> None:
        try:
            self.conn.send(data.encode())
        except BrokenPipeError:
            pass
    
    def accept_http(self) -> bool:
        # accept connection and parse incoming data
        try:
            self.conn, addr = super().accept()
        except OSError:
            return False
        # print("Connection from ", str(addr))

        # split headers and body
        raw = None
        try:
            raw = self.conn.recv(4096).decode()
            rawheaders, body = raw.split("\r\n\r\n", 1)
        except ValueError as e:
            print("Exception while unpacking the data:", repr(e))
            print(raw)
            self.conn.close()
            return False
        finally:
            del raw

        # parse headers
        rawheaders = rawheaders.split("\r\n")
        request = rawheaders.pop(0).split(" ")  # first line always contains the method, uri and HTTP version
        headers = {}
        for header in rawheaders:  # rest of the header block gets parsed into dictionary
            header = header.split(":", 1)
            headers[header[0].strip()] = header[1].strip()

        # get method and uri
        method = request[0]
        uri = request[1].split("/")
        # print(f"Parsed Request: {method}, {uri}, {body}")

        # a lot can go wrong. catch everything so the server doesnt stop working...
        try:
            # handle GET requests
            if method == "GET":
                # check if uri is an existing file, if so, send it
                if uri[1] in os.listdir(self.path):
                    # print(f"Send {uri}")
                    self.send_file(self.path + uri[1])
                # if uri is /pixels we want to send the pixel array
                elif uri[1] == "pixels":
                    # print("Send pixel-array")
                    self.send_pixels()
                # in case uri is empty, send the index.html
                elif uri[1] == "":
                    # print("Send index.html")
                    self.send_file(self.path + "index.html")
                # for get requests on /json answer with the state of the endpoint
                elif uri[1] == "json":
                    if len(uri) > 2:
                        answer = self.jsonparse({uri[2]: None})
                    else:  # send status
                        answer = self.jsonparse({"light": None, "text": None, "mode": None})
                    self.send_json(answer)
                elif uri[1] == "wifi":
                    if len(uri) == 4:
                        ssid = uri[2]
                        key = uri[3]
                        print(f"New WiFi Data received: {ssid}, {key}")
                        with open("wifi.txt", "w") as file:
                            file.write(ssid)
                            file.write("\n")
                            file.write(key)
                            file.write("\n")
                        print("WiFi Data stored. Rebooting...")
                        self.send_header()
                        # machine.reset()
                # 404 for everything else
                else:
                    self.send_rcode(404, f"{'/'.join(uri)} not found")

            # handle POST requests
            elif method == "POST":
                # if uri is json we expect a json string in the body and try to parse it
                if uri[1] == "json":
                    try:
                        js = json.loads(body)
                    except ValueError:  # body does not contain a valid json string
                        self.send_rcode(400, "Request does not contain a valid json string.")
                    else:
                        # We have valid json. Parsing...
                        self.send_json(self.jsonparse(js))
                else:
                    # send 404 for unknown uri
                    self.send_rcode(404, f"{'/'.join(uri)} not found")
            else:
                # send 501 for unknown method
                self.send_rcode(501, f"Method {method} not implemented")
        except Exception as e:
            # something went wrong, send error code
            self.send_rcode(500, "Server Error: " + traceback.format_exc())

        # close connection and free ram
        self.conn.close()
        return True

    def jsonparse(self, js: dict) -> dict:
        answer = {}
        for command in js.keys():
            params = js[command]
            print(f"Received command {command}: {params}")
            if command == "setpixel":  # set pixels at x, y to color
                if type(params) == list:
                    answer[command] = []
                    for pixel in params:
                        x = pixel.get("x")
                        y = pixel.get("y")
                        color = pixel.get("c")
                        if None in (x, y, color):
                            answer[command] += "Parameters Missing"
                            break
                        x = int(x)
                        y = int(y)
                        color = int(color)
                        # print(f"Set Pixel at {x}, {y} to {color}")
                        self.display.pixel(x, y, color)
                        self.display.show()
                        answer[command].append(pixel)
                else:
                    answer[command] = "Expecting a list of parameters"
            elif command == "mode":
                if params is not None:
                    self.display.mode = params
                    self.display.lastClock = ""
                answer[command] = self.display.mode
            elif command == "text":
                if type(params) == dict:
                    if params.get("font"):
                        self.display.font = params.get("font")
                    if params.get("align"):
                        self.display.align = params.get("align")
                    if params.get("text") is not None:
                        self.display.lastText = params.get("text")
                    self.display.text(self.display.lastText)
                answer[command] = {"text": self.display.lastText,
                                   "align": self.display.align,
                                   "font": self.display.font}
            elif command == "fonts":
                answer[command] = list(self.display.fonts.keys())
            elif command == "clear":
                self.display.clear()
                self.display.show()
                answer[command] = "OK"
            elif command == "fill":
                self.display.fill(params)
                self.display.show()
            else:
                answer[command] = "Unknown Command"
        print("Answer:", answer)
        return answer
