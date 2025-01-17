import pandas as pd
import requests
from fpdf import FPDF
import seaborn as sns
from matplotlib import pyplot as plt
from fastapi import APIRouter
from starlette.responses import FileResponse
from fastapi import APIRouter , Request , Depends
from sqlalchemy.ext.asyncio import AsyncSession
import os
from datetime import datetime
import matplotlib.ticker as ticker
# from authentication.authorization import get_token_async
from sqlalchemy.ext.asyncio import AsyncSession
import matplotlib.dates as md
import numpy as np
from matplotlib.ticker import FuncFormatter
from storage.database_vdm_async import get_vdm_db_async
from routers.vessel import vessel_color
from storage.database_vdm_async import get_vdm_db_async
from matplotlib.ticker import MultipleLocator
from routers.pdf.vpq_columns_data import vsl_info, main_engine_info, propeller_info, me_cons_info, electrical_loads_info, aux_oil_fired_info, thruste_infor, anchor_info, tank_capacities_info, vessel_equipment_info, vessel_intakes_info, general_distribution_20_info, general_distribution_40_info, general_distribution_40hc_info, general_distribution_45hc, vessel_reefer_capacity, miscellaneous_info, communication_info, vessel_plans_info, aux_engine_consumptions_info, auxiliary_engine_1_info, auxiliary_engine_2_info, auxiliary_engine_3_info, auxiliary_engine_4_info, auxiliary_engine_5_info

import plotly.graph_objects as go

from plotly.subplots import make_subplots
import urllib.parse

import io
from PIL import Image

import plotly.graph_objects as go

from plotly.subplots import make_subplots
import matplotlib.dates as mdates

import warnings
warnings.filterwarnings("ignore")

#  return FileResponse(path = './documents/'+vessel_name+'_MSC_Sox_all_year.pdf',filename='MSC_SOX.pdf')




oceanix_logo_path = "./images/logo/oceanix_logo.png"
msc_logo_path = "./images/logo/msc.png"


router = APIRouter()


def make_directory(path):
    isExist = os.path.exists(path)
    if not isExist:

    # Create a new directory because it does not exist
        os.makedirs(path)

path = "documents"
make_directory(path)

path = "images"
make_directory(path)


@router.delete('/api/v1/documents')
def index():
    
    path = r"\documents"

    
    dir_list = os.listdir(path)
    # ti_c=[]
    print(dir_list)
    for i in dir_list:
        path1=""
        path1=path+'\\'+i
        print(path1)
        ti_c=os.path.getmtime(path1)
        startdate=datetime.fromtimestamp(ti_c).strftime('%Y-%m-%d %H:%M:%S')
        print(startdate)
        # continue  
        startdate=datetime.strptime(str(startdate),'%Y-%m-%d %H:%M:%S')
        # print("fjjjjjjjjjjjjjjjjj",startdate)
        now = datetime.now()
        print(now)
        dif=now-startdate
        dif=dif.seconds/3600
        print(dif)
        if dif > 1:
            if os.path.isfile(path1):
                os.remove(path1)
                print(path1)
                print("ddddddd")
            else:
                print("Error: %s file not found" % path1) 



@router.post('/api/v1/pdf/sox')
async def index(info : Request , tabname:str = None, selection:str = None ,vessel_name:str = None , method:str = None , start_date:str = None, end_date:str = None,year:str = None,fleet:str =None , types: str = None):
    s = await info.json()
    # print(s)
    print("Start")

    if tabname == 'All':

        if types == '0':
            types = 'MSC SM Vessels'
        elif types == '7':
            types = 'Charter Vessels'
        elif types == '8':
            types = 'Sorrento Vessels'
    else:
        types = ''
        pass


    data1 = pd.DataFrame.from_dict(s['data']['ae_me']['daily_data'])
    data1 = data1.replace([0], np.nan)
    pivoted_data1 = data1.pivot(index='date_month',columns='category',values='ae_sox_value').reset_index()
    lst = data1['date_month'].unique().tolist()
    pivoted_data1 = pivoted_data1.set_index('date_month')
    pivoted_data1 = pivoted_data1.loc[lst]   
    pivoted_data1 = pivoted_data1.reset_index()

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    ax = pivoted_data1.plot(x='date_month', kind='bar', stacked=True,figsize=(50,20))
    ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))
    plt.xticks(rotation=45, ha='right',fontsize=33)
    plt.yticks(fontsize=33)
    plt.xlabel('Date',fontweight="bold",size=44)
    plt.ylabel('Total SOx Daily (MT)',fontweight="bold",size=44)
    ax.legend(title=None,fontsize=35)
    plt.savefig('./images/sox_vessel_date_meaeblr_daily.png', bbox_inches="tight")  
    plt.clf()

    data2 = pd.DataFrame.from_dict(s['data']['ae_me']['monthly_data'])
    data2 = data2.replace([0], np.nan)
    pivoted_data2 = data2.pivot(index='date_month',columns='category',values='ae_sox_value').reset_index()
    pivoted_data2['Month'] = pd.to_datetime(pivoted_data2['date_month'], format='%Y-%B')

    pivoted_data2 = pivoted_data2.sort_values('Month')

    pivoted_data2 = pivoted_data2.drop(['Month'],axis=1)

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    ax = pivoted_data2.plot(x='date_month', kind='bar', stacked=True,figsize=(20,10))

    plt.xlabel('Date',fontweight="bold",size=15)
    plt.ylabel('Total SOx Monthly (MT)',fontweight="bold",size=15)
    plt.xticks(rotation=45, ha='right',fontsize=13)
    plt.yticks(fontsize=13)
    ax.legend(title=None,fontsize=15)

    plt.savefig('./images/sox_vessel_date_meaeblr_monthly.png', bbox_inches="tight")
    plt.clf()

    data3 = pd.DataFrame.from_dict(s['data']['ae_me']['daily_sox'])
    data3 = data3.replace([0], np.nan)
    pivoted_data3 = data3.pivot(index='date_month',columns='category',values='ae_sox_value').reset_index()
    lst = data3['date_month'].unique().tolist()
    pivoted_data3 = pivoted_data3.set_index('date_month')
    pivoted_data3 = pivoted_data3.loc[lst]   
    pivoted_data3 = pivoted_data3.reset_index()

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    ax = pivoted_data3.plot(x='date_month', kind='bar', stacked=True,figsize=(50,20))
    ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))
    plt.xticks(rotation=45, ha='right',fontsize=33)
    plt.yticks(fontsize=33)
    plt.xlabel('Date',fontweight="bold",size=44)
    plt.ylabel('Total SOx Daily (MT)',fontweight="bold",size=44)
    ax.legend(title=None,fontsize=35)

    plt.xlabel('Date',fontweight="bold",size=16)
    plt.ylabel('Total SOx Daily (MT)',fontweight="bold",size=16)
    ax.legend(title=None)
    plt.savefig('./images/sox_vessel_date_fueltype_daily.png', bbox_inches="tight")
    plt.clf()

    data4 = pd.DataFrame.from_dict(s['data']['ae_me']['monthly_sox'])
    data4 = data4.replace([0], np.nan)
    pivoted_data4 = data4.pivot(index='date_month',columns='category',values='ae_sox_value').reset_index()
    try:
        pivoted_data4['Month'] = pd.to_datetime(pivoted_data4['date_month'], format='%Y-%B')
    except:    
        pivoted_data4['Month'] = pd.to_datetime(pivoted_data4['date_month'], format='%b %Y')

    pivoted_data4 = pivoted_data4.sort_values('Month')

    pivoted_data4 = pivoted_data4.drop(['Month'],axis=1)

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    ax = pivoted_data4.plot(x='date_month', kind='bar', stacked=True,figsize=(20,10))

    plt.xlabel('Date',fontweight="bold",size=16)
    plt.ylabel('Total SOx Monthly (MT)',fontweight="bold",size=16)
    plt.xticks(rotation=45, ha='right',fontsize=15)
    plt.yticks(fontsize=13)
    ax.legend(title=None,fontsize=15)
    plt.savefig('./images/sox_vessel_date_fueltype_monthly.png', bbox_inches="tight")
    plt.clf()

    data6 = pd.DataFrame.from_dict(s['data']['datatable'])
    df_main = data6[data6['name'].isin(["Main Engine", "AE Total", "Boiler", "Total"])].rename(columns={
        'name': 'Machinery',
        'total_fuel': 'Total Fuel',
        'total_sox': 'Total SOx'
    })

    # Creating the second DataFrame with "HS", "LS", and "ULS"
    df_fuel_types = data6[data6['name'].isin(["HS", "LS", "ULS","Total"])].rename(columns={
        'name': 'Fuel Type',
        'total_fuel': 'Total Fuel',
        'total_sox': 'Total SOx'
    })

    # Displaying the resulting DataFrames
    # print("DataFrame 1 (Main Engine, AE Total, Boiler):")
    # print(df_main)

    # print("\nDataFrame 2 (HS, LS, ULS):")
    # print(df_fuel_types)

    def simple_table(spacing=3):

        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        
        pdf.image(msc_logo_path,160,8,w=30)

        pdf.set_xy(80,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 60, "SOx Report",ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)

        
        if tabname=='Vessel':
            pdf.cell(10, 2, "Vessel :"+" "+vessel_name,ln=True)
        elif tabname=='Fleet':
            pdf.cell(10, 2, "Fleet :"+" "+fleet,ln=True) 
        elif tabname=='All':   
            pdf.cell(10, 2, "Type : "+" "+types,ln=True)  
        if selection == 'Year':
            pdf.cell(10, 12,"Monitoring period :  "+" "+ year,ln=True)
        else:
            pdf.cell(10, 12,"Monitoring period :  "+" "+ start_date+" "+"TO"+" "+end_date,ln=True)
        pdf.cell(10, 2, "Method :"+" "+method,ln=True)
        pdf.line(10, 75, 190, 75)

        pdf.set_xy(20,75)
        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Daily SOx',ln=True) 
        pdf.image("./images/sox_vessel_date_meaeblr_daily.png",10,95,w=185,h=80)


        pdf.set_xy(20,175)
        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Monthly SOx',ln=True) 
        pdf.image("./images/sox_vessel_date_meaeblr_monthly.png",10,195,w=185,h=80)

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 2 page **********************************************************#
        pdf.add_page()  

        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)

        pdf.set_xy(20,10)
        pdf.cell(180, 10, 'Fuel Type Daily SOx',ln=True) 
        pdf.image("./images/sox_vessel_date_fueltype_daily.png",10,25,w=185,h=80)

        pdf.set_xy(20,130)
        pdf.cell(180, 10, 'Fuel Type Monthly SOx',ln=True) 
        pdf.image("./images/sox_vessel_date_fueltype_monthly.png",10,145,w=185,h=80)


        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 3 page **********************************************************#
        pdf.add_page()  
        spacing = 2
        table_head1 = [df_main.columns.tolist()]
        table_values1 = df_main.values.tolist()
        pdf.set_font("Arial", 'B', size=8.5)
        col_width = pdf.w /3.5  # Adjust column width based on number of columns
        row_height = pdf.font_size
        pdf.cell(180, 10, 'SOx Data Table', ln=True)


        # Add table header for the first DataFrame
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        for row in table_head1:
            for item in row:
                pdf.cell(col_width, row_height * spacing, txt=item, border=1, fill=True)
            pdf.ln(row_height * spacing)

        # Add table data for the first DataFrame
        pdf.set_font("Arial", size=8.5)
        pdf.set_text_color(0, 0, 0)
        for row in table_values1:
            for item in row:
                pdf.cell(col_width, row_height * spacing, txt=str(item), border=1)
            pdf.ln(row_height * spacing)

        pdf.ln(10)  # Adjust the value to set the desired gap size

        # Set title and formatting for the second DataFrame
        pdf.set_font("Arial", 'B', size=18)
        pdf.set_text_color(25, 47, 133)

        # Format for DataFrame header
        table_head2 = [df_fuel_types.columns.tolist()]
        table_values2 = df_fuel_types.values.tolist()
        pdf.set_font("Arial", 'B', size=8.5)
        col_width = pdf.w /3.5  # Adjust column width based on number of columns
        row_height = pdf.font_size

        # Add table header for the second DataFrame
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        for row in table_head2:
            for item in row:
                pdf.cell(col_width, row_height * spacing, txt=item, border=1, fill=True)
            pdf.ln(row_height * spacing)

        # Add table data for the second DataFrame
        pdf.set_font("Arial", size=8.5)
        pdf.set_text_color(0, 0, 0)
        for row in table_values2:
            for item in row:
                pdf.cell(col_width, row_height * spacing, txt=str(item), border=1)
            pdf.ln(row_height * spacing)


        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        pdf.output('./documents/'+types+'_MSC_Sox_all_year.pdf','F')
    
    simple_table()
    return FileResponse(path = './documents/'+types+'_MSC_Sox_all_year.pdf',filename='MSC_SOX.pdf')



@router.post('/api/v1/pdf/nox')
async def index(info : Request , tabname:str = None, selection:str = None ,vessel_name:str = None , method:str = None , start_date:str = None, end_date:str = None,year:str = None,fleet:str =None , types: str = None,vsl:str = None):
    s = await info.json()
    print(s)

    if tabname == 'All':

        if types == '0':
            types = 'MSC SM Vessels'
        elif types == '7':
            types = 'Charter Vessels'
        elif types == '8':
            types = 'Sorrento Vessels'
    else:
        pass
    data1 = pd.DataFrame.from_dict(s['data']['ae_me']['daily_data_me_ae'])

    data1 = data1.replace([0], np.nan)
    data1["corrected_date"]= pd.to_datetime(data1["date_month"], format='%d %b %Y')

    pivoted_data1 = data1.pivot(index='date_month',columns='category',values='nox_value').reset_index()
    lst = data1['date_month'].unique().tolist()
    pivoted_data1 = pivoted_data1.set_index('date_month')
    pivoted_data1 = pivoted_data1.loc[lst]   
    pivoted_data1 = pivoted_data1.reset_index()


    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    ax = pivoted_data1.plot(x='date_month', kind='bar', stacked=True,figsize=(60,20))

    ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))
    plt.xticks(rotation=45, ha='right',fontsize=35)
    plt.yticks(fontsize=35)
    plt.xlabel('Date',fontweight="bold",size=44)
    plt.ylabel('Total NOx Daily (MT)',fontweight="bold",size=44)
    ax.legend(title=None,fontsize=35)
    plt.savefig('./images/nox_vessel_date_meae_daily.png', bbox_inches="tight")
    plt.clf()
    data2 = pd.DataFrame.from_dict(s['data']['ae_me']['monthly_data_me_ae'])
    data2 = data2.replace([0], np.nan)
    pivoted_data2 = data2.pivot(index='date_month',columns='category',values='nox_value').reset_index()
    pivoted_data2['month_number'] = pivoted_data2['date_month'].apply(lambda x: datetime.strptime(x, "%Y-%B").month)
    pivoted_data2['year'] = pivoted_data2['date_month'].apply(lambda x: datetime.strptime(x, "%Y-%B").year)
    pivoted_data2 = pivoted_data2.sort_values(by=['year','month_number'])
    pivoted_data2 = pivoted_data2.drop(['year','month_number'],axis=1)



    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    ax = pivoted_data2.plot(x='date_month', kind='bar', stacked=True,figsize=(20,10))
    plt.xlabel('Date',fontweight="bold",size=15)
    plt.ylabel('Total NOx Monthly (MT)',fontweight="bold",size=15)
    plt.xticks(rotation=45, ha='right',fontsize=13)
    plt.yticks(fontsize=13)
    ax.legend(title=None,fontsize=15)
    plt.savefig('./images/nox_vessel_date_meae_monthly.png', bbox_inches="tight")
    plt.clf()

    data3 = pd.DataFrame.from_dict(s['data']['ae_me']['daily_data_ae'])
    data3 = data3.replace([0], np.nan)
    data3 = data3[(data3['category']=='AE 1') | (data3['category']=='AE 2')| (data3['category']=='AE 3')| (data3['category']=='AE 4')|(data3['category']=='AE 5')]
    pivoted_data3 = data3.pivot(index='date_month',columns='category',values='ae_nox_value').reset_index()
    lst = data3['date_month'].unique().tolist()
    pivoted_data3 = pivoted_data3.set_index('date_month')
    pivoted_data3 = pivoted_data3.loc[lst] 
    pivoted_data3 = pivoted_data3.reset_index()

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    ax = pivoted_data3.plot(x='date_month', kind='bar', stacked=True,figsize=(50,20))
    ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))
    plt.xticks(rotation=45, ha='right',fontsize=33)
    plt.yticks(fontsize=33)
    plt.xlabel('Date',fontweight="bold",size=44)
    plt.ylabel('Total NOx Daily (MT)',fontweight="bold",size=44)
    ax.legend(title=None,fontsize=35)
    plt.savefig('./images/nox_vessel_date_ae_daily.png', bbox_inches="tight")
    plt.clf()

    data4 = pd.DataFrame.from_dict(s['data']['ae_me']['monthly_data_ae'])
    data4 = data4.replace([0], np.nan)
    pivoted_data4 = data4.pivot(index='date_month',columns='category',values='ae_nox_value').reset_index()
    pivoted_data4['month_number'] = pivoted_data4['date_month'].apply(lambda x: datetime.strptime(x, "%Y-%B").month)
    pivoted_data4['year'] = pivoted_data4['date_month'].apply(lambda x: datetime.strptime(x, "%Y-%B").year)


    pivoted_data4 = pivoted_data4.sort_values(by=['year','month_number'])
    pivoted_data4 = pivoted_data4.drop(['year','month_number'],axis=1)


    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    ax = pivoted_data4.plot(x='date_month', kind='bar', stacked=True,figsize=(20,10))
    plt.xticks(rotation=45, ha='right',fontsize=13)
    plt.yticks(fontsize=13)
    plt.xlabel('Date',fontweight="bold",size=15)
    plt.ylabel('Total NOx Monthly (MT)',fontweight="bold",size=15)
    ax.legend(title=None,fontsize=15)
    plt.savefig('./images/nox_vessel_date_ae_monthly.png', bbox_inches="tight")
    plt.clf()





    # url="http://192.168.54.16:5200/api/v1/nox/emission/9625970"
    # p=requests.get(url , headers =  headers).json()

    if s['data']['emission']['data']:
    # Create the DataFrame
        data5 = pd.DataFrame.from_dict(s['data']['emission']['data'])

        # Verify the columns are present before selecting them
        expected_columns = ['vessel_name', 'nox_me_ev', 'nox_ae1_ev', 'nox_ae2_ev', 'nox_ae3_ev', 'nox_ae4_ev', 'nox_ae5_ev']
        missing_columns = [col for col in expected_columns if col not in data5.columns]

        if missing_columns:
            print(f"Missing columns: {missing_columns}")
        else:
            data5 = data5[expected_columns]
            data5.rename(columns = {
                'vessel_name':'Vessel Name',
                'nox_me_ev':'Main Engine',
                'nox_ae1_ev':'AE 1',
                'nox_ae2_ev':'AE 2',
                'nox_ae3_ev':'AE 3',
                'nox_ae4_ev':'AE 4',
                'nox_ae5_ev':'AE 5'
            }, inplace = True)
            data5 = data5.fillna('')
    else:
        data5 = pd.DataFrame()  

    # The rest of your code
    if s['data']['wise']['data']:
        # Access the first item in the list
        data_item = s['data']['wise']['data'][0]
        
        # Extract the latest, monthly, and yearly data
        latest_data = data_item['latest']
        monthly_data = data_item['monthly']
        yearly_data = data_item['yearly']
        
        # Create DataFrames from the extracted data
        data6 = pd.DataFrame.from_dict([latest_data])
        data6 = data6.transpose().reset_index()
        
        data7 = pd.DataFrame.from_dict([monthly_data])
        data7 = data7.transpose().reset_index()
        
        data8 = pd.DataFrame.from_dict([yearly_data])
        data8 = data8.transpose().reset_index()

        # Add monthly and yearly NOx data to the latest DataFrame
        data6['NOx this Month'] = data7[0]
        data6['NOx this Year'] = data8[0]
        
        # Rename columns for clarity
        data6.rename(columns={0: 'NOx latest', 'index': 'Name'}, inplace=True)

        latest_date = data6['NOx latest'].values[0]
        latest_month = data6['NOx this Month'].values[0]
        latest_year = data6['NOx this Year'].values[0]

        # Update column names with latest dates
        data6.rename(columns={
            'NOx latest': f'NOx latest {latest_date} (MT)',
            'NOx this Month': f'NOx this Month {latest_month} (MT)',
            'NOx this Year': f'NOx this Year {latest_year} (MT)'
        }, inplace=True)

        # Remove the first row if necessary
        data6 = data6.iloc[1:]

        # Replace names with more meaningful descriptions
        data6['Name'] = data6['Name'].replace({
            'me_total_nox_imo': 'Main Engine',
            'ae_total_nox_imo': 'AE Total',
            'ae1_nox_imo': 'AE 1',
            'ae2_nox_imo': 'AE 2',
            'ae3_nox_imo': 'AE 3',
            'ae4_nox_imo': 'AE 4',
            'ae5_nox_imo': 'AE 5'
        })

        # Set the order for the 'Name' column
        ordered_names = ['Main Engine', 'AE Total', 'AE 1', 'AE 2', 'AE 3', 'AE 4', 'AE 5']
        data6['Name'] = pd.Categorical(data6['Name'], categories=ordered_names, ordered=True)

        # Sort the DataFrame by the ordered 'Name' column and reset index
        data6 = data6.sort_values('Name').reset_index(drop=True)

        # Convert all values to string format
        data6 = data6.astype(str)





    def simple_table(spacing=3):
    
        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        
        pdf.image(msc_logo_path,160,8,w=30)

        pdf.set_xy(80,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 60, "NOx Report",ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)

        if  tabname=='Vessel':
            pdf.cell(10, 2, "Vessel :"+" "+vessel_name,ln=True)
        elif  tabname=='Fleet':
            pdf.cell(10, 2, "Fleet :"+" "+fleet,ln=True) 
        elif  tabname=='All':   
            pdf.cell(10, 2, "Type : "+" "+types,ln=True)  
        if selection == 'Year':
            pdf.cell(10, 12,"Monitoring period :  "+" "+ year,ln=True)
        else:
            pdf.cell(10, 12,"Monitoring period :  "+" "+ start_date+" "+"TO"+" "+end_date,ln=True)
        pdf.cell(10, 2, "Method :"+" "+method,ln=True)
        pdf.line(10, 75, 190, 75)

        pdf.set_xy(20,73)
        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'ME - AE Daily NOx',ln=True) 
        pdf.image("./images/nox_vessel_date_meae_daily.png",10,95,w=185,h=80)



        pdf.set_xy(20,185)
        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'ME - AE Monthly NOx',ln=True) 
        pdf.image("./images/nox_vessel_date_meae_monthly.png",10,195,w=185,h=80)

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 2 page **********************************************************#
        pdf.add_page()  

        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)

        pdf.set_xy(20,10)
        pdf.cell(180, 10, 'AE Daily NOx',ln=True) 
        pdf.image("./images/nox_vessel_date_ae_daily.png",10,25,w=185,h=80)
    

        pdf.set_xy(20,130)
        pdf.cell(180, 10, 'AE Monthly NOx',ln=True) 
        pdf.image("./images/nox_vessel_date_ae_monthly.png",10,145,w=185,h=80)


        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 3 page **********************************************************#
        if s['data']['wise']['data']:
        
            pdf.add_page()  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 10, ' ',ln=True)
            print("PDF4")
            pdf.cell(180, 10, 'IMO Method Data',ln=True)

            spacing=2
            tablefirst_head1 = [data6.columns.tolist()]
            tablefirst1 = data6.values.tolist()
            pdf.set_font("Arial",'B', size=8.5)
            col_width = pdf.w /4.5
            row_height = pdf.font_size
            for row in tablefirst_head1:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=8.5)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /4.5
            row_height = pdf.font_size
            for row in tablefirst1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)


            pdf.set_font("Arial",'B', size=15)
            pdf.cell(10,35," " ,ln=True)
            pdf.set_xy(10,80)
            pdf.set_text_color(25,47,133)
            
            pdf.cell(180, 10, 'NOx Values',ln=True)

            spacing=2
            tablefirst_head2 = [data5.columns.tolist()]
            tablefirst2 = data5.values.tolist()
            pdf.set_font("Arial",'B', size=6.2)
            col_width = pdf.w /9
            row_height = pdf.font_size
            for row in tablefirst_head2:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=6.2)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /9
            row_height = pdf.font_size
            for row in tablefirst2:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=str(item), border=1)
                pdf.ln(row_height*spacing)




            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        if vessel_name:
            print("===============================================")
            pdf_name = vessel_name + '_MSC_Nox.pdf'
        elif fleet:
            pdf_name = fleet + '_MSC_Nox.pdf'
        else:
            pdf_name = 'MSC_Nox.pdf'
            
           
        pdf.output('./documents/'+pdf_name,'F')
        
    if vessel_name:
        pdf_name = vessel_name + '_MSC_Nox.pdf'
    elif fleet:
        pdf_name = fleet + '_MSC_Nox.pdf'
    else:
        pdf_name = 'MSC_Nox.pdf'


    simple_table()
    print("======",pdf_name)
    return FileResponse(path = './documents/'+pdf_name,filename='MSC_NOX.pdf')
            



@router.post('/api/v1/pdf/eeoimrv/document')
def index():
    data = [
    {
      "__EMPTY": 1,
      "Type OF Fuel": "Diesel/gas oil",
      "Carbon Content": 0.875,
      "CF (t-CO2/t-Fuel)": 3.206,
      "References": "ISO 8217 Grades DMX through DMC"
    },
    {
      "__EMPTY": 2,
      "Type OF Fuel": "Light fuel oil(LFO)",
      "Carbon Content": 0.86,
      "CF (t-CO2/t-Fuel)": 3.151,
      "References": "ISO 8217 Grades RMA through RMD"
    },
    {
      "__EMPTY": 3,
      "Type OF Fuel": "Heavy fuel oil(HFO)",
      "Carbon Content": 0.85,
      "CF (t-CO2/t-Fuel)": 3.114,
      "References": "ISO 8217 Grades RME through RMK"
    },
    {
      "__EMPTY": 4,
      "Type OF Fuel": "Liquified Petroleum Gas(LPG)Propane",
      "Carbon Content": 0.819,
      "CF (t-CO2/t-Fuel)": 3
    },
    {
      "__EMPTY": 5,
      "Type OF Fuel": "Liquified Petroleum Gas(LPG)Butane",
      "Carbon Content": 0.827,
      "CF (t-CO2/t-Fuel)": 3.03
    },
    {
      "__EMPTY": 6,
      "Type OF Fuel": "Liquified Natural Gas(LNG)",
      "Carbon Content": 0.75,
      "CF (t-CO2/t-Fuel)": 2.75
    }
  ]

    Description = pd.DataFrame.from_dict(data)
    Description=Description.replace(np.nan,'-')
    Description = Description.astype(str)
    Description=Description[['Type OF Fuel', 'Carbon Content','CF (t-CO2/t-Fuel)', 'References']]


    from fpdf import FPDF
    def simple_table(spacing=3):

        pdf = FPDF()
        pdf.add_page()
        
        #Page Number
        pdf.set_y(265)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")
        
        
        pdf.set_font('Arial', 'B', 18)

        #Logo
        
        pdf.image(msc_logo_path,160,12,w=30)
    
    #Cell postion from left side
        pdf.set_xy(82,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(170, 73, 'DESCRIPTION',ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 55, 199, 55)#(x_start, y_start, x_end, y_end)
        pdf.set_line_width(0)
        
        pdf.set_font('Arial', "B",14)
        pdf.set_xy(10,30)
        pdf.set_text_color(0,0,0)    
        pdf.cell(170, 73, 'FLOW CHART FOR ENERGY EFFICIENCY CALCULATIONS',ln=True)
        
        #Flow Chart Graph
        pdf.image("./images/others/eeoi_mrv_flowchart.png",20.2,80,w=170,h=150)
        
        #Page 2
        pdf.add_page()

        #General Info
        pdf.set_xy(10,10)
        pdf.set_text_color(0,0,0)
        pdf.cell(170, 73, 'GENERAL INFO',ln=True)

        #ECA Zones and non-ECA Zones
        pdf.set_font('Arial', "B",12)
        pdf.set_xy(10,26)
        pdf.cell(170, 73, 'ECA Zones and non-ECA Zones',ln=True)
        
        pdf.set_font('Arial', "",10)
        pdf.set_xy(10,68)
        pdf.multi_cell(185, 6,  'The fuel consumption data for each vessel is collected for both ECA zones and non-ECA zones. ECA zone or Emission Control Zones are sea areas in which stricter controls were established to minimize airborne emissions (SOx, NOx, Ozone depleting substances, Volatile organic compounds) from ships.',align='L')

        
        #Fuel consumption equivalent
        pdf.set_font('Arial', "B",12)
        pdf.set_xy(10,56)
        pdf.cell(170, 73, 'Fuel consumption equivalent',ln=True)
        
        pdf.set_font('Arial', "",10)
        pdf.set_xy(10,98)
        pdf.multi_cell(185, 6,  'Fuel HS equivalent is the equivalent fuel (tonnes) in terms of HS fuel after converting the other types of fuel used (LS, MDO, MGO, MGO LS) by using conversion factors.',align='L')

        #Fuel mass to CO2 mass conversion factor (CF, in Tonne-CO2/Tonne-Fuel)
        pdf.set_font('Arial', "B",12)
        pdf.set_xy(10,80)
        pdf.cell(170, 73, 'Fuel mass to CO2 mass conversion factor (CF, in Tonne-CO2/Tonne-Fuel)',ln=True)
        
        pdf.set_font('Arial', "",10)
        pdf.set_xy(10,122)
        pdf.multi_cell(185, 6,  'CF is a non-dimensional conversion factor between fuel consumption measured in tonnes and CO2 emission also measured in tonnes based on carbon content. CO2 in tonnes can be calculated by multiplying CF with the respective fuel consumption.',align='L')

        #Transportation work
        pdf.set_font('Arial', "B",12)
        pdf.set_xy(10,110)
        pdf.cell(170, 73, 'Transportation work',ln=True)
        
        pdf.set_font('Arial', "",10)
        pdf.set_xy(10,152)
        pdf.multi_cell(185, 6,  'Transportation work based on Tonne- miles is the product of cargo per voyage in tonnes and the distance travelled in miles per voyage. Transportation work based on TEU- miles is the product of cargo per voyage in tonnes and the distance travelled in miles per voyage. The total transportation work is the sum of transportation work of all the voyages.',align='L')

        #EEOI/MRV Calculations
        pdf.set_font('Arial', "B",12)
        pdf.set_xy(10,146)
        pdf.cell(170, 73, 'EEOI/MRV Calculations',ln=True)
        
        pdf.set_font('Arial', "",10)
        pdf.set_xy(10,188)
        pdf.multi_cell(185, 6,  'For each voyage the energy efficiency is calculated. For the calculation of energy efficiency, the following formula is used.',align='L')
        
        pdf.image("./images/others/eeoi_mrv_equation.png",10,209,w=130,h=30)
    
        pdf.set_xy(10,250)
        pdf.multi_cell(185, 6,  'Here CF is the factor used for the conversion of the fuel mass to equivalent carbon content. This varies from fuel types. This index may be in terms of gram CO2/Tonne-mile or gram CO2/TEU-mile, based on the data used for calculations.',align='L')
        
        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(266)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R") 
        
        #New Page
        pdf.add_page()
        pdf.set_font('Arial', "B",12)  
        pdf.set_xy(10,20)
        pdf.multi_cell(185, 6,  'Generally Used Values',align='L')

        
        #Types of Fuel Table
        pdf.set_xy(10,30)
        Table_1_head=[['Type OF Fuel', 'Carbon Content','CF (t-CO2/t-Fuel)', 'References']]
        Table_1=Description.values.tolist()
        pdf.set_font("Arial","B", size=8)
        col_width = pdf.w / 4.4
        row_height = pdf.font_size
        
        for row in Table_1_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial","", size=7.5)
        pdf.set_text_color(0,0,0)
        for row in Table_1:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)

            
            
        #Ref:- MEPC.1/Circ.684
        pdf.set_font('Arial', "",10)
        pdf.set_xy(10,67)
        pdf.cell(170, 73, 'Ref:- MEPC.1/Circ.684',ln=True)
        
        pdf.set_font('Arial', "I",9)
        pdf.set_xy(10,109)
        pdf.multi_cell(185, 6,  'The methodology used in the calculation of energy efficiency in MRV is similar to that of EEOI but the only difference is that in MRV the data relating to the "IN PORT" condition is not taken',align='L')
    
        #EEOI/MRV Calculations
        pdf.set_font('Arial', "B",12)
        pdf.set_xy(10,91)
        pdf.cell(170, 73, 'EEOI/MRV Calculations',ln=True)
        
        pdf.set_font('Arial', "",10)
        pdf.set_xy(10,132)
        pdf.multi_cell(185, 6,  'For each voyage the energy efficiency is calculated. For the calculation of energy efficiency, the following formula is used.',align='L')

            
        
        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(266)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")
        
        pdf.output('./documents/MSC EEOI_MRV Description.pdf','F')

    simple_table()

    return FileResponse(path = './documents/MSC EEOI_MRV Description.pdf',filename='MSC EEOI_MRV Description.pdf')


    

@router.post('/api/v1/pdf/environmental/ciianalysis')
async def index( info : Request , tab_name : str = None, report_type : str = None ,year: str = None  ,start_date: str = None ,end_date: str = None ,period_comparison : bool = None, selection : str = None , vessel_name: str = None):

    s = await info.json()

    if tab_name == 'CII Daily Analysis':
        
        if report_type == 'Year':
        
            #inputs
            # vessel_name = 'MSC ANS'
            # year = '2022'

            # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6IjkyMzdhYWI2LWNjODctNDYxNC05ZTI2LWNhYzVhYzFkOWRhNSIsImlhdCI6MTY3MTQyOTI5OCwiZXhwIjoxNjcxNTE1Njk4fQ.nUINy_6tAZLYaJvc5ZH6FI6yxEbNnYSJCdYJr0kHjq0"
            # headers = {'Authorization': "Bearer {}".format(token)}
            # url="http://192.168.54.70:9885/api/v1/cii/year/8512906?year=2021"
            # s=requests.get(url , headers =  headers).json()

            data1 = pd.DataFrame.from_dict(s['data']['daily_chart'])
            cl_map = {'A':'green','B':'lightgreen','C':'yellow','D':'orange','E':'red',None : 'white'}
            data1['color_col'] = data1['cii_rating'].map(cl_map)
            #data1 = data1.sort_values(by=['day_no'])
            data3 = pd.DataFrame.from_dict(s['data']['table_data_1'])
            table_data=data3[['date','total_fuel','total_co2','miles_by_gps','cii_rating','required_cii','attained_cii','current_cii']]

            dict_date = pd.Series(data3['required_cii'].values,index=data3['date']).to_dict()
            data1['required_cii'] = np.nan
            data1['required_cii'] = data1['required_cii'].fillna(data1['date'].apply(lambda x: dict_date.get(x)))

            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            fig, ax = plt.subplots()
            data1.plot(x="date", y="current_cii", kind="line", ax=ax,color='cyan',figsize=(40,15))
            data1.plot(x="date", y="required_cii", kind="line", linestyle='dotted', ax=ax,color='blue',figsize=(40,15))
            data1.plot(x="date", y="attained_cii", kind="bar", ax=ax,color=data1['color_col'],label='')
            for container in ax.containers:
                ax.bar_label(container,size=8)
            #for legends
            for i, j in cl_map.items():
                ax.bar(data1['date'], data1['attained_cii'],width=0,color=j,label=i) 
            ax.legend()
            plt.xlabel('Date',fontweight="bold",size=20)
            plt.ylabel('CII',fontweight="bold",size=20)
            ax.xaxis.set_major_locator(md.WeekdayLocator(interval=1))
            plt.xticks(rotation=45, ha='right')
            plt.title('CII Daily Trend', size=25,fontweight="bold")
            ax.legend(title=None)
            plt.savefig('./images/msc_environment_cii_year.png')
            plt.clf()
            from fpdf import FPDF

            pdf = FPDF()
            #************* 1 page ***********#
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)
            # pdf.image(oceanix_logo_path,15,15,w=35)
            pdf.image(msc_logo_path,160,8,w=30)
            pdf.set_xy(58,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 60, "CII Daily Trend Report",ln=True)
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 190, 50)#(x_start, y_start, x_end, y_end)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",12)
            pdf.set_xy(10,55)
        
            pdf.cell(10, 2, "Vessel :"+" "+vessel_name,ln=True)
            pdf.cell(10, 12,"Year :  "+" "+ year,ln=True)
            pdf.line(10, 70, 190, 70)
            pdf.set_xy(20,80)
            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 10, 'CII Daily Trend',ln=True) 
            pdf.image("./images/msc_environment_cii_year.png",1,90,w=210,h=100)
            #Page Number
            pdf.set_text_color(0,0,0)
            #table
            pdf.set_xy(20,200)
            spacing=3
            fo_cnsptn_details_head = [['Date','Total Fuel','Total Co2','Distance','CII Rating','Required CII','Attained CII','Current CII' ]]
            table_data = table_data.values.tolist()
            pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
            pdf.set_font('Arial', 'B',size=6)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /10
            row_height = pdf.font_size
            for row in fo_cnsptn_details_head:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)


            pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
            pdf.set_font('Arial', '',size= 6)
            pdf.set_x(20)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /10
            pdf.set_x(20)
            row_height = (pdf.font_size)+.2
            for row in table_data:
                for item in row:
                    pdf.cell(col_width, row_height*spacing, txt=str(item), border=1)
                pdf.ln(row_height*spacing)
                pdf.set_x(20)

            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
            pdf.output('./documents/'+vessel_name+'_MSC_Environment_montoring_cii_year.pdf','F')
       

            return FileResponse(path = './documents/'+vessel_name+'_MSC_Environment_montoring_cii_year.pdf',filename='CI_Daily.pdf')


                
        elif report_type == 'Date':
            
            #inputs
            # vessel_name = 'MSC ANS'
            # start_date = '2021-01-01'
            # end_date = '2021-12-31'
            
            # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6IjkyMzdhYWI2LWNjODctNDYxNC05ZTI2LWNhYzVhYzFkOWRhNSIsImlhdCI6MTY3MTQyOTI5OCwiZXhwIjoxNjcxNTE1Njk4fQ.nUINy_6tAZLYaJvc5ZH6FI6yxEbNnYSJCdYJr0kHjq0"
            # headers = {'Authorization': "Bearer {}".format(token)}
            # url="http://192.168.54.70:9575/api/v1/cii/date/8509387?mindate=2021-01-01&maxdate=2021-12-31"
            # f=requests.get(url , headers =  headers).json()
            
            data2 = pd.DataFrame.from_dict(s['data']['daily_chart'])
            
            cl_map = {'A':'green','B':'lightgreen','C':'yellow','D':'orange','E':'red',None : 'white'}
            data2['color_col'] = data2['cii_rating'].map(cl_map)
            #data2 = data2.sort_values(by=['day_no'])
            data3 = pd.DataFrame.from_dict(s['data']['table_data_1'])
            table_data=data3[['date','total_fuel','total_co2','miles_by_gps','cii_rating','required_cii','attained_cii','current_cii']]
            dict_date = pd.Series(data3['required_cii'].values,index=data3['date']).to_dict()
            data2['required_cii'] = np.nan
            data2['required_cii'] = data2['required_cii'].fillna(data2['date'].apply(lambda x: dict_date.get(x)))

            
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            fig, ax = plt.subplots()
            data2.plot(x="date", y="current_cii", kind="line", ax=ax,color='cyan',figsize=(40,15))
            data2.plot(x="date", y="required_cii", kind="line", linestyle='dotted', ax=ax,color='blue',figsize=(80,15))
            data2.plot(x="date", y="attained_cii", kind="bar", ax=ax,color=data2['color_col'],label='')
            for container in ax.containers:
                ax.bar_label(container,size=9,fmt='%.1f')
            #for legends
            for i, j in cl_map.items():
                ax.bar(data2['date'], data2['attained_cii'],width=0,color=j,label=i) 
            ax.xaxis.set_major_locator(md.WeekdayLocator(interval=1))
            ax.legend()
            plt.xlabel('Date',fontweight="bold",size=50)
            plt.ylabel('CII',fontweight="bold",size=50)
            plt.title('CII Daily Trend', size=55,fontweight="bold")
            plt.xticks(rotation=45, ha='right')
            ax.legend(title=None)
            max_attained_cii = data2['attained_cii'].max()
            ax.set_ylim(0, max_attained_cii + 10)
            plt.savefig('./images/msc_environment_cii_date.png')
            plt.clf()
            
            from fpdf import FPDF


            pdf = FPDF()
            #***************** 1 page ******************#
            pdf.add_page(orientation='L')
            pdf.set_font('Arial', 'B', 18)

            # pdf.image(oceanix_logo_path,15,15,w=35)
            pdf.image(msc_logo_path,250,8,w=30)

            pdf.set_xy(110,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 60, "CII Daily Trend Report",ln=True)
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 285, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",12)
            pdf.set_xy(10,55)
            
            pdf.cell(10, 2, "Vessel :"+" "+vessel_name,ln=True)
            pdf.cell(10, 12,"Monitoring period :  "+" "+ start_date+" "+"TO"+" "+end_date,ln=True)
            pdf.line(10, 70, 285, 70)

            pdf.set_xy(20,80)
            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 10, 'CII Daily Trend',ln=True) 
            pdf.image("./images/msc_environment_cii_date.png",1,90,w=310,h=100)
            pdf.set_y(187)
            #Page Number
            pdf.set_text_color(0,0,0)
            #table
            pdf.set_xy(20,200)
            spacing=3
            fo_cnsptn_details_head = [['Date','Total Fuel','Total Co2','Distance','CII Rating','Required CII','Attained CII','Current CII' ]]
            table_data = table_data.values.tolist()
            pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
            pdf.set_font('Arial', 'B',size=6)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /10
            row_height = pdf.font_size
            for row in fo_cnsptn_details_head:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)


            pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
            pdf.set_font('Arial', '',size= 6)
            pdf.set_x(20)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /10
            pdf.set_x(20)
            row_height = (pdf.font_size)+.2
            for row in table_data:
                for item in row:
                    pdf.cell(col_width, row_height*spacing, txt=str(item), border=1)
                pdf.ln(row_height*spacing)
                pdf.set_x(20)

            pdf.set_y(187)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


            pdf.output('./documents/'+vessel_name+'_MSC_Environment_montoring_cii_date.pdf','F')


            return FileResponse(path = './documents/'+vessel_name+'_MSC_Environment_montoring_cii_date.pdf',filename='CI_Daily.pdf')

                
                
    elif tab_name == 'CII Weekly Analysis':
        
        #inputs
        # vessel = 'MSC ANS'
        # year = '2022'
        
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6IjkyMzdhYWI2LWNjODctNDYxNC05ZTI2LWNhYzVhYzFkOWRhNSIsImlhdCI6MTY3MTQyOTI5OCwiZXhwIjoxNjcxNTE1Njk4fQ.nUINy_6tAZLYaJvc5ZH6FI6yxEbNnYSJCdYJr0kHjq0"
        # headers = {'Authorization': "Bearer {}".format(token)}
        # url="http://192.168.54.70:9575/api/v1/cii/weekly/9282261?year=2021"
        # g=requests.get(url , headers =  headers).json()
        
        data3 = pd.DataFrame.from_dict(s['data']['chart_data'])
        data3['attained_cii'] = data3['attained_cii'].astype('float64')

        cl_map = {'A':'green','B':'lightgreen','C':'yellow','D':'orange','E':'red',None : 'white'}
        data3['color_col'] = data3['attained_rating'].map(cl_map)
        
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        fig, ax = plt.subplots()
        data3.plot(x="week_number", y="current_cii", kind="line", ax=ax,color='cyan',figsize=(30,10))
        data3.plot(x="week_number", y="required_cii", kind="line", linestyle='dotted', ax=ax,color='blue',figsize=(30,15))
        data3['color_col'].fillna('gray', inplace=True)
        data3.plot(x="week_number", y="attained_cii", kind="bar", ax=ax,color=data3['color_col'],label='')
        for container in ax.containers:
            ax.bar_label(container,size=8)
        #for legends
        for i, j in cl_map.items():
            ax.bar(data3['week_number'], data3['attained_cii'],width=0,color=j,label=i) 

        ax.legend()
        def change_width(ax, new_value) :
            for patch in ax.patches :
                current_width = patch.get_width()
                diff = current_width - new_value

                # we change the bar width
                patch.set_width(new_value)

                # we recenter the bar
                patch.set_x(patch.get_x() + diff * .5)    
        plt.xlabel('Week number',fontweight="bold",size=20)
        plt.ylabel('Attained CII',fontweight="bold",size=20)
        plt.title('CII Weekly Trend',size=25,fontweight="bold")
        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_environment_cii_week.png')
        plt.clf()
        
        value_counts = data3[data3['attained_rating'] != 0]['attained_rating'].value_counts().reset_index()
        value_counts.columns = ['attained_rating', 'count']
        value_counts = value_counts[~(value_counts['attained_rating'].isnull() | (value_counts['attained_rating'] == ''))]
        value_counts['color_col'] = value_counts['attained_rating'].map(cl_map)

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = ['green','lightgreen','yellow','orange','red']
        ax.pie(value_counts['count'],labels = value_counts["attained_rating"], autopct='%.1f%%', colors=value_counts['color_col'])
        ax.set_title('CII Weekly Trend',size=15,fontweight="bold")
        plt.tight_layout()
        plt.savefig('./images/msc_environment_cii_week_piechart.png')
        plt.clf()
        
        from fpdf import FPDF

        pdf = FPDF()
        #**************** 1 page *******************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        # pdf.image(oceanix_logo_path,15,15,w=35)
        pdf.image(msc_logo_path,160,8,w=30)

        pdf.set_xy(58,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 60, "CII Weekly Trend Report",ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)
        pdf.cell(10, 2, "Vessel :"+" "+vessel_name,ln=True)
        if year:
            if year != 'null':
                pdf.cell(10, 12, "Year: " + " " + year, ln=True)
                pdf.line(10, 70, 190, 70)
            else:
                pdf.multi_cell(0, 12, "Starting Date: " + start_date)
                pdf.multi_cell(0, 3, "Ending Date : " + end_date)
                pdf.line(10, 75, 190, 75)
            
        else:
            pdf.multi_cell(0, 12, "Starting Date: " + start_date)
            pdf.multi_cell(0, 3, "Ending Date : " + end_date)
            pdf.line(10, 75, 190, 75)

        pdf.set_xy(20,80)
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'CII Weekly Trend',ln=True) 
        pdf.image("./images/msc_environment_cii_week.png",1,90,w=210,h=100)

        pdf.set_xy(40,200) 
        pdf.image("./images/msc_environment_cii_week_piechart.png",70,200,w=80,h=80)

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


        pdf.output('./documents/'+vessel_name+'_MSC_Environment_montoring_cii_week.pdf','F')



        return FileResponse(path = './documents/'+vessel_name+'_MSC_Environment_montoring_cii_week.pdf',filename='CI_Weekly.pdf')


@router.post('/api/v1/pdf/datamonitoring/loaddia/{imo}')
async def index( info : Request , method : str = None, period_start : str = None ,period_end: str = None  ,period_comp_start: str = None ,period_comp_end: str = None ,period_comparison : bool = None, selection : str = None , vessel_name: str = None,imo:str = None,mcr_value:float = None,types:str = None,class_name:str = None,mcr_power:str = None,new_mcr_power:str = None,mcr_rpm:str = None,new_mcr_rpm:str = None,vdm_db:AsyncSession=Depends(get_vdm_db_async)):
    colorPallet=await vessel_color(vdm_db)
    if mcr_power == 'null':
        mcr_power = None
    if new_mcr_power == 'null':
        new_mcr_power = None
    if mcr_rpm == 'null':
        mcr_rpm = None
    if new_mcr_rpm == 'null':
        new_mcr_rpm = None
    s = await info.json()
    

    imo_lst = list(s['data']['data'].keys())  # List of 'imo' values
    legend_labels = []  # Empty list to store legend labels
    required_curve_columns = ['shaft_speed', 'pover_load', 'p_continuous', 'max_speed', 'prop_curve_s', 'prop_curve_l', 'prop_curve_bp']

    if types != 'both':
        if method == 'vessel':
            fig, ax = plt.subplots(figsize=(12, 9))
            for j, imo in enumerate(imo_lst):
                data_scatter = pd.DataFrame(s["data"]["data"][imo])
                data_curve = pd.DataFrame(s['data']['LoadDiagramData'])
                if all(col in data_curve.columns for col in required_curve_columns):
                    data_curve = data_curve[required_curve_columns].astype(float)
                    data_curve = data_curve.sort_values(by='shaft_speed')
                    data_curve = data_curve.replace([''], np.nan)
                    data_curve = data_curve.dropna(how='all')

                    if types == 'vrs':
                        data_scatter = data_scatter[['type', 'vessel_name', 'imo', 'rpm', 'power_kw', 'me_load', 'rpm_loaddia']]
                        data_scatter_vrs = data_scatter[data_scatter['type'] == 'VRS Data']
                        ax.scatter(data_scatter_vrs['rpm_loaddia'], data_scatter_vrs['me_load'], color='green', label='VRS Data')

                    elif types == 'egoship':
                        data_scatter = data_scatter[['type', 'vessel_name', 'imo', 'rpm', 'power_kw', 'me_load', 'rpm_loaddia']]
                        data_scatter_ada = data_scatter[data_scatter['type'] == 'ADA Data']
                        ax.scatter(data_scatter_ada['rpm_loaddia'], data_scatter_ada['me_load'], color='red', label='ADA Data')

                        new_curve = s['data']['LoadDiagramData']
                        if new_curve:
                            x_value = new_curve[0].get('x', None)
                            y_value = new_curve[0].get('y', None)
                            if x_value is not None and y_value is not None:
                                ax.scatter([x_value], [y_value], color='yellow', label='New RPM and Power')

                    # Plot the curves
                    ax.plot(data_curve['shaft_speed'], data_curve['pover_load'], label='P Overload')
                    ax.plot(data_curve['shaft_speed'], data_curve['p_continuous'], label='P Continuous')
                    ax.plot(data_curve['max_speed'], data_curve['pover_load'], label='Max Speed')
                    ax.plot(data_curve['shaft_speed'], data_curve['prop_curve_s'], label='Prop Curve S')
                    ax.plot(data_curve['shaft_speed'], data_curve['prop_curve_l'], label='Prop Curve L')
                    ax.plot(data_curve['shaft_speed'], data_curve['prop_curve_bp'], label='Prop Curve BP')

                    ax.legend(loc='upper right')
                    ax.set_xlabel('RPM (%)')
                    ax.set_ylabel('Power (kW%)')
                    plt.savefig('./images/data_monitoring_load_diagram_vessel.png', bbox_inches='tight')

        elif method == 'class':
             for ld_key, imos in s['data']['LoadDiagramData']['plot_points_imos_list'].items():
                fig, ax = plt.subplots(figsize=(12, 9))
                legend_labels = set()
                for imo in imos:
                    if imo in imo_lst:
                        data_scatter = pd.DataFrame(s["data"]["data"][imo])
                        data_curve = pd.DataFrame(s['data']['LoadDiagramData']['chart_data'][ld_key])
                        if all(col in data_curve.columns for col in required_curve_columns):
                            data_curve = data_curve[required_curve_columns].astype(float)
                            data_curve = data_curve.sort_values(by='shaft_speed')
                            data_curve = data_curve.replace([''], np.nan)
                            data_curve = data_curve.dropna(how='all')

                            curves = {
                                'Power Over Load': ('shaft_speed', 'pover_load', 'red'),
                                'Continuous Power': ('shaft_speed', 'p_continuous', '#2f7dad'),
                                'Max Speed': ('max_speed', 'pover_load', '#36dbe0'),
                                'Prop Curve S': ('shaft_speed', 'prop_curve_s', 'green'),
                                'Prop Curve L': ('shaft_speed', 'prop_curve_l', '#b036e0'),
                                'Prop Curve BP': ('shaft_speed', 'prop_curve_bp', '#54eb77')}
                            
                            for curve_name, (x_col, y_col, color) in curves.items():
                                if curve_name not in legend_labels:
                                    ax.plot(data_curve[x_col], data_curve[y_col], label=curve_name, color=color)
                                    legend_labels.add(curve_name) 
                                else:
                                    ax.plot(data_curve[x_col], data_curve[y_col], color=color)

                            

                        if not data_scatter.empty and 'vessel_name' in data_scatter.columns:
                            data_scatter = data_scatter[['type', 'vessel_name', 'imo', 'rpm', 'power_kw', 'me_load', 'rpm_loaddia']]
                            label = data_scatter['vessel_name'].values[0]
                            vessel_imo = data_scatter['imo'].tolist() 

                            print(colorPallet)

                            # Map colors to the corresponding 'imo' values
                            color = [colorPallet.get(imo, '#000000') for imo in vessel_imo]  # Default to black if no color found
                            scatter = ax.scatter(data_scatter['rpm_loaddia'], data_scatter['me_load'], color=color)
                            print('color:', color)

                            if label not in legend_labels:
                                legend_labels.add(label)
                                ax.scatter([], [], color=scatter.get_facecolor()[0], label=label)
                            else:
                                ax.scatter(data_scatter['rpm_loaddia'], data_scatter['me_load'], color=color)

                            new_curve = s['data']['LoadDiagramData'].get('chart_data', {}).get(ld_key, [])
                            if new_curve:
                                x_value = new_curve[0].get('x', None)
                                y_value = new_curve[0].get('y', None)
                                if x_value is not None and y_value is not None:
                                    ax.scatter([x_value], [y_value], color='yellow', label=f'New RPM and Power {ld_key}')


                        
                        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
                        ax.set_xlabel('RPM (%)')
                        ax.set_ylabel('Power (kW%)')
                        file_name = f'./images/data_monitoring_load_diagram_{ld_key}.png'
                        plt.savefig(file_name, bbox_inches='tight')

    elif types == 'both':
        if method == 'class':
            for ld_key, imos in s['data']['LoadDiagramData']['plot_points_imos_list'].items():
                fig, ax = plt.subplots(figsize=(12, 9))
                legend_labels = []  # Ensure legend_labels is reset for each plot
                for imo in imos:
                    if imo in imo_lst:
                        data_scatter_imo = pd.DataFrame(s["data"]['data'][imo])
                        if not data_scatter_imo.empty and 'vessel_name' in data_scatter_imo.columns:
                            data_scatter_imo = data_scatter_imo[['type', 'vessel_name', 'imo', 'rpm', 'power_kw', 'me_load', 'rpm_loaddia']]
                            data_scatter_vrs = data_scatter_imo[data_scatter_imo['type'] == 'VRS Data']
                            data_scatter_ada = data_scatter_imo[data_scatter_imo['type'] == 'ADA Data']

                            if f'{ld_key} VRS Data' not in legend_labels:
                                ax.scatter(data_scatter_vrs['rpm_loaddia'], data_scatter_vrs['me_load'], color='#43c72c', label='VRS Data')
                                legend_labels.append(f'{ld_key} VRS Data')
                            else:
                                ax.scatter(data_scatter_vrs['rpm_loaddia'], data_scatter_vrs['me_load'], color='#43c72c')

                            if f'{ld_key} ADA Data' not in legend_labels:
                                ax.scatter(data_scatter_ada['rpm_loaddia'], data_scatter_ada['me_load'], color='#ba1c41', label='ADA Data')
                                legend_labels.append(f'{ld_key} ADA Data')
                            else:
                                ax.scatter(data_scatter_ada['rpm_loaddia'], data_scatter_ada['me_load'], color='#ba1c41')

                new_curve = s['data']['LoadDiagramData'].get('chart_data', {}).get(ld_key, [])
                if new_curve:
                    x_value = new_curve[0].get('x', None)
                    y_value = new_curve[0].get('y', None)
                    if x_value is not None and y_value is not None:
                        ax.scatter([x_value], [y_value], color='yellow', label=f'New RPM and Power {ld_key}')

                data_curve = pd.DataFrame(s['data']['LoadDiagramData']['chart_data'][ld_key])
                if all(col in data_curve.columns for col in required_curve_columns):
                    data_curve = data_curve[required_curve_columns].astype(float)
                    data_curve = data_curve.sort_values(by='shaft_speed')
                    data_curve = data_curve.replace([''], np.nan)
                    data_curve = data_curve.dropna(how='all')

                    ax.plot(data_curve['shaft_speed'], data_curve['pover_load'], label='P Overload')
                    ax.plot(data_curve['shaft_speed'], data_curve['p_continuous'], label='P Continuous')
                    ax.plot(data_curve['max_speed'], data_curve['pover_load'], label='Max Speed')
                    ax.plot(data_curve['shaft_speed'], data_curve['prop_curve_s'], label='Prop Curve S')
                    ax.plot(data_curve['shaft_speed'], data_curve['prop_curve_l'], label='Prop Curve L')
                    ax.plot(data_curve['shaft_speed'], data_curve['prop_curve_bp'], label='Prop Curve BP')

                ax.legend(loc='upper right')
                ax.set_xlabel('RPM (%)')
                ax.set_ylabel('Power (kW%)')
                file_name = f'./images/data_monitoring_load_diagram_{ld_key}.png'
                plt.savefig(file_name, bbox_inches='tight')
                

        elif method == 'vessel':
            fig, ax = plt.subplots(figsize=(12, 9))
            dataframes_list = []
            for imo in imo_lst:
                dataframes_list.append(pd.DataFrame(s["data"]['data'][imo]))

            data_scatter = pd.concat(dataframes_list, ignore_index=True)
            data_scatter_vrs = data_scatter[data_scatter['type'] == 'VRS Data']
            ax.scatter(data_scatter_vrs['rpm_loaddia'], data_scatter_vrs['me_load'], color='green', label='VRS Data')

            data_scatter_ada = data_scatter[data_scatter['type'] == 'ADA Data']
            ax.scatter(data_scatter_ada['rpm_loaddia'], data_scatter_ada['me_load'], color='red', label='ADA Data')

            new_curve = s['data']['LoadDiagramData']
            if new_curve:
                x_value = new_curve[0].get('x', None)
                y_value = new_curve[0].get('y', None)
                if x_value is not None and y_value is not None:
                    ax.scatter([x_value], [y_value], color='yellow', label='New RPM and Power')

            data_curve = pd.DataFrame(s['data']['LoadDiagramData'])
            if all(col in data_curve.columns for col in required_curve_columns):
                data_curve = data_curve[required_curve_columns].astype(float)
                data_curve = data_curve.sort_values(by='shaft_speed')
                data_curve = data_curve.replace([''], np.nan)
                data_curve = data_curve.dropna(how='all')

                ax.plot(data_curve['shaft_speed'], data_curve['pover_load'], label='P Overload')
                ax.plot(data_curve['shaft_speed'], data_curve['p_continuous'], label='P Continuous')
                ax.plot(data_curve['max_speed'], data_curve['pover_load'], label='Max Speed')
                ax.plot(data_curve['shaft_speed'], data_curve['prop_curve_s'], label='Prop Curve S')
                ax.plot(data_curve['shaft_speed'], data_curve['prop_curve_l'], label='Prop Curve L')
                ax.plot(data_curve['shaft_speed'], data_curve['prop_curve_bp'], label='Prop Curve BP')

            ax.set_xlabel('RPM (%)')
            ax.set_ylabel('Power (kW%)')
            ax.legend(loc='upper right')
            plt.savefig('./images/data_monitoring_load_diagram_vessel.png', bbox_inches='tight')
            # plt.show()



    #PDF

    from fpdf import FPDF
    def simple_table(spacing=3):
 
        #report_prepared_date= "11-10-2022"
    
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        pdf.image(msc_logo_path,160,8,w=30)

        pdf.set_xy(10,20)
        pdf.set_text_color(25,47,133)
        #pdf.cell(80, 100, "Load Diagram Report",ln=True)
        pdf.multi_cell(0, 10, "Load Diagram Report", align="C")

        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 35, 199, 35)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,40)

        if method == 'class':
            pdf.cell(10, 3, "Class Name :"+" "+vessel_name,ln=True)
        else:
            pdf.cell(10, 3, "Vessel Name :"+" "+vessel_name,ln=True)

        pdf.cell(10, 11,"Monitoring Period :"+" "+ period_start + " " + "to" + " " + period_end,ln=True)
        pdf.line(10, 55, 199, 55)

        #pdf.set_x(10)
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)

        if method == 'class':
            # Debug: Print the length of plot_points_imos_list
            print(f"Total Load Diagrams: {len(s['data']['LoadDiagramData']['plot_points_imos_list'])}")

            for i, ld_key in enumerate(s['data']['LoadDiagramData']['plot_points_imos_list']):
                print(f"Adding Load Diagram for: {ld_key}")  # Debug: Print each key being processed
                if i != 0:
                    pdf.add_page()
                # Add the correct image based on the load diagram key
                file_name = f'./images/data_monitoring_load_diagram_{ld_key}.png'
                pdf.image(file_name, 20, 70, w=170, h=150)
        else:
            # Add a single image if the method is not 'class'
            pdf.image('./images/data_monitoring_load_diagram_vessel.png', 20, 70, w=170, h=150)

        if method != 'class':
            pdf.set_xy(20, 230)
            pdf.set_font("Arial", 'B', size=8)
            pdf.set_fill_color(21, 55, 188)
            pdf.set_text_color(255, 255, 255)

            if new_mcr_power is not None and new_mcr_rpm is not None:
                mcr_power_percent = round((float(new_mcr_power) * 100) / float(mcr_power), 2)
                mcr_rpm_percent = round((float(new_mcr_rpm) * 100) / float(mcr_rpm), 2)
                pdf.cell(0, 10, "              Engine Power Limited: (" + str(new_mcr_power) + " kw, " + str(mcr_power_percent) + "%) " + '                                                    '
                        "Engine RPM Limited: (" + str(new_mcr_rpm) + ", " + str(mcr_rpm_percent) + "%)", ln=True, border=1, fill=True)
            else:
                mcr_power_percent = 'null'
                mcr_rpm_percent = 'null'
                pdf.cell(0, 10, "Engine Power Limited: (" + str(new_mcr_power) + ", " + str(mcr_power_percent) + ") " +
                        "Engine RPM Limited: (" + str(new_mcr_rpm) + ", " + str(mcr_rpm_percent) + ")", ln=True, border=1, fill=True)

        
        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        pdf.output(file_path,'F')

    if method == 'class':
        file_path = './documents/'+vessel_name+'_data_monitoring_load_diagram.pdf'

    else:
        file_path = './documents/'+vessel_name+'_data_monitoring_load_diagram.pdf'
    simple_table()
    return FileResponse(path =file_path,filename='LoadDia.pdf')
    

@router.post('/api/v1/pdf/datamonitoring/sfoc')
async def index(info : Request ,vessel_name:str = None, period_start:str = None, period_end:str = None, period_comparison : bool = None , period_comp_start:str = None , period_comp_end:str = None , method:str = None):

    s = await info.json()
    print('vessel_nmae:',vessel_name.replace(" ", "").replace("-", "_"))
    # vessel_name = vessel_name.replace(" ", "").replace("-", "_")
    if method == 'vrs':
        method_type = 'VRS Data'
    elif method == 'egoship':
        method_type = 'ADA Data'
    else:
        method_type = 'both'
    
    # Handle data processing
    for i in s['data']['data']:
        a = i
    
    data1 = pd.DataFrame.from_dict(s['data']['data'][a])
    data2 = pd.DataFrame.from_dict(s['data']['shoptrialData'])
    data2['load'] = data2['load'].astype('float64')
    data2['sfoc'] = data2['sfoc'].astype('float64')
    data2['sfoc_corrected'] = data2['sfoc_corrected'].astype('float64')
    
    vrs_data = data1[data1['type'] == 'VRS Data']
    ada_data = data1[data1['type'] == 'ADA Data']
    
    # Plotting function
    def plot_sfoc_deviation(method_type, ax, period_comparison):
        vrs_color_sfoc = 'green'
        ada_color_sfoc = 'red'
        corrected_sfoc_color = 'red'
        # Plot based on method type
        if method_type == 'VRS Data':
            vrs_data.plot(x="me_load", y="sfoc", kind="scatter", ax=ax, color=vrs_color_sfoc, label='VRS Data')
        elif method_type == 'ADA Data':
            ada_data.plot(x="me_load", y="sfoc", kind="scatter", ax=ax, color=ada_color_sfoc, label='ADA Data')
        elif method_type == 'both':
            vrs_data.plot(x="me_load", y="sfoc", kind="scatter", ax=ax, color=vrs_color_sfoc, label='VRS Data')
            ada_data.plot(x="me_load", y="sfoc", kind="scatter", ax=ax, color=ada_color_sfoc, label='ADA Data')
        # Plot Corrected SFOC
        data2.plot(x="load", y="sfoc_corrected", kind="line", ax=ax, color=corrected_sfoc_color, label='Corrected SFOC', marker='o', markersize=5)
        data2.plot(x="load", y="sfoc", kind="line", ax=ax, color='green', label='SFOC', marker='o', markersize=5)

    # Generate plot and save it
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    fig, ax = plt.subplots(figsize=(15, 10))
    
    plot_sfoc_deviation(method_type, ax, period_comparison)
    
    # Set labels and title
    plt.xlabel('% LOAD', fontweight="bold", size=20)
    plt.ylabel('SFOC (g/kWhr)', fontweight="bold", size=20)
    #plt.title('SFOC Deviation', size=25, fontweight="bold")
    ax.set_ylim(0, 500)
    ax.legend()
    
    # Save the plot
    plt.savefig('./images/data_monotoring_sfoc_deviation_both.png')
    # plt.show()
    
    # PDF Report Generation
    def create_pdf_report(vessel_name, method_type, period_start, period_end, period_comp_start=None, period_comp_end=None):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)
    
        # PDF Title
        pdf.set_xy(58, 15)
        pdf.set_text_color(25, 47, 133)
        pdf.cell(180, 60, "SFOC Deviation Report", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)
    
        # Vessel details
        if period_comparison and period_comp_start and period_comp_end:
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "", 12)
            pdf.set_xy(10, 55)
            pdf.cell(10, 2, "Vessel Name: " + vessel_name, ln=True)
            pdf.cell(10, 12, "Monitoring Period: " + period_start + " to " + period_end, ln=True)
            pdf.cell(10, 2, "Comparison Period: " + period_comp_start + " to " + period_comp_end, ln=True)   
            pdf.cell(10, 11, "Type: " + method_type, ln=True)
            pdf.line(10, 80, 190, 80)
    
        else:
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "", 12)
            pdf.set_xy(10, 55)
            pdf.cell(10, 2, "Vessel Name: " + vessel_name, ln=True)
            pdf.cell(10, 12, "Monitoring Period: " + period_start + " to " + period_end, ln=True)
            pdf.cell(10, 3, "Type: " + method_type, ln=True)
            pdf.line(10, 75, 190, 75)
        
        # Plot image
        pdf.set_xy(70, 80)
        pdf.set_font("Arial", 'B', size=18)
        pdf.set_text_color(25, 47, 133)
        pdf.cell(80, 28, 'SFOC Deviation', ln=True)
        pdf.image("./images/data_monotoring_sfoc_deviation_both.png",1,95,w=200,h=120)    


        # Page Number
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 2, 'Page %s' % pdf.page_no(), align="R")
    
        pdf.output('./documents/'+vessel_name+'_datamonitoring_sfoc.pdf','F')
    
    # Handling different conditions for period comparison and method type
    if period_comparison:
        if method_type == 'VRS Data':
            create_pdf_report(vessel_name, 'VRS Data', period_start, period_end, period_comp_start, period_comp_end)
        elif method_type == 'ADA Data':
            create_pdf_report(vessel_name, 'ADA Data', period_start, period_end, period_comp_start, period_comp_end)
        elif method_type == 'both':
            create_pdf_report(vessel_name, 'VRS & ADA Data', period_start, period_end, period_comp_start, period_comp_end)
    else:
        if method_type == 'VRS Data':
            create_pdf_report(vessel_name, 'VRS Data', period_start, period_end)
        elif method_type == 'ADA Data':
            create_pdf_report(vessel_name, 'ADA Data', period_start, period_end)
        elif method_type == 'both':
            create_pdf_report(vessel_name, 'VRS & ADA Data', period_start, period_end)



    return FileResponse(path = './documents/'+vessel_name+'_datamonitoring_sfoc.pdf',filename='datamonitoring_sfoc.pdf')


@router.post('/api/v1/pdf/datamonitoring/operationalprofile')
async def index(info : Request  ,vessel_name: str = None, mindate: str = None , maxdate: str = None , report_type : str = None , group : str = None,types:str = None,class_name:str = None,teu:str = None,vdm_db:AsyncSession=Depends(get_vdm_db_async)):
    s = await info.json()
    print("sssss",s)
    colorPallet=await vessel_color(vdm_db)
    
    pdf_name = 'OperationProfile_'+str(vessel_name)
    mindate = datetime.strptime(mindate,'%Y-%m-%d').strftime('%d %b %Y')
    maxdate = datetime.strptime(maxdate,'%Y-%m-%d').strftime('%d %b %Y')
    # report_type = 'vessel'
    # types = 'draft' #input
    
    
    # period_start = mindate
    # period_end = maxdate
    
    # report_type = 'Single Vessel' or 'Class Vessel' or 'Multi Vessel' or 'TEU Group'
    
    #pdf_name = vessel_name + "_Data_Monitering_Opertion_Profile.pdf"
    
    if not s['data']:
        return  {'data':[],'Error':'No Data Found'}
    if report_type == 'vessel':
        #input parameters
        # period_start = '2021-01-01'
        # period_end = '2022-02-01'
    
    
        for i in s['data']:
            a = i
        vessel_imo = list(s['data'].keys())[0]
        color = colorPallet.get(vessel_imo, '#000000')
        data1 = pd.DataFrame.from_dict(s['data'][a][0]['sog'])
        data1['vesselname'] = data1['vesselname'].fillna(data1['vesselname'].mode()[0])
        data1 = data1[['range','value','vesselname']]
        data1 = data1.dropna()
        vessel = data1['vesselname'].values[0]
    
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=data1,palette=[color],hue='vesselname')
        plt.xlabel('Speed (kn)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        # plt.title('Speed (kn)', size=18,fontweight="bold")
        plt.bar_label(ax.containers[0],size=8,fmt='%.1f')
        ax.legend(title=None)
        plt.xticks(rotation=45)
    
        plt.savefig('./images/msc_operational_single_sog.png',bbox_inches='tight')
        
        vessel_imo = list(s['data'].keys())[0]
        color = colorPallet.get(vessel_imo, '#000000')
        data2 = pd.DataFrame.from_dict(s['data'][a][0]['draft'])
        data2['vesselname'] = data2['vesselname'].fillna(data2['vesselname'].mode()[0])
        data2 = data2[['range','value','vesselname']]
        data2 = data2.dropna()
    
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=data2,palette=[color],hue='vesselname')
        plt.xlabel('Draft (m)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        # plt.title('Draft (m)', size=18,fontweight="bold")
        plt.bar_label(ax.containers[0],size=8,fmt='%.1f')
        ax.legend(title=None)
        plt.xticks(rotation=45)
        plt.savefig('./images/msc_operational_single_draft.png',bbox_inches='tight')
    

        vessel_imo = list(s['data'].keys())[0]
        color = colorPallet.get(vessel_imo, '#000000')
        data3 = pd.DataFrame.from_dict(s['data'][a][0]['power'])
        data3['vesselname'] = data3['vesselname'].fillna(data3['vesselname'].mode()[0])
        data3 = data3[['range','value','vesselname']]
        data3 = data3.dropna()
    
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=data3,palette=[color],hue='vesselname')
        plt.xlabel('Power (kW)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        ax.xaxis.set_major_locator(MultipleLocator(2))
        # plt.title('Power (kW)', size=18,fontweight="bold")
        plt.bar_label(ax.containers[0],size=8,fmt='%.1f')
        ax.legend(title=None)
        plt.xticks(rotation=45)
        plt.savefig('./images/msc_operational_single_power.png',bbox_inches='tight')


        vessel_imo = list(s['data'].keys())[0]
        color = colorPallet.get(vessel_imo, '#000000')
        data4 = pd.DataFrame.from_dict(s['data'][a][0]['seastate'])
        data4['vesselname'] = data4['vesselname'].fillna(data4['vesselname'].mode()[0])
        data4 = data4[['range','value','vesselname']]
        data4 = data4.dropna()
    
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=data4,palette=[color],hue='vesselname')
        plt.xlabel('SeaState',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        # plt.title('SeaState', size=18,fontweight="bold")
        plt.bar_label(ax.containers[0],size=8,fmt='%.1f')
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_single_seastate.png',bbox_inches='tight')
    
        vessel_imo = list(s['data'].keys())[0]
        color = colorPallet.get(vessel_imo, '#000000')
        data5 = pd.DataFrame.from_dict(s['data'][a][0]['load'])
        data5['vesselname'] = data5['vesselname'].fillna(data5['vesselname'].mode()[0])
        data5 = data5[['range','value','vesselname']]
        data5 = data5.dropna()
    
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(20,10))
        ax = sns.barplot(x="range", y="value", data=data5,palette=[color],hue='vesselname')
        plt.xlabel('ME Load(%)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Slip', size=18,fontweight="bold")
        plt.bar_label(ax.containers[0],size=8,fmt='%.1f')
        ax.legend(title=None)
        plt.xticks(rotation=45)
        plt.savefig('./images/msc_operational_single_slip.png',bbox_inches='tight')

        vessel_imo = list(s['data'].keys())[0]
        color = colorPallet.get(vessel_imo, '#000000')
        data6 = pd.DataFrame.from_dict(s['data'][a][0]['rpm'])
        data6['vesselname'] = data6['vesselname'].fillna(data5['vesselname'].mode()[0])
        data6 = data6[['range','value','vesselname']]
        data6 = data6.dropna()
    
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(20,10))
        ax = sns.barplot(x="range", y="value", data=data6,palette=[color],hue='vesselname')
        plt.xlabel('RPM',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        # plt.title('RPM', size=18,fontweight="bold")
        plt.bar_label(ax.containers[0],size=8,fmt='%.1f',rotation=45)
        ax.legend(title=None)
        ax.xaxis.set_major_locator(MultipleLocator(2))
        plt.xticks(rotation=45)
        plt.savefig('./images/msc_operational_single_rpm.png',bbox_inches='tight')
    
    
        if types != 'operation_profile':
    
            data7 = pd.DataFrame.from_dict(s['data'][a][0][types])
            data7['vesselname'] = data7['vesselname'].fillna(data7['vesselname'].mode()[0])
            data7['type'] = data7['type'].fillna(data7['type'].mode()[0])
            data7['type'] = data7['type'].map(lambda x: x.capitalize())
            data7 = data7.dropna()
            column_1 = data7['type'].values[0]
            column_2 = data7['vesselname'].values[0]
            data7_org = data7[['range','value']]
            data7_org['value'] = data7_org['value'].apply(lambda x: str(x) + '%')
            data7_org = data7_org.rename(columns={'range': column_1, 'value': column_2})
            data7_org = data7_org.astype(str)
    
        else:
    
            data8 = pd.DataFrame.from_dict(s['data'][a][0][types]['columns'])
            data8[0] = data8[0].astype(str)
            lst = data8[0].values.tolist()
            data9 = pd.DataFrame.from_dict(s['data'][a][0][types]['index'])
            data9.rename(columns = {0:'Speed/Draft'}, inplace = True)
            data9 = data9.astype(str)
            data10 = pd.DataFrame.from_dict(s['data'][a][0][types]['data'])
            data10.columns = lst
            data10 = data10.astype(str)
            data11 = pd.concat([data9, data10], axis=1, join='inner')
            for i in lst:
                data11[i] = data11[i].apply(lambda x: str(x) + '%')
            data11 = data11.astype(str)
            
        from fpdf import FPDF
        def simple_table(spacing=3):

            pdf = FPDF()
#*********************************************** 1 page **********************************************************#
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)
            
           
            pdf.image(msc_logo_path,160,8,w=30)
            
            pdf.set_xy(58,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 60, "Operating Profile"+" "+" "+"Report",ln=True)
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 190, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",12)
            pdf.set_xy(10,55)
            
            pdf.cell(10, 2, "Vessel Name :"+" "+vessel_name,ln=True)
            # pdf.cell(10, 2, "Multi Vessels",ln=True)

            pdf.cell(10, 12,"Monitoring period :  "+" "+ mindate+" "+"TO"+" "+maxdate,ln=True)
            pdf.line(10, 70, 190, 70)
            
            pdf.set_xy(20,75)
            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 10, 'Speed',ln=True) 
            pdf.image("./images/msc_operational_single_sog.png",20,85,w=160,h=70)
            
            pdf.set_xy(20,170)
            pdf.cell(180, 10, 'Draft',ln=True) 
            pdf.image("./images/msc_operational_single_draft.png",20,180,w=150,h=80)
            
            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
            
            #*********************************************** 2 page **********************************************************#
            pdf.add_page()  
            
            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            
            pdf.set_xy(20,25)
            pdf.cell(180, 10, 'Power',ln=True) 
            pdf.image("./images/msc_operational_single_power.png",20,35,w=150,h=80)
            
            pdf.set_xy(20,125)
            pdf.cell(180, 10, 'Sea State',ln=True) 
            pdf.image("./images/msc_operational_single_seastate.png",20,135,w=150,h=80)
            
            
            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
            
            
            #*********************************************** 3 page **********************************************************#
            pdf.add_page()  
            
            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            
            pdf.set_xy(20,25)
            pdf.cell(180, 10, 'ME LOAD (%)',ln=True) 
            pdf.image("./images/msc_operational_single_slip.png",20,35,w=160,h=80)
            
            pdf.set_xy(20,125)
            pdf.cell(180, 10, 'RPM',ln=True) 
            pdf.image("./images/msc_operational_single_rpm.png",20,145,w=160,h=80)
            
            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
            
            #*********************************************** 4 page **********************************************************#
            pdf.add_page()  
            
            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            
            pdf.set_xy(10,30)
            pdf.cell(180, 10, types.capitalize(),ln=True)
            
            if types != 'operation_profile':
                spacing=3
                tablefirst_head1 = [data7_org.columns.tolist()]
                tablefirst1 = data7_org.values.tolist()
                pdf.set_font("Arial",'B', size=8)
                col_width = pdf.w /2.5
                row_height = pdf.font_size
                for row in tablefirst_head1:
                    pdf.set_text_color(255,255,255)
                    pdf.set_fill_color(21,55,188)
                    for item in row:
                        pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                    pdf.ln(row_height*spacing)
            
                pdf.set_font("Arial", size=8)
                pdf.set_text_color(0,0,0)
                col_width = pdf.w /2.5
                row_height = pdf.font_size
                for row in tablefirst1:
                    for item in row:
                        pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                    pdf.ln(row_height*spacing)
            
            else: 
                spacing=3
                tablefirst_head1 = [data11.columns.tolist()]
                tablefirst1 = data11.values.tolist()
                pdf.set_font("Arial",'B', size=8)
                col_width = pdf.w /11.5
                row_height = pdf.font_size
                for row in tablefirst_head1:
                    pdf.set_text_color(255,255,255)
                    pdf.set_fill_color(21,55,188)
                    for item in row:
                        pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                    pdf.ln(row_height*spacing)
            
                pdf.set_font("Arial", size=8)
                pdf.set_text_color(0,0,0)
                col_width = pdf.w /11.5
                row_height = pdf.font_size
                for row in tablefirst1:
                    for item in row:
                        pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                    pdf.ln(row_height*spacing)
            
            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

            pdf.output('./documents/'+pdf_name,'F')

        
        simple_table()

        return FileResponse(path = './documents/'+pdf_name,filename='MSC_Data_monitoring_Operationl_teu.pdf')

    elif report_type == 'class': 
        
        #input parameters
        # period_start = '2021-01-01'
        # period_end = '2022-02-01'
        # class_name = 'ADITI'
        
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6ImEyYjE5NjliLTA1ZjEtNGVkOC1hMDYwLTRmODQzMWI1MjQwZCIsImlhdCI6MTY3MTI1MTY0NSwiZXhwIjoxNjcxMzM4MDQ1fQ.4De3ezhyJ0aiV-5_Gm3uZEUGkR0Hg0_UpfEsuK_SJ7k"
        # headers = {'Authorization': "Bearer {}".format(token)}
        # url="https://msc.oceanix.cloud/api/v1/datamonitoring/operationalprofile/vrs/class/2018-01-02/2018-02-01/ADITI/Both/AT%20SEA/5/30/5/35/50/350/0/9/500/100000/-30/30/5/35/1/26/-500/500/10/100"
        # s=requests.get(url , headers =  headers).json()
        
        count = 0
        for i in s['data']:
            data1 = pd.DataFrame.from_dict(s['data'][i][0]['sog'])
            data1['vesselname'] = data1['vesselname'].fillna(data1['vesselname'].mode()[0])
            data1 = data1[['range','value','vesselname']]
            data1 = data1.dropna()
            if count != 0:
                df_sog = pd.concat([df_sog,data1],axis=0)
            else:
                df_sog = data1
            count = count+1
            
        #pivoted_sog = df_sog.pivot(index='range',columns='vesselname',values='value').reset_index()   
        pivoted_sog = df_sog.fillna(0)
        list_vsl_sog = df_sog['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_sog,palette=colors,hue='vesselname')

        #ax = pivoted_sog.plot(x="range", y=list_vsl_sog, kind="bar",figsize=(18,8),width=barWidth)
        plt.xlabel('Speed (kn)',fontweight="bold",size=14)
        plt.ylabel('Data Points (%)',fontweight="bold",size=14)
        #plt.title('Speed (kn)', size=16,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
        plt.xticks(rotation=360)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_class_sog.png', bbox_inches='tight')
        plt.clf()

        count = 0
        for i in s['data']:
            data2 = pd.DataFrame.from_dict(s['data'][i][0]['draft'])
            data2['vesselname'] = data2['vesselname'].fillna(data2['vesselname'].mode()[0])
            data2 = data2[['range','value','vesselname']]
            data2 = data2.dropna()
            if count != 0:
                df_draft = pd.concat([df_draft,data2],axis=0)
            else:
                df_draft = data2
            count = count+1

        #pivoted_draft = df_draft.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_draft = df_draft.fillna(0)   
        list_vsl_draft = df_draft['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_draft,palette= colors,hue='vesselname')

        #ax = pivoted_draft.plot(x="range", y=list_vsl_draft, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('Draft (m)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Draft (m)', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
        plt.xticks(rotation=360)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_class_draft.png', bbox_inches='tight')
        plt.clf()


        count = 0
        for i in s['data']:
            data3 = pd.DataFrame.from_dict(s['data'][i][0]['power'])
            data3['vesselname'] = data3['vesselname'].fillna(data3['vesselname'].mode()[0])
            data3 = data3[['range','value','vesselname']]
            data3 = data3.dropna()
            if count != 0:
                df_power = pd.concat([df_power,data3],axis=0)
            else:
                df_power = data3
            count = count+1

        # pivoted_power = df_power.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_power = df_power.fillna(0)    
        list_vsl_power = df_power['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_power,palette= colors,hue='vesselname')
        # ax = pivoted_power.plot(x="range", y=list_vsl_power, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('Power (kW)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Power (kW)', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  

        plt.xticks(rotation=45)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_class_power.png', bbox_inches='tight')
        plt.clf()

        count = 0
        for i in s['data']:
            data4 = pd.DataFrame.from_dict(s['data'][i][0]['seastate'])
            data4['vesselname'] = data4['vesselname'].fillna(data4['vesselname'].mode()[0])
            data4 = data4[['range','value','vesselname']]
            data4 = data4.dropna()
            if count != 0:
                df_seastate = pd.concat([df_seastate,data4],axis=0)
            else:
                df_seastate = data4
            count = count+1

        #pivoted_seastate = df_seastate.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_seastate = df_seastate.fillna(0)
        list_vsl_seastate = df_seastate['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_seastate,palette= colors,hue='vesselname')
        #ax = pivoted_seastate.plot(x="range", y=list_vsl_seastate, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('SeaState',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('SeaState', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  

        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_class_seastate.png', bbox_inches='tight') 
        plt.clf()

        count = 0
        for i in s['data']:
            data5 = pd.DataFrame.from_dict(s['data'][i][0]['load'])
            data5['vesselname'] = data5['vesselname'].fillna(data5['vesselname'].mode()[0])
            data5 = data5[['range','value','vesselname']]
            data5 = data5.dropna()
            if count != 0:
                df_load = pd.concat([df_load,data5],axis=0)
            else:
                df_load = data5
            count = count+1

        #pivoted_load = df_load.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_load = df_load.fillna(0)    
        list_vsl_load = df_load['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_load,palette= colors,hue='vesselname')
        #ax = pivoted_load.plot(x="range", y=list_vsl_load, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('ME LOAD (%)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Slip', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  

        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_class_slip.png', bbox_inches='tight')
        plt.clf()

        count = 0
        for i in s['data']:
            data6 = pd.DataFrame.from_dict(s['data'][i][0]['rpm'])
            data6['vesselname'] = data6['vesselname'].fillna(data6['vesselname'].mode()[0])
            data6 = data6[['range','value','vesselname']]
            data6 = data6.dropna()
            if count != 0:
                df_rpm = pd.concat([df_rpm,data6],axis=0)
            else:
                df_rpm = data6
            count = count+1

        #pivoted_rpm = df_rpm.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_rpm = df_rpm.fillna(0)   
        list_vsl_rpm = df_rpm['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 2
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_rpm,palette= colors,hue='vesselname')
        #ax = pivoted_rpm.plot(x="range", y=list_vsl_load, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('RPM',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('RPM', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  
        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_class_rpm.png', bbox_inches='tight')
        plt.clf()
        
        # types = 'draft' #input parameter
        count = 0
        for i in s['data']:
            #clr = new_color_lst[j]
            data7 = pd.DataFrame.from_dict(s['data'][i][0][types])
            data7['vesselname'] = data7['vesselname'].fillna(data7['vesselname'].mode()[0])
            data7 = data7[['range','value','vesselname']]
            data7 = data7.dropna()
            if count != 0:
                df_parameter = pd.concat([df_parameter,data7],axis=0)
            else:
                df_parameter = data7
            count = count+1
            
        pivoted_parameter = df_parameter.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_parameter = pivoted_parameter.fillna(0)
        types_column1 =  types.capitalize()
        pivoted_parameter = pivoted_parameter.rename(columns={'range': types_column1})
        pivoted_parameter = pivoted_parameter.astype(str)
        
        from fpdf import FPDF
        def simple_table(spacing=3):

            #report_prepared_date= "11-10-2022"

            pdf = FPDF()
            #*********************************************** 1 page **********************************************************#
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)

            
            pdf.image(msc_logo_path,160,8,w=30)

            pdf.set_xy(58,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 60, "Operating Profile"+" "+" "+"Report",ln=True)
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 190, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",12)
            pdf.set_xy(10,55)
    
            pdf.cell(10, 2, "Class Name :"+" "+class_name,ln=True)
            pdf.cell(10, 12,"Monitoring period :  "+" "+ mindate+" "+"TO"+" "+maxdate,ln=True)
            pdf.line(10, 70, 190, 70)

            pdf.set_xy(20,75)
            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 10, 'Speed',ln=True) 
            pdf.image("./images/msc_operational_class_sog.png",30,85,w=160,h=90)

            pdf.set_xy(20,170)
            pdf.cell(180, 10, 'Draft',ln=True) 
            pdf.image("./images/msc_operational_class_draft.png",30,180,w=160,h=90)

            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

            #*********************************************** 2 page **********************************************************#
            pdf.add_page()  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)

            pdf.set_xy(20,20)
            pdf.cell(180, 10, 'Power',ln=True) 
            pdf.image("./images/msc_operational_class_power.png",30,35,w=160,h=90)

            pdf.set_xy(20,125)
            pdf.cell(180, 10, 'SeaState',ln=True) 
            pdf.image("./images/msc_operational_class_seastate.png",30,140,w=160,h=90)


            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


            #*********************************************** 3 page **********************************************************#
            pdf.add_page()  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)

            pdf.set_xy(20,20)
            pdf.cell(180, 10, 'ME LOAD (%)',ln=True) 
            pdf.image("./images/msc_operational_class_slip.png",30,35,w=160,h=90) 

            pdf.set_xy(20,125)
            pdf.cell(180, 10, 'RPM',ln=True) 
            pdf.image("./images/msc_operational_class_rpm.png",30,140,w=160,h=90)

            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

            #*********************************************** 4 page **********************************************************#
            pdf.add_page(orientation='L')  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)

            pdf.set_xy(10,30)
            pdf.cell(180, 10, types_column1,ln=True) 

            spacing=2
            tablefirst_head1 = [pivoted_parameter.columns.tolist()]
            tablefirst1 = pivoted_parameter.values.tolist()
            pdf.set_font("Arial",'B', size=7)
            col_width = pdf.w /7.5
            row_height = pdf.font_size
            for row in tablefirst_head1:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /7.5
            row_height = pdf.font_size
            for row in tablefirst1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)



            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

            pdf.output('./documents/'+pdf_name,'F')

        simple_table()
        return FileResponse(path = './documents/'+pdf_name,filename='MSC_Data_monitoring_Operationl_teu.pdf')


    elif report_type == 'multi': 
        
        #input parameter
        # period_start = '2021-01-01'
        # period_end = '2022-02-01'
        
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6ImEyYjE5NjliLTA1ZjEtNGVkOC1hMDYwLTRmODQzMWI1MjQwZCIsImlhdCI6MTY3MTI1MTY0NSwiZXhwIjoxNjcxMzM4MDQ1fQ.4De3ezhyJ0aiV-5_Gm3uZEUGkR0Hg0_UpfEsuK_SJ7k"
        # headers = {'Authorization': "Bearer {}".format(token)}
        # url="https://msc.oceanix.cloud/api/v1/datamonitoring/operationalprofile/vrs/multi/2018-01-02/2018-02-01/9282259,9282261/Both/AT%20SEA/5/30/5/35/50/350/0/9/500/100000/-30/30/5/35/1/26/-500/500/10/100"
        # s=requests.get(url , headers =  headers).json()
        
        count = 0
        for i in s['data']:
            #clr = new_color_lst[j]
            data1 = pd.DataFrame.from_dict(s['data'][i][0]['sog'])
            data1['vesselname'] = data1['vesselname'].fillna(data1['vesselname'].mode()[0])
            data1 = data1[['range','value','vesselname']]
            data1 = data1.dropna()
            if count != 0:
                df_sog = pd.concat([df_sog,data1],axis=0)
            else:
                df_sog = data1
            count = count+1
            
        #pivoted_sog = df_sog.pivot(index='range',columns='vesselname',values='value').reset_index()   
        pivoted_sog = df_sog.fillna(0)
        list_vsl_sog = df_sog['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_sog,palette=colors,hue='vesselname')

    #     ax = pivoted_sog.plot(x="range", y=list_vsl_sog, kind="bar",figsize=(18,8),width=barWidth)
        plt.xlabel('Speed (kn)',fontweight="bold",size=14)
        plt.ylabel('Data Points (%)',fontweight="bold",size=14)
        #plt.title('Speed (kn)', size=16,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
        plt.xticks(rotation=360)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_multi_sog.png', bbox_inches='tight')
        plt.clf()

        count = 0
        for i in s['data']:
            data2 = pd.DataFrame.from_dict(s['data'][i][0]['draft'])
            data2['vesselname'] = data2['vesselname'].fillna(data2['vesselname'].mode()[0])
            data2 = data2[['range','value','vesselname']]
            data2 = data2.dropna()
            if count != 0:
                df_draft = pd.concat([df_draft,data2],axis=0)
            else:
                df_draft = data2
            count = count+1

        #pivoted_draft = df_draft.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_draft = df_draft.fillna(0)   
        list_vsl_draft = df_draft['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_draft,palette= colors,hue='vesselname')

        #ax = pivoted_draft.plot(x="range", y=list_vsl_draft, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('Draft (m)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Draft (m)', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
        plt.xticks(rotation=360)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_multi_draft.png', bbox_inches='tight')
        plt.clf()


        count = 0
        for i in s['data']:
            data3 = pd.DataFrame.from_dict(s['data'][i][0]['power'])
            data3['vesselname'] = data3['vesselname'].fillna(data3['vesselname'].mode()[0])
            data3 = data3[['range','value','vesselname']]
            data3 = data3.dropna()
            if count != 0:
                df_power = pd.concat([df_power,data3],axis=0)
            else:
                df_power = data3
            count = count+1

        # pivoted_power = df_power.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_power = df_power.fillna(0)    
        list_vsl_power = df_power['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_power,palette= colors,hue='vesselname')
        # ax = pivoted_power.plot(x="range", y=list_vsl_power, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('Power (kW)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Power (kW)', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  

        plt.xticks(rotation=45)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_multi_power.png', bbox_inches='tight')
        plt.clf()

        count = 0
        for i in s['data']:
            data4 = pd.DataFrame.from_dict(s['data'][i][0]['seastate'])
            data4['vesselname'] = data4['vesselname'].fillna(data4['vesselname'].mode()[0])
            data4 = data4[['range','value','vesselname']]
            data4 = data4.dropna()
            if count != 0:
                df_seastate = pd.concat([df_seastate,data4],axis=0)
            else:
                df_seastate = data4
            count = count+1

        #pivoted_seastate = df_seastate.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_seastate = df_seastate.fillna(0)
        list_vsl_seastate = df_seastate['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_seastate,palette= colors,hue='vesselname')
        #ax = pivoted_seastate.plot(x="range", y=list_vsl_seastate, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('SeaState',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('SeaState', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  

        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_multi_seastate.png', bbox_inches='tight')
        plt.clf()

        count = 0
        for i in s['data']:
            data5 = pd.DataFrame.from_dict(s['data'][i][0]['load'])
            data5['vesselname'] = data5['vesselname'].fillna(data5['vesselname'].mode()[0])
            data5 = data5[['range','value','vesselname']]
            data5 = data5.dropna()
            if count != 0:
                df_load = pd.concat([df_load,data5],axis=0)
            else:
                df_load = data5
            count = count+1

        #pivoted_load = df_load.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_load = df_load.fillna(0)    
        list_vsl_load = df_load['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_load,palette= colors,hue='vesselname')
        #ax = pivoted_load.plot(x="range", y=list_vsl_load, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('ME LOAD (%)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Slip', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  

        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_multi_slip.png', bbox_inches='tight')
        plt.clf()

        count = 0
        for i in s['data']:
            data6 = pd.DataFrame.from_dict(s['data'][i][0]['rpm'])
            data6['vesselname'] = data6['vesselname'].fillna(data6['vesselname'].mode()[0])
            try:
                data6 = data6[['range','value','vesselname']]
            except:
                continue
            data6 = data6.dropna()
            if count != 0:
                df_rpm = pd.concat([df_rpm,data6],axis=0)
            else:
                df_rpm = data6
            count = count+1

        #pivoted_rpm = df_rpm.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_rpm = df_rpm.fillna(0)   
        list_vsl_rpm = df_rpm['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 2
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_rpm,palette= colors,hue='vesselname')
        #ax = pivoted_rpm.plot(x="range", y=list_vsl_load, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('RPM',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('RPM', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  
        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_multi_rpm.png', bbox_inches='tight')
        plt.clf()
        
        # types = 'draft' #input parameter
        count = 0
        for i in s['data']:
            data7 = pd.DataFrame.from_dict(s['data'][i][0][types])
            data7['vesselname'] = data7['vesselname'].fillna(data7['vesselname'].mode()[0])
            data7 = data7[['range','value','vesselname']]
            data7 = data7.dropna()
            if count != 0:
                df_parameter = pd.concat([df_parameter,data7],axis=0)
            else:
                df_parameter = data7
            count = count+1
            
        pivoted_parameter = df_parameter.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_parameter = pivoted_parameter.fillna(0)    
        types_column1 =  types.capitalize()
        pivoted_parameter = pivoted_parameter.rename(columns={'range': types_column1})
        pivoted_parameter = pivoted_parameter.astype(str)
        
        from fpdf import FPDF
        def simple_table(spacing=3):

            pdf = FPDF()
            #*********************************************** 1 page **********************************************************#
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)

            
            pdf.image(msc_logo_path,160,8,w=30)

            pdf.set_xy(58,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 60, "Operating Profile"+" "+" "+"Report",ln=True)
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 190, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",12)
            pdf.set_xy(10,55)
            
            # pdf.cell(10, 2, "Vessel Names :"+" "+vessel_name,ln=True)
            pdf.cell(10, 2, "Multi Vessels",ln=True)

            pdf.cell(10, 12,"Monitoring period :  "+" "+ mindate+" "+"TO"+" "+maxdate,ln=True)
            pdf.line(10, 70, 190, 70)

            pdf.set_xy(20,75)
            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 10, 'Speed',ln=True) 
            pdf.image("./images/msc_operational_multi_sog.png",30,85,w=160,h=90)

            pdf.set_xy(20,170)
            pdf.cell(180, 10, 'Draft',ln=True) 
            pdf.image("./images/msc_operational_multi_draft.png",30,180,w=160,h=90)

            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

            #*********************************************** 2 page **********************************************************#
            pdf.add_page()  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)

            pdf.set_xy(20,20)
            pdf.cell(180, 10, 'Power',ln=True) 
            pdf.image("./images/msc_operational_multi_power.png",30,35,w=160,h=90)

            pdf.set_xy(20,125)
            pdf.cell(180, 10, 'SeaState',ln=True) 
            pdf.image("./images/msc_operational_multi_seastate.png",30,140,w=160,h=90)


            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


            #*********************************************** 3 page **********************************************************#
            pdf.add_page()  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)

            pdf.set_xy(20,20)
            pdf.cell(180, 10, 'ME LOAD (%)',ln=True) 
            pdf.image("./images/msc_operational_multi_slip.png",30,35,w=160,h=90) 

            pdf.set_xy(20,130)
            pdf.cell(180, 10, 'RPM',ln=True) 
            pdf.image("./images/msc_operational_multi_rpm.png",30,140,w=160,h=90)

            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

            #*********************************************** 4 page **********************************************************#
            pdf.add_page()  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)

            pdf.set_xy(10,30)
            pdf.cell(180, 10, types_column1,ln=True) 

            spacing=2
            tablefirst_head1 = [pivoted_parameter.columns.tolist()]
            tablefirst1 = pivoted_parameter.values.tolist()
            pdf.set_font("Arial",'B', size=7)
            col_width = pdf.w /8
            row_height = pdf.font_size
            for row in tablefirst_head1:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /8
            row_height = pdf.font_size
            for row in tablefirst1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)



            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


            pdf.output('./documents/'+pdf_name,'F')

        simple_table()
        return FileResponse(path = './documents/'+pdf_name,filename='MSC_Data_monitoring_Operationl_teu.pdf')

            
    elif report_type == 'teu':
        
        #input parameters
        # period_start = '2021-01-01'
        # period_end = '2022-02-01'
        # teu = '1000'
        
        count = 0
        for i in s['data']:
            #clr = new_color_lst[j]
            data1 = pd.DataFrame.from_dict(s['data'][i][0]['sog'])
            data1['vesselname'] = data1['vesselname'].fillna(data1['vesselname'].mode()[0])
            data1 = data1[['range','value','vesselname']]
            data1 = data1.dropna()
            if count != 0:
                df_sog = pd.concat([df_sog,data1],axis=0)
            else:
                df_sog = data1
            count = count+1
            
        #pivoted_sog = df_sog.pivot(index='range',columns='vesselname',values='value').reset_index()   
        pivoted_sog = df_sog.fillna(0)
        list_vsl_sog = df_sog['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_sog,palette=colors,hue='vesselname')

    #     ax = pivoted_sog.plot(x="range", y=list_vsl_sog, kind="bar",figsize=(18,8),width=barWidth)
        plt.xlabel('Speed (kn)',fontweight="bold",size=14)
        plt.ylabel('Data Points (%)',fontweight="bold",size=14)
        #plt.title('Speed (kn)', size=16,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
        plt.xticks(rotation=360)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_teu_sog.png', bbox_inches='tight')
        
        count = 0
        for i in s['data']:
            data2 = pd.DataFrame.from_dict(s['data'][i][0]['draft'])
            data2['vesselname'] = data2['vesselname'].fillna(data2['vesselname'].mode()[0])
            data2 = data2[['range','value','vesselname']]
            data2 = data2.dropna()
            if count != 0:
                df_draft = pd.concat([df_draft,data2],axis=0)
            else:
                df_draft = data2
            count = count+1

        #pivoted_draft = df_draft.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_draft = df_draft.fillna(0)   
        list_vsl_draft = df_draft['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_draft,palette= colors,hue='vesselname')

        #ax = pivoted_draft.plot(x="range", y=list_vsl_draft, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('Draft (m)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Draft (m)', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
        plt.xticks(rotation=360)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_teu_draft.png', bbox_inches='tight')
        plt.clf()


        count = 0
        for i in s['data']:
            data3 = pd.DataFrame.from_dict(s['data'][i][0]['power'])
            data3['vesselname'] = data3['vesselname'].fillna(data3['vesselname'].mode()[0])
            data3 = data3[['range','value','vesselname']]
            data3 = data3.dropna()
            if count != 0:
                df_power = pd.concat([df_power,data3],axis=0)
            else:
                df_power = data3
            count = count+1

        # pivoted_power = df_power.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_power = df_power.fillna(0)    
        list_vsl_power = df_power['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_power,palette= colors,hue='vesselname')
        # ax = pivoted_power.plot(x="range", y=list_vsl_power, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('Power (kW)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Power (kW)', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  

        plt.xticks(rotation=45)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_teu_power.png', bbox_inches='tight')
        
        count = 0
        for i in s['data']:
            data4 = pd.DataFrame.from_dict(s['data'][i][0]['seastate'])
            data4['vesselname'] = data4['vesselname'].fillna(data4['vesselname'].mode()[0])
            data4 = data4[['range','value','vesselname']]
            data4 = data4.dropna()
            if count != 0:
                df_seastate = pd.concat([df_seastate,data4],axis=0)
            else:
                df_seastate = data4
            count = count+1

        #pivoted_seastate = df_seastate.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_seastate = df_seastate.fillna(0)
        list_vsl_seastate = df_seastate['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_seastate,palette= colors,hue='vesselname')
        #ax = pivoted_seastate.plot(x="range", y=list_vsl_seastate, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('SeaState',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('SeaState', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  

        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_teu_seastate.png', bbox_inches='tight')
        plt.clf()

        count = 0
        for i in s['data']:
            data5 = pd.DataFrame.from_dict(s['data'][i][0]['load'])
            data5['vesselname'] = data5['vesselname'].fillna(data5['vesselname'].mode()[0])
            data5 = data5[['range','value','vesselname']]
            data5 = data5.dropna()
            if count != 0:
                df_load = pd.concat([df_load,data5],axis=0)
            else:
                df_load = data5
            count = count+1

        #pivoted_load = df_load.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_load = df_load.fillna(0)    
        list_vsl_load = df_load['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 0.8
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_load,palette= colors,hue='vesselname')
        #ax = pivoted_load.plot(x="range", y=list_vsl_load, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('ME LOAD (%)',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('Slip', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  

        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_teu_slip.png', bbox_inches='tight')
        plt.clf()

        count = 0
        for i in s['data']:
            data6 = pd.DataFrame.from_dict(s['data'][i][0]['rpm'])
            data6['vesselname'] = data6['vesselname'].fillna(data6['vesselname'].mode()[0])
            try:
                data6 = data6[['range','value','vesselname']]
            except:
                continue
            data6 = data6.dropna()
            if count != 0:
                df_rpm = pd.concat([df_rpm,data6],axis=0)
            else:
                df_rpm = data6
            count = count+1

        #pivoted_rpm = df_rpm.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_rpm = df_rpm.fillna(0)   
        list_vsl_rpm = df_rpm['vesselname'].unique().tolist()
        vessel_imo=list(s['data'].keys())
        colors = [colorPallet.get(imo, '#000000') for imo in vessel_imo]

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        barWidth = 2
        plt.figure(figsize=(15,5))
        ax = sns.barplot(x="range", y="value", data=pivoted_rpm,palette= colors,hue='vesselname')
        #ax = pivoted_rpm.plot(x="range", y=list_vsl_load, kind="bar",figsize=(18,9),width=barWidth)
        plt.xlabel('RPM',fontweight="bold",size=16)
        plt.ylabel('Data Points (%)',fontweight="bold",size=16)
        #plt.title('RPM', size=18,fontweight="bold")
        for bar in ax.patches:
            height = bar.get_height()
            if pd.notna(height):  # Check if height is not NaN
                ax.text(bar.get_x() + bar.get_width() / 2., 0.5 * height, int(height),
                        ha='center', va='center', color='white')
            else:
                ax.text(bar.get_x() + bar.get_width() / 2., 0, '0',
                        ha='center', va='center', color='white')  
        plt.xticks(rotation=90)
        ax.legend(title=None)
        plt.savefig('./images/msc_operational_teu_rpm.png', bbox_inches='tight')
        plt.clf()
        
        # types = 'draft' #input parameter
        
        count = 0
        for i in s['data']:
            data7 = pd.DataFrame.from_dict(s['data'][i][0][types])
            data7['vesselname'] = data7['vesselname'].fillna(data7['vesselname'].mode()[0])
            data7 = data7[['range','value','vesselname']]
            data7 = data7.dropna()
            if count != 0:
                df_parameter = pd.concat([df_parameter,data7],axis=0)
            else:
                df_parameter = data7
            count = count+1
            
        pivoted_parameter = df_parameter.pivot(index='range',columns='vesselname',values='value').reset_index()
        pivoted_parameter = pivoted_parameter.fillna(0)
        types_column1 =  types.capitalize()
        pivoted_parameter = pivoted_parameter.rename(columns={'range': types_column1})
        pivoted_parameter = pivoted_parameter.astype(str)
        
        from fpdf import FPDF
        def simple_table(spacing=3):

            pdf = FPDF()
            #*********************************************** 1 page **********************************************************#
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)

            
            pdf.image(msc_logo_path,160,8,w=30)

            pdf.set_xy(58,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 60, "Operating Profile"+" "+" "+"Report",ln=True)
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 190, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",12)
            pdf.set_xy(10,55)
            
            pdf.cell(10, 2, "TEU :"+" "+str(class_name),ln=True)
            pdf.cell(10, 12,"Monitoring period :  "+" "+ mindate+" "+"TO"+" "+maxdate,ln=True)
            pdf.line(10, 70, 190, 70)

            pdf.set_xy(20,75)
            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)
            pdf.cell(180, 10, 'Speed',ln=True) 
            pdf.image("./images/msc_operational_teu_sog.png",30,85,w=160,h=90)

            pdf.set_xy(20,170)
            pdf.cell(180, 10, 'Draft',ln=True) 
            pdf.image("./images/msc_operational_teu_draft.png",30,180,w=160,h=90)

            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

            #*********************************************** 2 page **********************************************************#
            pdf.add_page()  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)

            pdf.set_xy(20,20)
            pdf.cell(180, 10, 'Power',ln=True) 
            pdf.image("./images/msc_operational_teu_power.png",30,35,w=160,h=90)

            pdf.set_xy(20,125)
            pdf.cell(180, 10, 'SeaState',ln=True) 
            pdf.image("./images/msc_operational_teu_seastate.png",30,140,w=160,h=90)


            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


            #*********************************************** 3 page **********************************************************#
            pdf.add_page()  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)

            pdf.set_xy(20,20)
            pdf.cell(180, 10, 'ME LOAD (%)',ln=True) 
            pdf.image("./images/msc_operational_teu_slip.png",30,35,w=160,h=90) 

            pdf.set_xy(20,125)
            pdf.cell(180, 10, 'RPM',ln=True) 
            pdf.image("./images/msc_operational_teu_rpm.png",30,140,w=160,h=90)

            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

            #*********************************************** 4 page **********************************************************#
            pdf.add_page(orientation='L')  

            pdf.set_font("Arial",'B', size=18)
            pdf.set_text_color(25,47,133)

            pdf.set_xy(10,30)
            pdf.cell(180, 10, types_column1,ln=True) 

            spacing=2
            tablefirst_head1 = [pivoted_parameter.columns.tolist()]
            tablefirst1 = pivoted_parameter.values.tolist()
            pdf.set_font("Arial",'B', size=6)
            col_width = pdf.w /7.5
            row_height = pdf.font_size
            for row in tablefirst_head1:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=6)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /7.5
            row_height = pdf.font_size
            for row in tablefirst1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)



            #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

            pdf.output('./documents/'+pdf_name,'F')
            

    
        simple_table()

        return FileResponse(path = './documents/'+pdf_name,filename='MSC_Data_monitoring_Operationl_teu.pdf')


@router.post('/api/v1/pdf/datamonitoring/timeseries')
async def index(info : Request,imo : str=None, method : str=None,vessel_name: str = None, mindate: str = None , maxdate: str = None , parameter : str = None ,graph_type : str = None ,Bar_Type : str = None , group:str = None , report_type : str = None , vessel_mode : str = None ,multi_parameter : str = None ,y_axis_value:str = None,legend_name: str = None,vdm_db:AsyncSession=Depends(get_vdm_db_async)):
    
    pdf_name = vessel_name + "_Data_Monitering_Time_Series.pdf" 
    color_lst=await vessel_color(vdm_db)
    
    s = await info.json()
    date_obj = mindate + " TO " + maxdate

    #__________Input Parameter _________________
    input_para_data_moni_time={"Monitoring Period": [date_obj],
                                "Parameter":parameter,
                            "Graph_Type":[graph_type],'Vessel':vessel_name,
                            'Vessels':vessel_name,'Group':group,"Report_Type":[report_type],"Mode":[vessel_mode],"Multi_Parameter":multi_parameter,"Bar_Type":[Bar_Type]}
    input_data = pd.DataFrame.from_dict(input_para_data_moni_time)

    #input parameter Single - Multi Parameter
    parameter_list = parameter.split(',')
    # if len(parameter_list) == 1:
    #     parameter_list = parameter_list[0]

    ############ Pdf heading ##############

    if input_data["Mode"].values[0]=="vessel":
        a = input_data["Vessels"].values[0]
        c="Vessel"
    elif input_data["Mode"].values[0]=="multi":   
        a = input_data["Vessels"].values[0]
        c="Multi vessels"
    elif input_data["Mode"].values[0]=="teu":
        a = input_data["Vessels"].values[0]
        c="Teu Group"
    elif input_data["Mode"].values[0]=="class":
        a = input_data["Vessels"].values[0]
        c="Class"    
    else:
        a="invalid"

    b = input_data["Monitoring Period"].values[0]
    d = input_data["Parameter"].values[0].upper()
    print("-------------------------------------------------------")
    print(d)
    print("-------------------------------------------------------")
    print(input_data["Graph_Type"].values[0])
    if input_data["Report_Type"].values[0]=="M":
        e="MONTHLY"
    if input_data["Report_Type"].values[0]=="D":
        e="DAILY"
    if input_data["Report_Type"].values[0]=="Y":
        e="YEARLY"        
    if input_data["Report_Type"].values[0]=="Q":
        e="QUARTERLY"        

    ########################### Single Vessel Multi Parameter#################
    multi_data =s['data']

    first_pair = next(iter((multi_data.items())) )

    first_pair[0]
    # print(parameter_list[0])
    parameter_list=list(parameter_list)
    Parameter_len= len(parameter_list)



        


    data_1 = pd.DataFrame.from_dict(s['data'][first_pair[0]])
    data_1= data_1.fillna(0)
   


    # Rename keys using the `rename` method for dictionaries
    color_lst = { 
        'sog': color_lst.pop('Avg SOG (kn)'), 
        'draft': color_lst.pop('\tAvg Draft (m)'), 
        'distance_covered'  : color_lst.pop('Total Distance Travelled (NM)'),
        'stw' : color_lst.pop('Avg STW (kn)'),
        'trim' : color_lst.pop('Avg Trim (m)'),
        'sea_state' : color_lst.pop('Avg Sea State'),
        'slip'       : color_lst.pop('Avg ME Slip (%)'),
        'cargo_total'    : color_lst.pop('Total Cargo (MT)'),
        'sw_temp'  : color_lst.pop('Avg Sea Water Temperature (℃)'),
        'ambient_temp'  : color_lst.pop('Avg Ambient Temperature (℃)'),   
        'me_load'  : color_lst.pop('Avg ME Load (%)'),
        'power_kw'  : color_lst.pop('Avg ME Power (kW)'),
        'sfoc'    : color_lst.pop('Avg ME SFOC (g/kW.h)'),
        'scoc'    : color_lst.pop('Avg ME SCOC (g/kW.h)'),
        'me_con'         : color_lst.pop('Total ME FOC (MT)'),
        'total_steaming_time' : color_lst.pop('Total ME Running Time (Hrs)'),
        'ae_con'                 : color_lst.pop('Total AE FOC (MT)'),
        'ae_power'        : color_lst.pop('\tAvg AE Power (kW)'),
        'ae_t_steaming'      : color_lst.pop('Total AE Running Time (Hrs)'),
        'bl_con'   : color_lst.pop('Total Boiler FOC (MT)'),
        'hs'    : color_lst.pop('Total Fuel HS (MT)'),
        'ls'    : color_lst.pop('Total Fuel LS (MT)'),
        'mdo'   : color_lst.pop('Total Fuel MDO (MT)'),
        'mgo'       : color_lst.pop('Total Fuel MGO (MT)'),
        'mgo_ls'   : color_lst.pop('Total Fuel MGO LS (MT)'),
        't_co2'     : color_lst.pop('Total CO2 (MT)'),
        't_con'   : color_lst.pop('Total FOC (MT)'),
        'total_steaming_time_mean': color_lst.pop('AVG ME Running Time (Hrs)'),
        'rpm': color_lst.pop('Avg ME RPM (rpm)'),
        'lng': color_lst.pop('Total Cyliner oil (Ltr)'),
        'oil_cyl': color_lst.pop('Total Fuel LNG (MT)'),
        
        **color_lst  # This keeps all the other original keys unchanged
    }






    #__________________saving graph based on user input __________________
    bar_width = 0.35
 
    if input_data["Report_Type"].values[0]=="D"and input_data["Multi_Parameter"].values[0]=="normal":


        count = 0
        j = 0
        cumulative_sum = None
        if input_data["Graph_Type"].values[0] == 'Line':
            if method!='both':
                fig, ax = plt.subplots(figsize = (15, 7))
                for i in s['data']:
                    
                    data = pd.DataFrame.from_dict(s['data'][i])

                    data["corrected_date"]= pd.to_datetime(data["corrected_date"], format='%d %b %Y')

                    data['corrected_date']= pd.to_datetime(data['corrected_date'], format = '%d-%m-%Y')
                    data = data.sort_values(by='corrected_date')

                    data['corrected_date']= data['corrected_date'].dt.strftime('%d-%m-%Y')
                    data = data.sort_values(by='corrected_date')
                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']
                    vessel_imo=list(s['data'].keys())
                    color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                    if count != 0:
                        sns.lineplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)
                    else:
                        sns.lineplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)

                    count = count+1
                    j = j+1


                lst = data['corrected_date'].unique().tolist()
                # print("dfddfdf:", pd.to_datetime(lst).max())
                # date_range = pd.to_datetime(lst).max() - pd.to_datetime(lst).min()
                date_range = pd.to_datetime(lst, format='%d-%m-%Y').max() - pd.to_datetime(lst, format='%d-%m-%Y').min()



                if date_range.days < 365:  # Adjust the threshold as needed
                    ax.xaxis.set_major_locator(md.DayLocator(interval=7))
                else:
                    ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))
                plt.xticks(rotation=45, ha='right')

                    # set axes labels
                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14) 
                ax.legend()
                ax.legend_.set_bbox_to_anchor((1.17, 1))
                ax.legend_.set_title(None)

                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")



            else:
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    data['corrected_date'] = pd.to_datetime(data['corrected_date'], format='mixed')
            # Assuming you've defined combined_data, vrs_data, ada_data before
                    data = data.sort_values(by='corrected_date')
                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']



            # Create a new figure
            fig, ax = plt.subplots(figsize=(15, 7))



            # Plot VRS Data
            ax.plot(vrs_data['corrected_date'], vrs_data[parameter], color='green', label='VRS Data')

            # Plot ADA Data
            ax.plot(ada_data['corrected_date'], ada_data[parameter], color='red', label='ADA Data')



            # Add legend
            ax.legend()



            # Set axis labels
            ax.set_xlabel('Date')
            ax.set_ylabel(parameter)



            # Rotate x-axis labels
            plt.xticks(rotation=-45)
            fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")



            plt.clf()



        elif input_data["Graph_Type"].values[0] == 'Bar':
        #fig, ax = plt.subplots(figsize = (15, 7))
            if method!='both':
                combined_data = pd.DataFrame()
                fig, ax = plt.subplots(figsize = (15, 7))
                for i in s['data']:

                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                    combined_data = combined_data.replace([0], np.nan)
                    combined_data["date_"]=combined_data["corrected_date"]
                    combined_data["date_"]=pd.to_datetime(combined_data["date_"])
                    combined_data_sorted = combined_data.sort_values(by='date_')
                lst = combined_data['corrected_date'].unique().tolist()
                vessel_imo=list(s['data'].keys())
                color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
            #             ax = grouped_data.plot(kind='bar', figsize=(15, 7), color=new_color_lst)
                sns.barplot(data=combined_data_sorted, x='corrected_date', y=input_data["Parameter"].values[0], hue='vessel_name', palette=color)



                ax.set_xlabel('corrected_date')
                ax.set_ylabel(input_data["Parameter"].values[0]) 
                date_range = pd.to_datetime(lst).max() - pd.to_datetime(lst).min()
                if date_range.days < 365:  # Adjust the threshold as needed
                    ax.xaxis.set_major_locator(md.DayLocator(interval=7))
                else:
                    ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))
                plt.xticks(rotation=45, ha='right')

                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14)
                ax.legend_.set_bbox_to_anchor((1.17, 1))
                ax.legend_.set_title(None)
                plt.savefig("./images/Data_monitering_Time_Series.png", bbox_inches="tight")
                plt.clf()
            else:
                def parse_date(date_str):
                    return datetime.strptime(date_str, '%d %b %Y')

           
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                   
                    data = data.sort_values(by='corrected_date')
                    
                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                    

                    fig, ax = plt.subplots(figsize=(15, 7))

                    vrs_indexes = range(len(vrs_data))
                    ada_indexes = range(len(ada_data))

                    ax.bar(vrs_indexes, vrs_data[parameter], bar_width, color='green', label='VRS Data')
                    ax.bar([i + bar_width for i in ada_indexes], ada_data[parameter], bar_width, color='red', label='ADA Data')

                    ax.set_xlabel('Daily')
                    ax.set_ylabel(parameter)

                    # Combine, sort, and reformat dates
                    all_dates = pd.concat([vrs_data['corrected_date'], ada_data['corrected_date']]).unique()
                    all_dates = sorted(all_dates, key=parse_date)

                    ax.set_xticks([i for i in range(len(all_dates))])
                    ax.set_xticklabels(all_dates, rotation=45)

                    ax.legend()
                    plt.tight_layout()
                    # fig.show()
                fig.savefig("./images/Data_monitering_Time_Series.png", bbox_inches="tight")
                
                
        elif input_data["Graph_Type"].values[0] == 'Scatter':
            if method!='both':
                fig, ax = plt.subplots(figsize = (15, 7))
                for i in s['data']:
                    vessel_imo=list(s['data'].keys())
                    color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                    data = pd.DataFrame.from_dict(s['data'][i])

                    data["corrected_date"]= pd.to_datetime(data["corrected_date"], format='%d %b %Y')



    #                 data['corrected_date']= pd.to_datetime(data['corrected_date'], format = '%d-%m-%Y')





    #                 data['corrected_date']= data['corrected_date'].dt.strftime('%d-%m-%Y')
                    if count != 0:
                        sns.scatterplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)
                    else:
                        sns.scatterplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)

                    count = count+1
                    j = j+1
                data["corrected_date"]= pd.to_datetime(data["corrected_date"], format='%d %b %Y')



                data['corrected_date']= pd.to_datetime(data['corrected_date'], format = '%d-%m-%Y')
                data = data.sort_values(by='corrected_date')



                data['corrected_date']= data['corrected_date'].dt.strftime('%d-%m-%Y')
                
                lst = data['corrected_date'].unique().tolist()
                date_range = pd.to_datetime(lst, format='%d-%m-%Y').max() - pd.to_datetime(lst, format='%d-%m-%Y').min()

                # date_range = pd.to_datetime(lst).max() - pd.to_datetime(lst).min()


                if date_range.days < 365:  # Adjust the threshold as needed
                    ax.xaxis.set_major_locator(md.DayLocator(interval=7))
                else:
                    ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))
                plt.xticks(rotation=45, ha='right')



                    # set axes labels
                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14)  
                ax.legend_.set_bbox_to_anchor((1.17, 1))
                ax.legend_.set_title(None)
                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")

                plt.clf() 
            else:
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    data['corrected_date']=pd.to_datetime(data['corrected_date'])
                    data = data.sort_values(by='corrected_date')

                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                fig, ax = plt.subplots(figsize=(15, 7))

                ax.plot(vrs_data['corrected_date'], vrs_data[parameter], 'o', color='green', label='VRS Data')
                ax.plot(ada_data['corrected_date'], ada_data[parameter], 'o', color='red', label='ADA Data')

                ax.set_xlabel('Date')
                ax.set_ylabel(parameter)
                ax.legend()
                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")
                plt.clf()



    ################################################    

    elif input_data["Report_Type"].values[0]=="M"and input_data["Multi_Parameter"].values[0]=="normal":
        count = 0
        j = 0
        cumulative_sum = None
        if input_data["Graph_Type"].values[0] == 'Line':
            if method!='both':
                fig, ax = plt.subplots(figsize = (15, 7))
                for i in s['data']:
                    vessel_imo=list(s['data'].keys())
                    color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                    data = pd.DataFrame.from_dict(s['data'][i])

                    if count != 0:
                        sns.lineplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)
                    else:
                        sns.lineplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)

                    count = count+1
                    j = j+1


                plt.xticks(rotation=45, ha='right')

                    # set axes labels
                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14)  
                ax.legend_.set_bbox_to_anchor((1.17, 1))
                ax.legend_.set_title(None)

                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")

              
            else:
            
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    data['corrected_date'] = pd.to_datetime(data['corrected_date'], format='mixed')


                # Assuming you've defined combined_data, vrs_data, ada_data before
                    data = data.sort_values(by='corrected_date')

                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                # Create a new figure
                fig, ax = plt.subplots(figsize=(15, 7))

                # Plot VRS Data
                ax.plot(vrs_data['corrected_date'], vrs_data[parameter], color='green', label='VRS Data')

                # Plot ADA Data
                ax.plot(ada_data['corrected_date'], ada_data[parameter], color='red', label='ADA Data')

                # Add legend
                ax.legend()

                # Set axis labels
                ax.set_xlabel('Date')
                ax.set_ylabel(parameter)

                # Rotate x-axis labels
                plt.xticks(rotation=-45)

                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")

               

        elif input_data["Graph_Type"].values[0] == 'Bar':
            if method!='both':
                #fig, ax = plt.subplots(figsize = (15, 7))

                combined_data = pd.DataFrame()
                for i in s['data']:

                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                    combined_data = combined_data.replace([0], np.nan)
                    # grouped_data = combined_data.groupby(['corrected_date', 'vessel_name'])[input_data["Parameter"].values[0]].mean().unstack()

                combined_data["date_"]=combined_data["corrected_date"]
                combined_data["date_"]=pd.to_datetime(combined_data["date_"])
                combined_data_sorted = combined_data.sort_values(by='date_')
                vessel_imo=list(s['data'].keys())
                color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                plt.figure(figsize=(15, 7))
                sns.barplot(data=combined_data_sorted, x='corrected_date', y=input_data["Parameter"].values[0], hue='vessel_name', palette=color)

                plt.xlabel('corrected_date', fontweight="bold")
                plt.ylabel(input_data["Parameter"].values[0], fontweight="bold", size=14)
                plt.xlabel('Monthly', fontweight="bold")
                plt.ylabel(y_axis_value, fontweight="bold", size=14)
                plt.legend(title='Vessel Name', bbox_to_anchor=(1.17, 1))
                sns.despine()
                plt.xticks(rotation=45, ha='right')
                plt.savefig("./images/Data_monitering_Time_Series.png", bbox_inches="tight")
                plt.clf()
            else:
                def parse_date(date_str):
                    return datetime.strptime(date_str, '%b %Y')

                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    try:
                        data = data.sort_values(by='corrected_date')
                    except:
                        continue
                    

                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                   

                    fig, ax = plt.subplots(figsize=(15, 7))

                    vrs_indexes = range(len(vrs_data))
                    ada_indexes = range(len(ada_data))

                    ax.bar(vrs_indexes, vrs_data[parameter], bar_width, color='green', label='VRS Data')
                    ax.bar([i + bar_width for i in ada_indexes], ada_data[parameter], bar_width, color='red', label='ADA Data')

                    ax.set_xlabel('Month')
                    ax.set_ylabel(parameter)

                    # Combine, sort, and reformat dates
                    all_dates = pd.concat([vrs_data['corrected_date'], ada_data['corrected_date']]).unique()
                    all_dates = sorted(all_dates, key=parse_date)

                    ax.set_xticks([i for i in range(len(all_dates))])
                    ax.set_xticklabels(all_dates, rotation=45)

                    ax.legend()
                    plt.tight_layout()
                    # fig.show()
                    fig.savefig("./images/Data_monitering_Time_Series.png", bbox_inches="tight")
                    
                

        elif input_data["Graph_Type"].values[0] == 'Scatter':
            if method!='both':
                fig, ax = plt.subplots(figsize = (15, 7))
                for i in s['data']:
                    vessel_imo=list(s['data'].keys())
                    color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                    data = pd.DataFrame.from_dict(s['data'][i])

                    if count != 0:
                        sns.scatterplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)
                    else:
                        sns.scatterplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)

                    count = count+1
                    j = j+1


                plt.xticks(rotation=45, ha='right')

                # set axes labels
                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14)  
                ax.legend_.set_bbox_to_anchor((1.17, 1))     
                ax.legend_.set_title(None)

                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")

                plt.clf()
            else:
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    data['corrected_date']=pd.to_datetime(data['corrected_date'])
                    data = data.sort_values(by='corrected_date')

                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                fig, ax = plt.subplots(figsize=(15, 7))

                ax.plot(vrs_data['corrected_date'], vrs_data[parameter], 'o', color='green', label='VRS Data')
                ax.plot(ada_data['corrected_date'], ada_data[parameter], 'o', color='red', label='ADA Data')

                ax.set_xlabel('Date')
                ax.set_ylabel(parameter)
                ax.legend()
                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")
                


    #########################################
    elif input_data["Report_Type"].values[0]=="Q"and input_data["Multi_Parameter"].values[0]=="normal":
        count = 0
        j = 0
        cumulative_sum = None
        if input_data["Graph_Type"].values[0] == 'Line':
            if method!='both':
                fig, ax = plt.subplots(figsize = (15, 7))
                for i in s['data']:
                    vessel_imo=list(s['data'].keys())
                    color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                    data = pd.DataFrame.from_dict(s['data'][i])
                    data["corrected_date"]  = pd.to_datetime(data["corrected_date"])
                    data = data.sort_values(by='corrected_date')
                    data['date'] = data['corrected_date'].dt.strftime('%Y-%B')


                    if count != 0:
                        sns.lineplot(ax = ax, data=data, x=data['date'].astype(str), y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)
                    else:
                        sns.lineplot(ax = ax, data=data, x= data['date'].astype(str), y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)

                    count = count+1
                    j = j+1



                plt.xticks(rotation=45, ha='right')

                    # set axes labels
                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14)  
                ax.legend_.set_bbox_to_anchor((1.17, 1))
                ax.legend_.set_title(None)

                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")

                plt.clf()
            else:
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    data["corrected_date"]  = pd.to_datetime(data["corrected_date"])
                    data = data.sort_values(by='corrected_date')
                    data['date'] = data['corrected_date'].dt.strftime('%Y-%B')

                # Assuming you've defined combined_data, vrs_data, ada_data before
                    #data = data.sort_values(by='corrected_date')

                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                # Create a new figure
                fig, ax = plt.subplots(figsize=(15, 7))

                # Plot VRS Data
                ax.plot(vrs_data['corrected_date'], vrs_data[parameter], color='green', label='VRS Data')

                # Plot ADA Data
                ax.plot(ada_data['corrected_date'], ada_data[parameter], color='red', label='ADA Data')

                # Add legend
                ax.legend()

                # Set axis labels
                ax.set_xlabel('Date')
                ax.set_ylabel(parameter)

                # Rotate x-axis labels
                plt.xticks(rotation=-45)
                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")

                plt.clf()


        elif input_data["Graph_Type"].values[0] == 'Bar':
            
            if method!='both':
                print('qwertyuiopasdfghjk')
                combined_data = pd.DataFrame()
                for i in s['data']:

                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                    combined_data = combined_data.replace([0], np.nan)
                    # grouped_data = combined_data.groupby(['corrected_date', 'vessel_name'])[input_data["Parameter"].values[0]].mean().unstack()

                combined_data["date_"]=combined_data["corrected_date"]
                combined_data["date_"]=pd.to_datetime(combined_data["date_"])
                combined_data_sorted = combined_data.sort_values(by='date_')
                vessel_imo=list(s['data'].keys())
                color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                plt.figure(figsize=(15, 7))
                sns.barplot(data=combined_data_sorted, x='corrected_date', y=input_data["Parameter"].values[0], hue='vessel_name', palette=color)

                plt.xlabel('corrected_date', fontweight="bold")
                plt.ylabel(input_data["Parameter"].values[0], fontweight="bold", size=14)
                plt.xlabel('Quarterly', fontweight="bold")
                plt.ylabel(y_axis_value, fontweight="bold", size=14)
                plt.legend(title='Vessel Name', bbox_to_anchor=(1.17, 1))
                sns.despine()
                plt.xticks(rotation=45, ha='right')
                # plt.clf()
                plt.savefig("./images/Data_monitering_Time_Series.png", bbox_inches="tight")
                plt.clf()
            else:
                def parse_date(date_str):
                    try:
                        return datetime.strptime(date_str, '%Y-%B')
                    except:
                        return date_str
                    

                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    try:
                        data = data.sort_values(by='corrected_date')
                    except:
                        continue
                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                    

                    fig, ax = plt.subplots(figsize=(15, 7))

                    vrs_indexes = range(len(vrs_data))
                    ada_indexes = range(len(ada_data))

                    ax.bar(vrs_indexes, vrs_data[parameter], bar_width, color='green', label='VRS Data')
                    ax.bar([i + bar_width for i in ada_indexes], ada_data[parameter], bar_width, color='red', label='ADA Data')

                    ax.set_xlabel('Quaterly')
                    ax.set_ylabel(parameter)

                    # Combine, sort, and reformat dates
                    vrs_data['corrected_date'] = sorted(vrs_data['corrected_date'], key=parse_date)
                    ada_data['corrected_date'] = sorted(ada_data['corrected_date'], key=parse_date)
                    
                    
                    all_dates = pd.concat([vrs_data['corrected_date'], ada_data['corrected_date']]).unique()
                    # print("all_dates===========",all_dates)
                    # all_dates = sorted(all_dates, key=parse_date)

                    ax.set_xticks([i for i in range(len(all_dates))])
                    ax.set_xticklabels(all_dates, rotation=45)

                    ax.legend()
                    # plt.tight_layout()
                    # fig.show()
                    # plt.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")
                    fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")
                
        elif input_data["Graph_Type"].values[0] == 'Scatter':
            if method!='both':
                fig, ax = plt.subplots(figsize = (15, 7))
                for i in s['data']:
                    vessel_imo=list(s['data'].keys())
                    color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                    data = pd.DataFrame.from_dict(s['data'][i])
                    data["corrected_date"]  = pd.to_datetime(data["corrected_date"])
                    data['date'] = data['corrected_date'].dt.strftime('%Y-%B')
                    if count != 0:
                        sns.scatterplot(ax = ax, data=data, x=data['date'].astype(str), y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)
                    else:
                        sns.scatterplot(ax = ax, data=data, x=data['date'].astype(str), y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)

                    count = count+1
                    j = j+1


                plt.xticks(rotation=45, ha='right')

                # set axes labels
                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14)  
                ax.legend_.set_bbox_to_anchor((1.17, 1))
                ax.legend_.set_title(None)

                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")

                plt.clf()
            else:
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    try:
                        data['corrected_date']=pd.to_datetime(data['corrected_date'])
                        data = data.sort_values(by='corrected_date')
                    except:
                        continue
                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                fig, ax = plt.subplots(figsize=(15, 7))

                ax.plot(vrs_data['corrected_date'], vrs_data[parameter], 'o', color='green', label='VRS Data')
                ax.plot(ada_data['corrected_date'], ada_data[parameter], 'o', color='red', label='ADA Data')

                ax.set_xlabel('Date')
                ax.set_ylabel(parameter)
                ax.legend()
                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")
                
    elif input_data["Report_Type"].values[0]=="Y"and input_data["Multi_Parameter"].values[0]=="normal":

        count = 0
        j = 0
        cumulative_sum = None
        if input_data["Graph_Type"].values[0] == 'Line':
            if method!='both':
                fig, ax = plt.subplots(figsize = (15, 7))
                for i in s['data']:
                    vessel_imo=list(s['data'].keys())
                    color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                    data = pd.DataFrame.from_dict(s['data'][i])

                    if count != 0:
                        sns.lineplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)
                    else:
                        sns.lineplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)

                    count = count+1
                    j = j+1




                    # set axes labels
                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14)  
                ax.legend_.set_bbox_to_anchor((1.17, 1))
                ax.legend_.set_title(None)
                fig.savefig('./images/Data_monitering_Time_Series.png')
                plt.clf()
            else:
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    try:
                        data['corrected_date'] = pd.to_datetime(data['corrected_date'], format='mixed')
                        data = data.sort_values(by='corrected_date')
                    except:
                        continue    

                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                # Create a new figure
                fig, ax = plt.subplots(figsize=(15, 7))

                # Plot VRS Data
                ax.plot(vrs_data['corrected_date'], vrs_data[parameter], color='green', label='VRS Data')

                # Plot ADA Data
                ax.plot(ada_data['corrected_date'], ada_data[parameter], color='red', label='ADA Data')

                # Add legend
                ax.legend()

                # Set axis labels
                ax.set_xlabel('Date')
                ax.set_ylabel(parameter)

                # Rotate x-axis labels
                plt.xticks(rotation=-45)
                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")
                
                plt.clf()

        elif input_data["Graph_Type"].values[0] == 'Bar':
            if method!='both':
                combined_data = pd.DataFrame()
                for i in s['data']:

                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                    combined_data = combined_data.replace([0], np.nan)
                    grouped_data = combined_data.groupby(['corrected_date', 'vessel_name'])[input_data["Parameter"].values[0]].mean().unstack()

                lst = combined_data['corrected_date'].unique().tolist()
                vessel_imo=list(s['data'].keys())
                color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                ax = grouped_data.plot(kind='bar', figsize=(15, 7), color=color)
                ax.set_xlabel('corrected_date')
                ax.set_ylabel(input_data["Parameter"].values[0])
                date_range = pd.to_datetime(lst).max() - pd.to_datetime(lst).min()
                if date_range.days < 365:  # Adjust the threshold as needed
                    ax.xaxis.set_major_locator(md.DayLocator(interval=7))
                else:
                    ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))
                plt.xticks(rotation=45, ha='right')

                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14)
                ax.legend_.set_bbox_to_anchor((1.17, 1))
                ax.legend_.set_title(None)
                plt.savefig("./images/Data_monitering_Time_Series.png", bbox_inches="tight")
                plt.clf()
                # plt.show()
                
             
            else:
                combined_data = pd.DataFrame()
                # fig, ax = plt.subplots(figsize = (15, 7))

                def parse_date(date_str):
                    return datetime.strptime(date_str, '%Y')

                for i in s['data']:
                    try:
                        data = pd.DataFrame.from_dict(s['data'][i])
                        data = data.sort_values(by='corrected_date')
                    except:
                        continue
                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                    

                    fig, ax = plt.subplots(figsize=(15, 7))

                    vrs_indexes = range(len(vrs_data))
                    ada_indexes = range(len(ada_data))

                    ax.bar(vrs_indexes, vrs_data[parameter], bar_width, color='green', label='VRS Data')
                    ax.bar([i + bar_width for i in ada_indexes], ada_data[parameter], bar_width, color='red', label='ADA Data')

                    ax.set_xlabel('Quaterly')
                    ax.set_ylabel(parameter)

                    # Combine, sort, and reformat dates
                    all_dates = pd.concat([vrs_data['corrected_date'], ada_data['corrected_date']]).unique()
                    all_dates = sorted(all_dates, key=parse_date)

                    ax.set_xticks([i for i in range(len(all_dates))])
                    ax.set_xticklabels(all_dates, rotation=45)

                    ax.legend()
                    plt.tight_layout()
                    # fig.show()
                plt.savefig("./images/Data_monitering_Time_Series.png", bbox_inches="tight")
                plt.clf()


        elif input_data["Graph_Type"].values[0] == 'Scatter':
            if method!='both':
                fig, ax = plt.subplots(figsize = (15, 7))
                for i in s['data']:
                    vessel_imo=list(s['data'].keys())
                    color = [color_lst.get(imo, '#000000') for imo in vessel_imo]
                    data = pd.DataFrame.from_dict(s['data'][i])

                    if count != 0:
                        sns.scatterplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)
                    else:
                        sns.scatterplot(ax = ax, data=data, x='corrected_date', y=input_data["Parameter"].values[0],hue="vessel_name",palette=color)

                    count = count+1
                    j = j+1




                # set axes labels
                plt.xlabel('Date',fontweight="bold")
                plt.ylabel(y_axis_value,fontweight="bold",size=14)  
                ax.legend_.set_bbox_to_anchor((1.17, 1))

                ax.legend_.set_title(None)
                fig.savefig('./images/Data_monitering_Time_Series.png')      
                plt.clf()
            else:
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    data['corrected_date']=pd.to_datetime(data['corrected_date'])
                    data = data.sort_values(by='corrected_date')

                    vrs_data = data[data['type'] == 'VRS Data']
                    ada_data = data[data['type'] == 'ADA Data']

                fig, ax = plt.subplots(figsize=(15, 7))

                ax.plot(vrs_data['corrected_date'], vrs_data[parameter], 'o', color='green', label='VRS Data')
                ax.plot(ada_data['corrected_date'], ada_data[parameter], 'o', color='red', label='ADA Data')

                ax.set_xlabel('Date')
                ax.set_ylabel(parameter)
                ax.legend()
                fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")
                
    
    ####### Multi Parameter############

    elif input_data["Mode"].values[0]=="vessel" and  input_data["Report_Type"].values[0]=="D" and input_data["Multi_Parameter"].values[0]=="multiple":
        data_1["corrected_date"]= pd.to_datetime(data_1["corrected_date"], format='%d %b %Y')
    #     data_1['corrected_date']= pd.to_datetime(data_1['corrected_date'], format = '%d-%m-%Y')
    #     try:
    #         data_1["corrected_date"] = pd.to_datetime(data_1["corrected_date"], format='%d-%m-%Y')
    #     except:
    #         data_1["corrected_date"] = pd.to_datetime(data_1["corrected_date"], format='%d %b %Y')
            
        lst = data_1['corrected_date'].unique().tolist()
        date_range = pd.to_datetime(lst).max() - pd.to_datetime(lst).min()
        colors = [color_lst.get(param, '#000000') for param in parameter_list]

        if input_data["Graph_Type"].values[0] == 'Line':
            fig, ax = plt.subplots(figsize=(20, 10))

            for i in range(Parameter_len):
                sns.lineplot(ax=ax, data=data_1, x='corrected_date', y=parameter_list[i], color=colors[i], label=f'{parameter_list[i]}')

            plt.xlabel('Date', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)

            if date_range.days < 365:  # Adjust the threshold as needed
                ax.xaxis.set_major_locator(md.DayLocator(interval=7))
            else:
                ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))

            # Rotate x-ticks
            plt.xticks(rotation=45, ha='right')
            ax.legend(loc='best', bbox_to_anchor=(1, 1))
            plt.tight_layout()
            fig.savefig('./images/Data_monitoring_Time_Series_Line.png', bbox_inches="tight")
            # plt.show()

            fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")

            plt.clf()
        elif input_data["Graph_Type"].values[0] == 'Bar':
            fig, ax = plt.subplots(figsize=(20, 10))
            index = np.arange(len(data_1['corrected_date']))
        
            # Dynamically adjust bar width
            bar_width = 0.4 if input_data["Bar_Type"].values[0] != 'stacked' else 0.8
        
            # Stacked Bar Plot
            if input_data["Bar_Type"].values[0] == 'stacked':
                bottom = np.zeros(len(data_1))
                # Clean and split legend names
                for i, parameter in enumerate(parameter_list):
                    ax.bar(index + i * bar_width, data_1[parameter], bar_width, color=colors[i], label=parameter_list[i])
                    bottom += data_1[parameter].values
            else:
                # Side-by-side bars
                for i, parameter in enumerate(parameter_list):
                    ax.bar(index + i * bar_width, data_1[parameter], bar_width, color=colors[i], label=parameter_list[i])

        
            # X-axis adjustments
            ax.set_xlabel('Date', fontsize=12, fontweight='bold')
            ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        
            # Set major ticks dynamically based on data size
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
            # Rotate and align x-axis labels
            plt.xticks(index[::10], data_1['corrected_date'].dt.strftime('%Y-%m-%d')[::10], 
                       rotation=45, ha='right')  # Show every 10th tick (adjust dynamically)
        
            # Add legend and layout
            ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
            plt.tight_layout()
        
            # Save and show the plot
            plt.savefig('./images/Data_monitoring_Time_Series_Bar.png', bbox_inches="tight")
            # plt.show()

        elif input_data["Graph_Type"].values[0] == 'Scatter':
            fig, ax = plt.subplots(figsize=(20, 10))
            for i in range(Parameter_len):
                sns.scatterplot(ax=ax, data=data_1, x='corrected_date', y=parameter_list[i], color=colors[i], label=f'{parameter_list[i]}')

            plt.xlabel('Date', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)

            if date_range.days < 365:  # Adjust the threshold as needed
                ax.xaxis.set_major_locator(md.DayLocator(interval=7))
            else:
                ax.xaxis.set_major_locator(md.WeekdayLocator(interval=2))

            plt.xticks(rotation=45, ha='right')
            ax.legend(loc='best', bbox_to_anchor=(1, 1))
            plt.tight_layout()
            
            fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")

            plt.clf() 
    elif input_data["Mode"].values[0] == "vessel" and input_data["Report_Type"].values[0] == "M" and input_data["Multi_Parameter"].values[0] == "multiple":
        # Convert 'corrected_date' to datetime and sort by date
        data_1['corrected_date'] = pd.to_datetime(data_1['corrected_date'])
        data_1 = data_1.sort_values(by='corrected_date').reset_index(drop=True)
    
        # Get unique dates and calculate date range
        lst = data_1['corrected_date'].dt.strftime('%b %Y').unique().tolist()  # Format to month and year
        print("suuuuuuuuuuuuuuuuuuuuuuuuuuuu")
        date_range = pd.to_datetime(lst).max() - pd.to_datetime(lst).min()
    
        # Get colors for the parameters
        colors = [color_lst.get(param, '#000000') for param in parameter_list]
    
        if input_data["Graph_Type"].values[0] == 'Line':
            fig, ax = plt.subplots(figsize=(15, 7))
    
            for i in range(Parameter_len):
                sns.lineplot(ax=ax, data=data_1, x='corrected_date', y=parameter_list[i], color=colors[i], label=f'{parameter_list[i]}')
    
            plt.xlabel('Monthly', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)
            plt.xticks(rotation=45, ha='right')
            ax.legend(loc='best', bbox_to_anchor=(1.17, 1))
    
            plt.tight_layout()
            fig.savefig('./images/Data_monitoring_Time_Series_Line.png', bbox_inches="tight")
    
        elif input_data["Graph_Type"].values[0] == 'Bar':
            fig, ax = plt.subplots(figsize=(15, 7))
            bar_width = 0.35  # Width of each bar
            index = np.arange(len(data_1))  # Recreate index after sorting
    
            if input_data["Bar_Type"].values[0] == 'stacked':
                bottom = np.zeros(len(data_1))
                for i, parameter in enumerate(parameter_list):
                    ax.bar(index, data_1[parameter], bar_width, bottom=bottom, color=colors[i], label=f'{parameter_list[i]}')
                    bottom += data_1[parameter].values
            else:
                for i, parameter in enumerate(parameter_list):
                    ax.bar(index + i * bar_width, data_1[parameter], bar_width, color=colors[i], label=f'{parameter_list[i]}')
    
            plt.xlabel('Date', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)
            plt.xticks(index, data_1['corrected_date'].dt.strftime('%b %Y'), rotation=45, ha='right')
            ax.legend(loc='best', bbox_to_anchor=(1.17, 1))
    
            plt.tight_layout()
            fig.savefig('./images/Data_monitoring_Time_Series_Bar.png', bbox_inches="tight")
            # plt.show()
        elif input_data["Graph_Type"].values[0] == 'Scatter':
            fig, ax = plt.subplots(figsize=(15, 7))
    
            for i in range(Parameter_len):
                sns.scatterplot(ax=ax, data=data_1, x='corrected_date', y=parameter_list[i], color=colors[i], label=f'{parameter_list[i]}')
    
            plt.xlabel('Date', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)
            plt.xticks(rotation=45, ha='right')
            ax.legend(loc='best', bbox_to_anchor=(1.17, 1))
    
            plt.tight_layout()
            fig.savefig('./images/Data_monitoring_Time_Series_Scatter.png', bbox_inches="tight")
            plt.clf()

    elif input_data["Mode"].values[0]=="vessel" and input_data["Report_Type"].values[0]=="Q" and input_data["Multi_Parameter"].values[0]=="multiple":
        
        # Correct the quarter format in the 'corrected_date' column
        data_1['corrected_date'] = data_1['corrected_date'].astype(str).str.replace(r'(\d{4})(Q\d)', r'\1 - \2', regex=True)
        
        # Assign quarter labels
        data_1['quarter'] = pd.PeriodIndex(data_1['corrected_date'], freq='Q')
        
        # Generate unique quarters and calculate date range
        quarters = data_1['quarter'].unique().tolist()
        date_range = data_1['quarter'].max().end_time - data_1['quarter'].min().start_time
        
        # Plot Line Graph
        if input_data["Graph_Type"].values[0] == 'Line':
            fig, ax = plt.subplots(figsize=(15, 7))
        
            for i in range(Parameter_len):
                sns.lineplot(ax=ax, data=data_1, x='corrected_date', y=parameter_list[i], color=colors[i], label=f'{parameter_list[i]}')
        
            plt.xlabel('Quarterly', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)
            plt.xticks(rotation=45, ha='right')  # Adjust for readability
            plt.tight_layout()
        
            ax.legend(loc='best', bbox_to_anchor=(1.17, 1))
            fig.savefig('./images/Data_monitoring_Time_Series_Line.png', bbox_inches="tight")
            # plt.show()
        
        # Define the index for x-axis based on the length of data_1
        index = np.arange(len(data_1))
        
        # Correct the quarter format in 'quarters' column
        quarters = data_1['corrected_date'].astype(str).str.replace(r'(\d{4})(Q\d)', r'\1 - \2', regex=True)
        
        # Bar Graph
        if input_data["Graph_Type"].values[0] == 'Bar':
            fig, ax = plt.subplots(figsize=(15, 7))
            bar_width = 0.35  # Width of each bar
        
            if input_data["Bar_Type"].values[0] == 'stacked':
                bottom = np.zeros(len(data_1))  # Initialize bottom for stacked bars
                for i, parameter in enumerate(parameter_list):
                    ax.bar(index, data_1[parameter], bar_width, bottom=bottom, 
                           color=colors[i], label=f'{parameter_list[i]}')
                    bottom += data_1[parameter].values  # Update bottom for next series
            else:  # Grouped bar chart
                for i, parameter in enumerate(parameter_list):
                    ax.bar(index + i * bar_width, data_1[parameter], bar_width, 
                           color=colors[i], label=f'{parameter_list[i]}')
        
            # Label and Ticks
            plt.xlabel('Quarter', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)
            plt.xticks(index + (len(parameter_list) - 1) * bar_width / 2, quarters, 
                       rotation=45, ha='right')  # Align x-ticks to quarters
        
            # Legend
            ax.legend(loc='best', bbox_to_anchor=(1.17, 1))
        
            # Adjust layout and save figure
            plt.tight_layout()
            fig.savefig('./images/Data_monitoring_Time_Series_Bar.png', bbox_inches="tight")
            # plt.show()
        
        # Scatter Plot
        elif input_data["Graph_Type"].values[0] == 'Scatter':
            fig, ax = plt.subplots(figsize=(15, 7))
        
            for i in range(Parameter_len):
                sns.scatterplot(ax=ax, data=data_1, x='quarter', y=parameter_list[i], 
                                color=colors[i], label=f'{parameter_list[i]}')
        
            plt.xlabel('Quarter', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)
            plt.xticks(index, quarters, rotation=45, ha='right')  # Correct x-axis tick labels
            ax.legend(loc='best', bbox_to_anchor=(1.17, 1))
        
            plt.tight_layout()
            fig.savefig('./images/Data_monitoring_Time_Series_Scatter.png', bbox_inches="tight") 

    elif input_data["Mode"].values[0]=="vessel" and input_data["Report_Type"].values[0]=="Y" and input_data["Multi_Parameter"].values[0]=="multiple":
        lst = data_1['corrected_date'].unique().tolist()
        date_range = pd.to_datetime(lst).max() - pd.to_datetime(lst).min()
        colors = [color_lst.get(param, '#000000') for param in parameter_list]

        if input_data["Graph_Type"].values[0] == 'Line':
            fig, ax = plt.subplots(figsize=(15, 7))

            for i in range(Parameter_len):
                sns.lineplot(ax=ax, data=data_1, x='corrected_date', y=parameter_list[i], color=colors[i], label=f'{parameter_list[i]}')

            plt.xlabel('Date', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)
            plt.xticks(rotation=45, ha='right')

            # Save and show plot
            plt.tight_layout()
            fig.savefig('./images/Data_monitoring_Time_Series_Line.png', bbox_inches="tight")
            plt.clf()

        elif input_data["Graph_Type"].values[0] == 'Bar':
            fig, ax = plt.subplots(figsize=(15, 7))
            bar_width = 0.35  # Width of each bar
            n = len(data_1['corrected_date'])  # Number of data points
            index = np.arange(n)  # Index for the x-axis locations of the bars
            
            if input_data["Bar_Type"].values[0] == 'stacked':
                bottom = np.zeros(n)
                for i, parameter in enumerate(parameter_list):
                    ax.bar(index, data_1[parameter], bar_width, bottom=bottom, color=colors[i], label=f'{parameter_list[i]}')
                    bottom += data_1[parameter].values
            else:
                for i, parameter in enumerate(parameter_list):
                    ax.bar(index + i * bar_width, data_1[parameter], bar_width, color=colors[i], label=f'{parameter_list[i]}')

            plt.xlabel('Date', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)
            plt.xticks(index + bar_width * (len(parameter_list) - 1) / 2, data_1['corrected_date'], rotation=45, ha='right')
            
            # Explicitly create the legend first
            legend = ax.legend()
            legend.set_bbox_to_anchor((1, 1))  # Adjust legend position
            
            plt.tight_layout()
            fig.savefig('./images/Data_monitoring_Time_Series_Bar.png', bbox_inches="tight")
            plt.clf()


        elif input_data["Graph_Type"].values[0] == 'Scatter':
            fig, ax = plt.subplots(figsize=(15, 7))

            for i, parameter in enumerate(parameter_list):
                sns.scatterplot(ax=ax, data=data_1, x='corrected_date', y=parameter, color=colors[i], label=f'{parameter_list[i]}')

            plt.xlabel('Date', fontweight="bold", size=12)
            plt.ylabel("Value", fontweight="bold", size=12)
            plt.xticks(rotation=45, ha='right')
            
            # Adjust legend only if it exists
            if ax.legend_ is not None:
                ax.legend_.set_bbox_to_anchor((1.17, 1))
            
            # #plt.clf()

            fig.savefig('./images/Data_monitering_Time_Series.png', bbox_inches="tight")
            plt.clf() 




    #____________PDF____________________
        
        



    def simple_table(spacing=3):

        #report_prepared_date= "11-10-2022"

        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        
        pdf.image(msc_logo_path,160,8,w=35)

    #Cell postion from left side
        pdf.set_xy(25,35)
        pdf.set_text_color(25,47,133)
        print(input_data)
        if input_data["Multi_Parameter"].values[0]=="normal":
            pdf.multi_cell(155, 20, d+ " "+ e +" "+"REPORT",align='C')
        elif input_data["Multi_Parameter"].values[0]=="multiple" :
            pdf.multi_cell(155, 20,  e +" "+"REPORT",align='C')
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)#(x_start, y_start, x_end, y_end)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)
        #pdf.multi_cell(80,14.5,"Report Date :"+" "+ report_prepared_date, align='R')

        
        pdf.cell(10, 2, c+ ":"+" "+a,ln=True)
        pdf.cell(10, 12,"Monitoring period :  "+" "+ b,ln=True)
        pdf.line(10, 70, 190, 70)
        
        
        
        pdf.set_xy(15,65)
        # Set image based on Multi_Parameter and Graph_Type
        if input_data["Multi_Parameter"][0] == "normal":
            image_path = "./images/Data_monitering_Time_Series.png"
        else:
            graph_type = input_data["Graph_Type"][0]
            if graph_type == "Line":
                image_path = "./images/Data_monitering_Time_Series_Line.png"
            elif graph_type == "Bar":
                image_path = "./images/Data_monitoring_Time_Series_Bar.png"
            elif graph_type == "Scatter":
                image_path = "./images/Data_monitering_Time_Series_Scatter.png"
            else:
                image_path = "./images/Data_monitering_Time_Series.png"  # Default image if unknown

        # Insert the image
        pdf.image(image_path, 15, 80, w=180, h=150)
        
        pdf.output('documents/'+pdf_name,'F')
        
        # pdf.output('documents/.pdf','F')
    simple_table()  
    return FileResponse(path = './documents/'+pdf_name,filename='Data_monitering_Time_Series.pdf')
    
@router.post('/api/v1/pdf/datamonitoring/relational/multi')
async def index(info : Request ,vessel_name:str = None , mindate:str = None , maxdate:str = None, y_axis :str = None , x_axis :str = None,x:str=None):
    
    Multi_Parameter_Relational =  await info.json()

    #__________Relational Single Vessel___________


    # url= "https://msc.oceanix.cloud/api/sysapi/api/v1/datamonitoring/data=vrs/group=vessel/mindate=2021-01-01/maxdate=2022-02-01/period=D/imo=9648075/voycond=Both/status=At%20Sea/draftmin=5/draftmax=30/sogmin=5/sogmax=35/sfocmin=50/sfocmax=350/seastatemin=0/seastatemax=9/mcrmin=500/mcrmax=100000/slipmin=-30/slipmax=30/stwmin=5/stwmax=35/steamingtimemin=1/steamingtimemax=26/rpmmin=-500/rpmmax=500/loadmin=10/loadmax=100"
    # Multi_Parameter_Relational =requests.get(url , headers =  headers).json()

    date_obj = [mindate + " TO " + maxdate]
    
    #__________Input Parameter _________________
    input_para_data_moni_time={"Monitoring Period": date_obj,'Vessel':vessel_name,"Mode":["Single Vessel"],"Multi_Parameter":"multi"}
    input_data = pd.DataFrame.from_dict(input_para_data_moni_time)



    # Y_axis_selection = ["sog","rpm"]
    Y_axis_selection = y_axis.split(",")
    # print(Y_axis_selection)
    # X_axis_selection= "sfoc"
    X_axis_selection= x_axis

    input_data_mode ="Single Vessel"
    Multi_paramter= "True"
    a= input_data["Vessel"].values[0]
    b = input_data["Monitoring Period"].values[0]

    #_______________________#
    multi_data =Multi_Parameter_Relational['data']

    first_pair = next(iter((multi_data.items())) )

    first_pair[0]



    Parameter_len= len(Y_axis_selection)

    data_1 = pd.DataFrame.from_dict(Multi_Parameter_Relational['data'][first_pair[0]])

    # color_lst = ['blue','yellow','red','violet','green','cyan','pink','gray','orange','purple','indigo','magenta']
    color_lst = ['brown', 'darkviolet', 'red', 'green', 'orange', 'blue', 'yellow', 'cyan', 'pink', 'gray', 'olive', 'purple', 'indigo', 'magenta', 'beige', 'black', 'teal', 'maroon', 'navy', 'turquoise', 'salmon', 'gold', 'silver', 'coral', 'violet', 'lime', 'orchid', 'plum', 'khaki']

    new_color_lst_1 = []

    for z in range (0,Parameter_len):
        color_sel = color_lst[z]
        new_color_lst_1.append(color_sel)
    new_color_lst_1 
    #_________Graph______________#
    if input_data_mode =="Single Vessel" and Multi_paramter== "True" :
        fig, ax = plt.subplots(figsize = (15, 7))
        j = 0
        i = 0
        while i < Parameter_len:
            clr = new_color_lst_1[j]

            sns.scatterplot(ax=ax,data=data_1, x=X_axis_selection, y=Y_axis_selection[i] ,color=clr,label=Y_axis_selection[i])

            i += 1
            j = j+1
        plt.xlabel(x,fontweight="bold",size=14)
        plt.ylabel("Value",fontweight="bold",size=14)  
            
        fig.savefig("./images/Data_monitering_relational_Multi_Parameter.png")
        plt.clf() 
    else:
        print("Wrong Input")
        
    #__________Pdf________________________    
        
    def Relational_Parameter_Multi(spacing=3):

        #report_prepared_date= "11-10-2022"

        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        #pdf.image(oceanix_logo_path,15,15,w=35)
        pdf.image(msc_logo_path,160,8,w=35)

    #Cell postion from left side
        pdf.set_xy(25,35)
        pdf.set_text_color(25,47,133)
        
        pdf.multi_cell(155, 20,  "RELATIONAL PARAMETER REPORT",align='C')
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)#(x_start, y_start, x_end, y_end)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)

        
        pdf.cell(10, 2, "Vessel"+ ":"+" "+a,ln=True)
        pdf.cell(10, 12,"Monitoring period :  "+" "+ b,ln=True)
        pdf.line(10, 70, 190, 70)
        
        
        
        pdf.set_xy(15,65)
        pdf.image("./images/Data_monitering_relational_Multi_Parameter.png",15,80,w=180,h=130)
        
        pdf_name = vessel_name + '_' + 'Data_monitering_relational_Multi_Parameter.pdf'
        pdf.output('./documents/'+pdf_name,'F')

    pdf_name = vessel_name + '_' + 'Data_monitering_relational_Multi_Parameter.pdf'

    Relational_Parameter_Multi() 
    return FileResponse(path = './documents/'+pdf_name,filename='datamonitoring_relationaldata.pdf')


@router.post('/api/v1/pdf/datamonitoring/relational')
async def index(info : Request,imo:str = None,vessel_name:str = None,report_type:str = None ,method:str=None, mindate:str = None , maxdate:str = None , group:str = None , x:str = None , y:str = None , x_axis :str = None , y_axis : str = None ,  Type :str = None,vdm_db:AsyncSession=Depends(get_vdm_db_async)):
    # pdf_name = ""
    # try:
    #     imos = vessel_name[-7:]
    #     if isinstance(imos,[len(imos)==7,int]) == True:
    #         pass
    # except:
    #     pass    
            
    colorPallet=await vessel_color(vdm_db)
    s = await info.json()
    # report_type="Single Vessel"     #Group    #Multi
    # period="2021-01-01 to 2022-02-01"
    period = mindate + " to " + maxdate
    Group_Number=group
    # x="M/E RPM (RPM)"
    # y="M/E Power (kW)"
    # x_axis="rpm"
    # y_axis="power_kw"
    # Type="3rd Degree Polynomial"     #Linear   #2nd Degree Polynomial  3rd Degree Polynomial
    x_input_None=x.upper()
    y_input_None=y.upper()
    # x_axis = x.replace('%20', ' ')
    # y_axis = y.replace('%20', ' ')
    None_Heading=x_input_None+" Vs "+y_input_None+" REPORT"
    None_Heading = None_Heading.replace('_', ' ')
    # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6IjU5N2E3NDA3LWRlYjAtNGQwMy04ZWQyLTA3YzBkYmI3OTJhNiIsImlhdCI6MTY3MDY1MTgyOCwiZXhwIjoxNjcwNzM4MjI4fQ.yAg0IyNKWZ7ygWi5OCrr28F4GbI-Bu541bqCg6Qn33A"
    # headers = {'Authorization': "Bearer {}".format(token)}
    column_mapping = {
                'corrected_date': 'Corrected Date',
                'distance_covered': 'Distance Covered (nm)',
                'cargo_total': 'Cargo Total (mt)',
                'me_con': 'ME Consumption (mt)',
                'total_steaming_time': 'Total Steaming Time (h)',
                'total_steaming_time_mean': 'Total Steaming Time Mean (h)',
                'ae_con': 'AE Consumption (mt)',
                'ae_t_steaming': 'AE Total Steaming Time (h)',
                'bl_con': 'BL Consumption (mt)',
                'hs': 'HS Fuel (mt)',
                'ls': 'LS Fuel (mt)',
                'mdo': 'MDO (mt)',
                'mgo': 'MGO (mt)',
                'mgo_ls': 'MGO LS (mt)',
                't_co2': 'Total CO2 Emissions (mt)',
                't_con': 'Total Consumption (mt)',
                'oil_cyl': 'Cylinder Oil (l)',
                'sog': 'SOG (kn)',
                'scoc': 'SCOC (g/kWh)',
                'stw': 'STW (kn)',
                'sfoc': 'SFOC (g/kWh)',
                'rpm': 'RPM',
                'slip': 'Slip (%)',
                'power_kw': 'Power (kW)',
                'me_load': 'ME Load (%)',
                'draft': 'Draft (m)',
                'sea_state': 'Sea State (Beaufort)',
                'sw_temp': 'SW Temp (°C)',
                'ambient_temp': 'Ambient Temp (°C)',
                'ae_power': 'AE Power (kW)',
                'trim': 'Trim (m)',
                'eca': 'ECA',
                'rpm_loaddia': 'RPM Load Diagram',
                'lng': 'LNG Consumption (mt)',
                'type': 'Vessel Type',
                # 'vessel_name': 'Vessel Name',
                # 'imo': 'IMO Number'
            }
    if report_type=="vessel":
        pdf_name = vessel_name + "DR_Single_Vessel.pdf"
        if method!='both':
        
            for i in s['data']:
                imo = i
            print("imoimoimoimoimoimoimo",imo)    

            DataTable_df = pd.DataFrame.from_dict(s['data'][imo])
            print(DataTable_df.columns)
            

            # Rename the columns in your DataFrame
            DataTable_df = DataTable_df.rename(columns=column_mapping)
            print("DataTable_dfDataTable_df",DataTable_df.columns)
            print("DataTable_dfDataTable_df",x_axis)
            if column_mapping[x_axis] and column_mapping[y_axis]:
                x_axis = column_mapping[x_axis]
                y_axis = column_mapping[y_axis]

              
            
            try:
                DataTable_df = DataTable_df[DataTable_df[x_axis] != 0]
                DataTable_df = DataTable_df.dropna(subset=[x_axis])
            except:
                pass    
            # vessel_name_single_None=DataTable_df[["vessel_name"]]

            fig, ax = plt.subplots(figsize = (15, 7))
            if Type=="None":
                sns.scatterplot(x=x_axis, y=y_axis, data=DataTable_df, hue="vessel_name", palette=colorPallet)
            elif Type=="Linear":
            #sns.regplot(df1.sqft_living, df1.Price, data = df1, scatter_kws = {‘color’: ‘g’}, line_kws = {‘color’: ‘red’})
                sns.regplot(x=x_axis, y=y_axis,data = DataTable_df,scatter_kws={'s':18},ci=None,ax=ax,color=colorPallet[imo], label=vessel_name)
            elif Type=="2nd Degree Polynomial" or Type == 'Quad':
                sns.regplot(x=x_axis, y=y_axis,data = DataTable_df,order=2,scatter_kws={'s':18},ci=None,ax=ax,color=colorPallet[imo], label=vessel_name)
            elif Type=="3rd Degree Polynomial":
                sns.regplot(x=x_axis, y=y_axis,data = DataTable_df,order=3,scatter_kws={'s':18},ci=None,ax=ax,color=colorPallet[imo], label=vessel_name)

            plt.xlabel(x, fontsize= 15,fontweight="bold")
            plt.ylabel(y, fontsize= 15,fontweight="bold")#fontname="Times New Roman"
            plt.title(x+"  Vs  "+y, size=18,fontweight="bold")        

            for tick in ax.get_xticklabels():
                tick.set_fontweight('bold')

            for tick in ax.get_yticklabels():
                tick.set_fontweight('bold')

            legend = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))                

            ax.tick_params(axis='x', labelsize=12)
            ax.tick_params(axis='y', labelsize=12)
            plt.tight_layout()

            plt.savefig('./images/Data Monitoring- Relational Parameter-Single,Group,Multi.png', bbox_inches = 'tight')        
        else:
            for i in s['data']:
                imo = i
              
            DataTable_df = pd.DataFrame.from_dict(s['data'][imo])
            try:
                DataTable_df = DataTable_df[DataTable_df[x_axis] != 0]
            except:
                   pass  
            # vessel_name_single_None = DataTable_df[["vessel_name"]]
            vrs_data = DataTable_df[DataTable_df['type'] == 'VRS Data']
            ada_data = DataTable_df[DataTable_df['type'] == 'ADA Data']

            fig, ax = plt.subplots(figsize=(15, 7))

            if Type == "None":
                sns.scatterplot(x=x_axis, y=y_axis, data=ada_data, color="red", label="ADA Data", ax=ax)
                sns.scatterplot(x=x_axis, y=y_axis, data=vrs_data, color="green", label="VRS Data", ax=ax)
            elif Type == "Linear":
                sns.regplot(x=x_axis, y=y_axis, data=ada_data, color="red", scatter_kws={'s': 18}, ci=None, label="ADA Data", ax=ax)
                sns.regplot(x=x_axis, y=y_axis, data=vrs_data, color="green", scatter_kws={'s': 18}, ci=None, label="VRS Data", ax=ax)
            elif Type == "2nd Degree Polynomial" or Type == 'Quad':
                sns.regplot(x=x_axis, y=y_axis, data=ada_data, color="red", order=2, scatter_kws={'s': 18}, ci=None, label="ADA Data", ax=ax)
                sns.regplot(x=x_axis, y=y_axis, data=vrs_data, color="green", order=2, scatter_kws={'s': 18}, ci=None, label="VRS Data", ax=ax)
            elif Type == "3rd Degree Polynomial":
                sns.regplot(x=x_axis, y=y_axis, data=ada_data, color="red", order=3, scatter_kws={'s': 18}, ci=None, label="ADA Data", ax=ax)
                sns.regplot(x=x_axis, y=y_axis, data=vrs_data, color="green", order=3, scatter_kws={'s': 18}, ci=None, label="VRS Data", ax=ax)

            plt.xlabel(x_axis, fontsize=15, fontweight="bold")
            plt.ylabel(y_axis, fontsize=15, fontweight="bold")
            plt.title(f"{x_axis} Vs {y_axis}", size=18, fontweight="bold")

            for tick in ax.get_xticklabels():
                tick.set_fontweight('bold')

            for tick in ax.get_yticklabels():
                tick.set_fontweight('bold')

            legend = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            ax.tick_params(axis='x', labelsize=12)
            ax.tick_params(axis='y', labelsize=12)
            plt.tight_layout()
            plt.savefig('./images/Data Monitoring- Relational Parameter-Single,Group,Multi.png', bbox_inches = 'tight') 
            
     
        def simple_table(spacing=2.5):
            pdf = FPDF()
            pdf.add_page()
        
        #Page Number
            pdf.set_y(265)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")
        
        #Logo
            # pdf.image(oceanix_logo_path,20,30,w=30)
            pdf.image(msc_logo_path,160,24,w=30)
        
            #Main Heading
            pdf.set_font('Arial', 'B', 16)
            pdf.set_xy(50,52)
            pdf.set_text_color(25,47,133)
        
            pdf.cell(115, 8, None_Heading,align='C')
            pdf.set_line_width(1)
            pdf.line(10, 62, 199, 62)#(x_start, y_start, x_end, y_end)
        
        #Vessel Name
            pdf.set_font('Arial', '', 13)
            pdf.set_text_color(0,0,0)
            pdf.set_xy(10,66)
            pdf.multi_cell(90, 7,"Vessel Name  : ",align='L')
            pdf.set_xy(52,66)
            pdf.multi_cell(90, 7,vessel_name,align='L') 
        
        #Monitoring Period
            pdf.set_xy(10,75)
            pdf.multi_cell(90, 7,"Monitoring Period  : ",align='L')
            pdf.set_xy(52,75)
            pdf.multi_cell(90, 7,period,align='L') 

        #Type
            pdf.set_xy(10,84)
            pdf.multi_cell(90, 7,"Type  : ",align='L')
            pdf.set_xy(52,84)
            pdf.multi_cell(90, 7,Type,align='L')
        
        #X axis
            pdf.set_xy(10,93)
            pdf.multi_cell(90, 7,"X-axis  : ",align='L')
            pdf.set_xy(52,93)
            pdf.multi_cell(90, 7,x,align='L')
        
        #Y axis
            pdf.set_xy(10,100)
            pdf.multi_cell(90, 7,"Y-axis  : ",align='L')
            pdf.set_xy(52,100)
            pdf.multi_cell(90, 7,y,align='L')
        
        
            pdf.set_line_width(0)
            pdf.line(10, 107, 220, 107)  # Adjust the Y-coordinate to be after the Y-axis text
        
        #Setting Data Monitoring - Relationa Parameters
            pdf.image("./images/Data Monitoring- Relational Parameter-Single,Group,Multi.png",18.5,113,w=170,h=100) 
    #------------------------------------------------------------------------------------------------------------------------------#
            pdf.output('./documents/'+pdf_name,'F')
     
        simple_table()     
        
        
    elif report_type=="teu" or report_type == 'class':
        pdf_name = vessel_name + "DR_Group_Vessel.pdf"

        # url_Group="https://msc.oceanix.cloud/api/sysapi/api/v1/datamonitoring/data=vrs/group=group/mindate=2021-01-01/maxdate=2022-02-01/period=D/imo=1/voycond=Both/status=At%20Sea/draftmin=5/draftmax=30/sogmin=5/sogmax=35/sfocmin=50/sfocmax=350/seastatemin=0/seastatemax=9/mcrmin=500/mcrmax=100000/slipmin=-30/slipmax=30/stwmin=5/stwmax=35/steamingtimemin=1/steamingtimemax=26/rpmmin=-500/rpmmax=500/loadmin=10/loadmax=100"
        # s=requests.get(url_Group , headers =  headers).json()
    #.....................................................IMO & COLOR setting......................................................#
        imo_lst = [i for i in s['data']]
        len_imo_lst = len(imo_lst)

        count = 0
        j = 0
        if Type == 'None':
            fig, ax = plt.subplots(figsize=(15, 7))
            
            for i in s['data']:
                # Skip 'regression_vrs' part if present in s['data']
                if i == 'regression_vrs':
                    continue
                clr = colorPallet.get(i, "#000000")  # Use default black color if IMO not in colorPallet
    
                data = pd.DataFrame.from_dict(s['data'][i])
                data = data[data[x_axis] != 0]
                sns.scatterplot(ax=ax, data=data, x=x_axis, y=y_axis, palette=[clr], hue="vessel_name")
                count = count + 1
                j = j + 1

        else:
            for i in s['data']:
                clr = colorPallet[i]

                fig, ax = plt.subplots(figsize=(15, 7))
                data = pd.DataFrame.from_dict(s['data'][i])
                data = data[data[x_axis] != 0]

                sns.scatterplot(ax=ax, data=data, x=x_axis, y=y_axis, palette=[clr], hue="vessel_name")

                if Type == 'Linear':
                    sns.regplot(ax=ax, data=data, x=x_axis, y=y_axis, scatter_kws={'s': 20}, ci=None, color=clr)
                elif Type == '2nd Degree Polynomial' or Type == 'Quad':
                    sns.regplot(ax=ax, data=data, x=x_axis, y=y_axis, scatter_kws={'s': 20}, ci=None, order=2, color=clr)
                elif Type == '3rd Degree Polynomial':
                    sns.regplot(ax=ax, data=data, x=x_axis, y=y_axis, scatter_kws={'s': 20}, ci=None, order=3, color=clr)                                
            
        plt.xlabel(x, fontsize= 15,fontweight="bold")
        plt.ylabel(y, fontsize= 15,fontweight="bold")#fontname="Times New Roman"
        plt.title(x+"  Vs  "+y, size=18,fontweight="bold")       

        for tick in ax.get_xticklabels():
            tick.set_fontweight('bold')

        for tick in ax.get_yticklabels():
            tick.set_fontweight('bold')

        legend = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))                
                    
        ax.tick_params(axis='x', labelsize=12)
        ax.tick_params(axis='y', labelsize=12)
        plt.tight_layout()


        plt.savefig('images/Data Monitoring- Relational Parameter-Single,Group,Multi.png' , bbox_inches ='tight')       

        def simple_table(spacing=2.5):
            pdf = FPDF()
            pdf.add_page()
        
            #Page Number
            pdf.set_y(265)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")
        
            #Logo
            # pdf.image(oceanix_logo_path,20,30,w=30)
            pdf.image(msc_logo_path,160,24,w=30)
        
            #Main Heading
            pdf.set_font('Arial', 'B', 16)
            pdf.set_xy(50,52)
            pdf.set_text_color(25,47,133)
        
            pdf.cell(115, 8, None_Heading,align='C')
            pdf.set_line_width(1)
            pdf.line(10, 62, 199, 62)#(x_start, y_start, x_end, y_end)
        
            #Vessel Name
            pdf.set_font('Arial', '', 13)
            pdf.set_text_color(0,0,0)
            pdf.set_xy(10,66)
            if report_type=="teu" :
                pdf.multi_cell(90, 7,"TEU Value  : ",align='L')

            else:
                pdf.multi_cell(90, 7,"Class Name  : ",align='L')
            pdf.set_xy(52,66)
            pdf.multi_cell(90, 7,Group_Number,align='L') 
        
            #Monitoring Period
            pdf.set_xy(10,75)
            pdf.multi_cell(90, 7,"Monitoring Period  : ",align='L')
            pdf.set_xy(52,75)
            pdf.multi_cell(90, 7,period,align='L') 

            #Type
            pdf.set_xy(10,84)
            pdf.multi_cell(90, 7,"Type  : ",align='L')
            pdf.set_xy(52,84)
            pdf.multi_cell(90, 7,Type,align='L')
        
            #X axis
            pdf.set_xy(10,93)
            pdf.multi_cell(90, 7,"X-axis  : ",align='L')
            pdf.set_xy(52,93)
            pdf.multi_cell(90, 7,x,align='L')
        
            #Y axis
            pdf.set_xy(10,103)
            pdf.multi_cell(90, 7,"Y-axis  : ",align='L')
            pdf.set_xy(52,103)
            pdf.multi_cell(90, 7,y,align='L')
        
        
            pdf.set_line_width(0)
            pdf.line(10, 102, 199, 102)
        
            #Setting Data Monitoring - Relationa Parameters
            
            pdf.image("./images/Data Monitoring- Relational Parameter-Single,Group,Multi.png",10,113,w=190,h=100) 
    #------------------------------------------------------------------------------------------------------------------------------#
            pdf.output('./documents/'+pdf_name,'F')
   
        simple_table()     
                

            
    elif report_type=="multi":
        pdf_name = vessel_name + "DR_Multi_Vessel.pdf"
       
        # url_multi="https://msc.oceanix.cloud/api/sysapi/api/v1/datamonitoring/data=vrs/group=multi/mindate=2021-01-01/maxdate=2022-02-01/period=D/imo=9228320,9626302,9345908,9360946,9689897,9610640/voycond=Both/status=At Sea/draftmin=5/draftmax=30/sogmin=5/sogmax=35/sfocmin=50/sfocmax=350/seastatemin=0/seastatemax=9/mcrmin=500/mcrmax=100000/slipmin=-30/slipmax=30/stwmin=5/stwmax=35/steamingtimemin=1/steamingtimemax=26/rpmmin=-500/rpmmax=500/loadmin=10/loadmax=100"   
        # s=requests.get(url_multi , headers =  headers).json()
    #.....................................................IMO & COLOR setting......................................................#
        imo_lst = [i for i in s['data']]
        len_imo_lst = len(imo_lst)
        
        if Type == 'None':
            fig, ax = plt.subplots(figsize=(15, 7))
            for i in s['data']:
                # Skip 'regression_vrs' part if present in s['data']
                if i == 'regression_vrs':
                    continue
                clr = colorPallet.get(i, "#000000")  # Use default black color if IMO not in colorPallet
                # print("=======================",s['data'][i])
                # print("++++++++++++++++++++++",x_axis)
                data = pd.DataFrame.from_dict(s['data'][i])
                try:
                    data = data[data[x_axis] != 0]
                except:
                    continue    
                sns.scatterplot(ax=ax, data=data, x=x_axis, y=y_axis, palette=[clr], hue="vessel_name")
                print(clr)
        else:
            fig, ax = plt.subplots(figsize=(15, 7))
            for i in s['data']:
                # Skip 'regression_vrs' part if present in s['data']
                if i == 'regression_vrs':
                    continue
    
                clr = colorPallet.get(i, "#000000")  # Use default black color if IMO not in colorPallet
 
                data = pd.DataFrame.from_dict(s['data'][i])
                data = data[data[x_axis] != 0]
                sns.scatterplot(ax=ax, data=data, x=x_axis, y=y_axis, palette=[clr], hue="vessel_name")

                if Type == 'Linear':
                    sns.regplot(ax=ax, data=data, x=x_axis, y=y_axis, scatter_kws={'s': 20}, ci=None,color=clr)
                elif Type == '2nd Degree Polynomial' or Type == 'Quad':
                    sns.regplot(ax=ax, data=data, x=x_axis, y=y_axis, scatter_kws={'s': 20}, ci=None, order=2,color=clr)
                elif Type == '3rd Degree Polynomial':
                    sns.regplot(ax=ax, data=data, x=x_axis, y=y_axis, scatter_kws={'s': 20}, ci=None, order=3,color=clr)                  
                              
        plt.xlabel(x, fontsize= 15,fontweight="bold")
        plt.ylabel(y, fontsize= 15,fontweight="bold")#fontname="Times New Roman"
        plt.title(x+"  Vs  "+y, size=18,fontweight="bold") 
        plt.tight_layout()       
        plt.savefig('images/Data Monitoring- Relational Parameter-Single,Group,Multi.png',bbox_inches = "tight")        

        def simple_table(spacing=2.5):
            pdf = FPDF()
            pdf.add_page()
        
            #Page Number
            pdf.set_y(265)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")
        
        #Logo
            # pdf.image(oceanix_logo_path,20,30,w=30)
            pdf.image(msc_logo_path,160,24,w=30)
        
            #Main Heading
            pdf.set_font('Arial', 'B', 16)
            pdf.set_xy(50,52)
            pdf.set_text_color(25,47,133)
        
            pdf.cell(115, 8, None_Heading,align='C')
            pdf.set_line_width(1)
            pdf.line(10, 62, 199, 62)#(x_start, y_start, x_end, y_end)
            
            #Vessel Name
            pdf.set_font('Arial', '', 13)
            pdf.set_text_color(0,0,0)
            pdf.set_xy(10,66)
            pdf.multi_cell(90, 7,"Vessel Names  : ",align='L')
            pdf.set_xy(52,66)
            pdf.set_font('Arial', '', 11.5)
            pdf.multi_cell(140, 7,vessel_name,align='L') 
        
        #Monitoring Period
            pdf.set_font('Arial', '', 13)
            pdf.set_xy(10,78)
            pdf.multi_cell(90, 7,"Monitoring Period  : ",align='L')
            pdf.set_xy(52,78)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(90, 7,period,align='L') 

        #X axis
            pdf.set_xy(10,86)
            pdf.set_font('Arial', '', 13)
            pdf.multi_cell(90, 7,"Type  : ",align='L')
            pdf.set_xy(52,86)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(90, 7,Type,align='L')
        
        #X axis
            pdf.set_xy(10,95)
            pdf.set_font('Arial', '', 13)
            pdf.multi_cell(90, 7,"X-axis  : ",align='L')
            pdf.set_xy(52,95)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(90, 7,x,align='L')
        
        #Y axis
            pdf.set_xy(10,104)
            pdf.set_font('Arial', '', 13)
            pdf.multi_cell(90, 7,"Y-axis  : ",align='L')
            pdf.set_xy(52,104)
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(90, 7,y,align='L')
        
        
            pdf.set_line_width(0)
            pdf.line(10, 104, 199, 104)
        
            #Setting Data Monitoring - Relationa Parameters
            pdf.image("./images/Data Monitoring- Relational Parameter-Single,Group,Multi.png",18.5,113,w=170,h=100) 
    #------------------------------------------------------------------------------------------------------------------------------#
            pdf.output('./documents/'+pdf_name,'F')
        
        simple_table() 

    return FileResponse(path = './documents/'+pdf_name,filename='datamonitoring_r.pdf')
    

@router.post("/api/v1/pdf/voyagecal/performancecurve")
async def index(info : Request , vessel_name: str = None , date_range : str = None, sea_state : str = None, draft : str = None):
    s = await info.json()
  
    if not s:
        return {'data':[]}
    try:
        test_data = s['data']

    except:
        return {'data':[]}

    #______________Input Parameter__________________
    # vessel_name="msc Singapore"
    # date_range= "From 01 Jul 2017 To 31 Dec 2017"
    # sea_state="3" #Seastate
    # draft="10" #draft

    #____________________________
    # token ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6IjUyODNkNWY0LTZhZDktNDNkMC05OWI4LTJiNWVlNGEzYzEwMiIsImlhdCI6MTY2OTc4MDc3OCwiZXhwIjoxNjY5ODY3MTc4fQ.eL_Ye4sdnRDj4f7TlGvCp22cGx9QtPvCMw7zNqIaIT0"
    # headers = {'Authorization': "Bearer {}".format(token)}
    # URL="http://192.168.54.79:8585/api/v1/vc/eta_foc/pc/9648075?date=From%20%2021%20Dec%202016%20%20To%20%2019%20Jun%202017&type=Noon&seastate=3&draft=10"
    # s=requests.get(URL , headers =  headers).json()
    s
    #____________________________

    fo = pd.DataFrame.from_dict(s['data']['foTable'])
    #fo = fo[  [ col for col in fo.columns if col != 'Speed/Draft' ]+['Speed/Draft']  ]

    power= pd.DataFrame.from_dict(s['data']['powerTable'])
    #power = power[  [ col for col in power.columns if col != 'Speed/Draft' ]+['Speed/Draft']  ]
    fo_sea= pd.DataFrame.from_dict(s['data']['seaStateTable'])
   # fo_sea = fo_sea[  [ col for col in fo_sea.columns if col != 'Speed/Draft' ]+['Speed/Draft']  ]

   #___________________Tables_______________________
    fo_Chart = pd.DataFrame.from_dict(s['data']['foChart'])

    power_Chart = pd.DataFrame.from_dict(s['data']['powerChart'])
    fo_sea_Chart = pd.DataFrame.from_dict(s['data']['seaStateChart'])


    #Specifying colors for 3 Charts based on frequncy of values

 

    fo_color = (fo.shape[1])-1
    power_color=(power.shape[1])-1
    fo_sea_color = (fo_sea.shape[1])-1

    

    # color_lst = ['blue','yellow','red','violet','green','cyan','pink','gray','orange','purple','indigo','magenta']
    color_lst = ['brown', 'darkviolet', 'red', 'green', 'orange', 'blue', 'yellow', 'cyan', 'pink', 'gray', 'olive', 'purple', 'indigo', 'magenta', 'beige', 'black', 'teal', 'maroon', 'navy', 'turquoise', 'salmon', 'gold', 'silver', 'coral', 'violet', 'lime', 'orchid', 'plum', 'khaki']

    new_color_lst1 = []
    new_color_lst2 = []
    new_color_lst3 = []

    

    for z in range (0,fo_color):
        color_sel = color_lst[z]
        new_color_lst1.append(color_sel)


    


    for z in range (0,power_color):
        color_sel = color_lst[z]
        new_color_lst2.append(color_sel)
        

    

    for z in range (0,fo_sea_color):
        color_sel = color_lst[z]
        new_color_lst3.append(color_sel)
    

    fo_column_head = list(fo.columns.values)
    fo_object =fo.astype(str)
    power_column_head = list(power.columns.values)
    power_object =power.astype(str)
    fo_sea_column_head = list(fo_sea.columns.values)
    fo_sea_object =fo_sea.astype(str)

    #_______________________Graph________________________________

    #--------------- Graph 1-----------------#

    fig_1, axes = plt.subplots(1, 1)
    sns.lineplot(data=fo_Chart, x='speed', y='fo_consumption', marker = 'o',markersize = 5,lw=1,hue='category',palette=new_color_lst1)
    plt.title('Speed FO/24 Hrs Curve',fontweight="bold",size=10)
    axes.set_xlabel('Speed (knots)',fontweight="bold",size=8)
    axes.set_ylabel('FO/24 Hrs (tonne)',fontweight="bold",size=8)
    axes.legend_.set_title(None)


    fig_1.savefig('images/fo_1_sb.png')
    plt.clf()


    #--------------- Graph 2 -----------------#
    
    fig_2, axes = plt.subplots(1, 1)
    sns.lineplot(data=power_Chart, x='speed', y='fo_consumption', marker = 'o',markersize = 5,lw=1,hue='category',palette=new_color_lst2)
    plt.title('Speed Power Curve',fontweight="bold",size=10)
    axes.set_xlabel('Speed (knots)',fontweight="bold",size=8)
    axes.set_ylabel('Power (KW)',fontweight="bold",size=8)
    axes.legend_.set_title(None)


    fig_2.savefig('images/power_performance_sb.png')

    plt.clf()


    #--------------- Graph 3 -----------------#
    fig_3, axes = plt.subplots(1, 1)
    plt.title('Speed FO/24 hrs for Sea State',fontweight="bold",size=10)
    sns.lineplot(data=fo_sea_Chart, x='speed', y='fo_consumption', marker = 'o',markersize = 5,lw=1,hue='category',palette=new_color_lst3)
    axes.set_xlabel('Speed (knots)',fontweight="bold",size=8)
    axes.set_ylabel('FO/24 Hrs (tonne)',fontweight="bold",size=8)
    plt.setp(axes.get_legend().get_title(), fontsize='5')

    

    axes.legend_.set_title(None)

    fig_3.savefig('images/fo_seastate_sb.png')

    plt.clf()

    #____________________PDF_____________________

    from fpdf import FPDF
    def performance_curve_pdf(spacing=3):

        #report_prepared_date= "11-10-2022"

        pdf = FPDF()
        #***********************************************  page 1 **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        pdf.image(oceanix_logo_path,15,15,w=35)
        pdf.image(msc_logo_path,160,8,w=35)

    #Cell postion from left side
        pdf.set_xy(65,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(170, 60, 'performance CURVE',ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)#(x_start, y_start, x_end, y_end)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)
        #pdf.multi_cell(80,14.5,"Report Date :"+" "+ report_prepared_date, align='R')

        
        pdf.cell(10, 2, "Vessel Name :"+" "+vessel_name,ln=True)
        pdf.cell(10, 12,"Date :"+" "+ date_range,ln=True)
        
        pdf.line(10, 70, 190, 70)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'FO Calculator Table',ln=True,align='C')
        pdf.line(10, 85, 190, 85)
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        pdf.set_font('Arial', "",14)
        pdf.cell(10, 12,"Sea State :"+" "+ sea_state,ln=True)
        
        spacing=3
        fo_head = [fo_column_head]
        fo_values = fo_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /10
        row_height = pdf.font_size
        for row in fo_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /10
        row_height = pdf.font_size
        for row in fo_values:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        
        pdf.image("./images/fo_1_sb.png",15,180,w=160,h=100) 
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")  
    #***********************************************  page 2 **********************************************************#
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(70, 18, 'Power Calculaor Table',ln=True,align='C')
        
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        
        
        spacing=3
        power_head = [power_column_head]
        power_values = power_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /10
        row_height = pdf.font_size
        for row in power_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /10
        row_height = pdf.font_size
        for row in power_values:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.image("./images/power_performance_sb.png",15,130,w=180,h=130)
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")  
        
        
        
        
        #***********************************************  page3 **********************************************************#
        pdf.add_page() 
        
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(83, 18, 'FO calculator for Sea State',ln=True,align='C')
        pdf.set_text_color(0,0,0)
        pdf.set_font('Arial', "",14)
        pdf.cell(9, 12,"Draft Selected :"+" "+ draft,ln=True) 
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        
        
        spacing=3
        fo_sea_head = [fo_sea_column_head]
        fo_sea_values = fo_sea_object.values.tolist()
        pdf.set_font("Arial",'B', size=6.8)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /10.6
        row_height = pdf.font_size
        for row in fo_sea_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /10.6
        row_height = pdf.font_size
        for row in fo_sea_values:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        
        
        pdf.image("./images/fo_seastate_sb.png",15,130,w=180,h=130)
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")  
            
    
        pdf.output('./documents/performance_curve_2.pdf','F')

    performance_curve_pdf()   
    return FileResponse(path = './documents/performance_curve_2.pdf',filename='performance_curve_2.pdf')
    
    





@router.post("/api/v1/pdf/environmental")
async def index( info : Request,vessel_name : str = None , date_start : str = None , date_end:str = None,pid:str = None, vcode : str = None):

    s = await info.json()
    if not s:
        return {'data':[]}
    a=vessel_name
    # b= "08-02-2021 to 05-10-2021"
    b = date_start + " to " + date_end
    c= pid   #Passage id
    d= vcode   #voyage Code
    #________________________

    

    # url="http://localhost:9111/api/v1/envm/eeoi/vwr/9648075?pid=56L&vcode=Cristobal-PUERTO%20SANDINO&date1=2020-01-01&date2=2022-11-15"
    # s=requests.get(url).json()

    # return s

    

    fo_cnsptn_details = pd.DataFrame.from_dict(s['table1'])
    fo_cnsptn_details = fo_cnsptn_details[['index','Fuel(HS)', 'Fuel (LS)', 'Fuel (MDO)', 'Fuel (MGO)', "Fuel (MGO)LS" ]]
    reported_data = pd.DataFrame.from_dict(s['reported_data'])

    reported_data= reported_data[["index","Value",'Units']]
    voy_condtn = pd.DataFrame.from_dict(s['pie_chart'])
    Char_data = pd.DataFrame.from_dict(s['EECHARTDATA'])

    fo_cnsptn_details_object =fo_cnsptn_details.astype(str)

    reported_data_object =reported_data.astype(str)


    voy_condtn["voyage_no"] = pd.to_numeric(voy_condtn["voyage_no"], errors='coerce', downcast='integer')
    color =  [ '#0066CC',"#AC2EB5","#663300","#F1F50C"]

    #--------------- Voy cond info -----------------#
    max_info = voy_condtn.groupby('voy_condition')['voyage_no'].max().reset_index()

    info = ""
    for index, row in max_info.iterrows():
        info += f"The voyage condition of {row['voyage_no']}: {row['voy_condition']}\n"

    print(info)

    #--------------- Graph 1 -----------------#

    plt.figure(figsize=(13, 6))
    fig_voy = sns.barplot(data=Char_data, x='date', y='eeoi', palette=['#EB222D'])
    ax1 = fig_voy

    fig_voy.grid(False)
    fig_voy.set_xlabel('Date', fontweight='bold', size=12)
    fig_voy.set_ylabel('Energy efficiency (grams/tonne-mile)', fontweight='bold', size=10)
    for p in ax1.patches:
        fig_voy.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', 
                        xytext=(0, 5), 
                        textcoords='offset points',
                        fontsize=8,
                        color='black')
    plt.xticks(rotation=45, ha='right')
    plt.savefig('./images/eeoi_date_sb.png', bbox_inches='tight')
    ##plt.clf()
    #--------------- Graph 2 -----------------#

    plt.figure(figsize=(13, 6))
    fig_voy = sns.barplot(data=Char_data, x='date', y='eeoit', palette=['#EB222D'])
    ax1 = fig_voy
    fig_voy.grid(False)
    fig_voy.set_xlabel('Date', fontweight='bold', size=12)
    fig_voy.set_ylabel('EEEOIT (grams/TEU-mile)', fontweight='bold', size=10)
    for p in ax1.patches:
        fig_voy.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', 
                        xytext=(0, 5), 
                        textcoords='offset points',
                        fontsize=8,
                        color='black')

    plt.xticks(rotation=45, ha='right')
    plt.savefig('./images/eeoit_date_sb.png', bbox_inches='tight')
    ##plt.clf()


    #--------------- Graph 3 -----------------#

    plt.figure(figsize=(12, 6))
    fig_voy = sns.barplot(data=Char_data, x='date', y='total_co_2', palette=['#EF521D'])
    ax2 = fig_voy
    fig_voy.grid(False)
    fig_voy.set_xlabel('Date', fontweight='bold', size=12)
    fig_voy.set_ylabel('CO2 (tonnes)', fontweight='bold', size=10)
    for p in ax2.patches:
        fig_voy.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', 
                        xytext=(0, 5), 
                        textcoords='offset points',
                        fontsize=8,
                        color='black')

    plt.xticks(rotation=45, ha='right')
    plt.savefig('./images/tot_co2_date_sb.png', bbox_inches='tight')
    ##plt.clf()


    #--------------- Graph 4 -----------------#

    plt.figure(figsize=(12, 6))
    fig_voy = sns.barplot(data=Char_data, x='date', y='foc', palette=["#EF8717"])
    ax1 = fig_voy
    fig_voy.grid(False)
    fig_voy.set_xlabel('Date', fontweight='bold', size=11)
    fig_voy.set_ylabel('FO (tonnes)', fontweight='bold', size=10)
    for p in ax1.patches:
        fig_voy.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', 
                        xytext=(0, 5), 
                        textcoords='offset points',
                        fontsize=8,
                        color='black')

    plt.xticks(rotation=45, ha='right')
    plt.savefig('./images/FO_consptn_date_sb.png', bbox_inches='tight')
    ##plt.clf()

   

    #_______________________PDF Creation___________
    spacing=3

    #report_prepared_date= "11-10-2022"

    pdf = FPDF()
    #*********************************************** 1 page **********************************************************#
    pdf.add_page()
    # pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
    pdf.set_font('Arial', 'B',size= 18)

    # pdf.set_font('fonts/arial.ttf', '', 18)

    
    # pdf.image(msc_logo_path,160,8,w=35)



    #Cell postion from left side
    pdf.set_xy(65,15)
    pdf.set_text_color(25,47,133)
    pdf.cell(170, 60, 'VOYAGE WISE REPORT',ln=True)
    pdf.set_text_color(0,0,0)
    pdf.set_line_width(1)
    pdf.line(10, 50, 190, 50)#(x_start, y_start, x_end, y_end)
    pdf.set_line_width(0.2)
    # pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
    pdf.set_font('Arial', '',size= 12)
    # pdf.set_font('fonts/arial.ttf', "",12)
    pdf.set_xy(10,60)
    #pdf.multi_cell(80,14.5,"Report Date :"+" "+ report_prepared_date, align='R')


    pdf.cell(10, 2, "Vessel Name :"+" "+a,ln=True)
    pdf.cell(10, 12,"Date Range:"+" "+ b,ln=True)
    pdf.cell(10, 2,"Voyage Code:"+" "+ d,ln=True)
    pdf.cell(10, 12, "Passage ID :"+" "+c,ln=True)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(25,47,133)
    #pdf.cell(180, 18, 'Voyage Condition',ln=True,align='C')
    #pdf.line(10, 100, 190, 100)
    pdf.set_line_width(0)
    # pdf.set_text_color(0,0,0)

    pdf.set_x(50)

    pdf.cell(50, 50,info,ln=True)
    pdf.set_text_color(0,0,0)

    pdf.line(10, 85, 190, 85)

    # pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
    pdf.set_font('Arial', 'B',size= 18)
    pdf.set_text_color(25,47,133)
    pdf.set_xy(14,150)
    pdf.multi_cell(180, 5, 'Fuel Consumption Details',align='C')
    pdf.set_text_color(0,0,0)

    pdf.set_xy(10,160)
    spacing=3
    fo_cnsptn_details_head = [['Fuel Consumption Details','Fuel(HS)', 'Fuel (LS)', 'Fuel (MDO)', 'Fuel (MGO)', "Fuel (MGO)LS" ]]
    fo_cnsptn_details_values = fo_cnsptn_details_object.values.tolist()
    # pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
    pdf.set_font('Arial', 'B',size=7.0)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /7
    row_height = pdf.font_size
    for row in fo_cnsptn_details_head:
        pdf.set_text_color(255,255,255)
        pdf.set_fill_color(21,55,188)
        for item in row:
            pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
        pdf.ln(row_height*spacing)


    #pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
    pdf.set_font('Arial', '',size= 4.9)

    pdf.set_text_color(0,0,0)
    col_width = pdf.w /7

    row_height = (pdf.font_size)+.3
    for row in fo_cnsptn_details_values:
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                    txt=item, border=1)
        pdf.ln(row_height*spacing)

    #Page Number

    pdf.set_y(273)
    # pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
    pdf.set_font('Arial', 'I',size= 8)
    pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")      

    #*********************************************** Page 2 **********************************************************#
    pdf.add_page()
    spacing=3
    reported_data_head = [["Parameter","Value","Units"]]
    reported_data_values = reported_data_object.values.tolist()
    pdf.set_font("Arial",'B', size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /3.5
    row_height = pdf.font_size
    for row in reported_data_head:
        pdf.set_text_color(255,255,255)
        pdf.set_fill_color(21,55,188)
        for item in row:
            pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
        pdf.ln(row_height*spacing)
    pdf.set_font("Arial", size=6.5)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /3.5
    row_height = pdf.font_size
    for row in reported_data_values:
        for item in row:
            pdf.cell(col_width, row_height*spacing,txt=item, border=1)
        pdf.ln(row_height*spacing)
        
    #Page Number    
    pdf.set_y(273)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

    #*********************************************** Page 3 **********************************************************#
    pdf.add_page()
    pdf.set_text_color(25,47,133)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_xy(10,15)
    pdf.multi_cell(180, 18, 'Date vs EEOI',align='C')
    pdf.set_text_color(0,0,0)
    if (Char_data["eeoi"].sum())==0:
        pdf.set_font('Arial', 'B', 14)
        pdf.multi_cell(130, 35,"No data avialable",align='L')
    else:
        #pdf.set_xy(10,115)
        pdf.image("./images/eeoi_date_sb.png",15,30,w=180,h=120)

    pdf.set_text_color(25,47,133)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_xy(10,155)
    pdf.multi_cell(180, 18, 'Date vs EEOI (TEU)',align='C')
    pdf.set_text_color(0,0,0)
    if (Char_data["eeoit"].sum())==0:
        pdf.set_font('Arial', 'B', 14)
        pdf.multi_cell(130, 35,"No data avialable",align='L')
    else:
        #pdf.set_xy(10,115)
        pdf.image("./images/eeoit_date_sb.png",15,170,w=180,h=120)
    #Page Number    
    pdf.set_y(273)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


    #*********************************************** Page 4 **********************************************************#
    pdf.add_page()
    pdf.set_text_color(25,47,133)
    #pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
    pdf.set_font('Arial', 'B',size= 18)
    pdf.set_xy(10,15)
    pdf.multi_cell(180, 18, 'Date vs CO2 Emission',align='C')
    pdf.set_text_color(0,0,0)

    if (Char_data["total_co_2"].sum())==0:
    # pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
        pdf.set_font('Arial', 'B',size= 14)
        pdf.multi_cell(130, 35,"No data avialable",align='L')
    else: 
        #pdf.set_xy(10,115)
        pdf.image("./images/tot_co2_date_sb.png",15,30,w=180,h=120)


    pdf.set_text_color(25,47,133)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_xy(10,155)
    pdf.multi_cell(180, 18, 'Date vs FO Consumption ',align='C')
    pdf.set_text_color(0,0,0)
    if (Char_data["foc"].sum())==0:
        pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
        pdf.set_font('Arial', 'B',size= 14)
        pdf.multi_cell(130, 35,"No data avialable",align='L')
    else: 

        pdf.image("./images/FO_consptn_date_sb.png",15,170,w=180,h=120)


    #Page Number
    pdf.set_y(273)
    pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
    pdf.set_font('Arial', 'I',size= 8)
    pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")    

        
    pdf_name ='./documents/'+ vessel_name+'_'+b+'environmental.pdf'
    pdf.output(pdf_name,'F')
        
 
    return FileResponse(path = pdf_name,filename=pdf_name)
    
    



# @router.post('/me_report')
# @router.post('/api/v1/pdf/me')
# async def index(data:Request):
#     from matplotlib import pyplot as plt
#     s = await data.json()

#     # return data
#     if not os.path.exists('images'):
#         os.makedirs('images')


#     time = datetime.now()
#     # url="http://localhost:9090/data"

#     # s=requests.get(url).json()
#     r = pd.DataFrame.from_dict(s['Results_tab']['Table_2'])
#     r = r.astype(str)

#     def data1_fn():
#         data1 = pd.DataFrame.from_dict(s['Results_tab']['table_1'])
#         data1 = data1.replace('[ ' ' ]','')
#         data1 = data1.astype(str)

#         return data1

#     def data2_fn():
#         print(r)
#         data2 = r[['Title', 'Kind_of_Graph', 'Shop_trial', 'Measured_value','Deviation','status']]
#         return data2

#     def data3_4_fn():
#         data3 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_chart_1'][0]['scatter_1'])
#         data3.rename(columns = {'x':'Engine speed scatter'}, inplace = True)
#         data3.rename(columns = {'y':'Engine load scatter'}, inplace = True)
#         data3.rename(columns = {'category':'category scatter'}, inplace = True)

#         data4 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_chart_1'][0]['scatter_2'])
#         data4.rename(columns = {'x':'Engine speed curve'}, inplace = True)
#         data4.rename(columns = {'y':'Engine load curve'}, inplace = True)
#         lst_category = data4['category'].unique()
        


#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.scatterplot(x="Engine speed scatter", y="Engine load scatter", data=data3,legend='auto',hue='category scatter',s=80)
#         for i in lst_category:
#             df = data4[data4['category']==i]
#             plt.plot(df['Engine speed curve'], df['Engine load curve'],marker = 'o',markersize = 10,label = i)

#         plt.xlabel('Engine Speed (rpm)',fontweight="bold",size=16)
#         plt.ylabel('Engine Load (%)',fontweight="bold",size=16)
#         plt.title('Load Diagram',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.legend(title=None)
#         plt.savefig('./images/loaddiagram.png')

#     def data5_fn():

#         data5 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_chart_2'])
#         data5['date_duplicate'] = data5.loc[:, 'date']
#         data5['date'] = data5['date'].astype("datetime64[ns]")
#         data5 = data5.sort_values(by='date')
#         data5['Month_name'] = pd.to_datetime(data5['date']).apply(lambda x:x.strftime("%B"))
#         data5['Year'] = pd.to_datetime(data5['date']).apply(lambda x:x.strftime("%Y"))
#         data5['Month_name_slice'] = data5['Month_name'].str.slice(0,3)
#         data5['month_year'] = data5['Month_name_slice'] + ' ' + data5['Year']
#         data5 = data5.sort_values(by='date')

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"

#         plt.figure(figsize=(10,5))
#         ax = sns.lineplot( x='month_year', y='deviation', data=data5,marker = 'o',markersize = 10)
#         plt.xlabel('Month',fontweight="bold",size=16)
#         plt.ylabel('Torque Rich Index',fontweight="bold",size=16)
#         plt.title('Torque Rich Index',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#         ax.legend(title=None)
#         plt.savefig('./images/torque_rich_index.png')

#     def data6_fn():

#         # data6 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_table_1'])
#         data6_a = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_table_1'])
#         data6=data6_a[["dates","historicx","historicy"]]
#         data6.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#         data6.rename(columns = {'historicx':'Engine RPM'}, inplace = True)
#         data6.rename(columns = {'historicy':'Engine Load'}, inplace = True)
#         data6['Date of Measurment'] = data6['Date of Measurment'].astype('datetime64[ns]')
#         data6['Date of Measurment'] = data6['Date of Measurment'].astype(str)
#         data6 = data6.astype(str)
#         return data6


#     def data7_fn():
#         data7 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_1'][0]['scatter_1'])
#         data7.rename(columns = {'Engine_Speed':'Engine speed scatter'}, inplace = True)
#         data7.rename(columns = {'Tc_Speed':'Corrected T/C speed scatter'}, inplace = True)

#         data8 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_1'][0]['scatter_2'][0])
#         data8.rename(columns = {'Engine_Speed':'Engine speed curve'}, inplace = True)
#         data8.rename(columns = {'Tc_Speed':'Corrected T/C speed curve'}, inplace = True)

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.scatterplot(x="Engine speed scatter", y="Corrected T/C speed scatter", data=data7,legend='auto',hue='Date',s=80)
#         plt.plot(data8['Engine speed curve'], data8['Corrected T/C speed curve'],marker = 'o',markersize = 10,label = "Shoptrial Data",color = 'brown')
#         plt.xlabel('Engine Speed (rpm)',fontweight="bold",size=16)
#         plt.ylabel('Corrected T/C Speed (rpm)',fontweight="bold",size=16)
#         plt.title('T/C Speed Vs Engine Speed',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.legend(title=None)
#         plt.savefig('./images/engine_corrected_speed_daigram.png')



#     def data9_fn():
#         data9 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_2'])
#         data9['date_duplicate'] = data9.loc[:, 'date']
#         data9['date'] = data9['date'].astype("datetime64[ns]")
#         data9 = data9.sort_values(by='date')
#         data9['Month_name'] = pd.to_datetime(data9['date']).apply(lambda x:x.strftime("%B"))
#         data9['Year'] = pd.to_datetime(data9['date']).apply(lambda x:x.strftime("%Y"))
#         data9['Month_name_slice'] = data9['Month_name'].str.slice(0,3)
#         data9['month_year'] = data9['Month_name_slice'] + ' ' + data9['Year']

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.lineplot(  x='month_year', y='deviation', data=data9,marker = 'o',markersize = 10)
#         plt.xlabel('Month',fontweight="bold",size=16)
#         plt.ylabel('Deviation %',fontweight="bold",size=16)
#         plt.title('% deviation',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#         ax.legend(title=None)
#         plt.savefig('./images/deviation.png')


#     def data10_fn():
#         data10 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_table_1'])
#         data10.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#         data10.rename(columns = {'historicx':'Engine Speed'}, inplace = True)
#         data10.rename(columns = {'historicy':'T/C Speed'}, inplace = True)
#         data10['Date of Measurment'] = data10['Date of Measurment'].astype('datetime64[ns]')
#         data10 = data10.astype(str)

#         return data10



#     def data11_fn():
#         data11 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_table_2'])
#         data11.rename(columns = {'x':'Engine Speed'}, inplace = True)
#         data11.rename(columns = {'y':'T/C Speed'}, inplace = True)
#         data11 = data11.dropna()
#         data11 = data11.astype(str)
#         return data11


#     def data12_dn():
#         data12 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['scatter_1'])
#         data12.rename(columns = {'tc_speed':'Corrected T/C speed scatter'}, inplace = True)
#         data12.rename(columns = {'Pscav':'Corrected Pscav scatter'}, inplace = True)

#         data13 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['scatter_2'][0])
#         data13.rename(columns = {'tc_speed':'Corrected T/C curve'}, inplace = True)
#         data13.rename(columns = {'Pscav':'Corrected Pscav curve'}, inplace = True)

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.scatterplot(x="Corrected T/C speed scatter", y="Corrected Pscav scatter", data=data12,legend='auto',hue='Date',s=80)
#         plt.plot(data13['Corrected T/C curve'], data13['Corrected Pscav curve'],marker = 'o',markersize = 10,label = "Shoptrial Data",color = 'brown')
#         plt.xlabel('Corrected T/C Speed (rpm)',fontweight="bold",size=16)
#         plt.ylabel('Corrected Pscav (Bar)',fontweight="bold",size=16)
#         plt.title('Pscav Vs T/C Speed',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.legend(title=None)
#         plt.savefig('./images/pscav_tc_speed_daigram.png')

        

#     pscav_tc_speed_value = r.loc[r['Kind_of_Graph'] == 'Pscav Vs T/C Speed']['remarks'].item()



#     def data14_fn():
#         data14 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["pscav_vs_tc_chart_2"])
#         data14['date_duplicate'] = data14.loc[:, 'date']
#         data14['date'] = data14['date'].astype("datetime64[ns]")
#         data14 = data14.sort_values(by='date')
#         data14['Month_name'] = pd.to_datetime(data14['date']).apply(lambda x:x.strftime("%B"))
#         data14['Year'] = pd.to_datetime(data14['date']).apply(lambda x:x.strftime("%Y"))
#         data14['Month_name_slice'] = data14['Month_name'].str.slice(0,3)
#         data14['month_year'] = data14['Month_name_slice'] + ' ' + data14['Year']

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.lineplot( x='month_year', y='deviation', data=data14,marker = 'o',markersize = 10)
#         plt.xlabel('Month',fontweight="bold",size=16)
#         plt.ylabel('Deviation %',fontweight="bold",size=16)
#         plt.title('% deviation',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#         ax.legend(title=None)
#         plt.savefig('./images/deviation_pscav_tc.png')


#     def data15_fn():
#         data15 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_table_1'])
#         data15.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#         data15.rename(columns = {'historicx':'T/C Speed'}, inplace = True)
#         data15.rename(columns = {'historicy':'Pscav (Bar)'}, inplace = True)
#         data15['Date of Measurment'] = data15['Date of Measurment'].astype('datetime64[ns]')
#         data15 = data15.astype(str)

#         return data15




#     def data16_fn():
#         data16 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_table_2'])
#         data16.rename(columns = {'x':'T/C Speed'}, inplace = True)
#         data16.rename(columns = {'y':'Pscav(Bar)'}, inplace = True)
#         data16 = data16.dropna()
#         data16 = data16.astype(str)
#         return data16


#     def data17_fn():
#         data17 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_chart_1'][0]['scatter_1'])
#         data17.rename(columns = {'Pscav':'Corrected Pscav scatter'}, inplace = True)
#         data17.rename(columns = {'Press_drop':'Press drop at A/C scatter'}, inplace = True) 

#         data18 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['press_vs_pscav_chart_1'][0]['scatter_2'][0])
#         data18.rename(columns = {'Pscav':'Corrected Pscav curve'}, inplace = True)
#         data18.rename(columns = {'Press_drop':'Press drop at A/C curve'}, inplace = True)

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.scatterplot(x="Corrected Pscav scatter", y="Press drop at A/C scatter", data=data17,legend='auto',hue='Date',s=80)
#         plt.plot(data18['Corrected Pscav curve'], data18['Press drop at A/C curve'],marker = 'o',markersize = 10,label = "Shoptrial Data",color = 'brown')
#         plt.xlabel('Corrected Pscav (Bar)',fontweight="bold",size=16)
#         plt.ylabel('Press Drop at A/C (kPa)',fontweight="bold",size=16)
#         plt.title('Press Drop at A/C Vs Pscav',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.legend(title=None)
#         plt.savefig('./images/pscav_press_drop_daigram.png')

#     press_drop_pscav_value = r.loc[r['Kind_of_Graph'] == 'Press. drop at A/C Vs Pscav']['remarks'].item()




#     def data19_fn():
#         data19 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["press_vs_pscav_chart_2"])
#         data19['date_duplicate'] = data19.loc[:, 'date']
#         data19['date'] = data19['date'].astype("datetime64[ns]")
#         data19 = data19.sort_values(by='date')
#         data19['Month_name'] = pd.to_datetime(data19['date']).apply(lambda x:x.strftime("%B"))
#         data19['Year'] = pd.to_datetime(data19['date']).apply(lambda x:x.strftime("%Y"))
#         data19['Month_name_slice'] = data19['Month_name'].str.slice(0,3)
#         data19['month_year'] = data19['Month_name_slice'] + ' ' + data19['Year']

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.lineplot( x='month_year', y='deviation', data=data19,marker = 'o',markersize = 10)
#         plt.xlabel('Month',fontweight="bold",size=16)
#         plt.ylabel('Deviation %',fontweight="bold",size=16)
#         plt.title('% deviation',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#         ax.legend(title=None)
#         plt.savefig('./images/press_drop_pscav.png')


#     def data20_fn():
#         data20 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['press_vs_pscav_table_1'])
#         data20.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#         data20.rename(columns = {'historicx':'Pscav (Bar)'}, inplace = True)
#         data20.rename(columns = {'historicy':'Pr. Drop at A/C'}, inplace = True)
#         data20['Date of Measurment'] = data20['Date of Measurment'].astype('datetime64[ns]')
#         data20 = data20.astype(str)
#         return data20

#     def data21_fn():
#         data21 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['press_vs_pscav_table_2'])
#         data21.rename(columns = {'x':'Pscav (Bar)'}, inplace = True)
#         data21.rename(columns = {'y':'Pr. Drop at A/C'}, inplace = True)
#         data21 = data21.dropna()
#         data21 = data21.astype(str)
#         return data21

#     def data22_fn():
#         data22 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1'][0]['scatter_1'])
#         data22.rename(columns = {'Pscav':'Corrected Pscav scatter'}, inplace = True)
#         data22.rename(columns = {'Pcomp':'Corrected Pcomp scatter'}, inplace = True)

#         data23 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1'][0]['scatter_2'][0])
#         data23.rename(columns = {'Pscav':'Corrected Pscav curve'}, inplace = True)
#         data23.rename(columns = {'Pcomp':'Corrected Pcomp curve'}, inplace = True)

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.scatterplot( x="Corrected Pscav scatter", y="Corrected Pcomp scatter", data=data22,legend='auto',hue='Date',s=80)
#         plt.plot(data23['Corrected Pscav curve'], data23['Corrected Pcomp curve'],marker = 'o',markersize = 10,label = "Shoptrial Data",color = 'brown')
#         plt.xlabel('Corrected Pscav (Bar)',fontweight="bold",size=16)
#         plt.ylabel('Corrected Pcomp (Bar)',fontweight="bold",size=16)
#         plt.title('Pcomp Vs Pscav',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.legend(title=None)
#         plt.savefig('./images/pscav_pcomp_diagram.png')


#     pcomp_pscav_value = r.loc[r['Kind_of_Graph'] == 'Pcomp vs Pscav']['remarks'].item()


#     def data24_fn():
#         data24 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["pcomp_vs_pscav_chart_2"])
#         data24['date_duplicate'] = data24.loc[:, 'date']
#         data24['date'] = data24['date'].astype("datetime64[ns]")
#         data24 = data24.sort_values(by='date')
#         data24['Month_name'] = pd.to_datetime(data24['date']).apply(lambda x:x.strftime("%B"))
#         data24['Year'] = pd.to_datetime(data24['date']).apply(lambda x:x.strftime("%Y"))
#         data24['Month_name_slice'] = data24['Month_name'].str.slice(0,3)
#         data24['month_year'] = data24['Month_name_slice'] + ' ' + data24['Year']

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.lineplot( x='month_year', y='deviation', data=data24,marker = 'o',markersize = 10)
#         plt.xlabel('Month',fontweight="bold",size=16)
#         plt.ylabel('Deviation %',fontweight="bold",size=16)
#         plt.title('% deviation',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#         ax.legend(title=None)
#         plt.savefig('./images/pcomp_pscav.png')


#     def data25_fn():
#         data25 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_table_1'])
#         data25.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#         data25.rename(columns = {'historicx':'Pscav (Bar)'}, inplace = True)
#         data25.rename(columns = {'historicy':'Pcomp (Bar)'}, inplace = True)

#         data25['Date of Measurment'] = data25['Date of Measurment'].astype('datetime64[ns]')
#         data25 = data25.astype(str)
#         return data25



#     def data26_fn():
#         data26 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_table_2'])
#         data26.rename(columns = {'x':'Pscav (Bar)'}, inplace = True)
#         data26.rename(columns = {'y':'Pcomp (Bar)'}, inplace = True)
#         data26 = data26.dropna()
#         data26 = data26.astype(str)
#         return data26

#     def data27_fn():
#         data27 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_chart_1'][0]['scatter_1'])
#         data27.rename(columns = {'Engine_load':'Engine Load scatter'}, inplace = True)
#         data27.rename(columns = {'Texh':'Corrected Texh scatter'}, inplace = True)

#         data28 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_chart_1'][0]['scatter_2'][0])
#         data28.rename(columns = {'Engine_load':'Engine Load curve'}, inplace = True)
#         data28.rename(columns = {'Texh':'Corrected Texh curve'}, inplace = True)

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.scatterplot(x="Engine Load scatter", y="Corrected Texh scatter", data=data27,legend='auto',hue='Date',s=80)
#         plt.plot(data28['Engine Load curve'], data28['Corrected Texh curve'],marker = 'o',markersize = 10,label = "Shoptrial Data",color = 'brown')
#         plt.xlabel('Engine Load (%)',fontweight="bold",size=16)
#         plt.ylabel('Corrected Texh Cyl. Out. (deg.C)',fontweight="bold",size=16)
#         plt.title('Texh Vs Load',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.legend(title=None)
#         plt.savefig('./images/engine_load_texh_daigram.png')

#     engine_load_texh_value = r.loc[r['Kind_of_Graph'] == 'Texh Vs Engine Load']['remarks'].item()


#     def data29_fn():
#         data29 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["tex_vs_el_chart_2"])
#         data29['date_duplicate'] = data29.loc[:, 'date']
#         data29['date'] = data29['date'].astype("datetime64[ns]")
#         data29 = data29.sort_values(by='date')
#         data29['Month_name'] = pd.to_datetime(data29['date']).apply(lambda x:x.strftime("%B"))
#         data29['Year'] = pd.to_datetime(data29['date']).apply(lambda x:x.strftime("%Y"))
#         data29['Month_name_slice'] = data29['Month_name'].str.slice(0,3)
#         data29['month_year'] = data29['Month_name_slice'] + ' ' + data29['Year']

#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.lineplot( x='month_year', y='deviation', data=data29,marker = 'o',markersize = 10)
#         plt.xlabel('Month',fontweight="bold",size=16)
#         plt.ylabel('Deviation %',fontweight="bold",size=16)
#         plt.title('% deviation',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#         ax.legend(title=None)
#         plt.savefig('./images/engine_load_corr_texh.png')

#     def data30_fn():
#         data30 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_table_1'])
#         data30.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#         data30.rename(columns = {'historicx':'Engine Load (%)'}, inplace = True)
#         data30.rename(columns = {'historicy':'Texh (deg.C)'}, inplace = True)
#         data30['Date of Measurment'] = data30['Date of Measurment'].astype('datetime64[ns]')
#         data30['Engine Load (%)'] = data30['Engine Load (%)'].round(2)
#         data30 = data30.astype(str)
#         return data30

#     def data31_fn():
#         data31 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_table_2'])
#         data31.rename(columns = {'x':'Engine Load (%)'}, inplace = True)
#         data31.rename(columns = {'y':'Texh (deg.C)'}, inplace = True)
#         data31 = data31.dropna()
#         data31 = data31.astype(str)
#         return data31


#     data1= data1_fn()
#     data2 = data2_fn()
#     data3_4_fn()
#     data5_fn()
#     data6 = data6_fn()
#     data7_fn()
#     data9_fn()
#     data10 = data10_fn()
#     data11 = data11_fn()
#     data12_dn()
#     data14_fn()
#     data15 = data15_fn()
#     data16 = data16_fn()
#     data17_fn()
#     data19_fn()
#     data20 = data20_fn()
#     data21 =data21_fn()
#     data22_fn()
#     data24_fn()
#     data25 = data25_fn()
#     data26 = data26_fn()
#     data27_fn()
#     data29_fn()
#     data30 = data30_fn()
#     data31 = data31_fn()

#     print("Completed all the function")
#     time2 = datetime.now()

#     print((time2-time).total_seconds())


#     data32 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_chart_1'][0]['scatter_1'])
#     data32.rename(columns = {'Engine_load':'Engine Load scatter'}, inplace = True)
#     data32.rename(columns = {'tc_speed':'Corrected T/C scatter'}, inplace = True)

#     data33 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_chart_1'][0]['scatter_2'][0])
#     data33.rename(columns = {'Engine_load':'Engine Load curve'}, inplace = True)
#     data33.rename(columns = {'tc_speed':'Corrected T/C curve'}, inplace = True)

#     plt.rcParams["font.weight"] = "bold"
#     plt.rcParams["axes.labelweight"] = "bold"
#     plt.figure(figsize=(10,5))
#     ax = sns.scatterplot(x="Engine Load scatter", y="Corrected T/C scatter", data=data32,legend='auto',hue='Date',s=80)
#     plt.plot(data33['Engine Load curve'], data33['Corrected T/C curve'],marker = 'o',markersize = 10,label = "Shoptrial Data",color = 'brown')
#     plt.xlabel('Engine Load (%)',fontweight="bold",size=16)
#     plt.ylabel('Corrected T/C Speed (rpm)',fontweight="bold",size=16)
#     plt.title('Engine Load Vs T/C Speed',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#     ax.legend(title=None)
#     plt.savefig('./images/engine_load_tc_daigram.png')

#     speed_load_value = r.loc[r['Kind_of_Graph'] == 'T/C Speed Vs Engine Load']['remarks'].item()

#     data34 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["tc_vs_EL_chart_2"])
#     data34['date_duplicate'] = data34.loc[:, 'date']
#     data34['date'] = data34['date'].astype("datetime64[ns]")
#     data34 = data34.sort_values(by='date')
#     data34['Month_name'] = pd.to_datetime(data34['date']).apply(lambda x:x.strftime("%B"))
#     data34['Year'] = pd.to_datetime(data34['date']).apply(lambda x:x.strftime("%Y"))
#     data34['Month_name_slice'] = data34['Month_name'].str.slice(0,3)
#     data34['month_year'] = data34['Month_name_slice'] + ' ' + data34['Year']

#     plt.rcParams["font.weight"] = "bold"
#     plt.rcParams["axes.labelweight"] = "bold"
#     plt.figure(figsize=(10,5))
#     ax = sns.lineplot( x='month_year', y='deviation', data=data34,marker = 'o',markersize = 10)
#     plt.xlabel('Month',fontweight="bold",size=16)
#     plt.ylabel('Deviation %',fontweight="bold",size=16)
#     plt.title('% deviation',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#     ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#     ax.legend(title=None)
#     plt.savefig('./images/engine_load_corr_tc.png')

#     data35 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_table_1'])
#     data35.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#     data35.rename(columns = {'historicx':'Engine Load (%)'}, inplace = True)
#     data35.rename(columns = {'historicy':'T/C Speed (rpm)'}, inplace = True)
#     data35['Date of Measurment'] = data35['Date of Measurment'].astype('datetime64[ns]')
#     data35['Engine Load (%)'] = data35['Engine Load (%)'].round(2)
#     data35 = data35.astype(str)

#     data36 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_table_2'])
#     data36.rename(columns = {'x':'Engine Load (%)'}, inplace = True)
#     data36.rename(columns = {'y':'T/C Speed (rpm)'}, inplace = True)
#     data36 = data36.dropna()
#     data36 = data36.astype(str)

#     data37 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_chart_1'][0]['scatter_1'])
#     data37.rename(columns = {'Engine_load':'Engine Load scatter'}, inplace = True)
#     data37.rename(columns = {'Sfoc':'Fuel oil consumption scatter'}, inplace = True)

#     data38 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_chart_1'][0]['scatter_2'][0])
#     data38.rename(columns = {'Engine_load':'Engine Load curve'}, inplace = True)
#     data38.rename(columns = {'Sfoc':'Fuel oil consumption curve'}, inplace = True)

#     plt.rcParams["font.weight"] = "bold"
#     plt.rcParams["axes.labelweight"] = "bold"
#     plt.figure(figsize=(10,5))
#     ax = sns.scatterplot(x="Engine Load scatter", y="Fuel oil consumption scatter", data=data37,legend='auto',hue='Date',s=80)
#     plt.plot(data38['Engine Load curve'], data38['Fuel oil consumption curve'],marker = 'o',markersize = 10,label = "Shoptrial Data",color = 'brown')
#     plt.xlabel('Engine Load (%)',fontweight="bold",size=16)
#     plt.ylabel('Fuel Oil Consumption (g/kWhr)',fontweight="bold",size=16)
#     plt.title('Fuel Oil Consumption Rate Vs Engine Load',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#     ax.legend(title=None)
#     plt.savefig('./images/engine_load_sfoc_daigram.png')

#     load_sfoc_value = r.loc[r['Kind_of_Graph'] == 'SFOC Vs Engine Load']['remarks'].item()

#     data39 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["sfoc_vs_el_chart_2"])
#     data39['date_duplicate'] = data39.loc[:, 'date']
#     data39['date'] = data39['date'].astype("datetime64[ns]")
#     data39 = data39.sort_values(by='date')
#     data39['Month_name'] = pd.to_datetime(data39['date']).apply(lambda x:x.strftime("%B"))
#     data39['Year'] = pd.to_datetime(data39['date']).apply(lambda x:x.strftime("%Y"))
#     data39['Month_name_slice'] = data39['Month_name'].str.slice(0,3)
#     data39['month_year'] = data39['Month_name_slice'] + ' ' + data39['Year']

#     plt.rcParams["font.weight"] = "bold"
#     plt.rcParams["axes.labelweight"] = "bold"
#     plt.figure(figsize=(10,5))
#     ax = sns.lineplot( x='month_year', y='deviation', data=data39,marker = 'o',markersize = 10)
#     plt.xlabel('Month',fontweight="bold",size=16)
#     plt.ylabel('Deviation %',fontweight="bold",size=16)
#     plt.title('% deviation',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#     ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#     ax.legend(title=None)
#     plt.savefig('./images/engine_load_sfoc.png')

#     data40 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_table_1'])
#     data40.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#     data40.rename(columns = {'historicx':'Engine Load'}, inplace = True)
#     data40.rename(columns = {'historicy':'SFOC (g/kW-hr)'}, inplace = True)
#     data40['Date of Measurment'] = data40['Date of Measurment'].astype('datetime64[ns]')
#     data40['Engine Load'] = data40['Engine Load'].round(2)
#     data40_a = pd.DataFrame.from_dict(s['sfoc_trend']['sfoc_trend_table'])
#     data40_a['date'] = data40_a['date'].astype('datetime64[ns]')

 


#     dict_sfoc_shop = pd.Series(data40_a['sfoc_shop'].values,index=data40_a['date']).to_dict()
#     dict_sfoc_deviation = pd.Series(data40_a['deviation'].values,index=data40_a['date']).to_dict()
#     dict_sfoc_result = pd.Series(data40_a['type'].values,index=data40_a['date']).to_dict()

 

#     data40['SFOC Shop Trail'] = np.nan
#     data40['SFOC Shop Trail']= data40['SFOC Shop Trail'].fillna(data40['Date of Measurment'].apply(lambda x:dict_sfoc_shop.get(x)))
#     data40['Deviation'] = np.nan

 

#     data40['Deviation']= data40['Deviation'].fillna(data40['Date of Measurment'].apply(lambda x:dict_sfoc_deviation.get(x)))
#     data40['Result'] = np.nan
#     data40['Result']= data40['Result'].fillna(data40['Date of Measurment'].apply(lambda x:dict_sfoc_result.get(x)))
#     data40 = data40.astype(str)

#     data41 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_table_2'])
#     data41.rename(columns = {'x':'Engine Load'}, inplace = True)
#     data41.rename(columns = {'y':'SFOC (g/kW-hr)'}, inplace = True)
#     data41 = data41.dropna()
#     data41 = data41.astype(str)

#     if (s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1']) == []:
#         data42_to_change = 'null'
#     else:
#         data42_to_change = 'yes'
#         data42 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1'][0]['scatter_1'])
#         data42.rename(columns = {'Engine_speed':'Engine speed scatter'}, inplace = True)
#         data42.rename(columns = {'Pump_mark':'corrected pump mark scatter'}, inplace = True)
        
#         data43 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1'][0]['scatter_2'][0])
#         data43.rename(columns = {'Engine_speed':'Engine speed curve'}, inplace = True)
#         data43.rename(columns = {'Pump_mark':'corrected pump mark curve'}, inplace = True)
        
#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.scatterplot(x="Engine speed scatter", y="corrected pump mark scatter", data=data42,legend='auto',hue='Date',s=80)
#         plt.plot(data43['Engine speed curve'], data43['corrected pump mark curve'],marker = 'o',markersize = 10,label = "Shoptrial Data",color = 'brown')
#         plt.xlabel('Engine Speed (rpm)',fontweight="bold",size=16)
#         plt.ylabel('Corrected Pump Mark',fontweight="bold",size=16)
#         plt.title('Pump Mark Vs Engine Speed',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.legend(title=None)
#         plt.savefig('./images/engine_speed_corrected_pumpmark_daigram.png')
        
#         engine_speed_corrected_pumpmark_value = r.loc[r['Kind_of_Graph'] == 'Pump Mark Vs Engine Speed']['remarks'].item()
        
#         data44 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["pump_mark_vs_ES_chart_2"])
        
#         data44['date_duplicate'] = data44.loc[:, 'date']
#         data44['date'] = data44['date'].astype("datetime64[ns]")
#         data44 = data44.sort_values(by='date')
        
#         data44['Month_name'] = pd.to_datetime(data44['date']).apply(lambda x:x.strftime("%B"))
#         data44['Year'] = pd.to_datetime(data44['date']).apply(lambda x:x.strftime("%Y"))
#         data44['Month_name_slice'] = data44['Month_name'].str.slice(0,3)
#         data44['month_year'] = data44['Month_name_slice'] + ' ' + data44['Year']
        
#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.lineplot( x='month_year', y='deviation', data=data44,marker = 'o',markersize = 10)
#         plt.xlabel('Month',fontweight="bold",size=16)
#         plt.ylabel('Deviation %',fontweight="bold",size=16)
#         plt.title('% deviation',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#         ax.legend(title=None)
#         plt.savefig('./images/engine_speed_corrected_pump_deviation.png')
        
#         data45 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_table_1'])
#         data45.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#         data45.rename(columns = {'historicx':'Engine Speed'}, inplace = True)
#         data45.rename(columns = {'historicy':'Pump Mark'}, inplace = True)
        
#         data45['Date of Measurment'] = data45['Date of Measurment'].astype('datetime64[ns]')
#         data45['Engine Speed'] = data45['Engine Speed'].round(2)
#         data45 = data45.astype(str)
        
#         data46 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_table_2'])
#         data46.rename(columns = {'x':'Engine Speed'}, inplace = True)
#         data46.rename(columns = {'y':'Pump Mark'}, inplace = True)
        
#         data46 = data46.dropna()
#         data46 = data46.astype(str)
        
        
#     if (s['Engine_Performance_Tab']['pmax_pcomp_vs_pump_mark_chart_1'])== []:
#         data47_to_change = 'null'
#     else:
#         data47_to_change = 'yes'
#         data47 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pmax_pcomp_vs_pump_mark_chart_1'][0]['scatter_1'])
#         data47.rename(columns = {'Pump_mark':'pump mark scatter'}, inplace = True)
#         data47.rename(columns = {'Pmax_Pcomp':'pmax pcomp scatter'}, inplace = True)
        
#         data48 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pmax_pcomp_vs_pump_mark_chart_1'][0]['scatter_2'][0])
#         data48.rename(columns = {'Pump_mark':'pump mark curve'}, inplace = True)
#         data48.rename(columns = {'Pmax_Pcomp':'pmax pcomp curve'}, inplace = True)
        
#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.scatterplot( x="pump mark scatter", y="pmax pcomp scatter", data=data47,legend='auto',hue='Date',s=80)
#         plt.plot(data48['pump mark curve'], data48['pmax pcomp curve'],marker = 'o',markersize = 10,label = "Shoptrial Data",color = 'brown')
#         plt.xlabel('Pump Mark(measured)',fontweight="bold",size=16)
#         plt.ylabel('Pmax-Pcomp(bar)',fontweight="bold",size=16)
#         plt.title('(PMAX-PCOMP) Vs Pump Mark',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.legend(title=None)
#         plt.savefig('./images/pmax_pcomp_pump_mark_daigram.png')
        
#         pmax_pcomp_pump_mark_value = r.loc[r['Kind_of_Graph'] == '(Pmax-Pcomp) Vs Pump Mark']['remarks'].item()
        
#         data49 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["pmax_pcomp_vs_pump_mark_chart_2"])
        
#         data49['date_duplicate'] = data49.loc[:, 'date']
#         data49['date'] = data49['date'].astype("datetime64[ns]")
#         data49 = data49.sort_values(by='date')
        
#         data49['Month_name'] = pd.to_datetime(data49['date']).apply(lambda x:x.strftime("%B"))
#         data49['Year'] = pd.to_datetime(data49['date']).apply(lambda x:x.strftime("%Y"))
#         data49['Month_name_slice'] = data49['Month_name'].str.slice(0,3)
#         data49['month_year'] = data49['Month_name_slice'] + ' ' + data49['Year']
        
#         plt.rcParams["font.weight"] = "bold"
#         plt.rcParams["axes.labelweight"] = "bold"
#         plt.figure(figsize=(10,5))
#         ax = sns.lineplot( x='month_year', y='deviation', data=data49,marker = 'o',markersize = 10)
#         plt.xlabel('Month',fontweight="bold",size=16)
#         plt.ylabel('Deviation %',fontweight="bold",size=16)
#         plt.title('% deviation',fontname="fonts/Times New Roman", size=18,fontweight="bold")
#         ax.yaxis.set_major_formatter(ticker.PercentFormatter())
#         ax.legend(title=None)
#         plt.savefig('./images/pmax_pcomp_pump_mark_deviation.png')
        
#         data50 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pmax_pcomp_vs_pump_mark_table_1'])
#         data50.rename(columns = {'dates':'Date of Measurment'}, inplace = True)
#         data50.rename(columns = {'historicx':'Pump Mark'}, inplace = True)
#         data50.rename(columns = {'historicy':'Pmax - Pcomp'}, inplace = True)
        
#         data50['Date of Measurment'] = data50['Date of Measurment'].astype('datetime64[ns]')
#         data50['Pump Mark'] = data50['Pump Mark'].round(2)
#         data50 = data50.astype(str)
        
#         data51 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pmax_pcomp_vs_pump_mark_table_2'])
#         data51.rename(columns = {'x':'Pump Mark'}, inplace = True)
#         data51.rename(columns = {'y':'Pmax - Pcomp'}, inplace = True)
        
#         data51 = data51.dropna()
#         data51 = data51.astype(str)
        
#     data52 = pd.DataFrame.from_dict(s['Power_curve_Tab']['graph_1'])

#     data53 = pd.DataFrame.from_dict(s['Power_curve_Tab']['graph_2'])

#     # eng_load_st =  list(data52["engine_load1"])
#     # tcr_st =  list(data52["tc_rpm1"])
#     # eng_rpm_st =  list(data52["engine_rpm1"])
#     # pcomp_st =  list(data52["pcomp1"])
#     # pmax_st =  list(data52["pmax1"])
#     # pscav_st =  list(data52["pscav1"])
#     # sfoc_st =  list(data52["sfoc1"])

#     # eng_load_1 =  list(data53["engine_load"])
#     # eng_rpm_1 =  list(data53["engine_rpm"])
#     pcomp_1 =  list(data53["pcomp"])
#     pmax_1 =  list(data53["pmax"])
#     # pscav_1 =  list(data53["pscav"])
#     # date_1 =  list(data53["date1"])

#     fig_power_curve, axes = plt.subplots(6, 1, figsize=(7, 12.5), sharey=False) #sharey is flase because diff axis interval
#     sns.scatterplot(data=data53, x='engine_load', y='tc_rpm', ax=axes[0], hue="date1",legend=False)
#     sns.lineplot(data=data52, x='engine_load1', y='tc_rpm1',marker = 'o',markersize = 7, ax=axes[0])
#     axes[0].set_xlabel('',fontweight="bold",size=0)
#     axes[0].set_ylabel('TC RPM',fontweight="bold",size=9)
#     axes[0].grid(False)
#     sns.scatterplot(data=data53, x='engine_load', y='engine_rpm', ax=axes[1], hue="date1",legend=False)
#     sns.lineplot(data=data52, x='engine_load1', y='engine_rpm1', ax=axes[1],marker = 'o',markersize = 7,)
#     axes[1].set_xlabel('',fontweight="bold",size=0)
#     axes[1].set_ylabel('Engine RPM',fontweight="bold",size=9)
#     axes[1].grid(False)
#     sns.scatterplot(data=data53, x='engine_load', y='pcomp', ax=axes[2], hue="date1",legend=False)
#     sns.lineplot(data=data52, x='engine_load1', y='pcomp1', ax=axes[2],marker = 'o',markersize = 7,)
#     axes[2].set_xlabel('',fontweight="bold",size=0)
#     axes[2].set_ylabel('PCOMP',fontweight="bold",size=9)
#     axes[2].grid(False)
#     sns.scatterplot(data=data53, x='engine_load', y='pmax', ax=axes[3], hue="date1",legend=False)
#     sns.lineplot(data=data52, x='engine_load1', y='pmax1', ax=axes[3],marker = 'o',markersize = 7,)
#     axes[3].set_xlabel('',fontweight="bold",size=0)
#     axes[3].set_ylabel('PMAX',fontweight="bold",size=9)
#     axes[3].grid(False)
#     sns.scatterplot(data=data53, x='engine_load', y='pscav', ax=axes[4], hue="date1",legend=False)
#     sns.lineplot(data=data52, x='engine_load1', y='pscav1', ax=axes[4],marker = 'o',markersize = 7,)
#     axes[4].set_xlabel('',fontweight="bold",size=0)
#     axes[4].set_ylabel('PSCAV',fontweight="bold",size=9)
#     axes[4].grid(False)
#     sns.scatterplot(data=data53, x='engine_load', y='sfoc', ax=axes[5], hue="date1",legend=False)
#     sns.lineplot(data=data52, x='engine_load1', y='sfoc1', ax=axes[5],marker = 'o',markersize = 7,)
#     axes[5].set_xlabel('Engine Load',fontweight="bold",size=12)
#     axes[5].set_ylabel('SFOC',fontweight="bold",size=9)
#     axes[5].grid(False)

#     plt.savefig('./images/Power_curve.png')

#     import matplotlib.pyplot as plt
#     plt.clf()
#     plt.figure(figsize=(10,5))



#     Pmax_Deviation_value = r.loc[r['Kind_of_Graph'] == 'Pmax Deviation']['remarks'].item()
#     Pcomp_Deviation_value = r.loc[r['Kind_of_Graph'] == 'Pcomp Deviation']['remarks'].item()
#     Texh_Deviation_value = r.loc[r['Kind_of_Graph'] == 'Texh Deviation']['remarks'].item()
#     # Pumpmark_Deviation_value = r.loc[r['Kind_of_Graph'] == 'Pump Mark Deviation']['remarks'].item()

#     #1.pmax
#     data54 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_chart_1'])
#     data55 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_chart_2'][0])
#     data56 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_table_1'])
#     m1 =data56[data56['Measured'] !=0] 
#     Pmax_filtered= m1[['cylinder', 'Measured', 'average', 'deviation', 'result',]]
#     pmax_1= Pmax_filtered.astype(str)
#     Pmax_data1 = pmax_1.values.tolist()
#     Pmax_data1

#     color =  ['#CC0000','#29EE29', '#0066CC',"#AC2EB5","#663300","#F1F50C"]
#     plt.title('Pmax Mean',fontweight="bold",size=14)
#     fig_pmax=sns.barplot(data=data55, x="x", y="y",hue="x",palette=color)
#     ax1=fig_pmax
#     for p in ax1.patches:
#         ax1.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
#                     ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
#                     textcoords='offset points')
#     ax1.get_legend().remove()
#     fig_pmax.grid(False)
#     fig_pmax.set_xlabel('',fontweight="bold",size=0)
#     fig_pmax.set_ylabel('Bar',fontweight="bold",size=14)
#     plt.savefig('./images/Pmax_mean.png')
#     plt.clf()



#     plt.title('Pmax Deviation',fontweight="bold",size=16)
#     fig_pmax_dev=sns.barplot(data=m1, x="cylinder", y="deviation",palette=color)
#     ax2=fig_pmax_dev
#     fig_pmax_dev.grid(False)
#     fig_pmax_dev.set_xlabel('Cylinder No',fontweight="bold",size=16)
#     fig_pmax_dev.set_ylabel('Deviation from mean (bar)',fontweight="bold",size=14)
#     plt.savefig('./images/Pmax_deviation.png')
#     plt.clf()




#     #2.pcomp
#     data57 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_chart_1'])
#     data58 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_chart_2'][0])
#     data59 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_table_1'])
#     m2 =data59[data59['measure'] !=0] 
#     Pcomp_filtered= m2[['cylinder', 'measure', 'average', 'deviation', 'result',]]
#     pcomp_1= Pcomp_filtered.astype(str)
#     Pcomp_data1 = pcomp_1.values.tolist()

#     plt.title('Pcomp Mean',fontweight="bold",size=16)
#     fig_pcomp=sns.barplot(data=data58, x="x", y="y",hue="x",palette=color)
#     ax3=fig_pcomp
#     for p in ax3.patches:
#         ax3.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
#                     ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
#                     textcoords='offset points')
#     ax3.get_legend().remove()
#     fig_pcomp.grid(False)
#     fig_pcomp.set_xlabel('',fontweight="bold",size=0)
#     fig_pcomp.set_ylabel('Bar',fontweight="bold",size=14)
#     plt.savefig('./images/Pcomp_mean.png')
#     plt.clf()



#     plt.title('Pcomp Deviation',fontweight="bold",size=16)
#     fig_pcomp_dev=sns.barplot(data=m2, x="cylinder", y="deviation",palette=color)
#     ax4=fig_pcomp_dev
#     fig_pcomp_dev.grid(False)
#     fig_pcomp_dev.set_xlabel('Cylinder No',fontweight="bold",size=14)
#     fig_pcomp_dev.set_ylabel('Deviation from mean (bar)',fontweight="bold",size=14)
#     plt.savefig('./images/Pcomp_deviation.png')
#     plt.clf()



#     #3.Texh
#     data60 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_chart_1'])
#     data61 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_chart_2'][0])
#     data62 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_table_1'])
#     m3 =data62[data62['ex_temp'] !=0] 
#     Texh_filtered= m3[['cylinder', 'ex_temp', 'average', 'deviation', 'result',]]
#     texh_1= Texh_filtered.astype(str)
#     Texh_data1 = texh_1.values.tolist()

#     plt.title('Exhaust Temperature Mean',fontweight="bold",size=16)
#     fig_texh=sns.barplot(data=data61, x="x", y="y",hue="x",palette=color)
#     ax5=fig_texh
#     for p in ax5.patches:
#         ax5.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
#                     ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
#                     textcoords='offset points')
#     ax5.get_legend().remove()
#     fig_texh.grid(False)
#     fig_texh.set_xlabel('',fontweight="bold",size=0)
#     fig_texh.set_ylabel('Bar',fontweight="bold",size=14)
#     plt.savefig('./images/Texh_mean.png')
#     plt.clf()



#     plt.title('Exhaust Temperature Deviation',fontweight="bold",size=16)
#     fig_texh_dev=sns.barplot(data=m3, x="cylinder", y="deviation",palette=color)
#     ax6=fig_texh_dev
#     fig_texh_dev.grid(False)
#     fig_texh_dev.set_xlabel('Cylinder No',fontweight="bold",size=14)
#     fig_texh_dev.set_ylabel('Deviation from mean (bar)',fontweight="bold",size=14)
#     plt.savefig('./images/Texh_deviation.png')
#     plt.clf()



#     #4.pumpmark
#     if (s['Cylinder_comparison_Tab']['pump_mark_table_1'])== []:
#         data63_to_change = 'null'
#     else:
#         data63_to_change = 'yes'
#         data63 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['pump_mark_table_1'])
#         data64 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['pump_mark_chart_1'])
#         m4 =data63[data63['ex_temp'] !=0] 
#         Pmark_filtered= m4[['cylinder', 'ex_temp', 'average', 'deviation', 'result',]]
#         Pmark_1= Pmark_filtered.astype(str)
#         Pmark_data1 = Pmark_1.values.tolist()

 

#         Pumpmark_Deviation_value = r.loc[r['Kind_of_Graph'] == 'Pump Mark Deviation']['remarks'].item()
#         if data63['ex_temp'].sum()!= 0:
#             plt.title('Pump Mark Deviation',fontweight="bold",size=16)
#             fig_texh_dev=sns.barplot(data=m4, x="cylinder", y="deviation",palette=color)
#             ax7=fig_texh_dev
#             fig_texh_dev.grid(False)
#             fig_texh_dev.set_xlabel('Cylinder No',fontweight="bold",size=14)
#             fig_texh_dev.set_ylabel('Deviation from mean (bar)',fontweight="bold",size=14)
#             plt.savefig('./images/pmark_deviation.png')
#             plt.clf()
#         else:
#             print("")



        

#     #************************************************* PDF CODE ***********************************************************#
#     a = data1['particulars'].values[0]
#     b=  data6.values[0][0]
#     speed_corrected_speed_value = r.loc[r['Kind_of_Graph'] == 'T/C Speed Vs Engine Speed']['remarks'].item()

#     c = ["#588AEE","#57CFA0","#5A6C8D","#EBB517","#6B5BEE","#69C0E2","#8E5CB2","#F49243"]
#     fig, ax1 = plt.subplots(figsize = (15, 7))

    

#     g =plt.bar(data40_a['month'],data40_a["sfoc"],color=c)

    

#     g =sns.lineplot(x='month', y='sfoc_shop',marker = 'o', data=data40_a, ax=ax1,color="yellow",label = "sfoc_shop") # on secondary ax2

    

#     plt.xlabel('Month',fontweight="bold")
#     plt.ylabel("SFOC Shop Trail",fontweight="bold") 
#     plt.title('SFOC Trend (sfoc g/kWhr Vs Month)', size=18,fontweight="bold")
#     ax1.set(ylim=(130, 200))
#     fig.savefig("./images/sfoc_trend.png")

#     def simple_table(spacing=3):
#         print("Starting PDF")
#         #report_prepared_date= "11-10-2022"

#         pdf = FPDF()
#         #*********************************************** 1 page **********************************************************#
#         pdf.add_page()
#         # pdf.set_font('Arial', 'B', 18,'fonts/arial.ttf')
#         # pdf.add_font('Arial', 'B','fonts/arial.ttf') 
#         # pdf.add_font("Arial", "", 'fonts/arial.ttf', uni=True)
#         pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
#         pdf.set_font('Arial', 'B',size= 18)

#         # pdf.image(oceanix_logo_path,15,15,w=35)
#         pdf.image(msc_logo_path,160,8,w=35)

#     #Cell postion from left side
#         pdf.set_xy(50,15)
#         # pdf.set_text_color(25,47,133)
#         pdf.cell(170, 60,  'ENGINE PERFORMANCE REPORT')
#         # pdf.set_text_color(0,0,0)
#         pdf.set_line_width(1)
#         pdf.line(10, 50, 199, 50)#(x_start, y_start, x_end, y_end)
#         pdf.set_line_width(0.2)
#         pdf.set_font('Arial', "",12)
#         pdf.set_xy(10,55)
#         #pdf.multi_cell(80,14.5,"Report Date :"+" "+ report_prepared_date, align='R')

        
#         pdf.cell(10, 2, "Vessel Name :"+" "+a,ln=True)
#         pdf.cell(10, 12,"Test Date :"+" "+ b,ln=True)
        
#         pdf.line(10, 70, 199, 70)
#         pdf.set_font('Arial', 'B', 18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 18, 'Engine Details',ln=True,align='C')
#         pdf.line(10, 85, 199, 85)
        
#         pdf.set_line_width(0)
#         pdf.set_text_color(0,0,0)
        
#         tablefirst_head = [['Title','Particulars']]
#         tablefirst = data1.values.tolist()
#         pdf.set_font("Arial",'B', size=8)
#         col_width = pdf.w /2.21
#         row_height = pdf.font_size-.5
#         for row in tablefirst_head:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)

#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.21
#         row_height = pdf.font_size-.5
#         for row in tablefirst:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)

#         pdf.line(10, 145, 199, 145)
#         pdf.set_font('Arial', 'B', 18)
#         pdf.set_text_color(25,47,133)
#         pdf.set_xy(10,138)
#         pdf.cell(180, 24, 'Result Table',ln=True,align='C') 
#         pdf.line(10, 155, 199, 155) 

#         pdf.set_xy(10,165)
#         spacing = 3.5
#         tablefirst_head1 = [['Title','Kind Of Graph','Shop Trial Value','Measured Value','Analysis Result','Status']]
#         tablefirst1 = data2.values.tolist()
#         pdf.set_font("Arial",'B', size=6.2)

#         col_width = pdf.w /6.68
#         row_height = pdf.font_size-.4
#         for row in tablefirst_head1:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)


#         pdf.set_font("Arial", size=6.2)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /6.68
#         row_height = pdf.font_size-.4
#         for row in tablefirst1:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)

#         #Page Number
#         pdf.set_y(274.7)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
            
#         # tablefirst_head = [['Title','Particulars']]
#         # tablefirst = data1.values.tolist()
#         # pdf.set_font("Arial",'B', size=10)
#         # col_width = pdf.w /2.21
#         # row_height = pdf.font_size
#         # for row in tablefirst_head:
#         #     pdf.set_text_color(255,255,255)
#         #     pdf.set_fill_color(21,55,188)
#         #     for item in row:
#         #         pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#         #     pdf.ln(row_height*spacing)
            
#         # pdf.set_font("Arial",'B', size=10)
#         # pdf.set_text_color(0,0,0)
#         # col_width = pdf.w /2.21
#         # row_height = pdf.font_size
#         # for row in tablefirst:
#         #     for item in row:
#         #         pdf.cell(col_width, row_height*spacing,
#         #                 txt=item, border=1)
#         #     pdf.ln(row_height*spacing)
            
#         # #pdf.set_line_width(0.4)
#         # pdf.line(10, 122, 199, 122)
#         # pdf.set_font('Arial', 'B', 18)
#         # pdf.set_text_color(25,47,133)
#         # pdf.cell(180, 24, 'Result Table',ln=True,align='C') 
#         # pdf.line(10, 138, 199, 138) 
        
    
#         # spacing = 4
#         # tablefirst_head1 = [['Title', 'Kind of Graph', 'Standard Value', 'Analysis Result','Deviation','Limit','Status']]
#         # tablefirst1 = data2.values.tolist()
#         # pdf.set_font("Arial",'B', size=5.6)
        
#         # #pdf.set_text_color(0,0,0)
#         # col_width = pdf.w /7.5
#         # row_height = pdf.font_size
#         # for row in tablefirst_head1:
#         #     pdf.set_text_color(255,255,255)
#         #     pdf.set_fill_color(21,55,188)
#         #     for item in row:
#         #         pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#         #     pdf.ln(row_height*spacing)
            
            
#         # pdf.set_font("Arial", size=5.6)
#         # pdf.set_text_color(0,0,0)
#         # col_width = pdf.w /7.5
#         # row_height = pdf.font_size
#         # for row in tablefirst1:
#         #     for item in row:
#         #         pdf.cell(col_width, row_height*spacing,
#         #                 txt=item, border=1)
#         #     pdf.ln(row_height*spacing)
            
#         # #Page Number
#         # pdf.set_y(273)
#         # pdf.set_font('Arial', 'I', 8)
#         # pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")    
        
#         # tablefirst_head = [['Title','Particulars']]
#         # tablefirst = data1.values.tolist()
#         # pdf.set_font("Arial",'B', size=8)
#         # col_width = pdf.w /2.21
#         # row_height = pdf.font_size-.5
#         # for row in tablefirst_head:
#         #     pdf.set_text_color(255,255,255)
#         #     pdf.set_fill_color(21,55,188)
#         #     for item in row:
#         #         pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#         #     pdf.ln(row_height*spacing)

#         # pdf.set_font("Arial",'B', size=8)
#         # pdf.set_text_color(0,0,0)
#         # col_width = pdf.w /2.21
#         # row_height = pdf.font_size-.5
#         # for row in tablefirst:
#         #     for item in row:
#         #         pdf.cell(col_width, row_height*spacing,
#         #                 txt=item, border=1)
#         #     pdf.ln(row_height*spacing)

#         # pdf.line(10, 153, 199, 153)
#         # pdf.set_font('Arial', 'B', 18)
#         # pdf.set_text_color(25,47,133)
#         # #pdf.set_xy(10,138)
#         # pdf.cell(180, 20, 'Result Table',ln=True,align='C') 
#         # pdf.line(10, 164, 199, 164) 

#         # pdf.set_xy(10,166)
#         # spacing = 3.5
#         # tablefirst_head1 = [['Title','Kind Of Graph','Shop Trial Value','Measured Value','Analysis Result','Status']]
#         # tablefirst1 = data2.values.tolist()
#         # pdf.set_font("Arial",'B', size=6.2)

#         # col_width = pdf.w /6.68
#         # row_height = pdf.font_size-.4
#         # for row in tablefirst_head1:
#         #     pdf.set_text_color(255,255,255)
#         #     pdf.set_fill_color(21,55,188)
#         #     for item in row:
#         #         pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#         #     pdf.ln(row_height*spacing)


#         # pdf.set_font("Arial", size=6.2)
#         # pdf.set_text_color(0,0,0)
#         # col_width = pdf.w /6.68
#         # row_height = pdf.font_size-.4
#         # for row in tablefirst1:
#         #     for item in row:
#         #         pdf.cell(col_width, row_height*spacing,
#         #                 txt=item, border=1)
#         #     pdf.ln(row_height*spacing)

#         # #Page Number
#         # pdf.set_y(274.7)
#         # pdf.set_font('Arial', 'I', 8)
#         # pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
#     #*********************************************** 2 page **********************************************************#        
#         pdf.add_page()  
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, 'Engine Performance',ln=True,align='C')   
#         pdf.cell(180, 15, '1.Load Diagram',ln=True,align='C')
#         pdf.image("./images/loaddiagram.png",1,32,w=110,h=80)
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         #if (speed_load_value==''):
#             #pdf.cell(10, 150,"Remarks :"+" "+'Normal' ,ln=True)
#         #else:    
#             #pdf.set_xy(10,115)
#             #pdf.multi_cell(80, 3,"Remarks :"+" "+speed_load_value )
#         pdf.image("./images/torque_rich_index.png",105,32,w=108,h=80) 
        
#         pdf.set_font("Arial",'B', size=15)
#         pdf.set_xy(10,140)
#         pdf.cell(1, 8,"Test Data" ,ln=True)
        
#         spacing=4
#         tablefirst_head2 = [['Date of Measurment', 'Engine RPM', 'Engine Load']]
#         tablefirst2 = data6.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst_head2:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst2:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
            
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")    
#     #*********************************************** 3 page **********************************************************#    
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, '2.T/C Speed Vs Engine Speed',ln=True,align='C') 
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         pdf.image("./images/engine_corrected_speed_daigram.png",2,32,w=110,h=80)
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         if (speed_corrected_speed_value==''):
#             pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else:    
#             pdf.set_xy(10,115)
#             pdf.multi_cell(185, 3,"Remarks :")
#             pdf.set_xy(10,118)
#             pdf.multi_cell(185, 3,speed_corrected_speed_value ,border=1)
#         pdf.image("./images/deviation.png",105,32,w=108,h=80) 
        
#         pdf.set_font("Arial",'B', size=15)
#         pdf.set_xy(10,140)
#         pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
#         spacing=3
#         tablefirst_head3 = [['Date of Measurment', 'Engine Speed', 'T/C Speed']]
#         tablefirst3 = data10.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst_head3:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst3:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
        
#         pdf.set_font("Arial",'B', size=15)
#         #pdf.set_xy(10,130)
#         pdf.cell(10,35,"Shop Trial Data" ,ln=True)
#         pdf.set_xy(10,220)
        
#         spacing=3
#         tablefirst_head4 = [['Engine Speed', 'T/C Speed']]
#         tablefirst4 = data11.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst_head4:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst4:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
            
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")   
#     #*********************************************** 4 page **********************************************************#     
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, '3.Pscav Vs T/C Speed',ln=True,align='C') 
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         pdf.image("./images/pscav_tc_speed_daigram.png",2,32,w=110,h=80)
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         if (pscav_tc_speed_value==' ') | (pscav_tc_speed_value==''):
#             pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else:    
#             pdf.set_xy(10,115)
#             pdf.multi_cell(185, 3,"Remarks :" )
#             pdf.set_xy(10,118)
#             pdf.multi_cell(185, 3,pscav_tc_speed_value )

#         pdf.image("./images/deviation_pscav_tc.png",105,32,w=108,h=80) 
#         pdf.set_font("Arial",'B', size=15)
#         pdf.set_xy(10,140)
#         pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
#         spacing=3
#         tablefirst_head5 = [['Date of Measurment', 'T/C Speed', 'Pscav(Bar)']]
#         tablefirst5 = data15.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst_head5:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst5:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
        
#         pdf.set_font("Arial",'B', size=15)
#         #pdf.set_xy(10,130)
#         pdf.cell(10,35,"Shop Trial Data" ,ln=True)
#         pdf.set_xy(10,220)
        
#         spacing=3
#         tablefirst_head6 = [['T/C Speed', 'Pscav(Bar)']]
#         tablefirst6 = data16.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst_head6:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst6:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
        
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
#     #*********************************************** 5 page **********************************************************#    
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, '4.Press. drop at A/C Vs Pscav',ln=True,align='C') 
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         pdf.image("./images/pscav_press_drop_daigram.png",2,32,w=110,h=80)
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         if (press_drop_pscav_value=='') | (press_drop_pscav_value==' '):
#             pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else: 
#             pdf.set_xy(10,115)
#             pdf.multi_cell(185, 3,"Remarks :" )
#             pdf.set_xy(10,118)
#             pdf.multi_cell(185, 3,press_drop_pscav_value )

#         pdf.image("./images/press_drop_pscav.png",105,32,w=108,h=80) 
#         pdf.set_font("Arial",'B', size=15)
#         pdf.set_xy(10,140)
#         pdf.cell(1, 8,"Test Data" ,ln=True)   
        
#         spacing=3
#         tablefirst_head7 = [['Date of Measurment', 'Pscav (Bar)', 'Pr. Drop at A/C']]
#         tablefirst7 = data20.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst_head7:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst7:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial",'B', size=15)
#         #pdf.set_xy(10,130)
#         pdf.cell(10,35,"Shop Trial Data" ,ln=True)
#         pdf.set_xy(10,220)
        
#         spacing=3
#         tablefirst_head8 = [['Pscav (Bar)', 'Pr. Drop at A/C']]
#         tablefirst8 = data21.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst_head8:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst8:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)  
        
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
#     #*********************************************** 6 page **********************************************************#
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, '5.Pcomp Vs Pscav',ln=True,align='C') 
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         pdf.image("./images/pscav_pcomp_diagram.png",2,32,w=110,h=80)
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         if (pcomp_pscav_value==' ') | (pcomp_pscav_value==''):
#             pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else: 
#             pdf.set_xy(10,115)
#             pdf.multi_cell(185, 3,"Remarks :")
#             pdf.set_xy(10,118)
#             pdf.multi_cell(185, 3,pcomp_pscav_value )

#         pdf.image("./images/pcomp_pscav.png",105,32,w=108,h=80) 
#         pdf.set_font("Arial",'B', size=15)
#         pdf.set_xy(10,140)
#         pdf.cell(1, 8,"Test Data" ,ln=True) 
        
#         spacing=3
#         tablefirst_head9 = [['Date of Measurment', 'Pscav (Bar)', 'Pcomp (Bar)']]
#         tablefirst9 = data25.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst_head9:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst9:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial",'B', size=15)
#         #pdf.set_xy(10,130)
#         pdf.cell(10,35,"Shop Trial Data" ,ln=True)
#         pdf.set_xy(10,220)
        
#         spacing=3
#         tablefirst_head10 = [['Pscav (Bar)', 'Pcomp (Bar)']]
#         tablefirst10 = data26.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst_head10:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst10:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
        
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
#     #*********************************************** 7 page **********************************************************#  
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, '6.Texh Vs Engine Load',ln=True,align='C') 
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         pdf.image("./images/engine_load_texh_daigram.png",2,32,w=110,h=80)
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         if (engine_load_texh_value=='') | (engine_load_texh_value==' '):
#             pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else: 
#             pdf.set_xy(10,115)
#             pdf.multi_cell(185, 3,"Remarks :")
#             pdf.set_xy(10,118)
#             pdf.multi_cell(185, 3,engine_load_texh_value )

#         pdf.image("./images/engine_load_corr_texh.png",105,32,w=108,h=80) 
#         pdf.set_font("Arial",'B', size=15)
#         pdf.set_xy(10,140)
#         pdf.cell(1, 8,"Test Data" ,ln=True)    
        
#         spacing=3
#         tablefirst_head11 = [['Date of Measurment', 'Engine Load (%)', 'Texh (deg.C)']]
#         tablefirst11 = data30.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst_head11:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst11:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial",'B', size=15)
#         #pdf.set_xy(10,130)
#         pdf.cell(10,35,"Shop Trial Data" ,ln=True)
#         pdf.set_xy(10,220)
        
#         spacing=3
#         tablefirst_head12 = [['Engine Load (%)', 'Texh (deg.C)']]
#         tablefirst12 = data31.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst_head12:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst12:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
        
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
#     #*********************************************** 8 page **********************************************************#  
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, '7.T/C Speed Vs Engine Load',ln=True,align='C') 
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)   
#         pdf.image("./images/engine_load_tc_daigram.png",2,32,w=110,h=80)
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         if (speed_load_value==' ') | (speed_load_value==''):
#             pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else: 
#             pdf.set_xy(10,115)
#             pdf.multi_cell(185, 3,"Remarks :")
#             pdf.set_xy(10,118)
#             pdf.multi_cell(185, 3,speed_load_value )
            
#         pdf.image("./images/engine_load_corr_tc.png",105,32,w=108,h=80) 
#         pdf.set_font("Arial",'B', size=15)
#         pdf.set_xy(10,140)
#         pdf.cell(1, 8,"Test Data" ,ln=True)  
        
#         spacing=3
#         tablefirst_head13 = [['Date of Measurment', 'Engine Load (%)', 'T/C Speed (rpm)']]
#         tablefirst13 = data35.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst_head13:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /3.5
#         row_height = pdf.font_size
#         for row in tablefirst13:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial",'B', size=15)
#         #pdf.set_xy(10,130)
#         pdf.cell(10,35,"Shop Trial Data" ,ln=True)
#         pdf.set_xy(10,220)
        
#         spacing=3
#         tablefirst_head14 = [['Engine Load (%)', 'T/C Speed (rpm)']]
#         tablefirst14 = data36.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst_head14:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
            
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst14:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#             pdf.ln(row_height*spacing)
        
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

#         #*********************************************** 9 page **********************************************************#
        

#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, '8.SFOC Vs Engine Load',ln=True,align='C')
#         pdf.set_font("Arial",'B', size=8)
#         pdf.set_text_color(0,0,0)
#         pdf.image("./images/engine_load_sfoc_daigram.png",2,32,w=110,h=80)
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
        

#         pdf.image("./images/engine_load_sfoc.png",105,32,w=108,h=80)
        
#         pdf.image("./images/sfoc_trend.png",5,142,w=195,h=130)
#         if (load_sfoc_value=='') | (load_sfoc_value==' '):
#             pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else:
#             pdf.set_xy(10,115)
#             pdf.multi_cell(185, 3,"Remarks :")
#             pdf.set_xy(10,118)
#             pdf.multi_cell(185, 3,load_sfoc_value )
            
        
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
#         #*********************************************** 9b page **********************************************************#
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=15)
#         pdf.set_xy(10,20)
#         pdf.cell(1, 8,"Test Data" ,ln=True)
        
#         pdf.set_xy(10,30)
        
#         spacing=3
#         tablefirst_head15 = [['Date of Measurment', 'Engine Load', 'SFOC (g/kW-hr)','SFOC Shop Trail', 'Deviation', 'Result']]
#         tablefirst15 = data40.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /6.8
#         row_height = pdf.font_size
#         for row in tablefirst_head15:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
        
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /6.8
#         row_height = pdf.font_size
#         for row in tablefirst15:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1)
#             pdf.ln(row_height*spacing)
        
#         pdf.set_font("Arial",'B', size=15)
#         #pdf.set_xy(10,130)
#         pdf.cell(10,35,"Shop Trial Data" ,ln=True)
#         pdf.set_xy(10,110)
        

#         spacing=3
#         tablefirst_head16 = [['Engine Load', 'SFOC (g/kW-hr)']]
#         tablefirst16 = data41.values.tolist()
#         pdf.set_font("Arial",'B', size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst_head16:
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#             pdf.ln(row_height*spacing)
        
#         pdf.set_font("Arial", size=7)
#         pdf.set_text_color(0,0,0)
#         col_width = pdf.w /2.33
#         row_height = pdf.font_size
#         for row in tablefirst16:
#             for item in row:
#                 pdf.cell(col_width, row_height*spacing,txt=item, border=1)
#             pdf.ln(row_height*spacing)
        

#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


#     #*********************************************** 10 page **********************************************************#  
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, '9.Pump Mark Vs Engine Speed',ln=True,align='C')
#         if data42_to_change == 'null':
#             pdf.set_xy(10,30)
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
            
#             pdf.set_font("Arial",'B', size=14)
#             pdf.set_xy(10,50)
#             pdf.cell(1, 8,"Deviation" ,ln=True)
            
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
            
#             pdf.set_font("Arial",'B', size=14)
#             pdf.set_xy(10,80)
#             pdf.cell(1, 8,"Test Data" ,ln=True)
            
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
            
#             pdf.set_font("Arial",'B', size=14)
#             pdf.set_xy(10,110)
#             pdf.cell(1, 8,"Shop Trial Data" ,ln=True)
            
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
#         elif(data42_to_change == 'yes'):    
#             pdf.set_font("Arial",'B', size=8)
#             pdf.set_text_color(0,0,0)            
#             pdf.image("./images/engine_speed_corrected_pumpmark_daigram.png",2,32,w=110,h=80)
#             pdf.set_font("Arial",'B', size=7)
#             pdf.set_text_color(0,0,0)
        
#             if (engine_speed_corrected_pumpmark_value=='') | (engine_speed_corrected_pumpmark_value==' '):
#                 pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
#             else: 
#                 pdf.set_xy(10,115)
#                 pdf.multi_cell(185, 3,"Remarks :")
#                 pdf.set_xy(10,118)
#                 pdf.multi_cell(185, 3,engine_speed_corrected_pumpmark_value )
#             pdf.image("./images/engine_speed_corrected_pump_deviation.png",105,32,w=108,h=80) 
#             pdf.set_font("Arial",'B', size=15)
#             pdf.set_xy(10,140)
#             pdf.cell(1, 8,"Test Data" ,ln=True)  
        
#             spacing=3
#             tablefirst_head17 = [['Date of Measurment', 'Engine Speed', 'Pump Mark']]
#             tablefirst17 = data45.values.tolist()
#             pdf.set_font("Arial",'B', size=7)
#             pdf.set_text_color(0,0,0)
#             col_width = pdf.w /3.5
#             row_height = pdf.font_size
#             for row in tablefirst_head17:
#                 pdf.set_text_color(255,255,255)
#                 pdf.set_fill_color(21,55,188)
#                 for item in row:
#                     pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#                 pdf.ln(row_height*spacing)
            
#             pdf.set_font("Arial", size=7)
#             pdf.set_text_color(0,0,0)
#             col_width = pdf.w /3.5
#             row_height = pdf.font_size
#             for row in tablefirst17:
#                 for item in row:
#                     pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#                 pdf.ln(row_height*spacing)
        
#             pdf.set_font("Arial",'B', size=15)
#             #pdf.set_xy(10,130)
#             pdf.cell(10,35,"Shop Trial Data" ,ln=True)
#             pdf.set_xy(10,220)
        
#             spacing=3
#             tablefirst_head18 = [['Engine Speed', 'Pump Mark']]
#             tablefirst18 = data46.values.tolist()
#             pdf.set_font("Arial",'B', size=7)
#             pdf.set_text_color(0,0,0)
#             col_width = pdf.w /2.33
#             row_height = pdf.font_size
#             for row in tablefirst_head18:
#                 pdf.set_text_color(255,255,255)
#                 pdf.set_fill_color(21,55,188)
#                 for item in row:
#                     pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#                 pdf.ln(row_height*spacing)
            
#             pdf.set_font("Arial", size=7)
#             pdf.set_text_color(0,0,0)
#             col_width = pdf.w /2.33
#             row_height = pdf.font_size
#             for row in tablefirst18:
#                 for item in row:
#                     pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#                 pdf.ln(row_height*spacing)
        
        
        
        
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
#     #*********************************************** 11 page **********************************************************#  
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, '10.Pmax - Pcomp Vs Pump Mark',ln=True,align='C') 
#         if data47_to_change=='null':
#             pdf.set_xy(10,30)
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
            
#             pdf.set_font("Arial",'B', size=14)
#             pdf.set_xy(10,50)
#             pdf.cell(1, 8,"Deviation" ,ln=True)
            
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
            
#             pdf.set_font("Arial",'B', size=14)
#             pdf.set_xy(10,80)
#             pdf.cell(1, 8,"Test Data" ,ln=True)
            
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
            
#             pdf.set_font("Arial",'B', size=14)
#             pdf.set_xy(10,110)
#             pdf.cell(1, 8,"Shop Trial Data" ,ln=True)
            
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
#         elif(data47_to_change == 'yes'):    
#             pdf.set_font("Arial",'B', size=8)
#             pdf.set_text_color(0,0,0)      
#             pdf.image("./images/pmax_pcomp_pump_mark_daigram.png",2,32,w=110,h=80)
#             pdf.set_font("Arial",'B', size=7)
#             pdf.set_text_color(0,0,0)
#             if (pmax_pcomp_pump_mark_value=='') | (pmax_pcomp_pump_mark_value==' '):
#                 pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
#             else: 
#                 pdf.set_xy(10,115)
#                 pdf.multi_cell(185, 3,"Remarks :")
#                 pdf.set_xy(10,118)
#                 pdf.multi_cell(185, 3,pmax_pcomp_pump_mark_value )
#             pdf.image("./images/pmax_pcomp_pump_mark_deviation.png",105,32,w=108,h=80) 
#             pdf.set_font("Arial",'B', size=15)
#             pdf.set_xy(10,140)
#             pdf.cell(1, 8,"Test Data" ,ln=True)  
        
#             spacing=3
#             tablefirst_head19 = [['Date of Measurment','Pump Mark','Pmax - Pcomp']]
#             tablefirst19 = data50.values.tolist()
#             pdf.set_font("Arial",'B', size=7)
#             pdf.set_text_color(0,0,0)
#             col_width = pdf.w /3.5
#             row_height = pdf.font_size
#             for row in tablefirst_head19:
#                 pdf.set_text_color(255,255,255)
#                 pdf.set_fill_color(21,55,188)
#                 for item in row:
#                     pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#                 pdf.ln(row_height*spacing)
            
#             pdf.set_font("Arial", size=7)
#             pdf.set_text_color(0,0,0)
#             col_width = pdf.w /3.5
#             row_height = pdf.font_size
#             for row in tablefirst19:
#                 for item in row:
#                     pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#                 pdf.ln(row_height*spacing)
        
#             pdf.set_font("Arial",'B', size=15)
#             #pdf.set_xy(10,130)
#             pdf.cell(10,35,"Shop Trial Data" ,ln=True)
#             pdf.set_xy(10,220)
        
#             spacing=3
#             tablefirst_head20 = [['Pump Mark','Pmax - Pcomp']]
#             tablefirst20 = data51.values.tolist()
#             pdf.set_font("Arial",'B', size=7)
#             pdf.set_text_color(0,0,0)
#             col_width = pdf.w /2.33
#             row_height = pdf.font_size
#             for row in tablefirst_head20:
#                 pdf.set_text_color(255,255,255)
#                 pdf.set_fill_color(21,55,188)
#                 for item in row:
#                     pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
#                 pdf.ln(row_height*spacing)
            
#             pdf.set_font("Arial", size=7)
#             pdf.set_text_color(0,0,0)
#             col_width = pdf.w /2.33
#             row_height = pdf.font_size
#             for row in tablefirst20:
#                 for item in row:
#                     pdf.cell(col_width, row_height*spacing,
#                         txt=item, border=1)
#                 pdf.ln(row_height*spacing)
        
#         #Page Number
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
#     #*********************************************** 12 page **********************************************************#  
#         pdf.add_page()
#         pdf.set_font("Arial",'B', size=20)

#         #pdf.image("./images/Power_curve.png",5,10)
#         pdf.image("./images/Power_curve.png",10,20,w=180,h=220)
#         pdf.set_text_color(25,47,133)
#         pdf.cell(180, 10, 'Power Curve',ln=True,align='C') 
#         #Page Number
#         pdf.set_text_color(0,0,0)
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % (pdf.page_no()),align="R")

#     #*********************************************** 13 page **********************************************************#
#         pdf.add_page()
#         pdf.set_text_color(25,47,133)
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_xy(10,10)
#         pdf.cell(180,20,txt ='Cylinder Comparison', align='C')

#         pdf.set_font("Arial",'B', size=12)
#         pdf.set_text_color(0,0,0)

        
#         pdf.image("./images/Pmax_mean.png",3,50,w=110,h=80) 
#         pdf.image("./images/Pmax_deviation.png",106,50,w=110,h=80) 

#         pdf.set_xy(10,30)
#         pdf.cell(70, 30,"1) Maximum Pressure" )
#         pdf.set_font("Arial",'B', size=8)
#         if (Pmax_Deviation_value==' ') | (Pmax_Deviation_value==''):
#             pdf.set_xy(15,40)
#             pdf.cell(10, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else:
#             pdf.set_xy(15,130)
#             pdf.multi_cell(185, 3,"Remarks :")
#             pdf.set_xy(15,133)
#             pdf.multi_cell(185, 3,Pmax_Deviation_value )
            
#         pdf.set_xy(10,170) 
#         Pmax_data= [['Cylinder Number','Measured Value (bar)','Average value','(Measured)-(Average)',"Result"]]
#         pdf.set_font("Arial", "B",size=8)
#         col_width = pdf.w /5.88
#         row_height = pdf.font_size
#         for row in Pmax_data:
#             pdf.cell(5.2)
#             pdf.set_text_color(255,255,255)
#             pdf.set_fill_color(21,55,188)
#             for item in row:
#                 pdf.cell(col_width, row_height*3,
#                         txt=item, border=1, fill=True)
#             pdf.ln(row_height*3)   
            
#         pdf.set_text_color(0,0,0)  
#         pdf.set_font("Arial", "B",size=8)
#         col_width = pdf.w /5.88
#         row_height = pdf.font_size-.5
#         for row in Pmax_data1:
#             pdf.cell(5.2)
#             pdf.set_fill_color(255, 255, 255 )
#             for item in row:
#                 pdf.cell(col_width, row_height*3,
#                         txt=item, border=1, fill=True)
#             pdf.ln(row_height*3)
        
        
#         #Page Number
#         pdf.set_text_color(0,0,0)
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
#     #*********************************************** 14 page **********************************************************# 
#         pdf.add_page()
#         pdf.set_text_color(25,47,133)
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_xy(10,10)
#         #pdf.multi_cell(180,20,txt ='Cylinder Comparison', align='C')

#         pdf.set_font("Arial",'B', size=12)
#         pdf.set_text_color(0,0,0)

        
#         pdf.image("./images/Pcomp_mean.png",3,50,w=110,h=80) 
#         pdf.image("./images/Pcomp_deviation.png",106,50,w=110,h=80) 

#         pdf.set_xy(10,30)
#         pdf.cell(70, 20,"2) Compressor Pressure" )
#         pdf.set_font("Arial",'B', size=8)
#         if (Pcomp_Deviation_value=='') | (Pcomp_Deviation_value==' '):
#             pdf.set_xy(15,40)
#             pdf.cell(10, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else:
#             pdf.set_xy(15,130)
#             pdf.multi_cell(185, 3,"Remarks :" )
#             pdf.set_xy(15,133)
#             pdf.multi_cell(185, 3,Pcomp_Deviation_value)
            
#         pdf.set_xy(10,170) 
#         Pmax_data= [['Cylinder Number','Measured Value (bar)','Average value','(Measured)-(Average)',"Result"]]
#         pdf.set_font("Arial", "B",size=8)
#         col_width = pdf.w /5.88
#         row_height = pdf.font_size
#         for row in Pmax_data:
#             pdf.cell(5.2)
#             pdf.set_text_color(253,253,253)   
#             pdf.set_fill_color(1, 0, 173 )
#             for item in row:
#                 pdf.cell(col_width, row_height*3,
#                         txt=item, border=1, fill=True)
#             pdf.ln(row_height*3)
        
#         pdf.set_text_color(4,4,5)  
#         pdf.set_font("Arial", "B",size=8)
#         col_width = pdf.w /5.88
#         row_height = pdf.font_size-.5
#         for row in Pcomp_data1:
#             pdf.cell(5.2)
#             pdf.set_fill_color(255, 255, 255 )
#             for item in row:
#                 pdf.cell(col_width, row_height*3,
#                         txt=item, border=1, fill=True)
#             pdf.ln(row_height*3)
        
        
#         #Page Number
#         pdf.set_text_color(0,0,0)
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        
#     #*********************************************** 15 page **********************************************************# 
#         pdf.add_page()
#         pdf.set_text_color(25,47,133)
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_xy(10,10)
#         #pdf.multi_cell(180,20,txt ='Cylinder Comparison', align='C')

#         pdf.set_font("Arial",'B', size=12)
#         pdf.set_text_color(0,0,0)

        
#         pdf.image("./images/Texh_mean.png",3,50,w=110,h=80) 
#         pdf.image("./images/Texh_deviation.png",105,50,w=110,h=80) 

#         pdf.set_xy(10,30)
#         pdf.cell(70, 20,"3) M/E Cylinder Exhaust Temperature" )
#         pdf.set_font("Arial",'B', size=8)
#         if (Texh_Deviation_value=='') | (Texh_Deviation_value==' '):
#             pdf.set_xy(15,40)
#             pdf.cell(10, 195,"Remarks :"+" "+'Normal' ,ln=True)
#         else:
#             pdf.set_xy(15,130)
#             pdf.multi_cell(185, 3,"Remarks :" )
#             pdf.set_xy(15,133)
#             pdf.multi_cell(185, 3,Texh_Deviation_value)
            
#         pdf.set_xy(10,170) 
#         Pmax_data= [['Cylinder Number','Measured Value (Deg)','Average value','(Measured)-(Average)',"Result"]]
#         pdf.set_font("Arial", "B",size=8)
#         col_width = pdf.w /5.88
#         row_height = pdf.font_size
#         for row in Pmax_data:
#             pdf.cell(5.2)
#             pdf.set_text_color(253,253,253)   
#             pdf.set_fill_color(1, 0, 173 )
#             for item in row:
#                 pdf.cell(col_width, row_height*3,
#                         txt=item, border=1, fill=True)
#             pdf.ln(row_height*3)
        
#         pdf.set_text_color(4,4,5)  
#         pdf.set_font("Arial", "B",size=8)
#         col_width = pdf.w /5.88
#         row_height = pdf.font_size-.5
#         for row in Texh_data1:
#             pdf.cell(5.2)
#             pdf.set_fill_color(255, 255, 255 )
#             for item in row:
#                 pdf.cell(col_width, row_height*3,
#                         txt=item, border=1, fill=True)
#             pdf.ln(row_height*3)   
        
        
#         #Page Number
#         pdf.set_text_color(0,0,0)
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
#     #*********************************************** 16 page **********************************************************#   
#         pdf.add_page()
#         pdf.set_text_color(25,47,133)
#         pdf.set_font("Arial",'B', size=18)
#         pdf.set_xy(10,10)
#         pdf.set_font("Arial",'B', size=12)
#         pdf.set_text_color(0,0,0)
#         pdf.set_xy(10,30)
#         pdf.cell(70, 20,"4) Pumpmark" )
        
#         if data63_to_change=='null':
#             pdf.set_xy(10,50)
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
            
#             pdf.set_font("Arial",'B', size=14)
#             pdf.set_xy(10,70)
#             pdf.cell(1, 8,"Deviation" ,ln=True)
            
#             pdf.set_font("Arial", size=10)
#             pdf.set_text_color(0,0,0) 
#             pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
            
#         elif(data63_to_change == 'yes'):    
        
#             pdf.set_font("Arial",'B', size=8)
#             pdf.image("./images/pmark_deviation.png",50,42,w=120,h=80)
#             if (Pumpmark_Deviation_value=='') | (Pumpmark_Deviation_value==' '):
#                 pdf.set_xy(15,40)
#                 pdf.cell(10, 195,"Remarks :"+" "+'Normal' ,ln=True)
#             else:
#                 pdf.set_xy(15,130)
#                 pdf.multi_cell(185, 3,"Remarks :" )
#                 pdf.set_xy(15,133)
#                 pdf.multi_cell(185, 3,Pumpmark_Deviation_value)
            
#             pdf.set_xy(10,170) 
#             Pmax_data= [['Cylinder Number','Measured Value (Deg)','Average value','(Measured)-(Average)',"Result"]]
#             pdf.set_font("Arial", "B",size=8)
#             col_width = pdf.w /5.88
#             row_height = pdf.font_size
#             for row in Pmax_data:
#                 pdf.cell(5.2)
#                 pdf.set_text_color(253,253,253)   
#                 pdf.set_fill_color(1, 0, 173 )
#                 for item in row:
#                     pdf.cell(col_width, row_height*3,
#                         txt=item, border=1, fill=True)
#                 pdf.ln(row_height*3)
        
#             pdf.set_text_color(4,4,5)  
#             pdf.set_font("Arial", "B",size=8)
#             col_width = pdf.w /5.88
#             row_height = pdf.font_size-.5
#             for row in Pmark_data1:
#                 pdf.cell(5.2)
#                 pdf.set_fill_color(255, 255, 255 )
#                 for item in row:
#                     pdf.cell(col_width, row_height*3,
#                         txt=item, border=1, fill=True)
#                 pdf.ln(row_height*3)   
        
        
#         #Page Number
#         pdf.set_text_color(0,0,0)
#         pdf.set_y(273)
#         pdf.set_font('Arial', 'I', 8)
#         pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
#         print("Last----------------------------")
        
#         pdf.output('./documents/msc_ME_REPORT.pdf','F')
#         # pdf.output('./documents/python1.pdf', 'F')
#         # pdf.output('./documents/./msc_ME_PERFORMANCE_FOLDER/msc_PERFORMANCE_report_with_api.pdf')
   
#     simple_table()

    

#     return FileResponse(path = './documents/msc_ME_REPORT.pdf',filename='ME_REPORT.pdf')


@router.post('/api/v1/pdf/environmental/yearly')
async def index(info:Request ,input_mvg: str = None , CDate_1_start:str = None , CDate_1_end:str = None , CDate_2_start:str = None , CDate_2_end:str = None ):
    s = await info.json()
    try:
        s['year1']
    except:
        return {'data':[]}

    if not s:
        return {'data':[]}

    print(input_mvg ,CDate_1_start ,CDate_1_end ,CDate_2_start,CDate_2_end)

    # input_mvg="1"
    # Comparison_Date_1_Starting="2019-01-01"
    # Comparison_Date_1_Ending="2019-12-31"
    # Comparison_Date_2_Starting="2020-01-01"
    # Comparison_Date_2_Ending="2020-12-31"

    Comparison_Date_1=CDate_1_start+" - "+CDate_1_end
    Comparison_Date_2=CDate_2_start+" - "+CDate_2_end

    year1 = pd.DataFrame.from_dict(s['year1']['finaldata'])
    year2 = pd.DataFrame.from_dict(s['year2']['finaldata'])
    year1 = year1.astype(str)
    year2 = year2.astype(str)
    starting_year=year1[["year"]]
    Ending_year=year2[["year"]]
    Heading="YEAR"+"  "+starting_year+" - "+Ending_year+"  "+"EEOI ANALYSIS"
    Vessel_Name=year1[["vessel_name"]]
    table1_df = pd.DataFrame.from_dict(s['table1']['table1'])
    table1_df = table1_df.rename(columns={'index': 'Year', "improvement": '% Improvement','year1': starting_year['year'].values[0],'year2': Ending_year['year'].values[0]})
    table1_df["% Improvement"]=table1_df["% Improvement"].astype("float64")
    table1_model=table1_df[["Year",starting_year['year'].values[0],Ending_year['year'].values[0],"% Improvement"]]
    table1_model["% Improvement"]=table1_model["% Improvement"].astype(str)+"%"
    table1_model = table1_model.astype(str)
    table1_df_graph = table1_df.set_index(['Year'])
    table1_df_graph = table1_df_graph.loc[["EEOI for Cargo [MT]", "Total equiv. HFO [Kilo MT]","Total equiv. HFO [Kilo MT]"]]
    table1_df_graph_new=table1_df_graph[[starting_year['year'].values[0],Ending_year['year'].values[0]]]
    table1_df_graph_new_sum_year_1=table1_df_graph_new[starting_year['year'].values[0]].sum()
    table1_df_graph_new_sum_year_2=table1_df_graph_new[Ending_year['year'].values[0]].sum()
    table1_df_graph_new_sum_Total=table1_df_graph_new_sum_year_1+table1_df_graph_new_sum_year_2
    #For 1 st Graph
    table1_df_graph_a = table1_df_graph_new.plot.bar(rot=0, color={starting_year['year'].values[0]: "Blue", Ending_year['year'].values[0]: "red"},width=0.8)
    plt.xlabel(" ", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.ylabel("  ", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.title('EEOI Analysis', size=15,fontweight="bold",fontname="Times New Roman")
    table1_df_graph_a.bar_label(table1_df_graph_a.containers[0])
    table1_df_graph_a.bar_label(table1_df_graph_a.containers[1])
    # Set general font size
    plt.rcParams['font.size'] = '7'
    # Set tick font size
    for label in (table1_df_graph_a.get_xticklabels() + table1_df_graph_a.get_yticklabels()):
        label.set_fontsize(8)
    plt.savefig('images/Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly  SEABORN.png')
    plt.clf()
    table1_df_graph_a = table1_df_graph_new.plot.bar(rot=0, color={starting_year['year'].values[0]: "Blue", Ending_year['year'].values[0]: "red"},width=0.8)
    plt.xlabel(" ", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.ylabel("  ", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.title('EEOI Analysis', size=15,fontweight="bold",fontname="Times New Roman")
    table1_df_graph_a.bar_label(table1_df_graph_a.containers[0])
    table1_df_graph_a.bar_label(table1_df_graph_a.containers[1])
    # Set general font size
    plt.rcParams['font.size'] = '7'
    # Set tick font size
    for label in (table1_df_graph_a.get_xticklabels() + table1_df_graph_a.get_yticklabels()):
        label.set_fontsize(8)
    plt.savefig('images/Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly  SEABORN.png')
    plt.clf()
    #2nd Table
    table1_df_graph = table1_df_graph.loc[["CO2[MT/NM]", "EEOI for Cargo [MT]","Total equiv. HFO [Kilo MT]"]].reset_index()
    table1_graph=table1_df_graph[['% Improvement', '2020','2019']]
    table1_graph_T=table1_graph.T.reset_index()
    table1_graph_T = table1_graph_T.astype(str)
    #2nd Graph
    table1_graph_Improvement=table1_df_graph[["Year","% Improvement"]]
    table1_graph_Improvement_sum=table1_graph_Improvement["% Improvement"].sum()

    #2nd Graph For Improvement
    plt.figure(figsize=(10,5))
    Improvement_Bar=sns.barplot( x="Year", y="% Improvement",data = table1_graph_Improvement,color="#050952",errwidth=0 )
    plt.xlabel(" ", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.ylabel("% Improvement", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.title('Yearly % Improvement EEOI Analysis', size=15,fontweight="bold",fontname="Times New Roman")# fontname="Times New Roman"
    Improvement_Bar.bar_label(Improvement_Bar.containers[0])
    #plt.rcParams['font.size'] = '10'
    # Set general font size
    plt.rcParams['font.size'] = '7'
    # Set tick font size
    for label in (Improvement_Bar.get_xticklabels() + Improvement_Bar.get_yticklabels()):
        label.set_fontsize(8)
    plt.savefig('images/Environment- Yearly- Improvement Bar Graph- Yearly  SEABORN.png')
    plt.clf()
    #Moving Average Year1 and Year2
    mvg_year1 = pd.DataFrame.from_dict(s['year1']['moving data average'])
    mvg_year2 = pd.DataFrame.from_dict(s['year2']['moving data average'])
    MVG_Total_sum=mvg_year1["EEOI for Cargo [MT]"].sum()+mvg_year2["EEOI for Cargo [MT]"].sum()

    Mvg_Legend_Year1=input_mvg+" "+"Moving Avg"+" "+starting_year['year'].values[0]
    Mvg_Legend_Year2=input_mvg+" "+"Moving Avg"+" "+Ending_year['year'].values[0]
    #Moving Average - Graph 3

    plt.figure(figsize=(10,5))
    MVG_1=sns.lineplot(x = "S.No",y = "movingavg2mt",data = mvg_year1,color="#050952" ,marker="o",markersize=8,label=Mvg_Legend_Year1)
    MVG_2=sns.lineplot(x = "S.No",y = "movingavg2mt",data = mvg_year2,color="#08a615",marker="o",markersize=8,label=Mvg_Legend_Year2)
    plt.xlabel(" ", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.ylabel("Moving Average", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.title('EEOI Moving Average [MT]', size=15,fontweight="bold",fontname="Times New Roman")# fontname="Times New Roman"
    plt.savefig('images/Environment- Yearly Analysis - Moving Average.png  SEABORN.png')
    plt.clf()

    #------------------------------------------------------------------------------------------------------------------------------#
    #PDF CODE 

    def simple_table(spacing=2.5):
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
        
        #Page Number
        pdf.set_y(265)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")
        
        #Logo
        # pdf.image(oceanix_logo_path,20,30,w=30)
        pdf.image(msc_logo_path,160,24,w=30)
        
        #Main Heading
        pdf.set_font('Arial', 'B', 18)
        pdf.set_xy(50,52)
        pdf.set_text_color(25,47,133)
        pdf.multi_cell(115, 8, Heading['year'].values[0],align='C')
        pdf.set_line_width(1)
        pdf.line(10, 61, 199, 61)#(x_start, y_start, x_end, y_end)
        
        #Vessel Name
        pdf.set_font('Arial', '', 13)
        pdf.set_text_color(0,0,0)
        pdf.set_xy(10,66)
        pdf.multi_cell(90, 7,"Vessel Name  : ",align='L')
        pdf.set_xy(55,66)
        pdf.multi_cell(90, 7,Vessel_Name['vessel_name'].values[0],align='L') 
        pdf.set_xy(10,73)
        pdf.multi_cell(90, 7,"Comparison Date 1 : ",align='L')
        pdf.set_xy(55,73)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(90, 7,Comparison_Date_1,align='L') 
        pdf.set_xy(10,80)
        pdf.set_font('Arial', '', 13)
        pdf.multi_cell(90, 7,"Comparison Date 2 : ",align='L')
        pdf.set_xy(55,80)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(90, 7,Comparison_Date_2,align='L')    
        pdf.set_line_width(0)
        pdf.line(10, 90, 199, 90)
        
        #Table 1
        pdf.set_xy(10,98)
        pdf.set_line_width(0)
        Table_1_head_Year=[['Year', '2019', '2020', '% Improvement']]
        Table_1_Year = table1_model.values.tolist()
        pdf.set_font("Arial","B", size=9)
        col_width = pdf.w / 4.44
        row_height = pdf.font_size
        
        for row in Table_1_head_Year:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial","", size=7.7)
        pdf.set_text_color(0,0,0)
        for row in Table_1_Year:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
    #------------------------------------------------------------------------------------------------------------------------------#
        #2nd Page
        pdf.add_page()
        
        #Yearly EEOI Analysis Heading
        pdf.set_font('Arial', 'B', 15)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(10,20)
        pdf.cell(180, 7,"YEARLY EEOI ANALYSIS",ln=True,align='L')
        pdf.set_text_color(0,0,0)
        
        #Table 2
        pdf.set_xy(10,30)

        Table_2_head_Year=[["Year","CO2[MT/NM]", "EEOI for Cargo [MT]","Total equiv. HFO [Kilo MT]"]]
        Table_2_Year = table1_graph_T.values.tolist()
        pdf.set_font("Arial","B", size=9)
        col_width = pdf.w / 4.44
        row_height = pdf.font_size
        
        for row in Table_2_head_Year:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial","", size=7.7)
        pdf.set_text_color(0,0,0)
        for row in Table_2_Year:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            

        if table1_df_graph_new_sum_Total.sum()==0:
            pdf.set_xy(80,100)

            pdf.set_font('Arial', 'B', 15)
            pdf.multi_cell(50,20,"No Data Available",align='C')
        else:
            #Setting Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly
            pdf.image("./images/Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly  SEABORN.png",32,62,w=145,h=90) 
        
        
        #Yearly % Improvment EEOI Analysis Heading
        pdf.set_font('Arial', 'B', 15)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(10,167)
        pdf.cell(170, 7,"YEARLY % IMPROVEMENT - EEOI ANALYSIS",ln=True,align='L')
        pdf.set_text_color(0,0,0)
        
        if table1_graph_Improvement_sum==0:
            pdf.set_xy(80,213)

            pdf.set_font('Arial', 'B', 15)
            pdf.multi_cell(50,20,"No Data Available",align='C')
        else:
            #Setting Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly
            pdf.image("./images/Environment- Yearly- Improvement Bar Graph- Yearly  SEABORN.png",32,175,w=145,h=90)
        
        #Page Number 2
        pdf.set_y(265)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")
        
    #------------------------------------------------------------------------------------------------------------------------------#
        #3rd Page
        pdf.add_page()

        #Yearly % Improvment EEOI Analysis Heading
        pdf.set_font('Arial', 'B', 15)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(10,20)
        pdf.cell(170, 7,"YEARLY EEOI MOVING AVERAGE",ln=True,align='L')
        pdf.set_text_color(0,0,0)
        
        if MVG_Total_sum==0:
            pdf.set_xy(80,68)

            pdf.set_font('Arial', 'B', 15)
            pdf.multi_cell(50,20,"No Data Available",align='C')
        else:
        #Setting Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly
            pdf.image("./images/Environment- Yearly Analysis - Moving Average.png  SEABORN.png",33.5,30,w=145,h=90)
        
        
        
        
        
        
        #Page Number 3
        pdf.set_y(265)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")


    #------------------------------------------------------------------------------------------------------------------------------#
        pdf.output('./documents/msc - Environment Monitoring - Yearly Analysis  SEABORN.pdf','F')
   
    # pdf_name = 'environmental_yearl'
    simple_table()
    return FileResponse(path = './documents/msc - Environment Monitoring - Yearly Analysis  SEABORN.pdf',filename='msc - Environment Monitoring - Yearly Analysis  SEABORN.pdf')
    


@router.post('/api/v1/pdf/imodcs')
async def index(info : Request , vessel_name: str = None , year : str = None):
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6IjhlYzg3Y2M3LTQyNjYtNDVmZi1hYTc3LTM4YzE2ZDIwNTgzMyIsImlhdCI6MTY2OTg3NjIzMiwiZXhwIjoxNjY5OTYyNjMyfQ.B7L4fEJij32qVDBG_z34WBnOc3H9NkGGkhdonWsowgE"
    headers = {'Authorization': "Bearer {}".format(token)}
    url="https://msc.oceanix.cloud/api/sysapi/api/v1/idcs/9648075?year=2020"
    
    input_parameter = "All Vesdsfdfsel"
    input_parameter_year = 2022
    input_parameter_group = 1
    input_parameter_fleet = 2

    s=requests.get(url , headers=headers).json()
    data1 = pd.DataFrame.from_dict([s['data']])
    data1=data1.T
    data1 = data1.astype(str).reset_index()
    data1 = data1.rename(columns={'index': 'Title', 0: 'Particulars'})
    data2 = pd.DataFrame.from_dict([s['data2']])
    data2['year'] = input_parameter_year
    data2['Group'] = input_parameter_group
    data2['Fleet'] = input_parameter_fleet
    data2 = data2.astype(str)
    data3=data2[["Hours","Distance","Starting","Ending"]]
    data3 = data3.rename(columns={'Hours': 'Hours Underway (h)', "Distance": 'Distance Travelled (Nm)','Starting': 'Starting Date', "Ending": 'Ending Date'})
    data3=data3.T.reset_index()
    data3 = data3.rename(columns={'index': 'Title_1', 0: 'Particulars_1'})
    data4=data2[['Method used to Measure FO Consumption', 'others', 'Ethanol',
        'Methanol', 'LNG', 'LPG (Propane)', 'HFO', 'LFO', 'Diesel']]
    #LNG is missing
    #LNG (Cf : 2.750)
    data4 = data4.rename(columns={"others":"Others",'Ethanol': 'Ethanol (Cf : 1.913)', "Methanol": 'Methanol (Cf : 1.375)','LNG': 'LNG (Cf : 2.750)','LPG (Butane)': 'LPG (Butane) (Cf : 3.030)', "LPG (Propane)": 'LPG (Propane) (Cf : 3.000)', "HFO": 'HFO (Cf : 3.114)','LFO': 'LFO (Cf : 3.151)', "Diesel": 'Diesel/ Gas Oil (Cf : 3.206)'})
    data4=data4.T.reset_index()
    data4 = data4.rename(columns={'index': 'Title_2', 0: 'Particulars_3'})
   
    def simple_table(spacing=3):

        pdf = FPDF()
        pdf.add_page()

        #Page Number
        pdf.set_y(265)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")

        #Logo
        # pdf.image(oceanix_logo_path,20,30,w=30)
        pdf.image(msc_logo_path,160,24,w=30)

        #Cell postion from left side
        pdf.set_font('Arial', 'B', 18)
        pdf.set_xy(60,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(130, 90, 'ANNUAL EMISSION REPORT',ln=True)
        pdf.set_line_width(1)
        pdf.line(10, 65, 199, 65)#(x_start, y_start, x_end, y_end)

        #First table - Details of Vessel
        pdf.set_line_width(0)


        if input_parameter=="All Vessel":
                
            Table_1_head=[['Vessel Name', 'Year']]
            pdf.set_xy(10,70)

            pdf.set_font("Arial","B", size=9)
            col_width = pdf.w / 2.22
            row_height = pdf.font_size
        
            for row in Table_1_head:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)
            
            pdf.set_text_color(0,0,0)
            pdf.set_xy(10,79.8)
            pdf.multi_cell(94.38, 8, data1['Particulars'].values[0],border=True,align='L')
            pdf.set_xy(104.68,79.8)
            pdf.multi_cell(94.38, 8, data2['year'].values[0],border=True,align='L')
        
         

        else:
            Table_1_head=[['Vessel Name', 'Year',"Fleet","Group"]]
            pdf.set_xy(10,70)

            pdf.set_font("Arial","B", size=9)
            col_width = pdf.w / 4.44
            row_height = pdf.font_size
        
            for row in Table_1_head:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)
                
            pdf.set_text_color(0,0,0)
            pdf.set_xy(10,79.8)
            pdf.multi_cell(47.19, 8, data1['Particulars'].values[0],border=True,align='L')
            pdf.set_xy(57.34,79.8)
            pdf.multi_cell(47.19, 8, data2['year'].values[0],border=True,align='L')
            pdf.set_xy(104.48,79.8)
            pdf.multi_cell(47.19, 8, data2['Fleet'].values[0],border=True,align='L')
            pdf.set_xy(151.99,79.8)
            pdf.multi_cell(47.19, 8, data2['Group'].values[0],border=True,align='L')
        
        pdf.set_font('Arial', "B",13)
        pdf.set_xy(10,92)
        pdf.set_text_color(25,47,133)


        pdf.multi_cell(185,10,"SHIP PARTICULARS", align='L')
        pdf.set_draw_color(0,0,0)

        Data1 = data1.values.tolist()
        pdf.set_font("Arial","B", size=8)
        col_width = pdf.w / 2.22
        row_height = pdf.font_size
        
        pdf.set_font("Arial", size=8)
        pdf.set_text_color(0,0,0)
        for row in Data1:

            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1)
            pdf.ln(row_height*spacing)

        pdf.set_font('Arial', "B",13)
        pdf.set_xy(10,192)
        pdf.set_text_color(25,47,133)
        pdf.multi_cell(185,10,"ANNUAL FUEL CONSUMPTION REPORT", align='L')
        pdf.set_draw_color(0,0,0)

        Data3 = data3.values.tolist()
        pdf.set_font("Arial","B", size=8)
        col_width = pdf.w / 2.22
        row_height = pdf.font_size
        
        pdf.set_font("Arial", size=8)
        pdf.set_text_color(0,0,0)
        for row in Data3:

            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1)
            pdf.ln(row_height*spacing)
        
    #------------------------------------------------------------------------------------------------------------------------------#

        #2nd Page
        pdf.add_page()

        pdf.set_xy(10,20)
        Data4 = data4.values.tolist()
        pdf.set_font("Arial","B", size=8)
        col_width = pdf.w / 2.22
        row_height = pdf.font_size
        
        pdf.set_font("Arial", size=8)
        pdf.set_text_color(0,0,0)
        for row in Data4:

            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1)
            pdf.ln(row_height*spacing)

        #Page Number
        pdf.set_y(265)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")


        pdf.output('./documents/msc - IMO DCS - Annual Emission Report.pdf','F')
            
            
    simple_table()


    return FileResponse(path = './documents/msc - IMO DCS - Annual Emission Report.pdf',filename='msc - Environment Monitoring - Yearly Analysis  SEABORN.pdf')

@router.post('/api/v1/pdf/voyagecal/eta_foc')
async def index(info : Request , report_type: str = None , vessel_name:str = None,date_range:str=None,voyage_dist:str = None,draft:str=None,speed:str=None,fleet:str=None,group:str=None):
    s = await info.json()
    if not s:
        return {'data':[]}
        
    # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6IjhlYzg3Y2M3LTQyNjYtNDVmZi1hYTc3LTM4YzE2ZDIwNTgzMyIsImlhdCI6MTY2OTg3NjIzMiwiZXhwIjoxNjY5OTYyNjMyfQ.B7L4fEJij32qVDBG_z34WBnOc3H9NkGGkhdonWsowgE"
    # headers = {'Authorization': "Bearer {}".format(token)}
    # url="http://192.168.54.32:9111/api/v1/vc/eta_foc/9648075?date=From%20%2021%20Dec%202016%20%20To%20%2019%20Jun%202017&type=Noon&dis=5000&sp=12&dt=10"
    # s=requests.get(url , headers =  headers).json()
  
    DataTable_df = pd.DataFrame.from_dict(s['data']["tab1data"])
    DataTable_df = DataTable_df.rename(columns={'sea_state': 'SEASTATE', 'power': 'POWER (kW)', 'fo_24hrs': 'FO/24 Hrs (T)','fo_voyage': 'Fo Voyage'})
    DataTable = DataTable_df.astype(str)
    DataTable_first_graph=DataTable_df["FO/24 Hrs (T)"].sum()+DataTable_df["SEASTATE"].sum()
    DataTable_second_graph=DataTable_df["POWER (kW)"].sum()+DataTable_df["SEASTATE"].sum()

    # report_type = report

    if report_type=="All Vessel":
        Input_parameters={"data":[{"Vessel Name":vessel_name,
                "Analysis Date Range":date_range,
                "Voyage Distance":voyage_dist,
                "Draft":draft,
                "Speed":speed}]}
        print(Input_parameters)

    elif report_type=="Fleet Wise":
        Input_parameters={"data":[{"Vessel Name":vessel_name,
                "Analysis Date Range":date_range,
                "Voyage Distance":voyage_dist,
                "Draft":draft,
                "Speed":speed,
                "Fleet":fleet,
                "Group":group}]}
    print(Input_parameters)

    ETA = pd.DataFrame.from_dict(Input_parameters['data'])
    ETA=ETA.T
    ETA = ETA.astype(str).reset_index()
    ETA = ETA.rename(columns={'index': 'Input Parmeters', 0: 'Values'})    
        
    #ETA & FOC Calculator - FO/24 Hrs v/s Seastate

    #plt.figure(figsize=(10,5))
    sns.lineplot( x="SEASTATE", y="FO/24 Hrs (T)",data = DataTable_df,color="Blue",marker= "o",markersize=7)
    plt.xlabel("SEASTATE", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.ylabel("FO/24 Hrs (T)", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.title('FO/24 Hrs  v/s  Seastate', size=15,fontweight="bold",fontname="Times New Roman")# fontname="Times New Roman"
    plt.savefig('images/Seaborn Voyage Calculator- ETA and FOC-24 Hrs.png')
    plt.clf()

    #ETA & FOC Calculator - Power v/s Seastate

    #plt.figure(figsize=(10,5))
    sns.lineplot(  x="SEASTATE", y="POWER (kW)",data = DataTable_df,color="Blue",marker= "o",markersize=7)
    plt.xlabel("SEASTATE", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.ylabel("POWER (kW)", fontsize= 12,fontweight="bold",fontname="Times New Roman")
    plt.title('Power  v/s  Seastate', size=15,fontweight="bold",fontname="Times New Roman")# fontname="Times New Roman"
    plt.savefig('images/Seaborn Voyage Calculator- ETA and FOC -POWER (kW).png')
    plt.clf()

    def simple_table(spacing=3):

        pdf = FPDF()
        pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 

        pdf.add_page()
        pdf.set_y(265)
        #Page Number
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")

        # pdf.image(oceanix_logo_path,20,30,w=30)
        pdf.image(msc_logo_path,160,24,w=30)
    
        pdf.set_font('Arial', 'B', 18)
        pdf.set_xy(60,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(130, 90, 'ETA AND FOC CALCULATOR',ln=True)
        pdf.set_line_width(1)
        pdf.line(10, 65, 199, 65)#(x_start, y_start, x_end, y_end)
    
        pdf.set_xy(10,70)
        pdf.set_line_width(0)
        Table_1_head=[['Input Parmeters', 'Values']]
        Table_1 = ETA.values.tolist()
        pdf.set_font("Arial","B", size=9)
        col_width = pdf.w / 2.22
        row_height = pdf.font_size

        for row in Table_1_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        
    
            
            pdf.set_font("Arial","B", size=8)
            pdf.set_text_color(0,0,0)
            for row in Table_1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        
            #Data Table Heading
            pdf.set_font('Arial', "B",15)
            if report_type=="All Vessel":
                pdf.set_xy(10,133)
            else :
                pdf.set_xy(10,153)
                
            pdf.set_text_color(25,47,133)
            pdf.multi_cell(185,10,"DATA TABLE", align='L')
            pdf.set_draw_color(0,0,0)   

            if report_type=="All Vessel":
        
                pdf.set_xy(10,145)

            else :
                pdf.set_xy(10,165)

            #Table 2
            pdf.set_line_width(0)
            Table_2_head=[['SEASTATE', 'POWER (kW)', 'FO/24 Hrs (T)',"Fo Voyage"]]
            Table_2 = DataTable.values.tolist()
            pdf.set_font("Arial","B", size=9)
            col_width = pdf.w / 4.44
            row_height = pdf.font_size
            
            for row in Table_2_head:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)
            
            pdf.set_font("Arial","", size=8)
            pdf.set_text_color(0,0,0)
            for row in Table_2:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        
    #------------------------------------------------------------------------------------------------------------------------------#
            #2nd Page
            pdf.add_page()
        
            #FO-24 Hrs - Seastate Heading
            pdf.set_font('Arial', "B",15)
            pdf.set_xy(10,20)
            pdf.set_text_color(25,47,133)
            pdf.multi_cell(185,10,"FO/24 Hrs v/s SEASTATE", align='')
            pdf.set_draw_color(0,0,0)
            pdf.set_text_color(0,0,0)

            if DataTable_first_graph==0:
                pdf.set_xy(82,71)
                pdf.set_font('Arial', 'B', 15)
                pdf.multi_cell(50,20,"No Data Available",align='C')
            else:
                #Setting ETA & FOC Calculator - FO-24 Hrs - Seastate
                pdf.image("./images/Seaborn Voyage Calculator- ETA and FOC-24 Hrs.png",30,30,w=155,h=105) 
        
            #Power - Seastate Heading
            pdf.set_font('Arial', "B",15)
            pdf.set_xy(10,145)
            pdf.set_text_color(25,47,133)
            pdf.multi_cell(185,10,"POWER v/s SEASTATE", align='L')
            pdf.set_draw_color(0,0,0)
            pdf.set_text_color(0,0,0)
            if DataTable_second_graph==0:
                pdf.set_xy(82,192)
                pdf.set_font('Arial', 'B', 15)
                pdf.multi_cell(50,20,"No Data Available",align='C')
            else:
                #Setting ETA & FOC Calculator - Power - Seastate
                pdf.image("./images/Seaborn Voyage Calculator- ETA and FOC -POWER (kW).png",30,160,w=155,h=105)
        
        
        #Page Number
            pdf.set_text_color(0,0,0)
            pdf.set_y(266)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R") 

        
    #------------------------------------------------------------------------------------------------------------------------------#
        
            pdf_name = vessel_name + 'msc - Voyage Calculator - ETA & FOC Calculator  SEABORN.pdf'

            pdf.output('./documents/' + pdf_name,'F')
    pdf_name = vessel_name + 'msc - Voyage Calculator - ETA & FOC Calculator  SEABORN.pdf'
    
    simple_table()    
        
   

    return FileResponse(path = './documents/' + pdf_name)


@router.post('/api/v1/pdf/environmental/eeoi_mrv')
async def index(info : Request , vessel_name: str = None , year : str = None):    
    s = await info.json()
    if  not s:
        return {'data':[]}
    # url="https://msc.oceanix.cloud/api/sysapi/api/v1/envm/eeoi/ywer/9648075?year=2019"
    # s=requests.get(url).json()
    a = vessel_name
    b = year
    
    data1 = pd.DataFrame.from_dict(s['table1'])
    data1 = data1[['fuel_cons_details','Fuel(HS)','Fuel (LS)','Fuel (MDO)','Fuel (MGO)','Fuel (MGO)LS']]
    data1 = data1.astype(str)
    data2 = pd.DataFrame.from_dict(s['reported_data'])
    data2 = data2[['index','Value']]
    data2 = data2.astype(str)
    data3 = pd.DataFrame.from_dict(s['eechartdata'])

    #1st Graph EEOI & Voyage Number

    plt.figure(figsize=(16, 16))
    Improvement_Bar = sns.barplot(x="voyage_no", y="eeoi", data=data3, color="red", errwidth=0)
    plt.xlabel("Voyage Number", fontsize=16, fontweight="bold")
    plt.ylabel("Energy Efficiency (grams/tonne-mile)", fontsize=16, fontweight="bold")
    plt.title('Energy Efficiency (grams/tonne-mile)', size=15, fontweight="bold")
    for p in Improvement_Bar.patches:
        Improvement_Bar.annotate(format(p.get_height(), '.2f'), 
                                (p.get_x() + p.get_width() / 2., p.get_height()), 
                                ha='center', va='bottom', 
                                xytext=(0, 5), 
                                textcoords='offset points',
                                fontsize=9,
                                rotation=90,fontweight="bold")
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tick_params(axis='x', rotation=90)  
    plt.tight_layout()
    plt.savefig('./images/EEOI_MRV - Yearly Emission - EEOI Analysis Bar Graph- Yearly  SEABORN.png')
    plt.clf()


    #2nd Graph EEOIT & Voyage Number

    plt.figure(figsize=(16, 18))
    EEOI_Bar = sns.barplot(x="voyage_no", y="eeoiTEU", data=data3, color="green", errwidth=0)
    plt.xlabel("Voyage Number", fontsize=16, fontweight="bold")
    plt.ylabel("Energy Efficiency (grams/TEU-mile)", fontsize=16, fontweight="bold")
    plt.title('Energy Efficiency (grams/TEU-mile)', size=15, fontweight="bold")
    for p in EEOI_Bar.patches:
        EEOI_Bar.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', 
                        xytext=(0, 5), 
                        textcoords='offset points',
                        fontsize=9,
                        rotation=90,fontweight="bold")
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tick_params(axis='x', rotation=90)   
    plt.tight_layout()
    plt.savefig('./images/EEOI_MRV - Yearly Emission - EEOIT Analysis Bar Graph- Yearly  SEABORN.png')
    plt.clf()

    #3rd Graph CO2 & Voyage Number
    plt.figure(figsize=(16, 18))
    CO2_Bar = sns.barplot(x="voyage_no", y="co2", data=data3, color="orange", errwidth=0)
    plt.xlabel("Voyage Number", fontsize=16, fontweight="bold")
    plt.ylabel("CO₂ (tonnes)", fontsize=16, fontweight="bold")
    plt.title('CO₂ (tonnes)', size=15, fontweight="bold")
    for p in CO2_Bar.patches:
        CO2_Bar.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', 
                        xytext=(0, 5), 
                        textcoords='offset points',
                        fontsize=9,
                        rotation=90,fontweight="bold")
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tick_params(axis='x', rotation=90)  
    plt.tight_layout()
    plt.savefig('./images/EEOI_MRV - Yearly Emission - CO2 Analysis Bar Graph- Yearly  SEABORN.png')
    plt.clf()

    #4th Graph Fuel & Voyage Number
    plt.figure(figsize=(16, 16))
    FUEL_Bar = sns.barplot(x="voyage_no", y="totalfo", data=data3, color="yellow", errwidth=0)
    plt.xlabel("Voyage Number", fontsize=16, fontweight="bold")
    plt.ylabel("FO (tonnes)", fontsize=16, fontweight="bold")
    plt.title('FO (tonnes)', size=15, fontweight="bold")
    for p in FUEL_Bar.patches:
        FUEL_Bar.annotate(format(p.get_height(), '.2f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', 
                        xytext=(0, 5), 
                        textcoords='offset points',
                        fontsize=9,
                        rotation=90,fontweight="bold")
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tick_params(axis='x', rotation=90)  
    plt.tight_layout()
    plt.savefig('./images/EEOI_MRV - Yearly Emission - Fuel Analysis Bar Graph- Yearly  SEABORN.png')
    plt.clf()


    #***************************************************    PDF CODE    ***********************************************************#

    def simple_table(spacing=3):

        #report_prepared_date= "11-10-2022"

        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        #pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 

        pdf.set_font('Arial', 'B', 18)
        
        pdf.image(msc_logo_path,162,8,w=35)

    #Cell postion from left side
        pdf.set_xy(60,14)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 60, 'ANNUAL VOYAGE REPORT ',ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 199, 50)#(x_start, y_start, x_end, y_end)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)
        #pdf.multi_cell(80,14.5,"Report Date :"+" "+ report_prepared_date, align='R')

        pdf.cell(10, 2, "Vessel Name :"+" "+vessel_name,ln=True)
        pdf.cell(10, 12,"Calendar Year :"+" "+ year,ln=True)

        pdf.line(10, 70, 199, 70)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, ' ',ln=True,align='C')

        #Fuel Consumption Details Heading
        pdf.set_font('Arial', 'B', 15)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(10,80)
        pdf.cell(180, 7,"FUEL CONSUMPTION DETAILS",ln=True,align='L')
        pdf.set_text_color(0,0,0)
        #pdf.line(10, 85, 199, 85)

        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)

        pdf.set_xy(10,92)

        tablefirst_head = [['FUEL CONS DETAILS','Fuel (HS)','Fuel (LS)','Fuel (MDO)','Fuel (MGO)',"Fuel (MGO)LS"]]
        tablefirst = data1.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        col_width = pdf.w /6.7
        row_height = pdf.font_size
        for row in tablefirst_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)

        pdf.set_font("Arial", size=5)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /6.7
        row_height = pdf.font_size
        for row in tablefirst:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)

        pdf.set_xy(10,165)    

        spacing=2
        tablefirst_head1 = [['PARAMETER','VALUE']]
        tablefirst1 = data2.values.tolist()
        pdf.set_font("Arial",'B', size=10)
        col_width = pdf.w /2.2
        row_height = pdf.font_size
        for row in tablefirst_head1:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)

        pdf.set_font("Arial", size=8)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.2
        row_height = pdf.font_size
        for row in tablefirst1:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)


        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 2 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(182, 10, ' Voyage Vs EEOI',ln=True,align='C')  
        pdf.set_text_color(0,0,0)
        pdf.set_font("Arial", size=12)
        #pdf.set_xy(10,10)
        #pdf.cell(180, 15,"SeaState Selected :"+" "+ c,ln=True) 

        if data3["eeoi"].sum()==0:
            pdf.set_xy(90,55)
            pdf.set_font('Arial', 'B', 15)
            pdf.multi_cell(50,20,"No Data Available",align='C')
        else:    
            pdf.image("./images/EEOI_MRV - Yearly Emission - EEOI Analysis Bar Graph- Yearly  SEABORN.png",15,20,w=180,h=120) 
        
        pdf.set_font("Arial",'B', size=20)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 255, ' Voyage Vs EEOIT',ln=True,align='C')  
        pdf.set_text_color(0,0,0)
        pdf.set_font("Arial", size=12)
        #pdf.set_xy(10,10)
        #pdf.cell(180, 15,"SeaState Selected :"+" "+ c,ln=True) 
        if data3["eeoiTEU"].sum()==0:
            pdf.set_xy(80,40)
            pdf.set_font('Arial', 'B', 15)
            pdf.multi_cell(50,235,"No Data Available",align='C')
        else:
            pdf.image("./images/EEOI_MRV - Yearly Emission - EEOIT Analysis Bar Graph- Yearly  SEABORN.png",15,152,w=180,h=120) 
            
        pdf.set_text_color(0,0,0)
        pdf.set_y(274)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

                #*********************************************** 3 page **********************************************************#
        pdf.add_page()          
        pdf.set_xy(10,15)
        pdf.set_font("Arial",'B', size=18)
        #pdf.set_text_color(0,0,0)
        pdf.set_text_color(25,47,133)
        pdf.cell(182, 18, 'Voyage Vs Co2',ln=True,align='C') 
        pdf.set_text_color(0,0,0)

        if data3["co2"].sum()==0:
            pdf.set_xy(80,193)
            pdf.set_font('Arial', 'B', 15)
            pdf.multi_cell(130,35,"No Data Available",align='C')
        else:
            pdf.image("./images/EEOI_MRV - Yearly Emission - CO2 Analysis Bar Graph- Yearly  SEABORN.png",15,30,w=180,h=120)
            
            pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 243, ' Voyage Vs FO Consumption',ln=True,align='C')  
        pdf.set_text_color(0,0,0)
        pdf.set_font("Arial", size=12)
        #pdf.set_xy(10,10)
        #pdf.cell(180, 15,"SeaState Selected :"+" "+ c,ln=True) 
        if data3["totalfo"].sum()==0:
            pdf.set_xy(80,63)
            pdf.set_font('Arial', 'B', 15)
            pdf.multi_cell(50,235,"No Data Available",align='C')
        else:
            pdf.image("./images/EEOI_MRV - Yearly Emission - Fuel Analysis Bar Graph- Yearly  SEABORN.png",15,160,w=180,h=115) 

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(274)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        pdf.output('./documents/msc Environment - EEOI_MRV - Yearly Emission Report.pdf','F')

    simple_table()

    return FileResponse(path = './documents/msc Environment - EEOI_MRV - Yearly Emission Report.pdf')


@router.post("/api/v1/pdf/performance") # Done By Farsi
async def index(info : Request , start_date:str = None ,end_date:str = None,slip_min:str = None,slip_max:str = None,sea_state_min:str = None,sea_state_max:str = None,steaming_min:str = None,steaming_max:str = None,draft_min:str = None,draft_max:str = None,speed_min:str = None,speed_max:str = None,sfoc_min:str = None,sfoc_max:str = None, power_min:str = None,power_max:str = None,sea_state:str = None,draft:str = None,vessel_name:str = None,types:str = None):
# @router.post("/api/v1/pdf/performance") # Done By Farsi
# async def index(info : Request , start_date:str = None ,end_date:str = None,slip_min:str = None,slip_max:str = None,sea_state_min:str = None,sea_state_max:str = None,steaming_min:str = None,steaming_max:str = None,draft_min:str = None,draft_max:str = None,speed_min:str = None,speed_max:str = None,sfoc_min:str = None,sfoc_max:str = None, power_min:str = None,power_max:str = None,sea_state:str = None,draft:str = None):
    s = await info.json()
    if  not s:
        return {'data':[]}

    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6ImU3ZDY3NGJmLTJlYTgtNDI1ZC04MmNjLWZiYTQyZjNmOGViNyIsImlhdCI6MTY3MDMwMDcyNCwiZXhwIjoxNjcwMzg3MTI0fQ.k9bWye5u8Dmu8J2w983l5Wuei3iZh3uRu3dEFz-tib8"
    # headers = {'Authorization': "Bearer {}".format(token)}
    # url="http://192.168.54.79:8585/api/v1/pa/9648075?date1=2018-08-22&date2=2019-02-18&draft_min=5.5&draft_max=10.5&power_min=908&power_max=6050&speed_min=9&speed_max=14&slip_min=-00&slip_max=20&sfoc_min=100&sfoc_max=350&sea_state_min=0&sea_state_max=8&steaming_min=5&steaming_max=26&seastate=3&draft=1"
    # s=requests.get(url , headers =  headers).json()

    #***************************input parameters*******************************************#
    #fleet = '3'
    #group = '10'
    vesselname_df = pd.DataFrame.from_dict(s['data']['tab1']['Noon'])
    vsl = vessel_name
    # vsl = vessel_name
    date_start = start_date
    date_end = end_date

    # slip_min =.0
    # slip_max =0
    # sea_state_min =
    # sea_state_max =
    # steaming_time_min =
    # steaming_time_max =0
    # draft_min =
    # draft_max =5
    # speed_min =
    # speed_max =0
    # sfoc_min =.0
    # sfoc_max =.0
    # power_min =.0
    # power_max =0.0

    # sea_state = '3'
    # draft = '10'
    # Decode URL-encoded characters and clean up
    decoded_name = urllib.parse.unquote(vsl)
    vsl = decoded_name.replace(" - ", " -").strip()

    #**************************Applied Data Filters***************************************#
    data = {' ': ['Slip', 'Sea State', 'Steaming Time(Hrs)', 'Draft(m)','Speed(kn)','SFOC(kg/kW-Hr)','Power(kW)'],
            'Min': [slip_min, sea_state_min, steaming_min, draft_min, speed_min, sfoc_min, power_min],
            'Max': [slip_max, sea_state_max, steaming_max, draft_max, speed_max, sfoc_max, power_max]}
    data_filter_df = pd.DataFrame(data)
    data_filter_df = data_filter_df.astype(str)


    accuracy_pwr=s["data"]['tab2']['dpower']
    accuracy_fo=s["data"]['tab2']['dfo']
    date1=s["data"]['tab2']['date1']
    date2=s["data"]['tab2']['date2']

    accuracy_pwr=str(accuracy_pwr)+'%'
    accuracy_fo= str(accuracy_fo)+'%'
    date1 = datetime.strptime(date1, '%d %b %Y').date()
    date2 = datetime.strptime(date2, '%d %b %Y').date()

    # Format the date range string
    date_range = f"{date1.strftime('%d %b %Y')} to {date2.strftime('%d %b %Y')}"


    #**************************Performance Curve - FO Consumption**************************#
    data1 = pd.DataFrame.from_dict(s['data']['tab3']['table1'])
    data1 = data1.astype(str)
    if types == 'vrs':
        data1.rename(columns={'STW/Draft': 'stw/Draft'}, inplace=True)
        
    data1 = data1[['stw/Draft'] + [col for col in data1.columns if col != 'stw/Draft']]


    data2 = pd.DataFrame.from_dict(s['data']['tab3']['chart1'])
    if types == 'vrs':
        data2.rename(columns={'STW': 'stw'}, inplace=True)

    category1_lst = data2['Category'].unique().tolist()
    print(category1_lst)
    len_category1_lst = len(category1_lst)
    color_lst1 = ['brown','darkviolet','red','green','orange','blue','yellow','cyan','pink','gray','olive','purple','indigo','magenta','beige','lavender','black','lightgreen']
    new_color_lst1 = []
    for z in range (0,len_category1_lst):
        color_sel = color_lst1[z]
        new_color_lst1.append(color_sel)

    count = 0
    j = 0
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    for i in category1_lst:
        df1 = data2[data2['Category']==i]
        clr = new_color_lst1[j]
        if count == 0:
            ax = sns.lineplot(x="stw", y='fo_consumption', data=df1,marker = 'o',markersize = 10,label = i,color=clr)
        else:
            sns.lineplot(x="stw", y='fo_consumption', data=df1,marker = 'o',markersize = 10,label = i,color=clr)
        count = count+1
        j = j+1
    plt.xlabel('Speed (knots)',fontweight="bold",size=12)
    plt.ylabel('FO/24Hrs (tonne)',fontweight="bold",size=12)
    plt.title('Speed FO/24 Hrs Curve', size=17,fontweight="bold")
    ax.legend(title=None, loc='upper left')
    plt.savefig('./images/performance_analysis_speed_draft.png')    
    plt.clf()
    #***************************Performance Curve - Power*******************************#
    data3 = pd.DataFrame.from_dict(s['data']['tab3']['table2'])
    data3 = data3.astype(str)
    if types == 'vrs':
        data3.rename(columns={'STW/Draft': 'stw/Draft'}, inplace=True)
    data3 = data3[['stw/Draft'] + [col for col in data3.columns if col != 'stw/Draft']]


    data4 = pd.DataFrame.from_dict(s['data']['tab3']['chart2'])
    if types == 'vrs':
        data4.rename(columns={'STW': 'stw'}, inplace=True)


    category2_lst = data4['Category'].unique().tolist()
    len_category2_lst = len(category2_lst)

    color_lst2 = ['brown','darkviolet','red','green','orange','blue','yellow','cyan','pink','gray','olive','purple','indigo','magenta','beige','lavender','black','lightgreen']
    new_color_lst2 = []
    for z in range (0,len_category2_lst):
        color_sel = color_lst2[z]
        new_color_lst2.append(color_sel)

    count = 0
    j = 0
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,8))
    for i in category2_lst:
        df2 = data4[data4['Category']==i]
        clr = new_color_lst2[j]
        if count == 0:
            ax = sns.lineplot(x="stw", y='Power', data=df2,marker = 'o',markersize = 10,label = i,color=clr)
        else:
            sns.lineplot(x="stw", y='Power', data=df2,marker = 'o',markersize = 10,label = i,color=clr)
        count = count+1
        j = j+1
    plt.xlabel('Speed (knots)',fontweight="bold",size=12)
    plt.ylabel('Power (kW))',fontweight="bold",size=12)
    plt.title('Speed Power Curve', size=17,fontweight="bold")
    plt.xticks(rotation=60)
    ax.legend(title=None, loc='upper left')
    plt.savefig('./images/performance_analysis_speed_power.png')
    plt.clf()

    #*******************************FO Calculator for Sea State****************************#
    data5 = pd.DataFrame.from_dict(s['data']['tab3']['table3'])
    data5 = data5.astype(str)
    print("data5",data5.columns)
    if types == 'vrs':
        # data5.rename(columns={'STW/Draft': 'stw/Draft'}, inplace=True)
        data5.rename(columns={'STW/Sea State': 'stw/Sea State'}, inplace=True)

    data5 = data5[['stw/Sea State'] + [col for col in data5.columns if col != 'stw/Sea State']]

    data6 = pd.DataFrame.from_dict(s['data']['tab3']['chart3'])
    if types == 'vrs':
        data6.rename(columns={'STW': 'stw'}, inplace=True)


    category3_lst = data6['Category'].unique().tolist()
    len_category3_lst = len(category3_lst)

    color_lst3 = ['brown','darkviolet','red','green','orange','blue','yellow','cyan','pink','gray','olive','purple','indigo','magenta','beige','lavender','black','lightgreen']
    new_color_lst3 = []
    for z in range (0,len_category3_lst):
        color_sel = color_lst3[z]
        new_color_lst3.append(color_sel)

    count = 0
    j = 0
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,8))
    for i in category3_lst:
        df3 = data6[data6['Category']==i]
        clr = new_color_lst3[j]
        if count == 0:
            ax = sns.lineplot(x="stw", y='fo_consumption', data=df3,marker = 'o',markersize = 10,label = i,color=clr)
        else:
            sns.lineplot(x="stw", y='fo_consumption', data=df3,marker = 'o',markersize = 10,label = i,color=clr)
        count = count+1
        j = j+1
    plt.xlabel('Speed (knots)',fontweight="bold",size=12)
    plt.ylabel('FO/24Hrs (tonne)',fontweight="bold",size=12)
    plt.title('Speed FO/24Hrs Curve For Sea State', size=17,fontweight="bold")
    plt.xticks(rotation=60)
    ax.legend(loc='upper left')
    plt.savefig('./images/performance_analysis_fo_calculator_for_sea_state.png')
    plt.clf()

    #******************************************* PDF CODE *************************************************************#

    def simple_table(spacing=3):

        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        # pdf.add_font('Arial', '', uni=True)    
        pdf.set_font('Arial', 'B', 18)

        #pdf.image(oceanix_logo_path,15,15,w=35)
        pdf.image(msc_logo_path,162,8,w=35)

    #Cell postion from left side
        pdf.set_xy(47,14)
        pdf.set_text_color(25,47,133)
        if types=='vrs':
            pdf.cell(200, 60, 'PERFORMANCE ANALYSIS (VRS)',ln=True)
        else:
            pdf.cell(200, 60, 'PERFORMANCE ANALYSIS (ADA)',ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 199, 50)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)



        pdf.cell(10, 2, "Vessel Name :"+" "+vessel_name,ln=True)
        pdf.cell(10, 12,"Analysis Date Range :"+" "+ start_date + " " + "to" + " " + end_date,ln=True)
        pdf.line(10, 70, 199, 70)
        pdf.set_line_width(0)
        pdf.set_xy(10,85)
        pdf.set_fill_color(255, 204, 153)

        # First section: Accuracy in Power prediction
        pdf.multi_cell(0, 10, "Accuracy in Power prediction: " + accuracy_pwr, border=1, fill=True, align='C')
        pdf.ln(2)  

        # Second section: Accuracy in FO/24 Hrs prediction
        pdf.multi_cell(0, 10, "Accuracy in FO/24 Hrs prediction: " + accuracy_fo, border=1, fill=True, align='C')
        pdf.ln(2)  

        # Third section: Analysis period
        pdf.multi_cell(0, 10, "Analysis Period: " + date_range, border=1, fill=True, align='C')


        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(175, 65, 'Applied Data Filters',ln=True,align='C')

        pdf.set_text_color(0,0,0)

        pdf.set_xy(10,165)

        tablefirst_head = [['','Min','Max']]
        tablefirst = data_filter_df.values.tolist()
        pdf.set_font("Arial",'B', size=10)
        col_width = pdf.w /3.3
        row_height = pdf.font_size
        for row in tablefirst_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)

        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.3
        row_height = pdf.font_size
        for row in tablefirst:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
                     

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 2 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Performance Curve - FO Consumption',ln=True,align='C')  
        pdf.set_text_color(0,0,0)
        pdf.set_font("Arial", size=12)
        pdf.set_xy(10,23)
        pdf.cell(180, 15,"SeaState Selected :"+" "+ sea_state,ln=True) 

        spacing=2
        tablefirst_head1 = [data1.columns.tolist()]
        tablefirst1 = data1.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        col_width = pdf.w /14
        row_height = pdf.font_size + 1
        for row in tablefirst_head1:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)

        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /14
        row_height = pdf.font_size + 1
        for row in tablefirst1:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)

        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        pdf.add_page()  
        #pdf.set_xy(10,130)
        pdf.set_font("Arial",'B', size=20)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 35, 'FO/24 Hrs Vs Speed',ln=True,align='C')
        pdf.image("./images/performance_analysis_speed_draft.png",10,35,w=180,h=120)    

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 3 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Performance Curve - Power',ln=True,align='C')
        pdf.set_xy(10,30)

        spacing=2
        tablefirst_head2 = [data3.columns.tolist()]
        tablefirst2 = data3.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        col_width = pdf.w /14
        row_height = pdf.font_size+1
        for row in tablefirst_head2:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)

        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /14
        row_height = pdf.font_size+1
        for row in tablefirst2:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)

        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        pdf.add_page()  

        #pdf.set_xy(10,130)
        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 35, 'Power Vs Speed',ln=True,align='C') 
        pdf.image("./images/performance_analysis_speed_power.png",10,35,w=180,h=120)    

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 4 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'FO Calculator for Sea State',ln=True,align='C')
        pdf.set_xy(10,30)

        spacing=2
        tablefirst_head3 = [data5.columns.tolist()]
        tablefirst3 = data5.values.tolist()
        pdf.set_font("Arial",'B', size=6)
        col_width = pdf.w /11.3
        row_height = pdf.font_size
        for row in tablefirst_head3:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)

        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /11.3
        row_height = pdf.font_size
        for row in tablefirst3:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)

        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        pdf.add_page()  
        #pdf.set_xy(10,105)
        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 35, 'FO Vs Speed for Sea state',ln=True,align='C') 
        pdf.set_text_color(0,0,0)
        pdf.set_font("Arial", size=12)
        #pdf.set_xy(15,120)
        pdf.cell(50, 0.1,"Draft Selected :"+" "+ draft,ln=True) 
        pdf.image("./images/performance_analysis_fo_calculator_for_sea_state.png",10,35,w=180,h=120)    

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        
        pdf_name = vsl + 'Performance_Analysis.pdf'
        pdf.output('./documents/' + pdf_name,'F')
    pdf_name = vsl + 'Performance_Analysis.pdf'

    simple_table()

    return FileResponse(path = './documents/' +pdf_name)

@router.post("/api/v1/pdf/prepost/perfomancecurve")
async def index(info : Request ,imo:str = None ,key_date: str = None ,slip_min: str = None ,slip_max: str = None ,sea_state_min: str = None ,sea_state_max: str = None ,steaming_time_min: str = None ,steaming_time_max: str = None ,draft_min: str = None ,draft_max: str = None ,speed_min: str = None ,speed_max: str = None ,sfoc_min: str = None ,sfoc_max: str = None ,power_min: str = None ,power_max: str = None ,sea_state: str = None ,draft: str = None ,spacing: str = None,types:str=None,method:str=None):

    spacing=3
    s = await info.json()

    
    if  not s:
        return {'data':[]}
    from datetime import datetime
    
    key_date = datetime.strptime(key_date,'%Y-%m-%d').strftime('%d %b %Y')
    if types =='vrs':
        vesselname_df = pd.DataFrame.from_dict(s['vrs']['vrs_data_visualization']['daily_data_chart'])
        vsl = vesselname_df['VESSEL'].values[0]
        post_data_count=s['vrs']['vrs_header']['post_data_count']
        pre_data_count=s['vrs']['vrs_header']['pre_data_count']
        pre_date=s['vrs']['vrs_header']['pre_date']
        post_date=s['vrs']['vrs_header']['post_date']
    else:  
        vesselname_df = pd.DataFrame.from_dict(s['ada']['ada_data_visualization']['daily_data_chart'])
        vsl = vesselname_df['VESSEL'].values[0]  
        post_data_count=s['ada']['ada_header']['post_data_count']
        pre_data_count=s['ada']['ada_header']['pre_data_count']
        pre_date=s['ada']['ada_header']['pre_date']
        post_date=s['ada']['ada_header']['post_date']


    from datetime import datetime

    date_objects = [datetime.strptime(date_str, '%d %b %Y') for date_str in pre_date]

    # Assign values to pre_date_start and pre_date_end
    pre_date_start = date_objects[0].strftime('%d %b %Y')


    pre_date_end = date_objects[1].strftime('%d %b %Y')


    date_objects = [datetime.strptime(date_str, '%d %b %Y') for date_str in post_date]

    # Assign values to pre_date_start and pre_date_end
    post_date_start = date_objects[0].strftime('%d %b %Y')
    post_date_end = date_objects[1].strftime('%d %b %Y')

    if types =='vrs':
        vesselname_df=pd.DataFrame.from_dict(s['vrs']['vrs_data_visualization']['daily_data_chart'])
    else:
        vesselname_df=pd.DataFrame.from_dict(s['ada']['ada_data_visualization']['daily_data_chart'])

    vsl = vesselname_df['VESSEL'].values[0]

    if types =='vrs':
        gain_power=s['vrs']["vrs_data_prediction"]["gain_power"]
        gain_fo=s['vrs']["vrs_data_prediction"]["gain_fo"]
        power_accuracy=s['vrs']["vrs_data_prediction"]["accuracy_in_power"]
        fo_accuracy=s['vrs']["vrs_data_prediction"]["accuracy_in_fo"]

    
    else:
        gain_power=s['ada']["ada_data_prediction"]["gain_power"]
        gain_fo=s['ada']["ada_data_prediction"]["gain_fo"]
        power_accuracy=s['ada']["ada_data_prediction"]["accuracy_in_power"]
        fo_accuracy=s['ada']["ada_data_prediction"]["accuracy_in_fo"]    


    data = {' ': ['Draft(m)', 'Power(kW)', 'Speed(knots)', 'Slip(%)','SFOC(kg/kW-Hr)','Sea State','Steaming Time(Hrs)'],
            'Min': [draft_min, power_min, speed_min, slip_min, sfoc_min, sea_state_min, steaming_time_min],
            'Max': [draft_max, power_max, speed_max, slip_max, sfoc_max, sea_state_max, steaming_time_max]}
    data_filter_df = pd.DataFrame(data)
    data_filter_df = data_filter_df.astype(str)



    if types=='vrs':
        power_comparison_table=pd.DataFrame.from_dict(s['vrs']['vrs_data_performanceCurve']['power_comparison']['table_data'])
        data2 = pd.DataFrame.from_dict(s['vrs']['vrs_data_performanceCurve']['power_comparison']['chart_data'])
    else:
        power_comparison_table=pd.DataFrame.from_dict(s['ada']['ada_data_performanceCurve']['power_comparison']['table_data'])
        data2 = pd.DataFrame.from_dict(s['ada']['ada_data_performanceCurve']['power_comparison']['chart_data'])


    power_comparison_table = power_comparison_table[['Speed (knots)','Before','After']]
    power_comparison_table=power_comparison_table.rename(columns={'Before':'Before Power(kW)','After':'After Power(kW)','Speed (knots)': f"{method.upper()} (knots)"})
    data2_pre = data2[data2['CATEGORY']=='Pre Analysis']
    data2_post = data2[data2['CATEGORY']=='Post Analysis']

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,7))
    ax = sns.lineplot(x="SPEED", y='POWER', data=data2_pre,marker = 'o',markersize = 10,label = 'Pre Analysis',color='green')
    sns.lineplot(x="SPEED", y='POWER', data=data2_post,marker = 'o',markersize = 10,label = "Post Power",color='red')
    plt.xlabel(f"{method.upper()} (knots)", fontweight="bold", size=12)
    plt.ylabel('POWER(kW)',fontweight="bold",size=12)
    plt.xticks(rotation=90, ha='right')
    plt.title('Power Comparison', size=15,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/Power Comparison.png')

    if types=='vrs':
        fo_comparison_table=pd.DataFrame.from_dict(s['vrs']['vrs_data_performanceCurve']['fo_comparison']['table_data'])
        data3 = pd.DataFrame.from_dict(s['vrs']['vrs_data_performanceCurve']['fo_comparison']['chart_data'])
    else:
        fo_comparison_table=pd.DataFrame.from_dict(s['ada']['ada_data_performanceCurve']['fo_comparison']['table_data'])
        data3 = pd.DataFrame.from_dict(s['ada']['ada_data_performanceCurve']['fo_comparison']['chart_data'])

    fo_comparison_table = fo_comparison_table[['Speed (knots)','Before','After']]
    fo_comparison_table = fo_comparison_table.rename(columns={'Before':'Before FO(MT)','After':'After FO(MT)','Speed (knots)': f"{method.upper()} (knots)"})
    data3_pre = data3[data3['CATEGORY']=='Pre Analysis']
    data3_post = data3[data3['CATEGORY']=='Post Analysis']


    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,7))
    ax = sns.lineplot(x="SPEED", y='FO', data=data3_pre,marker = 'o',markersize = 10,label = 'Pre Analysis',color='green')
    sns.lineplot(x="SPEED", y='FO', data=data3_post,marker = 'o',markersize = 10,label = "Post Power",color='red')
    plt.xlabel(f"{method.upper()} (knots)", fontweight="bold", size=12)
    plt.ylabel('FO(MT)',fontweight="bold",size=12)
    plt.xticks(rotation=90, ha='right')
    plt.title('FO Comparison', size=15,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/FO Comparison.png')


    from fpdf import FPDF

    pdf = FPDF()

    # 1st Page
    pdf.add_page()
    pdf.set_font('Arial', 'B', 18)
    pdf.image(msc_logo_path, 162, 8, w=35)
    pdf.set_xy(60, 14)
    pdf.set_text_color(25, 47, 133)
    if types == 'vrs':
        pdf.cell(180, 60, 'PRE-POST ANALYSIS (VRS)', ln=True)
    else:
        pdf.cell(180, 60, 'PRE-POST ANALYSIS (ADA)', ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_line_width(1)
    pdf.line(10, 50, 199, 50)
    pdf.set_line_width(0.2)
    pdf.set_font('Arial', "", 12)
    pdf.set_xy(10, 55)

    pdf.cell(10, 2, "Vessel Name :"+" "+vsl+"  "+str(imo)+" ",ln=True)
    pdf.cell(10, 10,"Key Date :"+" "+key_date ,ln=True)
    pdf.cell(10, 3,"Pre Analysis Date Range :"+" "+ pre_date_start + " " + "to" + " " + pre_date_end,ln=True)
    pdf.cell(10, 8,"Post Analysis Date Range :"+" "+ post_date_start + " " + "to" + " " + post_date_end,ln=True)

    pdf.line(10, 80, 199, 80)
    pdf.set_xy(10,140)

    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(25, 47, 133)
    pdf.cell(180, 26, 'Applied Data Filters', ln=True, align='C')
    
    # Reset line width and text color for the table
    pdf.set_line_width(0)
    pdf.set_text_color(0, 0, 0)
    
    # Define table headers and data
    tablefirst_head = [['', 'Min', 'Max']]  # Table header
    tablefirst = data_filter_df.values.tolist()  # Convert DataFrame to list of lists
    
    # Modify row label dynamically
    for row in tablefirst:
        if row[0] == 'Speed(knots)':
            row[0] = f"{method.upper()} (knots)"
    
    # Table Parameters
    pdf.set_font("Arial", 'B', size=10)  
    spacing = 1.5  
    col_width = pdf.w / 3.6  
    row_height = pdf.font_size + 2  
    table_width = col_width * len(tablefirst_head[0])  
    x_start = (pdf.w - table_width) / 2  
    
    # Draw Header Row
    for row in tablefirst_head:
        pdf.set_text_color(255, 255, 255)  
        pdf.set_fill_color(21, 55, 188)  
        pdf.set_xy(x_start, pdf.get_y())  
        for item in row:
            pdf.cell(col_width, row_height * spacing, txt=item, border=1, fill=True)
        pdf.ln(row_height * spacing)  
    
    # Draw Data Rows
    pdf.set_font("Arial", size=10)  
    pdf.set_text_color(0, 0, 0)  
    for row in tablefirst:
        pdf.set_xy(x_start, pdf.get_y())  
        for item in row:
            pdf.cell(col_width, row_height * spacing, txt=str(item), border=1)  
        pdf.ln(row_height * spacing)  


    # Performance Metrics Section
    pdf.set_xy(10, 85)
    pdf.cell(10, 5, "Pre Data Count :"+" "+str(pre_data_count)+'                    ' + "Draft: " + str(draft),ln=True)
    pdf.cell(10, 7, "Post Data Count :"+" "+str(post_data_count)+'                ' + "Sea State: " + str(sea_state),ln=True)

    # Calculate positions for 4 boxes
    page_width = pdf.w
    box_width = 40
    box_height = 25
    spacing = 10
    start_x = (page_width - (4 * box_width + 3 * spacing)) / 2
    start_y = 110

    # Function to draw metric box
    def draw_metric_box(x, y, value, label, color, text_color=(0, 0, 0)):
        pdf.set_xy(x, y)
        
        # Draw filled rectangle with color
        pdf.set_fill_color(*color)
        pdf.rect(x, y, box_width, box_height, 'F')
        
        # Draw black border
        pdf.set_draw_color(0, 0, 0)  # Set border color to black
        pdf.set_line_width(0.5)      # Set border width
        pdf.rect(x, y, box_width, box_height, 'D')  # Draw border only
        
        # Set text color based on parameter
        pdf.set_text_color(*text_color)
        
        # Value text (larger, positioned at top)
        pdf.set_font('Arial', 'B', 14)
        pdf.set_xy(x, y + 3)
        pdf.cell(box_width, 10, str(value), align='C', ln=True)
        
        # Label text (smaller, positioned at bottom)
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(x, y + 13)
        pdf.multi_cell(box_width, 4, label, align='C')

    # Draw the four metric boxes
    # Power Gain/Loss Box
    if gain_power >= 0:
        draw_metric_box(start_x, start_y, f"{gain_power:.2f}%", " Gain in Power %", (0, 255, 0))  # Green with black text
    else:
        draw_metric_box(start_x, start_y, f"{gain_power:.2f}%", " Loss in Power %", (255, 0, 0), (255, 255, 255))  # Red with white text

    # FO Gain/Loss Box
    if gain_fo >= 0:
        draw_metric_box(start_x + box_width + spacing, start_y, f"{gain_fo:.2f}%", " Gain in FO %", (0, 255, 0))  # Green with black text
    else:
        draw_metric_box(start_x + box_width + spacing, start_y, f"{gain_fo:.2f}%", "Loss in FO %", (255, 0, 0), (255, 255, 255))  # Red with white text

    # Power Accuracy Box
    draw_metric_box(start_x + (box_width + spacing) * 2, start_y, f"{power_accuracy:.1f}%", "Accuracy in\nPower prediction", (255, 165, 0))  # Orange with black text

    # FO Accuracy Box
    draw_metric_box(start_x + (box_width + spacing) * 3, start_y, f"{fo_accuracy:.1f}%", "Accuracy in\nFO prediction", (255, 165, 0))  # Orange with black text

    # Reset text color and line width
    pdf.set_text_color(0, 0, 0)
    pdf.set_line_width(0.2)

    # Continue with Applied Data Filters section
    pdf.set_xy(10, 140)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(25, 47, 133)
    pdf.cell(180, 26, 'Applied Data Filters', ln=True, align='C')


    # Rest of the code remains the same...
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_xy(10, 40)

    # Page numbering
    pdf.set_y(273)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 2, 'Page %s' % pdf.page_no(), align="R")

    # 2nd Page
    pdf.add_page()
    pdf.set_xy(10, 15)
    pdf.set_font("Arial",'B', size=18)
    pdf.set_text_color(25,47,133)
    pdf.cell(180, 25, 'Power Comparison Table', ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)


    spacing = 2
    tablefirst_head1 = [power_comparison_table.columns.tolist()]
    tablefirst1 = power_comparison_table.values.tolist()
    pdf.set_font("Arial", 'B', size=10)
    col_width = pdf.w /3.6
    row_height = pdf.font_size
    pdf.set_xy(17, 46)
    for row in tablefirst_head1:
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        for item in row:
            pdf.cell(col_width, row_height * spacing, txt=str(item), border=1, fill=True)
        pdf.ln(row_height * spacing)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /3.6
    row_height = pdf.font_size

    for row in tablefirst1:
        pdf.set_x(17)
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                    txt=str(item), border=1)
        pdf.ln(row_height*spacing)

        
    pdf.set_xy(45, 75)
    pdf.set_font("Arial",'B', size=16)
    pdf.set_text_color(25,47,133)
    pdf.image("./images/Power Comparison.png",13,160,w=190,h=120) 

    #Page Number
    pdf.set_text_color(0,0,0)
    pdf.set_y(273)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


    #*********************************************** 3 page **********************************************************#
    pdf.add_page() 


    pdf.set_xy(10, 15)
    pdf.set_font("Arial",'B', size=16)
    pdf.set_text_color(25,47,133)
    pdf.cell(180, 25, 'FO Comparison Table',ln=True,align='C')

    spacing = 2
    tablefirst_head1 = [fo_comparison_table.columns.tolist()]
    tablefirst1 = fo_comparison_table.values.tolist()
    pdf.set_font("Arial", 'B', size=10)
    col_width = pdf.w / 3.6
    row_height = pdf.font_size
    pdf.set_xy(17, 46)
    for row in tablefirst_head1:
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        for item in row:
            pdf.cell(col_width, row_height * spacing, txt=str(item), border=1, fill=True)
        pdf.ln(row_height * spacing)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /3.6

    row_height = pdf.font_size
    for row in tablefirst1:
        pdf.set_x(17)
        
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                    txt=str(item), border=1)
        pdf.ln(row_height*spacing)
        
    pdf.set_xy(45, 75)
    pdf.set_font("Arial",'B', size=16)
    pdf.set_text_color(25,47,133)
    pdf.image("./images/FO Comparison.png",12,145,w=190,h=120)

    #Page Number
    pdf.set_text_color(0,0,0)
    pdf.set_y(273)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        
    pdf_name = 'VRS_Data_Performance_Curve.pdf'
    pdf.output('./documents/' + pdf_name,'F')


    return FileResponse(path = './documents/' +pdf_name)

@router.post("/api/v1/pdf/prepost")
async def index(info : Request , pre_date_start: str = None ,pre_date_end: str = None ,post_date_start: str = None ,post_date_end: str = None ,slip_min: str = None ,slip_max: str = None ,sea_state_min: str = None ,sea_state_max: str = None ,steaming_time_min: str = None ,steaming_time_max: str = None ,draft_min: str = None ,draft_max: str = None ,speed_min: str = None ,speed_max: str = None ,sfoc_min: str = None ,sfoc_max: str = None ,power_min: str = None ,power_max: str = None ,draft: str = None):
    s = await info.json()
    if  not s:
        return {'data':[]}
    

    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6ImU3ZDY3NGJmLTJlYTgtNDI1ZC04MmNjLWZiYTQyZjNmOGViNyIsImlhdCI6MTY3MDMwMDcyNCwiZXhwIjoxNjcwMzg3MTI0fQ.k9bWye5u8Dmu8J2w983l5Wuei3iZh3uRu3dEFz-tib8"
    # headers = {'Authorization': "Bearer {}".format(token)}
    # url="http://192.168.54.32:9111/api/v1/pre_post/9648075?pre_date_min=2018-05-24&pre_date_max=2018-08-22&speed_min=10&speed_max=14&power_min=907.5&power_max=60508&draft_min=5.5&draft_max=10.5&slip_min=-20&slip_max=20&sfoc_min=150&sfoc_max=350&sea_state_min=0&sea_state_max=8&steam_min=5&steam_max=26&post_date_min=2018-08-23&post_date_max=2018-11-20&indraft=10.5"
    # s=requests.get(url , headers =  headers).json()

    #*************************input parameters**********************#
    # vsl = 'Strategic Alliance'
    vesselname_df = pd.DataFrame.from_dict(s['data']['tab_1_data'])
    vsl = vesselname_df['VESSEL'].values[0]
    # pre_date_start = '2018-05-24'
    # pre_date_end = '2018-08-22'
    # post_date_start = '2018-08-23'
    # post_date_end = '2018-11-20'

    # slip_min = -20.0
    # slip_max = 20.0
    # sea_state_min = 0.0
    # sea_state_max = 0.8
    # steaming_time_min = 5.0
    # steaming_time_max = 26.0
    # draft_min = 5.5
    # draft_max = 10.5
    # speed_min = 9.0
    # speed_max = 14.0
    # sfoc_min = 150.0
    # sfoc_max = 350.0
    # power_min = 907.0
    # power_max = 6050.0

    # draft = '10'

    #*************************Applied Data Filters*******************#
    data = {' ': ['Draft(m)', 'Power(kW)', 'Speed(kn)', 'Slip','SFOC(kg/kW-Hr)','Sea State','Steaming Time(Hrs)'],
            'Min': [draft_min, power_min, speed_min, slip_min, sfoc_min, sea_state_min, steaming_time_min],
            'Max': [draft_max, power_max, speed_max, slip_max, sfoc_max, sea_state_max, steaming_time_max]}
    data_filter_df = pd.DataFrame(data)
    data_filter_df = data_filter_df.astype(str)

    #*************************Seatrial Interpolation*****************#
    data1_table = pd.DataFrame.from_dict(s['data']['tab_3_data']['table_1'])
    data1 = pd.DataFrame.from_dict(s['data']['tab_3_chart']['chart_1'])

    data1_scantling = data1[data1['category']=='Scantling Power']
    data1_ballast = data1[data1['category']=='Ballast Power']
    data1_trial = data1[data1['category']=='Trial Power']

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(x="Power", y='value', data=data1_scantling,marker = 'o',markersize = 10,label = 'Scantling Power',color='blue')
    sns.lineplot(x="Power", y='value', data=data1_ballast,marker = 'o',markersize = 10,label = "Ballast Power",color='green')
    sns.lineplot(x="Power", y='value', data=data1_trial,marker = 'o',markersize = 10,label = "Trial Power",color='yellow')
    plt.xlabel('Speed',fontweight="bold",size=12)
    plt.ylabel('Power',fontweight="bold",size=12)
    plt.title('Seatrial Interpolation', size=15,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('images/prepost_seatrail_interpolation.png')
    plt.clf()

    data1_table = data1_table.astype(str)

    speed_gain = s['data']['Speed Gain']
    speed_gain = str(speed_gain)

    #***************************Pre/Post Power Vs Speed******************#
    data2_table = pd.DataFrame.from_dict(s['data']['tab_3_data']['table_2'])
    data2 = pd.DataFrame.from_dict(s['data']['tab_3_chart']['chart_2'])

    data2_pre = data2[data2['category']=='Pre Power']
    data2_post = data2[data2['category']=='Post Power']
    data2_trial = data2[data2['category']=='Trial Power']

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(x="Power", y='value', data=data2_pre,marker = 'o',markersize = 10,label = 'Pre Power',color='blue')
    sns.lineplot(x="Power", y='value', data=data2_post,marker = 'o',markersize = 10,label = "Post Power",color='green')
    sns.lineplot(x="Power", y='value', data=data2_trial,marker = 'o',markersize = 10,label = "Trial Power",color='yellow')
    plt.xlabel('Speed',fontweight="bold",size=12)
    plt.ylabel('Power',fontweight="bold",size=12)
    plt.title('Pre/Post Power vs Speed', size=15,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('images/prepost_power_speed.png')
    plt.clf()

    data2_table = data2_table.astype(str)

    #***************************Pre/Post FO vs Speed*********************#
    data3_table = pd.DataFrame.from_dict(s['data']['tab_3_data']['table_3'])
    data3 = pd.DataFrame.from_dict(s['data']['tab_3_chart']['chart_3'])

    data3_pre = data3[data3['category']=='Pre FO/24 Hrs']
    data3_post = data3[data3['category']=='Post FO/24 Hrs']
    data3_trial = data3[data3['category']=='Trial FO/24 Hrs']

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(x="FO/24 Hrs", y='value', data=data3_pre,marker = 'o',markersize = 10,label = 'Pre Speed',color='blue')
    sns.lineplot(x="FO/24 Hrs", y='value', data=data3_post,marker = 'o',markersize = 10,label = "Post Speed",color='green')
    sns.lineplot(x="FO/24 Hrs", y='value', data=data3_trial,marker = 'o',markersize = 10,label = "Trial Speed",color='yellow')
    plt.xlabel('Speed',fontweight="bold",size=12)
    plt.ylabel('FO/24 Hrs',fontweight="bold",size=12)
    plt.title('Pre/Post FO vs Speed', size=15,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('images/prepost_fo_speed.png')
    plt.clf()

    data3_table = data3_table.astype(str)

    #**************************************************** PDF CODE ******************************************************#

    def simple_table(spacing=3):
        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 
        pdf.set_font('Arial', 'B', 18)

        
        pdf.image(msc_logo_path,162,8,w=35)

    #Cell postion from left side
        pdf.set_xy(60,14)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 60, 'PRE-POST ANALYSIS',ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 199, 50)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)
        
        
        pdf.cell(10, 2, "Vessel Name :"+" "+vsl,ln=True)
        pdf.cell(10, 12,"Pre Analysis Date Range :"+" "+ pre_date_start + " " + "to" + " " + pre_date_end,ln=True)
        pdf.cell(10, 2,"Post Analysis Date Range :"+" "+ post_date_start + " " + "to" + " " + post_date_end,ln=True)
        
        
        pdf.line(10, 77, 199, 77)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 26, 'Applied Data Filters',ln=True,align='C')
        pdf.line(10, 92, 199, 92)
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        
        pdf.set_xy(10,100)
        
        tablefirst_head = [['','Min','Max']]
        tablefirst = data_filter_df.values.tolist()
        pdf.set_font("Arial",'B', size=10)
        col_width = pdf.w /3.3
        row_height = pdf.font_size
        for row in tablefirst_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.3
        row_height = pdf.font_size
        for row in tablefirst:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 2 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Seatrial Interpolation',ln=True,align='C')  
        pdf.set_text_color(0,0,0)
        pdf.set_font("Arial", size=12)
        pdf.set_xy(10,23)
        pdf.cell(180, 6,"Draft Selected :"+" "+ draft,ln=True)
        pdf.cell(180, 6,"Gain in Speed :"+" "+ speed_gain + " " + "%",ln=True)
        pdf.set_xy(10,40)
        
        spacing=2
        tablefirst_head1 = [data1_table.columns.tolist()]
        tablefirst1 = data1_table.values.tolist()
        pdf.set_font("Arial",'B', size=10)
        col_width = pdf.w /4.5
        row_height = pdf.font_size
        for row in tablefirst_head1:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /4.5
        row_height = pdf.font_size
        for row in tablefirst1:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_xy(10,120)
        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)
        pdf.image("./images/prepost_seatrail_interpolation.png",15,130,w=180,h=120)    
        
        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 3 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Pre/Post Power Vs Speed',ln=True,align='C')
        pdf.set_xy(10,30)
        
        spacing=2
        tablefirst_head2 = [data2_table.columns.tolist()]
        tablefirst2 = data2_table.values.tolist()
        pdf.set_font("Arial",'B', size=10)
        col_width = pdf.w /4.5
        row_height = pdf.font_size
        for row in tablefirst_head2:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /4.5
        row_height = pdf.font_size
        for row in tablefirst2:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_xy(10,120)
        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133)
        pdf.image("./images/prepost_power_speed.png",10,125,w=180,h=120)    
        
        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 4 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Pre/Post FO vs Speed',ln=True,align='C')
        pdf.set_xy(10,30)
        
        spacing=2
        tablefirst_head3 = [data3_table.columns.tolist()]
        tablefirst3 = data3_table.values.tolist()
        pdf.set_font("Arial",'B', size=10)
        col_width = pdf.w /4.5
        row_height = pdf.font_size
        for row in tablefirst_head3:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /4.5
        row_height = pdf.font_size
        for row in tablefirst3:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_xy(10,120)
        pdf.set_font("Arial",'B', size=16)
        pdf.set_text_color(25,47,133) 
        pdf.image("./images/prepost_fo_speed.png",10,125,w=180,h=120)    
        
        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        pdf.output('./documents/msc_prepost_report_with_api.pdf','F')
        #pdf.output('/Users/farseena/Downloads/msc_ME_PERFORMANCE_FOLDER/msc_PERFORMANCE_report_with_api.pdf')

    simple_table()

    return FileResponse(path = './documents/msc_prepost_report_with_api.pdf')




@router.post("/api/v1/pdf/charterparty")
async def index(info : Request,min_date :str = None , max_date : str = None , dep_port: str = None , arrival_port :str = None , vessel_name  : str = None , group:str = None , voyage : str = None,fleet : str = None, report_type : str = None  , warrented_do : str =None , weather_wind_force : str = None , weather_sea_state : str = None , current_factor : str = None):

    data = await info.json()


    # "http://192.168.54.32:9111/api/v1/cp/var?imo=9278052&voy_no=VOY-006&mindate=2020-11-06T00:00:00&maxdate=2020-12-30T23:59:59&sea_state=3&wind_force=4&current_factor=0.35&wdoc=0.1"


    #______Input Variables for Headings________#
    a=vessel_name
    # b= "14" #Group
    b = group
    # c= "60" #Voyage Parameter
    c  = voyage
    # d = "4B" # Fleet wis
    # 
    d = fleet

    #_____input parameters for Table 2_________
    # warrented_do =0.1 # Warranted DO Consumption About (MT/day)
    # weather_wind_force= 4 #Good Weather Wind Force
    # weather_sea_state = 3 #Good Weather Douglass Sea State
    # current_factor = 0.35    #Current Factor

    port = {
        'data':{
        'dep_port' : dep_port,
        'arrival_port' : arrival_port
        }
    }
    #________Table 1______________#
    port_df = pd.DataFrame.from_dict(port)
    port_table = port_df.T.reset_index()
    port_table['index'] = port_table['index'].str.replace('data', 'Port')

    #Extracting dates


    #Inserting date
    new_row = {'index':'Date', 'arrival_port':max_date, 'dep_port':min_date}
    #append row to the dataframe
    port_table = pd.concat([port_table, pd.DataFrame([new_row])])

    voy_det=port_table[['index','dep_port', 'arrival_port' ]]


    #________Table 2______________#
    Warrented_Speed =data['data']['warrented_speed']
    Warrented_fo =data['data']['warrented_fo']


    Speed_consmptn = {
        'Parameter' : ['Warranted Speed About (Knots)', 'Warranted FO Consumption About (MT/day)', 'Warranted DO Consumption About (MT/day)','Good Weather Wind Force','Good Weather Douglass Sea State','Current Factor'],
        'Value' : [Warrented_Speed, Warrented_fo, warrented_do,weather_wind_force,weather_sea_state,current_factor],
        
    }
    Speed_consmptn =pd.DataFrame(Speed_consmptn)






    #________Table 3______________#

    Tile_1 =data['data']['time_&_consumption_value']['tile_1']
    Tile_2 =data['data']['time_&_consumption_value']['tile_2']
    Tile_3 =data['data']['time_&_consumption_value']['tile_3']

    Tile1 = pd.DataFrame.from_dict(Tile_1)
    Tile2 = pd.DataFrame.from_dict(Tile_2)
    Tile3 = pd.DataFrame.from_dict(Tile_3)
    Tile1["Parameter"]="Time"
    Tile2["Parameter"]="Fuel Oil"
    Tile3["Parameter"]="Diesel Oil"
    time_conmptn= pd.concat([Tile1,Tile2,Tile3])

    time_conmptn_Final=time_conmptn[['Parameter','message', 'value' ]]
    time_conmptn_Final


    #________Table 4______________#


    Cal_Table_2 =data['data']['calculationTab']['Table2']
    time_cal = pd.DataFrame.from_dict(Cal_Table_2)

    #________Table 5______________#


    Cal_Table_1 =data['data']['calculationTab']['Table1']

    good_weather = pd.DataFrame.from_dict(Cal_Table_1)


    #________Table 6______________#

    Cal_Table_3 =data['data']['calculationTab']['Table3']


    conmptn_cal = pd.DataFrame.from_dict(Cal_Table_3)
    conmptn_cal

    ########### Converting to string for inserting into table ###############


    voy_det_object =voy_det.astype(str)
    good_weather_object =good_weather.astype(str)
    Speed_consmptn_object =Speed_consmptn.astype(str)

    time_cal_object =time_cal.astype(str)
    conmptn_cal_object =conmptn_cal.astype(str)
    time_conmptn_object =time_conmptn_Final.astype(str)



    def Charter_Party_pdf(spacing=3):

        #report_prepared_date= "11-10-2022"

        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.add_font('Arial', '', 'fonts/arial.ttf', uni=True) 

        pdf.set_font('Arial', 'B', 18)

        
        pdf.image(msc_logo_path,160,8,w=35)

    #Cell postion from left side
        pdf.set_xy(60,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(170, 60, 'CHARTER PARTY ANALYSIS',ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)#(x_start, y_start, x_end, y_end)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)
        #pdf.multi_cell(80,14.5,"Report Date :"+" "+ report_prepared_date, align='R')

        if  report_type=="Fleet Wise" :
            pdf.cell(10, 2, "Vessel Name :"+" "+a,ln=True)
            pdf.cell(12, 10,"Group:"+" "+ b,ln=True)
            pdf.cell(18, 2,"Fleet:"+" "+ d,ln=True)

        elif  report_type=="All Vessels": 
            pdf.cell(10, 13, "Vessel Name :"+" "+a,ln=True)
  
            
        pdf.set_line_width(.3)
        pdf.line(10, 70, 190, 70)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'Voyage Details',ln=True,align='C')
        pdf.line(10, 85, 190, 85)
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        pdf.set_font('Arial', "",13)
        pdf.cell(10, 12,"Voyage No :"+" "+ c,ln=True)
    #______________________________table 1__________________________________#    
        pdf.set_xy(10,105)
        spacing=3
        voy_head = [["Title","Departure","Arrival"]]
        voy_values = voy_det_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        for row in voy_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        for row in voy_values:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)

    #______________________________table 2__________________________________#    

        
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'Speed and Consumption Warranty & Good weather definition',ln=True,align='C')
    
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        
        pdf.set_xy(10,145)
        
        spacing=3
        Speed_consmptn_head = [["Parameter","Value"]]
        Speed_consmptn_values = Speed_consmptn_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        for row in Speed_consmptn_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        for row in Speed_consmptn_values:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        #______________________________table 3__________________________________#    

        
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'Time and Consumption Value',ln=True,align='C')
        
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        
        pdf.set_xy(10,215)
        spacing=3
        time_conmptn_head = [["Parameter","Message","Value"]]
        time_conmptn_values = time_conmptn_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        for row in time_conmptn_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        for row in time_conmptn_values:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")  
        #*********************************************** Page 2 **********************************************************#
        
        pdf.add_page()
        
        
        
    #______________________________table 4__________________________________#    

        pdf.set_xy(10,15)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Time Calculations',ln=True,align='C')
        
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        
        pdf.set_xy(10,30)
        spacing=3
        time_cal_head = [["Parameter","Time"]]
        time_cal_values = time_cal_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        for row in time_cal_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        for row in time_cal_values:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)

        
        
    
        #______________________________table 5__________________________________#    

        
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'Good Weather Analysis',ln=True,align='C')
        
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        
        pdf.set_xy(10,70)
        spacing=3
        good_weather_head = [["Parameter","Good Weather","Entire Voyage"]]
        good_weather_values = good_weather_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        for row in good_weather_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        for row in good_weather_values:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)    
        #______________________________table 6__________________________________#    
        
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'Consumption Analysis',ln=True,align='C')
    
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)    
        
        pdf.set_xy(10,132)
        spacing=3
        conmptn_cal_head = [["Parameter","Consumption in MT"]]
        conmptn_cal_values = conmptn_cal_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        for row in conmptn_cal_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        for row in conmptn_cal_values:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing) 
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")  
        
        
        
        pdf_name = vessel_name + '_Charter_Party_Analysis.pdf'                
        pdf.output('./documents/' + pdf_name,'F')

    pdf_name = vessel_name + '_Charter_Party_Analysis.pdf'
    Charter_Party_pdf()    


    return FileResponse(path = './documents/' +pdf_name)


@router.post('/api/v1/pdf/ae/performance')
async def index(info : Request):
    s = await info.json()
   
    Table1 = pd.DataFrame.from_dict(s['Results_tab']['table_1']).astype(str)
    vessel_name = Table1['particulars'].values[0]
    Test_Date= Table1['particulars'].values[4]
    Table_2 = pd.DataFrame.from_dict(s['Results_tab']['Table_2']).astype(str)
    Table_3= pd.DataFrame.from_dict(s['Results_tab']['Table_3']).astype(str)

    #1.JWC Vs Engine Speed- Graph 1
    chart_1_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_chart_1'][0]['scatter_1'])
    chart_1_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_chart_1'][0]['scatter_2'][0])
    chart_1_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_chart_1'][0]['test'])

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="Engine_load", y="Sfoc", data=chart_1_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(chart_1_scatter_2['Engine_load'], chart_1_scatter_2['Sfoc'],marker = 'o',label =chart_1_scatter_2['category'].values[0],color='#f7f707')
    plt.plot(chart_1_plot_1['x'], chart_1_plot_1['y'],color='#f7f707')
    plt.xlabel('Engine Load(%)',fontweight="bold",size=16)
    plt.ylabel('SFOC(g/kW-hr)',fontweight="bold",size=16)
    plt.title('Load Diagram', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/sfoc_vs_load.png')
    plt.clf()

    #chart 2
    chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/ssfoc_vs_load_Deviation.png')
    plt.clf()

    Table_4= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_table_1'])
    Table_4=Table_4.rename({'dates':'Date of Measurement','historicx':'Engine Load(%)','historicy':'SFOC(g/kW-hr)'},axis=1).astype(str)
    Table_5= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_table_2'])
    Table_5=Table_5.rename({'x':'Engine Load(%)','y':'SFOC(g/kW-hr)'},axis=1).astype(str)

    #texh_vs_load
    texh_vs_load_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_chart_1'][0]['scatter_1'])
    texh_vs_load_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_chart_1'][0]['scatter_2'][0])
    texh_vs_load_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_chart_1'][0]['test'])

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="Engine_load", y="texh", data=texh_vs_load_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(texh_vs_load_scatter_2['Engine_load'], texh_vs_load_scatter_2['texh'],marker = 'o',label =texh_vs_load_scatter_2['category'].values[0],color='#f7f707')
    plt.plot(texh_vs_load_plot_1['x'], texh_vs_load_plot_1['y'],color='#f7f707')
    plt.xlabel('Engine Load(%)',fontweight="bold",size=16)
    plt.ylabel('Correct Texh Cyl.Out.(deg.C)',fontweight="bold",size=16)
    plt.title('Texh Vs Load', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/sTexh_load.png')
    plt.clf()

    #chart2
    texh_vs_load_chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=texh_vs_load_chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/sTexh_load_deviation.png')
    plt.clf()

    Table_6= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_table_1'])
    Table_6=Table_6.rename({'dates':'Date of Measurement','historicx':'Engine Load(%)','historicy':'Texh(deg.C)'},axis=1).astype(str)
    Table_7= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_table_2'])
    Table_7=Table_7.rename({'x':'Engine Load(%)','y':'Texh(deg.C)'},axis=1).astype(str)

    #pumpmark_vs_load
    pumpmark_vs_load_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pm_vs_load_chart_1'][0]['scatter_1'])
    pumpmark_vs_load_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pm_vs_load_chart_1'][0]['scatter_2'][0])
    pumpmark_vs_load_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pm_vs_load_chart_1'][0]['test'])
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="Engine_load", y="Pump_mark", data=pumpmark_vs_load_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(pumpmark_vs_load_scatter_2['Engine_load'], pumpmark_vs_load_scatter_2['Pump_mark'],marker = 'o',label =pumpmark_vs_load_scatter_2['category'].values[0],color='#f7f707')
    plt.plot(pumpmark_vs_load_plot_1['x'], pumpmark_vs_load_plot_1['y'],color='#f7f707')
    plt.xlabel('Engine Load(%)',fontweight="bold",size=16)
    plt.ylabel('PumpMark',fontweight="bold",size=16)
    plt.title('PumpMark Vs Load', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/sPumpmark_load.png')
    plt.clf()

    #chart2
    pumpmark_vs_load_chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pm_vs_load_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=pumpmark_vs_load_chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/sPumpmark_load_deviation.png')
    plt.clf()

    Table_8= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pm_vs_load_table_1'])
    Table_8=Table_8.rename({'dates':'Date of Measurement','historicx':'Engine Load(%)','historicy':'PumpMark'},axis=1).astype(str)
    Table_9= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pm_vs_load_table_2'])
    Table_9=Table_9.rename({'x':'Engine Load(%)','y':'PumpMark'},axis=1).astype(str)

    #T_c_speed_load
    T_c_speed_load_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_chart_1'][0]['scatter_1'])
    T_c_speed_load_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_chart_1'][0]['scatter_2'][0])
    T_c_speed_load_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_chart_1'][0]['test'])
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="Engine_load", y="tc_speed", data=T_c_speed_load_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(T_c_speed_load_scatter_2['Engine_load'], T_c_speed_load_scatter_2['tc_speed'],marker = 'o',label =T_c_speed_load_scatter_2['category'].values[0],color='#f7f707')
    plt.plot(T_c_speed_load_plot_1['x'], T_c_speed_load_plot_1['y'],color='#f7f707')
    plt.xlabel('Engine Load(%)',fontweight="bold",size=16)
    plt.ylabel('Corrected T/C Speed(rpm)',fontweight="bold",size=16)
    plt.title('T/C Speed Vs Engine Load', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/sTc_speed_vs_load.png')
    plt.clf()

    #Chart 2
    T_c_speed_load_chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=T_c_speed_load_chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/sTc_speed_vs_load_deviation.png')
    plt.clf()

    Table_10= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_table_1'])
    Table_10=Table_10.rename({'dates':'Date of Measurement','historicx':'Engine Load(%)','historicy':'PumpMark'},axis=1).astype(str)
    Table_11= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_table_2'])
    Table_11=Table_11.rename({'x':'Engine Load(%)','y':'PumpMark'},axis=1).astype(str)

    #pcomp_vs_pscav
    pcomp_vs_pscav_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1'][0]['scatter_1'])
    pcomp_vs_pscav_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1'][0]['scatter_2'][0])
    pcomp_vs_pscav_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1'][0]['test'])
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="Pscav", y="Pcomp", data=pcomp_vs_pscav_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(pcomp_vs_pscav_scatter_2['Pscav'], pcomp_vs_pscav_scatter_2['Pcomp'],marker = 'o',label =pcomp_vs_pscav_scatter_2['category'].values[0],color='#f7f707')

    plt.plot(pcomp_vs_pscav_plot_1['x'], pcomp_vs_pscav_plot_1['y'],color='#f7f707')
    plt.xlabel('Corrected Pscav (MPa.abs)',fontweight="bold",size=16)
    plt.ylabel('Corrected Pcomp (bar)',fontweight="bold",size=16)
    plt.title('Pcomp vs Pscav', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/sPcomp_vs_Pscav.png')
    plt.clf()


    #chart2
    pcomp_vs_pscav_scatter_chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=pcomp_vs_pscav_scatter_chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/sPcomp_vs_Pscav_deviation.png')
    plt.clf()

    Table_12= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_table_1'])
    Table_12=Table_12.rename({'dates':'Date of Measurement','historicx':'Pscav (MPa.abs)','historicy':'Pcomp (bar)'},axis=1).astype(str)
    Table_13= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_table_2'])
    Table_13=Table_13.rename({'x':'Pscav (MPa.abs)','y':'Pcomp (bar)'},axis=1).astype(str)

    #pm_vs_engine_speed
    pm_vs_engine_speed_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1'][0]['scatter_1'])
    pm_vs_engine_speed_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1'][0]['scatter_2'][0])
    pm_vs_engine_speed_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1'][0]['test'])
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="Engine_speed", y="pump_mark", data=pm_vs_engine_speed_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(pm_vs_engine_speed_scatter_2['Engine_speed'], pm_vs_engine_speed_scatter_2['pump_mark'],marker = 'o',label =pm_vs_engine_speed_scatter_2['category'].values[0],color='#f7f707')
    plt.plot(pm_vs_engine_speed_plot_1['x'], pm_vs_engine_speed_plot_1['y'],color='#f7f707')
    plt.xlabel('Engine Speed (RPM)',fontweight="bold",size=16)
    plt.ylabel('Corrected Pump Mark',fontweight="bold",size=16)
    plt.title('PumpMark vs Engine Speed', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/spm_vs_engine_speed.png')
    plt.clf()

    #chart 2
    pm_vs_engine_speed_chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=pm_vs_engine_speed_chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/spm_vs_engine_speed_deviation.png')
    plt.clf()

    Table_14= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_table_1'])
    Table_14=Table_14.rename({'dates':'Date of Measurement','historicx':'Engine Speed (RPM)','historicy':'Pump Mark'},axis=1).astype(str)
    Table_15= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_table_2'])
    Table_15=Table_15.rename({'x':'Engine Speed (RPM)','y':'Pump Mark'},axis=1).astype(str)

    #tc_speed_vs_engine_speed
    tc_speed_vs_engine_speed_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_speed_engine_speed_chart_1'][0]['scatter_1'])
    tc_speed_vs_engine_speed_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_speed_engine_speed_chart_1'][0]['scatter_2'][0])
    tc_speed_vs_engine_speed_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_speed_engine_speed_chart_1'][0]['test'])
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="Engine_speed", y="tc_speed", data=tc_speed_vs_engine_speed_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(tc_speed_vs_engine_speed_scatter_2['Engine_speed'], tc_speed_vs_engine_speed_scatter_2['tc_speed'],marker = 'o',label =tc_speed_vs_engine_speed_scatter_2['category'].values[0],color='#f7f707')
    plt.plot(tc_speed_vs_engine_speed_plot_1['x'], tc_speed_vs_engine_speed_plot_1['y'],color='#f7f707')
    plt.xlabel('Engine Speed (RPM)',fontweight="bold",size=16)
    plt.ylabel('Corrected T/C Speed (RPM)',fontweight="bold",size=16)
    plt.title('T/C Speed vs Engine Speed', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/sTc_speed_vs_engine_speed.png')
    plt.clf()

    #chart 2
    tc_speed_vs_engine_speed_chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_speed_engine_speed_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=tc_speed_vs_engine_speed_chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/sT_C_Engine_Speed_deviation.png')
    plt.clf()

    Table_16= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_speed_engine_speed_table_1'])
    Table_16=Table_16.rename({'dates':'Date of Measurement','historicx':'Engine Speed (RPM)','historicy':'T/C Speed (RPM)'},axis=1).astype(str)
    Table_17= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_speed_engine_speed_table_2'])
    Table_17=Table_17.rename({'x':'Engine Speed (RPM)','y':'T/C Speed (RPM)'},axis=1).astype(str)

    #pscav_vs_load
    pscav_vs_load_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_chart_1'][0]['scatter_1'])
    pscav_vs_load_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_chart_1'][0]['scatter_2'][0])
    pscav_vs_load_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_chart_1'][0]['test'])

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="Engine_load", y="Pscav", data=pscav_vs_load_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(pscav_vs_load_scatter_2['Engine_load'], pscav_vs_load_scatter_2['Pscav'],marker = 'o',label =pscav_vs_load_scatter_2['category'].values[0],color='#f7f707')
    plt.plot(pscav_vs_load_plot_1['x'], pscav_vs_load_plot_1['y'],color='#f7f707')
    plt.xlabel('Engine Load (%)',fontweight="bold",size=16)
    plt.ylabel('PScav (Bar)',fontweight="bold",size=16)
    plt.title('Pscav vs Engine Load', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/spscav_vs_load.png')
    plt.clf()

    #chart 2
    pscav_vs_load_chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=pscav_vs_load_chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/spscav_vs_load_deviation.png')
    plt.clf()

    Table_18= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_table_1'])
    Table_18=Table_18.rename({'dates':'Date of Measurement','historicx':'Engine Load (%)','historicy':'PScav (Bar)'},axis=1).astype(str)
    Table_19= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_table_2'])
    Table_19=Table_19.rename({'x':'Engine Load (%)','y':'PScav (Bar)'},axis=1).astype(str)

    #pscav_vs_tc_speed
    pscav_vs_tc_speed_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['scatter_1'])
    pscav_vs_tc_speed_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['scatter_2'][0])
    pscav_vs_tc_speed_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['test'])
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="tc_speed", y="Pscav", data=pscav_vs_tc_speed_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(pscav_vs_tc_speed_scatter_2['tc_speed'], pscav_vs_tc_speed_scatter_2['Pscav'],marker = 'o',label =pscav_vs_tc_speed_scatter_2['category'].values[0],color='#f7f707')
    plt.plot(pscav_vs_tc_speed_plot_1['x'], pscav_vs_tc_speed_plot_1['y'],color='#f7f707')
    plt.xlabel('Corrected T/C Speed (RPM)',fontweight="bold",size=16)
    plt.ylabel('PScav (Bar)',fontweight="bold",size=16)
    plt.title('Pscav vs T/C Speed', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/spscav_vs_tc_speed.png')
    plt.clf()

    #chart 2

    pscav_vs_tc_speed_chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=pscav_vs_tc_speed_chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/spscav_vs_tc_speed_deviation.png')
    plt.clf()

    Table_20= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_table_1'])
    Table_20=Table_20.rename({'dates':'Date of Measurement','historicx':'T/C Speed (RPM)','historicy':'PScav (Bar)'},axis=1).astype(str)
    Table_21= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_table_2'])
    Table_21=Table_21.rename({'x':'T/C Speed (RPM)','y':'PScav (Bar)'},axis=1).astype(str)

    #pcomp_vs_load
    pcomp_vs_load_scatter_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_chart_1'][0]['scatter_1'])
    pcomp_vs_load_scatter_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_chart_1'][0]['scatter_2'][0])
    pcomp_vs_load_plot_1= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_chart_1'][0]['test'])

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.scatterplot(x="Engine_load", y="Pcomp", data=pcomp_vs_load_scatter_1,legend='auto',hue='Date',s=80)
    plt.scatter(pcomp_vs_load_scatter_2['Engine_load'], pcomp_vs_load_scatter_2['Pcomp'],marker = 'o',label =pcomp_vs_load_scatter_2['category'].values[0],color='#f7f707')

    plt.plot(pcomp_vs_load_plot_1['x'], pcomp_vs_load_plot_1['y'],color='#f7f707')
    plt.xlabel('Engine Load',fontweight="bold",size=16)
    plt.ylabel('PComp (Bar)',fontweight="bold",size=16)
    plt.title('Pcomp vs Engine Load(%)', size=18,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/spcomp_vs_load.png')
    plt.clf()

    #chart 2
    pcomp_vs_load_chart_2= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_chart_2'])
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(  x='date', y='deviation', data=pcomp_vs_load_chart_2,marker = 'o',markersize = 10)
    plt.xlabel('Month',fontweight="bold",size=16)
    plt.ylabel('Deviation %',fontweight="bold",size=16)
    plt.title('% deviation', size=18,fontweight="bold")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    plt.savefig('./images/spcomp_vs_load_deviation.png')
    plt.clf()

    Table_22= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_table_1'])
    Table_22=Table_22.rename({'dates':'Date of Measurement','historicx':'Engine Load (%)','historicy':'PComp (Bar)'},axis=1).astype(str)
    Table_23= pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_table_2'])
    Table_23=Table_23.rename({'x':'Engine Load (%)','y':'PComp (Bar)'},axis=1).astype(str)

    #max_pres
    max_pres_chart_1= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_chart_1'])
    max_pres_cylinder_No=max_pres_chart_1['cylinder'].max()-1
    max_pres_chart_2= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_chart_2'][0])
    max_pres_table_1= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_table_1'])
    max_pres_table_1=max_pres_table_1[['cylinder', 'Measured', 'average', 'deviation', 'result']]
    max_pres_table_1['Measured']=max_pres_table_1['Measured'].astype(int)
    max_pres_table_1=max_pres_table_1.astype(str)
    max_pres_table_1=max_pres_table_1.rename(columns={'cylinder':'Cylinder Number','measure': 'Measured Value (Bar)', 
                                                        'average':'Average Value',
                                                        'deviation': 'Deviation','result': 'Result'}).astype(str)

    #chart 1
    color =  ['#588aee','#57cfa0']
    #______________   Pmax   ____________________
    plt.title('Pmax Mean',fontweight="bold",size=14)

    fig_pmax=sns.barplot(data=max_pres_chart_2, x="x", y="y",hue="x",palette=color)
    ax1=fig_pmax
    for p in ax1.patches:
        ax1.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                    textcoords='offset points')
    ax1.get_legend().remove()
    fig_pmax.grid(False)
    fig_pmax.set_xlabel('',fontweight="bold",size=0)
    fig_pmax.set_ylabel('Bar',fontweight="bold",size=14)
    plt.savefig('./images/sPmax_mean.png')
    plt.clf()

    #chart 2
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.barplot(x="cylinder", y="deviation", data=max_pres_chart_1,color='#588aee')
    plt.xlabel('Cylinder No',fontweight="bold",size=16)
    plt.ylabel('Deviation from mean (bar)',fontweight="bold",size=16)
    plt.title('Pmax Deviation', size=18,fontweight="bold")
    ax.legend(title=None)
    ax.get_legend().remove()
    plt.savefig('./images/spmax_deviation.png')
    plt.clf()

    #comp_press
    comp_press_chart_1= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_chart_1'])
    comp_press_cylinder_No=comp_press_chart_1['Cylinder'].max()-1
    comp_press_chart_2= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_chart_2'][0])
    comp_press_table_1= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_table_1'])
    comp_press_table_1=comp_press_table_1[['cylinder', 'measure', 'average', 'deviation', 'result']]
    comp_press_table_1['measure']=comp_press_table_1['measure'].astype(int)
    comp_press_table_1=comp_press_table_1.rename(columns={'cylinder':'Cylinder Number','measure': 'Measured Value (Bar)', 
                                                        'average':'Average Value',
                                                        'deviation': 'Deviation','result': 'Result'}).astype(str)

    #chart 1
    color =  ['#588aee','#57cfa0']
    #______________   Pmax   ____________________
    plt.title('Pcomp Mean',fontweight="bold",size=14)

    fig_pmax=sns.barplot(data=comp_press_chart_2, x="x", y="y",hue="x",palette=color)
    ax1=fig_pmax
    for p in ax1.patches:
        ax1.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                    textcoords='offset points')
    ax1.get_legend().remove()
    fig_pmax.grid(False)
    fig_pmax.set_xlabel('',fontweight="bold",size=0)
    fig_pmax.set_ylabel('Bar',fontweight="bold",size=14)
    plt.savefig('./images/sPcomp_mean.png')
    plt.clf()

    #chart 2
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.barplot(x="Cylinder", y="deviation", data=comp_press_chart_1,color='#588aee')
    plt.xlabel('Cylinder No',fontweight="bold",size=16)
    plt.ylabel('Deviation from mean (bar)',fontweight="bold",size=16)
    plt.title('Pcomp Deviation', size=18,fontweight="bold")
    ax.legend(title=None)
    ax.get_legend().remove()
    plt.savefig('./images/spcomp_deviation.png')
    plt.clf()

    #exh_temp
    exh_temp_chart_1= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_chart_1'])
    exh_temp_cylinder_No=exh_temp_chart_1['Cylinder'].max()-1
    exh_temp_chart_2= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_chart_2'][0])
    exh_temp_table_1= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_table_1'])
    exh_temp_table_1=exh_temp_table_1[['cylinder', 'ex_temp', 'average', 'deviation', 'result']]
    exh_temp_table_1['ex_temp']=exh_temp_table_1['ex_temp'].astype(int)
    exh_temp_table_1=exh_temp_table_1.rename(columns={'cylinder':'Cylinder Number','ex_temp': 'Measured Value (Bar)', 
                                                        'average':'Average Value',
                                                        'deviation': 'Deviation','result': 'Result'}).astype(str)

    #chart 1
    color =  ['#588aee','#57cfa0']
    #______________   Pmax   ____________________
    plt.title('Exhaust Temp Mean',fontweight="bold",size=14)

    fig_pmax=sns.barplot(data=exh_temp_chart_2, x="x", y="y",hue="x",palette=color)
    ax1=fig_pmax
    #annotate axis = seaborn axis
    for p in ax1.patches:
        ax1.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                    textcoords='offset points')
    ax1.get_legend().remove()
    fig_pmax.grid(False)
    fig_pmax.set_xlabel('',fontweight="bold",size=0)
    fig_pmax.set_ylabel('Bar',fontweight="bold",size=14)
    plt.savefig('./images/sexh_temp_mean.png')
    plt.clf()

    #chart2 
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.barplot(x="Cylinder", y="deviation", data=exh_temp_chart_1,color='#588aee')
    plt.xlabel('Cylinder No',fontweight="bold",size=16)
    plt.ylabel('Deviation from mean (bar)',fontweight="bold",size=16)
    plt.title('Exhaust Temp Deviation', size=18,fontweight="bold")
    ax.legend(title=None)
    ax.get_legend().remove()
    plt.savefig('./images/sexh_temp_deviation.png')
    plt.clf()

    #Pump Mark
    pump_mark_chart_1= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['pump_mark_chart_1'])
    pump_mark_cylinder_No=pump_mark_chart_1['cylinder'].max()-1
    pump_mark_table_1= pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['pump_mark_table_1'])
    pump_mark_table_1=pump_mark_table_1[['cylinder', 'ex_temp', 'average', 'deviation', 'result']]
    pump_mark_table_1['ex_temp']=pump_mark_table_1['ex_temp'].astype(int)
    pump_mark_table_1=pump_mark_table_1.rename(columns={'cylinder':'Cylinder Number','ex_temp': 'Measured Value (Bar)', 
                                                        'average':'Average Value',
                                                        'deviation': 'Deviation','result': 'Result'}).astype(str)
    pump_mark_chart_1_sum=pump_mark_chart_1['cylinder'].sum()+pump_mark_chart_1['deviation'].sum()

    #chart 1
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.barplot(x="cylinder", y="deviation", data=pump_mark_chart_1,color='#588aee')
    plt.xlabel('Cylinder No',fontweight="bold",size=16)
    plt.ylabel('Pump Mark Deviation from mean',fontweight="bold",size=16)
    plt.title('Pump Mark Deviation', size=18,fontweight="bold")
    ax.legend(title=None)
    ax.get_legend().remove()
    plt.savefig('./images/spumpmark_deviation.png')
    plt.clf()

    from fpdf import FPDF
    def simple_table(spacing=3):

        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        
        pdf.image(msc_logo_path,160,8,w=30)

    #Cell postion from left side
        pdf.set_xy(55,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(170, 60, 'Engine Monitoring Report')
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 199, 50)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)
        
        pdf.cell(10, 2, "Vessel Name :"+" "+vessel_name,ln=True)
        pdf.cell(10, 12,"Test Date :"+" "+ Test_Date,ln=True)
        
        pdf.line(10, 70, 199, 70)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'Engine Type',ln=True,align='C')
        pdf.line(10, 85, 199, 85)
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        
        pdf.set_xy(10,92)
        tablefirst_head = [['Title','Particulars']]
        tablefirst = Table1.values.tolist()
        pdf.set_font("Arial",'B', size=10)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial",'B', size=10)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 2 page **********************************************************#        
        pdf.add_page()  
        pdf.line(10, 15, 199, 15)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 24, 'Result Table',ln=True,align='C') 
        pdf.line(10, 30, 199, 30) 
        
    
        spacing = 3.5
        tablefirst_head1 = [['Title', 'Kind of Graph', 'Shoptrial Value','Analysis Result','Status']]
        tablefirst1 = Table_2.values.tolist()
        pdf.set_font("Arial",'B', size=8)
        col_width = pdf.w /5.55
        row_height = pdf.font_size
        for row in tablefirst_head1:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
            
        pdf.set_font("Arial", size=8)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /5.55
        row_height = pdf.font_size
        for row in tablefirst1:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        pdf.line(10, 137, 199, 137)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 24, 'TRH Table',ln=True,align='C') 
        pdf.line(10, 150, 199, 150)   
        
        spacing = 3.5
        tablefirst_head2 = [['Title', 'Particulars']]
        tablefirst2 = Table_3.values.tolist()
        pdf.set_font("Arial",'B', size=8)
        
        #pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.22
        row_height = pdf.font_size
        for row in tablefirst_head2:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
            
        pdf.set_font("Arial", size=8)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.22
        row_height = pdf.font_size
        for row in tablefirst2:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)        
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        #*********************************************** 3 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Engine Performance',ln=True,align='C')   
        pdf.cell(178, 15, '1. JWC Vs Engine Speed',ln=True,align='C')
        pdf.image("./images/sfoc_vs_load.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/ssfoc_vs_load_Deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
        spacing=3
        tablefirst_head3 = [['Date of Measurment', 'Engine Load(%)', 'SFOC(g/kW-hr)']]
        tablefirst3 = Table_4.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head3:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst3:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head4 = [['Engine Load(%)', 'SFOC(g/kW-hr)']]
        tablefirst4 = Table_5.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head4:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst4:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")  
        
        #*********************************************** 4 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '2. Texh Vs Engine Load',ln=True,align='C')
        pdf.image("./images/sTexh_load.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/sTexh_load_deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        spacing=3
        tablefirst_head5 = [['Date of Measurment', 'Engine Load(%)', 'Texh(deg.C)']]
        tablefirst5 = Table_6.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head5:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst5:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head6 = [['Engine Load(%)', 'Texh(deg.C)']]
        tablefirst6 = Table_7.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head6:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst6:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 5 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '3. Pump Mark Vs Engine Speed',ln=True,align='C')
        pdf.image("./images/sPumpmark_load.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/sPumpmark_load_deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
        spacing=3
        tablefirst_head7 = [['Date of Measurment', 'Engine Load(%)', 'PumpMark']]
        tablefirst7 = Table_8.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head7:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst7:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head8 = [['Engine Load(%)', 'PumpMark']]
        tablefirst8 = Table_9.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head8:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst8:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 6 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '4. T/C Speed Vs Engine Load',ln=True,align='C')
        pdf.image("./images/sTc_speed_vs_load.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/sTc_speed_vs_load_deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
        spacing=3
        tablefirst_head9 = [['Date of Measurment', 'Engine Load(%)', 'T/C Speed (rpm)']]
        tablefirst9 = Table_10.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head9:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst9:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head10 = [['Engine Load(%)', 'T/C Speed (rpm)']]
        tablefirst10 = Table_11.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head10:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst10:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 7 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '5. Pcomp Vs Pscav',ln=True,align='C')
        pdf.image("./images/sPcomp_vs_Pscav.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/sPcomp_vs_Pscav_deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
        spacing=3
        tablefirst_head11 = [['Date of Measurment', 'Pscav (MPa.abs)', 'Pcomp (bar)']]
        tablefirst11 = Table_12.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head11:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst11:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head12 = [['Pscav (MPa.abs)', 'Pcomp (bar)']]
        tablefirst12 = Table_13.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head12:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst12:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 8 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '6. Pumpmark Vs Engine Speed',ln=True,align='C')
        pdf.image("./images/spm_vs_engine_speed.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/spm_vs_engine_speed_deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
        spacing=3
        tablefirst_head13 = [['Date of Measurment', 'Engine Speed (RPM)', 'Pump Mark']]
        tablefirst13 = Table_14.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head13:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst13:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head14 = [['Engine Speed (RPM)', 'Pump Mark']]
        tablefirst14 = Table_15.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head14:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst14:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 9 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '7. T/C Speed Vs Engine Speed',ln=True,align='C')
        pdf.image("./images/sTc_speed_vs_engine_speed.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/sT_C_Engine_Speed_deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
        spacing=3
        tablefirst_head15 = [['Date of Measurment','Engine Speed (RPM)', 'T/C Speed (RPM)']]
        tablefirst15 = Table_16.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head15:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst15:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head16 = [['Engine Speed (RPM)', 'T/C Speed (RPM)']]
        tablefirst16 = Table_17.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head16:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst16:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 10 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '8. Pscav Vs Engine Load',ln=True,align='C')
        pdf.image("./images/spscav_vs_load.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/spscav_vs_load_deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
        spacing=3
        tablefirst_head17 = [['Date of Measurment','Engine Load (%)', 'PScav (Bar)']]
        tablefirst17 = Table_18.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head17:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst17:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head18 = [['Engine Load (%)', 'PScav (Bar)']]
        tablefirst18 = Table_19.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head18:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst18:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 11 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '9. Pscav Vs T/C Speed',ln=True,align='C')
        pdf.image("./images/spscav_vs_tc_speed.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/spscav_vs_tc_speed_deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
        spacing=3
        tablefirst_head19 = [['Date of Measurment','T/C Speed (RPM)', 'PScav (Bar)']]
        tablefirst19 = Table_20.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head19:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst19:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head20 = [['T/C Speed (RPM)', 'PScav (Bar)']]
        tablefirst20 = Table_21.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head20:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst20:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 12 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '10. Pcomp Vs Engine Load',ln=True,align='C')
        pdf.image("./images/spcomp_vs_load.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/spcomp_vs_load_deviation.png",105,32,w=108,h=80)
        
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)
        
        
        spacing=3
        tablefirst_head21 = [['Date of Measurment','Engine Load (%)', 'PComp (Bar)']]
        tablefirst21 = Table_22.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst_head21:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.319
        row_height = pdf.font_size
        for row in tablefirst21:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,35,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,185)
        
        spacing=3
        tablefirst_head22 = [['Engine Load (%)', 'PComp (Bar)']]
        tablefirst22 = Table_23.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst_head22:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.21
        row_height = pdf.font_size
        for row in tablefirst22:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        #*********************************************** 13 page **********************************************************#     
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Cylinder Comparison',ln=True,align='C')   
        pdf.cell(178, 15, '1. Maximum Pressure',ln=True,align='C')
        pdf.image("./images/sPmax_mean.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/spmax_deviation.png",105,32,w=108,h=80)
        
        pdf.set_xy(10,140)
        
        spacing=3
        tablefirst_head23 = [['Cylinder Number', 'Measured Value (Bar)', 'Average Value','Deviation', 'Result']]
        tablefirst23 = max_pres_table_1.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /5.54
        row_height = pdf.font_size
        for row in tablefirst_head23:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /5.54
        row_height = pdf.font_size
        for row in tablefirst23:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
            #*********************************************** 14 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133) 
        pdf.cell(178, 15, '2. Compressor Pressure',ln=True,align='C')
        pdf.image("./images/sPcomp_mean.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/spcomp_deviation.png",105,32,w=108,h=80)
        
        pdf.set_xy(10,140)
        
        spacing=3
        tablefirst_head24 = [['Cylinder Number', 'Measured Value (Bar)', 'Average Value','Deviation', 'Result']]
        tablefirst24 = comp_press_table_1.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /5.54
        row_height = pdf.font_size
        for row in tablefirst_head24:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /5.54
        row_height = pdf.font_size
        for row in tablefirst24:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")  
        
        #*********************************************** 15 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133) 
        pdf.cell(178, 15, '3. M/E Cyl. Exhaust Temperature',ln=True,align='C')
        pdf.image("./images/sexh_temp_mean.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        
        pdf.image("./images/sexh_temp_deviation.png",105,32,w=108,h=80)
        
        pdf.set_xy(10,140)
        
        spacing=3
        tablefirst_head25 = [['Cylinder Number', 'Measured Value (Deg.C)', 'Average Value','Deviation', 'Result']]
        tablefirst25 = exh_temp_table_1.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /5.54
        row_height = pdf.font_size
        for row in tablefirst_head25:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
            
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /5.54
        row_height = pdf.font_size
        for row in tablefirst25:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
    #*********************************************** 16 page **********************************************************#
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133) 
        pdf.cell(178, 15, '4. Pumpmark',ln=True,align='C')
        if pump_mark_chart_1_sum==0:
            pdf.set_font("Arial",'B', size=15)
            pdf.set_text_color(0,0,0) 
            pdf.set_xy(20,30)
            pdf.cell(170, 15, '',ln=True,align='C',border=1)
            pdf.set_xy(95,28)
            pdf.cell(20, 20, 'NULL',ln=True,align='C')
        else:
            pdf.image("./images/spumpmark_deviation.png",25,32,w=150,h=80)
            pdf.set_font("Arial",'B', size=8)
            pdf.set_text_color(0,0,0)


            pdf.set_xy(10,140)

            spacing=3
            tablefirst_head26 = [['Cylinder Number', 'Measured Value (Deg.C)', 'Average Value','Deviation', 'Result']]
            tablefirst26 = pump_mark_table_1.values.tolist()
            pdf.set_font("Arial",'B', size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /5.54
            row_height = pdf.font_size
            for row in tablefirst_head26:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /5.54
            row_height = pdf.font_size
            for row in tablefirst26:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        pdf_name = 'MSC_AE_Performance_Report_' + vessel_name + '.pdf' 
        pdf.output('./documents/' + pdf_name,'F')

    
    pdf_name = 'MSC_AE_Performance_Report_' + vessel_name + '.pdf'
    simple_table()

    return FileResponse(path = './documents/'+pdf_name,filename='AE.pdf')



@router.post('/api/v1/pdf/electrical')
async def index(info : Request , vessel_name:str = None,type:str=None,period:str=None,engine:str=None,fleet:str = None , classes:str =None):
    s = await info.json()
    print(s)
   
    if type == 'vessel':
        
        data1 = pd.DataFrame.from_dict(s['data']['table_data'])
        data1['test_load'] = data1['test_load'].astype(str)
        data1['test_load'] = data1['test_load'].replace('NonekW', np.nan)
        num_rows = data1.shape[0]
        data12=data1.rename(columns={
            'parameters': 'Parameters',
            'test_load': 'Test Load',
            'load_teasted_kw': 'Load Tested (kW)',
            'rated_capacity': 'Rated Capacity (kW)',
            'max_cont_loading_possible_upto': 'Max.Cont.loading Possible Upto',
            'remarks': 'Remarks',
            'model': 'Model'
        })

        column_order = ['Parameters', 'Test Load', 'Model', 'Rated Capacity (kW)', 'Load Tested (kW)', 'Max.Cont.loading Possible Upto', 'Remarks']

        data12 = data12[column_order]
        data12
        if data1['test_load'].isna().sum()!=num_rows:
            h = data1[data1['test_load'].notnull()]
            h['test_load'] = h['test_load'].str.replace('kW', '')
        else:
            h = data1
            
        dict1 = pd.Series(h['test_load'].values,index=h['parameters']).to_dict()
        data2 = pd.DataFrame.from_dict(s['data']['data']['chardata'])
        data2['Date'] = pd.to_datetime(data2['date'], dayfirst = True)
        data2 = data2.fillna(0)
        
        lst = data2['key_name'].unique().tolist()
        
        c = pd.DataFrame(columns=['Machine', 'Test Load','Test Date','Max. Noon Reported Load','Reported Date']) 
        m = 0
        for i in lst:
            a = data2[data2['key_name']==i]
            max_value_row = a.loc[a['value'].idxmax()]
            max_value_rows = a.loc[a['value'] == a['value'].max()]
            b = max_value_rows.head(1)
            b['date_time'] = pd.to_datetime(b['Date'])
            b['first_of_month'] = b['date_time'].apply(lambda x: datetime(x.year, x.month, 1) if x.day == 1 else x - pd.offsets.MonthBegin(1))
            b = b.astype(str)

            # Create a list for each row and append it to the DataFrame
            d = [b['key_name'].values[0], np.nan, b['first_of_month'].values[0], b['value'].values[0], b['Date'].values[0]]
            c.loc[m] = d
            m += 1     
            
        c['Test Load'] = np.nan
        c['Test Load'] = c['Test Load'].fillna(c['Machine'].apply(lambda x: dict1.get(x)))    
        
        data1_ae_engine_data = data1[data1['parameters']==engine]
        data1_ae_engine_data['max_cont_loading_possible_upto'] = data1_ae_engine_data['max_cont_loading_possible_upto'].astype(str)
        data1_ae_engine_data = data1_ae_engine_data[data1_ae_engine_data['max_cont_loading_possible_upto'] != 'None']
        data2_ae_engine_data = data2[data2['key_name']==engine]
        if data1_ae_engine_data.empty:
            data2_ae_engine_data['line1'] = 0
        else:
            data2_ae_engine_data['line1'] = data1_ae_engine_data['max_cont_loading_possible_upto'].values[0]
            data2_ae_engine_data['line1'] = data2_ae_engine_data['line1'].str.replace('%', '')

        data2_ae_engine_data['line1'] = data2_ae_engine_data['line1'].astype(float)
        data2_ae_engine_data['Test Load'] = np.nan
        data2_ae_engine_data['Test Load'] = data2_ae_engine_data['Test Load'].fillna(data2_ae_engine_data['key_name'].apply(lambda x: dict1.get(x)))
        data2_ae_engine_data['Test Load'] = data2_ae_engine_data['Test Load'].replace('None%', 0)
        data2_ae_engine_data['Test Load'] = data2_ae_engine_data['Test Load'].replace('None', 0)
        data2_ae_engine_data['Test Load'] = data2_ae_engine_data['Test Load'].astype(float)
        
        
        data2_ae_engine_data['New_column'] = data2_ae_engine_data['Date'].groupby(data2_ae_engine_data['Date']).cumcount().add(1)
        data2_ae_engine_data['New_column'] = data2_ae_engine_data['New_column'].apply(lambda x: chr(64 + x))
        data2_ae_engine_data['New_column'] = 'Noon Report Data'

        #Graph Code

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(13, 10))

        ax = sns.barplot(x="date", y="value", hue="New_column", data=data2_ae_engine_data)
        if not data2_ae_engine_data['Test Load'].isna().all():
            sns.lineplot(x="date", y="Test Load", data=data2_ae_engine_data, color='yellow', label='Tested Load')
            sns.lineplot(x="date", y="line1", data=data2_ae_engine_data, color='red', label='Maximum Continuous Loading')
        plt.xlabel('Date', fontweight="bold", size=16)
        plt.ylabel('%LOAD', fontweight="bold", size=16)
        plt.title('Auxiliary Electrical Load', size=18, fontweight="bold")
        
        ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        plt.xticks(rotation=45)
        handles, labels = ax.get_legend_handles_labels()
        #ax.legend(handles + [plt.Line2D([0], [0], color='yellow')], ['Tested Load','Maximum Continuous Loading','Noon Reported Data'],title=None,loc='upper right')
        ax.legend(loc='upper right')
        plt.savefig('./images/elecrical_graph.png')
        
        # plt.rcParams["font.weight"] = "bold"
        # plt.rcParams["axes.labelweight"] = "bold"
        # plt.figure(figsize=(13,10))
        # ax = sns.barplot(x="date", y="value", data=data2_ae_engine_data,color='blue',label ='Noon Reported Data')
        # sns.lineplot(x="date", y="line1", data=data2_ae_engine_data,color='brown',label='Maximum Continuos Loading') 
        # all_nan = data2_ae_engine_data['Test Load'].isna().all()
        # if all_nan:
        #     pass
        # else:
        #     sns.lineplot(x="date", y="Test Load", data=data2_ae_engine_data,color='yellow',label='Tested Load')
        # plt.xlabel('Date',fontweight="bold",size=16)
        # plt.ylabel('%LOAD',fontweight="bold",size=16)
        # plt.title('Auxillaries Electrical Load', size=18,fontweight="bold")
        # ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        # plt.xticks(rotation=45)
        # ax.legend(title=None)
        # plt.savefig('./images/elecrical_graph.png')
        
        c['Test Load'] = c['Test Load'].replace(np.nan,'')
        c = c.astype(str)
        data12['Test Load'] = data12['Test Load'].replace(np.nan,'')
        data12 = data12.astype(str)
        
        from fpdf import FPDF
        def simple_table(spacing=3):

            pdf = FPDF()
            #*********************************************** 1 page **********************************************************#
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)

            
            pdf.image(msc_logo_path,160,8,w=30)

        #Cell postion from left side
            pdf.set_xy(65,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(175, 60, 'Monthly Electrical Report')
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 199, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",13)
            pdf.set_xy(10,55)

            pdf.cell(10, 2, "Vessel :"+" "+vessel_name,ln=True)
            pdf.cell(10, 12,"Monitoring Period :"+" "+ period,ln=True)
            pdf.line(10, 70, 199, 70)

            pdf.set_xy(10, 75)
            spacing = 2  # Adjust the spacing as needed

            tablefirst_head1 = [data12.columns.tolist()]
            tablefirst1 = data12.values.tolist()

            pdf.set_font("Arial", "B", size=7)




            col_widths = [max(pdf.get_string_width(str(item)) for item in col) + 3 for col in zip(*tablefirst_head1, *tablefirst1)]
            # Header
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(21, 55, 188)

            for item, width in zip(tablefirst_head1[0], col_widths):
                pdf.cell(width, 8, txt=item, border=1, fill=True)
            pdf.ln(8)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0, 0, 0)


            for row in tablefirst1:
                for item, width in zip(row, col_widths):
                     pdf.cell(width, 8, txt=str(item), border=1)
                pdf.ln(8)
            pdf.set_xy(10,130)    
            pdf.set_font('Arial', "B",14)    
            pdf.cell(10, 20, "Auxiliary Engine Selected :"+" "+engine,ln=True)  
            pdf.image("./images/elecrical_graph.png",20,150,w=160,h=110) 

            #Page Number
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 


            pdf.output(pdf_name,'F')
        pdf_name = './documents/MSC_Electrical_report_with_api' + vessel_name + '.pdf'

        simple_table()     

    else:#fleet wise
        
     
        
        data1 = pd.DataFrame.from_dict(s['data']['table_data'])
        data1['test_load'] = data1['test_load'].astype(str)
        data1['test_load'] = data1['test_load'].replace('NonekW', np.nan)
        num_rows = data1.shape[0]
        if data1['test_load'].isna().sum()!=num_rows:
            h = data1[data1['test_load'].notnull()]
            h['test_load'] = h['test_load'].str.replace('kW', '')
        else:
            h = data1
            
        dict1 = pd.Series(h['test_load'].values,index=h['parameters']).to_dict()
        data2 = pd.DataFrame.from_dict(s['data']['data']['chardata'])
        data2['Date'] = pd.to_datetime(data2['date'], dayfirst = True)
        data2 = data2.fillna(0)
        
        lst = data2['key_name'].unique().tolist()
        
        c = pd.DataFrame(columns=['Machine', 'Test Load','Test Date','Max. Noon Reported Load','Reported Date']) 
        m = 0
        for i in lst:
            a = data2[data2['key_name']==i]
            max_value_row = a.loc[a['value'].idxmax()]
            max_value_rows = a.loc[a['value'] == a['value'].max()]
            b = max_value_rows.head(1)
            b['date_time'] = pd.to_datetime(b['Date'])
            b['first_of_month'] = b['date_time'].apply(lambda x: datetime(x.year, x.month, 1) if x.day == 1 else x - pd.offsets.MonthBegin(1))
            b = b.astype(str)
            d = []
            d.append(b['key_name'].values[0])
            d.append(np.nan)
            d.append(b['first_of_month'].values[0])
            d.append(b['value'].values[0])
            d.append(b['Date'].values[0])
            c.loc[m] = (d)
            m = m+1
            
        c['Test Load'] = np.nan
        c['Test Load'] = c['Test Load'].fillna(c['Machine'].apply(lambda x: dict1.get(x)))    
        
        data1_ae_engine_data = data1[data1['parameters']==engine]
        data1_ae_engine_data['max_cont_loading_possible_upto'] = data1_ae_engine_data['max_cont_loading_possible_upto'].astype(str)
        data1_ae_engine_data = data1_ae_engine_data[data1_ae_engine_data['max_cont_loading_possible_upto'] != 'None']
        data2_ae_engine_data = data2[data2['key_name']==engine]
        print(data2_ae_engine_data)
        if data1_ae_engine_data.empty:
            data2_ae_engine_data['line1'] = 0
        else:
            data2_ae_engine_data['line1'] = data1_ae_engine_data['max_cont_loading_possible_upto'].values[0]
            data2_ae_engine_data['line1'] = data2_ae_engine_data['line1'].str.replace('%', '')
       
        data2_ae_engine_data['line1'] = data2_ae_engine_data['line1'].astype(float)
        data2_ae_engine_data['Test Load'] = np.nan
        data2_ae_engine_data['Test Load'] = data2_ae_engine_data['Test Load'].fillna(data2_ae_engine_data['key_name'].apply(lambda x: dict1.get(x)))
        data2_ae_engine_data['Test Load'] = data2_ae_engine_data['Test Load'].replace('None%', 0)
        data2_ae_engine_data['Test Load'] = data2_ae_engine_data['Test Load'].replace('None', 0)
        data2_ae_engine_data['Test Load'] = data2_ae_engine_data['Test Load'].astype(float)


        data2_ae_engine_data['New_column'] = data2_ae_engine_data['Date'].groupby(data2_ae_engine_data['Date']).cumcount().add(1)
        data2_ae_engine_data['New_column'] = data2_ae_engine_data['New_column'].apply(lambda x: chr(64 + x))
        
        #Graph Code

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(13, 10))

        ax = sns.barplot(x="date", y="value", hue="New_column", data=data2_ae_engine_data)
        if not data2_ae_engine_data['Test Load'].isna().all():
            sns.lineplot(x="date", y="Test Load", data=data2_ae_engine_data, color='yellow', label='Tested Load')

        plt.xlabel('Date', fontweight="bold", size=16)
        plt.ylabel('%LOAD', fontweight="bold", size=16)
        plt.title('Auxiliary Electrical Load', size=18, fontweight="bold")
        
        ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        plt.xticks(rotation=45)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles + [plt.Line2D([0], [0], color='yellow')], ['Tested Load','Noon Reported Data','Noon Reported Data'], title=None)
        plt.savefig('./images/elecrical_graph_fleet.png')


        # plt.rcParams["font.weight"] = "bold"
        # plt.rcParams["axes.labelweight"] = "bold"
        # plt.figure(figsize=(13,10))
        # ax = sns.barplot(x="date", y="value", data=data2_ae_engine_data,color='blue',label ='Noon Reported Data')
        # sns.lineplot(x="date", y="line1", data=data2_ae_engine_data,color='brown',label='Maximum Continuos Loading')
        # all_nan = data2_ae_engine_data['Test Load'].isna().all()
        # if all_nan:
        #     pass
        # else:
        #     sns.lineplot(x="date", y="Test Load", data=data2_ae_engine_data,color='yellow',label='Tested Load')
        # plt.xlabel('Date',fontweight="bold",size=16)
        # plt.ylabel('%LOAD',fontweight="bold",size=16)
        # plt.title('Auxillaries Electrical Load', size=18,fontweight="bold")
        # ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        # plt.xticks(rotation=45)
        # ax.legend(title=None)
        # plt.savefig('./images/elecrical_graph_fleet.png')
        
        c['Test Load'] = c['Test Load'].replace(np.nan,'')
        c = c.astype(str)
        
        from fpdf import FPDF
        def simple_table(spacing=3):

            pdf = FPDF()
            #*********************************************** 1 page **********************************************************#
            pdf.add_page()
            pdf.set_font('Arial', 'B', 18)

            
            pdf.image(msc_logo_path,160,8,w=30)

        #Cell postion from left side
            pdf.set_xy(65,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(175, 60, 'Monthly Electrical Report')
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 199, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",13)
            pdf.set_xy(10,55)

            pdf.cell(10, 2, "Fleet :"+" "+fleet,ln=True)
            pdf.cell(10, 12,"Class :"+" "+ classes,ln=True)
            pdf.cell(10, 2, "Vessel :"+" "+vessel_name,ln=True)
            pdf.cell(10, 12, "Monitoring Period :"+" "+period,ln=True)

            pdf.line(10, 80, 199, 80)

            pdf.set_xy(10,82)
            spacing=3
            tablefirst_head1 = [c.columns.tolist()]
            tablefirst1 = c.values.tolist()
            pdf.set_font("Arial",'B', size=8)
            col_width = pdf.w /5.5
            row_height = pdf.font_size
            for row in tablefirst_head1:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=8)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /5.5
            row_height = pdf.font_size
            for row in tablefirst1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            pdf.set_xy(10,130)    
            pdf.set_font('Arial', "B",14)    
            pdf.cell(10, 20, "Auxiliary Engine Selected :"+" "+engine,ln=True)  
            pdf.image("./images/elecrical_graph_fleet.png",20,150,w=160,h=110) 

            #Page Number
            pdf.set_y(273)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 


            pdf.output(pdf_name,'F')


        pdf_name = './documents/MSC_Electrical_report_fleet_with_api' + vessel_name + '.pdf'
        simple_table()     

    return FileResponse(path = pdf_name,filename='Electrical.pdf')


@router.post('/api/v1/pdf/me/performance')
async def index(info : Request):
    s = await info.json()
    from datetime import datetime

    if s['Results_tab']['table_1']:
        data1 = pd.DataFrame.from_dict(s['Results_tab']['table_1'])
    else:
        data1 = pd.DataFrame()
    data1 = pd.DataFrame.from_dict(s['Results_tab']['table_1'])
    if not data1.empty:
        data1 = data1.replace('[ ' ' ]','')
        data1 = data1.astype(str)

        r = pd.DataFrame.from_dict(s['Results_tab']['Table_2'])
        r = r.astype(str)

        # Create a DataFrame for engine performance
        engine_performance_df = r[r['Title'] == "Engine Performance"]

        # Create another DataFrame for cylinder comparison
        comparison_cylinder_df = r[r['Title'] == "Comparison of Each Cylinder"]

        # Optional: Cleaning up 'remarks' column as per your previous message
        engine_performance_df['remarks'] = engine_performance_df['remarks'].replace({'nan': '', 'None': ''})
        comparison_cylinder_df['remarks'] = comparison_cylinder_df['remarks'].replace({'nan': '', 'None': ''})

        # Optionally convert all columns to string (if not already done)
        engine_performance_df = engine_performance_df.astype(str)
        comparison_cylinder_df = comparison_cylinder_df.astype(str)

        # Clean up the 'remarks' column in the original DataFrame as well
        r['remarks'] = r['remarks'].replace({'nan': '', 'None': ''})
        
        engine_performance_df = engine_performance_df.rename(columns={
        'Kind_of_Graph': 'Kind Of Graph',
        'Shop_trial': 'Shop Trial Value',
        'Measured_value': 'Measured Value',
        'Deviation': 'Deviation',
        'status': 'Status'
        })
        # Renaming columns for comparison_cylinder_df
        comparison_cylinder_df = comparison_cylinder_df.rename(columns={
            'Kind_of_Graph': 'Kind Of Graph',
            'Shop_trial': 'Measured Average',
            'Measured_value': 'Measured Value',
            'Deviation': 'Deviation',
            'status': 'Status'
        })


        # Create the specific data subsets
        data_engine_performance = engine_performance_df[[ 'Kind Of Graph', 'Shop Trial Value',  'Measured Value', 'Deviation', 'Status']]
        data_comparison_cylinder = comparison_cylinder_df[[ 'Kind Of Graph',  'Measured Average',  'Measured Value', 'Deviation', 'Status']]
    else:
        pass 
    if s['Engine_Performance_Tab']['load_diagram_chart_1']:
        data3 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_chart_1'][0]['scatter_1'])
        data4 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_chart_1'][0]['scatter_2'])
    else:
        data3 = pd.DataFrame()
        data4 = pd.DataFrame()

    if not data3.empty:
        data3.rename(columns={'x': 'Engine speed scatter', 'y': 'Engine load scatter', 'category': 'category scatter'}, inplace=True)
    else:
        pass

    if not data4.empty:
        data4.rename(columns={'x': 'Engine speed curve', 'y': 'Engine load curve'}, inplace=True)
        data4 = data4.sort_values(by=['Engine speed curve', 'Engine load curve'])
        lst_category = data4['category'].unique()
    else:
        pass    

    # plt.rcParams["font.weight"] = "bold"
    # plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(6.5, 4.5))

    # Plotting scatter points
    scatter_plot = sns.scatterplot(x="Engine speed scatter", y="Engine load scatter", data=data3, hue='category scatter', s=150)

    # Custom colors for each category
    category_colors = {
        'P.Overload': 'red',
        'P.Continuous': 'blue',
        'Prop..curve.S': 'green',
        'Prop..curve.L': 'violet',
        'Prop..curve.B.P.': 'lightgreen',
        'Max.speed': 'lightskyblue'
    }

    # Plotting curves with specific colors
    if not data4.empty:
        for i in lst_category:
            df = data4[data4['category'] == i]
            color = category_colors.get(i, 'black')  # Default to black if category not found
            plt.plot(df['Engine speed curve'], df['Engine load curve'], marker='o', markersize=5, label=f'{i} Curve', color=color)

    # Plotting additional data point (New Power & RPM)
    new_power = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_chart_1'][0]['scatter_chart'])
    if not new_power.empty:
        try:
            plt.vlines(x=new_power["x"].values[0], ymin=0, ymax=new_power["y"].values[0], color="yellow", zorder=2, lw=1.5, label='New Power & RPM')
            plt.hlines(y=new_power["y"].values[0], xmin=0, xmax=new_power["x"].values[0], color="yellow", zorder=2, lw=1.5)
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/loaddiagram.png')  # Save as image
            plt.clf()
    else:
        pass

    # Setting labels and title
    plt.xlabel('Engine Speed (RPM %)',  size=11)
    plt.ylabel('Engine Load (%)',  size=11)
    plt.title('Load Diagram', size=16, fontweight="bold")

    # Combining legend entries
    handles, labels = scatter_plot.get_legend_handles_labels()
    plt.legend(handles=handles, labels=labels, loc='upper left',fontsize='small', bbox_to_anchor=(0.02, 0.98),handlelength=2, title=None)


    # Adjusting layout
    plt.tight_layout()

    # Saving the figure
    plt.savefig('./images/loaddiagram.png')
    plt.clf()


    # data5 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_chart_2'])
    if s['Engine_Performance_Tab']['load_diagram_chart_2']:
        data5 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_chart_2'])
    else:
        data5 = pd.DataFrame()

    if not data5.empty:
        data5['date'] = pd.to_datetime(data5['date'], format='%d-%b-%Y')
        data5['formatted_date'] = data5['date'].dt.strftime('%d-%b-%Y')
        try:
            data5['date'] = data5['date'].astype("datetime64[ns]")
        except:
            data5['date'] = pd.to_datetime(data5['date'], format='%d-%b-%Y')
            data5['formatted_date'] = data5['date'].dt.strftime('%d-%b-%Y')
        data5 = data5.sort_values(by='date')
        data5['date'] = data5['date'].astype(str)

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(10, 5))
        data5['deviation'].replace({None: np.nan}, inplace=True)
        try:
            ax = sns.lineplot(x='date', y='deviation', data=data5, marker='o', markersize=10)
        except:
            ax = plt.plot(data5['date'], data5['deviation'], marker='o')
        plt.xlabel('Month', fontweight="bold", size=16)
        plt.ylabel('% Deviation', fontweight="bold", size=16)
        plt.title('Torque Rich Index', size=18, fontweight="bold")
        try:
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        except:
            pass
        try:
            ax.legend(title=None)
        except:
            pass
        plt.savefig('./images/torque_rich_index.png')
        plt.clf()
    else:
        pass

    # Handling load_diagram_table_1
    if s['Engine_Performance_Tab']['load_diagram_table_1']:
        data6_a = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['load_diagram_table_1'])
    else:
        data6_a = pd.DataFrame()

    if not data6_a.empty:
        data6 = data6_a[["dates", "historicx", "historicy", "historicz"]]
        data6.rename(columns={
            'dates': 'Date of measurement',
            'historicx': 'Engine RPM',
            'historicy': 'Engine Load',
            'historicz': 'Shaft Power'
        }, inplace=True)

        data6['Date of measurement'] = pd.to_datetime(data6['Date of measurement'], format='%d-%b-%Y')
        data6['Date of measurement'] = data6['Date of measurement'].dt.strftime('%d-%b-%Y')
        data6 = data6.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_1']:
        data7 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_1'][0]['scatter_1'])
    else:
        data7 = pd.DataFrame()
    if not data7.empty:
        data7.rename(columns = {'Engine_Speed':'Engine speed scatter'}, inplace = True)
        data7.rename(columns = {'Tc_Speed':'Corrected T/C speed scatter'}, inplace = True)
    else:
        pass

    if s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_1']:

        data8 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_1'][0]['scatter_2'])
    else:
        data8 = pd.DataFrame()
    if not data8.empty:
        data8.rename(columns = {'Engine_Speed':'Engine speed curve'}, inplace = True)
        data8.rename(columns = {'Tc_Speed':'Corrected T/C speed curve'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_1']:

        speed_vs_tc = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_1'][0]['test'])
    else:
        speed_vs_tc = pd.DataFrame()
    if not speed_vs_tc.empty:
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.scatterplot(x="Engine speed scatter", y="Corrected T/C speed scatter", data=data7,legend='auto',hue='Date',s=150)
            plt.scatter(data8['Engine speed curve'], data8['Corrected T/C speed curve'],marker = 'o',label ='Shoptrial Data',color='blue')
            plt.plot(speed_vs_tc['x'], speed_vs_tc['y'],color='blue')
            plt.xlabel('Engine Speed (rpm)',fontweight="bold",size=16)
            plt.ylabel('Corrected T/C Speed (rpm)',fontweight="bold",size=16)
            plt.title('T/C Speed Vs Engine Speed', size=18,fontweight="bold")
            ax.legend(title=None)
            plt.savefig('./images/engine_corrected_speed_daigram.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/engine_corrected_speed_daigram.png')  # Save as image
            plt.clf()
    else:
        pass
    if s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_2']:

        data9 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_chart_2'])
    else:
        data9 = pd.DataFrame()
    if not data9.empty:
        try:
            data9['date'] = data9['date'].astype("datetime64[ns]") 
        except:    
            data9['date'] = pd.to_datetime(data9['date'], format='%d-%b-%Y')
        data9 = data9.sort_values(by='date')
        data9['date'] = data9['date'].astype(str)

        speed_corrected_speed_value = r.loc[r['Kind_of_Graph'] == 'T/C Speed Vs Engine Speed']['remarks'].item()

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(10,5))
        try:
            ax = sns.lineplot(  x='date', y='deviation', data=data9,marker = 'o',markersize = 10)
            plt.xlabel('Month',fontweight="bold",size=16)
            plt.ylabel('Deviation %',fontweight="bold",size=16)
            plt.title('% deviation', size=18,fontweight="bold")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/deviation.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/deviation.png')  # Save as image
            plt.clf()

    else:
        pass
    if s['Engine_Performance_Tab']['t_c_speed_vs_E_S_table_1']:

        data10 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_table_1'])
    else:
        data10 = pd.DataFrame()
    if not data10.empty:

        data10.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data10.rename(columns = {'historicx':'Engine Speed'}, inplace = True)
        data10.rename(columns = {'historicy':'T/C Speed'}, inplace = True)
        # data10['Date of measurement'] = data10['Date of measurement'].astype('datetime64[ns]')  error akash


        data10['Date of measurement'] = pd.to_datetime(data10['Date of measurement'], format='%d-%b-%Y')
        data10 = data10.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['t_c_speed_vs_E_S_table_2']:
        data11 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['t_c_speed_vs_E_S_table_2'])
    else:
        data11 = pd.DataFrame()
    if not data11.empty:
        data11.rename(columns = {'x':'Engine Speed'}, inplace = True)
        data11.rename(columns = {'y':'T/C Speed'}, inplace = True)
        data11 = data11.dropna()
        data11 = data11.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['pscav_vs_tc_chart_1']:

        data12 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['scatter_1'])
    else:
        data12 = pd.DataFrame()
    if not data12.empty:
        data12.rename(columns = {'tc_speed':'Corrected T/C speed scatter'}, inplace = True)
        data12.rename(columns = {'Pscav':'Corrected Pscav scatter'}, inplace = True)
    else:
        pass

    if s['Engine_Performance_Tab']['pscav_vs_tc_chart_1']:

        data13 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['scatter_2'])
    else:
        data13 = pd.DataFrame()

    if not data13.empty:
        data13.rename(columns = {'tc_speed':'Corrected T/C curve'}, inplace = True)
        data13.rename(columns = {'Pscav':'Corrected Pscav curve'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['pscav_vs_tc_chart_1']:

        tc_vs_pscav = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['test'])
    else:
        tc_vs_pscav = pd.DataFrame()
    if not tc_vs_pscav.empty:
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.scatterplot(x="Corrected T/C speed scatter", y="Corrected Pscav scatter", data=data12,legend='auto',hue='Date',s=150)
            plt.scatter(data13['Corrected T/C curve'], data13['Corrected Pscav curve'],marker = 'o',label ='Shoptrial Data',color='blue')
            sns.regplot(x="Corrected T/C curve", y="Corrected Pscav curve", data=data13, scatter=False, color='blue', order=2, ci=None, line_kws={"linewidth": 1.5})

            #plt.plot(tc_vs_pscav['x'], tc_vs_pscav['y'],color='blue')

            plt.xlabel('Corrected T/C Speed (rpm)',fontweight="bold",size=16)
            plt.ylabel('Corrected Pscav (Bar)',fontweight="bold",size=16)
            plt.title('Pscav Vs T/C Speed', size=18,fontweight="bold")
            ax.legend(title=None)
            plt.savefig('./images/pscav_tc_speed_daigram.png')
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/pscav_tc_speed_daigram.png')  # Save as image
            plt.clf()
    else:
        pass
    # data12 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['scatter_1'])
    # data12.rename(columns = {'tc_speed':'Corrected T/C speed scatter'}, inplace = True)
    # data12.rename(columns = {'Pscav':'Corrected Pscav scatter'}, inplace = True)

    # data13 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['scatter_2'])
    # if not data13.empty:
    #     data13.rename(columns = {'tc_speed':'Corrected T/C curve'}, inplace = True)
    #     data13.rename(columns = {'Pscav':'Corrected Pscav curve'}, inplace = True)
    # else:
    #     pass
    # tc_vs_pscav = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_chart_1'][0]['test'])

    # plt.rcParams["font.weight"] = "bold"
    # plt.rcParams["axes.labelweight"] = "bold"
    # plt.figure(figsize=(10,5))
    # ax = sns.scatterplot(x="Corrected T/C speed scatter", y="Corrected Pscav scatter", data=data12,legend='auto',hue='Date',s=150)
    # plt.scatter(data13['Corrected T/C curve'], data13['Corrected Pscav curve'],marker = 'o',label ='Shoptrial Data',color='blue')
    # sns.regplot(x="Corrected T/C curve", y="Corrected Pscav curve", data=data13, scatter=False, color='blue', order=2, ci=None, line_kws={"linewidth": 1.5})

    # #plt.plot(tc_vs_pscav['x'], tc_vs_pscav['y'],color='blue')

    # plt.xlabel('Corrected T/C Speed (rpm)',fontweight="bold",size=16)
    # plt.ylabel('Corrected Pscav (Bar)',fontweight="bold",size=16)
    # plt.title('Pscav Vs T/C Speed', size=18,fontweight="bold")
    # ax.legend(title=None)
    # plt.savefig('pscav_tc_speed_daigram.png')
    # plt.clf()

    pscav_tc_speed_value = r.loc[r['Kind_of_Graph'] == 'Pscav Vs T/C Speed']['remarks'].item()
    if s['Engine_Performance_Tab']["pscav_vs_tc_chart_2"]:
        data14 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["pscav_vs_tc_chart_2"])
    else:
        data14 = pd.DataFrame()
    if not data14.empty:
        try:
            data14['date'] = data14['date'].astype("datetime64[ns]")
        except:     
            data14['date'] = pd.to_datetime(data14['date'], format='%d-%b-%Y')
        data14 = data14.sort_values(by='date')
        data14['date'] = data14['date'].astype(str)
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.lineplot( x='date', y='deviation', data=data14,marker = 'o',markersize = 10)
            plt.xlabel('Month',fontweight="bold",size=16)
            plt.ylabel('Deviation %',fontweight="bold",size=16)
            plt.title('% deviation', size=18,fontweight="bold")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/deviation_pscav_tc.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/deviation_pscav_tc.png')  # Save as image
            plt.clf()
    else :
        pass
    if s['Engine_Performance_Tab']['pscav_vs_tc_table_1']:
        data15 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_table_1'])
    else:
        data15 = pd.DataFrame()

    if not data15.empty:
        data15.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data15.rename(columns = {'historicx':'T/C Speed'}, inplace = True)
        data15.rename(columns = {'historicy':'Pscav (Bar)'}, inplace = True)
        # data15['Date of measurement'] = data15['Date of measurement'].astype('datetime64[ns]')
        data15['Date of measurement'] = pd.to_datetime(data15['Date of measurement'], format='%d-%b-%Y')
        data15 = data15.astype(str)
    else :
        pass
    if s['Engine_Performance_Tab']['pscav_vs_tc_table_2']:       
        data16 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_tc_table_2'])
    else:
        data16 = pd.DataFrame()
    if not data15.empty:
        data16.rename(columns = {'x':'T/C Speed'}, inplace = True)
        data16.rename(columns = {'y':'Pscav(Bar)'}, inplace = True)
        data16 = data16.dropna()
        data16 = data16.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['pscav_vs_load_chart_1']:

        data17 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_chart_1'][0]['scatter_1'])
    else:
        data17 = pd.DataFrame()
    if not data17.empty:
        data17.rename(columns = {'engine_load':'engine_load scatter'}, inplace = True)
        data17.rename(columns = {'pscav':'pscav scatter'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['pscav_vs_load_chart_1']:
        data18 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_chart_1'][0]['scatter_2'])
    else:
        data18 = pd.DataFrame()
    if not data18.empty:
        data18.rename(columns = {'engine_load':'engine_load curve'}, inplace = True)
        data18.rename(columns = {'pscav':'pscav curve'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['pscav_vs_load_chart_1']:

        pscav_vs_load = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_chart_1'][0]['test'])
    else:
        pscav_vs_load = pd.DataFrame()
    if not pscav_vs_load.empty:
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.scatterplot(x="engine_load scatter", y="pscav scatter", data=data17,legend='auto',hue='Date',s=150)
            plt.scatter(data18['engine_load curve'], data18['pscav curve'],marker = 'o',label ='Shoptrial Data',color='blue')
            plt.plot(pscav_vs_load['x'], pscav_vs_load['y'],color='blue')
            plt.xlabel('Engine Load (%)',fontweight="bold",size=16)
            plt.ylabel('Pscav (Bar)',fontweight="bold",size=16)
            plt.title('Pscav Vs Load', size=18,fontweight="bold")
            ax.legend(title=None)
            plt.savefig('./images/pscav_load_daigram.png')
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/pscav_load_daigram.png')  # Save as image
            plt.clf()
    else:
        pass
    pscav_load_value = r.loc[r['Kind_of_Graph'] == 'Pscav Vs Engine Load']['remarks'].item()
    if s['Engine_Performance_Tab']["pscav_vs_load_chart_2"]:

        data19 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["pscav_vs_load_chart_2"])
    else:
        data19 = pd.DataFrame()
    if not data19.empty:

        try:
            data19['date'] = data19['date'].astype("datetime64[ns]")
        except:    
            data19['date'] = pd.to_datetime(data19['date'], format='%d-%b-%Y')

        data19 = data19.sort_values(by='date')
        data19['date'] = data19['date'].astype(str)
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.lineplot( x='date', y='deviation', data=data19,marker = 'o',markersize = 10)
            plt.xlabel('Month',fontweight="bold",size=16)
            plt.ylabel('Deviation %',fontweight="bold",size=16)
            plt.title('% deviation', size=18,fontweight="bold")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/pscav_load.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/pscav_load.png')  # Save as image
            plt.clf()
    else:
        pass
    if s['Engine_Performance_Tab']['pscav_vs_load_table_1']:
        data20 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_table_1'])
    else:
        data20 = pd.DataFrame()
    if not data20.empty:

        data20.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data20.rename(columns = {'historicx':'Engine Load(%)'}, inplace = True)
        data20.rename(columns = {'historicy':'PScav(Bar)'}, inplace = True)
        # data20['Date of measurement'] = data20['Date of measurement'].astype('datetime64[ns]')
        data20['Date of measurement'] = pd.to_datetime(data20['Date of measurement'], format='%d-%b-%Y')


        data20 = data20.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['pscav_vs_load_table_2']:
        data21 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pscav_vs_load_table_2'])
    else:
        data21 = pd.DataFrame()
    if not data21.empty:
        data21.rename(columns = {'x':'Engine Load(%)'}, inplace = True)
        data21.rename(columns = {'y':'PScav(Bar)'}, inplace = True)
        data21 = data21.dropna()
        data21 = data21.astype(str)
    else:
        pass
    if  s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1']:
        data22 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1'][0]['scatter_1'])
    else:
        data22=pd.DataFrame()
    if not data22.empty:

        data22.rename(columns={'Pscav': 'Corrected Pscav scatter'}, inplace=True)
        data22.rename(columns={'Pcomp': 'Corrected Pcomp scatter'}, inplace=True)
    else:
        pass
    if  s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1']:

        data23 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1'][0]['scatter_2'])
    else:
        data23=pd.DataFrame()
    if not data23.empty:

        data23.rename(columns={'Pscav': 'Corrected Pscav curve'}, inplace=True)
        data23.rename(columns={'Pcomp': 'Corrected Pcomp curve'}, inplace=True)
    else:
        pass
    if s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1']:
        pscav_vs_pressdrop = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_chart_1'][0]['test'])
    else:
        pscav_vs_pressdrop=pd.DataFrame()
    if not pscav_vs_pressdrop.empty:
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10, 5))
            ax = sns.scatterplot(x="Corrected Pscav scatter", y="Corrected Pcomp scatter", data=data22, legend='auto', hue='Date', s=150)
            plt.scatter(data23['Corrected Pscav curve'], data23['Corrected Pcomp curve'], marker='o', label='Shoptrial Data', color='blue')

            sns.regplot(x="Corrected Pscav curve", y="Corrected Pcomp curve", data=data23, scatter=False, color='blue', order=2, ci=None, line_kws={"linewidth": 1.5})
            # plt.plot(pscav_vs_pressdrop['x'], pscav_vs_pressdrop['y'],color='blue')

            plt.xlabel('Corrected Pscav (Bar)', fontweight="bold", size=16)
            plt.ylabel('Corrected Pcomp (Bar)', fontweight="bold", size=16)
            plt.title('Pcomp Vs Pscav', size=18, fontweight="bold")
            ax.legend(title=None)

            plt.savefig('./images/pscav_pcomp_diagram.png')
            # plt.clf()
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/pscav_pcomp_diagram.png')  # Save as image
            plt.clf()


    else:
        pass
    pcomp_pscav_value = r.loc[r['Kind_of_Graph'] == 'Pcomp vs Pscav']['remarks'].item()
    if s['Engine_Performance_Tab']["pcomp_vs_pscav_chart_2"]:
        data24 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["pcomp_vs_pscav_chart_2"])
    else:
        data24=pd.DataFrame()

    if not data24.empty:
        try:
            data24['date'] = data24['date'].astype("datetime64[ns]")
        except:    
            data24['date'] = pd.to_datetime(data24['date'], format='%d-%b-%Y')

        data24 = data24.sort_values(by='date')
        data24['date'] = data24['date'].astype(str)
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.lineplot( x='date', y='deviation', data=data24,marker = 'o',markersize = 10)
            plt.xlabel('Month',fontweight="bold",size=16)
            plt.ylabel('Deviation %',fontweight="bold",size=16)
            plt.title('% deviation', size=18,fontweight="bold")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/pcomp_pscav.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/pcomp_pscav.png')  # Save as image
            plt.clf()
    else:
        pass
    if s['Engine_Performance_Tab']['pcomp_vs_pscav_table_1']:
        data25 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_table_1'])
    else:
        data25 = pd.DataFrame()
    if not data25.empty:

        data25.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data25.rename(columns = {'historicx':'Pscav (Bar)'}, inplace = True)
        data25.rename(columns = {'historicy':'Pcomp (Bar)'}, inplace = True)
        # data25['Date of measurement'] = data25['Date of measurement'].astype('datetime64[ns]')
        data25['Date of measurement'] = pd.to_datetime(data25['Date of measurement'], format='%d-%b-%Y')

        data25 = data25.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['pcomp_vs_pscav_table_2']:
        data26 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_pscav_table_2'])
    else:
        data26 = pd.DataFrame()
    if not data26.empty:
        data26.rename(columns = {'x':'Pscav (Bar)'}, inplace = True)
        data26.rename(columns = {'y':'Pcomp (Bar)'}, inplace = True)
        data26 = data26.dropna()
        data26 = data26.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['tex_vs_el_chart_1']:
        data27 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_chart_1'][0]['scatter_1'])
    else:
        data27 = pd.DataFrame()
    if not data27.empty:

        data27.rename(columns = {'Engine_load':'Engine Load scatter'}, inplace = True)
        data27.rename(columns = {'Texh':'Corrected Texh scatter'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['tex_vs_el_chart_1']:
        data28 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_chart_1'][0]['scatter_2'])
    else:
        data28 = pd.DataFrame()

    if not data28.empty:
        data28.rename(columns = {'Engine_load':'Engine Load curve'}, inplace = True)
        data28.rename(columns = {'Texh':'Corrected Texh curve'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['tex_vs_el_chart_1']:
        engineload_vs_correctedtexh = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_chart_1'][0]['test'])
    else:
        engineload_vs_correctedtexh = pd.DataFrame()
    try:
        if not engineload_vs_correctedtexh.empty :


            try:
                plt.rcParams["font.weight"] = "bold"
                plt.rcParams["axes.labelweight"] = "bold"
                plt.figure(figsize=(10,5))
                ax = sns.scatterplot(x="Engine Load scatter", y="Corrected Texh scatter", data=data27,legend='auto',hue='Date',s=150)
                print(data28)
                plt.scatter(data28['Engine Load curve'], data28['Corrected Texh curve'],marker = 'o',label ='Shoptrial Data',color='blue')
                plt.plot(engineload_vs_correctedtexh['x'], engineload_vs_correctedtexh['y'],color='blue')
                plt.xlabel('Engine Load (%)',fontweight="bold",size=16)
                plt.ylabel('Corrected Texh Cyl. Out. (deg.C)',fontweight="bold",size=16)
                plt.title('Texh Vs Load', size=18,fontweight="bold")
                ax.legend(title=None)
                plt.savefig('./images/engine_load_texh_daigram.png')
                plt.clf()
            except:
                plt.figure(figsize=(6, 6))
                ax = plt.gca()
                ax.axis('off')  # Turn off axis
                ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
                plt.savefig('./images/engine_load_texh_daigram.png')  # Save as image
                plt.clf()
        else:
            pass
    except:
        pass
    engine_load_texh_value = r.loc[r['Kind_of_Graph'] == 'Texh Vs Engine Load']['remarks'].item()
    if s['Engine_Performance_Tab']["tex_vs_el_chart_2"]:
        data29 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["tex_vs_el_chart_2"])
    else:
        data29 = pd.DataFrame()
    if not data29.empty:
        try:
            data29['date'] = data29['date'].astype("datetime64[ns]")
        except:    
            data29['date'] = pd.to_datetime(data29['date'], format='%d-%b-%Y')

        data29 = data29.sort_values(by='date')
        data29['date'] = data29['date'].astype(str)

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(10,5))
        try:
            ax = sns.lineplot( x='date', y='deviation', data=data29,marker = 'o',markersize = 10)
            plt.xlabel('Month',fontweight="bold",size=16)
            plt.ylabel('Deviation %',fontweight="bold",size=16)
            plt.title('% deviation', size=18,fontweight="bold")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/engine_load_corr_texh.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/engine_load_corr_texh.png')  # Save as image
            plt.clf()
    else:
        pass
    if s['Engine_Performance_Tab']['tex_vs_el_table_1']:
        data30 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_table_1'])
    else:
        data30 = pd.DataFrame()
    if not data30.empty:
        data30.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data30.rename(columns = {'historicx':'Engine Load (%)'}, inplace = True)
        data30.rename(columns = {'historicy':'Texh (deg.C)'}, inplace = True)
        # data30['Date of measurement'] = data30['Date of measurement'].astype('datetime64[ns]')
        data30['Date of measurement'] = pd.to_datetime(data30['Date of measurement'], format='%d-%b-%Y')

        data30['Engine Load (%)'] = data30['Engine Load (%)'].round(2)
        data30 = data30.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['tex_vs_el_table_2']:
        data31 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tex_vs_el_table_2'])
    else:
        data31 = pd.DataFrame()
    if not data31.empty:

        data31.rename(columns = {'x':'Engine Load (%)'}, inplace = True)
        data31.rename(columns = {'y':'Texh (deg.C)'}, inplace = True)
        data31 = data31.dropna()
        data31 = data31.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['tc_vs_EL_chart_1']:

        data32 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_chart_1'][0]['scatter_1'])
    else:
        data32 = pd.DataFrame()
    if not data32.empty:

        data32.rename(columns = {'Engine_load':'Engine Load scatter'}, inplace = True)
        data32.rename(columns = {'tc_speed':'Corrected T/C scatter'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['tc_vs_EL_chart_1']:
        data33 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_chart_1'][0]['scatter_2'])
    else:
        data33 = pd.DataFrame()
    if not data33.empty:
        data33.rename(columns = {'Engine_load':'Engine Load curve'}, inplace = True)
        data33.rename(columns = {'tc_speed':'Corrected T/C curve'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['tc_vs_EL_chart_1']:

        engineload_vs_correctedtc = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_chart_1'][0]['test'])
    else:
        engineload_vs_correctedtc = pd.DataFrame()
    if not engineload_vs_correctedtc.empty:
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.scatterplot(x="Engine Load scatter", y="Corrected T/C scatter", data=data32,legend='auto',hue='Date',s=150)
            plt.scatter(data33['Engine Load curve'], data33['Corrected T/C curve'],marker = 'o',label ='Shoptrial Data',color='blue')
            plt.plot(engineload_vs_correctedtc['x'], engineload_vs_correctedtc['y'],color='blue')
            plt.xlabel('Engine Load (%)',fontweight="bold",size=16)
            plt.ylabel('Corrected T/C Speed (rpm)',fontweight="bold",size=16)
            plt.title('Engine Load Vs T/C Speed', size=18,fontweight="bold")
            ax.legend(title=None)
            plt.savefig('./images/engine_load_tc_daigram.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/engine_load_tc_daigram.png')  # Save as image
            plt.clf()
    else:
        pass
    speed_load_value = r.loc[r['Kind_of_Graph'] == 'T/C Speed Vs Engine Load']['remarks'].item()
    if s['Engine_Performance_Tab']["tc_vs_EL_chart_2"]:
        data34 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["tc_vs_EL_chart_2"])
    else:
        data34 = pd.DataFrame()
    if not data34.empty:

        try:
            data34['date'] = data34['date'].astype("datetime64[ns]")
        except:    
            data34['date'] = pd.to_datetime(data34['date'], format='%d-%b-%Y')
        data34 = data34.sort_values(by='date')
        data34['date'] = data34['date'].astype(str)

        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.figure(figsize=(10,5))
        try:
            ax = sns.lineplot( x='date', y='deviation', data=data34,marker = 'o',markersize = 10)
            plt.xlabel('Month',fontweight="bold",size=16)
            plt.ylabel('Deviation %',fontweight="bold",size=16)
            plt.title('% deviation', size=18,fontweight="bold")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/engine_load_corr_tc.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/engine_load_corr_tc.png')  # Save as image
            plt.clf()

    else:
        pass
    if s['Engine_Performance_Tab']['tc_vs_EL_table_1']:
        data35 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_table_1'])
    else:
        data35 = pd.DataFrame()
    if not data35.empty:
        data35.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data35.rename(columns = {'historicx':'Engine Load (%)'}, inplace = True)
        data35.rename(columns = {'historicy':'T/C Speed (rpm)'}, inplace = True)
        # data35['Date of measurement'] = data35['Date of measurement'].astype('datetime64[ns]')
        data35['Date of measurement'] = pd.to_datetime(data35['Date of measurement'], format='%d-%b-%Y')

        data35['Engine Load (%)'] = data35['Engine Load (%)'].round(2)
        data35 = data35.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['tc_vs_EL_table_2']:

        data36 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['tc_vs_EL_table_2'])
    else:
        data36 = pd.DataFrame()
    if not data36.empty:

        data36.rename(columns = {'x':'Engine Load (%)'}, inplace = True)
        data36.rename(columns = {'y':'T/C Speed (rpm)'}, inplace = True)
        data36 = data36.dropna()
        data36 = data36.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['sfoc_vs_el_chart_1']:
        data37 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_chart_1'][0]['scatter_1'])
    else:
        data37 = pd.DataFrame()
    if not data37.empty:

        data37.rename(columns = {'Engine_load':'Engine Load scatter'}, inplace = True)
        data37.rename(columns = {'Sfoc':'Fuel oil consumption scatter'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['sfoc_vs_el_chart_1']:

        data38 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_chart_1'][0]['scatter_2'])
    else:
        data38 = pd.DataFrame()
    if not data38.empty:

        data38.rename(columns = {'Engine_load':'Engine Load curve'}, inplace = True)
        data38.rename(columns = {'Sfoc':'Fuel oil consumption curve'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['sfoc_vs_el_chart_1']:

        engineload_vs_fo = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_chart_1'][0]['test'])
    else:
        engineload_vs_fo = pd.DataFrame()
    if not engineload_vs_fo.empty:
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.scatterplot(x="Engine Load scatter", y="Fuel oil consumption scatter", data=data37,legend='auto',hue='Date',s=150)
            plt.scatter(data38['Engine Load curve'], data38['Fuel oil consumption curve'],marker = 'o',label ='Shoptrial Data',color='blue')
            plt.plot(engineload_vs_fo['x'], engineload_vs_fo['y'],color='blue')
            plt.xlabel('Engine Load (%)',fontweight="bold",size=16)
            plt.ylabel('Fuel Oil Consumption (g/kWhr)',fontweight="bold",size=16)
            plt.title('Fuel Oil Consumption Rate Vs Engine Load', size=18,fontweight="bold")
            ax.legend(title=None)
            plt.savefig('./images/engine_load_sfoc_daigram.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/engine_load_sfoc_daigram.png')  # Save as image
            plt.clf()
    else:
        pass
    load_sfoc_value = r.loc[r['Kind_of_Graph'] == 'SFOC Vs Engine Load']['remarks'].item()
    if s['Engine_Performance_Tab']["sfoc_vs_el_chart_2"]:
        data39 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["sfoc_vs_el_chart_2"])
    else:
        data39 = pd.DataFrame() 
    if not data39.empty:
        try:
            data39['date'] = data39['date'].astype("datetime64[ns]")
        except:    
            data39['date'] = pd.to_datetime(data39['date'], format='%d-%b-%Y')

        data39 = data39.sort_values(by='date')
        data39['date'] = data39['date'].astype(str)
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.lineplot( x='date', y='deviation', data=data39,marker = 'o',markersize = 10)
            plt.xlabel('Month',fontweight="bold",size=16)
            plt.ylabel('Deviation %',fontweight="bold",size=16)
            plt.title('% deviation', size=18,fontweight="bold")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/engine_load_sfoc.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/engine_load_sfoc.png')  # Save as image
            plt.clf()
    else:
        pass
    if s['Engine_Performance_Tab']['sfoc_vs_el_table_1']:

        data40 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_table_1'])
    else:
        data40 = pd.DataFrame()
    if not data40.empty:
        data40.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data40.rename(columns = {'historicx':'Engine Load'}, inplace = True)
        data40.rename(columns = {'historicy':'SFOC (g/kW-hr)'}, inplace = True)
        # data40['Date of measurement'] = data40['Date of measurement'].astype('datetime64[ns]')
        data40['Date of measurement'] = pd.to_datetime(data40['Date of measurement'], format='%d-%b-%Y')

        data40['Engine Load'] = data40['Engine Load'].round(2)
        data40 = data40.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['sfoc_vs_el_table_2']:

        data41 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['sfoc_vs_el_table_2'])
    else:
        data41 = pd.DataFrame()
    if not data41.empty:
        data41.rename(columns = {'x':'Engine Load'}, inplace = True)
        data41.rename(columns = {'y':'SFOC (g/kW-hr)'}, inplace = True)
        # data41 = data41.dropna()
        data41 = data41.astype(str)
    else:
        pass
    if (s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1']) == []:
        data42_to_change = 'null'
    else:
        data42_to_change = 'yes'
        data42 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1'][0]['scatter_1'])
        data42.rename(columns = {'Engine_speed':'Engine speed scatter'}, inplace = True)
        data42.rename(columns = {'Pump_mark':'corrected pump mark scatter'}, inplace = True)

        data43 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1'][0]['scatter_2'])
        data43.rename(columns = {'Engine_speed':'Engine speed curve'}, inplace = True)
        data43.rename(columns = {'Pump_mark':'corrected pump mark curve'}, inplace = True)

        enginespeed_vs_pumpmark = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_chart_1'][0]['test'])
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.scatterplot(x="Engine speed scatter", y="corrected pump mark scatter", data=data42,legend='auto',hue='Date',s=150)
            plt.scatter(data43['Engine speed curve'], data43['corrected pump mark curve'],marker = 'o',label ='Shoptrial Data',color='blue')
            plt.plot(enginespeed_vs_pumpmark['x'], enginespeed_vs_pumpmark['y'],color='blue')
            plt.xlabel('Engine Speed (rpm)',fontweight="bold",size=16)
            plt.ylabel('Corrected Pump Mark',fontweight="bold",size=16)
            plt.title('Pump Mark Vs Engine Speed', size=18,fontweight="bold")
            ax.legend(title=None)
            plt.savefig('./images/engine_speed_corrected_pumpmark_daigram.png')
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/engine_speed_corrected_pumpmark_daigram.png')  # Save as image
            plt.clf()
        engine_speed_corrected_pumpmark_value = r.loc[r['Kind_of_Graph'] == 'Pump Mark Vs Engine Speed']['remarks'].item()

        data44 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["pump_mark_vs_ES_chart_2"])
        try:    
            data44['date'] = data44['date'].astype("datetime64[ns]")
        except:    
            data44['date'] = pd.to_datetime(data44['date'], format='%d-%b-%Y')    

        data44 = data44.sort_values(by='date')
        data44['date'] = data44['date'].astype(str)
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.lineplot( x='date', y='deviation', data=data44,marker = 'o',markersize = 10)
            plt.xlabel('Month',fontweight="bold",size=16)
            plt.ylabel('Deviation %',fontweight="bold",size=16)
            plt.title('% deviation', size=18,fontweight="bold")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/engine_speed_corrected_pump_deviation.png')
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/engine_speed_corrected_pump_deviation.png')  # Save as image
            plt.clf()

        data45 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_table_1'])
        data45.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data45.rename(columns = {'historicx':'Engine Speed'}, inplace = True)
        data45.rename(columns = {'historicy':'Pump Mark'}, inplace = True)    
        # data45['Date of measurement'] = data45['Date of measurement'].astype('datetime64[ns]')
        data45['Date of measurement'] = pd.to_datetime(data45['Date of measurement'], format='%d-%b-%Y')

        data45['Engine Speed'] = data45['Engine Speed'].round(2)
        data45 = data45.astype(str)

        data46 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pump_mark_vs_ES_table_2'])
        data46.rename(columns = {'x':'Engine Speed'}, inplace = True)
        data46.rename(columns = {'y':'Pump Mark'}, inplace = True)   
        data46 = data46.dropna()
        data46 = data46.astype(str)
    if s['Engine_Performance_Tab']['pcomp_vs_load_chart_1']:
        data47 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_chart_1'][0]['scatter_1'])
    else:
        data47 = pd.DataFrame()
    if not data47.empty:
        data47.rename(columns = {'engine_load':'engine_load scatter'}, inplace = True)
        data47.rename(columns = {'pcomp':'pcomp scatter'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['pcomp_vs_load_chart_1']:
        data48 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_chart_1'][0]['scatter_2'])
    else:
        data48 = pd.DataFrame()
    if not data48.empty:

        data48.rename(columns = {'engine_load':'engine_load curve'}, inplace = True)
        data48.rename(columns = {'pcomp':'pcomp curve'}, inplace = True)
    else:
        pass
    if s['Engine_Performance_Tab']['pcomp_vs_load_chart_1']:
        load_vs_pcomp = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_chart_1'][0]['test'])
    else:
        load_vs_pcomp = pd.DataFrame()
    if not load_vs_pcomp.empty:
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.scatterplot( x="engine_load scatter", y="pcomp scatter", data=data47,legend='auto',hue='Date',s=150)
            plt.scatter(data48['engine_load curve'], data48['pcomp curve'],marker = 'o',label ='Shoptrial Data',color='blue')
            plt.plot(load_vs_pcomp['x'], load_vs_pcomp['y'],color='blue')
            plt.xlabel('Engine Load(%)',fontweight="bold",size=16)
            plt.ylabel('Pcomp(Bar)',fontweight="bold",size=16)
            plt.title('PComp Vs Load', size=18,fontweight="bold")
            ax.legend(title=None)
            plt.savefig('./images/pcomp_load_daigram.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/pcomp_load_daigram.png')  # Save as image
            plt.clf()
    else:
        pass
    if s['Engine_Performance_Tab']['pcomp_vs_load_chart_2']:
        data49 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["pcomp_vs_load_chart_2"])
    else:   
        data49 = pd.DataFrame()
    if not data49.empty:

        try:
            data49['date'] = data49['date'].astype("datetime64[ns]")
        except:    
            data49['date'] = pd.to_datetime(data49['date'], format='%d-%b-%Y')
        data49 = data49.sort_values(by='date')
        data49['date'] = data49['date'].astype(str)
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10,5))
            ax = sns.lineplot( x='date', y='deviation', data=data49,marker = 'o',markersize = 10)
            plt.xlabel('Month',fontweight="bold",size=16)
            plt.ylabel('Deviation %',fontweight="bold",size=16)
            plt.title('% deviation', size=18,fontweight="bold")
            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/pcomp_load_deviation.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/pcomp_load_deviation.png')  # Save as image
            plt.clf()
    if s['Engine_Performance_Tab']['pcomp_vs_load_table_1']:

        data50 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_table_1'])
    else:
        data50 = pd.DataFrame()
    if not data50.empty:

        data50.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data50.rename(columns = {'historicx':'Engine Load (%)'}, inplace = True)
        data50.rename(columns = {'historicy':'Pcomp (Bar)'}, inplace = True)
        # data50['Date of measurement'] = data50['Date of measurement'].astype('datetime64[ns]')
        data50['Date of measurement'] = pd.to_datetime(data50['Date of measurement'], format='%d-%b-%Y')

        data50 = data50.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['pcomp_vs_load_table_2']:
        data51 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['pcomp_vs_load_table_2'])
    else:
        data51 = pd.DataFrame()
    if not data51.empty:
        data51.rename(columns = {'x':'Engine Load (%)'}, inplace = True)
        data51.rename(columns = {'y':'Pcomp (Bar)'}, inplace = True)
        data51 = data51.dropna()
        data51 = data51.astype(str)
    else:
        pass
    if s['Engine_Performance_Tab']['scav_temp_vs_date_chart_1']:
        data64 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['scav_temp_vs_date_chart_1'][0]['scatter_1'])
    else:
        data64 = pd.DataFrame()
    if not data51.empty:

        try:
            data64['Date'] = data64['Date'].astype("datetime64[ns]")
        except:    
            data64['Date'] = pd.to_datetime(data64['Date'], format='%d-%b-%Y')
        data64 = data64.sort_values(by='Date')
        data64['Date'] = data64['Date'].astype("str")
    else:
        pass
    if s['Engine_Performance_Tab']['scav_temp_vs_date_chart_1']:
        data65 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['scav_temp_vs_date_chart_1'][0]['scatter_2'])
    else:
        data65 = pd.DataFrame()
    if not data65.empty:

        try:
            data65['date'] = data65['date'].astype("datetime64[ns]")
        except:    
            data65['date'] = pd.to_datetime(data65['date'], format='%d-%b-%Y')
        data65 = data65.sort_values(by='date')
        data65['date'] = data65['date'].astype("str")
        data65['sw_temp'] = data65['sw_temp'].astype(float)
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        try:
            fig, ax1 = plt.subplots(figsize=(10, 5))
            sns.scatterplot(data=data64, x='Date', y='scavenge_air', ax=ax1, s=110)
            ax2 = ax1.twinx()
            sns.scatterplot(data=data65, x='date', y='sw_temp', ax=ax2, s=110, hue='date')
            sns.lineplot(data=data65, x='date', y='sw_temp', ax=ax2, color='red', label='Sea Water Temp')
            sns.lineplot(data=data64, x='Date', y='scavenge_air', ax=ax2, color='blue', label='Scavenge Air Temp')
            ax1.set_ylim(0, 50)
            ax2.set_ylim(0, 50)
            ax1.set_xlabel('Date', fontweight="bold", size=16)
            ax1.set_ylabel('Scav Temp (°C)', fontweight="bold", size=16)
            ax2.set_ylabel('Seawater Temp (°C)', fontweight="bold", size=16)
            plt.title('Scav Temp Vs Date', size=18, fontweight="bold")
            ax1.legend()
            plt.savefig('./images/scav_seawatertemp_daigram.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/scav_seawatertemp_daigram.png')  # Save as image
            plt.clf()
    else:
        pass
    if s['Engine_Performance_Tab']["scav_temp_vs_date_chart_2"]:

        data66 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']["scav_temp_vs_date_chart_2"])
    else:
        data66 = pd.DataFrame()
    if not data66.empty:
        try:
            data66['tdate'] = pd.to_datetime(data66['tdate'])
        except:    
            data66['tdate'] = pd.to_datetime(data66['tdate'], format='%d-%b-%Y')

        data66 = data66.sort_values(by='tdate')
        data66['tdate'] = data66['tdate'].astype(str)
        try:
            plt.rcParams["font.weight"] = "bold"
            plt.rcParams["axes.labelweight"] = "bold"
            plt.figure(figsize=(10, 5))

            ax = sns.scatterplot(x='tdate', y='testx', data=data66, marker='o', hue='tdate', s=150)

            sns.lineplot(x='tdate', y='testx', data=data66, color='black')

            plt.xlabel('Date', fontweight="bold", size=16)
            plt.ylabel('Engine Load(%)', fontweight="bold", size=16)
            plt.title('Engine Load', size=18, fontweight="bold")

            ax.yaxis.set_major_formatter(ticker.PercentFormatter())
            ax.legend(title=None)
            plt.savefig('./images/scav_seawatertemp.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/scav_seawatertemp.png')  # Save as image
            plt.clf()
    else:
        pass
    if s['Engine_Performance_Tab']['scav_temp_vs_date_table_1']:
        data67 = pd.DataFrame.from_dict(s['Engine_Performance_Tab']['scav_temp_vs_date_table_1'])
    else:
        data67 = pd.DataFrame()
    if not data67.empty:
        data67.rename(columns = {'dates':'Date of measurement'}, inplace = True)
        data67.rename(columns = {'historicx':'Engine Load (%)'}, inplace = True)
        data67.rename(columns = {'historicy':'Scav Temp(degree C)'}, inplace = True)
        data67.rename(columns = {'historicz':'S.W Temp(degree C)'}, inplace = True)
        # data67['Date of measurement'] = data50['Date of measurement'].astype('datetime64[ns]')
        data67['Date of measurement'] = pd.to_datetime(data67['Date of measurement'], format='%d-%b-%Y')

        data67 = data67.astype(str)
    else:
        pass
    if s['Power_curve_Tab']['graph_1']:
        data52 = pd.DataFrame.from_dict(s['Power_curve_Tab']['graph_1'])
    else:
        data52 = pd.DataFrame ()  
    if s['Power_curve_Tab']['graph_2']:
        data53 = pd.DataFrame.from_dict(s['Power_curve_Tab']['graph_2'])
    else:
        data53 = pd.DataFrame()
    pcomp_1 =  list(data53["pcomp"])
    pmax_1 =  list(data53["pmax"])
   
    if s['Power_curve_Tab']['graph_2']:

        data53 = pd.DataFrame.from_dict(s['Power_curve_Tab']['graph_2'])

    else:

        data53 = pd.DataFrame()

    pcomp_1 =  list(data53["pcomp"])

    pmax_1 =  list(data53["pmax"])

    if not data53.empty:

        fig_power_curve, axes = plt.subplots(7, 1, figsize=(7, 12.5), sharey=False) #sharey is flase because diff axis interval

        sns.scatterplot(data=data53, x='engine_load', y='pump_mark', ax=axes[0], hue="date",legend=False)

        sns.lineplot(data=data52, x='engine_load1', y='pump_mark1',marker = 'o',markersize = 7, ax=axes[0])

        axes[0].set_xlabel('',fontweight="bold",size=0)

        axes[0].set_ylabel('Pump Mark',fontweight="bold",size=9)

        axes[0].grid(False)

        sns.scatterplot(data=data53, x='engine_load', y='engine_rpm', ax=axes[1], hue="date",legend=False)

        sns.lineplot(data=data52, x='engine_load1', y='engine_rpm1',marker = 'o',markersize = 7, ax=axes[1])

        axes[1].set_xlabel('',fontweight="bold",size=0)

        axes[1].set_ylabel('TC RPM',fontweight="bold",size=9)

        axes[1].grid(False)

        sns.scatterplot(data=data53, x='engine_load', y='engine_rpm', ax=axes[2], hue="date",legend=False)

        sns.lineplot(data=data52, x='engine_load1', y='engine_rpm1', ax=axes[2],marker = 'o',markersize = 7,)

        axes[2].set_xlabel('',fontweight="bold",size=0)

        axes[2].set_ylabel('Engine RPM',fontweight="bold",size=9)

        axes[2].grid(False)

        sns.scatterplot(data=data53, x='engine_load', y='pcomp', ax=axes[3], hue="date",legend=False)

        sns.lineplot(data=data52, x='engine_load1', y='pcomp1', ax=axes[3],marker = 'o',markersize =7,)

        axes[3].set_xlabel('',fontweight="bold",size=0)

        axes[3].set_ylabel('PCOMP',fontweight="bold",size=9)

        axes[3].grid(False)

        sns.scatterplot(data=data53, x='engine_load', y='pmax', ax=axes[4], hue="date",legend=False)

        sns.lineplot(data=data52, x='engine_load1', y='pmax1', ax=axes[4],marker = 'o',markersize = 7,)

        axes[4].set_xlabel('',fontweight="bold",size=0)

        axes[4].set_ylabel('PMAX',fontweight="bold",size=9)

        axes[4].grid(False)

        sns.scatterplot(data=data53, x='engine_load', y='pscav', ax=axes[5], hue="date",legend=False)

        sns.lineplot(data=data52, x='engine_load1', y='pscav1', ax=axes[5],marker = 'o',markersize = 7,)

        axes[5].set_xlabel('',fontweight="bold",size=0)

        axes[5].set_ylabel('PSCAV',fontweight="bold",size=9)

        axes[5].grid(False)

        sns.scatterplot(data=data53, x='engine_load', y='sfoc', ax=axes[6], hue="date",legend=False)

        sns.lineplot(data=data52, x='engine_load1', y='sfoc1', ax=axes[6],marker = 'o',markersize = 7,)

        axes[6].set_xlabel('Engine Load',fontweight="bold",size=12)

        axes[6].set_ylabel('SFOC',fontweight="bold",size=9)

        axes[6].grid(False)
        
        fig_power_curve.suptitle('Engine load vs Parameters', size=18, fontweight="bold")
        fig_power_curve.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig('./images/Power_curve.png')

        plt.clf()

    else:

        pass
    Pmax_Deviation_value = r.loc[r['Kind_of_Graph'] == 'Pmax Deviation']['remarks'].item()
    Pcomp_Deviation_value = r.loc[r['Kind_of_Graph'] == 'Pcomp Deviation']['remarks'].item()
    Texh_Deviation_value = r.loc[r['Kind_of_Graph'] == 'Texh Deviation']['remarks'].item()

    #1.pmax
    data54 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_chart_1'])
    if s['Cylinder_comparison_Tab']['max_pres_chart_2']:
        data55 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_chart_2'][0])
    else:
        data55 = pd.DataFrame()
    # data56 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_table_1'])
    # m1 =data56[data56['Measured'] !=0] 
    # Pmax_filtered= m1[['cylinder', 'Measured', 'average', 'deviation', 'result',]]
    # pmax_1= Pmax_filtered.astype(str)
    # Pmax_data1 = pmax_1.values.tolist()
    if not data55.empty:
        try:
            color =  ['#CC0000','#29EE29', '#0066CC',"#AC2EB5","#663300","#F1F50C"]
            plt.title('Pmax Mean',fontweight="bold",size=14)
            fig_pmax=sns.barplot(data=data55, x="x", y="y",hue="x",palette=color)
            ax1=fig_pmax
            for p in ax1.patches:
                ax1.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')
            if ax1.get_legend(): 
                ax1.get_legend().remove()
            fig_pmax.grid(False)
            fig_pmax.set_xlabel('',fontweight="bold",size=0)
            fig_pmax.set_ylabel('Bar',fontweight="bold",size=14)
            plt.savefig('./images/Pmax_mean.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('./images/Pmax_mean.png')  # Save as image
            plt.clf()
    else:
        pass
    if s['Cylinder_comparison_Tab']['max_pres_table_1']:

        data56 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['max_pres_table_1'])
    else:
        data56 = pd.DataFrame()
    if not data56.empty:
        m1 =data56[data56['Measured'] !=0] 
        Pmax_filtered= m1[['cylinder', 'Measured', 'average', 'deviation', 'result',]]
        pmax_1= Pmax_filtered.astype(str)
        Pmax_data1 = pmax_1.values.tolist()

        plt.title('Pmax Deviation',fontweight="bold",size=16)
        try:
            fig_pmax_dev=sns.barplot(data=m1, x="cylinder", y="deviation",palette=color)
            ax2=fig_pmax_dev
            fig_pmax_dev.grid(False)
            fig_pmax_dev.set_xlabel('Cylinder No',fontweight="bold",size=16)
            fig_pmax_dev.set_ylabel('Deviation from mean (bar)',fontweight="bold",size=14)
            plt.savefig('./images/Pmax_deviation.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('Pmax_deviation.png')  # Save as image
            plt.clf()
    else:
        pass
    #2.pcomp
    # data57 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_chart_1'])
    if s['Cylinder_comparison_Tab']['comp_press_chart_2']:
        data58 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_chart_2'][0])
    else:
        data58=pd.DataFrame()
    # data59 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_table_1'])
    # m2 =data59[data59['measure'] !=0] 
    # Pcomp_filtered= m2[['cylinder', 'measure', 'average', 'deviation', 'result',]]
    # pcomp_1= Pcomp_filtered.astype(str)
    # Pcomp_data1 = pcomp_1.values.tolist()
    if not data58.empty:

        plt.title('Pcomp Mean',fontweight="bold",size=16)
        fig_pcomp=sns.barplot(data=data58, x="x", y="y",hue="x",palette=color)
        ax3=fig_pcomp
        for p in ax3.patches:
            ax3.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                        textcoords='offset points')
        if ax1.get_legend():
            ax3.get_legend().remove()
        fig_pcomp.grid(False)
        fig_pcomp.set_xlabel('',fontweight="bold",size=0)
        fig_pcomp.set_ylabel('Bar',fontweight="bold",size=14)
        plt.savefig('./images/Pcomp_mean.png')
        plt.clf()
    else:
        pass
    if s['Cylinder_comparison_Tab']['comp_press_table_1']:
        data59 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['comp_press_table_1'])
    else:  
        data59 = pd.DataFrame()
    Pcomp_data1=[]
    if not data59.empty:

        m2 =data59[data59['measure'] !=0] 
        Pcomp_filtered= m2[['cylinder', 'measure', 'average', 'deviation', 'result',]]
        pcomp_1= Pcomp_filtered.astype(str)
        Pcomp_data1 = pcomp_1.values.tolist()
        plt.title('Pcomp Deviation',fontweight="bold",size=16)
        fig_pcomp_dev=sns.barplot(data=m2, x="cylinder", y="deviation",palette=color)
        ax4=fig_pcomp_dev
        fig_pcomp_dev.grid(False)
        fig_pcomp_dev.set_xlabel('Cylinder No',fontweight="bold",size=14)
        fig_pcomp_dev.set_ylabel('Deviation from mean (bar)',fontweight="bold",size=14)
        plt.savefig('./images/Pcomp_deviation.png')
        plt.clf()
    else:
        pass
    #3.Texh
    # data60 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_chart_1'])
    if s['Cylinder_comparison_Tab']['exh_temp_chart_2']:
        data61 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_chart_2'][0])

    else:
        data61 = pd.DataFrame()
    # data62 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_table_1'])
    # m3 =data62[data62['ex_temp'] !=0] 
    # Texh_filtered= m3[['cylinder', 'ex_temp', 'average', 'deviation', 'result',]]
    # texh_1= Texh_filtered.astype(str)
    # Texh_data1 = texh_1.values.tolist()
    if not data61.empty:

        plt.title('Exhaust Temperature Mean',fontweight="bold",size=16)
        fig_texh=sns.barplot(data=data61, x="x", y="y",hue="x",palette=color)
        ax5=fig_texh
        for p in ax5.patches:
            ax5.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                        textcoords='offset points')
        if ax1.get_legend():
            ax5.get_legend().remove()
        fig_texh.grid(False)
        fig_texh.set_xlabel('',fontweight="bold",size=0)
        fig_texh.set_ylabel('Bar',fontweight="bold",size=14)
        plt.savefig('./images/Texh_mean.png')
        plt.clf()
    else:
        pass
    if s['Cylinder_comparison_Tab']['exh_temp_table_1']:
        data62 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['exh_temp_table_1'])
    else:
        data62 = pd.DataFrame()
    if not data62.empty:

        m3 =data62[data62['ex_temp'] !=0] 
        Texh_filtered= m3[['cylinder', 'ex_temp', 'average', 'deviation', 'result',]]
        texh_1= Texh_filtered.astype(str)
        Texh_data1 = texh_1.values.tolist()
        plt.title('Exhaust Temperature Deviation',fontweight="bold",size=16)
        try:
            fig_texh_dev=sns.barplot(data=m3, x="cylinder", y="deviation",palette=color)
            ax6=fig_texh_dev
            fig_texh_dev.grid(False)
            fig_texh_dev.set_xlabel('Cylinder No',fontweight="bold",size=14)
            fig_texh_dev.set_ylabel('Deviation from mean (bar)',fontweight="bold",size=14)
            plt.savefig('./images/Texh_deviation.png')
            plt.clf()
        except:
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.axis('off')  # Turn off axis
            ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
            plt.savefig('Texh_deviation.png')  # Save as image
            plt.clf()
    else:
        pass
    #4.pumpmark
    if (s['Cylinder_comparison_Tab']['pump_mark_table_1'])== []:
        data63_to_change = 'null'
    else:
        data63_to_change = 'yes'
        data63 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['pump_mark_table_1'])
        data64 = pd.DataFrame.from_dict(s['Cylinder_comparison_Tab']['pump_mark_chart_1'])
        if (data63['Measured'] == 0).all():
            data63_to_change = 'null'
        else:    
            m4 =data63[data63['Measured'] !=0] 
            Pmark_filtered= m4[['cylinder', 'Measured', 'average', 'deviation', 'result',]]
            Pmark_1= Pmark_filtered.astype(str)
            Pmark_data1 = Pmark_1.values.tolist()


            if 'Pump Mark Deviation' in r['Kind_of_Graph'].values:
                Pumpmark_Deviation_value = r.loc[r['Kind_of_Graph'] == 'Pump Mark Deviation']['remarks'].item()
            else:
                Pumpmark_Deviation_value = ''

            if data63['Measured'].sum()!= 0:
                plt.title('Pump Mark Deviation',fontweight="bold",size=16)
                try:
                    fig_texh_dev=sns.barplot(data=m4, x="cylinder", y="deviation",palette=color)
                    ax7=fig_texh_dev
                    fig_texh_dev.grid(False)
                    fig_texh_dev.set_xlabel('Cylinder No',fontweight="bold",size=14)
                    fig_texh_dev.set_ylabel('Deviation from mean (bar)',fontweight="bold",size=14)
                    plt.savefig('./images/pmark_deviation.png')
                except:
                    plt.figure(figsize=(6, 6))
                    ax = plt.gca()
                    ax.axis('off')  # Turn off axis
                    ax.text(0.5, 0.5, 'No data available', fontsize=20, ha='center', va='center')
                    plt.savefig('pmark_deviation.png')  # Save as image
                    plt.clf()
            else:
                print("")



####end
                
                
                
    #************************************************* PDF CODE ***********************************************************#

    if s['Results_tab']['testdate_data']:
        imo=s['Results_tab']['testdate_data']['imo']
    else:
        imo=''

    a = str(data1['particulars'].values[0])+"-" +str(imo)
    b= data1.iloc[ data1[data1['title'] == 'Test Date'].index.item()]['particulars']
    input_date = datetime.strptime(b, "%d-%b-%Y")
    b = input_date.strftime("%d %b %Y")

    def simple_table(spacing=3):
        
        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page() 
        pdf.set_font('Arial', 'B',size= 18)

        #pdf.image(oceanix_logo_path,15,15,w=35)
        pdf.image(msc_logo_path,160,8,w=30)

        pdf.set_xy(50,15)
        pdf.cell(170, 60,  'ENGINE PERFORMANCE REPORT')
        pdf.set_line_width(1)
        pdf.line(10, 50, 199, 50)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)

        pdf.cell(10, 2, "Vessel Name :"+" "+a,ln=True)
        pdf.cell(10, 12,"Test Date :"+" "+ b,ln=True)

        pdf.line(10, 65.5, 199, 65.5)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(10,64)
        pdf.cell(180, 15, 'Engine Details',ln=True,align='C')


        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        tablefirst_head = [['Title','Particulars']]
        tablefirst = data1.values.tolist()
        pdf.set_font("Arial",'B', size=6.6)
        col_width = pdf.w /2.21
        row_height = pdf.font_size-.5
        if len(tablefirst)>0:
            for row in tablefirst_head:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial",'B', size=6.6)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.21
            row_height = pdf.font_size-.5
            for row in tablefirst:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)

        # Drawing a line and setting the font for the header
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25, 47, 133)
        pdf.set_xy(10, 128)
        pdf.cell(180, 20, 'Engine Performance', ln=True, align='C')


        # Setting the table position and spacing
        pdf.set_xy(10, 145)
        spacing = 3.5
        tablefirst_head1 = [ 'Kind Of Graph', 'Shop Trial Value',  'Measured Value', 'Deviation', 'Status']
        tablefirst1 = data_engine_performance.values.tolist()

        # Setting the font for table headers
        pdf.set_font("Arial", 'B', size=5.5)
        col_width = pdf.w / 5.5
        row_height = pdf.font_size - .4

        # Drawing the table headers
        if len(tablefirst1) > 0:
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(21, 55, 188)
            for header in tablefirst_head1:
                pdf.cell(col_width, row_height * spacing, txt=header, border=1, fill=True)
            pdf.ln(row_height * spacing)

            # Setting the font for table content
            pdf.set_font("Arial", size=5.5)
            pdf.set_text_color(0, 0, 0)
            for row in tablefirst1:
                for item in row:
                    pdf.cell(col_width, row_height * spacing, txt=item, border=1)
                pdf.ln(row_height * spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)

        # Drawing another line and setting the font for the next section header
        #pdf.add_page() 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25, 47, 133)
        #pdf.set_xy(10,20)
        pdf.set_xy(10,210)
        pdf.cell(180, 10, 'Cylinder Comparison', ln=True, align='C')
        #pdf.line(10, 78, 199, 78)


        # Setting the table position and spacing for the next section
        pdf.set_xy(10, 222)
        tablefirst_head2 = [ 'Kind Of Graph', 'Shop_trial',  'Measured Average', 'Deviation', 'Status']
        tablefirst2 = data_comparison_cylinder.values.tolist()

        # Setting the font for table headers
        pdf.set_font("Arial", 'B', size=6.2)
        col_width = pdf.w /5.5
        row_height = pdf.font_size - .4

        # Drawing the table headers
        if len(tablefirst2) > 0:
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(21, 55, 188)
            for header in tablefirst_head2:
                pdf.cell(col_width, row_height * spacing, txt=header, border=1, fill=True)
            pdf.ln(row_height * spacing)

            # Setting the font for table content
            pdf.set_font("Arial", size=6.2)
            pdf.set_text_color(0, 0, 0)
            for row in tablefirst2:
                for item in row:
                    pdf.cell(col_width, row_height * spacing, txt=item, border=1)
                pdf.ln(row_height * spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
            
        #Page Number
        pdf.set_y(274.7)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


        # tablefirst_head = [['Title','Particulars']]
        # tablefirst = data1.values.tolist()
        # pdf.set_font("Arial",'B', size=8)
        # col_width = pdf.w /2.21
        # row_height = pdf.font_size
        # for row in tablefirst_head:
        #     pdf.set_text_color(255,255,255)
        #     pdf.set_fill_color(21,55,188)
        #     for item in row:
        #         pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
        #     pdf.ln(row_height*spacing)

        # pdf.set_font("Arial",'B', size=8)
        # pdf.set_text_color(0,0,0)
        # col_width = pdf.w /2.21
        # row_height = pdf.font_size
        # for row in tablefirst:
        #     for item in row:
        #         pdf.cell(col_width, row_height*spacing,
        #                 txt=item, border=1)
        #     pdf.ln(row_height*spacing)

        # pdf.line(10, 140, 199, 140)
        # pdf.set_font('Arial', 'B', 18)
        # pdf.set_text_color(25,47,133)
        # pdf.set_xy(10,135)
        # pdf.cell(180, 24, 'Result Table',ln=True,align='C') 
        # pdf.line(10, 152, 199, 152) 

        # pdf.set_xy(10,154)
        # spacing = 3.5
        # tablefirst_head1 = [['Title','Kind Of Graph','Shop Trial Value','Measured Value','Deviation','Status']]
        # tablefirst1 = data2.values.tolist()
        # pdf.set_font("Arial",'B', size=5.8)

        # col_width = pdf.w /6.68
        # row_height = pdf.font_size
        # for row in tablefirst_head1:
        #     pdf.set_text_color(255,255,255)
        #     pdf.set_fill_color(21,55,188)
        #     for item in row:
        #         pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
        #     pdf.ln(row_height*spacing)


        # pdf.set_font("Arial", size=5.8)
        # pdf.set_text_color(0,0,0)
        # col_width = pdf.w /6.68
        # row_height = pdf.font_size
        # for row in tablefirst1:
        #     for item in row:
        #         pdf.cell(col_width, row_height*spacing,
        #                 txt=item, border=1)
        #     pdf.ln(row_height*spacing)

        # #Page Number
        # pdf.set_y(274.7)
        # pdf.set_font('Arial', 'I', 8)
        # pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")    
        #*********************************************** 2 page **********************************************************#        
        pdf.add_page()  
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Engine Performance',ln=True,align='C')   
        pdf.cell(180, 15, '1.Load Diagram',ln=True,align='C')
        pdf.image("./images/loaddiagram.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)

        if not data5.empty:
            pdf.image("./images/torque_rich_index.png",105,32,w=108,h=80) 
        else:
            pdf.cell(180, 10,"No Data Avialable" ,ln=True)

        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)

        spacing=4
        tablefirst_head2 = [['Date of measurement', 'Engine RPM', 'Engine Load %','Shaft Power(kW)']]
        tablefirst2 = data6.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /4.5
        row_height = pdf.font_size
        if len(tablefirst2)>0:
            for row in tablefirst_head2:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /4.5
            row_height = pdf.font_size
            for row in tablefirst2:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")    
        #*********************************************** 3 page **********************************************************#    
        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '2.T/C Speed Vs Engine Speed',ln=True,align='C') 
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        if speed_vs_tc.empty:
            pdf.cell(180, 10,"No Data Avialable" ,ln=True)
        else:
            pdf.image("./images/engine_corrected_speed_daigram.png",2,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        if (speed_corrected_speed_value==''):
            pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else:    
            pdf.set_xy(10,115)
            pdf.multi_cell(185, 3,"Remarks :")
            pdf.set_xy(10,118)
            pdf.multi_cell(185, 3,speed_corrected_speed_value)
        if data9.empty:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        else:
            pdf.image("./images/deviation.png",105,32,w=108,h=80) 

        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(5, 8,"Test Data" ,ln=True)


        spacing=3
        tablefirst_head3 = [['Date of measurement', 'Engine Speed', 'T/C Speed']]
        tablefirst3 = data10.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        if len(tablefirst3)>0:
            for row in tablefirst_head3:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst3:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)

        pdf.set_font("Arial",'B', size=15)
        #pdf.set_xy(10,130)
        pdf.cell(10,17,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,220)

        spacing=3
        tablefirst_head4 = [['Engine Speed', 'T/C Speed']]
        tablefirst4 = data11.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        if len(tablefirst4)>0:
            for row in tablefirst_head4:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst4:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)

        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")   
        #*********************************************** 4 page **********************************************************#     
        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '3.Pscav Vs T/C Speed',ln=True,align='C') 
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        if tc_vs_pscav.empty:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        else:
            pdf.image("./images/pscav_tc_speed_daigram.png",2,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        if (pscav_tc_speed_value==' ') | (pscav_tc_speed_value==''):
            pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else:    
            pdf.set_xy(10,115)
            pdf.multi_cell(185, 3,"Remarks :" )
            pdf.set_xy(10,118)
            pdf.multi_cell(185, 3,pscav_tc_speed_value )
        if data14.empty:
            pdf.set_xy(120,60)########################
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        else:
            pdf.image("./images/deviation_pscav_tc.png",105,32,w=108,h=80) 
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(5, 8,"Test Data" ,ln=True)


        spacing=3
        tablefirst_head5 = [['Date of measurement', 'T/C Speed', 'Pscav(Bar)']]
        tablefirst5 = data15.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size

        if len(tablefirst5)>0:


            for row in tablefirst_head5:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst5:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)

        pdf.set_font("Arial",'B', size=15)
        pdf.cell(10,17,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,220)


        spacing=3

        tablefirst_head6 = [['T/C Speed', 'Pscav(Bar)']]
        tablefirst6 = data16.values.tolist()
        if len(tablefirst6)>0:
            pdf.set_font("Arial",'B', size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst_head6:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst6:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)



        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        #*********************************************** 5 page **********************************************************#    
        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '4.Pscav Vs EngineLoad',ln=True,align='C') 
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        if pscav_vs_load.empty:
            pdf.cell(185, 10,"No Data Avialable" ,ln=True)
        else:
            pdf.image("./images/pscav_load_daigram.png",2,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        if (pscav_load_value=='') | (pscav_load_value==' '):
            pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else: 
            pdf.set_xy(10,115)
            pdf.multi_cell(185, 3,"Remarks :" )
            pdf.set_xy(10,118)
            pdf.multi_cell(185, 3,pscav_load_value )
        if data19.empty:

            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        else:
            pdf.image("./images/pscav_load.png",105,32,w=108,h=80) 
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(5, 8,"Test Data" ,ln=True)   

        spacing=3
        tablefirst_head7 = [['Date of measurement', 'Engine Load(%)', 'Pscav(Bar)']]
        tablefirst7 = data20.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        if len(tablefirst7)>0:
            for row in tablefirst_head7:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst7:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)


        pdf.set_font("Arial",'B', size=15)
        pdf.cell(10,17,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,220)

        spacing=3
        tablefirst_head8 = [['Engine Load(%)', 'Pscav(Bar)']]
        tablefirst8 = data21.values.tolist()
        if len(tablefirst8)>0:
            pdf.set_font("Arial",'B', size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst_head8:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst8:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)  
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)


        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        #*********************************************** 6 page **********************************************************#
        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '5.Pcomp Vs Pscav',ln=True,align='C') 
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        print("pcomp_pscav_value",pcomp_pscav_value)
        pdf.image("./images/pscav_pcomp_diagram.png",2,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        if (pcomp_pscav_value==' ') | (pcomp_pscav_value==''):
            pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else: 
            pdf.set_xy(10,115)
            pdf.multi_cell(185, 3,"Remarks :")
            pdf.set_xy(10,118)
            pdf.multi_cell(185, 3,pcomp_pscav_value )
        if  data24.empty:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        else:
            pdf.image("./images/pcomp_pscav.png",105,32,w=108,h=80) 
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(5, 8,"Test Data" ,ln=True) 

        spacing=3
        tablefirst_head9 = [['Date of measurement', 'Pscav (Bar)', 'Pcomp (Bar)']]
        tablefirst9 = data25.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        if len(tablefirst9)>0:
            for row in tablefirst_head9:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst9:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)

        pdf.set_font("Arial",'B', size=15)
        pdf.cell(10,17,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,220)

        spacing=3
        tablefirst_head10 = [['Pscav (Bar)', 'Pcomp (Bar)']]
        tablefirst10 = data26.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        if len(tablefirst10)>0:
            for row in tablefirst_head10:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst10:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)

        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        #*********************************************** 7 page **********************************************************#  
        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '6.Texh Vs Engine Load',ln=True,align='C') 
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        pdf.image("./images/engine_load_texh_daigram.png",2,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        if (engine_load_texh_value=='') | (engine_load_texh_value==' '):
            pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else: 
            pdf.set_xy(10,115)
            pdf.multi_cell(185, 3,"Remarks :")
            pdf.set_xy(10,118)
            pdf.multi_cell(185, 3,engine_load_texh_value )

        pdf.image("./images/engine_load_corr_texh.png",105,32,w=108,h=80) 
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(5, 8,"Test Data" ,ln=True)    
        pdf.set_xy(10,150)
        spacing=3
        tablefirst_head11 = [['Date of measurement', 'Engine Load (%)', 'Texh (deg.C)']]
        tablefirst11 = data30.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        if len(tablefirst11)>0:
            for row in tablefirst_head11:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst11:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        pdf.set_font("Arial",'B', size=15)
        pdf.cell(10,17,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,220)

        spacing=3
        tablefirst_head12 = [['Engine Load (%)', 'Texh (deg.C)']]
        tablefirst12 = data31.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        if len(tablefirst12)>0:
            for row in tablefirst_head12:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst12:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        #*********************************************** 8 page **********************************************************#  
        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '7.T/C Speed Vs Engine Load',ln=True,align='C') 
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)
        if engineload_vs_correctedtc.empty: 
            pdf.cell(180, 10,"No Data Avialable" ,ln=True)
        else:
            pdf.image("./images/engine_load_tc_daigram.png",2,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        if (speed_load_value==' ') | (speed_load_value==''):
            pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else: 
            pdf.set_xy(10,115)
            pdf.multi_cell(185, 3,"Remarks :")
            pdf.set_xy(10,118)
            pdf.multi_cell(185, 3,speed_load_value )
        if data34.empty:
            pdf.cell(180, 10,"No Data Avialable" ,ln=True)
        else:
            pdf.image("./images/engine_load_corr_tc.png",105,32,w=108,h=80) 
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(5, 8,"Test Data" ,ln=True)  

        spacing=3
        tablefirst_head13 = [['Date of measurement', 'Engine Load (%)', 'T/C Speed (rpm)']]
        tablefirst13 = data35.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        if len(tablefirst13)>0:
            for row in tablefirst_head13:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst13:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        pdf.set_font("Arial",'B', size=15)
        pdf.cell(10,15,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,220)

        spacing=3
        tablefirst_head14 = [['Engine Load (%)', 'T/C Speed (rpm)']]
        tablefirst14 = data36.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        if len(tablefirst14)>0:
            for row in tablefirst_head14:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst14:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 9 page **********************************************************#


        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '8.SFOC Vs Engine Load',ln=True,align='C') 
        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)  
        if engineload_vs_fo.empty:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        else:     
            pdf.image("./images/engine_load_sfoc_daigram.png",2,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)

        if (load_sfoc_value=='') | (load_sfoc_value==' '):
            pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else: 
            pdf.set_xy(10,115)
            pdf.multi_cell(185, 3,"Remarks :"+" "+load_sfoc_value )
        pdf.image("./images/engine_load_sfoc.png",105,32,w=108,h=80) 
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(5, 8,"Test Data" ,ln=True)  

        spacing=3
        tablefirst_head15 = [['Date of Measurment', 'Engine Load', 'SFOC (g/kW-hr)']]
        tablefirst15 = data40.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        if len(tablefirst15)>0:
            for row in tablefirst_head15:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst15:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)

        pdf.set_font("Arial",'B', size=15)
        pdf.cell(10,17,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,220)

        spacing=3
        tablefirst_head16 = [['Engine Load', 'SFOC (g/kW-hr)']]
        tablefirst16 = data41.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        if len(tablefirst16)>0:
            for row in tablefirst_head16:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst16:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)     
        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 10 page **********************************************************#  
        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '9.Pcomp Vs Engine Load',ln=True,align='C') 

        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0)      
        if load_vs_pcomp.empty:
            pdf.cell(180, 10,"No Data Avialable" ,ln=True)
        else:
            pdf.image("./images/pcomp_load_daigram.png",2,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        if data49.empty:
            pdf.cell(180, 10,"No Data Avialable" ,ln=True)
        else:
            pdf.image("./images/pcomp_load_deviation.png",105,32,w=108,h=80) 
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(5, 8,"Test Data" ,ln=True)  

        spacing=3
        tablefirst_head19 = [['Date of measurement','Engine Load (%)','PComp (Bar)']]
        tablefirst19 = data50.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /3.5
        row_height = pdf.font_size
        if len(tablefirst19)>0:
            for row in tablefirst_head19:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst19:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        pdf.set_font("Arial",'B', size=15)
        pdf.cell(10,17,"Shop Trial Data" ,ln=True)
        pdf.set_xy(10,220)

        spacing=3
        tablefirst_head20 = [['Engine Load (%)','PComp (Bar)']]
        tablefirst20 = data51.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.33
        row_height = pdf.font_size
        if len(tablefirst20)>0:
            for row in tablefirst_head20:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst20:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
                pdf.ln(row_height*spacing)
        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        #*********************************************** 11 page **********************************************************#  
        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '10.Scav Temp Vs Date',ln=True,align='C') 

        pdf.set_font("Arial",'B', size=8)
        pdf.set_text_color(0,0,0) 
        if data65.empty:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        else:     
            pdf.image("./images/scav_seawatertemp_daigram.png",1,32,w=110,h=80)
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        if data66.empty:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)
        else:
            pdf.image("./images/scav_seawatertemp.png",106,32,w=108,h=80) 
        pdf.set_font("Arial",'B', size=15)
        pdf.set_xy(10,140)
        pdf.cell(1, 8,"Test Data" ,ln=True)  

        spacing=3
        tablefirst_head_n = [['Date of measurement','Engine Load (%)', 'Scav Temp(degree C)','S.W Temp(degree C)']]
        tablefirst_n = data67.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /4.5
        row_height = pdf.font_size
        if len(tablefirst_n)>0:
            for row in tablefirst_head_n:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /4.5
            row_height = pdf.font_size
            for row in tablefirst_n:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
                pdf.ln(row_height*spacing)

        else:
            pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)



        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 12 page **********************************************************#  
        pdf.add_page()
        pdf.set_font("Arial",'B', size=18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, '11.Pump Mark Vs Engine Speed',ln=True,align='C')
        if data42_to_change == 'null':
            pdf.set_xy(10,30)
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0,0,0) 
            pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)

            pdf.set_font("Arial",'B', size=14)
            pdf.set_xy(10,50)
            pdf.cell(1, 8,"Deviation" ,ln=True)

            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0,0,0) 
            pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)

            pdf.set_font("Arial",'B', size=14)
            pdf.set_xy(10,80)
            pdf.cell(1, 8,"Test Data" ,ln=True)

            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0,0,0) 
            pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)

            pdf.set_font("Arial",'B', size=14)
            pdf.set_xy(10,110)
            pdf.cell(1, 8,"Shop Trial Data" ,ln=True)

            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0,0,0) 
            pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)
        elif(data42_to_change == 'yes'):    
            pdf.set_font("Arial",'B', size=8)
            pdf.set_text_color(0,0,0)            
            pdf.image("./images/engine_speed_corrected_pumpmark_daigram.png",2,32,w=110,h=80)
            pdf.set_font("Arial",'B', size=7)
            pdf.set_text_color(0,0,0)

            if (engine_speed_corrected_pumpmark_value=='') | (engine_speed_corrected_pumpmark_value==' '):
                pdf.cell(30, 195,"Remarks :"+" "+'Normal' ,ln=True)
            else: 
                pdf.set_xy(10,115)
                pdf.multi_cell(185, 3,"Remarks :")
                pdf.set_xy(10,118)
                pdf.multi_cell(185, 3,engine_speed_corrected_pumpmark_value )
            pdf.image("./images/engine_speed_corrected_pump_deviation.png",105,32,w=108,h=80) 
            pdf.set_font("Arial",'B', size=15)
            pdf.set_xy(10,140)
            pdf.cell(5, 8,"Test Data" ,ln=True)  

            spacing=3
            tablefirst_head17 = [['Date of measurement', 'Engine Speed', 'Pump Mark']]
            tablefirst17 = data45.values.tolist()
            pdf.set_font("Arial",'B', size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst_head17:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /3.5
            row_height = pdf.font_size
            for row in tablefirst17:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial",'B', size=15)
            pdf.cell(10,17,"Shop Trial Data" ,ln=True)
            pdf.set_xy(10,220)

            spacing=3
            tablefirst_head18 = [['Engine Speed', 'Pump Mark']]
            tablefirst18 = data46.values.tolist()
            pdf.set_font("Arial",'B', size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst_head18:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=7)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /2.33
            row_height = pdf.font_size
            for row in tablefirst18:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
                pdf.ln(row_height*spacing)




        #Page Number
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")    
        #*********************************************** 12 page **********************************************************#  
        pdf.add_page()
        pdf.set_font("Arial",'B', size=20)
        if os.path.exists("./images/Power_curve.png"):
            pdf.image("./images/Power_curve.png",10,24,w=180,h=220)
        else:
            pdf.cell(180, 10,"No Data Avialable" ,ln=True)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 10, 'Performance Curve',ln=True,align='C') 
        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % (pdf.page_no()),align="R")

    #*********************************************** 13 page **********************************************************#
        pdf.add_page()
        pdf.set_text_color(25,47,133)
        pdf.set_font("Arial",'B', size=18)
        pdf.set_xy(10,10)
        pdf.cell(180,20,txt ='Cylinder Comparison', align='C')

        pdf.set_font("Arial",'B', size=12)
        pdf.set_text_color(0,0,0)


        pdf.image("./images/Pmax_mean.png",3,50,w=110,h=80) 
        pdf.image("./images/Pmax_deviation.png",106,50,w=110,h=80) 

        pdf.set_xy(10,30)
        pdf.cell(70, 30,"1) Maximum Pressure" )
        pdf.set_font("Arial",'B', size=8)
        if (Pmax_Deviation_value==' ') | (Pmax_Deviation_value==''):
            pdf.set_xy(15,40)
            pdf.cell(10, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else:
            pdf.set_xy(15,130)
            pdf.multi_cell(185, 3,"Remarks :")
            pdf.set_xy(15,133)
            pdf.multi_cell(185, 3,Pmax_Deviation_value )

        pdf.set_xy(10,170) 
        Pmax_data= [['Cylinder Number','Measured Value (bar)','Average value','Deviation',"Result"]]
        pdf.set_font("Arial", "B",size=8)
        col_width = pdf.w /5.88
        row_height = pdf.font_size
        for row in Pmax_data:
            pdf.cell(5.2)
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*3,
                        txt=item, border=1, fill=True)
            pdf.ln(row_height*3)   

        pdf.set_text_color(0,0,0)  
        pdf.set_font("Arial", "B",size=8)
        col_width = pdf.w /5.88
        row_height = pdf.font_size-.5
        for row in Pmax_data1:
            pdf.cell(5.2)
            pdf.set_fill_color(255, 255, 255 )
            for item in row:
                pdf.cell(col_width, row_height*3,
                        txt=item, border=1, fill=True)
            pdf.ln(row_height*3)


        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 14 page **********************************************************# 
        pdf.add_page()
        pdf.set_text_color(25,47,133)
        pdf.set_font("Arial",'B', size=18)
        pdf.set_xy(10,10)

        pdf.set_font("Arial",'B', size=12)
        pdf.set_text_color(0,0,0)


        pdf.image("./images/Pcomp_mean.png",3,50,w=110,h=80) 
        pdf.image("./images/Pcomp_deviation.png",106,50,w=110,h=80) 

        pdf.set_xy(10,30)
        pdf.cell(70, 20,"2) Compressor Pressure" )
        pdf.set_font("Arial",'B', size=8)
        if (Pcomp_Deviation_value=='') | (Pcomp_Deviation_value==' '):
            pdf.set_xy(15,40)
            pdf.cell(10, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else:
            pdf.set_xy(15,130)
            pdf.multi_cell(185, 3,"Remarks :" )
            pdf.set_xy(15,133)
            pdf.multi_cell(185, 3,Pcomp_Deviation_value)

        pdf.set_xy(10,170) 
        if len(Pcomp_data1) > 0:
            Pmax_data= [['Cylinder Number','Measured Value (bar)','Average value','Deviation',"Result"]]
            pdf.set_font("Arial", "B",size=8)
            col_width = pdf.w /5.88
            row_height = pdf.font_size
            for row in Pmax_data:
                pdf.cell(5.2)
                pdf.set_text_color(253,253,253)   
                pdf.set_fill_color(1, 0, 173 )
                for item in row:
                    pdf.cell(col_width, row_height*3,
                            txt=item, border=1, fill=True)
                pdf.ln(row_height*3)

            pdf.set_text_color(4,4,5)  
            pdf.set_font("Arial", "B",size=8)
            col_width = pdf.w /5.88
            row_height = pdf.font_size-.5

            for row in Pcomp_data1:
                pdf.cell(5.2)
                pdf.set_fill_color(255, 255, 255 )
                for item in row:
                    pdf.cell(col_width, row_height*3,
                            txt=item, border=1, fill=True)
                pdf.ln(row_height*3)
        else:

                pdf.cell(10, 170, 'No Data Avialable',ln=True,align='C',border=True)

                #Page Number
                pdf.set_text_color(0,0,0)
                pdf.set_y(274.5)
                pdf.set_font('Arial', 'I', 8)
                pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")




        #*********************************************** 15 page **********************************************************# 
        pdf.add_page()
        pdf.set_text_color(25,47,133)
        pdf.set_font("Arial",'B', size=18)
        pdf.set_xy(10,10)

        pdf.set_font("Arial",'B', size=12)
        pdf.set_text_color(0,0,0)


        pdf.image("./images/Texh_mean.png",3,50,w=110,h=80) 
        pdf.image("./images/Texh_deviation.png",105,50,w=110,h=80) 

        pdf.set_xy(10,30)
        pdf.cell(70, 20,"3) M/E Cylinder Exhaust Temperature" )
        pdf.set_font("Arial",'B', size=8)
        if (Texh_Deviation_value=='') | (Texh_Deviation_value==' '):
            pdf.set_xy(15,40)
            pdf.cell(10, 195,"Remarks :"+" "+'Normal' ,ln=True)
        else:
            pdf.set_xy(15,130)
            pdf.multi_cell(185, 3,"Remarks :" )
            pdf.set_xy(15,133)
            pdf.multi_cell(185, 3,Texh_Deviation_value)

        pdf.set_xy(10,170) 
        Pmax_data= [['Cylinder Number','Measured Value (Deg)','Average value','Deviation',"Result"]]
        pdf.set_font("Arial", "B",size=8)
        col_width = pdf.w /5.88
        row_height = pdf.font_size
        if len(Texh_data1)>0:
            for row in Pmax_data:
                pdf.cell(5.2)
                pdf.set_text_color(253,253,253)   
                pdf.set_fill_color(1, 0, 173 )
                for item in row:
                    pdf.cell(col_width, row_height*3,
                            txt=item, border=1, fill=True)
                pdf.ln(row_height*3)

            pdf.set_text_color(4,4,5)  
            pdf.set_font("Arial", "B",size=8)
            col_width = pdf.w /5.88
            row_height = pdf.font_size-.5
            for row in Texh_data1:
                pdf.cell(5.2)
                pdf.set_fill_color(255, 255, 255 )
                for item in row:
                    pdf.cell(col_width, row_height*3,
                            txt=item, border=1, fill=True)
                pdf.ln(row_height*3)   
        else:
            pdf.cell(10,140,'No Data Avialable',ln=True,align='C',border=True)

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")

        #*********************************************** 16 page **********************************************************#   
        pdf.add_page()
        pdf.set_text_color(25,47,133)
        pdf.set_font("Arial",'B', size=18)
        pdf.set_xy(10,10)
        pdf.set_font("Arial",'B', size=12)
        pdf.set_text_color(0,0,0)
        pdf.set_xy(10,30)
        pdf.cell(70, 20,"4) Pumpmark" )

        if data63_to_change=='null':
            pdf.set_xy(10,50)
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0,0,0) 
            pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)

            pdf.set_font("Arial",'B', size=14)
            pdf.set_xy(10,70)
            pdf.cell(1, 8,"Deviation" ,ln=True)

            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0,0,0) 
            pdf.cell(180, 10, 'No Data Avialable',ln=True,align='C',border=True)

        elif(data63_to_change == 'yes'):    

            pdf.set_font("Arial",'B', size=8)
            pdf.image("./images/pmark_deviation.png",50,42,w=120,h=80)
            if (Pumpmark_Deviation_value=='') | (Pumpmark_Deviation_value==' '):
                pdf.set_xy(15,40)
                pdf.cell(10, 195,"Remarks :"+" "+'Normal' ,ln=True)
            else:
                pdf.set_xy(15,130)
                pdf.multi_cell(185, 3,"Remarks :" )
                pdf.set_xy(15,133)
                pdf.multi_cell(185, 3,Pumpmark_Deviation_value)

            pdf.set_xy(10,170) 
            Pmax_data= [['Cylinder Number','Measured Value (Deg)','Average value','Deviation',"Result"]]
            pdf.set_font("Arial", "B",size=8)
            col_width = pdf.w /5.88
            row_height = pdf.font_size
            if len(Pmark_data1)>0:
                for row in Pmax_data:
                    pdf.cell(5.2)
                    pdf.set_text_color(253,253,253)   
                    pdf.set_fill_color(1, 0, 173 )
                    for item in row:
                        pdf.cell(col_width, row_height*3,
                            txt=item, border=1, fill=True)
                    pdf.ln(row_height*3)

                pdf.set_text_color(4,4,5)  
                pdf.set_font("Arial", "B",size=8)
                col_width = pdf.w /5.88
                row_height = pdf.font_size-.5
                for row in Pmark_data1:
                    pdf.cell(5.2)
                    pdf.set_fill_color(255, 255, 255 )
                    for item in row:
                        pdf.cell(col_width, row_height*3,
                            txt=item, border=1, fill=True)
                    pdf.ln(row_height*3)   
            else:
                pdf.multi_cell(70, 30, 'No Data Available', align='C', border=1)

        #Page Number
        pdf.set_text_color(0,0,0)
        pdf.set_y(274.5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")


        pdf.output(pdf_name,'F')
        
    pdf_name = './documents/MSC_ME_PERFORMANCE_report' + a + '.pdf'

    simple_table()         

    return FileResponse(path = pdf_name , filename='ME.pdf') 



@router.post('/api/v1/pdf/me/sfoc')
async def index(info : Request , vessel_name:str = None,fleet:str = None , month:str = None):
    s = await info.json()

    data1 = pd.DataFrame.from_dict(s['data']['tableData_All'])
    data1 = data1.astype(str)
    data1 = data1.drop(columns=['remark_mid', 'remark_end'])
    data1 = data1.rename(columns={"imo": "IMO","fleet": "FLEET","class": "CLASS","missing_vessels": "MISSING VESSELS","engine_maker": "ENGINE MAKER","missing_date": "MISSING DATE","email_id": "EMAIL ID"})
    data1.insert(0, 'Sl.No', range(1, len(data1) + 1))
    data1 = data1.replace('None', '')
    data1 = data1.replace({None: ''})

    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Rectangle, Patch
    import os

    # Validate required parameters
    if not all([fleet, month]):
        raise ValueError("fleet and month parameters are required")

    # Extract values from JSON data and parameters
    pie_data = s['data']['piechartData']
    values = {item['type']: item['value'] for item in pie_data}

    # Assign variables for each value
    total_vessels = values['Total Vessels']
    both_missing = values['Vessels With Both reports missing']
    mid_missing = values['Vessels With ONLY Mid reports missing']
    end_missing = values['Vessels With ONLY End reports missing']
    both_available = total_vessels - (both_missing + mid_missing + end_missing)

    total_mid_missing = both_missing + mid_missing
    total_end_missing = both_missing + end_missing

    # Format month string (remove %20 and handle parsing)
    def format_month(month_str):
        return month_str.replace('%20', ' ')

    # Plot setup with adjusted spacing
    fig = plt.figure(figsize=(12, 10))
    fig.patch.set_facecolor('white')
    # gs = plt.GridSpec(3, 2, height_ratios=[1, 2, 0.5], hspace=0.4)
    gs = plt.GridSpec(3, 2, height_ratios=[0.3, 2, 0.5], hspace=0.4)  # Reduce height of the progress bar
    # Progress bar with fixed proportions
    ax_progress = plt.subplot(gs[0, :])
    values_list = [both_missing, mid_missing, end_missing, both_available]
    colors = ['#FF4444', '#FF8C42', '#FFD700', '#4CAF50']
    text_colors = ['white', 'black', 'black', 'white']  # Text colors corresponding to the categories

    left = 0
    for i, (value, color, text_color) in enumerate(zip(values_list, colors, text_colors)):
        width = value / total_vessels
        ax_progress.add_patch(Rectangle((left, 0), width, 0.5, color=color))
        ax_progress.text(left + width / 2, 0.25, str(value),ha='center', va='center', color=text_color, fontsize=10,weight='bold')
        left += width

    ax_progress.set_xlim(0, 1)
    ax_progress.set_ylim(0, 1)
    ax_progress.axis('off')

    # Title and subtitle with dynamic values
    plt.figtext(0.5, 0.95, 'ME Reports Submission Progress', ha='center', fontsize=16, color='black')
    plt.figtext(
        0.5, 0.88, 
        f'Report Submission Status for {format_month(month)}: Out of {total_vessels} vessels, {both_missing} vessels have both reports missing.',
        ha='center', fontsize=10, color='black'
    )

    # Legend with adjusted position
    legend_elements = [
        Patch(facecolor='#FF4444', label='Both missing'),
        Patch(facecolor='#FF8C42', label='Mid missing'),
        Patch(facecolor='#FFD700', label='End missing'),
        Patch(facecolor='#4CAF50', label='Both available')
    ]
    plt.figlegend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.8), ncol=4, fontsize=10)

    # Gauge 1 for Mid Missing
    ax_gauge1 = plt.subplot(gs[1, 0])
    theta = np.linspace(np.pi, 0, 100)
    r = 0.7
    ax_gauge1.plot(r * np.cos(theta), r * np.sin(theta), color='#444444', linewidth=20, alpha=0.8)
    angle_mid = np.pi * (1 - total_mid_missing / total_vessels)
    ax_gauge1.plot(r * np.cos(np.linspace(np.pi, angle_mid, 100)), r * np.sin(np.linspace(np.pi, angle_mid, 100)), color='#FF4444', linewidth=20)
    ax_gauge1.plot(r * np.cos(np.linspace(angle_mid, 0, 100)), r * np.sin(np.linspace(angle_mid, 0, 100)), color='#4CAF50', linewidth=20)
    ax_gauge1.text(0, 0.1, f"{total_mid_missing} / {total_vessels}", ha='center', fontsize=20, color='black')
    ax_gauge1.text(0, -0.1, 'Mid Report Missing', ha='center', fontsize=12, color='black')
    # Add footer text closer to the gauge
    ax_gauge1.text(0, -0.6, f'{total_mid_missing} Mid Reports are missing', 
                ha='center', fontsize=10, color='black', wrap=True)
    ax_gauge1.set_xlim(-1, 1)
    ax_gauge1.set_ylim(-1, 1)
    ax_gauge1.axis('off')

    # Gauge 2 for End Missing
    ax_gauge2 = plt.subplot(gs[1, 1])
    ax_gauge2.plot(r * np.cos(theta), r * np.sin(theta), color='#444444', linewidth=20, alpha=0.6)
    angle_end = np.pi * (1 - total_end_missing / total_vessels)
    ax_gauge2.plot(r * np.cos(np.linspace(np.pi, angle_end, 100)), r * np.sin(np.linspace(np.pi, angle_end, 100)), color='#FF4444', linewidth=20)
    ax_gauge2.plot(r * np.cos(np.linspace(angle_end, 0, 100)), r * np.sin(np.linspace(angle_end, 0, 100)), color='#4CAF50', linewidth=20)
    ax_gauge2.text(0, 0.1, f"{total_end_missing} / {total_vessels}", ha='center', fontsize=20, color='black')
    ax_gauge2.text(0, -0.1, 'End Report Missing', ha='center', fontsize=12, color='black')
    # Add footer text closer to the gauge
    ax_gauge2.text(0.01, -0.6, f'{total_end_missing} End Reports are missing', 
                ha='center', fontsize=10, color='black', wrap=True)
    ax_gauge2.set_xlim(-1, 1)
    ax_gauge2.set_ylim(-1, 1)
    ax_gauge2.axis('off')

    # Gauge legend with adjusted position
    legend_elements_gauge = [
        Patch(facecolor='#4CAF50', label='Available reports'),
        Patch(facecolor='#FF4444', label='Missing reports')
    ]
    plt.figlegend(handles=legend_elements_gauge, loc='center', bbox_to_anchor=(0.5, 0.30), ncol=2, fontsize=10)

    plt.tight_layout()

    # Save the figure
    plt.savefig("./images/me_missing_vessels.png", bbox_inches='tight', dpi=300)

    from fpdf import FPDF

    from fpdf import FPDF
    
    pdf = FPDF()
    
    #*********************************************** 1st page with figure **********************************************************#
    pdf.add_page()
    pdf.set_font('Arial', 'B', 18)
    pdf.image(msc_logo_path,160,8,w=30)
    
    # Title with navy blue color
    pdf.set_font('Arial', 'B', 16)
    pdf.set_xy(62, 15)
    pdf.set_text_color(25, 47, 133)  # Navy blue color
    pdf.cell(165, 60, 'ME Missing Vessels Report')
    
    # Reset text color and add top line
    pdf.set_text_color(0, 0, 0)
    pdf.set_line_width(1)
    pdf.line(10, 50, 199, 50)
    
    # Reset line width for subsequent lines
    pdf.set_line_width(0.2)
    
    pdf.set_font('Arial', '', 13)
    pdf.set_xy(10, 55)
    pdf.cell(10, 2, f"Fleet: {fleet}   (Total Vessels: {total_vessels})", ln=True)
    pdf.cell(10, 12, f"Month: {format_month(month)}", ln=True)
    
    # Add bottom line
    pdf.line(10, 70, 199, 70)
    
    # Add figure on first page, centered
    image_width = 180
    image_height = 140
    pdf_width = pdf.w  # Get the PDF width
    
    # Calculate the x-coordinate to center the image
    x_center = (pdf_width - image_width) / 2
    
    # Add the image centered
    pdf.image("./images/me_missing_vessels.png", x=x_center, y=80, w=image_width, h=image_height)
    
    #*********************************************** 2nd page with table **********************************************************#
    pdf.add_page()
    
    # Title with navy blue color
    pdf.set_font('Arial', 'B', 16)
    pdf.set_xy(62, 15)
    pdf.set_text_color(25, 47, 133)  # Navy blue color
    pdf.cell(165, 20, 'ME Missing Vessels Table')
    
    # Add 20-line space before the table
    pdf.ln(25)  # Line break of 20 units (you can adjust this spacing)
    
    # Center the table on the page by adjusting the left margin
    col_widths = [10, 20, 15, 25, 25, 40, 18, 30]  # Custom column widths (adjust if necessary)
    pdf.set_x( (210 - sum(col_widths)) / 2 )  # Adjust table's left margin to center it
    
    # Add table headers
    pdf.set_font("Arial", 'B', size=6)
    
    # Column names based on your data
    headers = ["Sl.No", "IMO", "FLEET", "CLASS", "MISSING VESSELS", "ENGINE MAKER", "MISSING DATE", "EMAIL ID"]
    
    # Add headers with specific widths
    row_height = pdf.font_size
    spacing = 4  # Adjust row spacing as needed
    for header in headers:
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        pdf.cell(col_widths[headers.index(header)], row_height * spacing, txt=header, border=1, fill=True)
    pdf.ln(row_height * spacing)
    
    # Add table data with specific widths
    pdf.set_font("Arial", size=6)
    pdf.set_text_color(0, 0, 0)
    
    # Create table data (convert to string values for PDF)
    table_data = data1.values.tolist()
    
    # Add each row of data
    for row in table_data:
        pdf.set_x( (210 - sum(col_widths)) / 2 )  # Keep the table centered for each row
        for i, item in enumerate(row):
            pdf.cell(col_widths[i], row_height * spacing, txt=str(item), border=1)
        pdf.ln(row_height * spacing)
    
    # Save the PDF file
    pdf_name = './documents/MSC_SFOC_SCOC_Missing_vessel_report' + vessel_name + '.pdf'
    pdf.output(pdf_name, 'F')

        

    return FileResponse(path = pdf_name , filename='ME_SFOC.pdf')
    
@router.post('/api/v1/pdf/me/monthlyreport')
async def index(info : Request , vessel_name:str = None,fleet:str = None , month:str = None,selection:str = None):
    s = await info.json()


    print(s)
    if selection=='single':
        

        data1 = pd.DataFrame.from_dict(s['data'])
        data1 = data1.astype(str)
        
        first_10_columns = data1.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11]]
        middle_10_columns = data1.iloc[:,[0,1,11,12,13,14,15,16,17,18,19,20]]
        last_8_columns = data1.iloc[:,[0,1,11,21,22,23,24,25,26]]
        last_2_columns = data1.iloc[:,[0,1,11,27,28]]
        
        from fpdf import FPDF
        def simple_table(spacing=3):

            pdf = FPDF()
            #*********************************************** 1 page **********************************************************#
            pdf.add_page(orientation = 'L')
            pdf.set_font('Arial', 'B', 18)

            
            pdf.image(msc_logo_path,250,8,w=30)

        #Cell postion from left side
            pdf.set_xy(90,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(165, 60, 'SFOC & SCOC - Monthly Report')
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 285, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",13)
            pdf.set_xy(10,55)

            pdf.cell(10, 2, "Vessel :"+" "+vessel_name,ln=True)
            pdf.cell(10, 12,"Month :"+" "+ month,ln=True)
            pdf.line(10, 70, 285, 70)


            pdf.set_xy(10,75)
            spacing=3
            tablefirst_head1 = [first_10_columns.columns.tolist()]
            tablefirst1 = first_10_columns.values.tolist()
            pdf.set_font("Arial",'B', size=6)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst_head1:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=6)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            pdf.set_xy(10,110)
            spacing=3
            tablefirst_head2 = [middle_10_columns.columns.tolist()]
            tablefirst2 = middle_10_columns.values.tolist()
            pdf.set_font("Arial",'B', size=6)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst_head2:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=6)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst2:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            pdf.set_xy(10,145)    
            spacing=3
            tablefirst_head3 = [last_8_columns.columns.tolist()]
            tablefirst3 = last_8_columns.values.tolist()
            pdf.set_font("Arial",'B', size=6)
            col_width = pdf.w /9.75
            row_height = pdf.font_size
            for row in tablefirst_head3:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=6)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /9.75
            row_height = pdf.font_size
            for row in tablefirst3:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            pdf.set_xy(10,175)    
            spacing=3
            tablefirst_head4 = [last_2_columns.columns.tolist()]
            tablefirst4 = last_2_columns.values.tolist()
            pdf.set_font("Arial",'B', size=4)
            col_width = pdf.w /5.4
            row_height = pdf.font_size
            for row in tablefirst_head4:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=4)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /5.4
            row_height = pdf.font_size
            for row in tablefirst4:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)    



            pdf.output(pdf_name,'F')
        pdf_name = './documents/MSC_SFOC_SCOC_month_report_vessel' + vessel_name + '.pdf'
        
        simple_table()    
            
    elif selection=='fleet': 
   

        data1 = pd.DataFrame.from_dict(s['data'])
        data1 = data1.astype(str)
        
        first_10_columns = data1.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11]]
        middle_10_columns = data1.iloc[:,[0,1,11,12,13,14,15,16,17,18,19,20]]
        last_8_columns = data1.iloc[:,[0,1,11,21,22,23,24,25,26]]
        last_2_columns = data1.iloc[:,[0,1,11,27,28]]
        
        from fpdf import FPDF
        def simple_table(spacing=3):

            pdf = FPDF()
            #*********************************************** 1 page **********************************************************#
            pdf.add_page(orientation = 'L')
            pdf.set_font('Arial', 'B', 18)

            
            pdf.image(msc_logo_path,250,8,w=30)

        #Cell postion from left side
            pdf.set_xy(90,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(165, 60, 'SFOC & SCOC - Monthly Report')
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 285, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",13)
            pdf.set_xy(10,55)

            pdf.cell(10, 2, "Fleet :"+" "+fleet,ln=True)
            pdf.cell(10, 12,"Month :"+" "+ month,ln=True)
            pdf.line(10, 70, 285, 70)


            pdf.set_xy(10,72)
            spacing=2
            tablefirst_head1 = [first_10_columns.columns.tolist()]
            tablefirst1 = first_10_columns.values.tolist()
            pdf.set_font("Arial",'B', size=5)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst_head1:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=3.5)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            #pdf.set_xy(10,110)
            spacing=2
            tablefirst_head2 = [middle_10_columns.columns.tolist()]
            tablefirst2 = middle_10_columns.values.tolist()
            pdf.set_font("Arial",'B', size=5)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst_head2:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=3.5)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst2:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            #pdf.set_xy(10,145)    
            spacing=2
            tablefirst_head3 = [last_8_columns.columns.tolist()]
            tablefirst3 = last_8_columns.values.tolist()
            pdf.set_font("Arial",'B', size=5)
            col_width = pdf.w /9.75
            row_height = pdf.font_size
            for row in tablefirst_head3:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=3.5)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /9.75
            row_height = pdf.font_size
            for row in tablefirst3:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            #pdf.set_xy(10,175)    
            spacing=2
            tablefirst_head4 = [last_2_columns.columns.tolist()]
            tablefirst4 = last_2_columns.values.tolist()
            pdf.set_font("Arial",'B', size=3)
            col_width = pdf.w /5.4
            row_height = pdf.font_size
            for row in tablefirst_head4:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=3)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /5.4
            row_height = pdf.font_size
            for row in tablefirst4:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing) 

            pdf.output(pdf_name,'F')
        pdf_name = './documents/MSC_SFOC_SCOC_month_report_fleet' + vessel_name + '.pdf'

        simple_table()     
            
            
            
    elif selection=='multi':

        data1 = pd.DataFrame.from_dict(s['data'])
        data1 = data1.astype(str)
        
        list_vsl = data1['name'].unique().tolist()
        
        a = ''
        for i in list_vsl:
            a = a+i+","+" "
            
        b = a.rstrip(" ")
        vessels = b.rstrip(",") 
        
        first_10_columns = data1.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11]]
        middle_10_columns = data1.iloc[:,[0,1,11,12,13,14,15,16,17,18,19,20]]
        last_8_columns = data1.iloc[:,[0,1,11,21,22,23,24,25,26]]
        last_2_columns = data1.iloc[:,[0,1,11,27,28]]
        
        from fpdf import FPDF
        def simple_table(spacing=3):

            pdf = FPDF()
            #*********************************************** 1 page **********************************************************#
            pdf.add_page(orientation = 'L')
            pdf.set_font('Arial', 'B', 18)

            
            pdf.image(msc_logo_path,250,8,w=30)

        #Cell postion from left side
            pdf.set_xy(90,15)
            pdf.set_text_color(25,47,133)
            pdf.cell(165, 60, 'SFOC & SCOC - Monthly Report')
            pdf.set_text_color(0,0,0)
            pdf.set_line_width(1)
            pdf.line(10, 50, 285, 50)
            pdf.set_line_width(0.2)
            pdf.set_font('Arial', "",10)
            pdf.set_xy(10,55)

            pdf.cell(10, 2, "Vessels :"+" "+vessels,ln=True)
            pdf.cell(10, 12,"Month :"+" "+ month,ln=True)
            pdf.line(10, 70, 285, 70)


            pdf.set_xy(10,72)
            spacing=2
            tablefirst_head1 = [first_10_columns.columns.tolist()]
            tablefirst1 = first_10_columns.values.tolist()
            pdf.set_font("Arial",'B', size=5)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst_head1:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=3.5)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            #pdf.set_xy(10,110)
            spacing=2
            tablefirst_head2 = [middle_10_columns.columns.tolist()]
            tablefirst2 = middle_10_columns.values.tolist()
            pdf.set_font("Arial",'B', size=5)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst_head2:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=3.5)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /13
            row_height = pdf.font_size
            for row in tablefirst2:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            #pdf.set_xy(10,145)    
            spacing=2
            tablefirst_head3 = [last_8_columns.columns.tolist()]
            tablefirst3 = last_8_columns.values.tolist()
            pdf.set_font("Arial",'B', size=5)
            col_width = pdf.w /9.75
            row_height = pdf.font_size
            for row in tablefirst_head3:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=3.5)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /9.75
            row_height = pdf.font_size
            for row in tablefirst3:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing)

            #pdf.set_xy(10,175)    
            spacing=2
            tablefirst_head4 = [last_2_columns.columns.tolist()]
            tablefirst4 = last_2_columns.values.tolist()
            pdf.set_font("Arial",'B', size=3)
            col_width = pdf.w /5.4
            row_height = pdf.font_size
            for row in tablefirst_head4:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial", size=3)
            pdf.set_text_color(0,0,0)
            col_width = pdf.w /5.4
            row_height = pdf.font_size
            for row in tablefirst4:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                                txt=item, border=1)
                pdf.ln(row_height*spacing) 


            pdf.output(pdf_name,'F')
        pdf_name = './documents/MSC_SFOC_SCOC_month_report_Multi' + vessel_name + '.pdf'

        simple_table()     

        

        

    return FileResponse(path = pdf_name , filename='ME_MONTHLY_REPORT.pdf')


@router.post('/api/v1/pdf/intervention')
async def index(info : Request,monitoring_period:int = None):

    s = await info.json()
    s1 = s['data1']
    s2 = s['data2']
    Table1 = pd.DataFrame.from_dict([s1]).astype(str)
    VSL_Name = Table1['vessel'].values[0]
    Intervention = Table1['intervention'].values[0]
    Intervention_Date = Table1['date'].values[0]
    monitoring_period= s["monitoring_period"]
    str_mp= str(monitoring_period)
    draft =  Table1['draft'].values[0]
    seastate =  Table1['seastate'].values[0]
    Power_gain_int = s2['power']
    Power_gain = str(round(s2['power'],2))
    Fo_gain = str(round(s2['fo'],2))
    Fo_gain_int = s2['fo']

    #Data 1
    data1 = pd.DataFrame.from_dict(s2['fo_chart'])
    data1=data1.rename({'before':'pre_fo','after':'post_fo','index':'speed'},axis=1)
    #Chart 1
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(x="speed", y='pre_fo', data=data1,marker = 'o',markersize = 7,label = 'Pre Analysis',color='blue')
    sns.lineplot(x="speed", y='post_fo', data=data1,marker = 'o',markersize = 7,label = "Post Analysis",color='green')
    plt.xlabel('Speed (knots)',fontweight="bold",size=12)
    plt.ylabel('FO/24HR (Tonne)',fontweight="bold",size=12)
    plt.title('Speed FO Curve', size=15,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/speed_fo_intervention.png')

    #Data 2
    data2 = pd.DataFrame.from_dict(s2['power_chart'])
    data2= data2.rename({'before':'pre_power','after':'post_power','index':'speed'},axis=1)
    #Chart 1

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    plt.figure(figsize=(10,5))
    ax = sns.lineplot(x="speed", y='pre_power', data=data2,marker = 'o',markersize = 7,label = 'Pre Analysis',color='blue')
    sns.lineplot(x="speed", y='post_power', data=data2,marker = 'o',markersize = 7,label = "Post Analysis",color='green')
    plt.xlabel('Speed (knots)',fontweight="bold",size=12)
    plt.ylabel('Power (kW)',fontweight="bold",size=12)
    plt.title('Speed Power Curve', size=15,fontweight="bold")
    ax.legend(title=None)
    plt.savefig('./images/speed_power_intervention.png')


    from fpdf import FPDF
    def simple_table(spacing=3):

        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        
        pdf.image(msc_logo_path,160,8,w=30)

        #Cell postion from left side
        pdf.set_xy(67,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(175, 60, 'INTERVENTION REPORT')
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 199, 50)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)

        pdf.cell(10, 2, "Vessel Name :"+" "+VSL_Name,ln=True)
        pdf.cell(10, 12,"Intervention :"+" "+ Intervention,ln=True)
        pdf.cell(10, 2, "Intervention Date :"+" "+Intervention_Date,ln=True)
        pdf.cell(10, 10, "Monitoring Period :"+" "+str_mp,ln=True)


        pdf.line(10, 80, 199, 80)
        pdf.cell(10, 16, "Draft ="+" "+str(draft)+' meters')
        pdf.set_xy(60,29)
        pdf.cell(10, 120, "Seastate ="+" "+str(seastate),ln=True)
        pdf.set_text_color(25,47,133)
        pdf.set_font('Arial', 'B', 18)
        
        pdf.set_xy(60,80)
        pdf.set_text_color(25,47,133)
        pdf.cell(95, 47, 'FO Comparison',ln=True,align='C')
        pdf.set_xy(10,30)
        pdf.image("./images/speed_fo_intervention.png",10,110,w=190,h=120) 
        pdf.set_xy(20,240)
        pdf.set_text_color(0,0,0)
        pdf.set_font('Arial', "",12.5)
        # pdf.cell(10, 15, "Gain in FO :"+" "+Fo_gain+'%',ln=True)
        if Fo_gain_int >= 0:
            pdf.set_fill_color(0, 255,0 )
            pdf.cell(50, 10, "Gain in FO :"+" "+Fo_gain+'%', border=1, fill=True)
        else:
            pdf.set_fill_color(255, 0,0 )
            pdf.cell(50, 10, "Loss in FO :"+" "+Fo_gain+'%', border=1, fill=True)

        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 

        #*********************************************** 2 page **********************************************************#


        pdf.add_page()

        pdf.set_text_color(25,47,133)
        pdf.set_font('Arial', 'B', 18)
        

        pdf.cell(195, 20, 'Power Comparison',ln=True,align='C')
        #pdf.line(10, 85, 199, 85)
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        pdf.image("./images/speed_power_intervention.png",10,30,w=190,h=120)
        pdf.set_font('Arial', "",12.5)

        pdf.set_xy(20,160)
        # pdf.cell(10, 15, "Gain in Power :"+" "+Power_gain+'%',ln=True)
        if Power_gain_int >= 0:
            pdf.set_fill_color(0, 255,0 )
            pdf.cell(50, 10, "Gain in Power :"+" "+Power_gain+'%', border=1, fill=True)
        else:
            pdf.set_fill_color(255, 0,0 )
            pdf.cell(50, 10, "Loss in Power :"+" "+Power_gain+'%', border=1, fill=True)


        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        
 
        pdf.output(pdf_name,'F')
    pdf_name = './documents/MSC_Intervention_Report' + VSL_Name + '.pdf'
    simple_table()     

    return FileResponse(path = pdf_name , filename='ME_MONTHLY_REPORT.pdf')
  

@router.post('/api/v1/pdf/performanceresult/curve')
async def index(info : Request , vessel_name:str = None , date:str = None , sea_state:str = None):

    per_result = await info.json()
    

    fo_table = pd.DataFrame.from_dict(per_result['performance_result']["tab1"]["table1"])
    cols = ['Speed/Draft'] + [col for col in fo_table.columns if col != 'Speed/Draft']
    fo_table = fo_table[cols]
    fo_table



    po_table = pd.DataFrame.from_dict(per_result['performance_result']["tab1"]["table2"])
    cols = ['Speed/Draft'] + [col for col in po_table.columns if col != 'Speed/Draft']
    po_table = po_table[cols]
    po_table


    fo_Chart = pd.DataFrame.from_dict(per_result['performance_result']["tab1"]["chart1"])



    po_Chart = pd.DataFrame.from_dict(per_result['performance_result']["tab1"]["chart2"])



    fo_color = (fo_table.shape[1])-1
    power_color=(po_table.shape[1])-1


    # color_lst = ['blue','yellow','red','violet','green','cyan','pink','gray','orange','purple','indigo','magenta']
    color_lst = ['brown', 'darkviolet', 'red', 'green', 'orange', 'blue', 'yellow', 'cyan', 'pink', 'gray', 'olive', 'purple', 'indigo', 'magenta', 'beige', 'black', 'teal', 'maroon', 'navy', 'turquoise', 'salmon', 'gold', 'silver', 'coral', 'violet', 'lime', 'orchid', 'plum', 'khaki']

    new_color_lst1 = []
    new_color_lst2 = []

    for z in range (0,fo_color):
        color_sel = color_lst[z]
        new_color_lst1.append(color_sel)
    new_color_lst1 


    for z in range (0,power_color):
        color_sel = color_lst[z]
        new_color_lst2.append(color_sel)
    new_color_lst2

    ####################
    fo_column_head = list(fo_table.columns.values)
    fo_object =fo_table.astype(str)
    power_column_head = list(po_table.columns.values)
    power_object =po_table.astype(str)




    #_______________________Graph________________________________

    #--------------- Graph 1-----------------#
    fig_1, axes = plt.subplots(1, 1, figsize=(10, 6))  # Increase figure size
    sns.lineplot(data=fo_Chart, x='speed', y='fo_consumption', marker='o', markersize=5, lw=1, hue='category', palette=new_color_lst1)
    axes.set_xlabel('Speed (knots)', fontweight="bold", size=10)
    axes.set_ylabel('FO/24 Hrs (tonne)', fontweight="bold", size=10)
    axes.legend_.set_title(None)
    axes.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Place legend outside

    fig_1.tight_layout()


    fig_1.savefig('./images/fo_pr.png')
    plt.clf()




    # #--------------- Graph 2 -----------------#

    fig_2, axes = plt.subplots(1, 1, figsize=(10, 6))  # Increase figure size
    sns.lineplot(data=po_Chart, x='speed', y='fo_consumption', marker='o', markersize=5, lw=1, hue='category', palette=new_color_lst2)
    axes.set_xlabel('Speed (knots)', fontweight="bold", size=10)
    axes.set_ylabel('Power (KW)', fontweight="bold", size=10)
    axes.legend_.set_title(None)
    axes.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Place legend outside

    fig_2.tight_layout()

    fig_2.savefig('./images/po_pr.png')

    plt.clf()








    def performance_result_pdf(spacing=3):
        print("------------------------------------")

        #report_prepared_date= "11-10-2022"

        pdf = FPDF()
        #***********************************************  page 1 **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)

        #pdf.image(oceanix_logo_path,15,15,w=35)
        pdf.image(msc_logo_path,160,12,w=25)
        pdf.set_xy(65,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(170, 60, 'PERFORMANCE RESULTS',ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)#(x_start, y_start, x_end, y_end)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)
        #pdf.multi_cell(80,14.5,"Report Date :"+" "+ report_prepared_date, align='R')

        
        pdf.cell(10, 2, "Vessel Name :"+" "+vessel_name,ln=True)
        pdf.cell(10, 12,"Date :"+" "+ date,ln=True)
        
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        pdf.set_font('Arial', "",14)
        pdf.cell(15, 25,"Sea State :"+" "+ sea_state,ln=True)

        pdf.line(10, 70, 190, 70)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'FO Calculator Table',ln=True,align='C')

        
        spacing = 3
        fo_head = [fo_column_head]
        fo_values = fo_object.values.tolist()
        pdf.set_font("Arial", 'B', size=7)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(21, 55, 188)
        
        # Calculate the size of each column name
        col_widths = [pdf.get_string_width(str(item)) + 12 for item in fo_head[0]]
        
        row_height = pdf.font_size
        
        # Draw header with dynamic column width
        for item, width in zip(fo_head[0], col_widths):
            pdf.set_text_color(255, 255, 255)
            pdf.cell(width, row_height * spacing, txt=item, border=1, fill=True)
        pdf.ln(row_height * spacing)
        
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0, 0, 0)
        
        # Draw data with dynamic column width
        for row in fo_values:
            for item, width in zip(row, col_widths):
                pdf.cell(width, row_height * spacing, txt=item, border=1)
            pdf.ln(row_height * spacing)
        
        
    
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 

        #***********************************************  page 2 **********************************************************#
 
        pdf.add_page()
        #pdf.set_xy(10,50)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'FO Calculator Chart',ln=True,align='C')
        pdf.image("./images/fo_pr.png",15,25,w=170,h=100) 
        pdf.set_xy(10,135)
        pdf.cell(180, 10, 'Power Calculator Chart',ln=True,align='C')
        pdf.image("./images/po_pr.png",15,145,w=170,h=105) 
        
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")  
        #***********************************************  page 3 **********************************************************#
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 18, 'Power Calculator Table',ln=True,align='C')
        
        
        pdf.set_line_width(0)
        pdf.set_text_color(0,0,0)
        spacing = 3
        power_head = [power_column_head]
        power_values = power_object.values.tolist()
        pdf.set_font("Arial", 'B', size=7)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(21, 55, 188)
        
        # Calculate the size of each column name
        col_widths = [pdf.get_string_width(str(item)) + 12 for item in power_head[0]]
        
        row_height = pdf.font_size
        
        # Draw header with dynamic column width
        for item, width in zip(power_head[0], col_widths):
            pdf.set_text_color(255, 255, 255)
            pdf.cell(width, row_height * spacing, txt=item, border=1, fill=True)
        pdf.ln(row_height * spacing)
        
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0, 0, 0)
        
        # Draw data with dynamic column width
        for row in power_values:
            for item, width in zip(row, col_widths):
                pdf.cell(width, row_height * spacing, txt=item, border=1)
            pdf.ln(row_height * spacing)

        
        
    
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")  
        print("Downloading")
        print(pdf_name)
        pdf.output(pdf_name,'F')
        print("Downloaded")
    
    
    pdf_name = './documents/'+vessel_name+'_'+date+'_'+sea_state+'_'+'Performance_Result_Curve.pdf'
    performance_result_pdf()

    return FileResponse(path =  pdf_name,filename="Curve.pdf")
    
    


@router.post('/api/v1/pdf/period_comparison')
async def index( info : Request , first_Period : str = None, second_Period : str = None ,report_type: str = None  ,vessel_name: str = None ,fleet: str = None ,class_name : str = None, moving_average : str = None,first_period_min:str = None , first_period_max:str = None,second_period_min:str = None,second_period_max:str = None):
    if first_Period == 'null' or first_Period == 'None':
        first_Period = None
        
    if second_Period == 'null' or second_Period == 'None':
        second_Period = None
        
    if first_period_min == 'null' or first_period_min == 'None':
        first_period_min = None
        
    if first_period_max == 'null' or first_period_max == 'None':
        first_period_max = None
    s = await info.json()

    #VESSEL DETAILS
    # vsl_url='https://msc.oceanix.cloud/api/v1/vessels'
    # vsl_s=requests.get(vsl_url ).json()
    # vsl_name=pd.DataFrame.from_dict(s['vessel_data'])
    # vsl_name.head()
    # col_vsl= dict(zip(vsl_name['imo'], vsl_name['name']))
    # s=s['data']
    #INPUT PARAMETERS
    # first_Period='2019'
    # second_Period='2022'
    # Report_type="Vessel Wise"
    # vessel_name='MSC ANS'
    # fleet='1'
    # class_name='PCTC'
    # moving_average="1"
    vsl_name=pd.DataFrame.from_dict(s['vessel_data'])
    vsl_name.head()
    col_vsl= dict(zip(vsl_name['imo'], vsl_name['name']))

    if (first_Period and second_Period) != None:
        Heading="YEAR"+"  "+first_Period+" - "+second_Period+"  "+"EEOI ANALYSIS"
        first_Period_year = first_Period
        second_Period_year = second_Period
    else:
        date_object_first_Period = datetime.strptime(first_period_max, '%Y-%m-%d')
        first_Period_year = date_object_first_Period.year
        date_object_second_Period = datetime.strptime(second_period_max, '%Y-%m-%d')
        second_Period_year = date_object_second_Period.year
        Heading="YEAR"+"  "+str(first_Period_year)+" - "+str(second_Period_year)+"  "+"EEOI ANALYSIS"
        

        
    Table1 = pd.DataFrame.from_dict(s['data']['table1']['table1']).fillna(0)
    Table1['improvement'] = Table1['improvement'].astype(float).astype(int)
    Table1_str = Table1[['index', 'year1', 'year2', 'improvement']].astype(str)
    Table1_str['improvement'] = Table1_str['improvement'] + ' %'

    MVG_Total_sum = 0
    MVG_Total_TEU_sum = 0

    if report_type == 'vessel':
        mvg_year1 = pd.DataFrame.from_dict(s['data']['year1']['moving data average'])
        mvg_year2 = pd.DataFrame.from_dict(s['data']['year2']['moving data average'])

        if mvg_year1.empty and mvg_year2.empty:
            print('No Data Available')
        else:
            plt.figure(figsize=(10, 6))
            if not mvg_year1.empty:
                MVG_Total_sum += mvg_year1["EEOI For Cargo [MT]"].sum()
                sns.lineplot(x="S.No", y="EEOI For Cargo [MT]", data=mvg_year1, color="green", marker="o", markersize=8,
                            label=moving_average + " " + "Moving Avg" + " " + (first_Period if first_Period and second_Period else str(first_Period_year)))
                sns.lineplot(x="S.No", y="EEOIGOALMT", data=mvg_year1, color="blue", label='EEOI GOAL MT', linestyle='dotted')

            if not mvg_year2.empty:
                MVG_Total_sum += mvg_year2["EEOI For Cargo [MT]"].sum()
                sns.lineplot(x="S.No", y="EEOI For Cargo [MT]", data=mvg_year2, color="orange", marker="o", markersize=8,
                            label=moving_average + " " + "Moving Avg" + " " + (second_Period if first_Period and second_Period else str(second_Period_year)))
                sns.lineplot(x="S.No", y="EEOIGOALMT", data=mvg_year2, color="blue", linestyle='dotted')

            plt.xlabel(" ", fontsize=12, fontweight="bold", fontname="Times New Roman")
            plt.ylabel("Moving Average [MT]", fontsize=12, fontweight="bold", fontname="Times New Roman")
            plt.title('EEOI Moving Average [MT]', size=15, fontweight="bold", fontname="Times New Roman")
            plt.savefig('./images/Environment-Period-Comparison-Moving-Average-MT.png')
            #plt.clf()
            plt.clf()
            
            plt.figure(figsize=(10, 6))
            if not mvg_year1.empty:
                MVG_Total_TEU_sum += mvg_year1["EEOI For Cargo [TEU]"].sum()
                sns.lineplot(x="S.No", y="EEOI For Cargo [TEU]", data=mvg_year1, color="green", marker="o", markersize=8,
                            label=moving_average + " " + "Moving Avg" + " " + (first_Period if first_Period and second_Period else str(first_Period_year)))
                sns.lineplot(x="S.No", y="EEOIGOALMT", data=mvg_year1, color="blue", label='EEOI GOAL TEU', linestyle='dotted')

            if not mvg_year2.empty:
                MVG_Total_TEU_sum += mvg_year2["EEOI For Cargo [TEU]"].sum()
                sns.lineplot(x="S.No", y="EEOI For Cargo [TEU]", data=mvg_year2, color="orange", marker="o", markersize=8,
                            label=moving_average + " " + "Moving Avg" + " " + (second_Period if first_Period and second_Period else str(second_Period_year)))
                sns.lineplot(x="S.No", y="EEOIGOALMT", data=mvg_year2, color="blue", linestyle='dotted')

            plt.xlabel(" ", fontsize=12, fontweight="bold", fontname="Times New Roman")
            plt.ylabel("Moving Average [TEU]", fontsize=12, fontweight="bold", fontname="Times New Roman")
            plt.title('EEOI Moving Average [TEU]', size=15, fontweight="bold", fontname="Times New Roman")
            plt.savefig('./images/Environment-Period-Comparison-Moving-Average-TEU.png')
            #plt.clf()
            plt.clf()
            
    else:
        FirstPeriodData = pd.DataFrame.from_dict(s['data']['FirstPeriodData'])
        FirstPeriodData_1=FirstPeriodData[['Vessel Name', 'Cargo Total (MT)', 'Cargo Total (TEU)', 'Distance (NM)','Number of Voyages','Total CO2 (MT)',
                                        'Equivalent HFO (MT)','EEOI (gm/MT-NM)', 'EEOI (gm/TEU-NM)','Fuel per Miles(Kg/NM)','Distance per Voyage (NM)',
                                        'Fuel Consumption per Voyage (MT)']].round(2)
        #FirstPeriodData_1['eeoi_mt'] = FirstPeriodData_1['eeoi_mt'].astype('float32')
        #FirstPeriodData_1['eeoi_teu'] = FirstPeriodData_1['eeoi_teu'].astype('float32')
        FirstPeriodData_str=FirstPeriodData_1.astype(str)
        SecondPeriodData = pd.DataFrame.from_dict(s['data']['SecondPeriodData'])
        SecondPeriodData['Vessel Name'].nunique()
        SecondPeriodData_1=SecondPeriodData[['Vessel Name', 'Cargo Total (MT)', 'Cargo Total (TEU)', 'Distance (NM)','Number of Voyages','Total CO2 (MT)',
                                        'Equivalent HFO (MT)','EEOI (gm/MT-NM)', 'EEOI (gm/TEU-NM)','Fuel per Miles(Kg/NM)','Distance per Voyage (NM)',
                                        'Fuel Consumption per Voyage (MT)']].round(2)
        SecondPeriodData_str=SecondPeriodData_1.astype(str)
        Year1_Graph=pd.DataFrame.from_dict(s['data']['year1']['finaldata']).round(2)
        Year2_Graph=pd.DataFrame.from_dict(s['data']['year2']['finaldata']).round(2)
    
        #ENERGY EFFICIENCY
        Year1_Graph=pd.DataFrame.from_dict(s['data']['year1']['finaldata']).round(2)
        Year2_Graph=pd.DataFrame.from_dict(s['data']['year2']['finaldata']).round(2)

        Energy_Efficiency=Year1_Graph[['imo','eeoi_mt']]
        if second_Period != None:
            Energy_Efficiency[second_Period] = Energy_Efficiency['imo'].map(Year2_Graph.set_index('imo')['eeoi_mt'])
            Energy_Efficiency=Energy_Efficiency.sort_values(by=second_Period)
        else:
            Energy_Efficiency[str(second_Period_year)] = Energy_Efficiency['imo'].map(Year2_Graph.set_index('imo')['eeoi_mt'])
            Energy_Efficiency=Energy_Efficiency.sort_values(by= str(second_Period_year))


        Energy_Efficiency['Vessel Name'] = Energy_Efficiency['imo'].map(col_vsl)
        Energy_Efficiency['Vessel - IMO']= Energy_Efficiency['Vessel Name']
        Energy_Efficiency=Energy_Efficiency.rename({'eeoi_mt': str(first_Period_year)},axis=1)

            #For 1 st Graph
        if (first_Period and second_Period) != None:

            Energy_Efficiency_graph = Energy_Efficiency.plot.bar(rot=0, x='Vessel - IMO',color={first_Period: "#c44332", second_Period: "#1a75c1"},figsize=(25, 8))#width=0.8

        else:
            Energy_Efficiency_graph = Energy_Efficiency.plot.bar(rot=0, x='Vessel - IMO',color={str(first_Period_year): "#c44332", str(second_Period_year): "#1a75c1"},figsize=(25, 8))#width=0.8

        plt.xlabel("Vessel Name", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        plt.ylabel("Energy Efficiency (g/Ton-Nm)", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        plt.title('Energy Efficiency', size=30,fontweight="bold",fontname="Times New Roman")
        if len(Energy_Efficiency_graph.containers) > 0:
            Energy_Efficiency_graph.bar_label(Energy_Efficiency_graph.containers[0])
        if len(Energy_Efficiency_graph.containers) > 1:
            Energy_Efficiency_graph.bar_label(Energy_Efficiency_graph.containers[1])
        plt.xticks(rotation=90)
        plt.tight_layout()
        # Set general font size
        plt.rcParams['font.size'] = '12'
        plt.savefig('./images/Period Comparison - Energy Efficiency Graph.png', bbox_inches="tight")
        plt.clf()
        #plt.clf()


        #Energy Efficiency - period wise difference
        if (first_Period and second_Period) != None:

            Energy_Efficiency['Difference']=Energy_Efficiency[second_Period]-Energy_Efficiency[first_Period]
        else:
            Energy_Efficiency['Difference']=Energy_Efficiency[str(second_Period_year)]-Energy_Efficiency[str(first_Period_year)]
        Energy_Efficiency=Energy_Efficiency.sort_values(by='Difference',ascending=False)
        #For 2 nd Graph
        plt.figure(figsize=(25,7))
        EEOI_Diff=sns.barplot(x = "Vessel - IMO",y = "Difference",data = Energy_Efficiency,color="#cc0a0a")
        plt.xlabel("Vessel Name", fontsize= 20,fontweight="bold",fontname="Times New Roman")
        plt.ylabel("Energy Efficiency (g/Ton-Nm)", fontsize= 20,fontweight="bold",fontname="Times New Roman")
        plt.title('Energy Efficiency - Period wise Difference', size=30,fontweight="bold",fontname="Times New Roman")
        plt.xticks(rotation=90)
        plt.tight_layout()
        # Set general font size
        plt.rcParams['font.size'] = '12'
        plt.savefig('./images/Period Comparison - Energy Efficiency Difference Graph.png', bbox_inches="tight")
        plt.clf()
        #plt.clf()


        #Total_Cargo
        Total_Cargo=Year1_Graph[['imo','cargomt']]

        if second_Period !=None:
            Total_Cargo[second_Period] = Total_Cargo['imo'].map(Year2_Graph.set_index('imo')['cargomt'])
            Total_Cargo=Total_Cargo.sort_values(by=second_Period)
        else:
            Total_Cargo[str(second_Period_year)] = Total_Cargo['imo'].map(Year2_Graph.set_index('imo')['cargomt'])
            Total_Cargo=Total_Cargo.sort_values(by=str(second_Period_year))

        Total_Cargo['Vessel Name'] = Total_Cargo['imo'].map(col_vsl)
        Total_Cargo['Vessel - IMO']=Total_Cargo['Vessel Name']

        if first_Period !=None:
            Total_Cargo=Total_Cargo.rename({'cargomt':first_Period},axis=1)
            Total_Cargo_Graph = Total_Cargo.plot.bar(rot=0, x='Vessel - IMO',color={first_Period: "#c44332", second_Period: "#1a75c1"},figsize=(25, 8))

        else:
            Total_Cargo=Total_Cargo.rename({'cargomt':str(first_Period_year)},axis=1)
            Total_Cargo_Graph = Total_Cargo.plot.bar(rot=0, x='Vessel - IMO',color={str(first_Period_year): "#c44332", str(second_Period_year): "#1a75c1"},figsize=(25, 8))

        #For 3rd Graph
        plt.xlabel("Vessel Name", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        plt.ylabel("Total Cargo (metric-Tonne)", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        #plt.title('Total Cargo', size=30,fontweight="bold",fontname="Times New Roman")
        #Total_Cargo_Graph.bar_label(Total_Cargo_Graph.containers[0])
        #Total_Cargo_Graph.bar_label(Total_Cargo_Graph.containers[1])

        bars = Total_Cargo_Graph.containers
        Total_Cargo_Graph.bar_label(bars[0], fmt='%.2f', rotation=90)
        if len(bars) > 1:
            Total_Cargo_Graph.bar_label(bars[1], fmt='%.2f', rotation=90)
        # Set general font size
        plt.rcParams['font.size'] = '8'


        def format_y_tick(tick_val, tick_pos):
            """
            Formats y-axis tick labels to display values in k format
            """
            if tick_val >= 1000:
                return f"{tick_val/1000:.0f}k"
            else:
                return tick_val

        plt.xticks(rotation=90)
        plt.tight_layout()
        # Set y-axis tick formatter to custom function
        Total_Cargo_Graph.yaxis.set_major_formatter(FuncFormatter(format_y_tick))
        plt.savefig('./images/Period Comparison - Total Cargo Graph.png', bbox_inches="tight")
        plt.clf()
        #plt.clf()


        #Total Cargo - period wise difference

        if (first_Period and second_Period) != None:
            Total_Cargo['Difference']=Total_Cargo[second_Period]-Total_Cargo[first_Period]

        else:
            Total_Cargo['Difference']=Total_Cargo[str(second_Period_year)]-Total_Cargo[str(first_Period_year)]

        Total_Cargo=Total_Cargo.sort_values(by='Difference',ascending=False)
        #For 4 th Graph
        plt.figure(figsize=(25,7))
        Distance_Diff=sns.barplot(x = "Vessel - IMO",y = "Difference",data = Total_Cargo,color="#cc0a0a")
        plt.xlabel("Vessel Name", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        plt.ylabel("Total Cargo (metric-Tonne)", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        plt.title('Total Cargo - Period wise Difference', size=30,fontweight="bold",fontname="Times New Roman")
        plt.xticks(rotation=90)
        plt.tight_layout()
        # Set general font size
        plt.rcParams['font.size'] = '12'
        plt.savefig('./images/Period Comparison - Total Cargo Difference Graph.png', bbox_inches="tight")
        plt.clf()
        #plt.clf()


        #Total_Distance
        Total_Distance=Year1_Graph[['imo','average_distance']]
        if second_Period !=None:
            Total_Distance[second_Period] = Total_Distance['imo'].map(Year2_Graph.set_index('imo')['average_distance'])
            Total_Distance=Total_Distance.sort_values(by=second_Period)

        else:
            Total_Distance[str(second_Period_year)] = Total_Distance['imo'].map(Year2_Graph.set_index('imo')['average_distance'])
            Total_Distance=Total_Distance.sort_values(by=str(second_Period_year))


        Total_Distance['Vessel Name'] = Total_Distance['imo'].map(col_vsl)
        Total_Distance['Vessel - IMO']=Total_Cargo['Vessel Name']

        if first_Period !=None:

            Total_Distance=Total_Distance.rename({'average_distance':first_Period},axis=1)
        else:
            Total_Distance=Total_Distance.rename({'average_distance':str(first_Period_year)},axis=1)


        # For 5th Graph
        if (first_Period and second_Period) != None:

            Total_Distance_Graph = Total_Distance.plot.bar(rot=0, x='Vessel - IMO',color={first_Period: "#c44332", second_Period: "#1a75c1"},figsize=(25, 8))
        else:
            Total_Distance_Graph = Total_Distance.plot.bar(rot=0, x='Vessel - IMO',color={str(first_Period_year): "#c44332", str(second_Period_year): "#1a75c1"},figsize=(25, 8))


        plt.xlabel("Vessel Name", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        plt.ylabel("Total Distance (Nm)", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        plt.title('Total Distance', size=30,fontweight="bold",fontname="Times New Roman")
        bars = Total_Distance_Graph.containers
        Total_Distance_Graph.bar_label(bars[0], fmt='%.2f', rotation=90)
        if len(bars) > 1:
            Total_Distance_Graph.bar_label(bars[1], fmt='%.2f', rotation=90)
        # Set general font size
        plt.rcParams['font.size'] = '8'
        # Total_Distance_Graph.bar_label(Total_Distance_Graph.containers[0])
        # Total_Distance_Graph.bar_label(Total_Distance_Graph.containers[1])
        # Set general font size
        plt.xticks(rotation=90)
        Total_Distance_Graph.spines['top'].set_visible(False)
        plt.tight_layout()
        # Set y-axis tick formatter to custom function
        Total_Distance_Graph.yaxis.set_major_formatter(FuncFormatter(format_y_tick))
        plt.savefig('./images/Period Comparison - Total Distance Graph.png', bbox_inches="tight")
        plt.clf()
        #plt.clf()


        #Total Distance Period Wise Difference
        if (first_Period and second_Period) != None:

            Total_Distance['Difference']=Total_Distance[second_Period]-Total_Distance[first_Period]
        else:
            Total_Distance['Difference']=Total_Distance[str(second_Period_year)]-Total_Distance[str(first_Period_year)]


        Total_Distance=Total_Distance.sort_values(by='Difference',ascending=False)
        #For 6 th Graph
        plt.figure(figsize=(25,7))
        Distance_Diff=sns.barplot(x = "Vessel - IMO",y = "Difference",data = Total_Distance,color="#cc0a0a")
        plt.xlabel("Vessel Name", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        plt.ylabel("Total Distance (Nm)", fontsize= 22,fontweight="bold",fontname="Times New Roman")
        plt.title('Total Distance - Period wise Difference', size=30,fontweight="bold",fontname="Times New Roman")
        
        plt.xticks(rotation=90)
        plt.tight_layout()
        # Set general font size
        plt.rcParams['font.size'] = '12'
        plt.savefig('./images/Period Comparison - Total Distance Difference Graph.png', bbox_inches="tight")
        plt.clf()
        #plt.clf()


    EEOI_Analysis = Table1.set_index(['index'])
    EEOI_Analysis = EEOI_Analysis.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
    EEOI_Analysis=EEOI_Analysis[['year1','year2']]
    #For EEOI_Analysis_Graph

    if (first_Period and second_Period) != None:

        EEOI_Analysis_new=EEOI_Analysis.rename({"year1":first_Period ,'year2':second_Period},axis=1)
        EEOI_Analysis_Graph = EEOI_Analysis_new.plot.bar(rot=0, color={first_Period: "#588aee", second_Period: "#61d8a8"},width=0.8,figsize=(10, 6))

    else:
        EEOI_Analysis_new=EEOI_Analysis.rename({"year1":str(first_Period_year) ,'year2':str(second_Period_year)},axis=1)
        EEOI_Analysis_Graph = EEOI_Analysis_new.plot.bar(rot=0, color={str(first_Period_year): "#588aee", str(second_Period_year): "#61d8a8"},width=0.8,figsize=(10, 6))
    plt.xlabel(" ", fontsize= 15,fontweight="bold",fontname="Times New Roman")
    plt.ylabel(" Value ", fontsize= 15,fontweight="bold",fontname="Times New Roman")
    plt.title('EEOI ANALYSIS', size=18,fontweight="bold",fontname="Times New Roman")
    EEOI_Analysis_Graph.bar_label(EEOI_Analysis_Graph.containers[0])
    EEOI_Analysis_Graph.bar_label(EEOI_Analysis_Graph.containers[1])
    # Set general font size
    plt.rcParams['font.size'] = '8'
    # Set tick font size
    for label in (EEOI_Analysis_Graph.get_xticklabels() + EEOI_Analysis_Graph.get_yticklabels()):
        label.set_fontsize(9)

    plt.savefig('./images/Period Comparison - EEOI Analysis Bar Graph.png')
    plt.clf()
    #plt.clf()
    Improvement_Percent = Table1.set_index(['index'])
    Improvement_Percent = Improvement_Percent.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
    Improvement_Percent = Improvement_Percent[['improvement']].reset_index()
    Improvement_Percent = Improvement_Percent.set_index(['index'])
    import matplotlib.ticker as mtick
    Improvement_Graph = Improvement_Percent.plot.bar(rot=0,width=0.8,figsize=(10, 6),color='#adb59c')
    plt.xlabel(" ", fontsize=15, fontweight="bold", fontname="Times New Roman")
    plt.ylabel("% Improvement", fontsize=15, fontweight="bold", fontname="Times New Roman")
    plt.title('Yearly % Improvement EEOI Analysis', size=17, fontweight="bold", fontname="Times New Roman")

    # add labels to the bars
    Improvement_Graph.bar_label(Improvement_Graph.containers[0])

    # format the y-axis tick labels as percentages
    def to_percent(y, position):
        return f'{int(y)}%'

    Improvement_Graph.yaxis.set_major_formatter(mtick.FuncFormatter(to_percent))

    # add the percent symbol to the y-axis labels displayed on the graph
    for label in Improvement_Graph.yaxis.get_majorticklabels():
        label.set_text(label.get_text() + '%')
    for label in (EEOI_Analysis_Graph.get_xticklabels() + EEOI_Analysis_Graph.get_yticklabels()):
        label.set_fontsize(9)
    plt.legend().remove()
    # set the font size of the tick labels
    plt.rcParams['font.size'] = '8'
    plt.savefig('./images/Period Comparison - EEOI Analysis Improvement % Graph.png')
    plt.clf()
    #2nd Table
    Table_2 = Table1.set_index(['index'])
    Table_2 = Table_2.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]].reset_index()
    if (first_Period and second_Period) !=None:

        Table_2=Table_2.rename({'improvement':'Improvement (%)','year1':first_Period,'year2':second_Period,'index':'Year'},axis=1)
    else:
        Table_2=Table_2.rename({'improvement':'Improvement (%)','year1':str(first_Period_year),'year2': str(second_Period_year),'index':'Year'},axis=1)

    Table_2_new = Table_2.T.reset_index().T.set_index(0).T
    Table_2_str=Table_2_new.astype(str)






    

    from fpdf import FPDF
    def simple_table(spacing=2.5):
        pdf = FPDF()
        pdf.add_page()

        #Page Number
        pdf.set_y(265)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")

        #Logo
        # pdf.image("/Users/sreelakshmi.m//Downloads/Oceanix Logo (2).png",20,30,w=30)
        pdf.image(msc_logo_path,160,16,w=30)

        #Main Heading
        pdf.set_font('Arial', 'B', 18)
        pdf.set_xy(50,52)
        pdf.set_text_color(25,47,133)
        pdf.multi_cell(115, 8, Heading,align='C')
        pdf.set_line_width(1)
        pdf.line(10, 61, 199, 61)#(x_start, y_start, x_end, y_end)

        #Vessel Name
        pdf.set_font('Arial', '', 13)
        pdf.set_text_color(0,0,0)
        pdf.set_xy(10,66)
        if report_type=='vessel':  
            pdf.multi_cell(90, 7,"Vessel Name    : ",align='L')
            pdf.set_xy(50,66)
            pdf.multi_cell(90, 7,vessel_name,align='L')
        elif report_type=='fleet':  
            pdf.multi_cell(90, 7,"Fleet Name       : ",align='L')
            pdf.set_xy(50,66)
            pdf.multi_cell(90, 7,fleet,align='L')
        else:
            pdf.multi_cell(90, 7,"Class Name      : ",align='L')
            pdf.set_xy(50,66)
            pdf.multi_cell(90, 7,class_name,align='L')


        pdf.set_xy(10,73)
        pdf.multi_cell(90, 7,"First Period       : ",align='L')
        pdf.set_xy(50,73)
        pdf.set_font('Arial', '', 12)
        if first_Period  != None:
            pdf.multi_cell(90, 7,first_Period,align='L') 

        else:
            pdf.multi_cell(90, 7,first_period_min+' to '+first_period_max,align='L') 
        pdf.set_xy(10,80)
        pdf.set_font('Arial', '', 13)
        pdf.multi_cell(90, 7,"Second Period  : ",align='L')
        pdf.set_xy(50,80)
        pdf.set_font('Arial', '', 12)
        if second_Period  != None:
            pdf.multi_cell(90, 7,second_Period,align='L') 
        else:       
            pdf.multi_cell(90, 7,second_period_min+' to '+second_period_max,align='L') 

            #pdf.multi_cell(90, 7,first_period_min+' to '+first_period_max,align='L')
            #pdf.multi_cell(90, 7,second_period_min+' to '+second_period_max,align='L')
        pdf.set_line_width(0)
        pdf.line(10, 90, 199, 90)

        #Table 1
        pdf.set_xy(10,98)
        pdf.set_line_width(0)
        pdf.set_font('Arial', 'B', 15)
        pdf.set_text_color(25,47,133)
        pdf.cell(180, 7,"YEARLY ANALYSIS",ln=True,align='L')
        
        if (first_Period and second_Period)  != None:

            Table_1_head_Year=[['Year', first_Period, second_Period, '% Improvement']]
        else:
            Table_1_head_Year=[['Year', first_Period_year, second_Period_year, '% Improvement']]

        Table_1_Year = Table1_str.values.tolist()
        pdf.set_font("Arial","B", size=9)
        col_width = pdf.w / 4.44
        row_height = pdf.font_size

        for row in Table_1_head_Year:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=str(item), border=1,fill=True)
            pdf.ln(row_height*spacing)

        pdf.set_font("Arial","", size=7.7)
        pdf.set_text_color(0,0,0)
        for row in Table_1_Year:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
    #------------------------------------------------------------------------------------------------------------------------------#
        #2nd Page
        pdf.add_page()

        #Yearly EEOI Analysis Heading
        pdf.set_font('Arial', 'B', 15)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(10,20)
        pdf.cell(180, 7,"YEARLY EEOI ANALYSIS",ln=True,align='L')
        pdf.set_text_color(0,0,0)

        #Table 2
        pdf.set_xy(10,30)
        Table_2_head_Year=[['Year',"CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        Table_2_Year = Table_2_str.values.tolist()
        pdf.set_font("Arial","B", size=7)
        col_width = pdf.w / 5.65
        row_height = pdf.font_size

        for row in Table_2_head_Year:
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)

        pdf.set_font("Arial","", size=7.7)
        pdf.set_text_color(0,0,0)
        for row in Table_2_Year:
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)  

        #Setting Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly
        pdf.image("./images/Period Comparison - EEOI Analysis Bar Graph.png",10,65,w=193,h=90) 


        #Yearly % Improvment EEOI Analysis Heading
        pdf.set_font('Arial', 'B', 15)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(10,165)
        pdf.cell(170, 7,"YEARLY % IMPROVEMENT - EEOI ANALYSIS",ln=True,align='L')
        pdf.set_text_color(0,0,0)

        #Setting Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly
        pdf.image("./images/Period Comparison - EEOI Analysis Improvement % Graph.png",10,176,w=193,h=90)

        #Page Number 2
        pdf.set_y(265)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")

        #3rd Page
        pdf.add_page()
        if report_type=='vessel':
            #Yearly % Improvment EEOI Analysis Heading
            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
            pdf.set_xy(10,20)
            pdf.cell(170, 7,"YEARLY EEOI MOVING AVERAGE [MT]",ln=True,align='L')
            pdf.set_text_color(0,0,0)

            if mvg_year1.empty and mvg_year2.empty:
                pdf.set_xy(80,68)

                pdf.set_font('Arial', 'B', 15)
                pdf.multi_cell(50,20,"No Data Available",align='C')

            elif MVG_Total_sum == 0:
                pdf.set_xy(80,68)

                pdf.set_font('Arial', 'B', 15)
                pdf.multi_cell(50,20,"No Data Available",align='C')



            else:
            #Setting Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly
                pdf.image("./images/Environment-Period-Comparison-Moving-Average-MT.png",33.5,30,w=145,h=90) 


            #TEU GRAPH

            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
            pdf.set_xy(10,125)
            pdf.cell(170, 7,"YEARLY EEOI MOVING AVERAGE [TEU]",ln=True,align='L')
            pdf.set_text_color(0,0,0)

            if ( mvg_year1.empty and  mvg_year2.empty):
                pdf.set_xy(80,168)

                pdf.set_font('Arial', 'B', 15)
                pdf.multi_cell(50,20,"No Data Available",align='C')

            elif  MVG_Total_TEU_sum == 0:

                pdf.set_xy(80,168)

                pdf.set_font('Arial', 'B', 15)
                pdf.multi_cell(50,20,"No Data Available",align='C')
            else:
            #Setting Environment- Yearly Analysis - EEOI Analysis Bar Graph- Yearly
                pdf.image('./images/Environment-Period-Comparison-Moving-Average-TEU.png',33.5,135,w=145,h=90) 

        else:
            #ENERGY EFFICIENCY Heading
            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
            pdf.set_xy(10,20)
            pdf.cell(180, 7,"ENERGY EFFICIENCY",ln=True,align='L')
            pdf.set_text_color(0,0,0)
            #ENERGY EFFICIENCY GRAPH
            pdf.image("./images/Period Comparison - Energy Efficiency Graph.png",10,32,w=193,h=90)

            #ENERGY EFFICIENCY PERIOD WISE COMPARISON GRAPH
            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
            pdf.set_xy(10,138)
            pdf.cell(180, 7,"ENERGY EFFICIENCY - PERIOD WISE COMPARISON GRAPH",ln=True,align='L')
            pdf.set_text_color(0,0,0)
            #TOTAL CARGO Graph
            pdf.image("./images/Period Comparison - Energy Efficiency Difference Graph.png",10,150,w=193,h=90)

            #Page Number 3
            pdf.set_y(265)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")

            #4th Page
            pdf.add_page()
            #TOTAL CARGO
            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
            pdf.set_xy(10,20)
            pdf.cell(180, 7,"TOTAL CARGO",ln=True,align='L')
            pdf.set_text_color(0,0,0)
            #TOTAL CARGO Graph
            pdf.image("./images/Period Comparison - Total Cargo Graph.png",10,32,w=193,h=90)

            #TOTAL CARGO PERIOD WISE COMPARISON GRAPH
            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
            pdf.set_xy(10,138)
            pdf.cell(180, 7,"TOTAL CARGO - PERIOD WISE COMPARISON GRAPH",ln=True,align='L')
            pdf.set_text_color(0,0,0)
            #TOTAL CARGO Graph
            pdf.image("./images/Period Comparison - Total Cargo Difference Graph.png",10,150,w=193,h=90)

            #Page Number 3
            pdf.set_y(265)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")

            #5th Page
            pdf.add_page()
            #TOTAL DISTANCE
            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
            pdf.set_xy(10,20)
            pdf.cell(180, 7,"TOTAL DISTANCE",ln=True,align='L')
            pdf.set_text_color(0,0,0)
            #TOTAL DISTANCE Graph
            pdf.image("./images/Period Comparison - Total Distance Graph.png",10,32,w=193,h=90)

            #TOTAL DISTANCE PERIOD WISE COMPARISON GRAPH
            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
            pdf.set_xy(10,138)
            pdf.cell(180, 7,"TOTAL DISTANCE - PERIOD WISE COMPARISON GRAPH",ln=True,align='L')
            pdf.set_text_color(0,0,0)
            #TOTAL DISTANCE Graph
            pdf.image("./images/Period Comparison - Total Distance Difference Graph.png",10,150,w=193,h=90)

            #Page Number 3
            pdf.set_y(265)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0,10,'Page %s' % pdf.page_no(),align="R")




            pdf.add_page(orientation = 'L')
            #First Period Data
            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
            pdf.set_xy(10.1,10)
            pdf.cell(180, 7,"FIRST PERIOD DATA",ln=True,align='L')
            pdf.set_text_color(0,0,0)
            #First Period Table
            pdf.set_xy(10,20)
            Table_3_head_Year=[['Vessel Name','Cargomt','Cargoteu','Distance','EEOI_Voy_no','Totalco2_mt','Totalco2_kgnm',
                                                    'EEOI_mt', 'EEOI_teu','Fuelkg_nm','Average Distance','Average Fuelcons']]

            Table_3_Year1 = FirstPeriodData_str.values.tolist()
            pdf.set_font("Arial","B", size=5.5)
            col_width = pdf.w / 12.9
            row_height = pdf.font_size

            for row in Table_3_head_Year:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial","", size=6)
            pdf.set_text_color(0,0,0)
            for row in Table_3_Year1:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)


            #Second Period Data
            pdf.add_page(orientation = 'L')
            pdf.set_font('Arial', 'B', 15)
            pdf.set_text_color(25,47,133)
        #  pdf.set_xy(10,10)
            pdf.cell(180, 5,"",ln=True,align='L')
            pdf.cell(180, 7,"SECOND PERIOD DATA",ln=True,align='L')
            pdf.cell(180, 3,"",ln=True,align='L')
            pdf.set_text_color(0,0,0) 

            #Second Period Table
        #   pdf.set_xy(10,20)
            Table_4_head_Year=[['Vessel Name','Cargomt','Cargoteu','Distance','EEOI_Voy_no','Totalco2_mt','Totalco2_kgnm',
                                                    'EEOI_mt', 'EEOI_teu','Fuelkg_nm','Average Distance','Average Fuelcons']]
            Table_4_Year2 =SecondPeriodData_str.values.tolist()
            pdf.set_font("Arial","B", size=5.5)
            col_width = pdf.w / 12.9
            row_height = pdf.font_size

            for row in Table_4_head_Year:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(21,55,188)
                for item in row:
                    pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
                pdf.ln(row_height*spacing)

            pdf.set_font("Arial","", size=6)
            pdf.set_text_color(0,0,0)
            for row in Table_4_Year2:
                for item in row:
                    pdf.cell(col_width, row_height*spacing,
                            txt=item, border=1)
                pdf.ln(row_height*spacing)
    
    #------------------------------------------------------------------------------------------------------------------------------#
        pdf.output(pdf_name,'F')
    pdf_name = './documents/MSC_Period_Comparison' + vessel_name + '.pdf'

    
    simple_table()     

    return FileResponse(path = pdf_name,filename=pdf_name)





@router.post('/api/v1/pdf/slipreport')
async def index( info : Request,chart_type:str=None ,mode:str = None,start_date:str = None ,end_date:str = None , prop_type:str = None  ,vessel_name:str =None):
 
    slip_data = await info.json()

    

    slip_chart = pd.DataFrame.from_dict(slip_data["slipReportChartData"]['chartData1']).drop_duplicates(keep='first')

    if chart_type == 'class':
        if prop_type == "All":
            slip_chart_filtered = slip_chart
        else:
            slip_chart_filtered = slip_chart[slip_chart["prop_type"] == prop_type]
        slip_chart_pivot = slip_chart_filtered.pivot(index="vessel_name", columns="type", values="value").reset_index()
        slip_chart_melted = slip_chart_pivot.melt(id_vars='vessel_name', var_name='type', value_name='value')
        xlabel = 'Vessel'
        ylabel = '% Slip'
        legend_title = 'Type'
    else:
        if prop_type == "All":
            slip_chart_filtered = slip_chart.copy()  # Make a copy of the original DataFrame
            xlabel = 'Vessel'
            ylabel = '% Slip'
        else:
            slip_chart_filtered = slip_chart[slip_chart["prop_type"] == prop_type].copy()  # Filtered DataFrame
            xlabel = 'Vessel (' + prop_type + ')'
            ylabel = '% Deviation'
        legend_title = 'Type'

    custom_palette = {
        'Avg. Benchmark Slip (SOG)': 'purple',
        'Avg.Slip(SOG)': 'orange',
        'Deviation SOG': 'navy',
        'Avg. Benchmark Slip (STW)': 'teal',
        'Avg. Slip(STW)': 'yellowgreen',
        'Deviation STW': 'blue'
    }

    colors = [custom_palette[type_] for type_ in slip_chart_filtered['type'].unique()]
    sns.set_palette(colors)
    fig, ax = plt.subplots(figsize=(14, 10))

    sns.barplot(data=slip_chart_filtered, x='vessel_name', y='value', hue='type', ci=None)

    # Adding annotations
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            xytext = (0, 5)  # Offset for positive values
        else:
            xytext = (0, -15)  # Offset for negative values
        ax.annotate('{:.1f}'.format(height), 
                    xy=(p.get_x() + p.get_width() / 2, height),
                    xytext=xytext,  # Adjust the value to move the text higher or lower
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.legend(title=legend_title, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3)
    ax.grid(False)
    plt.xticks(rotation=45, fontsize=12)  
    plt.yticks(fontsize=12)
    plt.tight_layout()  
 
    plt.savefig('./images/slip_report_slip_deviation.png', bbox_inches='tight')
    # plt.show()
    ##plt.clf()




    ####################################################################################################
    def slip_report_class_fleet(spacing=3):

        pdf = FPDF()
        #*********************************************** 1 page **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 20)

        #pdf.image(oceanix_logo_path,15,15,w=35)
        #pdf.image(msc_logo_path,160,8,w=30)

    #Cell postion from left side
        pdf.set_xy(80,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(175, 20, 'Slip Report')
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 37, 199, 37)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",14)
        pdf.set_x(10)
        if chart_type=="class":
            pdf.cell(10, 60, "Class  :"+" "+mode,ln=True)
        elif chart_type=="fleet":    
            pdf.cell(10, 60, "Fleet  :"+" "+mode,ln=True)
        else:
            print("")
            
        pdf.set_xy(10,15)
        pdf.cell(10,75,"Monitoring Period :"+" "+ start_date + " " + "to" + " "+end_date ,ln=True)
        pdf.line(10, 60, 199, 60)

        if chart_type=="class":
            #pdf.line(10, 70, 199, 70)
            pdf.set_font('Arial', 'B', 18)
            pdf.set_text_color(25,47,133)
            #pdf.cell(180, 2, 'Slip Analysis',ln=True,align='C')
            pdf.image("./images/slip_report_slip_deviation.png",10,70,w=180,h=120)
        else:
            #pdf.line(10, 70, 199, 70)
            pdf.set_font('Arial', 'B', 18)
            pdf.set_text_color(25,47,133)
            #pdf.cell(180, 2, 'Slip Analysis',ln=True,align='C')
            pdf.image("./images/slip_report_slip_deviation.png",10,70,w=180,h=120)
        pdf.output(pdf_name,'F')
    # pdf_name = 'Slip_Report_class_Fleet.pdf'
    pdf_name = './documents/'+vessel_name+'_Slip_Report_class_Fleet.pdf'
    

   
    slip_report_class_fleet()     
    return FileResponse(path = pdf_name,filename=pdf_name)
# import pandas as pd
@router.post('/api/v1/pdf/vesselparticulars')
async def index( info : Request,vessel_name:str =None):
 
    data = await info.json()
    # data = 

    # url1="https://msc.oceanix.cloud/api/v1/attributes"
        
    prop_data=data['data1']
    # prop_data=requests.get(url1).json()
    # prop_data
    # import pandas as pd
    prop_table = pd.DataFrame.from_dict(prop_data['data'])
    prop_table_1=prop_table[["id","property_id","name"]]
    prop_table_1

    # url2="https://msc.oceanix.cloud/api/v1/vessels/9618276/generalinfo"
        
        
    # values=requests.get(url2).json()
    values=data['data2']





    values_table = pd.DataFrame.from_dict(values['data'])
    values_table_1=values_table[["attribute_id","property_id","value"]]
    values_table_1

    dict_1 = pd.Series(values_table_1['value'].values,index=values_table_1['attribute_id']).to_dict()




    prop_table_1['value'] = np.nan

    prop_table_1['value'] = prop_table_1['value'].fillna(prop_table_1['id'].apply(lambda x:dict_1.get(x)))

    prop_table_2 =prop_table_1[prop_table_1["property_id"]==1]
    prop_table_2

    # list1=[157,158,196,159]
    # prop_table_1a =prop_table_1[prop_table_1['id'].isin(list1)]

    prop_table_2 = prop_table_2.drop(prop_table_2[prop_table_2['name'] == '.'].index)

    prop_table_2a =prop_table_2[["name",'value']]
    # prop_table_1b =prop_table_1a[["name",'value']]
    prop_table_object =prop_table_2a.astype(str)
    # prop_table_1b_object =prop_table_1b.astype(str)

    ########## Shipyard and Classification ############
    shipyard_table_1 =prop_table_1[prop_table_1["property_id"]==4]
    shipyard_table_1

    shipyard_table_2 =prop_table_1[prop_table_1["property_id"]==5]
    shipyard_table_2

    shipyard_table_1a =shipyard_table_1[["name",'value']]
    shipyard_table_2a =shipyard_table_2[["name",'value']]
    shipyard_table_1a_object =shipyard_table_1a.astype(str)
    shipyard_table_2a_object =shipyard_table_2a.astype(str)

    ########## Drydock and Survey ############
    drydock_table_1 =prop_table_1[prop_table_1["property_id"]==14]
    drydock_table_1

    drydock_table_2 =prop_table_1[prop_table_1["property_id"]==15]
    drydock_table_2

    drydock_table_1a =drydock_table_1[["name",'value']]
    drydock_table_2a =drydock_table_2[["name",'value']]
    drydock_table_1a_object =drydock_table_1a.astype(str)
    drydock_table_2a_object =drydock_table_2a.astype(str)

    ########## Ship ID & Contact############
    ship_id_table_1 =prop_table_1[prop_table_1["property_id"]==16]
    ship_id_table_1

    ship_id_table_2 =prop_table_1[prop_table_1["property_id"]==17]
    ship_id_table_2

    ship_id_table_1a =ship_id_table_1[["name",'value']]
    ship_id_table_2a =ship_id_table_2[["name",'value']]
    ship_id_table_1a_object =ship_id_table_1a.astype(str)
    ship_id_table_2a_object =ship_id_table_2a.astype(str)
    ########## Tonnage & Loadline############
    tonnage_table_1 =prop_table_1[prop_table_1["property_id"]==18]
    tonnage_table_1

    tonnage_table_2 =prop_table_1[prop_table_1["property_id"]==19]
    tonnage_table_2

    tonnage_table_1a =tonnage_table_1[["name",'value']]
    tonnage_table_2a =tonnage_table_2[["name",'value']]
    tonnage_table_1a_object =tonnage_table_1a.astype(str)
    tonnage_table_2a_object =tonnage_table_2a.astype(str)

    hull_list1=['When was hull last painted?',
    'When is next hull painting planned?',
    'Is Hull silicon painted?',
    'Paint Maker',
    'Paint Type',
    'Paint Scheme (period)',
    'When was hull last cleaned?',
    'When is next hull cleaning planned?']
    ########## Hull & Coating ############
    hull_table_1 =prop_table_1[prop_table_1["property_id"]==20]
    hull_table_1

    hull_table_2 =prop_table_1[prop_table_1["property_id"]==21]
    hull_table_3a =prop_table_1[prop_table_1["property_id"]==31]
    hull_table_3 = hull_table_3a[hull_table_3a["name"].isin(hull_list1)]
    hull_table_4 = hull_table_3a[~hull_table_3a["name"].isin(hull_list1)]

    hull_table_1a =hull_table_1[["name",'value']]
    hull_table_2a =hull_table_2[["name",'value']]
    hull_table_3a =hull_table_3[["name",'value']]
    hull_table_4a =hull_table_4[["name",'value']]


    hull_table_1a_object =hull_table_1a.astype(str)
    hull_table_2a_object =hull_table_2a.astype(str)
    hull_table_3a_object =hull_table_3a.astype(str)
    hull_table_4a_object =hull_table_4a.astype(str)

    ########## Hull Outfitting ############
    hull_outfitting_table_1_a =prop_table_1[prop_table_1["property_id"]==9]

    hull_outfitting_table_1 = hull_outfitting_table_1_a.drop(hull_outfitting_table_1_a[hull_outfitting_table_1_a['name'] == '.'].index)


    hull_outfitting_table_1a =hull_outfitting_table_1[["name",'value']]
    hull_outfitting_table_1a_object =hull_outfitting_table_1a.astype(str)
    hull_outfitting_table_1
    ########## Hull piping ############
    hull_piping_table_1 =prop_table_1[prop_table_1["property_id"]==22]
    hull_piping_table_1

    hull_piping_table_2 =prop_table_1[prop_table_1["property_id"]==23]


    hull_piping_table_1a =hull_piping_table_1[["name",'value']]
    hull_piping_table_2a =hull_piping_table_2[["name",'value']]
    hull_piping_table_1a_object =hull_piping_table_1a.astype(str)
    hull_piping_table_2a_object =hull_piping_table_2a.astype(str)


    ########## Cargo Hold ############
    cargo_hold_table_1 =prop_table_1[prop_table_1["property_id"]==24]


    cargo_hold_table_2 =prop_table_1[prop_table_1["property_id"]==25]


    cargo_hold_table_1a =cargo_hold_table_1[["name",'value']]
    cargo_hold_table_2a =cargo_hold_table_2[["name",'value']]
    cargo_hold_table_1a_object =cargo_hold_table_1a.astype(str)
    cargo_hold_table_2a_object =cargo_hold_table_2a.astype(str)

    cargo_hold_table_3 =prop_table_1[prop_table_1["property_id"]==39]


    cargo_hold_table_4 =prop_table_1[prop_table_1["property_id"]==40]


    cargo_hold_table_3a =cargo_hold_table_3[["name",'value']]
    cargo_hold_table_4a =cargo_hold_table_4[["name",'value']]
    cargo_hold_table_3a_object =cargo_hold_table_3a.astype(str)
    cargo_hold_table_4a_object =cargo_hold_table_4a.astype(str)

    cargo_hold_table_5 =prop_table_1[prop_table_1["property_id"]==41]


    cargo_hold_table_6 =prop_table_1[prop_table_1["property_id"]==42]
    cargo_hold_table_7 =prop_table_1[prop_table_1["property_id"]==43]


    cargo_hold_table_5a =cargo_hold_table_5[["name",'value']]
    cargo_hold_table_6a =cargo_hold_table_6[["name",'value']]
    cargo_hold_table_5a_object =cargo_hold_table_5a.astype(str)
    cargo_hold_table_6a_object =cargo_hold_table_6a.astype(str)
    cargo_hold_table_7a =cargo_hold_table_7[["name",'value']]
    cargo_hold_table_7a_object =cargo_hold_table_7a.astype(str)



    ########## Machinery and Propulsion ############
    machin_prop_table_1 =prop_table_1[prop_table_1["property_id"]==26]


    machin_prop_table_2 =prop_table_1[prop_table_1["property_id"]==27]


    machin_prop_table_1a =machin_prop_table_1[["name",'value']]
    machin_prop_table_2a =machin_prop_table_2[["name",'value']]
    machin_prop_table_1a_object =machin_prop_table_1a.astype(str)
    machin_prop_table_2a_object =machin_prop_table_2a.astype(str)

    machin_prop_table_3 =prop_table_1[prop_table_1["property_id"]==45]


    machin_prop_table_4 =prop_table_1[prop_table_1["property_id"]==69]


    machin_prop_table_3a =machin_prop_table_3[["name",'value']]
    machin_prop_table_4a =machin_prop_table_4[["name",'value']]
    machin_prop_table_3a_object =machin_prop_table_3a.astype(str)
    machin_prop_table_4a_object =machin_prop_table_4a.astype(str)

    ########## LNG ############
    lng_table_1 =prop_table_1[prop_table_1["property_id"]==65]


    lng_table_2 =prop_table_1[prop_table_1["property_id"]==66]


    lng_table_1a =lng_table_1[["name",'value']]
    lng_table_2a =lng_table_2[["name",'value']]
    lng_table_1a_object =lng_table_1a.astype(str)
    lng_table_2a_object =lng_table_2a.astype(str)

    ########## Machinery Electrical ############
    elec_mach_table_1 =prop_table_1[prop_table_1["property_id"]==59]


    elec_mach_table_2 =prop_table_1[prop_table_1["property_id"]==32]


    elec_mach_table_1a =elec_mach_table_1[["name",'value']]
    elec_mach_table_2a =elec_mach_table_2[["name",'value']]
    elec_mach_table_1a_object =elec_mach_table_1a.astype(str)
    elec_mach_table_2a_object =elec_mach_table_2a.astype(str)

    elec_mach_table_3 =prop_table_1[prop_table_1["property_id"]==33]


    elec_mach_table_4 =prop_table_1[prop_table_1["property_id"]==44]


    elec_mach_table_3a =elec_mach_table_3[["name",'value']]
    elec_mach_table_4a =elec_mach_table_4[["name",'value']]
    elec_mach_table_3a_object =elec_mach_table_3a.astype(str)
    elec_mach_table_4a_object =elec_mach_table_4a.astype(str)

    elec_mach_table_5 =prop_table_1[prop_table_1["property_id"]==46]


    elec_mach_table_6 =prop_table_1[prop_table_1["property_id"]==47]
    elec_mach_table_7 =prop_table_1[prop_table_1["property_id"]==58]


    elec_mach_table_5a =elec_mach_table_5[["name",'value']]
    elec_mach_table_6a =elec_mach_table_6[["name",'value']]
    elec_mach_table_5a_object =elec_mach_table_5a.astype(str)
    elec_mach_table_6a_object =elec_mach_table_6a.astype(str)
    elec_mach_table_7a =elec_mach_table_7[["name",'value']]
    elec_mach_table_7a_object =elec_mach_table_7a.astype(str)

    elec_mach_table_8 =prop_table_1[prop_table_1["property_id"]==49]


    elec_mach_table_9 =prop_table_1[prop_table_1["property_id"]==50]
    elec_mach_table_10 =prop_table_1[prop_table_1["property_id"]==37]


    elec_mach_table_8a =elec_mach_table_8[["name",'value']]
    elec_mach_table_9a =elec_mach_table_9[["name",'value']]
    elec_mach_table_8a_object =elec_mach_table_8a.astype(str)
    elec_mach_table_9a_object =elec_mach_table_9a.astype(str)
    elec_mach_table_10a =elec_mach_table_10[["name",'value']]
    elec_mach_table_10a_object =elec_mach_table_10a.astype(str)
    elec_mach_table_11 =prop_table_1[prop_table_1["property_id"]==63]
    elec_mach_table_11a =elec_mach_table_11[["name",'value']]
    elec_mach_table_11a_object =elec_mach_table_11a.astype(str)
    ########## other mechanical ############
    other_mach_table_1 =prop_table_1[prop_table_1["property_id"]==35]
    other_mach_table_1 = other_mach_table_1.drop(other_mach_table_1[other_mach_table_1['name'] == '.'].index)


    other_mach_table_2 =prop_table_1[prop_table_1["property_id"]==36]


    other_mach_table_1a =other_mach_table_1[["name",'value']]
    other_mach_table_2a =other_mach_table_2[["name",'value']]
    other_mach_table_1a_object =other_mach_table_1a.astype(str)
    other_mach_table_2a_object =other_mach_table_2a.astype(str)

    other_mach_table_3 =prop_table_1[prop_table_1["property_id"]==60]


    other_mach_table_4 =prop_table_1[prop_table_1["property_id"]==61]


    other_mach_table_3a =other_mach_table_3[["name",'value']]
    other_mach_table_4a =other_mach_table_4[["name",'value']]
    other_mach_table_3a_object =other_mach_table_3a.astype(str)
    other_mach_table_4a_object =other_mach_table_4a.astype(str)

    other_mach_table_5 =prop_table_1[prop_table_1["property_id"]==62]


    other_mach_table_6 =prop_table_1[prop_table_1["property_id"]==67]


    other_mach_table_5a =other_mach_table_5[["name",'value']]
    other_mach_table_6a =other_mach_table_6[["name",'value']]
    other_mach_table_5a_object =other_mach_table_5a.astype(str)
    other_mach_table_6a_object =other_mach_table_6a.astype(str)

    ######### other mechanical ############
    Mis_table_1 =prop_table_1[prop_table_1["property_id"]==38]
    Mis_table_1 = Mis_table_1.drop(Mis_table_1[Mis_table_1['name'] == '.'].index)

    Mis_table_1a =Mis_table_1[["name",'value']]
    Mis_table_1a_object =Mis_table_1a.astype(str)
    ########## Reefer Capacity ############
    reefer_capacity_table_1 =prop_table_1[prop_table_1["property_id"]==54]
    reefer_capacity_table_2 =prop_table_1[prop_table_1["property_id"]==55]
    reefer_capacity_table_1a =reefer_capacity_table_1[["name",'value']]
    reefer_capacity_table_2a =reefer_capacity_table_2[["name",'value']]
    reefer_capacity_table_1a_object =reefer_capacity_table_1a.astype(str)
    reefer_capacity_table_2a_object =reefer_capacity_table_2a.astype(str)

    reefer_capacity_table_3 =prop_table_1[prop_table_1["property_id"]==56]

    reefer_capacity_table_3a =reefer_capacity_table_3[["name",'value']]
    reefer_capacity_table_3a_object =reefer_capacity_table_3a.astype(str)


    from fpdf import FPDF
    # import pandas as pd

    def Vessel_details_pdf(spacing=3):

        pdf = FPDF()
        #***********************************************  page 1 **********************************************************#
        pdf.add_page()
        pdf.set_font('Arial', 'B', 18)
    # 
        # pdf.image("Oceanix-160x120-06.png",15,15,w=35)
        pdf.image(msc_logo_path,160,12,w=25)
        pdf.set_xy(65,15)
        pdf.set_text_color(25,47,133)
        pdf.cell(170, 60, 'VESSEL PARTICULARS',ln=True)
        pdf.set_text_color(0,0,0)
        pdf.set_line_width(1)
        pdf.line(10, 50, 190, 50)#(x_start, y_start, x_end, y_end)
        pdf.set_line_width(0.2)
        pdf.set_font('Arial', "",12)
        pdf.set_xy(10,55)
        #pdf.multi_cell(80,14.5,"Report Date :"+" "+ report_prepared_date, align='R')

        
        pdf.cell(10, 2, "Vessel Name :"+" "+vessel_name,ln=True)
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,65)
        
        pdf.multi_cell(80, 3,"Principal Particulars" )
        
        
        
        pdf.line(10, 60, 190, 60)
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(19,75)
        
        spacing=3
        column_head_det = [["Vessel Particulars","Details"]]
        prop_values = prop_table_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        
        
    #    ########## 
    #     pdf.set_xy(19,95)
    #     column_head_det2 = [["Propeller Particulars","Details"]]
    #     prop_values1 = prop_table_1b_object.values.tolist()
    #     pdf.set_font("Arial",'B', size=7)
    #     pdf.set_text_color(0,0,0)
    #     col_width = pdf.w /2.25
    #     row_height = pdf.font_size
    #     for row in column_head_det2:
    #         pdf.set_text_color(255,255,255)
    #         pdf.set_fill_color(21,55,188)
    #         for item in row:
    #             pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
    #         pdf.ln(row_height*spacing)
    #     pdf.set_font("Arial", size=7)
    #     pdf.set_text_color(0,0,0)
    #     col_width = pdf.w /2.25
    #     row_height = pdf.font_size
    #     for row in prop_values1:
    #         pdf.set_x(19)
    #         for item in row:
    #             pdf.cell(col_width, row_height*spacing,
    #                      txt=item, border=1)
    #         pdf.ln(row_height*spacing)
            
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
    ############## Shipyard & Classification ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Shipyard & Classification" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Classification","Details"]]
        prop_values = shipyard_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        pdf.set_xy(19,150)    
        column_head_det = [["Shipyard","Details"]]
        prop_values = shipyard_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
    ############## Drydock & Survey ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Drydock & Survey" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Drydock","Details"]]
        prop_values = drydock_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        pdf.set_xy(19,150)    
        column_head_det = [["Survey","Details"]]
        prop_values = drydock_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")     
        
    ############## Ship ID & Contact ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Ship ID & Contact" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Ship ID","Details"]]
        prop_values = ship_id_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")         
            
    # pdf.set_xy(19,150)  

        pdf.add_page()  
        pdf.set_xy(19,20)

        column_head_det = [["Contact","Details"]]
        prop_values = ship_id_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")     
    ############## Tonnage & Loadline ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Tonnage & Loadline" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Tonnage","Details"]]
        prop_values = tonnage_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        pdf.set_xy(19,110)    
        column_head_det = [["Loadline","Details"]]
        prop_values = tonnage_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        ############## Hull  & Caoting ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Hull & Coating" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Hull","Details"]]
        prop_values = hull_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        pdf.set_xy(19,100)    
        column_head_det = [["Tanks & Hold","Details"]]
        prop_values = hull_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
        pdf.set_xy(19,160)    
        column_head_det = [["Coating Scheme","Details"]]
        prop_values = hull_table_3a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)          
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")   
        
        pdf.add_page() 
        pdf.set_font("Arial", size=12)
        for index, row in hull_table_4a.iterrows():
            name = row['name']
            value = row['value']
            pdf.set_text_color(25,47,133)
            pdf.set_font("Arial",'B', size=8.5)
            pdf.cell(200, 10, txt=f"{name}", ln=True)
            pdf.set_text_color(0,0,0)
            pdf.set_font("Arial", size=8)
            pdf.multi_cell(185, 10, txt=value)

            pdf.ln(5)
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
    ############## Hull  Outfitting ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Hull Outfitting" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Hull Outfitting","Details"]]
        prop_values = hull_outfitting_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        ############## Hull  Piping ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Hull Piping" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Tanks","Details"]]
        prop_values = hull_piping_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        pdf.add_page()    
    
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Systems","Details"]]
        prop_values = hull_piping_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        
        
        ############## Cargo Hold ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Cargo/Hold" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Hold Capacity","Details"]]
        prop_values = cargo_hold_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        pdf.add_page()    
    
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Other","Details"]]
        prop_values = cargo_hold_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        pdf.set_xy(19,65)
        column_head_det = [["General Distribution 20","Details"]]
        prop_values = cargo_hold_table_3a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)   
        pdf.set_xy(19,115)
        column_head_det = [["General Distribution 40","Details"]]
        prop_values = cargo_hold_table_4a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)  
        pdf.set_xy(19,165)
        column_head_det = [["General Distribution 40HC","Details"]]
        prop_values = cargo_hold_table_5a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)   
        pdf.set_xy(19,215)
        column_head_det = [["General Distribution 45HC","Details"]]
        prop_values = cargo_hold_table_6a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)         
            
            
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        pdf.add_page()

        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25, 47, 133)

        pdf.set_xy(19, 35)
        column_head_det = [["Vessel Reefer Capacity", "Details"]]
        prop_values = cargo_hold_table_7a_object.values.tolist()
        pdf.set_font("Arial", 'B', size=7)
        pdf.set_text_color(0, 0, 0)

        col_width_1 = pdf.get_string_width("Vessel Reefer Capacity") + 95  
        col_width_2 = pdf.get_string_width("Details") + 55  

        row_height = pdf.font_size

        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        pdf.cell(col_width_1, row_height * spacing, txt="Vessel Reefer Capacity", border=1, fill=True)
        pdf.cell(col_width_2, row_height * spacing, txt="Details", border=1, fill=True)
        pdf.ln(row_height * spacing)

        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0, 0, 0)
        for row in prop_values:
            pdf.set_x(19)
            pdf.cell(col_width_1, row_height * spacing, txt=row[0], border=1)
            pdf.cell(col_width_2, row_height * spacing, txt=row[1], border=1)
            pdf.ln(row_height * spacing)

        # Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 2, 'Page %s' % pdf.page_no(), align="R")
        
        
        ############## Machinery & Propulsion ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Machinery & Propulsion" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        column_head_det = [["Machinery","Details"]]
        prop_values = machin_prop_table_1a_object.values.tolist()
        pdf.set_font("Arial", 'B', size=7)
        pdf.set_text_color(0, 0, 0)

        col_width_1 = pdf.get_string_width("Machinery") + 95  
        col_width_2 = pdf.get_string_width("Details") + 70  

        row_height = pdf.font_size

        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        pdf.cell(col_width_1, row_height * spacing, txt="Machinery", border=1, fill=True)
        pdf.cell(col_width_2, row_height * spacing, txt="Details", border=1, fill=True)
        pdf.ln(row_height * spacing)

        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0, 0, 0)
        for row in prop_values:
            pdf.set_x(19)
            pdf.cell(col_width_1, row_height * spacing, txt=row[0], border=1)
            pdf.cell(col_width_2, row_height * spacing, txt=row[1], border=1)
            pdf.ln(row_height * spacing)
            
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        ############## LNG System ##################    
        #pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(19,55)
        
        column_head_det = [["Propulsion","Details"]]
        prop_values = machin_prop_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
    
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        ############## Other Machinery ##################    
        #pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(19,100)
        
    
        column_head_det = [["Type of Retrofit","Details"]]
        prop_values = machin_prop_table_4a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        ############## Machinery Electrical ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(19,20)

        column_head_det = [["ME Heavy Fuel Consumption","Details"]]
        prop_values = machin_prop_table_3a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
            
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        
        ############## LNG System ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"LNG System" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        
        column_head_det = [["LNG System Data","Details"]]
        prop_values = lng_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
    
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        ############## Other Machinery ##################    
        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(19,35)
        
    
        column_head_det = [[" M/E LNG Consumption","Details"]]
        prop_values = lng_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        
        
        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        #     ############## Machinery Electrical##################    


        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Machinery Electrical" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        
        column_head_det = [["Auxiliary Engine Summary","Details"]]
        prop_values = elec_mach_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
    
            
        pdf.set_xy(19,120)    
        column_head_det = [[" Auxiliary Engine","Details"]]
        prop_values = elec_mach_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        
        

        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        
        pdf.add_page()
        pdf.set_xy(19,20)    
        column_head_det = [[" Auxiliary Engine","Details"]]
        prop_values = elec_mach_table_3a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        pdf.set_xy(19,148.4)    
        column_head_det = [[" Auxiliary Engine","Details"]]
        prop_values = elec_mach_table_4a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
            
        
        #Page Number
        pdf.set_y(274.8)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        pdf.add_page()
        pdf.set_xy(19,20)    
        column_head_det = [[" Auxiliary Engine","Details"]]
        prop_values = elec_mach_table_5a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        pdf.set_xy(19,148.4)    
        column_head_det = [[" Auxiliary Engine","Details"]]
        prop_values = elec_mach_table_6a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
            
        
        #Page Number
        pdf.set_y(274.8)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        

        
        pdf.add_page()
        pdf.set_xy(19,20)    
        column_head_det = [["Emergency Generator","Details"]]
        prop_values = elec_mach_table_7a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        pdf.set_xy(19,148.4)    
        column_head_det = [["Shaft Generator","Details"]]
        prop_values = elec_mach_table_8a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
            
        
        #Page Number
        pdf.set_y(274.8)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        pdf.add_page()
        pdf.set_xy(19,20)    
        column_head_det = [["Turbo Generator","Details"]]
        prop_values = elec_mach_table_9a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)


        col_width_1 = pdf.get_string_width("Vessel Reefer Capacity") + 95  
        col_width_2 = pdf.get_string_width("Details") + 55  

        row_height = pdf.font_size

        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        pdf.cell(col_width_1, row_height * spacing, txt="Turbo Generator", border=1, fill=True)
        pdf.cell(col_width_2, row_height * spacing, txt="Details", border=1, fill=True)
        pdf.ln(row_height * spacing)

        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0, 0, 0)
        for row in prop_values:
            pdf.set_x(19)
            pdf.cell(col_width_1, row_height * spacing, txt=row[0], border=1)
            pdf.cell(col_width_2, row_height * spacing, txt=row[1], border=1)
            pdf.ln(row_height * spacing)

            
        pdf.set_xy(19,100)    
        column_head_det = [["Various Electrical Loads","Details"]]
        prop_values = elec_mach_table_10a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)


        col_width_1 = pdf.get_string_width("Various Electrical Loads") + 95  
        col_width_2 = pdf.get_string_width("Details") + 55  

        row_height = pdf.font_size

        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        pdf.cell(col_width_1, row_height * spacing, txt="Various Electrical Loads", border=1, fill=True)
        pdf.cell(col_width_2, row_height * spacing, txt="Details", border=1, fill=True)
        pdf.ln(row_height * spacing)

        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0, 0, 0)
        for row in prop_values:
            pdf.set_x(19)
            pdf.cell(col_width_1, row_height * spacing, txt=row[0], border=1)
            pdf.cell(col_width_2, row_height * spacing, txt=row[1], border=1)
            pdf.ln(row_height * spacing)
        pdf.set_xy(19,160)    
        column_head_det = [["Cold Ironing","Details"]]
        prop_values = elec_mach_table_11a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
                
            
        
        #Page Number
        pdf.set_y(274.8)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        #     ############## Machinery Electrical##################    


        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Other Machinery" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        
        column_head_det = [["Thruster","Details"]]
        prop_values = other_mach_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
    
            
        pdf.set_xy(19,220)    
        column_head_det = [["Anchor and Chain Cables","Details"]]
        prop_values = other_mach_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            
        
        

        #Page Number
        pdf.set_y(273)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        
        pdf.add_page()
        pdf.set_xy(19,20)    
        column_head_det = [["SOx Scrubber","Details"]]
        prop_values = other_mach_table_3a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width_1 = pdf.get_string_width("SOx Scrubber") + 105  
        col_width_2 = pdf.get_string_width("Details") + 55  

        row_height = pdf.font_size

        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        pdf.cell(col_width_1, row_height * spacing, txt="SOx Scrubber", border=1, fill=True)
        pdf.cell(col_width_2, row_height * spacing, txt="Details", border=1, fill=True)
        pdf.ln(row_height * spacing)

        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0, 0, 0)
        for row in prop_values:
            pdf.set_x(19)
            pdf.cell(col_width_1, row_height * spacing, txt=row[0], border=1)
            pdf.cell(col_width_2, row_height * spacing, txt=row[1], border=1)
            pdf.ln(row_height * spacing)
        #pdf.add_page()    
        pdf.set_xy(19,100)    
        column_head_det = [["Boiler","Details"]]
        prop_values = other_mach_table_4a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
            
        
        #Page Number
        pdf.set_y(274.8)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        
        pdf.add_page()
        pdf.set_xy(19,35)    
        column_head_det = [["Exhaust Gas Economiser","Details"]]
        prop_values = other_mach_table_5a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
                
        #Page Number
        pdf.set_y(274.8)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
        pdf.add_page()    
        pdf.set_xy(19,30)    
        column_head_det = [["Cargo Crane","Details"]]
        prop_values = other_mach_table_6a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
        
        #Page Number
        pdf.set_y(274.8)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
        
        #     ############## Machinery Electrical##################    


        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"Miscellaneous" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        
        column_head_det = [["Miscellaneous","Details"]]
        prop_values = Mis_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
            

        #Page Number
        pdf.set_y(274.8)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        
    #     ############## REEFER CARRYING CAPACITY##################    


        pdf.add_page()    
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(25,47,133)
        pdf.set_xy(15,20)
        
        pdf.multi_cell(80, 3,"REEFER CARRYING CAPACITY" ) 
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(25,47,133)
        
        pdf.set_xy(19,35)
        
        column_head_det = [["Original Reefer Sockets","Details"]]
        prop_values = reefer_capacity_table_1a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)
        pdf.set_xy(19,70)
        
        column_head_det = [["Current additional Reefer Sockets","Details"]]
        prop_values = reefer_capacity_table_2a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)  
            
            
        pdf.set_xy(19,120)
        
        column_head_det = [["Other","Details"]]
        prop_values = reefer_capacity_table_3a_object.values.tolist()
        pdf.set_font("Arial",'B', size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in column_head_det:
            
            pdf.set_text_color(255,255,255)
            pdf.set_fill_color(21,55,188)
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
            pdf.ln(row_height*spacing)
        pdf.set_font("Arial", size=7)
        pdf.set_text_color(0,0,0)
        col_width = pdf.w /2.25
        row_height = pdf.font_size
        for row in prop_values:
            pdf.set_x(19)
            for item in row:
                pdf.cell(col_width, row_height*spacing,
                        txt=item, border=1)
            pdf.ln(row_height*spacing)     
        

        #Page Number
        pdf.set_y(274.8)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R")
        

        pdf.output(pdf_name,'F')
        
    pdf_name = './documents/Vessel_details' + vessel_name + '.pdf'
    Vessel_details_pdf()  
    return FileResponse(path = pdf_name,filename=pdf_name)





@router.post('/api/v1/pdf/slipreport/vessels')
async def index(info : Request  ,vessel_name: str = None, parameter: str = None , graph_type: str = None , data : str = None , report_type : str = None,min_date:str = None,max_date:str = None):
    slip_data_ada = await info.json()
    import plotly.graph_objects as go
    import plotly.express as px
    import matplotlib.dates as mdates

    # input_para_slip={ "Parameter":[parameter],"Graph_Type":[ graph_type],"Data":[ data],"Vessel_name ":[vessel_name],"Report_Type":[ report_type],"start_date":[min_date],"end_date":[ max_date]}
    input_para_slip = {
    "Parameter": [parameter],
    "Graph_Type": [graph_type],
    "Data": [data],
    "Vessel_name": [vessel_name],
    "Report_Type": [report_type],
    "Date": ['2022-12-28']  
}

    input_data = pd.DataFrame.from_dict(input_para_slip)
    input_data



    if data == "VRS Data":
        types = "(VRS)"
        Slip_data = pd.DataFrame.from_dict(
            slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["data"])
    
        selected_period_deviation_vrs = str(
            (slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()][
                "metadata"]))
        slip_vessel_anno_vrs = pd.DataFrame.from_dict(
            slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()][
                "annotation"])
        daily_avg_slip_vrs = str(slip_vessel_anno_vrs["average_hydro_slip"].values[0])
        slip_vessel_anno_vrs["hyd_slip"].values[0]
        slip_vessel_anno_vrs["hyd_slip"].values[1]
    
        slip_vessel_meta_data = pd.DataFrame.from_dict(
            slip_data_ada["data"]["metadata"][input_data["Parameter"].item()])
        benchmark_avg_slip_vrs = str(slip_vessel_meta_data["average_slip"].values[0])
        benchmark_period = slip_vessel_meta_data["selection_period"].values[0]
        benchmark_keydate = slip_vessel_meta_data["key_dates"].values[0]
        prop_pitch = str(slip_vessel_meta_data["propeller_pitch"].values[0])
    
        Slip_data_vrs = pd.DataFrame.from_dict(
            slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["data"])
        if input_data["Report_Type"].item() == "daily":
            Slip_data["date"] = pd.to_datetime(Slip_data["date"], format='%d %b %Y')
            Slip_data['date'] = Slip_data['date'].dt.strftime('%d-%m-%Y')
        elif input_data["Report_Type"].item() == "monthly":
            pass
    
        plt.figure(figsize=(12, 8))
    
        plt.scatter(Slip_data['date'], Slip_data['value'], color='brown', label=Slip_data["type"].values[0])
    
        if input_data["Graph_Type"].item() == "Line":
            plt.plot(Slip_data['date'], Slip_data['value'], marker='o', markersize=7, color='brown',
                    label=Slip_data["type"].values[0])
        elif input_data["Graph_Type"].item() == "Scatter":
            plt.scatter(Slip_data['date'], Slip_data['value'], color='brown', label=Slip_data["type"].values[0])
    
        y_value1_vrs = slip_vessel_anno_vrs["benchmark"].values[0]
        y_value1_vrs=float(y_value1_vrs)
        plt.axhline(y=y_value1_vrs, xmin=0, xmax=1, color='yellow', linewidth=4, label='Average Benchmark Slip')
    
        y1_vrs = slip_vessel_anno_vrs["hyd_slip"].values[0]
        plt.axhline(y=y1_vrs, color='green',linestyle='--', linewidth=2, label='Fitted Hydraulic Slip')

        plt.tight_layout()
        plt.xlabel('Date')
        plt.xticks(rotation=-45)
        plt.ylabel('% Slip')
        
        plt.legend(loc='upper right')
        plt.gca().tick_params(axis='x', rotation=-45)
        # Calculate dynamic y-axis limit
        max_value = Slip_data['value'].max()
        plt.ylim(0, max_value + max_value * 0.2)  # Add 10% padding above the max value

        # Set y-ticks dynamically based on max_value
        plt.yticks(range(0, int(max_value + max_value * 0.2), 2)) 
        
        plt.savefig('./images/slip_report_vessel.png', bbox_inches='tight')
        #plt.show()

    elif data == 'EGOSHIP Data':
        types = '(ADA)'
        Slip_data = pd.DataFrame.from_dict(
        slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["data"])
        selected_period_deviation_ego = str(
            (slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()][
                "metadata"]))
        slip_vessel_anno_ego = pd.DataFrame.from_dict(
            slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()][
                "annotation"])
        daily_avg_slip_ego = str(slip_vessel_anno_ego["average_hydro_slip"].values[0])
        slip_vessel_anno_ego["hyd_slip"].values[0]
        slip_vessel_anno_ego["hyd_slip"].values[1]
    
        slip_vessel_meta_data = pd.DataFrame.from_dict(
            slip_data_ada["data"]["metadata"][input_data["Parameter"].item()])
        benchmark_avg_slip_ada = str(slip_vessel_meta_data["average_slip"].values[0])
        benchmark_period = slip_vessel_meta_data["selection_period"].values[0]
        benchmark_keydate = slip_vessel_meta_data["key_dates"].values[0]
        prop_pitch = str(slip_vessel_meta_data["propeller_pitch"].values[0])
    
        Slip_data_ego = pd.DataFrame.from_dict(
            slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["data"])
        if input_data["Report_Type"].item() == "daily":
            Slip_data["date"] = pd.to_datetime(Slip_data["date"], format='%d %b %Y')
            Slip_data['date'] = Slip_data['date'].dt.strftime('%d-%m-%Y')
        elif input_data["Report_Type"].item() == "monthly":
            pass
    

        plt.figure(figsize=(12, 8))
        plt.scatter(Slip_data['date'], Slip_data['value'], color='brown', label=Slip_data["type"].values[0])
    
        if input_data["Graph_Type"].item() == "Line":
            plt.plot(Slip_data['date'], Slip_data['value'], marker='o', markersize=7, color='brown',
                    label=Slip_data["type"].values[0])
        elif input_data["Graph_Type"].item() == "Scatter":
            plt.scatter(Slip_data['date'], Slip_data['value'], color='brown', label=Slip_data["type"].values[0])
    
        y_value1_ego = slip_vessel_anno_ego["benchmark"].values[0]
        y_value1_ego=float(y_value1_ego)
        plt.axhline(y=y_value1_ego, xmin=0, xmax=1, color='yellow', linewidth=2, label='Average Benchmark Slip')
    
        y1_ego = slip_vessel_anno_ego["hyd_slip"].values[0]
        plt.axhline(y=y1_ego, color='green',linestyle='--', linewidth=2, label='Fitted Hydraulic Slip')

        plt.tight_layout()
        plt.xlabel('Date')
        plt.xticks(rotation=-45)
        plt.ylabel('% Slip')
        plt.legend(loc='upper right')
        plt.gca().tick_params(axis='x', rotation=-45)

        # Calculate dynamic y-axis limit
        max_value = Slip_data['value'].max()
        plt.ylim(0, max_value + max_value * 0.2)  # Add 10% padding above the max value

        # Set y-ticks dynamically based on max_value
        plt.yticks(range(0, int(max_value + max_value * 0.2), 2))     # plt.savefig('slip_report_vessel.png') 

        
        plt.savefig('./images/slip_report_vessel.png', bbox_inches='tight')
        #plt.show()

        

    elif data == 'data_comparison':
        types = ''
        selected_period_deviation_vrs = str(
            (slip_data_ada["data"]["VRS DATA"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["metadata"]))
        Slip_data_vrs = pd.DataFrame.from_dict(
            slip_data_ada["data"]['VRS DATA']["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["data"])
        slip_vessel_anno_vrs = pd.DataFrame.from_dict(
            slip_data_ada["data"]['VRS DATA']["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["annotation"])
        daily_avg_slip_vrs = str(slip_vessel_anno_vrs["average_hydro_slip"].values[0])
        y1_vrs = slip_vessel_anno_vrs["hyd_slip"].values[0]
        y2_vrs = slip_vessel_anno_vrs["hyd_slip"].values[1]

        try:
            Slip_data_ego = pd.DataFrame.from_dict(
                slip_data_ada["data"]["EGOSHIP DATA"]["chartData"][input_data["Parameter"].item()][
                    input_data["Report_Type"].item()]["data"])
            selected_period_deviation_ego = str(
                (slip_data_ada["data"]["EGOSHIP DATA"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["metadata"]))
            slip_vessel_anno_ego = pd.DataFrame.from_dict(
                slip_data_ada["data"]["EGOSHIP DATA"]["chartData"][input_data["Parameter"].item()][
                    input_data["Report_Type"].item()]["annotation"])
            daily_avg_slip_ego = str(slip_vessel_anno_ego["average_hydro_slip"].values[0])
            y1_ego = slip_vessel_anno_ego["hyd_slip"].values[0]
            y2_ego = slip_vessel_anno_ego["hyd_slip"].values[1]
            ego_ship = "Yes"
        except:
            selected_period_deviation_ego = ''
            slip_vessel_anno_ego = pd.DataFrame()
            Slip_data_ego = pd.DataFrame()
            ego_ship = "No"
            daily_avg_slip_ego = ''
            y1_ego = 0
            y2_ego = 0

        # Metadata and benchmark data
        slip_vessel_meta_data = pd.DataFrame.from_dict(
            slip_data_ada["data"]["metadata"][input_data["Parameter"].item()])
        benchmark_avg_slip_vrs = str(slip_vessel_meta_data["average_slip"].values[0])
        benchmark_avg_slip_ada = str(slip_vessel_meta_data["average_slip_ada"].values[0])
        benchmark_period = slip_vessel_meta_data["selection_period"].values[0]
        benchmark_keydate = slip_vessel_meta_data["key_dates"].values[0]
        prop_pitch = str(slip_vessel_meta_data["propeller_pitch"].values[0])

        # Prepare Slip Data VRS
        if report_type=='daily':
            Slip_data_vrs['date'] = pd.to_datetime(Slip_data_vrs['date'], format='%d %b %Y', errors='coerce')
            Slip_data_vrs = Slip_data_vrs.sort_values(by='date')
        
            if not Slip_data_ego.empty:
                Slip_data_ego['date'] = pd.to_datetime(Slip_data_ego['date'], format='%d %b %Y')
                Slip_data_ego = Slip_data_ego.sort_values(by='date')

        else:
            Slip_data_vrs['date'] = pd.to_datetime(Slip_data_vrs['date'], format='%b %Y', errors='coerce')
            Slip_data_vrs = Slip_data_vrs.sort_values(by='date')
        
            if not Slip_data_ego.empty:
                Slip_data_ego['date'] = pd.to_datetime(Slip_data_ego['date'], format='%b %Y')
                Slip_data_ego = Slip_data_ego.sort_values(by='date')

        # Plotting
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot VRS data
        ax.plot(Slip_data_vrs['date'], Slip_data_vrs['value'], 'o-', color='green', label="Hydrodynamic Slip(VRS)")

        # Plot ADA data if available
        if ego_ship == "Yes" and not Slip_data_ego.empty:
            ax.plot(Slip_data_ego['date'], Slip_data_ego['value'], 'o-', color='red', label="Hydrodynamic Slip(ADA)")

        # Plot Average Benchmark Slip for VRS data
        ax.axhline(y=slip_vessel_anno_vrs["benchmark"].values[0], color='green', linestyle='-', linewidth=2, label='Average Benchmark Slip (VRS)')

        # Plot Average Benchmark Slip for ADA data if available
        if ego_ship == "Yes" and not slip_vessel_anno_ego.empty:
            ax.axhline(y=slip_vessel_anno_ego["benchmark"].values[0], color='red', linestyle='-', linewidth=2, label='Average Benchmark Slip (ADA)')

        # Plot Fitted Hydraulic Slip for VRS data
        ax.plot([Slip_data_vrs['date'].min(), Slip_data_vrs['date'].max()], [y1_vrs, y2_vrs], color='green', linestyle='--', linewidth=2, label='Fitted Hydraulic Slip (VRS)')

        # Plot Fitted Hydraulic Slip for ADA data if available
        if ego_ship == "Yes" and not slip_vessel_anno_ego.empty:
            ax.plot([Slip_data_ego['date'].min(), Slip_data_ego['date'].max()], [y1_ego, y2_ego], color='red', linestyle='--', linewidth=2, label='Fitted Hydraulic Slip (ADA)')

        # Formatting and labels
        #ax.set_title('Slip Data Comparison')
        ax.set_xlabel('Date')
        ax.set_ylabel('% Slip')
        if report_type == 'daily':
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))  # For daily reports
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))  # Set major ticks for each week
            ax.xaxis.set_minor_locator(mdates.DayLocator())  # Set minor ticks for each day
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.tick_params(axis='x', rotation=45)
        #ax.grid(True)

        # Legend
        ax.legend(loc='upper right')

        # Show plot
        plt.tight_layout()

        plt.savefig('./images/slip_report_vessel.png', bbox_inches='tight')
        #plt.show()

    def slip_vrs_ada(spacing=6):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 20)

       
        pdf.image(msc_logo_path,160,8,w=30)

    #Cell postion from left side
        pdf.set_xy(80, 15)
        pdf.set_text_color(25, 47, 133)
        
        pdf.cell(150, 60, 'Slip Report')
        pdf.set_text_color(0, 0, 0)
        
        # Horizontal line
        pdf.set_line_width(1)
        pdf.line(10, 50, 199, 50)
        
        # Content setup
        pdf.set_font('Arial', "", 12)
        pdf.set_xy(10, 55)
        
        # Debug information
        selected_deviation = selected_period_deviation_ego if data == "EGOSHIP Data" else selected_period_deviation_vrs
        daily_avg_slip = daily_avg_slip_ego if data == "EGOSHIP Data" else daily_avg_slip_vrs
        benchmark_slip = benchmark_avg_slip_ada if data == "EGOSHIP Data" else benchmark_avg_slip_vrs
        # print(f"Data type: {data}\nSelected period deviation: {selected_deviation}\nDaily average slip: {daily_avg_slip}\nBenchmark slip: {benchmark_slip}")
            # Determine avg_slip_label based on report_type

        if report_type == 'daily':

            avg_slip_label = "Daily Average Slip"

        elif report_type == 'monthly':

            avg_slip_label = "Monthly Average Slip"

        else:

            avg_slip_label = "Average Slip"  # Default label if none specified

 
        # Basic info
        info = [
            f"Vessel Name: {vessel_name}",
            f"Monitoring Period: {min_date} to {max_date}",
            f"Propeller Pitch: {prop_pitch}",
            f"Benchmark keydate: {benchmark_keydate}",
            f"Benchmark Period: {benchmark_period}"
        ]
        for line in info:
            pdf.cell(0, spacing, line, ln=True)
        
        # Slip data
        if data in ["EGOSHIP Data", "VRS Data"]:
            try:
                deviation = selected_period_deviation_ego if data == "EGOSHIP Data" else selected_period_deviation_vrs
                avg_slip = daily_avg_slip_ego if data == "EGOSHIP Data" else daily_avg_slip_vrs
                bench_slip = benchmark_avg_slip_ada if data == "EGOSHIP Data" else benchmark_avg_slip_vrs
                slip_type = "SOG" if parameter == "sog" else "STW"
                pdf.cell(0, spacing, f"Deviation for Selected Period: {deviation}%", ln=True)
                pdf.cell(0, spacing, f"{report_type.capitalize()} Average Slip ({slip_type}): {avg_slip}%", ln=True)
                pdf.cell(0, spacing, f"Average Benchmark Slip {types}: {bench_slip}", ln=True)
            except Exception as e:
                print(f"Error in {data} data section: {e}")
        
        elif data == "data_comparison":
            try:
                pdf.multi_cell(0, spacing, f"Deviation for Selected Period (VRS): {selected_period_deviation_vrs}%")
                if ego_ship == "Yes":
                    pdf.multi_cell(0, spacing, f"Deviation for Selected Period (ADA): {selected_period_deviation_ego}%")
                
                pdf.multi_cell(0, spacing, f"{avg_slip_label} (STW) (VRS): {daily_avg_slip_vrs}%")
                if ego_ship == "Yes":
                    pdf.multi_cell(0, spacing, f"{avg_slip_label} (STW) (ADA): {daily_avg_slip_ego}%")
                
                pdf.multi_cell(0, spacing, f"Average Benchmark Slip (VRS): {benchmark_avg_slip_vrs}")
                if ego_ship == "Yes":
                    pdf.multi_cell(0, spacing, f"Average Benchmark Slip (ADA): {benchmark_avg_slip_ada}")
            except Exception as e:
                print(f"Error in data comparison section: {e}")
        
        # Horizontal line after data and graph section
        pdf.ln(spacing)
        pdf.set_line_width(.5)
        pdf.line(8, 120, 197, 120)
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(25, 47, 133)
        pdf.cell(0, 50, 'Slip Report', ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', "", 12)
        
        # Add graph
        pdf.image("./images/slip_report_vessel.png", 12, pdf.get_y() + 6, w=190, h=120)
        pdf_name = vessel_name+'_MSC_Slip_report_vessel_month_without_api.pdf'
        pdf.output('./documents/' + pdf_name, 'F')

    pdf_name = vessel_name+'_MSC_Slip_report_vessel_month_without_api.pdf'
    slip_vrs_ada()


    return FileResponse(path = './documents/'+pdf_name,filename=pdf_name)

@router.post('/api/v1/pdf/vessels/vpq')
async def index(info : Request):
    data = await info.json()
    
    data = data['data']
    vessel_name = list(filter(lambda x: x['attribute_id'] == 61, data))[0]['value']


    class PDFWithLine(FPDF):
        def header(self):
            # Add navigation bar
            self.set_font('Arial', 'B', 12)
            logo_path = './images/logo/logo.png'  # Replace with the path to your logo image
            self.image(logo_path, 10, 8, 50)
            self.set_text_color(128, 128, 128)
            self.cell(0, 6, vessel_name + ' - VPQ', 0, 1, 'C')  # Add text to the navigation bar
            self.cell(0, 2, 'Page %s' % self.page_no(), 0, 0, 'R')  # Add page number in the top right corner
            
            self.ln(10)  # Add some space below the navigation bar

        def footer(self):
            # Add a line below the navigation bar
            self.set_draw_color(0, 0, 0)  # Set draw color to black
            self.line(10, 25, self.w - 10, 25) 
            self.line(10, self.h - 15, self.w - 10, self.h - 15)  # Draw a line in the footer
            self.cell(3)
            # Add page number
            self.set_font('Arial', '', 10)

            self.ln(10)  # Move to the next line
            self.set_text_color(128, 128, 128)
            self.set_font("", style="I")
            
            self.cell(0, 10, 'PDF Generated on '+str(datetime.now().date()), 0, 0, 'L')
        
    # Create PDF object
    pdf = PDFWithLine()
    pdf.add_page()

    # Set font for the content
    pdf.set_font("Arial", style='B', size=14)  # Bold, size 16

    # Add bold, centered, and larger text
    content_text = "VESSEL DESCRIPTION FORM"
    pdf.cell(0, 20, content_text, ln=True, align='C')

    # Output PDF

    # Set font for the content

    # JSON object to loop through

    # Custom line height and maximum lines per page
    line_height = 3
    # Variable to keep track of lines printed on the current page


    def loop_data(looping_data):
        for key, values in looping_data.items():
            value = list(filter(lambda x: x['attribute_id'] == values, data))
            if not value:
                value = 'No Data Found' 
            else:
                unit = value[0]['unit']
                value = value[0]['value']
                if not value or value == '':
                    value = 'No Data Found'
                else:
                    value = value + ' ' + unit

            pdf.cell(20)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("")

            pdf.set_font("Arial", size=9)  # Adjust the font size as needed
            pdf.set_font("") 
            # Print key and value with adjusted positions
            pdf.multi_cell(90, line_height, key)  # Print key with specified width

            # Adjust the position for the next cell (same line as the key)
            pdf.set_xy(120, pdf.get_y() - line_height)
            remaining_width = pdf.w - pdf.get_x() - 5
            
            if value == 'No Data Found':
                pdf.set_font("", style="I")
                pdf.set_text_color(255, 0, 128)

            pdf.multi_cell(remaining_width, line_height, value)  # Print value
            pdf.set_text_color(0, 0, 0)
            pdf.ln()  # Move to the next line


    info_data = {'VSL PHYSICAL INFO': vsl_info, 'MAIN ENGINE': main_engine_info, 'PROPELLER': propeller_info, 'M/E Consumption at various Engine Load and Speed': me_cons_info, 'VARIOUS ELECTRICAL LOADS': electrical_loads_info, 'Auxiliary Oil Fired Boiler': aux_oil_fired_info, 'THRUSTER': thruste_infor, 'ANCHOR & CHAIN CABLES': anchor_info, 'TANK CAPACITIES': tank_capacities_info, 'VESSEL EQUIPMENT': vessel_equipment_info, 'VESSEL INTAKES & GENERAL DISTRIBUTION': vessel_intakes_info, 'GENERAL DISTRIBUTION 20': general_distribution_20_info, 'GENERAL DISTRIBUTION 40': general_distribution_40_info, 'GENERAL DISTRIBUTION 40HC': general_distribution_40hc_info, 'GENERAL DISTRIBUTION 45HC': general_distribution_45hc, 'VESSEL REEFER CAPACITY': vessel_reefer_capacity, 'MISCELLANEOUS': miscellaneous_info, 'COMMUNICATION': communication_info, 'VESSEL PLANS': vessel_plans_info, 'AUX ENGINE CONSUMPTIONS': aux_engine_consumptions_info, 'AUXILIARY ENGINE 1': auxiliary_engine_1_info, 'AUXILIARY ENGINE 2': auxiliary_engine_2_info, 'AUXILIARY ENGINE 3': auxiliary_engine_3_info, 'AUXILIARY ENGINE 4': auxiliary_engine_4_info, 'AUXILIARY ENGINE 5': auxiliary_engine_5_info}

    for i, j in info_data.items():
        pdf.set_font("Arial", style='B', size=10)  # Bold, size 12
        pdf.cell(20)
        pdf.cell(30, line_height, i, 0, 0, 'L')
        pdf.ln() 
        pdf.ln() 
        loop_data(j)

    pdf_name = vessel_name + ' - VPQ'
    pdf.output('./documents/'+pdf_name)
    return FileResponse(path = './documents/'+pdf_name,filename=pdf_name)




# -----------------------------------------EEXI-------------------------------------------------------------------
@router.post('/api/v1/pdf/eexi_report_pdf/{imo}')
async def index(info:Request,imo:str=None,vessel_name:str =None,type:str =None,deadweight:int=None):
    x_deadweight= deadweight
    
    s = await info.json()
    
    # print(s['data'])
    graph_data  = s['data']['graphData']
    general_info = s['data']['tabData']['attributeValues']
    attributes_data = s['data']['tabData']['attributes']

    df1 = pd.DataFrame(s['data']['tabData']['attributes'])
    df1['attribute_id'] = df1['id'].values
    df2 = pd.DataFrame(s['data']['tabData']['attributeValues'])
    df3 = pd.merge(left = df1, right = df2, on = 'attribute_id', how = 'outer')
    df4  = df3[[  'attribute_id',  'imo', 'name', 'value','unit_x' ]]
    df4['value_unit'] = df4['value'].fillna('') + " " + df4['unit_x'].fillna('')
    mydict = dict(zip(zip(df4['name'], df4['attribute_id']), df4['value_unit']))
    def create_info_dataframe(attributeList, df4, mydict):
        selected_data = {}
        attribute_names = [key[0] for key in mydict.keys() if isinstance(key, (list, tuple)) and key]

        for attribute_id in attributeList:
            if attribute_id in df4['attribute_id'].values:
                attribute_name = df4[df4['attribute_id'] == attribute_id]['name'].iloc[0]
                if attribute_name in attribute_names:
                    value_unit = mydict[(attribute_name, attribute_id)]
                    selected_data[attribute_name] = value_unit

        info_df = pd.DataFrame(selected_data.items(), columns=['Particulars', 'Details'])
        return info_df

    # Define your lists and DataFrames here
    attributeList_general = [65, 1, 168, 62, 4]
    General_info = create_info_dataframe(attributeList_general, df4, mydict)

    attributeList_vessel = [14, 15, 16, 18, 83, 8]
    Principal_particulars = create_info_dataframe(attributeList_vessel, df4, mydict)

    attributeList_me = [147, 916, 915, 914, 333, 917, 918, 919, 149, 926, 927, 928, 576, 929, 930, 931, 721, 959, 960, 961]
    ME = create_info_dataframe(attributeList_me, df4, mydict)

    attributeList_ae = [153, 185, 188, 723, 724, 201, 203, 206, 725, 726, 279, 282, 285, 727, 728, 369, 370, 373, 729, 730, 375, 376, 379, 731, 732]
    AE = create_info_dataframe(attributeList_ae, df4, mydict)

    # Process selected attributes
    selected_attributes = ['required_eexi', 'attained_eexi', 'Maximum Speed']
    selected_data = {attr: graph_data.get(attr) for attr in selected_attributes if attr in graph_data}
    df = pd.DataFrame([selected_data]).transpose().reset_index()
    df.columns = ['Particulars', 'Details']

    # Process ship speed data
    selected_attributes = ['Maximum Speed']
    selected_data = {}
    for i in attributes_data:
        if i['name'] in selected_attributes:
            filtered_values = [x for x in general_info if x['attribute_id'] == i['id']]
            if filtered_values:
                value = filtered_values[0]['value']
                unit = i['unit']
                selected_data[i['name']] = f"{value} {unit}"
    ss = pd.DataFrame(selected_data.items(), columns=['Particulars', 'Details'])

    # Combine DataFrames
    combined_df = pd.concat([df, ss], ignore_index=True)

    # Define 'Particulars' for EEXI and speed
    combined_df.loc[combined_df['Particulars'] == 'required_eexi', 'Particulars'] = 'Required EEXI'
    combined_df.loc[combined_df['Particulars'] == 'attained_eexi', 'Particulars'] = 'Attained EEXI'
    combined_df.loc[combined_df['Particulars'] == 'Maximum Speed', 'Particulars'] = 'Ship Speed'
    
    # Calculate EEXI Result

    required_eexi = combined_df.loc[combined_df['Particulars'] == 'Required EEXI', 'Details'].values[0]

    attained_eexi = combined_df.loc[combined_df['Particulars'] == 'Attained EEXI', 'Details'].values[0]
    
    required_eexi_str = str(required_eexi)
    attained_eexi_str = str(attained_eexi)
      
    # Calculate EEXI Result
    required_eexi = combined_df.loc[combined_df['Particulars'] == 'Required EEXI', 'Details'].values[0]
    attained_eexi = combined_df.loc[combined_df['Particulars'] == 'Attained EEXI', 'Details'].values[0]
    eexi_result = 'PASS' if (attained_eexi is not None and required_eexi is not None and attained_eexi <= required_eexi) else 'FAIL'

    new_row = pd.DataFrame({'Particulars': ['EEXI Result'], 'Details': [eexi_result]})
    combined_df = pd.concat([combined_df, new_row], ignore_index=True)

    # Plotting
    d = pd.DataFrame.from_dict(s['data']['graphData']['graph_data'])
    #d = d.dropna(subset=["value"])

    d = d.dropna(subset=["year", "value"])
    d["year"] = pd.to_numeric(d["year"], errors='coerce')
    d["value"] = pd.to_numeric(d["value"], errors='coerce')

    # Define the DWT and value that cause the spike
    x_deadweight = int(deadweight)
    dwt_to_exclude = x_deadweight
    value_to_exclude = required_eexi

    # Filter the DataFrame to exclude the spike point for the line plot
    d_filtered = d[~((d["year"] == dwt_to_exclude) & (d["value"] == value_to_exclude))]

    fig, ax = plt.subplots(figsize=(10, 8))

    # Combine annotations for required, attained EEXI, and deadweight
    if attained_eexi_str is not None and required_eexi_str is not None and x_deadweight is not None:
        ax.annotate(
            f'Required EEXI: {required_eexi_str}\nAttained EEXI: {attained_eexi_str}\nDeadweight: {x_deadweight} MT',
            xy=(x_deadweight, float(attained_eexi_str)),  # Position annotation at attained EEXI point
            xytext=(-20, 10),  # Offset for readability
            textcoords='offset points',
            fontsize=12,
            color='black'
        )

    # Plot the Required EEXI values, with the spike removed
    ax.plot(d_filtered["year"].values, d_filtered["value"].values, color='blue', linewidth=2, label='Required EEXI')

    # Plot the excluded point (spike) separately with annotation
    ax.plot(dwt_to_exclude, value_to_exclude, marker='o', markersize=10, color='magenta', label='Attained EEXI')

    # Add labels and finalize plot
    ax.set_xlabel('Year (DWT)')
    ax.set_ylabel('EEXI Value')
    ax.legend()
    ax.grid(False)
    plt.tight_layout()
    # plt.savefig('./images/EEXI.png', bbox_inches='tight')
    # plt.show()
        


    # Additional Plot
    data = s['data']['graphData']['eexi_calc']
    if isinstance(data, dict):
        data = [data]
    eng_details = pd.DataFrame(data)

    mcr_pwr = eng_details['mcrpower'].iloc[0]
    mcr_rpm = eng_details['mcrrpm'].iloc[0]
    new_mcr_pwr = eng_details['newmcrpower'].iloc[0]
    new_mcr_rpm = eng_details['newmcrrpm'].iloc[0]

    mcr_pwr = str(mcr_pwr)
    mcr_rpm = str(mcr_rpm)
    new_mcr_pwr = str(new_mcr_pwr)
    new_mcr_rpm = str(new_mcr_rpm)  

    plt.savefig('./images/EEXI.png', bbox_inches='tight')

    plt.clf()

    from fpdf import FPDF

    spacing=3
    pdf = FPDF()
        #***********************************************  page 1 **********************************************************#
    

    pdf.add_page()
    #pdf.image(oceanix_logo_path,15,15,w=35)
    pdf.image(msc_logo_path,160,12,w=25)
    pdf.set_font('Arial', 'B', 18)

    pdf.set_xy(93,15)
    pdf.set_text_color(25,47,133)
    pdf.cell(175,55,"EEXI",ln=True) 
    pdf.set_text_color(0,0,0)
    pdf.set_line_width(0.5)
    pdf.line(10, 50, 190, 50)
    #pdf.set_line_width(0.2)
    pdf.set_font('Arial', "",14)
    pdf.set_xy(10,55)
    #pdf.multi_cell(80,14.5,"Report Date :"+" "+ report_prepared_date, align='R')


    pdf.cell(10,2, "Vessel Name :"+" "+vessel_name,ln=True)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(25,47,133)
    pdf.line(10, 60, 190, 59)
    pdf.set_line_width(0.5)

    pdf.image('./images/EEXI.png',23,70,w=160,h=105)

    pdf.set_xy(15,185)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(25,47,133)
    pdf.multi_cell(80, 3,"Result" ) 
    column_head_det = [["Result","Details"]]
    pdf.set_xy(15,195)
    prop_values = combined_df.values.tolist()
    pdf.set_font("Arial",'B', size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    for row in column_head_det:

        pdf.set_text_color(255,255,255)
        pdf.set_fill_color(21,55,188)
        for item in row:
            pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
        pdf.ln(row_height*spacing)
    pdf.set_font("Arial", size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    for row in prop_values:
        pdf.set_x(15)
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                    txt=str(item), border=1)
        pdf.ln(row_height*spacing) 


    pdf.set_xy(15,250)
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.set_font('Arial', 'B', 7)  # Bold text with slightly bigger font size
    cell_width = 40  # Adjusted cell width for uniformity
    cell_height = 12  # Adjusted cell height for slightly bigger text

    # Cells with a small space between them
    pdf.cell(cell_width, cell_height, "Engine Power: " + mcr_pwr + ' kW', border=1, fill=True,align='C')
    pdf.cell(5, cell_height, "", border=0)  # Spacer cell
    pdf.cell(cell_width, cell_height, "RPM: " + mcr_rpm, border=1, fill=True,align='C')
    pdf.cell(5, cell_height, "", border=0)  # Spacer cell
    pdf.cell(cell_width, cell_height, "Engine Power Limit: " + new_mcr_pwr + ' kW', border=1, fill=True,align='C')
    pdf.cell(5, cell_height, "", border=0)  # Spacer cell
    pdf.cell(cell_width, cell_height, "RPM Limit: " + new_mcr_rpm, border=1, fill=True,align='C')

    pdf.ln(cell_height + 5)    


    pdf.add_page()

    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(25,47,133)
    pdf.set_x(15)
    pdf.multi_cell(50, 40,"General Information" ) 
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(25,47,133)

    pdf.set_xy(15,40)
    column_head_det = [["Particulars","Details"]]
    prop_values = General_info.values.tolist()
    pdf.set_font("Arial",'B', size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    for row in column_head_det:

        pdf.set_text_color(255,255,255)
        pdf.set_fill_color(21,55,188)
        for item in row:
            pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
        pdf.ln(row_height*spacing)
    pdf.set_font("Arial", size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    for row in prop_values:
        pdf.set_x(15)
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                    txt=str(item), border=1)
        pdf.ln(row_height*spacing)

    pdf.set_x(15) 
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(25,47,133)
    pdf.multi_cell(85, 50,"Principal Particulars" ) 
    column_head_det = [["Particulars","Details"]]

    prop_values = Principal_particulars.values.tolist()
    pdf.set_font("Arial",'B', size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    pdf.set_xy(15,120)
    for row in column_head_det:

        pdf.set_text_color(255,255,255)
        pdf.set_fill_color(21,55,188)
        for item in row:
            pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
        pdf.ln(row_height*spacing)
    pdf.set_font("Arial", size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    for row in prop_values:
        pdf.set_x(15)
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                    txt=item, border=1)
        pdf.ln(row_height*spacing)     
    pdf.set_xy(15,180) 
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(25,47,133)
    pdf.multi_cell(80, 20,"Main Engine" ) 
    column_head_det = [["Main Engine","Details"]]
    prop_values = ME.values.tolist()
    pdf.set_xy(15,200)
    pdf.set_font("Arial",'B', size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    for row in column_head_det:

        pdf.set_text_color(255,255,255)
        pdf.set_fill_color(21,55,188)
        for item in row:
            pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
        pdf.ln(row_height*spacing)
    pdf.set_font("Arial", size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    for row in prop_values:
        pdf.set_x(15)
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                    txt=str(item), border=1)
        pdf.ln(row_height*spacing)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(25,47,133)
    pdf.set_xy(15,20)
    pdf.multi_cell(80, 3,"Auxiliary engine" ) 
    column_head_det = [["Auxiliary Engine","Details"]]
    prop_values = AE.values.tolist()
    pdf.set_xy(15,33)
    pdf.set_font("Arial",'B', size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    for row in column_head_det:
        pdf.set_text_color(255,255,255)
        pdf.set_fill_color(21,55,188)
        for item in row:
            pdf.cell(col_width, row_height*spacing,txt=item, border=1,fill=True)
        pdf.ln(row_height*spacing)
    pdf.set_font("Arial", size=7)
    pdf.set_text_color(0,0,0)
    col_width = pdf.w /2.25
    row_height = pdf.font_size
    for row in prop_values:
        pdf.set_x(15)
        for item in row:
            pdf.cell(col_width, row_height*spacing,
                    txt=str(item), border=1)
        pdf.ln(row_height*spacing)    

    
    pdf.set_y(273)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 

    # pdf.output('eexi.pdf', 'F')

    pdf_name = vessel_name + ' - EEXI'
    pdf.output('./documents/'+pdf_name)
    return FileResponse(path = './documents/'+pdf_name,filename=pdf_name)


@router.post('/api/v1/pdf/ae_missing_vessel_report_pdf/{fleet}')
async def index(info:Request,fleet:str=None,period:str =None,fleet_name:str =None,count:str=None):
    # import plotly.express as px
    # import plotly.io as pio
    s = await info.json()

    df=pd.DataFrame(s['data']['tableData'])
    df.rename(columns={'fleet':'FLEET','class':'CLASS','missing_vessels':'MISSING VESSELS','imo':"IMO",'engine_maker':"ENGINE MAKER"},inplace=True)

    df.insert(0, 'SL No.', range(1, len(df) + 1))
    chart=pd.DataFrame(s['data']['chartData'])
    labels = chart['type']
    sizes = chart['value']
    colors = ['green', 'blue']  # Custom colors: green and blue
    # colors = sns.color_palette('muted', len(labels))  # Seaborn-like colors

    # Apply Seaborn style
    sns.set(style="whitegrid")

    # Create a pie chart
    plt.figure(figsize=(7, 7))
    plt.pie(sizes, labels=labels, colors=colors, autopct=lambda p: f'{int(p * sum(sizes) / 100)}', startangle=90)

    # Save the image with the adjusted size
    plt.savefig('./images/electrical_graph_fleet.png', bbox_inches='tight')
    # pio.write_image(fig, './images/electrical_graph_fleet.png', scale=2)
    # plt.savefig('./images/electrical_graph_fleet.png', bbox_inches='tight')

    # fig.show()

    #Frontend
    # fleet='fleet1'
    # period='month'
    # fleet_name='fleet 2'
    # count='34'
    pdf = FPDF()
    spacing=3
    #*********************************************** 1 page **********************************************************#
    pdf.add_page()
    pdf.set_font('Arial', 'B', 18)

    # pdf.image(oceanix_logo_path,15,15,w=35)
    pdf.image(msc_logo_path,160,8,w=30)

    #Cell postion from left side
    pdf.set_xy(55,10)
    pdf.set_text_color(25,47,133)
    pdf.cell(175, 60, 'Monthly Missing Electrical Report')
    pdf.set_text_color(0,0,0)
    pdf.set_line_width(1)
    pdf.line(10, 50, 199, 50)
    pdf.set_line_width(0.2)
    pdf.set_font('Arial', "",13)
    pdf.set_xy(10,55)

    pdf.cell(10, 2, fleet_name,ln=True)

    pdf.cell(10, 13, "Month :"+" "+period,ln=True)
    if fleet_name=='All Fleets':
        pdf.cell(10, 5, "Total Vessels in :"+" "+count,ln=True)
    else:
        pdf.cell(10, 5, "Total Vessels in " + fleet_name+" :"+" "+count,ln=True)
    pdf.line(10, 80, 199, 80)
    pdf.image("./images/electrical_graph_fleet.png",60,85,w=100,h=75) 

    pdf.set_xy(5, 180)
    spacing = 3
    tablefirst_head1 = [df.columns.tolist()]
    tablefirst1 = df.values.tolist()

    # Adjusted column widths
    first_col_width = pdf.w / 18  # Smaller width for the first column
    second_col_width = pdf.w / 18  # Smaller width for the second column
    middle_col_width = pdf.w / 6   # Standard width for the middle columns
    last_col_width = pdf.w / 3     # Larger width for the last column

    pdf.set_font("Arial", 'B', size=8)
    row_height = pdf.font_size

    # Print table header
    for row in tablefirst_head1:
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(21, 55, 188)
        pdf.set_x(5)
        for i, item in enumerate(row):
            if i == 0:
                col_width = first_col_width  # First column
            elif i == 1:
                col_width = second_col_width  # Second column
            elif i == len(row) - 1:
                col_width = last_col_width  # Last column
            else:
                col_width = middle_col_width  # Middle columns
            pdf.cell(col_width, row_height * spacing, txt=item, border=1, fill=True)
        pdf.ln(row_height * spacing)

    # Print table rows
    pdf.set_font("Arial", size=8)
    pdf.set_text_color(0, 0, 0)

    for row in tablefirst1:
        pdf.set_x(5)
        for i, item in enumerate(row):
            if i == 0:
                col_width = first_col_width  # First column
            elif i == 1:
                col_width = second_col_width  # Second column
            elif i == len(row) - 1:
                col_width = last_col_width  # Last column
            else:
                col_width = middle_col_width  # Middle columns
            pdf.cell(col_width, row_height * spacing, txt=str(item), border=1)
        pdf.ln(row_height * spacing)

    pdf.set_xy(10,130)    
    pdf.set_font('Arial', "B",14)    

    #Page Number
    pdf.set_y(273)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0,2,'Page %s' % pdf.page_no(),align="R") 
    pdf.output('pdf_name.pdf','F')

    pdf_name = fleet_name + ' - AE MISSING VESSEL'
    pdf.output('./documents/'+pdf_name)
    return FileResponse(path = './documents/'+pdf_name,filename=pdf_name)
 

