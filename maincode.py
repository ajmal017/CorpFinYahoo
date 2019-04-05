import numpy as np
import pandas as pd
import matplotlib.pyplot as pl

#List of the companies for this study
tickerlist=['CF','SCHW','L']

#Import S&P adjusted closing price as reference
ttl=pd.read_csv('^GSPC.csv',usecols=['Date','Adj Close'])
ttl.columns=['Date','S&P_adjclose']
ttl['S&P_Return']=ttl['S&P_adjclose'].rolling(2).apply(lambda x: (x[1]/x[0]-1)*12*100)


#Add adjusted closing prices of different companies to the existing table
#Add name of the companies to column names
for i in tickerlist:
    company=pd.read_csv(str(i)+'.csv',usecols=['Date','Adj Close'])
    company.columns=['Date',str(i)+'_adjclose']
    ttl=ttl.merge(company,on='Date',suffixes=('_',''))
    ttl[str(i)+'_Return']=ttl[str(i)+'_adjclose'].rolling(2).apply( lambda x: (x[1]/x[0]-1)*12*100)


#Removing the first and the last row
ttl=ttl.iloc[1:len(ttl.Date)-1]


#Import required Bokeh libraries
from bokeh.layouts import widgetbox, row, column
from bokeh.plotting import figure, show, output_file
from bokeh.models import Circle, ColumnDataSource, Grid, Line, LinearAxis, Plot, Range1d, Label
from bokeh.io import curdoc, output_notebook
from bokeh.models.widgets import Select, Button, PreText

#Changing the 'Date' column of the table to time-series
ttl.Date=pd.to_datetime(ttl.Date)

#Initializations for Bokeh
company='CF'
source = ColumnDataSource(data={'x1': ttl['Date'],'x2': ttl['S&P_Return'], 'y1': ttl['CF_Return'],'y2': ttl['CF_adjclose'],'c':[company]*ttl['S&P_Return'].size})
#Initialize a text block for showing the Stock-S&P relevance 
stats = PreText(text='Stock Volatility (Beta) : '+str(np.polyfit(source.data['x2'],source.data['y1'],1)[0]), width=500,height=50)



#Figure 0, showing adjusted closing price through time
p0 = figure(x_axis_type="datetime", plot_width=400, plot_height=400)
p0.line('x1', 'y2' ,source=source, color='black', legend='c')
p0.grid.grid_line_alpha=0.3
p0.xaxis.axis_label = 'Date'
p0.yaxis.axis_label = 'Stock Closing Price'
p0.legend.location = "top_left"

#Figure 1, showing stock annual return through time
p1 = figure(x_axis_type="datetime",plot_width=400, plot_height=400)
p1.grid.grid_line_alpha=0.3
p1.xaxis.axis_label = 'Date'
p1.yaxis.axis_label = 'Stock Annual Return'
p1.line('x1', 'x2' ,source=source, color='grey', legend='S&P')
p1.line('x1', 'y1'  ,source=source, color='orange', legend='c')
p1.legend.location = "top_left"

#Figure 2, showing stock annual return against S&P annual return
p2 = figure(plot_width=400, plot_height=400)
p2.grid.grid_line_alpha=0.3
p2.xaxis.axis_label = 'S&P Annual Return'
p2.yaxis.axis_label = str(source.data['c'][0])+' Annual Return'
p2.scatter('x2', 'y1' ,source=source, color='orange' , legend='c')
p2.legend.location = "top_left"

#Adding an interactive trend line for figure 2
x = np.linspace(min(ttl['S&P_Return']), max(ttl['S&P_Return']), 10)
y = np.polyfit(source.data['x2'],source.data['y1'],1)[1] + np.polyfit(source.data['x2'],source.data['y1'],1)[0] * x
lines_source = ColumnDataSource(data=dict(x=x, y=y))
line = Line(x='x', y='y', line_color="#666699", line_width=2)
p2.add_glyph(lines_source, line)


#Linking plots, so they move together
p0.x_range = p1.x_range
p1.y_range = p2.y_range


def update_plot(attr, old, new):
	#Function to update company data by user input
    global company
    company=select.value
    source.data = {'x1': ttl['Date'],'x2': ttl['S&P_Return'], 'y1': ttl[str(company)+'_Return'],'y2': ttl[str(company)+'_adjclose'],'c':[company]*ttl['S&P_Return'].size}
    stats.text = 'Stock Volatility (Beta) : '+str(np.polyfit(source.data['x2'],source.data['y1'],1)[0])
    p2.yaxis.axis_label = str(source.data['c'][0])+' Annual Return'


#User input dropdown menu
select = Select(title="Which company:", value=tickerlist[0], options=tickerlist)
select.on_change('value',update_plot)


#Creating the final layout of the page
layout=column(row([widgetbox(select),stats]),row([p0,p1,p2]))
#show(layout)
curdoc().add_root(layout)
#output_file("js_on_change.html")