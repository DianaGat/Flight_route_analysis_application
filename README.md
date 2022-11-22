# Flight_route_analysis_application  
In this project, I created an automated application that takes an input by user, and based on the input, pulls data from APIs, procees it and creates static and interactive data vizualizations.  

The application allows user to get data analysis and vizualization for a desired flight route. Insight that will be presented to the user are based on nine (9) month of observations.  
 
## Instructions for the website  
The operator of the application needs to run the python script **MyServer.py**. After that, the web page with port 8080 will be available running the webpage.
The user needs to provide a desired input:  
- flight number;  
- code of the airport of departure (example: Helsinki airport is HEL);  
- code of the airport of arrival.  
If there are any problems finding this informations, this website can be helpful : <https://flightaware.com/live/findflight/>.  
Once this information is given, the user can press the button “Get Flight” and wait for the processing (it may take few minutes). The user will be automatically redirected to a new page where all the plots related to the flight route are present.  

## Importanat limitations  
The application ususe three (3) different API sources. Since this version of application was for private use, the API keys are exctarcted from the initial code and a user will need have their own API keys.  
1) API that is used to get historical flights of an interested route - Aviation Edge. This application can work without this API key, working with ten (10) pre-loaded databases that are loaded in GitHub. A table of available routes can be found at the end of this page. This API does not have a free version, website: <https://aviation-edge.com/premium-api/>.  
2) API that is used to get airport location that is later used in weather API request. The application can not work without this API key. The API key is free with monthly limiatations, website: <https://airlabs.co/#Pricing>.  
3) API that is used to get weather for airports hourly. The application can not work without this API key. The API key is free for 30 days, website: <https://www.worldweatheronline.com/weather-api/api/local-city-town-weather-api.aspx>.  

### Pre-laoded databases: abailable routes  
Departure_airport/Arrival_airport/Flight number  
1	 ams	man	pc7727  
2 	jfk	del	ai102  
3	 icn	cdg	ke901  
4	 hel	oul	ay441  
5	 hel	rix	Bt326  
6	 rix	ber	bt211  
7 	ber	rix	bt214  
8	 rix	hel	bt325  
9	 gru	lis	tp88  
10	krk	hel	ay1164  

![available_routes_input](https://user-images.githubusercontent.com/88134290/203369450-471a2da6-d012-4c16-95ba-d446415bfa19.png)

