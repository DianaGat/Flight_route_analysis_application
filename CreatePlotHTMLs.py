#3rd part. Here I import ready csv data file nd run analysis. 
#Also it uses the following coomon variables


import numpy as np
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper, ColorBar
from bokeh.transform import transform
from bokeh.models import WheelZoomTool
from bokeh.transform import jitter
import statistics as st
from bokeh.models import BoxAnnotation
from bokeh.models import Label, Range1d
from bokeh.models.tickers import FixedTicker
from bokeh.models.tickers import MonthsTicker
from bokeh.models import Whisker
from bokeh.transform import factor_cmap
from bokeh.layouts import row
from bokeh.plotting import gmap
from bokeh.plotting import figure
from bokeh.models import WMTSTileSource
import pandas as pd
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.models import Arrow, NormalHead, OpenHead, VeeHead
from bokeh.palettes import Spectral5
from bokeh.palettes import Cividis, Category20, Set3
from itertools import product
from bokeh.layouts import gridplot
from bokeh.models import (BasicTicker, Circle,
                          DataRange1d, Grid, LassoSelectTool, LinearAxis,
                          PanTool, Plot, ResetTool, WheelZoomTool)
from bokeh.models import FactorRange
import statistics as st
from bokeh.io import output_file
from bokeh.plotting import reset_output
import scipy.special
from bokeh.embed import components
def CreatePlotHTMLs(iata_flight_number, input_dep_airport, input_arr_airport, 
                    csv_path, output_path):
    output_file('output_file_test.html')
    data = pd.read_csv(csv_path, index_col = 0)
    data.dep_time = pd.to_datetime(data.dep_time)
    data.arr_time = pd.to_datetime(data.arr_time)
    data["arr_weekday"]= data.arr_time.dt.strftime("%A")
    data["dep_weekday"]= data.dep_time.dt.strftime("%A")
    embedHTML = ""
    #plot 1
    group = data.groupby("status")
    group = group.describe()
    p = figure(x_range=np.unique(data.status), 
               height=250, 
               title="Cancelled and landed flights",
               toolbar_location=None, tools="")
    p.vbar(x=np.unique(data.status), 
           top=group.arr_delay["count"], 
           width=0.9, 
           fill_color="#6096ba", alpha = 0.7)
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.yaxis.axis_label = "Count"
    #save(p, os.path.join(output_path, "plot1.html"))
    script, div = components(p)
    embedHTML = div + script
    
    cancelled = data[data["status"]!="landed"]
    data = data[data["status"]=="landed"]
    data.reset_index(drop = True, inplace=True)
    delayed = data[data["arr_delay"] > 0]
    delayed.reset_index(drop = True, inplace=True)
    
    
    strongly_delayed = data[data["arr_delay"] >= 15]
    strongly_delayed.set_index('dep_time',inplace=True)
    strongly_delayed_sorted_resampled = strongly_delayed.resample('M')[['flight_iata']].count()
    mildly_delayed = data[data["arr_delay"] > 0]
    mildly_delayed = mildly_delayed[mildly_delayed["arr_delay"] < 15]                  
    mildly_delayed.set_index('dep_time',inplace=True)
    mildly_delayed_sorted_resampled = mildly_delayed.resample('M')[['flight_iata']].count()
    not_delayed = data[data["arr_delay"] == 0]
    not_delayed.set_index('dep_time',inplace=True)
    not_delayed_sorted_resampled = not_delayed.resample('M')[['flight_iata']].count()
    
    #add delay type
    arr_delay_type= []
    count = 0
    while count != len(data):
        if data.arr_delay[count] == 0:
            arr_delay_type = np.append(arr_delay_type, "No delay")
        elif data.arr_delay[count] < 15:
            arr_delay_type = np.append(arr_delay_type, "Delay < 15 min")
        elif data.arr_delay[count] >= 15:
            arr_delay_type = np.append(arr_delay_type, "Delay > 15 min")
        count = count + 1
    data["arr_delay_type"] = arr_delay_type
    
    #plot2
    k = 6378137
    
    def wgs84_to_web_mercator(df, lon="lon", lat="lat"):
        """Converts decimal longitude/latitude to Web Mercator format"""
        k = 6378137
        df["x"] = df[lon] * (k * np.pi/180.0)
        df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
        return df
    
    print("departureLAT = ", data["dep_airport_lng"])
    df = pd.DataFrame(dict(name=["1", "2"], 
                           lon=[data["dep_airport_lng"][0],
                                data["arr_airport_lng"][0]],
                           lat=[data["dep_airport_lat"][0],
                                data["arr_airport_lat"][0]]))
    wgs84_to_web_mercator(df)
    url = 'http://a.basemaps.cartocdn.com/rastertiles/voyager/{Z}/{X}/{Y}.png'
    attribution = "Tiles by Carto, under CC BY 3.0. Data by OSM, under ODbL"
    p = figure(tools='pan, wheel_zoom', 
               x_axis_type="mercator", y_axis_type="mercator")
    p.add_layout(Arrow(end=OpenHead(line_color="firebrick", line_width=2),
                       x_start=df.lon[0] * (k * np.pi/180.0), 
                       y_start=np.log(np.tan((90 + df.lat[0]) * np.pi/360.0)) * k, 
                       x_end=df.lon[1] * (k * np.pi/180.0), 
                       y_end=np.log(np.tan((90 + df.lat[1]) * np.pi/360.0)) * k))
    
    tile_provider = get_provider(CARTODBPOSITRON)
    p.add_tile(tile_provider)
    p.circle(x=df['x'], y=df['y'], fill_color='orange', size=10)
    script, div = components(p)
    embedHTML = embedHTML + div + script
    
    print(f"Your flight {iata_flight_number} is from {input_dep_airport} to {input_arr_airport}.")
    print(f"Strating from {min(data.dep_date)} to {max(data.dep_date)} there were {len(data)} flights number {iata_flight_number}.")
    print(f"From the time of observation the flight was delayed {len(delayed)} times that is {len(delayed)/len(data)* 100:.1f}% times from all observed flights for this rote.")
    print(f"Maximum time of arrival delay is {max(data.arr_delay)} minutes, minimum is {min(data.arr_delay)}. Average time of arrival delay is {st.mean(data.arr_delay)}, the most frequent time is {st.mode(delayed.arr_delay)}")
    
    embedHTML = embedHTML + f"<p>Your flight {iata_flight_number} is from {input_dep_airport} to {input_arr_airport}<br>"
    embedHTML = embedHTML + f"Strating from {min(data.dep_date)} to {max(data.dep_date)} there were {len(data)} flights number {iata_flight_number}.<br>"
    embedHTML = embedHTML + f"From the time of observation the flight was delayed {len(delayed)} times that is {len(delayed)/len(data)* 100:.1f}% times from all observed flights for this rote.<br>"
    embedHTML = embedHTML + f"Maximum time of arrival delay is {max(data.arr_delay)} minutes, minimum is {min(data.arr_delay)}. Average time of arrival delay is {st.mean(data.arr_delay)}, the most frequent time is {st.mode(delayed.arr_delay)}</p>"
    
    #plot3
    def make_plot(title, hist, edges, x):
        p = figure(title=title, tools='', background_fill_color="#fafafa")
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color="#6096ba", line_color="white", alpha=0.7)
    
        p.y_range.start = 0
        p.legend.location = "center_right"
        p.legend.background_fill_color = "#fefefe"
        p.xaxis.axis_label = 'x'
        p.yaxis.axis_label = 'Pr(x)'
        p.grid.grid_line_color="white"
        return p
    hist, edges = np.histogram(data["arr_delay"], density=True, bins=10)
    x = np.linspace(0.0001, 8.0, 1000)
    sigma = 0.5
    p = make_plot("Distribution for arrival delays", hist, edges, x)
    p.xaxis.axis_label = ""
    p.yaxis.axis_label = "Arrival delay, min"
    script, div = components(p)
    embedHTML = embedHTML + div + script
    
    #plot4
    group = data.groupby(arr_delay_type)
    group = group.describe()
    p = figure(x_range=np.unique(data.arr_delay_type), 
               height=250, 
               title="Flights by delay type",
               toolbar_location=None, 
               tools="")
    p.vbar(x=np.unique(data.arr_delay_type), 
           top=group.arr_delay["count"], 
           width=0.9, 
           fill_color="#6096ba", alpha = 0.7)
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.yaxis.axis_label = "count"
    script, div = components(p)
    embedHTML = embedHTML + div + script
    #plot5
    mode1 = st.mode(data[data["arr_delay_type"] == "Delay < 15 min"]["arr_delay"])
    count1 = data[data["arr_delay_type"] == "Delay < 15 min"]["arr_delay"].count
    mode2 = st.mode(data[data["arr_delay_type"] == "Delay > 15 min"]["arr_delay"])
    delays = ["No delay", "Delay < 15 min", 'Delay > 15 min']
    source = ColumnDataSource(data)
    
    p = figure(height=300, y_range=delays,
               toolbar_location=None, sizing_mode="stretch_width",
               title="Arrival delays by delay type")
    p.circle(x='arr_delay', y=jitter('arr_delay_type', 
                                     width=0.6, 
                                     range=p.y_range),  
             source=source, 
             alpha=0.4, fill_color="black")
    p.x_range.range_padding = 0.01
    p.ygrid.grid_line_color = None
    p.xaxis.ticker = FixedTicker(ticks=list(range(0, int(max(data.arr_delay)), 5)))
    citation1 = Label(x=50, y=70, x_units='screen', y_units='screen',
                     text=f'The most frequent delay time is {int(mode1)} min',
                     border_line_color='black', border_line_alpha=0.0,
                     background_fill_color='white', background_fill_alpha=0.0)
    p.add_layout(citation1)
    citation2 = Label(x=750, y=150, x_units='screen', y_units='screen',
                     text=f'The most frequent delay time is {int(mode2)} min',
                     border_line_color='black', border_line_alpha=0.0,
                     background_fill_color='white', background_fill_alpha=0.0, )
    p.add_layout(citation2)
    low_box = BoxAnnotation(left=0.5, right = 14.5, 
                            fill_alpha=0.2, fill_color='#D55E00')
    mid_box = BoxAnnotation(left = 14.5, 
                            fill_alpha=0.2, fill_color='#0072B2')
    p.add_layout(low_box)
    p.add_layout(mid_box)
    p.xaxis.axis_label = "Arrival delay, min"
    script, div = components(p)
    embedHTML = embedHTML + div + script
    
    #plot6
    source = ColumnDataSource(data)
    hover = HoverTool(
            tooltips=[
                ("dep time", "@dep_time{%d %B %Y}"),
                ("arr delay", "@arr_delay"),
                ("dep weekday", "@dep_weekday"),
                ("dep weather desc", "@dep_weatherDesc"),
                ("arr weather desc", "@arr_weatherDesc"),
                ("dep terminal", "@dep_terminal")
                
            ],
        formatters={'@dep_time': 'datetime'})
    color_mapper = LinearColorMapper(palette="Viridis256", 
                                     low=data.arr_delay.min(), 
                                     high=data.arr_delay.max())
    p = figure(x_axis_type='datetime', y_axis_label='Arrival delay, min', 
               tools=[hover], 
               toolbar_location=None, 
               width=1000, height=600, 
               title="Arrival delay by date")
    p.circle(x='dep_time', y='arr_delay', 
             color=transform('arr_delay', color_mapper), 
             line_color="white", 
             size=7, 
             alpha=0.6, 
             source=data)
    p.xaxis.formatter.days = '%D/%m/%Y'
    p.xaxis.ticker = MonthsTicker(months=list(range(1,13)))
    color_bar = ColorBar(color_mapper=color_mapper, 
                         label_standoff=12, 
                         location=(0,0), 
                         title='Min')
    p.add_layout(color_bar, 'right')
    p.add_tools(WheelZoomTool())
    p.xaxis.axis_label = "Date"
    script, div = components(p)
    embedHTML = embedHTML + div + script
    
    #plot7
    p = figure(width=1000, height=600, 
               x_axis_type="datetime", 
               title="Arrival delay by date")
    p.xgrid.grid_line_color=None
    p.ygrid.grid_line_alpha=0.5
    p.xaxis.axis_label = 'Time'
    p.yaxis.axis_label = 'Value'
    p.line(data.arr_time, data.arr_delay, line_color="#6096ba")
    cr = p.circle(data.arr_time, data.arr_delay, size=10,
                  fill_color="grey", hover_fill_color="firebrick",
                  fill_alpha=0.2, hover_alpha=0.3,
                  line_color=None, hover_line_color="white")
    p.xaxis.formatter.days = '%d/%m/%Y'
    p.xaxis.ticker = MonthsTicker(months=list(range(1,13)))
    p.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))
    p.xaxis.axis_label = "Date"
    p.yaxis.axis_label = "Arrival delay, min"
    script, div = components(p)
    embedHTML = embedHTML + div + script
    
    #plot8
    data.arr_weatherDesc = data.arr_weatherDesc.astype(str)
    group = data.groupby(by=['arr_weatherDesc'])
    group_desc_arr = group.describe().arr_delay
    group_desc_more5_arr = group_desc_arr[group_desc_arr["count"] > 5]
    group_desc_more5_arr
    p = figure(width=1000, height=500, 
               title="Mean arrival delay by weather description",
               x_range=group, 
               toolbar_location=None, 
               tooltips=[("arr weather desc", "@arr_weatherDesc"), 
                         ("mean dep delay", "@arr_delay_mean"), 
                         ("count", "@arr_delay_count")])
    p.vbar(x='arr_weatherDesc', 
           top='arr_delay_mean', 
           width=1, 
           source=group,
           line_color="white", 
           fill_color="#6096ba", 
           alpha = 0.7)
    p.y_range.start = 0
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 1.2
    p.outline_line_color = None
    p.yaxis.axis_label = "Arrival delay, min"
    p.xaxis.axis_label = "Arrival weather description"
    script, div = components(p)
    embedHTML = embedHTML + div + script
    
    #plot9
    data.dep_weatherDesc = data.dep_weatherDesc.astype(str)
    group = data.groupby(by=['dep_weatherDesc'])
    group_desc_arr = group.describe().arr_delay
    group_desc_more5_arr = group_desc_arr[group_desc_arr["count"] > 5]
    group_desc_more5_arr
    p = figure(width=1000, height=500, 
               title="Mean departure delay by weather description",
               x_range=group, 
               toolbar_location=None, 
               tooltips=[("dep weather desc", "@dep_weatherDesc"), 
                         ("mean dep delay", "@arr_delay_mean"), 
                         ("count", "@arr_delay_count")])
    p.vbar(x='dep_weatherDesc', 
           top='arr_delay_mean', 
           width=1, 
           source=group,
           line_color="white", fill_color="#6096ba", alpha = 0.7)
    p.y_range.start = 0
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 1.2
    p.outline_line_color = None
    p.yaxis.axis_label = "Arrival delay, min"
    p.xaxis.axis_label = "Departure weather description"
    script, div = components(p)
    embedHTML = embedHTML + div + script
    
    Heavy_weather_conditions = ["Blizzard",
     'Fog', 'Light rain shower', 'Mist', 'Overcast', "Light snow showers",
    "Freezing fog", "Heavy snow", "Moderate or heavy snow showers",
    'Moderate snow', 'Thundery outbreaks possible', 
    "Moderate or heavy rain shower", "Patchy light rain with thunder", 
    "Patchy freezing drizzle possible", "Blowing snow", "Freezing drizzle", 
    "Heavy rain at times", "Heavy rain", "Light freezing rain"
     ]
    Light_and_moderate_weather_conditions = ['Cloudy', 'Light drizzle',
     'Light rain',  'Light sleet showers', "Clear", "Partly cloudy",
     'Patchy light rain', 'Light snow', 'Patchy rain possible', 'Sunny', 
     "Light sleet showers", "Patchy snow possible", "Patchy light snow", 
     "Light sleet", "Patchy sleet possible", "Patchy light drizzle", 
     "Patchy light rain", "Moderate rain at times",  "Moderate rain",
     ]
    df = data
    count = 0
    while count != len(df.dep_weatherDesc):
        if df.dep_weatherDesc[count] in Heavy_weather_conditions:
            df.dep_weatherDesc[count] = "heavy_weather_cond"
        elif df.dep_weatherDesc[count] in Light_and_moderate_weather_conditions:
            df.dep_weatherDesc[count] = "light_weather_cond"
        count = count + 1
        
    #plot10
    kinds = data.dep_weatherDesc.unique()
    # compute quantiles
    qs = df.groupby("dep_weatherDesc").dep_delay.quantile([0.25, 0.5, 0.75])
    qs = qs.unstack().reset_index()
    qs.columns = ["dep_weatherDesc", "q1", "q2", "q3"]
    df = pd.merge(df, qs, on="dep_weatherDesc", how="left")
    
    # compute IQR outlier bounds
    iqr = df["q3"] - df["q1"]
    df["upper"] = df.q3 + 1.5*iqr
    df["lower"] = df.q1 - 1.5*iqr
    
    qs2 = df.groupby("dep_weatherDesc").arr_delay.quantile([0.25, 0.5, 0.75])
    qs2 = qs2.unstack().reset_index()
    qs2.columns = ["dep_weatherDesc", "q12", "q22", "q32"]
    df = pd.merge(df, qs2, on="dep_weatherDesc", how="left")
    
    # compute IQR outlier bounds
    iqr2 = df["q32"] - df["q12"]
    df["upper2"] = df.q32 + 1.5*iqr2
    df["lower2"] = df.q12 - 1.5*iqr2
    
    source = ColumnDataSource(data = dict(df))#no_delay = not_delayed_sorted_resampled, 
                                              #delay_less_15 = mildly_delayed_sorted_resampled, 
                                              #delay_more_15 = strongly_delayed_sorted_resampled))
    
    p = figure(x_range=kinds, y_range= Range1d(start = 0, 
                                               end = max(df.dep_delay)+10), 
               tools="", toolbar_location=None,
               title="Departure delay by Weather type",
               background_fill_color="#eaefef", 
               y_axis_label="Departure delay", 
               tooltips=[("dep_delay", "@dep_delay")])
    p.xaxis.axis_label = "Departure weather description"
    
    
    # outlier range
    whisker = Whisker(base="dep_weatherDesc", 
                      upper="upper", lower="lower", 
                      source=source)
    whisker.upper_head.size = whisker.lower_head.size = 20
    p.add_layout(whisker)
    
    # quantile boxes
    cmap = factor_cmap("dep_weatherDesc", ["#DC5039", "#FBA40A"], kinds)
    p.vbar("dep_weatherDesc", 0.7, "q2", "q3", 
           source=source, color=cmap, line_color="black", alpha = 0.7)
    p.vbar("dep_weatherDesc", 0.7, "q1", "q2", 
           source=source, color=cmap, line_color="black", alpha = 0.7)
    
    # outliers
    outliers = df[~df.dep_delay.between(df.lower, df.upper)]
    p.scatter("dep_weatherDesc", "dep_delay", 
              source=outliers, size=6, color="black", alpha=0.3)
    
    p.xgrid.grid_line_color = None
    p.axis.major_label_text_font_size="14px"
    p.axis.axis_label_text_font_size="12px"
    p.yaxis.ticker = FixedTicker(ticks=list(range(0, int(max(data.dep_delay)+10), 5)))
    #p2
    p2 = figure(x_range=kinds, y_range= Range1d(start = 0, 
                                                end = max(df.dep_delay)+10), 
                tools="", 
                toolbar_location=None,
                title="Arrival delay by Weather type",
                background_fill_color="#eaefef", 
                y_axis_label="Arrival delay", 
                tooltips=[("arr_delay", "@arr_delay")])
    
    # outlier range
    whisker2 = Whisker(base="dep_weatherDesc", upper="upper2", lower="lower2", 
                       source=source)
    whisker2.upper_head.size = whisker.lower_head.size = 20
    p2.add_layout(whisker2)
    # quantile boxes
    cmap = factor_cmap("dep_weatherDesc", ["#DC5039", "#FBA40A"], kinds)
    p2.vbar("dep_weatherDesc", 0.7, "q22", "q32", 
            source=source, color=cmap, line_color="black")
    p2.vbar("dep_weatherDesc", 0.7, "q12", "q22", 
            source=source, color=cmap, line_color="black")
    # outliers
    outliers2 = df[~df.arr_delay.between(df.lower2, df.upper2)]
    p2.scatter("dep_weatherDesc", "arr_delay", 
               source=outliers2, 
               size=6, 
               color="black", alpha=0.3)
    p2.xgrid.grid_line_color = None
    p2.axis.major_label_text_font_size="14px"
    p2.axis.axis_label_text_font_size="12px"
    p2.yaxis.ticker = FixedTicker(ticks=list(range(0, int(max(data.dep_delay)+10), 5)))
    p2.xaxis.axis_label = "Departure weather description"
    script, div = components(row(p, p2))
    embedHTML = embedHTML + div + script
    
    df2 = data.copy()
    count = 0
    while count != len(df2.dep_tempC):
        if (int(df2.dep_tempC[count]) < 5):
            df2.dep_tempC[count] =  "below_5"
            count = count + 1
        elif (int(df2.dep_tempC[count]) >= 5):
            df2.dep_tempC[count] = "above_5"
            count = count + 1
            
    #plot11
    kinds = df2.dep_tempC.unique()
    # compute quantiles
    qs = df2.groupby("dep_tempC").dep_delay.quantile([0.25, 0.5, 0.75])
    qs = qs.unstack().reset_index()
    qs.columns = ["dep_tempC", "q1", "q2", "q3"]
    df2 = pd.merge(df2, qs, on="dep_tempC", how="left")
    # compute IQR outlier bounds
    iqr = df2["q3"] - df2["q1"]
    df2["upper"] = df2.q3 + 1.5*iqr
    df2["lower"] = df2.q1 - 1.5*iqr
    qs2 = df2.groupby("dep_tempC").arr_delay.quantile([0.25, 0.5, 0.75])
    qs2 = qs2.unstack().reset_index()
    qs2.columns = ["dep_tempC", "q12", "q22", "q32"]
    df2 = pd.merge(df2, qs2, on="dep_tempC", how="left")
    # compute IQR outlier bounds
    iqr2 = df2["q32"] - df2["q12"]
    df2["upper2"] = df2.q32 + 1.5*iqr2
    df2["lower2"] = df2.q12 - 1.5*iqr2
    source = ColumnDataSource(data = dict(df2))#no_delay = not_delayed_sorted_resampled, 
                                               #delay_less_15 = mildly_delayed_sorted_resampled, 
                                               #delay_more_15 = strongly_delayed_sorted_resampled))
    p = figure(x_range=kinds, y_range= Range1d(start = 0, 
                                               end = max(df2.dep_delay)+10), 
               tools="", 
               toolbar_location=None,
               title="Departure delay by Weather type",
               background_fill_color="#eaefef", 
               y_axis_label="Departure delay", 
               tooltips=[("dep_delay", "@dep_delay")])
    p.xaxis.axis_label = "Departure weather description"
    # outlier range
    whisker = Whisker(base="dep_tempC", 
                      upper="upper", lower="lower", 
                      source=source)
    whisker.upper_head.size = whisker.lower_head.size = 20
    p.add_layout(whisker)
    # quantile boxes
    cmap = factor_cmap("dep_tempC", ["#DC5039", "#FBA40A"], kinds)
    p.vbar("dep_tempC", 0.7, "q2", "q3", 
           source=source, color=cmap, line_color="black", alpha = 0.7)
    p.vbar("dep_tempC", 0.7, "q1", "q2", 
           source=source, color=cmap, line_color="black", alpha = 0.7)
    # outliers
    outliers = df2[~df2.dep_delay.between(df2.lower, df2.upper)]
    p.scatter("dep_tempC", "dep_delay", 
              source=outliers, size=6, color="black", alpha=0.3)
    p.xgrid.grid_line_color = None
    p.axis.major_label_text_font_size="14px"
    p.axis.axis_label_text_font_size="12px"
    p.yaxis.ticker = FixedTicker(ticks=list(range(0, int(max(data.dep_delay)+10), 5)))
    #p2
    p2 = figure(x_range=kinds, y_range= Range1d(start = 0, 
                                                end = max(df2.dep_delay)+10), 
                tools="", 
                toolbar_location=None,
                title="Arrival delay by Weather type",
                background_fill_color="#eaefef", 
                y_axis_label="Arrival delay", 
                tooltips=[("arr_delay", "@arr_delay")])
    # outlier range
    whisker2 = Whisker(base="dep_tempC", 
                       upper="upper2", lower="lower2", 
                       source=source)
    whisker2.upper_head.size = whisker.lower_head.size = 20
    p2.add_layout(whisker2)
    # quantile boxes
    cmap = factor_cmap("dep_tempC", ["#DC5039", "#FBA40A"], kinds)
    p2.vbar("dep_tempC", 0.7, "q22", "q32", 
            source=source, color=cmap, line_color="black")
    p2.vbar("dep_tempC", 0.7, "q12", "q22", 
            source=source, color=cmap, line_color="black")
    # outliers
    outliers2 = df2[~df2.arr_delay.between(df2.lower2, df2.upper2)]
    p2.scatter("dep_tempC", "arr_delay", 
               source=outliers2, size=6, color="black", alpha=0.3)
    p2.xgrid.grid_line_color = None
    p2.axis.major_label_text_font_size="14px"
    p2.axis.axis_label_text_font_size="12px"
    p2.yaxis.ticker = FixedTicker(ticks=list(range(0, int(max(data.dep_delay)+10), 5)))
    p2.xaxis.axis_label = "Departure weather description"
    script, div = components(row(p, p2))
    embedHTML = embedHTML + div + script
    
    #plot12
    days = ["December 2021", "2022 January", "February", "March", 
            "April", "May", "June", "July", "August", "September"]
    categories = ["no delay", "delay < 15 min", "delay > 15 min"]
    data1 = {'fruits' : days,
            'no delay' : np.array(not_delayed_sorted_resampled
                                  ).reshape(1,len(not_delayed_sorted_resampled))[0],
            'delay < 15 min' : np.array(mildly_delayed_sorted_resampled
                                        ).reshape(1,len(mildly_delayed_sorted_resampled))[0],
            'delay > 15 min' : np.array(strongly_delayed_sorted_resampled
                                        ).reshape(1,len(strongly_delayed_sorted_resampled))[0]
            }
    hover = HoverTool(
            tooltips=[("% of all flights of the month", "@{pers}{0.2f}%")],
        formatters={
            'pers' : 'printf',   # use 'printf' formatter for 'adj close' field                    
        },)
    x = [ (day, cat) for day in days for cat in categories ]
    counts = sum(zip(data1['no delay'], 
                     data1['delay < 15 min'], 
                     data1['delay > 15 min']), ()) 
    persentage_per_month = []
    start = 0
    end = 3
    count = 0
    while count != len(counts):
        persentage_per_month = np.append(persentage_per_month, 
                                         str(counts[count]/sum(counts[start:end])*100))
        count = count + 1
        persentage_per_month = np.append(persentage_per_month, 
                                         str(counts[count]/sum(counts[start:end])*100))
        count = count + 1
        persentage_per_month = np.append(persentage_per_month, 
                                         str(counts[count]/sum(counts[start:end])*100))
        count = count + 1
        start = start + 3
        end = end + 3
    persentage_per_month = persentage_per_month.tolist()
    data1.update({"persentage": persentage_per_month})
    source = ColumnDataSource(data=dict(x=x, counts=counts, 
                                        pers = persentage_per_month))
    p = figure(x_range=FactorRange(*x), 
               title="Flight delay type by Month",  
               width=1000, height=400, 
               tools = [hover])
    p.vbar(x='x', top='counts', 
           width=0.9, 
           source=source, 
           line_color="white", alpha = 0.7,
    
           # use the palette to colormap based on the the x[1:2] values
           fill_color=factor_cmap('x', 
                                  palette=["#6096ba", '#dbb84f', "#db874f"], 
                                  factors=categories, 
                                  start=1, end=2))
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = "Arrival delay, min"
    #save(p, os.path.join(output_path, "plot12.html"))
    script, div = components(p)
    embedHTML = embedHTML + div + script
        
    Heavy_weather_conditions = ["Blizzard",
     'Fog', 'Light rain shower', 'Mist', 'Overcast', "Light snow showers",
    "Freezing fog", "Heavy snow", "Moderate or heavy snow showers",
    'Moderate snow', 'Thundery outbreaks possible', 
    "Moderate or heavy rain shower", "Patchy light rain with thunder", 
    "Patchy freezing drizzle possible", "Blowing snow", "Freezing drizzle", 
    "Heavy rain at times", "Heavy rain", "Light freezing rain"
     ]
    Light_and_moderate_weather_conditions = ['Cloudy', 'Light drizzle',
     'Light rain',  'Light sleet showers', "Clear", "Partly cloudy",
     'Patchy light rain', 'Light snow', 'Patchy rain possible', 'Sunny', 
     "Light sleet showers", "Patchy snow possible", "Patchy light snow", 
     "Light sleet", "Patchy sleet possible", "Patchy light drizzle", 
     "Patchy light rain", "Moderate rain at times",  "Moderate rain",
     ]
    df = data
    count = 0
    while count != len(df.dep_weatherDesc):
        if df.dep_weatherDesc[count] in Heavy_weather_conditions:
            df.dep_weatherDesc[count] = "heavy_weather_cond"
        elif df.dep_weatherDesc[count] in Light_and_moderate_weather_conditions:
            df.dep_weatherDesc[count] = "light_weather_cond"
        count = count + 1
    
    #plot13
    kinds = df.dep_weekday.unique()
    array = kinds
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                'Friday','Saturday', 'Sunday']
    sorted_array = []
    prestored = []
    count = 0
    count_w = 0
    while count != len(array):
        if array[count] == weekdays[count_w]:
            prestored = np.append(prestored, weekdays[count_w])
            count_w = 0
            count = count + 1
        else:
            count_w = count_w + 1
    sorted_array = sorted(prestored, key=weekdays.index)
    kinds = sorted_array
    # compute quantiles
    qs = df.groupby("dep_weekday").dep_delay.quantile([0.25, 0.5, 0.75])
    qs = qs.unstack().reset_index()
    qs.columns = ["dep_weekday", "q1", "q2", "q3"]
    df = pd.merge(df, qs, on="dep_weekday", how="left")
    # compute IQR outlier bounds
    iqr = df["q3"] - df["q1"]
    df["upper"] = df.q3 + 1.5*iqr
    df["lower"] = df.q1 - 1.5*iqr
    #p2
    kinds2 = df.arr_weekday.unique()
    array2 = kinds2
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                'Friday','Saturday', 'Sunday']
    sorted_array2 = []
    prestored2 = []
    count = 0
    count_w = 0
    while count != len(array2):
        if array[count] == weekdays[count_w]:
            prestored2 = np.append(prestored2, weekdays[count_w])
            count_w = 0
            count = count + 1
        else:
            count_w = count_w + 1
    sorted_array2 = sorted(prestored2, key=weekdays.index)
    kinds2 = sorted_array2
    # compute quantiles
    qs2 = df.groupby("arr_weekday").arr_delay.quantile([0.25, 0.5, 0.75])
    qs2 = qs2.unstack().reset_index()
    qs2.columns = ["arr_weekday", "q12", "q22", "q32"]
    df = pd.merge(df, qs2, on="arr_weekday", how="left")
    # compute IQR outlier bounds
    iqr2 = df["q32"] - df["q12"]
    df["upper2"] = df.q32 + 1.5*iqr2
    df["lower2"] = df.q12 - 1.5*iqr2
    source = ColumnDataSource(df)
    p = figure(x_range=kinds, 
               tools="", toolbar_location=None,
               title="Departure delay by dep_weekday",
               background_fill_color="#eaefef", 
               y_axis_label="Departure delay", 
               tooltips=[("dep_delay", "@dep_delay")])
    # outlier range
    whisker = Whisker(base="dep_weekday", 
                      upper="upper", lower="lower", 
                      source=source)
    whisker.upper_head.size = whisker.lower_head.size = 20
    p.add_layout(whisker)
    # quantile boxes
    cmap = factor_cmap("dep_weekday", Set3[7], kinds)
    p.vbar("dep_weekday", 0.7, "q2", "q3", 
           source=source, color=cmap, line_color="black")
    p.vbar("dep_weekday", 0.7, "q1", "q2", 
           source=source, color=cmap, line_color="black")
    # outliers
    outliers = df[~df.dep_delay.between(df.lower, df.upper)]
    p.scatter("dep_weekday", "dep_delay", 
              source=outliers, size=6, color="black", alpha=0.3)
    p.xgrid.grid_line_color = None
    p.axis.major_label_text_font_size="14px"
    p.axis.axis_label_text_font_size="12px"
    #p2
    p2 = figure(x_range=kinds2, 
                tools="", toolbar_location=None,
                title="Arrival delay by arr_weekday",
                background_fill_color="#eaefef", 
                y_axis_label="Arrival delay", 
                tooltips=[("arr_delay", "@arr_delay")])
    # outlier range
    whisker2 = Whisker(base="arr_weekday", 
                       upper="upper2", lower="lower2", 
                       source=source)
    whisker2.upper_head.size = whisker.lower_head.size = 20
    p2.add_layout(whisker2)
    # quantile boxes
    cmap = factor_cmap("arr_weekday", Set3[7], kinds2)
    p2.vbar("arr_weekday", 0.7, "q22", "q32", 
            source=source, color=cmap, line_color="black")
    p2.vbar("arr_weekday", 0.7, "q12", "q22", 
            source=source, color=cmap, line_color="black")
    # outliers
    outliers2 = df[~df.arr_delay.between(df.lower2, df.upper2)]
    p2.scatter("arr_weekday", "arr_delay", 
               source=outliers, size=6, color="black", alpha=0.3)
    p2.xgrid.grid_line_color = None
    p2.axis.major_label_text_font_size="14px"
    p2.axis.axis_label_text_font_size="12px"
    script, div = components(row(p, p2))
    embedHTML = embedHTML + div + script

    
    #plot14
    data.dep_terminal = data.dep_terminal.astype(str)
    data.dep_weatherDesc = data.dep_weatherDesc.astype(str)
    group = data.groupby(by=["dep_terminal", 'dep_weatherDesc'])
    p = figure(width=800, height=500, 
               title="Mean dep delay by departure wather type and departure terminal if different",
               x_range=group, 
               toolbar_location=None, 
               tooltips=[("mean dep delay", "@dep_delay_mean"), 
                         ("count", "@dep_delay_count")])
    p.vbar(x='dep_terminal_dep_weatherDesc', top='dep_delay_mean', 
           width=1, 
           source=group,
           line_color="white", fill_color="#0072B2", alpha = 0.7)
    p.y_range.start = 0
    p.x_range.range_padding = 0.05
    p.xgrid.grid_line_color = None
    p.xaxis.axis_label = "Weather type and dep terminal if different"
    p.xaxis.major_label_orientation = 1.2
    p.outline_line_color = None
    p.yaxis.axis_label = "Departure delay, min"
    #save(p, os.path.join(output_path, "plot14.html"))
    script, div = components(p)
    embedHTML = embedHTML + div + script
    
    #plot15
    SPECIES = sorted(df.dep_weatherDesc.unique())
    ATTRS = ("dep_delay", "arr_delay", "dep_cloudcover", 
             "dep_tempC", "dep_windspeedKmph")
    N = len(ATTRS)
    source = ColumnDataSource(data=df)
    xdrs = [DataRange1d(bounds=None) for _ in range(N)]
    ydrs = [DataRange1d(bounds=None) for _ in range(N)]
    plots = []
    for i, (y, x) in enumerate(product(ATTRS, reversed(ATTRS))):
        p = Plot(x_range=xdrs[i%N], y_range=ydrs[i//N],
                 background_fill_color="#fafafa",
                 border_fill_color="white", 
                 width=200, height=200, 
                 min_border=5)
        if i % N == 0:  # first column
            p.min_border_left = p.min_border + 4
            p.width += 40
            yaxis = LinearAxis(axis_label=y)
            yaxis.major_label_orientation = "vertical"
            p.add_layout(yaxis, "left")
            yticker = yaxis.ticker
        else:
            yticker = BasicTicker()
        p.add_layout(Grid(dimension=1, ticker=yticker))
        if i >= N*(N-1):  # last row
            p.min_border_bottom = p.min_border + 40
            p.height += 40
            xaxis = LinearAxis(axis_label=x)
            p.add_layout(xaxis, "below")
            xticker = xaxis.ticker
        else:
            xticker = BasicTicker()
        p.add_layout(Grid(dimension=0, ticker=xticker))
        circle = Circle(x=x, y=y, 
                        fill_alpha=0.6, 
                        size=5, 
                        line_color=None,
                        fill_color=factor_cmap('dep_weatherDesc', 
                                               ["#000003", "#35B778"], 
                                               SPECIES))
        r = p.add_glyph(source, circle)
        p.x_range.renderers.append(r)
        p.y_range.renderers.append(r)
        # suppress the diagonal
        if (i%N) + (i//N) == N-1:
            r.visible = False
            p.grid.grid_line_color = None
        p.add_tools(PanTool(), WheelZoomTool(), ResetTool(), LassoSelectTool())
        plots.append(p)
    script, div = components(gridplot(plots, ncols=N))
    embedHTML = embedHTML + div + script
    return embedHTML
    
    