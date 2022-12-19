import streamlit as s
import csv
import pydeck as pdk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
from PIL import Image


filename="BostonCrime2021_7000_sample (3).csv"

def welcome_page():
    s.title("2021 Boston Crime Data Website")
    image_path= 'C:'+"\\"+'Users'+"\\"+'tchit\Desktop\Python_Assignments\Final Project 230\Boston_Picture.jpg'
    img = Image.open(image_path)
    s.image(img,width=600)
    s.write("This website includes a few ways to visualize data about crimes of 2021 in Boston.")
    s.write("Use the sidebar to see options.")

def open_file():
    df = pd.read_csv(filename)
    return df

def weighted_crime(offense, to_use_weighted_crime): #this categorizes how severe a crime was. 3 being most severe and dangerous
    if to_use_weighted_crime:
        if offense == "DRUGS - POSSESSION/ SALE/ MANUFACTURING/ USE" or offense == "SUDDEN DEATH" or offense == "HARASSMENT/ CRIMINAL HARASSMENT" or offense == "BURGLARY - COMMERICAL" or offense == "SICK/INJURED/MEDICAL - PERSON" or offense == "AUTO THEFT" or offense == "ASSAULT - AGGRAVATED" or offense == "FIRE REPORT" or offense == "WEAPON VIOLATION - CARRY/ POSSESSING/ SALE/ TRAFFICKING/ OTHER" or offense == "BURGLARY - RESIDENTIAL" or offense == "MISSING PERSON" or offense == "STOLEN PROPERTY - BUYING / RECEIVING / POSSESSING" or offense == "AUTO THEFT - LEASED/RENTED VEHICLE" or offense == "EXTORTION OR BLACKMAIL" or offense == "FIREARM/WEAPON - FOUND OR CONFISCATED" or offense == "AUTO THEFT - MOTORCYCLE / SCOOTER" or offense == "OTHER OFFENSE" or offense == "BREAKING AND ENTERING (B&E) MOTOR VEHICLE" or offense == "MURDER, NON-NEGLIGIENT MANSLAUGHTER" or offense == "EXPLOSIVES - TURNED IN OR FOUND" or offense == "DRUGS - POSSESSION OF DRUG PARAPHANALIA" or offense == "BOMB THREAT" or offense == "OPERATING UNDER THE INFLUENCE (OUI) DRUGS" or offense == "DANGEROUS OR HAZARDOUS CONDITION" or offense == "ANIMAL ABUSE":
            return 3
        elif offense == "M/V ACCIDENT - PROPERTY DAMAGE" or offense == "ROBBERY" or offense == "PROPERTY - LOST/ MISSING" or offense == "LARCENY THEFT FROM MV - NON-ACCESSORY" or offense == "LARCENY THEFT FROM BUILDING" or offense == "BALLISTICS EVIDENCE/FOUND" or offense == "SICK ASSIST - DRUG RELATED ILLNESS" or offense == "MISSING PERSON - LOCATED" or offense == "LARCENY SHOPLIFTING" or offense == "M/V ACCIDENT - INVOLVING PEDESTRIAN - INJURY" or offense == "FRAUD - CREDIT CARD / ATM FRAUD" or offense == "HARBOR INCIDENT / VIOLATION" or offense == "PROPERTY - LOST THEN LOCATED" or offense == "FORGERY / COUNTERFEITING" or offense == "INTIMIDATING WITNESS" or offense == "GRAFFITI" or offense == "LARCENY PICK-POCKET" or offense == "DISTURBING THE PEACE/ DISORDERLY CONDUCT/ GATHERING CAUSING ANNOYANCE/ NOISY PAR" or offense == "AIRCRAFT INCIDENTS" or offense == "AFFRAY" or offense == "BREAKING AND ENTERING (B&E) MOTOR VEHICLE (NO PROPERTY STOLEN)" or offense == "FUGITIVE FROM JUSTICE" or offense == "M/V ACCIDENT - POLICE VEHICLE" or offense == "DEATH INVESTIGATION" or offense == "MISSING PERSON - NOT REPORTED - LOCATED" or offense == "PROPERTY - STOLEN THEN RECOVERED" or offense == "EVADING FARE" or offense == "PROSTITUTION - SOLICITING" or offense == "ARSON" or offense == "PRISONER - SUICIDE / SUICIDE ATTEMPT":
            return 2
        else:
            return 1
    else:
        return 1

def make_data_weighted(file=open_file()): #this adds entries for having weighted crimes
    for i in range(len(file)):
        for j in range(weighted_crime(file.iloc[i,3],True)-1):
            file.loc[len(file)]=file.loc[i]
    return file

def pivot_table(df=open_file(),values=False): #values determine whether to show crime or weighted crime. False means it will show only number of crimes
    if values:
        df = make_data_weighted()
    df=df.pivot_table(index="DISTRICT",columns="DAY_OF_WEEK", values="INCIDENT_NUMBER",aggfunc='count')
    weekday_order={'Friday':5,'Monday':1,'Saturday':6,'Sunday':7,'Thursday':4,'Tuesday':2,'Wednesday':3}
    df.loc["x"]=weekday_order #we add this to our pivot table in order to sort weekdays
    df=df.sort_values(by='x', axis=1) #we sort weekdays by using our added row
    df.drop(df.index[(len(df)-1):len(df)],axis=0,inplace=True) #we remove the row that we added, since we don't need it anymore
    total_number_list=[]
    for i in range(len(df)):
        total_number=0
        for j in range(7):
            total_number=total_number+float(df.iloc[i,j])
        total_number_list.append(int(total_number))
    df['Total']=total_number_list
    df=df.div(52) #we divide by 52 since there are approximately 52 weeks in a year, so that's the
    if values:
        df=df.div(max(df["Total"]))#this normalizes the values so that max value=1. This is because value of weighted crime doesn't have a meaning. It is only important because it shows us relative amounts.
    return df

def map_page():
    file=open_file()
    #cleaning up the file because some locations are at (0,0) which isn't in US. This is important because we don't want streamlit to show the world map. So, we delete those entries with location (0,0)
    for j in range(2): #this code is for getting rid of locations (0,0) - locations that arent in boston.
        for i in range(len(file)):
            if i<len(file):
                i=len(file)-i-1
                if int(file.iloc[i,14])==0 or int(file.iloc[i,15])==0:
                    file=file.drop(file.index[i])
    #filtering for timeframe
    time1, time2 = s.sidebar.slider("Timeframe (hours)",min_value=0,max_value=24,value=[0,24])
    file=file[(file["HOUR"]>=time1)&(file["HOUR"]<=time2)] #filtering the whole data based on the hour of crime
    #filtering for districts
    district_list=pd.DataFrame(["A1","A7","A15","B2","B3","C6","C11","D4","D14","E5","E13","E18","External"]) #Blank entries are included in "External"
    for i in range(len(file)):
        count=0
        for j in district_list:
            count+=1
            if file.iloc[i,4] == j:
                count=0
        if count==13:
            file.iloc[i,4]="External" #this makes every blank entry external. It was possible to leave it as it is and include in unknown or neglect it, but that's what I thought was the right thing to do

    districts=s.multiselect("Districts",district_list)
    file=file[(file["DISTRICT"].isin(districts))]

    #getting locations and cleaning the data up since entries of location aren't always correct. Some districts' location doesn't match the actual district
    file["Lat"]= file["Lat"].astype(float)
    file["Long"]=file["Long"].astype(float)
    lat_avg=file.iloc[:,14].mean()
    lat_std=np.std(file.iloc[:,14])
    long_avg=file.iloc[:,15].mean()
    long_std=np.std(file.iloc[:,15])
    weird_constant=0
    for i in range(len(file)):
        i=i-weird_constant
        if abs(file.iloc[i,14]-lat_avg)>3*abs(lat_std) or abs(file.iloc[i,15]-long_avg)>3*abs(long_std): #this roughly takes out the crimes that are way out of the district. It uses standard deviation and average
            file=file.drop(file.index[i])
            weird_constant+=1
    location_list=file.iloc[:,14:16]
    location_list.rename(columns={"Lat":"lat", "Long": "lon"}, inplace= True)


    #choosing map
    map_choice = s.sidebar.selectbox("Graph", ["Scatter Plot","Chart"])
    if map_choice == "Scatter Plot":
        #for points on the map
        df = pd.DataFrame(
        location_list,
        columns=['lat', 'lon'])
        s.map(df)
    elif map_choice == "Chart":
        #for chart on the map
        pitch = s.sidebar.slider("Pitch",30,90)
        pitch=90-pitch
        initial_view_state1 = pdk.ViewState(
            latitude=location_list["lat"].mean(),
            longitude=location_list["lon"].mean(),
            zoom=9.5,
            pitch=pitch)
        layer1 = pdk.Layer(type='HexagonLayer',
            data=location_list,
            get_position='[lon, lat]',
            radius=180,
            elevation_scale=20,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
            coverage=1)
        map1 = pdk.Deck(initial_view_state=initial_view_state1,
                        layers=[layer1])
        s.pydeck_chart(map1)

def line_chart(df=open_file()):
    df=df.pivot_table(index="DAY_OF_WEEK",columns="HOUR", values="INCIDENT_NUMBER",aggfunc='count')
    weekday_order={'Friday':5,'Monday':1,'Saturday':6,'Sunday':7,'Thursday':4,'Tuesday':2,'Wednesday':3}
    df["x"]=weekday_order #we add this to our pivot table in order to sort weekdays
    df=df.sort_values(by='x', axis=0) #we sort weekdays by using our added column
    df=df.drop(columns=["x"]) #we remove the column that we added, since we don't need it anymore
    line_chart_data=pd.DataFrame(index=range(1),columns=range(1))
    for i in range(len(df)):
        expected_time_of_crime_committed=0
        for j in range(len(df.iloc[i,:])):
            expected_time_of_crime_committed+=df.iloc[i,j]*j/df.iloc[i,:].sum()
        line_chart_data.loc[df.index[i]]=expected_time_of_crime_committed
    line_chart_data=line_chart_data.dropna()
    line_chart_data=line_chart_data.rename(columns= {0:"Expected Hour of Crime"})
    line_chart_data=line_chart_data.rename(index={'Friday':5,'Monday':1,'Saturday':6,'Sunday':7,'Thursday':4,'Tuesday':2,'Wednesday':3})
    s.line_chart(data = line_chart_data)


def histogram(weighted_crime_variable):
    hours=[] #this is a list of hours on which crimes were commited. This way we know how many crimes were commited at a given hour
    file=open_file()
    day_of_the_week = s.selectbox("Day of the Week", ["Whole Week","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    for i in range(len(file)):
        k=int(file.iloc[i,11])
        if file.iloc[i,10]==day_of_the_week or day_of_the_week=="Whole Week":
            for j in range(weighted_crime(file.iloc[i,3],weighted_crime_variable)):
                hours.append(k)
    normaliser_constant=0
    for i in range(len(hours)):
        if normaliser_constant<hours.count(hours[i]):
            normaliser_constant=hours.count(hours[i])
    fig, ax = plt.subplots()
    if weighted_crime_variable:
        ax.hist(hours,edgecolor='black', bins=24, weights=np.ones_like(hours)/normaliser_constant) #weighted crime is on the scale of 0-1
        ax.set_ylabel('Relative Frequency of Crimes Committed')
    else:
        constant_for_correcting_scale=1/52
        if day_of_the_week=="Whole Week":
            constant_for_correcting_scale=1/(7*52)
        ax.hist(hours,edgecolor='black', bins=24, weights=np.ones_like(hours)*constant_for_correcting_scale)
        ax.set_ylabel('Frequency (crimes/day)')
    ax.set_xlabel('Hour')
    s.pyplot(fig)

    pass
def pie_chart(weighted_crime_variable):
    if weighted_crime_variable:
        s.title("Share of Crimes Committed in Districts (Weighted)")
    else:
        s.title("Share of Crimes Committed in Districts")
    district_list = [["A1",0],["A7",0],["A15",0],["B2",0],["B3",0],["C6",0],["C11",0],["D4",0],["D14",0],["E5",0],["E13",0],["E18",0],["External",0]]
    file=open_file()
    for p, i in file.iterrows():
        count=0
        for j in range(len(district_list)):
            count+=1
            if i["DISTRICT"] == district_list[j][0]:
                count=0

                district_list[j][1]+=weighted_crime(i["OFFENSE_DESCRIPTION"],weighted_crime_variable)
        if count==13:
            district_list[12][1]+=weighted_crime(i["OFFENSE_DESCRIPTION"],weighted_crime_variable)

    sizes=[]
    labels=[]
    district_list = sorted(district_list, key=lambda x: x[1]) #for having prettier pie chart
    for i in district_list: #list comprehension
        labels.append(i[0])
        sizes.append(i[1])
    fig1, ax1 = plt.subplots()

    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=0)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    s.pyplot(fig1)
    pass
s.sidebar.header("Inputs")
Type_Charts = ["None","Map", "Histogram", "Pie Chart", "Pivot Table", "Line Chart"]
graph_selection = s.sidebar.selectbox("Select the type of chart",Type_Charts)


if graph_selection=="None":
    welcome_page()
elif graph_selection=="Histogram":
    weighted_crime_variable=s.sidebar.checkbox("Weighted Crime")
    s.sidebar.info('Weighted crime roughly takes into account how severe the crime was. Severity of crimes are estimated on a scale of 1 - 3.' , icon="ℹ️")
    s.sidebar.info('Crime with severity of 1: Verbal Dispute')
    s.sidebar.info('Crime with severity of 2: Robbery')
    s.sidebar.info('Crime with severity of 3: Murder')
    histogram(weighted_crime_variable)
elif graph_selection == "Map":
    map_page()
elif graph_selection == "Pie Chart":
    weighted_crime_variable=s.sidebar.checkbox("Weighted Crime")
    s.sidebar.info('Weighted crime roughly takes into account how severe the crime was. Severity of crimes are estimated on a scale of 1 - 3.' , icon="ℹ️")
    s.sidebar.info('Crime with severity of 1: Verbal Dispute')
    s.sidebar.info('Crime with severity of 2: Robbery')
    s.sidebar.info('Crime with severity of 3: Murder')
    pie_chart(weighted_crime_variable)
elif graph_selection == "Pivot Table":
    weighted_crime_variable=s.sidebar.checkbox("Weighted Crime")
    s.sidebar.info('Weighted crime roughly takes into account how severe the crime was. Severity of crimes are estimated on a scale of 1 - 3.' , icon="ℹ️")
    s.sidebar.info('Crime with severity of 1: Verbal Dispute')
    s.sidebar.info('Crime with severity of 2: Robbery')
    s.sidebar.info('Crime with severity of 3: Murder')
    if not weighted_crime_variable:
        s.title("Average Number of Crimes Per District")
    else:
        s.title("Weighted Crimes")
        please_wait_message=s.empty()
        please_wait_message.text("Don't click anything while the code is being loaded. Please wait...")
    file = pivot_table(values=weighted_crime_variable)
    if weighted_crime_variable:
        please_wait_message.empty()
    s.write(file)
elif graph_selection=="Line Chart":
    s.title("Expected Time For Committing a Crime As a Function of Weekdays")
    line_chart()
