# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
import GetAndProcessFlightData
import CreatePlotHTMLs


PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
WEB_PATH = PROJECT_PATH + "\\web\\" # The web page files
LOCAL_DATABASE_PATH = PROJECT_PATH + "\\LocalDatabase\\" # The local database
CSV_FILENAME = "temp.csv"
RESULT_HTML_TEMPLATE = "resultTemplate.html"
RESULT_HTML = "result.html"

#three API keys
AVIATION_EDGE_API_KEY = "" # it is possible to run the program without this API key 
                           # but the flight routes are limited (see read.me)
                           # Otherwise, put an API key. Website: https://aviation-edge.com/premium-api/
AIRLABS_API_KEY = "" # put here a free ApI key. API website: https://airlabs.co/#Pricing
WORLD_WHEATER_API_KEY = "" # put a free API key here. API website: https://www.worldweatheronline.com/weather-api/api/historical-weather-api.aspx


class S(BaseHTTPRequestHandler):
    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        path = path[1:]
        if path == "":
            path = "index.html"
        try:
            with open(WEB_PATH + path, 'r') as myfile:
                self._set_headers(200)
                message=myfile.read()
                myfile.close()
        except IOError:
            self._set_headers(404)
            message = "NOT FOUND"
        self.wfile.write(bytes(message, "utf8"))
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        message = ""
        path = self.path[1:]
        if path == ("flightRequest.json"):
            self._set_headers(200)
            requestJson = json.loads(post_data)
            is_flight_found = GetAndProcessFlightData.GetAndProcessFlightData(
                requestJson["departureAirport"],
                                    requestJson["arrivalAirport"], 
                                    requestJson["flightNumber"],
                                    os.path.join(PROJECT_PATH, CSV_FILENAME),
                                    LOCAL_DATABASE_PATH,
                                    AVIATION_EDGE_API_KEY,
                                    AIRLABS_API_KEY,
                                    WORLD_WHEATER_API_KEY)
            if is_flight_found:
                html = CreatePlotHTMLs.CreatePlotHTMLs(requestJson["flightNumber"],
                            requestJson["departureAirport"], 
                            requestJson["arrivalAirport"],
                            os.path.join(PROJECT_PATH, CSV_FILENAME),
                            WEB_PATH)
                CreateResultHTML(html)
                message = "OK"
            else:
                message = "NOT OK"
       
        else:
            self._set_headers(404)
            message = "NOT FOUND"
        self.wfile.write(bytes(message, "utf8"))
        
def CreateResultHTML(htmlBody):
    templateFile = open(os.path.join(WEB_PATH, RESULT_HTML_TEMPLATE),mode='r')
    template = templateFile.read()
    templateFile.close()
    index = template.find(r"</body>")
    resultHtml = template[:index - 1] + htmlBody + template[index:] 
    resultFile = open(os.path.join(WEB_PATH, RESULT_HTML),mode='w')
    resultFile.write(resultHtml)
    resultFile.close()

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()