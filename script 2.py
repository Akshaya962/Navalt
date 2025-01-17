import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import requests
from fastapi import APIRouter,Request
import plotly.express as px
import base64
import plotly.offline as pyo
from plotly.subplots import make_subplots
from datetime import datetime
import urllib.parse
import os
from fastapi import APIRouter , Request , Depends
from storage.database_vdm_async import get_vdm_db_async
import plotly.graph_objects as go
from starlette.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from routers.vessel import vessel_color
import aiofiles

router = APIRouter()

msc_logo_path = "./images/logo/msc.png"


download_path = './documents/html/'

with open(msc_logo_path, 'rb') as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    image_tag = f'<img src="data:image/png;base64,{encoded_string}" alt="image_1" width="100px">'

if not os.path.exists(download_path):
    os.makedirs(download_path)
    



@router.post('/api/v1/html/datamonitoring/operationalprofile/{imo}')
async def index(info:Request,vessel_name:str = None,imo:str = None):
    
    data = await info.json()

    operation_profile_columns = data['data'][imo][0]["operation_profile"]["columns"]
    operation_profile_index = data['data'][imo][0]["operation_profile"]["index"]

    operation_profile_columns_int = [int(x) for x in operation_profile_columns]
    data1 = pd.DataFrame.from_dict(data['data'][imo][0]["operation_profile"]["data"])

    operational_values=data1.values.tolist()
    column_name_map = {old_col: new_col for old_col, new_col in zip(data1.columns, operation_profile_columns_int)}
    data1.rename(columns=column_name_map, inplace=True)

    data2=data1.copy()
    data2.insert(0, 'Speed/Draft', operation_profile_index)
    data2['Speed/Draft']=data2['Speed/Draft'].astype(int)
    data2a =data2.set_index('Speed/Draft')
    data3=data2a/100




    fig = go.Figure(data=[go.Surface(x=operation_profile_columns, y=operation_profile_index, z=operational_values)])
    fig.update_layout(scene=dict(xaxis_title='Draft', yaxis_title='Speed', zaxis_title='Data Points (%)'))
    html_file_path = download_path+'operational_profile_chart_'+imo+'.html'
    fig.write_html(html_file_path)

    import matplotlib.cm as cm






    def apply_heatmap(val):
        cmap = 'vlag'  
        vmin = data3.min().min()  
        vmax = data3.max().max()  
        
        # Normalize the value
        norm = plt.Normalize(vmin=vmin, vmax=vmax)

        # Get the colormap
        cmap_func = plt.get_cmap(cmap)
        
        # Apply the normalization and colormap to the single value
        heatmap_color = cmap_func(norm(val))[:3]
        
        # Convert the color to RGB and format as a CSS background-color property
        return f'background-color: rgb({int(heatmap_color[0]*255)},{int(heatmap_color[1]*255)},{int(heatmap_color[2]*255)}); color: black'

    styled_df = data3.style.applymap(apply_heatmap)



    styled_df = styled_df.format("{:.2%}")

    # display(styled_df)


    html_table_file = download_path+'operational_profile_table_'+imo+'.html'
    with open(html_table_file, 'w') as f:
        f.write(styled_df.to_html())

    with open(html_table_file, 'r') as f:
        html = f.read()

    with open(html_table_file, 'w') as f:
        f.write(html + '\n<style>\ntable {border-collapse: collapse;}\n</style>'+'\n<style>\ntable {margin: auto;}\n</style>')

    async def merge_html_files(input_file1, input_file2, output_file, msc_logo_path, vessel_name):
        async with aiofiles.open(input_file1, 'r', encoding='utf-8') as f1:
            html_content1 = await f1.read()
            
        async with aiofiles.open(input_file2, 'r', encoding='utf-8') as f2:
            html_content2 = await f2.read()

        async with aiofiles.open(msc_logo_path, 'rb') as image_file:
            encoded_string = base64.b64encode(await image_file.read()).decode('utf-8')

        image_tag = f'<img src="data:image/png;base64,{encoded_string}" alt="image_1" width="100px">'
        new_page_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title></title>
            <style>
                h2 {{
                    text-align: center;
                }}
                .centered {{
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <h2>Operational Profile Chart </h2>
            {image_tag}
            <h4>Vessel Name: {vessel_name} </h4>
            {html_content1}
            <h2>Operational Profile Table</h2>
            <div class="centered">
            {html_content2}
            </div>
        </body>
        </html>
        """

        async with aiofiles.open(output_file, 'w', encoding='utf-8') as f_out:
            await f_out.write(new_page_content)


    output_file = download_path+'final_'+imo+'.html'
    await merge_html_files(html_file_path, html_table_file, output_file,msc_logo_path,vessel_name)
    
    return FileResponse(path=output_file, filename='operational_profile.html')



    





@router.post('/api/v1/html/pre_post/{imo}')
async def index(info:Request, imo:str =None,
key_date:str = None,slip_min:str = None,slip_max:str = None,sea_state_min:str = None,sea_state_max:str = None,steaming_time_min:str = None,steaming_time_max:str = None,draft_min:str = None,draft_max:str = None,speed_min:str = None,speed_max:str = None,sfoc_min:str = None,sfoc_max:str = None,power_min:str = None,power_max:str = None,sea_state:str = None,draft:str = None,types:str = None,vessel_name:str = None,method:str=None):
    
    s = await info.json()
    
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
    import plotly.graph_objects as go
    import plotly.offline as pyo
    
    fig = go.Figure()

    # Add pre-analysis line
    fig.add_trace(go.Scatter(x=data2_pre['SPEED'], y=data2_pre['POWER'],
                            mode='lines+markers', name='Pre Analysis', marker=dict(color='green', size=8)))

    # Add post-power line
    fig.add_trace(go.Scatter(x=data2_post['SPEED'], y=data2_post['POWER'],
                            mode='lines+markers', name='Post Power', marker=dict(color='blue', size=8)))

    # Layout customization
    fig.update_layout(
        xaxis=dict(title= f"{method.upper()} (knots)", titlefont=dict(size=12, color='black', family='Arial, sans-serif'), showgrid=False),
        yaxis=dict(title='POWER (kW)', titlefont=dict(size=12, color='black', family='Arial, sans-serif'), showgrid=False),
        legend=dict(title=None),
        width=1000,
        height=700
    )


    # Save the plot to an HTML file
    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


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
    fig = go.Figure()

    # Add pre-analysis line
    fig.add_trace(go.Scatter(x=data3_pre['SPEED'], y=data3_pre['FO'],
                            mode='lines+markers', name='Pre FO', marker=dict(color='green', size=8)))

    # Add post-power line
    fig.add_trace(go.Scatter(x=data3_post['SPEED'], y=data3_post['FO'],
                            mode='lines+markers', name='Post FO', marker=dict(color='blue', size=8)))

    # Layout customization
    fig.update_layout(
        xaxis=dict(title=f"{method.upper()} (knots)", titlefont=dict(size=12, color='black', family='Arial, sans-serif'), showgrid=False),
        yaxis=dict(title='FO (MT)', titlefont=dict(size=12, color='black', family='Arial, sans-serif'), showgrid=False),
        legend=dict(title=None),
        width=1000,
        height=700
    )


    # Save the plot to an HTML file
    plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})





    import plotly.offline as pyo
    import plotly.graph_objects as go


    html_table = "<table border='1'>\n"
    # Create table header
    html_table += "<tr>"
    for col in data_filter_df.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr>\n"

    # Iterate over rows
    for index, row in data_filter_df.iterrows():
        html_table += "<tr>"
        for value in row:
            html_table += f"<td>{value}</td>"
        html_table += "</tr>\n"

    html_table += "</table>"


    html_table2 = "<table border='1'>\n"
    # Create table header
    html_table2 += "<tr>"
    for col in power_comparison_table.columns:
        html_table2 += f"<th>{col}</th>"
    html_table2 += "</tr>\n"

    # Iterate over rows
    for index, row in power_comparison_table.iterrows():
        html_table2 += "<tr>"
        for value in row:
            html_table2 += f"<td>{value}</td>"
        html_table2 += "</tr>\n"

    html_table2 += "</table>"


    html_table3 = "<table border='1'>\n"
    # Create table header
    html_table3 += "<tr>"
    for col in fo_comparison_table.columns:
        html_table3 += f"<th>{col}</th>"
    html_table3 += "</tr>\n"

    # Iterate over rows
    for index, row in fo_comparison_table.iterrows():
        html_table3 += "<tr>"
        for value in row:
            html_table3 += f"<td>{value}</td>"
        html_table3 += "</tr>\n"

    html_table3 += "</table>"





    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pre/Post</title>
        <style>
            body {{
                text-align: center;
            }}
            h1 {{
                color: #193185;
            }}
            h2{{
                color: #193185;
            }}
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
            }}
            
            .second-info{{ margin-left: 100px;}}
            table {{
                margin: 20px auto;
                    width: 511px;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            
                table, tr, td {{height: 34px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%;
                        display: flex;
                        justify-content: center;
            }}
                
                
            .rectangles-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;  /* Optional margin between rectangles and table */
            }}
            hr {{border-width: 3px;}}
            .rectangle {{
                min-width: 200px;
                #height: 100px;
                padding: 12px;
                border: 2px solid;
                margin-right: 20px;  /* Optional margin between rectangles */
                color: white;
                #display: flex;
                #flex-direction: row;
                #align-items: 'center';
                #justify-content: 'center'
                text-align: 'center';
            }}
            /* Apply additional styles based on conditions */
            .gain-positive {{
                background-color: #17d41a;
                border-color: #008000;
            }}
            .gain-negative {{
                background-color: #ff0000;
                border-color: #800000;
            }}
            .gold {{
            background-color: #FFA500;
            border-color: #800000; 
            }}
            th {{
        background: blue;
        color: white;
        height: 41px;
    }}
        </style>
    </head>
    <body>
        {image_tag}
        <h1>
            {'PRE-POST ANALYSIS (VRS)' if types == 'vrs' else 'PRE-POST ANALYSIS (ADA)'}
        </h1>
        <br>
        <br>
        <hr>

        <!-- Add information in HTML format -->
        <div class="info">
            <div class='first-info'>
                <p>Vessel Name: {vessel_name} </p>
                <p>Key Date: {key_date}</p>
                <p>Pre Analysis Date Range: {pre_date_start} to {pre_date_end}</p>
                <p>Post Analysis Date Range: {post_date_start} to {post_date_end}</p>
            </div>
            <div class='second-info'>
                <p>Pre Data Count: {pre_data_count}</p>
                <p>Post Data Count: {post_data_count}</p>
                <p>Draft(m): {draft}</p>
                <p>Sea State: {sea_state}</p>
            </div>
        </div>
    <br>
        <!-- Add the rectangles container with conditional styling -->
        <div class="rectangles-container">
            <div class="rectangle {'gain-positive' if gain_power >= 0 else 'gain-negative'}">
                <!-- Add content or leave it empty as needed -->
                <p>{gain_power}<br>{'% Gain in Power %' if gain_power >=0 else '% Loss in Power %' }</p>
            
            </div>
            <div class="rectangle {'gain-positive' if gain_fo >= 0 else 'gain-negative'}">
                <!-- Add content or leave it empty as needed -->
                <p>{gain_fo}<br>{'% Gain in FO %' if gain_fo >=0 else '% Loss in FO %' }</p>
            </div>
            
            <div class="rectangle gold">
            <p>{power_accuracy}%<br> Accuracy in Power prediction</p>
            </div>

            <div class="rectangle gold">
            <p>{fo_accuracy}%<br> Accuracy in FO prediction</p>
            </div>

            
        </div>
        <br>
        <h2>Applied Data Filters</h2>
        <!-- Add the centered and bigger table -->
        {html_table}
        <br>
        <br>
        <br>
        
        <h2>Power Comparison</h2>
        <div class="plot_div">
            {plot_div}
        </div>
        <br>
        <br>
        <br>
        <br>
        <h2>Power Comparison Table</h2>
        {html_table2}
        <br>
        <br>
        <br>
        <h2>FO Comparison</h2>
        <div class="plot_div">
            {plot_div2}
        </div>
        <br>
        <br>
        <br>
        <h2>FO Comparison Table</h2>
        
        {html_table3}

        <!-- ... (rest of the body content) ... -->
    </body>
    </html>
    """

    # Save the HTML content to a file
    file_name = 'pre_post'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:    
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)


@router.post('/api/v1/html/performance-analysis/{imo}')
async def index(info:Request, imo:str =None,start_date :str = None,end_date :str = None,types :str = None,fleet :str = None,group :str = None,slip_min :str = None,slip_max :str = None,sea_state_min :str = None,sea_state_max :str = None,steaming_time_min :str = None,steaming_time_max :str = None,draft_min :str = None,draft_max :str = None,speed_min :str = None,speed_max :str = None,sfoc_min :str = None,sfoc_max :str = None,power_min :str = None,steaming_max :str = None,power_max :str = None,steaming_min :str = None,sea_state :str = None,draft :str = None,vessel_name:str = None,key_dates:str=None):
    s = await info.json()
    # print(s)
    if types=='vrs':
        label = 'STW'
    else:
        label = 'stw'



    data = {' ': ['Slip', 'Sea State', 'Steaming Time(Hrs)', 'Draft(m)','Speed(kn)','SFOC(kg/kW-Hr)','Power(kW)'],
            'Min': [slip_min, sea_state_min, steaming_min, draft_min, speed_min, sfoc_min, power_min],
            'Max': [slip_max, sea_state_max, steaming_max, draft_max, speed_max, sfoc_max, power_max]}
    data_filter_df = pd.DataFrame(data)


    #**************************Performance Curve - FO Consumption**************************#
        # if types =='vrs':
    #     data1 = pd.DataFrame.from_dict(s['vrs']['tab3']['table1'])
    #     data2 = pd.DataFrame.from_dict(s['vrs']['tab3']['chart1'])
    # else:
    #     data1 = pd.DataFrame.from_dict(s['ada']['tab3']['table1'])
    #     data2 = pd.DataFrame.from_dict(s['ada']['tab3']['chart1'])

    accuracy_pwr=s["data"]['tab2']['dpower']
    accuracy_fo=s["data"]['tab2']['dfo']
    date1=s["data"]['tab2']['date1']
    date2=s["data"]['tab2']['date2']

    accuracy_pwr=str(accuracy_pwr)+'%'
    print('accuracy_pwr:',accuracy_pwr)
    accuracy_fo= str(accuracy_fo)+'%'
    date1 = datetime.strptime(date1, '%d %b %Y').date()
    date2 = datetime.strptime(date2, '%d %b %Y').date()
    # Format the date range string
    date_range = f"{date1.strftime('%d %b %Y')} to {date2.strftime('%d %b %Y')}"
    # Decode URL-encoded characters and clean up
    decoded_name = urllib.parse.unquote(vessel_name)
    vessel_name = decoded_name.replace(" - ", " -").strip()


      
        
        
    data1 = pd.DataFrame.from_dict(s['data']['tab3']['table1'])
    data1 = data1.astype(str)

    data2 = pd.DataFrame.from_dict(s['data']['tab3']['chart1'])

    category1_lst = data2['Category'].unique().tolist()
    color_lst1 = ['brown', 'darkviolet', 'red', 'green', 'orange', 'blue', 'yellow', 'cyan', 'pink', 'gray', 'olive', 'purple', 'indigo', 'magenta', 'beige', 'lavender', 'black', 'lightgreen']

    # Create figure for FO Consumption
    fig_fo = go.Figure()  
    for i, category in enumerate(category1_lst):
        df1 = data2[data2['Category'] == category]
        fig_fo.add_trace(go.Scatter(
            x=df1[label],
            y=df1['fo_consumption'],
            mode='lines+markers',
            name=category,
            line=dict(color=color_lst1[i % len(color_lst1)]),
            marker=dict(size=10)
        ))

    fig_fo.update_layout(
        title='Speed FO/24 Hrs Curve',
        xaxis_title='Speed (knots)',
        yaxis_title='FO/24Hrs (tonne)',
        legend_title=None,
        font=dict(size=12, family='Arial'),
        autosize=True
    )
    #fig.write_image('performance_analysis_speed_draft.png')
    ##fig.show()
    plot_div = pyo.plot(fig_fo, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})




    #***************************Performance Curve - Power*******************************#
    # if types =='vrs':

    #     data3 = pd.DataFrame.from_dict(s['vrs']['tab3']['table2'])
    #     data4 = pd.DataFrame.from_dict(s['vrs']['tab3']['chart2'])
    # else:
    #     data3 = pd.DataFrame.from_dict(s['ada']['tab3']['table2'])
    #     data4 = pd.DataFrame.from_dict(s['ada']['tab3']['chart2'])
    
    data3 = pd.DataFrame.from_dict(s['data']['tab3']['table2'])
    data3 = data3.astype(str)

    data4 = pd.DataFrame.from_dict(s['data']['tab3']['chart2'])

    category2_lst = data4['Category'].unique().tolist()
    color_lst2 = ['brown', 'darkviolet', 'red', 'green', 'orange', 'blue', 'yellow', 'cyan', 'pink', 'gray', 'olive', 'purple', 'indigo', 'magenta', 'beige', 'lavender', 'black', 'lightgreen']

    # Create figure for Power
    fig_power = go.Figure()

    for i, category in enumerate(category2_lst):
        df2 = data4[data4['Category'] == category]
        fig_power.add_trace(go.Scatter(
            x=df2[label],
            y=df2['Power'],
            mode='lines+markers',
            name=category,
            line=dict(color=color_lst2[i % len(color_lst2)]),
            marker=dict(size=10)
        ))

    fig_power.update_layout(
        title='Speed Power Curve',
        xaxis_title='Speed (knots)',
        yaxis_title='Power (kW)',
        legend_title=None,
        font=dict(size=12, family='Arial'),
        autosize=True
    )
    
            
    
    #fig.write_image('performance_analysis_speed_power.png')
    ##fig.show()
    plot_div2 = pyo.plot(fig_power, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        
        
    #*******************************FO Calculator for Sea State****************************#
    # if types =='vrs':
    #     data5 = pd.DataFrame.from_dict(s['vrs']['tab3']['table3'])
    #     data6 = pd.DataFrame.from_dict(s['vrs']['tab3']['chart3'])
    # else:
    #     data5 = pd.DataFrame.from_dict(s['ada']['tab3']['table3'])
    #     data6 = pd.DataFrame.from_dict(s['ada']['tab3']['chart3'])

    data5 = pd.DataFrame.from_dict(s['data']['tab3']['table3'])
    data5 = data5.astype(str)

    data6 = pd.DataFrame.from_dict(s['data']['tab3']['chart3'])

    category3_lst = data6['Category'].unique().tolist()
    color_lst3 = ['brown', 'darkviolet', 'red', 'green', 'orange', 'blue', 'yellow', 'cyan', 'pink', 'gray', 'olive', 'purple', 'indigo', 'magenta', 'beige', 'lavender', 'black', 'lightgreen']

    # Create figure for FO Calculator for Sea State
    fig_sea_state = go.Figure()

    for i, category in enumerate(category3_lst):
        df3 = data6[data6['Category'] == category]
        fig_sea_state.add_trace(go.Scatter(
            x=df3[label],
            y=df3['fo_consumption'],
            mode='lines+markers',
            name=category,
            line=dict(color=color_lst3[i % len(color_lst3)]),
            marker=dict(size=10)
        ))

    fig_sea_state.update_layout(
        title='Speed FO/24Hrs Curve For Sea State',
        xaxis_title='Speed (knots)',
        yaxis_title='FO/24Hrs (tonne)',
        legend_title=None,
        font=dict(size=12, family='Arial'),
        autosize=True
    )


    ##fig.show()
    plot_div3 = pyo.plot(fig_sea_state, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    html_table = "<table border='1'>\n"
    # Create table header
    html_table += "<tr>"
    for col in data_filter_df.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr>\n"

    # Iterate over rows
    for index, row in data_filter_df.iterrows():
        html_table += "<tr>"
        for value in row:
            html_table += f"<td>{value}</td>"
        html_table += "</tr>\n"

    html_table += "</table>"


    html_table2 = "<table border='1'>\n"
    # Create table header
    html_table2 += "<tr>"
    for col in data1.columns:
        html_table2 += f"<th>{col}</th>"
    html_table2 += "</tr>\n"

    # Iterate over rows
    for index, row in data1.iterrows():
        html_table2 += "<tr>"
        for value in row:
            html_table2 += f"<td>{value}</td>"
        html_table2 += "</tr>\n"

    html_table2 += "</table>"




    html_table3 = "<table border='1'>\n"
    # Create table header
    html_table3 += "<tr>"
    for col in data3.columns:
        html_table3 += f"<th>{col}</th>"
    html_table3 += "</tr>\n"

    # Iterate over rows
    for index, row in data3.iterrows():
        html_table3 += "<tr>"
        for value in row:
            html_table3 += f"<td>{value}</td>"
        html_table3 += "</tr>\n"

    html_table3 += "</table>"


    html_table4 = "<table border='1'>\n"
    # Create table header
    html_table4 += "<tr>"
    for col in data5.columns:
        html_table4 += f"<th>{col}</th>"
    html_table4 += "</tr>\n"

    # Iterate over rows
    for index, row in data5.iterrows():
        html_table4 += "<tr>"
        for value in row:
            html_table4 += f"<td>{value}</td>"
        html_table4 += "</tr>\n"

    html_table4 += "</table>"




    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Performance Analysis</title>
        <style>
            body {{
                text-align: center;
            }}
            h1 {{
                color: #193185;
            }}
            h2 {{
                color: #193185;
            }}
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
            }}

            .second-info {{ margin-left: 100px; }}
            table {{
                margin: 20px auto;
                width: 511px;
                border-collapse: collapse;
                border: solid;
                
            }}

            .card {{
                background-color: #FFEBCD; /* Light orange color */
                border: 1px solid #ccc;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                margin: 10px auto;
                padding: 15px;
                max-width: 400px;
                text-align: left;
                border-radius: 10px;
            }}
            table, tr, td {{
                height: 34px;
                border: 1px solid;
            }}
            .plot_div {{
                display: flex;
                justify-content: center;
            }}

            hr {{ border-width: 3px; }}

            th {{
                background: blue;
                color: white;
                height: 41px;
            }}
        </style>
    </head>
    <body>
        {image_tag}
        <h1>
            {'PERFORMANCE ANALYSIS (VRS)' if types == 'vrs' else 'PERFORMANCE ANALYSIS (ADA)'}
        </h1>
        <br>
        <br>
        <hr>

        <!-- Add information in HTML format -->
        <div class="info">
            <div class='first-info'>
                <p>Vessel Name: {vessel_name}</p>
                <p>Key Dates: {key_dates}</p>
                <p>Analysis Date Range: {start_date} to {end_date}</p>
            </div>
        </div>
        <hr>
        <br>

        <div class="info">
            <div class="card">
                <p>Accuracy in Power prediction: {accuracy_pwr}</p>
            </div>
            <div class="card">
                <p>Accuracy in FO/24 Hrs prediction: {accuracy_fo}</p>
            </div>
            <div class="card">
                <p>Analysis Date Range: {date_range}</p>
            </div>
        </div>
        <br>
        <br>

        <h2>Applied Data Filters</h2>
        {html_table}
        <br>
        <br>
        <br>

        <h2>Performance Curve - FO Consumption</h2>
        <p>SeaState Selected: {sea_state}</p>
        <br>
        <br>
        {html_table2}
        <br>
        <br>
        <h2>FO/24 Hrs Vs Speed</h2>
        <div class="plot_div">
            {plot_div}
        </div>
        <br>
        <br>
        <br>

        <h2>Performance Curve - Power</h2>
        {html_table3}
        <br>
        <br>
        <h2>Power VS Speed</h2>
        <div class="plot_div">
            {plot_div2}
        </div>
        <br>
        <br>
        <br>

        <h2>FO Calculator for Sea State</h2>
        {html_table4}
        <p>Draft Selected: {draft}</p>
        <br>
        <br>
        <h2>FO Vs Speed For Sea State</h2>
        <div class="plot_div">
            {plot_div3}
        </div>
        <br>
        <br>

        <!-- ... (rest of the body content) ... -->
    </body>
    </html>
    """

    # Save the HTML content to a file

    
    file_name = 'perfomance_analysis'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)

@router.post('/api/v1/html/datamonitoring/timeseries/{imo}')
async def index(info:Request,method : str = None,imo:str =None,vessel_name : str = None,mindate : str = None,maxdate : str = None,report_type : str = None,group : str = None,parameter : str = None,graph_type : str = None,vessel_mode : str = None,multi_parameter : str = None,date_obj : str = None,y_axis_value : str = None,vessel_names:str = None,Bar_Type : str = None,vdm_db: AsyncSession = Depends(get_vdm_db_async)):
    s = await info.json()
    color_lst=await vessel_color(vdm_db)
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
    multi_data =s['data']
    first_pair = next(iter((multi_data.items())) )

    #__________Input Parameter _________________
    input_para_data_moni_time={"Monitoring Period": [date_obj],
                                "Parameter":parameter,
                            "Graph_Type":[graph_type],'Vessel':vessel_name,
                            'Vessels':vessel_name,'Group':group,"Report_Type":[report_type],"Mode":[vessel_mode],"Multi_Parameter":multi_parameter,"Bar_Type":[Bar_Type]}
    input_data = pd.DataFrame.from_dict(input_para_data_moni_time)


    parameter_list = parameter.split(',')
    if len(parameter_list) == 1:
        parameter_list = parameter_list[0]    

    if input_data["Mode"].values[0]=="vessel":
        a = input_data["Vessels"].values[0]
        c="Vessel"
    elif input_data["Mode"].values[0]=="multi":   
        a = input_data["Vessels"].values[0]
        c="Vessels"
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

    if input_data["Report_Type"].values[0]=="M":
        e="MONTHLY"
    if input_data["Report_Type"].values[0]=="D":
        e="DAILY"
    if input_data["Report_Type"].values[0]=="Y":
        e="YEARLY"        
    if input_data["Report_Type"].values[0]=="Q":
        e="QUARTERLY"        

    multi_data =s['data']
    first_pair = next(iter((multi_data.items())) )
    first_pair[0]
    Parameter_len= len(parameter_list)
    data_1 = pd.DataFrame.from_dict(s['data'][first_pair[0]])
    import plotly.express as px

    if input_data["Report_Type"].values[0]=="D"and input_data["Multi_Parameter"].values[0]=="normal":
        count = 0
        j = 0
        cumulative_sum = None
        if input_data["Graph_Type"].values[0] == 'Line':
            if method!='both':
                vessel_imo = list(s['data'].keys())
                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row

                vessel_name = df['vessel_name'].iloc[0]
                df = df.replace([0], np.nan)
                df["date_"] = pd.to_datetime(df["corrected_date"])
                df = df.sort_values(by='date_')

                traces = []
                for imo in vessel_imo:
                    filtered_data = df[df['imo'] == imo]


                    color = color_lst.get(imo, '#000000') 


                    trace = go.Scatter(
                        x=df['corrected_date'],
                        y=df[input_data["Parameter"].values[0]],  
                        mode='lines+markers',
                        name=vessel_name,
                        line=dict(color=color),
                        showlegend=True
                        )
                    traces.append(trace)
                layout = go.Layout(
                        xaxis=dict(title='Daily', tickangle=-45),
                        yaxis=dict(title=y_axis_value)

                    ) 
                fig = go.Figure(data=traces, layout=layout)

                fig.show()
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            else:
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                combined_data = combined_data[['corrected_date', 'type', parameter]]

                vrs_data = combined_data[combined_data['type'] == 'VRS Data']
                ada_data = combined_data[combined_data['type'] == 'ADA Data']

                fig = go.Figure()

                fig.add_trace(go.Scatter(x=vrs_data['corrected_date'], y=vrs_data[parameter],
                                        mode='lines', line=dict(color='green'), name='VRS Data'))


                fig.add_trace(go.Scatter(x=ada_data['corrected_date'], y=ada_data[parameter],
                                        mode='lines', line=dict(color='red'), name='ADA Data'))


                fig.update_layout(
                                xaxis_title='Date',
                                yaxis_title=y_axis_value,
                                xaxis=dict(tickangle=-45,dtick=7))


                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})




        elif input_data["Graph_Type"][0] == 'Bar':
            if method!='both':
                imo = list(s['data'].keys())
                imo=imo[0]
               
                if imo :
                    vessel_imo = imo
                combined_data = pd.DataFrame()
                data=s['data'][vessel_imo]
                # print("ddd",data)
                # for imo, data in data:
                df = pd.DataFrame.from_dict(data)
                print("dffffffffffff",df)
                # df['imo'] = imo  # Add IMO number to each row
                combined_data = pd.concat([combined_data, df], ignore_index=True)
                combined_data = combined_data.replace([0], np.nan)
                combined_data["date_"] = pd.to_datetime(combined_data["corrected_date"])
                combined_data_sorted = combined_data.sort_values(by='date_')
                traces = []
                print(vessel_imo)
                # for imo in vessel_imo:
                filtered_data = combined_data_sorted[combined_data_sorted['imo'] == vessel_imo]
                print("filtered_data",filtered_data)
                vessel_name = filtered_data['vessel_name'].iloc[0]
                print("vessel",filtered_data['vessel_name'].iloc[0])
                color = color_lst.get(imo, '#000000')  # Default color if IMO not in color_lst
                trace = go.Bar(
                    x=filtered_data['corrected_date'],
                    y=filtered_data[input_data["Parameter"].values[0]],  # Replace 'parameter' with your actual column name
                    name=vessel_name,
                    marker=dict(color=color),
                    showlegend=True
                )
                traces.append(trace)

                # Create layout
                layout = go.Layout(
                    xaxis=dict(title='Daily', tickangle=-45),
                    yaxis=dict(title= y_axis_value),  # Replace 'Parameter' with your actual parameter
                    legend=dict(title='Vessel Name', x=1.05, y=1, traceorder="normal", font=dict(size=10))
                )

                fig = go.Figure(data=traces, layout=layout)
              
               
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

            else:

                color_map = {'VRS Data': 'green', 'ADA Data': 'red'}

                # Create traces for each type

                traces = []
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                    combined_data = combined_data.replace([0], np.nan)
                print(combined_data)

                for type_value, group in combined_data.groupby('type'):

                    trace = go.Bar(

                        x=group['corrected_date'],

                        y=group[input_data["Parameter"][0]],

                        name=type_value,

                        marker=dict(color=color_map.get(type_value))  # Set color based on type

                    )

                    traces.append(trace)

                # Define the layout

                layout = go.Layout(


                    xaxis=dict(title='corrected_date'),

                    yaxis=dict(title=input_data["Parameter"][0])

                )

                # Create the figure

                fig = go.Figure(data=traces, layout=layout)
                fig.update_layout(xaxis=dict( tickangle=-45,dtick=7))

                # Show the chart


                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})





        elif input_data["Graph_Type"][0] == 'Scatter':
            if method=='both':
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                # Extracting specific columns
                combined_data = combined_data[['corrected_date', 'type', parameter]]

                # Filtering data for VRS and ADA separately
                vrs_data = combined_data[combined_data['type'] == 'VRS Data']
                ada_data = combined_data[combined_data['type'] == 'ADA Data']

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=vrs_data['corrected_date'], y=vrs_data[parameter],
                                        mode='markers', marker=dict(color='green'), name='VRS Data'))

                fig.update_layout( xaxis_title='Date', yaxis_title=y_axis_value)
                fig.update_layout(xaxis=dict( tickangle=-45,dtick=7))

                fig.add_trace(go.Scatter(x=ada_data['corrected_date'], y=ada_data[parameter],
                                        mode='markers', marker=dict(color='red'), name='ADA Data'))




                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

            else:
                vessel_imo = list(s['data'].keys())


                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row

                vessel_name = df['vessel_name'].iloc[0]

                df = df.replace(0, np.nan)

                df["date_"] = pd.to_datetime(df["corrected_date"])
                df = df.sort_values(by='date_')

                traces = []
                for imo in vessel_imo:
                    filtered_data = df[df['imo'] == imo]


                    color = color_lst.get(imo, '#000000') 


                    trace = go.Scatter(
                        x=df['corrected_date'],
                        y=df[input_data["Parameter"].values[0]],  
                        mode='markers',
                        name=vessel_name,
                        line=dict(color=color),
                        showlegend=True
                        )
                    traces.append(trace)
                layout = go.Layout(
                        xaxis=dict(title='Daily', tickangle=-45),
                        yaxis=dict(title=y_axis_value)

                    ) 
                fig = go.Figure(data=traces, layout=layout)

                fig.show()
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    elif input_data["Report_Type"].values[0]=="M"and input_data["Multi_Parameter"].values[0]=="normal":    
        count = 0
        j = 0

        if input_data["Graph_Type"][0] == 'Line':
            if method!='both': 
                
                vessel_imo = list(s['data'].keys())


                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row

                vessel_name = df['vessel_name'].iloc[0]

                df = df.replace(0, np.nan)

                df["date_"] = pd.to_datetime(df["corrected_date"])
                df = df.sort_values(by='date_')

                traces = []
                for imo in vessel_imo:
                    filtered_data = df[df['imo'] == imo]



                    color = color_lst.get(imo, '#000000') 


                    trace = go.Scatter(
                        x=df['corrected_date'],
                        y=df[input_data["Parameter"].values[0]],  
                        mode='lines+markers',
                        name=vessel_name,
                        line=dict(color=color),
                        showlegend=True

                        )
                    traces.append(trace)
                layout = go.Layout(
                        xaxis=dict(title='Monthly', tickangle=-45),
                        yaxis=dict(title=y_axis_value),
                        showlegend=True)



                fig = go.Figure(data=traces, layout=layout)



                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

            else:
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                combined_data = combined_data[['corrected_date', 'type', parameter]]

                vrs_data = combined_data[combined_data['type'] == 'VRS Data']
                ada_data = combined_data[combined_data['type'] == 'ADA Data']

                fig = go.Figure()

                fig.add_trace(go.Scatter(x=vrs_data['corrected_date'], y=vrs_data[parameter],
                                        mode='lines', line=dict(color='green'), name='VRS Data'))


                fig.add_trace(go.Scatter(x=ada_data['corrected_date'], y=ada_data[parameter],
                                        mode='lines', line=dict(color='red'), name='ADA Data'))


                fig.update_layout(
                                xaxis_title='Month',
                                yaxis_title=y_axis_value,
                                xaxis=dict(tickangle=-45))


                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        elif input_data["Graph_Type"][0] == 'Bar':
            if method!='both':
                vessel_imo = list(s['data'].keys())
                combined_data = pd.DataFrame()

                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row
                    combined_data = pd.concat([combined_data, df], ignore_index=True)
                combined_data = combined_data.replace([0], np.nan)
                combined_data["date_"] = pd.to_datetime(combined_data["corrected_date"])
                combined_data_sorted = combined_data.sort_values(by='date_')
                traces = []
                for imo in vessel_imo:
                    filtered_data = combined_data_sorted[combined_data_sorted['imo'] == imo]
                    vessel_name = filtered_data['vessel_name'].iloc[0]
                    color = color_lst.get(imo, '#000000')  # Default color if IMO not in color_lst
                    trace = go.Bar(
                        x=filtered_data['corrected_date'],
                        y=filtered_data[input_data["Parameter"].values[0]],  # Replace 'parameter' with your actual column name
                        name=vessel_name,
                        marker=dict(color=color),
                        showlegend=True
                    )
                    traces.append(trace)

                # Create layout
                layout = go.Layout(
                    xaxis=dict(title='Monthly', tickangle=-45),
                    yaxis=dict(title=y_axis_value),  # Replace 'Parameter' with your actual parameter
                    legend=dict(title='Vessel Name', x=1.05, y=1, traceorder="normal", font=dict(size=10))
                )

                fig = go.Figure(data=traces, layout=layout)
                fig.show()



                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            else:

                color_map = {'VRS Data': 'green', 'ADA Data': 'red'}

                # Create traces for each type

                traces = []
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                    combined_data = combined_data.replace([0], np.nan)
                print(combined_data)

                for type_value, group in combined_data.groupby('type'):

                    trace = go.Bar(

                        x=group['corrected_date'],

                        y=group[input_data["Parameter"][0]],

                        name=type_value,

                        marker=dict(color=color_map.get(type_value))  # Set color based on type

                    )

                    traces.append(trace)

                # Define the layout

                layout = go.Layout(



                    xaxis=dict(title='Month'),

                    yaxis=dict(title=y_axis_value)

                )

                # Create the figure

                fig = go.Figure(data=traces, layout=layout)
                fig.update_layout(xaxis=dict( tickangle=-45))

                # Show the chart


                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        elif input_data["Graph_Type"][0] == 'Scatter':
            if method=='both':
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                # Extracting specific columns
                combined_data = combined_data[['corrected_date', 'type', parameter]]

                # Filtering data for VRS and ADA separately
                vrs_data = combined_data[combined_data['type'] == 'VRS Data']
                ada_data = combined_data[combined_data['type'] == 'ADA Data']

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=vrs_data['corrected_date'], y=vrs_data[parameter],
                                        mode='markers', marker=dict(color='green'), name='VRS Data'))

                fig.update_layout( xaxis_title='Month', yaxis_title=y_axis_value)
                fig.update_layout(xaxis=dict( tickangle=-45,dtick=7))

                fig.add_trace(go.Scatter(x=ada_data['corrected_date'], y=ada_data[parameter],
                                        mode='markers', marker=dict(color='red'), name='ADA Data'))




                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            else:
                vessel_imo = list(s['data'].keys())


                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row

                vessel_name = df['vessel_name'].iloc[0]

                df = df.replace(0, np.nan)

                df["date_"] = pd.to_datetime(df["corrected_date"])
                df = df.sort_values(by='date_')

                traces = []
                for imo in vessel_imo:
                    filtered_data = df[df['imo'] == imo]


                    color = color_lst.get(imo, '#000000') 


                    trace = go.Scatter(
                        x=df['corrected_date'],
                        y=df[input_data["Parameter"].values[0]],  
                        mode='markers',
                        name=vessel_name,
                        line=dict(color=color),
                        showlegend=True
                        )
                    traces.append(trace)
                layout = go.Layout(
                        xaxis=dict(title='Month', tickangle=-45),
                        yaxis=dict(title=y_axis_value)

                    ) 
                fig = go.Figure(data=traces, layout=layout)

                fig.show()
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    elif input_data["Report_Type"].values[0]=="Q"and input_data["Multi_Parameter"].values[0]=="normal":
        count = 0
        j = 0
        cumulative_sum = None

        if input_data["Graph_Type"][0] == 'Line':
            if method!='both':
                vessel_imo = list(s['data'].keys())


                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row

                vessel_name = df['vessel_name'].iloc[0]

                df = df.replace(0, np.nan)

                df["date_"] = pd.to_datetime(df["corrected_date"])
                df = df.sort_values(by='date_')

                traces = []
                for imo in vessel_imo:
                    filtered_data = df[df['imo'] == imo]


                    color = color_lst.get(imo, '#000000') 


                    trace = go.Scatter(
                        x=df['corrected_date'],
                        y=df[input_data["Parameter"].values[0]],  
                        mode='lines+markers',
                        name=vessel_name,
                        line=dict(color=color),
                        showlegend=True
                        )
                    traces.append(trace)
                layout = go.Layout(
                        xaxis=dict(title='Quarterly', tickangle=-45),
                        yaxis=dict(title=y_axis_value)

                    ) 
                fig = go.Figure(data=traces, layout=layout)

                fig.show()
                
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            else:
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                combined_data = combined_data[['corrected_date', 'type', parameter]]

                vrs_data = combined_data[combined_data['type'] == 'VRS Data']
                ada_data = combined_data[combined_data['type'] == 'ADA Data']

                fig = go.Figure()

                fig.add_trace(go.Scatter(x=vrs_data['corrected_date'], y=vrs_data[parameter],
                                        mode='lines', line=dict(color='green'), name='VRS Data'))


                fig.add_trace(go.Scatter(x=ada_data['corrected_date'], y=ada_data[parameter],
                                        mode='lines', line=dict(color='red'), name='ADA Data'))


                fig.update_layout(
                                xaxis_title='Quarterly',
                                yaxis_title=y_axis_value,
                                xaxis=dict(tickangle=-45,dtick=1))


                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        elif input_data["Graph_Type"].values[0] == 'Bar':
            if method!='both':
                vessel_imo = list(s['data'].keys())
                combined_data = pd.DataFrame()

                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row
                    combined_data = pd.concat([combined_data, df], ignore_index=True)
                combined_data = combined_data.replace([0], np.nan)
                combined_data["date_"] = pd.to_datetime(combined_data["corrected_date"])
                combined_data_sorted = combined_data.sort_values(by='date_')
                traces = []
                for imo in vessel_imo:
                    filtered_data = combined_data_sorted[combined_data_sorted['imo'] == imo]
                    vessel_name = filtered_data['vessel_name'].iloc[0]
                    color = color_lst.get(imo, '#000000')  # Default color if IMO not in color_lst
                    trace = go.Bar(
                        x=filtered_data['corrected_date'],
                        y=filtered_data[input_data["Parameter"].values[0]],  # Replace 'parameter' with your actual column name
                        name=vessel_name,
                        marker=dict(color=color),
                        showlegend=True
                    )
                    traces.append(trace)

                # Create layout
                layout = go.Layout(
                    xaxis=dict(title='Quarterly', tickangle=-45),
                    yaxis=dict(title=y_axis_value),  # Replace 'Parameter' with your actual parameter
                    legend=dict(title='Vessel Name', x=1.05, y=1, traceorder="normal", font=dict(size=10))
                )

                fig = go.Figure(data=traces, layout=layout)
                fig.show()
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            else:

                color_map = {'VRS Data': 'green', 'ADA Data': 'red'}

                # Create traces for each type

                traces = []
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                    combined_data = combined_data.replace([0], np.nan)
                print(combined_data)

                for type_value, group in combined_data.groupby('type'):

                    trace = go.Bar(

                        x=group['corrected_date'],

                        y=group[input_data["Parameter"][0]],

                        name=type_value,

                        marker=dict(color=color_map.get(type_value))  # Set color based on type

                    )

                    traces.append(trace)

                # Define the layout

                layout = go.Layout(


                    xaxis=dict(title='Quarterly'),

                    yaxis=dict(title=input_data["Parameter"][0])

                )

                # Create the figure

                fig = go.Figure(data=traces, layout=layout)
                fig.update_layout(xaxis=dict( tickangle=-45))

                # Show the chart


                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        elif input_data["Graph_Type"].values[0] == 'Scatter':
            if method=='both':
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                # Extracting specific columns
                combined_data = combined_data[['corrected_date', 'type', parameter]]

                # Filtering data for VRS and ADA separately
                vrs_data = combined_data[combined_data['type'] == 'VRS Data']
                ada_data = combined_data[combined_data['type'] == 'ADA Data']

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=vrs_data['corrected_date'], y=vrs_data[parameter],
                                        mode='markers', marker=dict(color='green'), name='VRS Data'))

                fig.update_layout( xaxis_title='Quarterly', yaxis_title=y_axis_value)
                fig.update_layout(xaxis=dict( tickangle=-45))

                fig.add_trace(go.Scatter(x=ada_data['corrected_date'], y=ada_data[parameter],
                                        mode='markers', marker=dict(color='red'), name='ADA Data'))




                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            else:
                vessel_imo = list(s['data'].keys())


                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row

                vessel_name = df['vessel_name'].iloc[0]

                df = df.replace(0, np.nan)

                df["date_"] = pd.to_datetime(df["corrected_date"])
                df = df.sort_values(by='date_')

                traces = []
                for imo in vessel_imo:
                    filtered_data = df[df['imo'] == imo]


                    color = color_lst.get(imo, '#000000') 


                    trace = go.Scatter(
                        x=df['corrected_date'],
                        y=df[input_data["Parameter"].values[0]],  
                        mode='markers',
                        name=vessel_name,
                        line=dict(color=color),
                        showlegend=True
                        )
                    traces.append(trace)
                layout = go.Layout(
                        xaxis=dict(title='Quarterly', tickangle=-45),
                        yaxis=dict(title=y_axis_value)

                    ) 
                fig = go.Figure(data=traces, layout=layout)

                fig.show()

                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    elif input_data["Report_Type"].values[0]=="Y"and input_data["Multi_Parameter"].values[0]=="normal":

        count = 0
        j = 0
        cumulative_sum = None

        if input_data["Graph_Type"].values[0] == 'Line':
            if method!='both':
                vessel_imo = list(s['data'].keys())


                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row

                vessel_name = df['vessel_name'].iloc[0]

                df = df.replace(0, np.nan)

                df["date_"] = pd.to_datetime(df["corrected_date"])
                df = df.sort_values(by='date_')

                traces = []
                for imo in vessel_imo:
                    filtered_data = df[df['imo'] == imo]


                    color = color_lst.get(imo, '#000000') 


                    trace = go.Scatter(
                        x=df['corrected_date'],
                        y=df[input_data["Parameter"].values[0]],  
                        mode='lines+markers',
                        name=vessel_name,
                        line=dict(color=color),
                        showlegend=True
                        )
                    traces.append(trace)
                layout = go.Layout(
                        xaxis=dict(title='Yearly', tickangle=-45),
                        yaxis=dict(title=y_axis_value)

                    ) 
                fig = go.Figure(data=traces, layout=layout)

                fig.show()
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            else:
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                combined_data = combined_data[['corrected_date', 'type', parameter]]

                vrs_data = combined_data[combined_data['type'] == 'VRS Data']
                ada_data = combined_data[combined_data['type'] == 'ADA Data']

                fig = go.Figure()

                fig.add_trace(go.Scatter(x=vrs_data['corrected_date'], y=vrs_data[parameter],
                                        mode='lines', line=dict(color='green'), name='VRS Data'))


                fig.add_trace(go.Scatter(x=ada_data['corrected_date'], y=ada_data[parameter],
                                        mode='lines', line=dict(color='red'), name='ADA Data'))


                fig.update_layout(
                                xaxis_title='Yearly',
                                yaxis_title=y_axis_value,
                                xaxis=dict(tickangle=-45))


                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        elif input_data["Graph_Type"].values[0] == 'Bar':
            if method!='both':
                vessel_imo = list(s['data'].keys())
                combined_data = pd.DataFrame()

                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row
                    combined_data = pd.concat([combined_data, df], ignore_index=True)
                combined_data = combined_data.replace([0], np.nan)
                combined_data["date_"] = pd.to_datetime(combined_data["corrected_date"])
                combined_data_sorted = combined_data.sort_values(by='date_')
                traces = []
                for imo in vessel_imo:
                    filtered_data = combined_data_sorted[combined_data_sorted['imo'] == imo]
                    if not filtered_data.empty:
                        vessel_name = filtered_data['vessel_name'].iloc[0]
                    else:
                        continue
                    
                    vessel_name = filtered_data['vessel_name'].iloc[0]
                    color = color_lst.get(imo, '#000000')  # Default color if IMO not in color_lst
                    trace = go.Bar(
                        x=filtered_data['corrected_date'],
                        y=filtered_data[input_data["Parameter"].values[0]],  # Replace 'parameter' with your actual column name
                        name=vessel_name,
                        marker=dict(color=color),
                        showlegend=True
                    )
                    traces.append(trace)

                # Create layout
                layout = go.Layout(
                    xaxis=dict(title='Yearly', tickangle=-45),
                    yaxis=dict(title=y_axis_value),  # Replace 'Parameter' with your actual parameter
                    legend=dict(title='Vessel Name', x=1.05, y=1, traceorder="normal", font=dict(size=10))
                )

                fig = go.Figure(data=traces, layout=layout)
              
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            else:

                color_map = {'VRS Data': 'green', 'ADA Data': 'red'}

                # Create traces for each type

                traces = []
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                    combined_data = combined_data.replace([0], np.nan)
                print(combined_data)

                for type_value, group in combined_data.groupby('type'):

                    trace = go.Bar(

                        x=group['corrected_date'],

                        y=group[input_data["Parameter"][0]],

                        name=type_value,

                        marker=dict(color=color_map.get(type_value))  # Set color based on type

                    )

                    traces.append(trace)

                # Define the layout

                layout = go.Layout(


                    xaxis=dict(title='Yearly'),

                    yaxis=dict(title=y_axis_value)

                )

                # Create the figure

                fig = go.Figure(data=traces, layout=layout)
                fig.update_layout(xaxis=dict( tickangle=-45))

                # Show the chart


                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        elif input_data["Graph_Type"].values[0] == 'Scatter':
            if method=='both':
                combined_data = pd.DataFrame()
                for i in s['data']:
                    data = pd.DataFrame.from_dict(s['data'][i])
                    combined_data = pd.concat([combined_data, data], ignore_index=True)
                # Extracting specific columns
                combined_data = combined_data[['corrected_date', 'type', parameter]]

                # Filtering data for VRS and ADA separately
                vrs_data = combined_data[combined_data['type'] == 'VRS Data']
                ada_data = combined_data[combined_data['type'] == 'ADA Data']

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=vrs_data['corrected_date'], y=vrs_data[parameter],
                                        mode='markers', marker=dict(color='green'), name='VRS Data'))

                fig.update_layout( xaxis_title='Yearly', yaxis_title=y_axis_value)
                fig.update_layout(xaxis=dict( tickangle=-45))

                fig.add_trace(go.Scatter(x=ada_data['corrected_date'], y=ada_data[parameter],
                                        mode='markers', marker=dict(color='red'), name='ADA Data'))




                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            else:
                vessel_imo = list(s['data'].keys())


                for imo, data in s['data'].items():
                    df = pd.DataFrame.from_dict(data)
                    df['imo'] = imo  # Add IMO number to each row

                vessel_name = df['vessel_name'].iloc[0]

                df = df.replace(0, np.nan)

                df["date_"] = pd.to_datetime(df["corrected_date"])
                df = df.sort_values(by='date_')

                traces = []
                for imo in vessel_imo:
                    filtered_data = df[df['imo'] == imo]

    #     ####### Multi Parameter############
    # elif input_data["Mode"].values[0]=="vessel" and  input_data["Report_Type"].values[0]=="D" and input_data["Multi_Parameter"].values[0]=="multiple":

    #             color = color_lst.get(imo, '#000000') 


    #             trace = go.Scatter(
    #                 x=data_1['corrected_date'],
    #                 y=data_1[input_data["Parameter"].values[0]],  
    #                 mode='markers',
    #                 name=vessel_name,
    #                 line=dict(color=color),
    #                 showlegend=True
    #                 )
    #             traces.append(trace)
    #             layout = go.Layout(
    #                     xaxis=dict(title='Yearly', tickangle=-45),
    #                     yaxis=dict(title=y_axis_value)

    #                 ) 
    #             fig = go.Figure(data=traces, layout=layout)

           

    #             plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})







    ####### Multi Parameter############
    elif input_data["Mode"].values[0]=="vessel" and  input_data["Report_Type"].values[0]=="D" and input_data["Multi_Parameter"].values[0]=="multiple":
            data_1["corrected_date"]= pd.to_datetime(data_1["corrected_date"], format='%d %b %Y')
        
            lst = data_1['corrected_date'].unique().tolist()
            date_range = pd.to_datetime(lst).max() - pd.to_datetime(lst).min()
            colors = [color_lst.get(param, '#000000') for param in parameter_list]
    
            if input_data["Graph_Type"].values[0] == 'Line':
                traces = []
                for i in range(Parameter_len):
                    trace = go.Scatter(
                        x=data_1['corrected_date'], 
                        y=data_1[parameter_list[i]], 
                        mode='lines', 
                        name=parameter_list[i],
                        line=dict(color=colors[i])
                    )
                    traces.append(trace)
                
                layout = go.Layout(
                    title='Daily Time Series Line Plot',
                    xaxis=dict(title='Date', tickangle=45),
                    yaxis=dict(title='Value'),
                    legend=dict(x=1, y=1, xanchor='right')
                )
                
                fig = go.Figure(data=traces, layout=layout)
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
                
    
            elif input_data["Graph_Type"].values[0] == 'Bar':
                traces = []
                
                if input_data["Bar_Type"].values[0] == 'stacked':
                    fig = go.Figure()
                    bottom = np.zeros(len(data_1))
                    for i, parameter in enumerate(parameter_list):
                        fig.add_trace(go.Bar(
                            x=data_1['corrected_date'], 
                            y=data_1[parameter],
                            name=parameter,
                            marker_color=colors[i]
                        ))
                else:
                    # Side-by-side bars
                    fig = go.Figure()
                    for i, parameter in enumerate(parameter_list):
                        fig.add_trace(go.Bar(
                            x=data_1['corrected_date'], 
                            y=data_1[parameter],
                            name=parameter,
                            marker_color=colors[i],
                            xaxis='x',
                            yaxis='y'
                        ))
                
                layout = go.Layout(
                    title='Daily Time Series Bar Plot',
                    xaxis=dict(title='Date', tickangle=45),
                    yaxis=dict(title='Value'),
                    barmode='stack' if input_data["Bar_Type"].values[0] == 'stacked' else 'group',
                    legend=dict(x=1, y=1, xanchor='right')
                )
                
                fig.update_layout(layout)
                fig.write_image("./images/Data_monitoring_Time_Series_Bar.png")
                fig.show()
    
            elif input_data["Graph_Type"].values[0] == 'Scatter':
                traces = []
                for i in range(Parameter_len):
                    trace = go.Scatter(
                        x=data_1['corrected_date'], 
                        y=data_1[parameter_list[i]], 
                        mode='markers', 
                        name=parameter_list[i],
                        marker=dict(color=colors[i])
                    )
                    traces.append(trace)
                
                layout = go.Layout(
                    title='Daily Time Series Scatter Plot',
                    xaxis=dict(title='Date', tickangle=45),
                    yaxis=dict(title='Value'),
                    legend=dict(x=1, y=1, xanchor='right')
                )
                
                fig = go.Figure(data=traces, layout=layout)
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

                fig.clf()

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
            traces = []
            for i in range(Parameter_len):
                trace = go.Scatter(
                    x=data_1['corrected_date'], 
                    y=data_1[parameter_list[i]], 
                    mode='lines', 
                    name=parameter_list[i],
                    line=dict(color=colors[i])
                )
                traces.append(trace)
            
            layout = go.Layout(
                title='Monthly Time Series Line Plot',
                xaxis=dict(title='Monthly', tickangle=45),
                yaxis=dict(title='Value'),
                legend=dict(x=1, y=1, xanchor='right')
            )
            
            fig = go.Figure(data=traces, layout=layout)
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    
        elif input_data["Graph_Type"].values[0] == 'Bar':
            if input_data["Bar_Type"].values[0] == 'stacked':
                fig = go.Figure()
                for i, parameter in enumerate(parameter_list):
                    fig.add_trace(go.Bar(
                        x=data_1['corrected_date'], 
                        y=data_1[parameter],
                        name=parameter,
                        marker_color=colors[i]
                    ))
                layout = go.Layout(
                    title='Monthly Time Series Bar Plot (Stacked)',
                    xaxis=dict(title='Date', tickangle=45),
                    yaxis=dict(title='Value'),
                    barmode='stack',
                    legend=dict(x=1, y=1, xanchor='right')
                )
            else:
                fig = go.Figure()
                for i, parameter in enumerate(parameter_list):
                    fig.add_trace(go.Bar(
                        x=data_1['corrected_date'], 
                        y=data_1[parameter],
                        name=parameter,
                        marker_color=colors[i]
                    ))
                layout = go.Layout(
                    title='Monthly Time Series Bar Plot (Grouped)',
                    xaxis=dict(title='Date', tickangle=45),
                    yaxis=dict(title='Value'),
                    barmode='group',
                    legend=dict(x=1, y=1, xanchor='right')
                )
            
            fig.update_layout(layout)
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

            # fig.show()
    
        elif input_data["Graph_Type"].values[0] == 'Scatter':
            traces = []
            for i in range(Parameter_len):
                trace = go.Scatter(
                    x=data_1['corrected_date'], 
                    y=data_1[parameter_list[i]], 
                    mode='markers', 
                    name=parameter_list[i],
                    marker=dict(color=colors[i])
                )
                traces.append(trace)
            
            layout = go.Layout(
                title='Monthly Time Series Scatter Plot',
                xaxis=dict(title='Date', tickangle=45),
                yaxis=dict(title='Value'),
                legend=dict(x=1, y=1, xanchor='right')
            )
            
            fig = go.Figure(data=traces, layout=layout)
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    
    elif input_data["Mode"].values[0]=="vessel" and input_data["Report_Type"].values[0]=="Q" and input_data["Multi_Parameter"].values[0]=="multiple":
        
        # Correct the quarter format in the 'corrected_date' column
        data_1['corrected_date'] = data_1['corrected_date'].astype(str).str.replace(r'(\d{4})(Q\d)', r'\1 - \2', regex=True)
        # Assign quarter labels
        data_1['quarter'] = pd.PeriodIndex(data_1['corrected_date'], freq='Q')
        
        # Generate unique quarters and calculate date range
        quarters = data_1['quarter'].unique().tolist()
        date_range = data_1['quarter'].max().end_time - data_1['quarter'].min().start_time
        
        colors = [color_lst.get(param, '#000000') for param in parameter_list]
        
        # Plot Line Graph
        if input_data["Graph_Type"].values[0] == 'Line':
            traces = []
            for i in range(Parameter_len):
                trace = go.Scatter(
                    x=data_1['corrected_date'], 
                    y=data_1[parameter_list[i]], 
                    mode='lines', 
                    name=parameter_list[i],
                    line=dict(color=colors[i])
                )
                traces.append(trace)
            
            layout = go.Layout(
                title='Quarterly Time Series Line Plot',
                xaxis=dict(title='Quarterly', tickangle=45),
                yaxis=dict(title='Value'),
                legend=dict(x=1, y=1, xanchor='right')
            )
            
            fig = go.Figure(data=traces, layout=layout)
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        
        # Bar Graph
        elif input_data["Graph_Type"].values[0] == 'Bar':
            if input_data["Bar_Type"].values[0] == 'stacked':
                fig = go.Figure()
                for i, parameter in enumerate(parameter_list):
                    fig.add_trace(go.Bar(
                        x=data_1['corrected_date'], 
                        y=data_1[parameter],
                        name=parameter,
                        marker_color=colors[i]
                    ))
                layout = go.Layout(
                    title='Quarterly Time Series Bar Plot (Stacked)',
                    xaxis=dict(title='Quarter', tickangle=45),
                    yaxis=dict(title='Value'),
                    barmode='stack',
                    legend=dict(x=1, y=1, xanchor='right')
                )
            else:
                fig = go.Figure()
                for i, parameter in enumerate(parameter_list):
                    fig.add_trace(go.Bar(
                        x=data_1['corrected_date'], 
                        y=data_1[parameter],
                        name=parameter,
                        marker_color=colors[i]
                    ))
                layout = go.Layout(
                    title='Quarterly Time Series Bar Plot (Grouped)',
                    xaxis=dict(title='Quarter', tickangle=45),
                    yaxis=dict(title='Value'),
                    barmode='group',
                    legend=dict(x=1, y=1, xanchor='right')
                )
            
            fig.update_layout(layout)
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
           
        
        # Scatter Plot
        elif input_data["Graph_Type"].values[0] == 'Scatter':
            traces = []
            for i in range(Parameter_len):
                trace = go.Scatter(
                    x=data_1['corrected_date'], 
                    y=data_1[parameter_list[i]], 
                    mode='markers', 
                    name=parameter_list[i],
                    marker=dict(color=colors[i])
                )
                traces.append(trace)
            
            layout = go.Layout(
                title='Quarterly Time Series Scatter Plot',
                xaxis=dict(title='Quarter', tickangle=45),
                yaxis=dict(title='Value'),
                legend=dict(x=1, y=1, xanchor='right')
            )
            
            fig = go.Figure(data=traces, layout=layout)
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    
    elif input_data["Mode"].values[0]=="vessel" and input_data["Report_Type"].values[0]=="Y" and input_data["Multi_Parameter"].values[0]=="multiple":
                lst = data_1['corrected_date'].unique().tolist()
                date_range = pd.to_datetime(lst).max() - pd.to_datetime(lst).min()
                colors = [color_lst.get(param, '#000000') for param in parameter_list]
    
                if input_data["Graph_Type"].values[0] == 'Line':
                    traces = []
                    for i in range(Parameter_len):
                        trace = go.Scatter(
                            x=data_1['corrected_date'], 
                            y=data_1[parameter_list[i]], 
                            mode='lines', 
                            name=parameter_list[i],
                            line=dict(color=colors[i])
                        )
                        traces.append(trace)
                    
                    layout = go.Layout(
                        title='Yearly Time Series Line Plot',
                        xaxis=dict(title='Date', tickangle=45),
                        yaxis=dict(title='Value'),
                        legend=dict(x=1, y=1, xanchor='right')
                    )
                    
                    fig = go.Figure(data=traces, layout=layout)
                    fig.write_image("./images/Data_monitoring_Time_Series_Line.png")
    
                elif input_data["Graph_Type"].values[0] == 'Bar':
                    if input_data["Bar_Type"].values[0] == 'stacked':
                        fig = go.Figure()
                        for i, parameter in enumerate(parameter_list):
                            fig.add_trace(go.Bar(
                                x=data_1['corrected_date'], 
                                y=data_1[parameter],
                                name=parameter,
                                marker_color=colors[i]
                            ))
                        layout = go.Layout(
                            title='Yearly Time Series Bar Plot (Stacked)',
                            xaxis=dict(title='Date', tickangle=45),
                            yaxis=dict(title='Value'),
                            barmode='stack',
                            legend=dict(x=1, y=1, xanchor='right')
                        )
                    else:
                        fig = go.Figure()
                        for i, parameter in enumerate(parameter_list):
                            fig.add_trace(go.Bar(
                                x=data_1['corrected_date'], 
                                y=data_1[parameter],
                                name=parameter,
                                marker_color=colors[i]
                            ))
                        layout = go.Layout(
                            title='Yearly Time Series Bar Plot (Grouped)',
                            xaxis=dict(title='Date', tickangle=45),
                            yaxis=dict(title='Value'),
                            barmode='group',
                            legend=dict(x=1, y=1, xanchor='right')
                        )
                    
                    fig.update_layout(layout)
                    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
                    plt.clf()
    
                elif input_data["Graph_Type"].values[0] == 'Scatter':
                    traces = []
                    for i, parameter in enumerate(parameter_list):
                        trace = go.Scatter(
                            x=data_1['corrected_date'], 
                            y=data_1[parameter],
                            mode='markers', 
                            name=parameter,
                            marker=dict(color=colors[i])
                        )
                        traces.append(trace)
                    
                    layout = go.Layout(
                        title='Yearly Time Series Scatter Plot',
                        xaxis=dict(title='Date', tickangle=45),
                        yaxis=dict(title='Value'),
                        legend=dict(x=1, y=1, xanchor='right')
                    )
                    
                    fig = go.Figure(data=traces, layout=layout)
                    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})




                
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Time Series</title>
        <style>
            body {{
                text-align: center;
            }}
            h1 {{
                color: #193185;
            }}
            h2{{
                color: #193185;
            }}
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                
            }}
            
      
            .plot_div{{
                        width: 100%;
                        
                        justify-content: center;
            }}
                
                
            
            hr {{border-width: 3px;}}
            
            
        
        </style>
    </head>
    <body>
        {image_tag}
        <h1>
            {d+' DAILY REPORT' if report_type == 'D' else
          d+' MONTHLY REPORT' if report_type == 'M' else
          d+' QUARTERLY REPORT' if report_type == 'Q' else
          d+' YEARLY REPORT' }
       
        </h1>
        <br>
        <br>
        <hr>
 
 
        <div class="info">
         {"<p> Vessel: " + vessel_names + "</p>" if vessel_mode == 'vessel' else
        "<p> Class: " + vessel_names + "</p>" if vessel_mode == 'class' else
        "<p> TEU Group: " + group + "</p>" if vessel_mode == 'teu' else
        "<p> Multi Vessel: " + vessel_names  + "</p>"}
        <p>Monitoring period : {mindate} TO {maxdate}</p>
        
        </div>
        <hr>
        {plot_div}
        </body>
    </html>
    """

    file_name = 'datamonitoring_timeseries_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)


@router.post('/api/v1/html/datamonitoring/loaddia/{imo}')
async def index(info:Request, imo:str =None,types:str = None,method:str = None,mcr_value:float = None,engine_power_limit_1:str = None , engine_power_limit_2:str = None , engine_rpm_limit_1:str  = None, engine_rpm_limit_2:str = None,vessel_name:str = None,new_mcr_rpm:str = None, new_mcr_power:str = None, mcr_rpm:str = None , mcr_power:str = None , period_start:str = None , period_end:str = None,vdm_db: AsyncSession = Depends(get_vdm_db_async)):
    
    s = await info.json()
    # data_scatter = pd.DataFrame(s["data"]["data"][imo])    
    # data_curve = pd.DataFrame(s['data']['LoadDiagramData'])
    # required_curve_columns = ['shaft_speed','pover_load','p_continuous','max_speed','prop_curve_s','prop_curve_l','prop_curve_bp']
    # if all(col in data_curve.columns for col in required_curve_columns):

    #     data_curve = data_curve[['shaft_speed','pover_load','p_continuous','max_speed','prop_curve_s','prop_curve_l','prop_curve_bp']].astype(float)
    #     data_curve = data_curve.sort_values(by='shaft_speed')
    #     data_curve = data_curve.replace([''], np.nan)
    #     data_curve = data_curve.dropna(how='all')


    fig = go.Figure()
    plot_div1 = plot_div2 = plot_div3 = ""


    imo_lst = list(s['data']['data'].keys()) 
    custom_colors = ['red', 'green', 'cyan', 'blue', 'violet', 'brown', 'yellow', 'pink', 'gray', 'orange']
    for j, imo in enumerate(imo_lst):
        data_scatter = pd.DataFrame(s["data"]["data"][imo])    
        data_curve = pd.DataFrame(s['data']['LoadDiagramData'])
        required_curve_columns = ['shaft_speed', 'pover_load', 'p_continuous', 'max_speed', 'prop_curve_s', 'prop_curve_l', 'prop_curve_bp']

        if types != 'both':
            if method == 'class':
                required_curve_columns = ['shaft_speed', 'pover_load', 'p_continuous', 'max_speed', 'prop_curve_s', 'prop_curve_l', 'prop_curve_bp']
                colorPallet=await vessel_color(vdm_db)
                for ld_key, imos in s['data']['LoadDiagramData']['plot_points_imos_list'].items():

                    # Create a Plotly figure

                    fig = go.Figure()
                
                    legend_labels = set()
                
                    for imo in imos:

                        if imo in imo_lst:

                            # Scatter data

                            data_scatter = pd.DataFrame(s["data"]["data"][imo])

                            # Curve data

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

                                    'Prop Curve BP': ('shaft_speed', 'prop_curve_bp', '#54eb77')

                                }
                
                                # Add curves to the Plotly figure

                                for curve_name, (x_col, y_col, color) in curves.items():

                                    if curve_name not in legend_labels:

                                        fig.add_trace(go.Scatter(

                                            x=data_curve[x_col],

                                            y=data_curve[y_col],

                                            mode='lines',

                                            name=curve_name,

                                            line=dict(color=color)

                                        ))

                                        legend_labels.add(curve_name)

                                    else:

                                        fig.add_trace(go.Scatter(

                                            x=data_curve[x_col],

                                            y=data_curve[y_col],

                                            mode='lines',

                                            showlegend=False,

                                            line=dict(color=color)

                                        ))
                
                            # Scatter plot for data_scatter

                            if not data_scatter.empty and 'vessel_name' in data_scatter.columns:

                                data_scatter = data_scatter[['type', 'vessel_name', 'imo', 'rpm', 'power_kw', 'me_load', 'rpm_loaddia']]

                                label = data_scatter['vessel_name'].values[0]

                                vessel_imo = data_scatter['imo'].tolist()
                
                                # Map colors to the corresponding 'imo' values

                                color = [colorPallet.get(imo, '#000000') for imo in vessel_imo]  # Default to black if no color found
                
                                fig.add_trace(go.Scatter(

                                    x=data_scatter['rpm_loaddia'],

                                    y=data_scatter['me_load'],

                                    mode='markers',

                                    marker=dict(color=color),

                                    name=label if label not in legend_labels else None

                                ))

                                legend_labels.add(label)
                
                                # Highlight new curve point if present

                                new_curve = s['data']['LoadDiagramData'].get('chart_data', {}).get(ld_key, [])

                                if new_curve:

                                    x_value = new_curve[0].get('x', None)

                                    y_value = new_curve[0].get('y', None)

                                    if x_value is not None and y_value is not None:

                                        fig.add_trace(go.Scatter(

                                            x=[x_value],

                                            y=[y_value],

                                            mode='markers',

                                            marker=dict(color='yellow', size=10),

                                            name=f'New RPM and Power {ld_key}'

                                        ))
                
                    # Update layout

                    fig.update_layout(

                        title=f'Load Diagram - {ld_key}',

                        xaxis_title='RPM (%)',

                        yaxis_title='Power (kW%)',

                        legend=dict(x=1.05, y=1, traceorder="normal"),

                        margin=dict(l=50, r=300, t=50, b=50)

                    )

                    if ld_key == 'loaddiagram_1':  # Modify this condition based on how you want to divide your plots
                        plot_div1 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
                        print("plot_div1plot_div1plot_div1plot_div1plot_div1")
                    elif ld_key == 'loaddiagram_2':
                        plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

                    elif ld_key == 'loaddiagram_3':
                        plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

              
                    print("plot_div1plot_div1plot_div1plot_div1plot_div1")


            else: # vessel
                if types == 'vrs':
                    data_scatter_vrs = data_scatter[data_scatter['type'] == 'VRS Data']
                    vessel_name = data_scatter_vrs['vessel_name'].values[0]
                    fig.add_trace(go.Scatter(x=data_scatter_vrs['rpm_loaddia'], y=data_scatter_vrs['me_load'], mode='markers', marker=dict(color='green'), name="VRS Data"))

                elif types == 'egoship':
                    data_scatter_ada = data_scatter[data_scatter['type'] == 'ADA Data']
                    vessel_name = data_scatter_ada['vessel_name'].values[0]
                    fig.add_trace(go.Scatter(x=data_scatter_ada['rpm_loaddia'], y=data_scatter_ada['me_load'], mode='markers', marker=dict(color='red'), name="ADA Data"))

                new_curve = pd.DataFrame(s['data']['LoadDiagramData'])
                new_curve = new_curve['scatter_chart'].values[-1]
                if new_curve:
                    x_value = new_curve[0].get('x', None)
                    y_value = new_curve[0].get('y', None)

                    if x_value is not None and y_value is not None:
                        fig.add_trace(go.Scatter(x=[x_value], y=[y_value], mode='markers', marker=dict(color='yellow'), name='New Power and RPM'))

        elif types == 'both':
            for ld_key, imos in s['data']['LoadDiagramData']['plot_points_imos_list'].items():

    # Create a Plotly figure
                fig = go.Figure()

                legend_labels = []  # Reset legend_labels for each plot
                for imo in imos:
                    if imo in imo_lst:
                        data_scatter_imo = pd.DataFrame(s["data"]['data'][imo])
                        if not data_scatter_imo.empty and 'vessel_name' in data_scatter_imo.columns:
                            data_scatter_imo = data_scatter_imo[['type', 'vessel_name', 'imo', 'rpm', 'power_kw', 'me_load', 'rpm_loaddia']]
                            data_scatter_vrs = data_scatter_imo[data_scatter_imo['type'] == 'VRS Data']
                            data_scatter_ada = data_scatter_imo[data_scatter_imo['type'] == 'ADA Data']

                            if f'{ld_key} VRS Data' not in legend_labels:
                                fig.add_trace(go.Scatter(
                                    x=data_scatter_vrs['rpm_loaddia'],
                                    y=data_scatter_vrs['me_load'],
                                    mode='markers',
                                    marker=dict(color='#43c72c'),
                                    name='VRS Data'
                                ))
                                legend_labels.append(f'{ld_key} VRS Data')
                            else:
                                fig.add_trace(go.Scatter(
                                    x=data_scatter_vrs['rpm_loaddia'],
                                    y=data_scatter_vrs['me_load'],
                                    mode='markers',
                                    marker=dict(color='#43c72c'),
                                    showlegend=False
                                ))

                            if f'{ld_key} ADA Data' not in legend_labels:
                                fig.add_trace(go.Scatter(
                                    x=data_scatter_ada['rpm_loaddia'],
                                    y=data_scatter_ada['me_load'],
                                    mode='markers',
                                    marker=dict(color='#ba1c41'),
                                    name='ADA Data'
                                ))
                                legend_labels.append(f'{ld_key} ADA Data')
                            else:
                                fig.add_trace(go.Scatter(
                                    x=data_scatter_ada['rpm_loaddia'],
                                    y=data_scatter_ada['me_load'],
                                    mode='markers',
                                    marker=dict(color='#ba1c41'),
                                    showlegend=False
                                ))

                # New curve
                new_curve = s['data']['LoadDiagramData'].get('chart_data', {}).get(ld_key, [])
                if new_curve:
                    x_value = new_curve[0].get('x', None)
                    y_value = new_curve[0].get('y', None)
                    if x_value is not None and y_value is not None:
                        fig.add_trace(go.Scatter(
                            x=[x_value],
                            y=[y_value],
                            mode='markers',
                            marker=dict(color='yellow'),
                            name=f'New RPM and Power {ld_key}'
                        ))

                # Plotting the curves
                data_curve = pd.DataFrame(s['data']['LoadDiagramData']['chart_data'][ld_key])
                if all(col in data_curve.columns for col in required_curve_columns):
                    data_curve = data_curve[required_curve_columns].astype(float)
                    data_curve = data_curve.sort_values(by='shaft_speed')
                    data_curve = data_curve.replace([''], np.nan)
                    data_curve = data_curve.dropna(how='all')
                    fig.add_trace(go.Scatter(x=data_curve['shaft_speed'], y=data_curve['pover_load'], mode='lines', name='P Overload', line=dict(color='red')))
                    fig.add_trace(go.Scatter(x=data_curve['shaft_speed'], y=data_curve['p_continuous'], mode='lines', name='P Continuous', line=dict(color='#2f7dad')))
                    fig.add_trace(go.Scatter(x=data_curve['max_speed'], y=data_curve['pover_load'], mode='lines', name='Max Speed', line=dict(color='#36dbe0')))
                    fig.add_trace(go.Scatter(x=data_curve['shaft_speed'], y=data_curve['prop_curve_s'], mode='lines', name='Prop Curve S', line=dict(color='green')))
                    fig.add_trace(go.Scatter(x=data_curve['shaft_speed'], y=data_curve['prop_curve_l'], mode='lines', name='Prop Curve L', line=dict(color='#b036e0')))
                    fig.add_trace(go.Scatter(x=data_curve['shaft_speed'], y=data_curve['prop_curve_bp'], mode='lines', name='Prop Curve BP', line=dict(color='#54eb77')))
                

                # Update layout
                fig.update_layout(
                    title=f"Load Diagram {ld_key}",
                    xaxis_title="RPM (%)",
                    yaxis_title="Power (kW%)",
                    
                    
                    legend=dict(x=1, y=1, traceorder='normal', orientation='v', bgcolor='rgba(255, 255, 255, 0.5)'),
                    autosize=False,
                    width=1200,
                    height=900
                )
                if ld_key == 'loaddiagram_1':  # Modify this condition based on how you want to divide your plots
                    plot_div1 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
                elif ld_key == 'loaddiagram_2':
                    plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
                elif ld_key == 'loaddiagram_3':
                    plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    if types == 'both':
        if method == 'class':
            html_content = f"""
            <!DOCTYPE html>
            <html>

            <head>
                <title>Load Diagram Report</title>
                <style>
                body {{
                        text-align: center;
                        font-family: 'Roboto', sans-serif;
                        color: #333;
                        background-color: #fff;
                    }}
                    
                    h1 {{
                        color: #193185;
                        font-size: 36px;
                        margin-bottom: 20px;
                    }}

                    h2 {{
                        color: #193185;
                        font-size: 30px; 
                    }}

                    img {{
                        width: 200px; /* Make the image larger */
                        float: right;
                    }}

                    .info {{
                        text-align: left;
                        margin-left: 20px;
                        display: flex;
                        font-size: 16px;
                        font-weight: bold;/* Increase font size for the information */
                    }}


                    .second-info {{
                        margin-left: 100px;
                    }}

                    .plot_div {{
                        width: 70%; /* Increase width of the plot_div */
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin: auto; /* Center the plot_div */
                    }}

                    .rectangles-container {{
                        display: flex;
                        justify-content: space-evenly;
                        align-items: center;
                        margin-bottom: 20px;
                    }}

                    hr {{
                        border-width: 3px;
                        border-color: #33;
                        margin-top: 20px;
                        border-style: solid; /* Add border style */
                    }}
                    
                .rectangle {{
                    min-width: 200px;
                    padding: 15px;
                    border: 2px solid #193185;
                    margin-right: 20px;
                    color: white;
                    text-align: center;
                    background-color: #193185; /* Use the same background color for all rectangles */
                    border-radius: 8px;
                    box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.2);
                    }}

                    th {{
                        background: blue;
                        color: white;
                        height: 41px;
                    }}
                </style>
            </head>

            <body>
                <br>
                <br>
                {image_tag}
                <br>
                <br>
                <h1>Load Diagram Report</h1>
                <hr>

                <!-- Add information in HTML format -->
                <div class="info">
                    <div class='first-info'>
                        <p style="font-size: 18px;">CLASS NAME: {vessel_name}</p>
                        <p style="font-size: 18px;">MONITORING PERIOD: {period_start} to {period_end}</p>
                    </div>
                </div>
                <hr>
                <br>
                <h2>Load Diagram</h2>
                <br>        <br>        <br>

        """
            
            # Dynamically adding the load diagram plots

            if ld_key == "loaddiagram_3":
                html_content += f"""

                    {plot_div1} <br><br><br>

                    {plot_div2} <br><br><br>

                    {plot_div3} <br><br>

                """

            elif ld_key == "loaddiagram_2":

                html_content += f"""

                    {plot_div1} <br><br><br>

                    {plot_div2} <br><br><br>

                """

            else:

                html_content += f"""

                    {plot_div1}

                """
            
            # Closing tags for the HTML content

            html_content += """
            </div>
            </div>
            <br>
            <br>
            </body>
            
                </html>

                """
 
            
              
        else:
            html_content = f"""
            <!DOCTYPE html>
            <html>

            <head>
                <title>Load Diagram Report</title>
                <style>
                body {{
                        text-align: center;
                        font-family: 'Roboto', sans-serif;
                        color: #333;
                        background-color: #fff;
                    }}
                    
                    h1 {{
                        color: #193185;
                        font-size: 36px;
                        margin-bottom: 20px;
                    }}

                    h2 {{
                        color: #193185;
                        font-size: 30px; 
                    }}

                    img {{
                        width: 200px; /* Make the image larger */
                        float: right;
                    }}

                    .info {{
                        text-align: left;
                        margin-left: 20px;
                        display: flex;
                        font-size: 16px;
                        font-weight: bold;/* Increase font size for the information */
                    }}


                    .second-info {{
                        margin-left: 100px;
                    }}

                    .plot_div {{
                        width: 70%; /* Increase width of the plot_div */
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin: auto; /* Center the plot_div */
                    }}

                    .rectangles-container {{
                        display: flex;
                        justify-content: space-evenly;
                        align-items: center;
                        margin-bottom: 20px;
                    }}

                    hr {{
                        border-width: 3px;
                        border-color: #33;
                        margin-top: 20px;
                        border-style: solid; /* Add border style */
                    }}
                    
                .rectangle {{
                    min-width: 200px;
                    padding: 15px;
                    border: 2px solid #193185;
                    margin-right: 20px;
                    color: white;
                    text-align: center;
                    background-color: #193185; /* Use the same background color for all rectangles */
                    border-radius: 8px;
                    box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.2);
                    }}

                    th {{
                        background: blue;
                        color: white;
                        height: 41px;
                    }}
                </style>
            </head>

            <body>
                <br>
                <br>
                {image_tag}
                <br>
                <br>
                <h1>Load Diagram Report</h1>
                <hr>

                <!-- Add information in HTML format -->
                <div class="info">
                    <div class='first-info'>
                        <p style="font-size: 18px;">VESSEL NAME: {vessel_name}</p>
                        <p style="font-size: 18px;">MONITORING PERIOD: {period_start} to {period_end}</p>
                    </div>
                </div>
                <hr>
                <br>
                <h2>Load Diagram</h2>
                <div class="plot_div">
                    {plot_div1}
                </div>

                <br>        <br>        <br>
                    <div class="plot_div">
                    {plot_div2}       
                    </div> <br>        <br>        <br>
                    <div class="plot_div">
                    {plot_div3}        <br>        <br>
                    </div>
            
                <br>
                <br>
                <br>
                <br>
                
                <!-- Add the rectangles container with conditional styling -->
                <div class="rectangles-container">
                    <div class="rectangle engine-power">
                        <p>Engine Power: {mcr_power} kW; RPM: {mcr_rpm}</p>
                    </div>
                    <div class="rectangle engine-rpm">
                        <p>Engine Power Limited: {new_mcr_power}; Engine RPM Limited: {new_mcr_rpm}</p>
                    </div>
                </div>
                <br>
                <br>
            </body>

            </html>
            """    
    else:
        
        html_content = f"""
        <!DOCTYPE html>
        <html>

        <head>
            <title>Load Diagram Report</title>
            <style>
            body {{
                    text-align: center;
                    font-family: 'Roboto', sans-serif;
                    color: #333;
                    background-color: #fff;
                }}
                
                h1 {{
                    color: #193185;
                    font-size: 36px;
                    margin-bottom: 20px;
                }}

                h2 {{
                    color: #193185;
                    font-size: 30px; 
                }}

                img {{
                    width: 200px; /* Make the image larger */
                    float: right;
                }}

                .info {{
                    text-align: left;
                    margin-left: 20px;
                    display: flex;
                    font-size: 16px;
                    font-weight: bold;/* Increase font size for the information */
                }}


                .second-info {{
                    margin-left: 100px;
                }}

                .plot_div {{
                    width: 70%; /* Increase width of the plot_div */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: auto; /* Center the plot_div */
                }}

                .rectangles-container {{
                    display: flex;
                    justify-content: space-evenly;
                    align-items: center;
                    margin-bottom: 20px;
                }}

                hr {{
                    border-width: 3px;
                    border-color: #33;
                    margin-top: 20px;
                    border-style: solid; /* Add border style */
                }}
                
            .rectangle {{
                min-width: 200px;
                padding: 15px;
                border: 2px solid #193185;
                margin-right: 20px;
                color: white;
                text-align: center;
                background-color: #193185; /* Use the same background color for all rectangles */
                border-radius: 8px;
                box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.2);
                }}

                th {{
                    background: blue;
                    color: white;
                    height: 41px;
                }}
            </style>
        </head>

        <body>
            <br>
            <br>
            {image_tag}
            <br>
            <br>
            <h1>Load Diagram Report</h1>
            <hr>

            <!-- Add information in HTML format -->
            <div class="info">
                <div class='first-info'>
                    <p style="font-size: 18px;">VESSEL NAME: {vessel_name}</p>
                    <p style="font-size: 18px;">MONITORING PERIOD: {period_start} to {period_end}</p>
                </div>
            </div>
            <hr>
            <br>
            <h2>Load Diagram</h2>
            <div class="plot_div">
                {plot_div1}
            </div>

            
        
            <br>
            <br>
            <br>
            <br>
            <!-- Add the rectangles container with conditional styling -->
            <div class="rectangles-container">
                <div class="rectangle engine-power">
                    <p>Engine Power: {mcr_power} kW; RPM: {mcr_rpm}</p>
                </div>
                <div class="rectangle engine-rpm">
                    <p>Engine Power Limited: {new_mcr_power}; Engine RPM Limited: {new_mcr_rpm}</p>
                </div>
            </div>
            <br>
            <br>
        </body>

        </html>
        """

    # Save the HTML content to a file

    file_name = 'datamonitoring_loaddia_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)


@router.post('/api/v1/html/eeoi/yearwise/emission/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None, year:str = None):
    s = await info.json()
    data1 = pd.DataFrame.from_dict(s['table1'])
    data1 = data1[['fuel_cons_details', 'Fuel(HS)', 'Fuel (LS)', 'Fuel (MDO)', 'Fuel (MGO)']]
    data1 = data1.rename(columns={'fuel_cons_details': 'FUEL CONS DETAILS'})
    data1 = data1.astype('str')

    data2 = pd.DataFrame.from_dict(s['reported_data'])
    data2 = data2[['index', 'Value']]
    data2 = data2.rename(columns={'index': 'PARAMETER', 'Value': 'VALUE'})
    data2 = data2.astype('str')

    data3 = pd.DataFrame.from_dict(s['eechartdata'])


    #1st Graph EEOI & Voyage Number
    fig = px.bar(data3, x='voyage_no', y='eeoi',
            labels={'eeoi': 'EEOI', 'voyage_no': 'Voyage Number'},
            title='EEOI(gm/Ton-miles)',
            height=500, width=800)

    # Add value labels above the bars
    fig.update_traces(texttemplate='%{y}', textposition='outside')

    # Customize the layout if needed
    fig.update_traces(marker=dict(color='red'))
    fig.update_layout(
    xaxis_title_text='Voyage Number',
    yaxis_title_text='EEOI',
    title=dict(
        text='EEOI(gm/Ton-miles)',
        font=dict(family="Roboto, sans-serif", size=20, color="black"),
        x=0.5,  # Center the title horizontally
    ),
    font=dict(family="Roboto, sans-serif", size=15, color="black"),  # Larger font size and stylish font
    xaxis=dict(showgrid=False),  # Hide x-axis grid
    yaxis=dict(showgrid=False),
    width=1070,
    height=550
    )
    # Show the plot
    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    fig = px.bar(data3, x='voyage_no', y='eeoiTEU',
                labels={'eeoiTEU': 'EEOI TEU', 'voyage_no': 'Voyage Number'},
                title='EEOI TEU (gm/TEU-miles)',
                height=500, width=800)
    
    # Add value labels above the bars
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    
    # Customize the layout
    fig.update_traces(marker=dict(color='green'))
    fig.update_layout(
        xaxis_title_text='Voyage Number',
        yaxis_title_text='EEOI TEU',
        title=dict(
            text='EEOI TEU (gm/TEU-miles)',
            font=dict(family="Roboto, sans-serif", size=20, color="black"),
            x=0.5,  # Center the title horizontally
        ),
        font=dict(family="Roboto, sans-serif", size=15, color="black"),  # Larger font size and stylish font
        xaxis=dict(showgrid=False),  # Hide x-axis grid
        yaxis=dict(showgrid=False),
        width=1070,
        height=550
    )
    
    # Show the plot
    fig.show()
    
    # Generate the HTML div for embedding the plot
    plot_div4 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    #2nd Graph CO2 & Voyage Number
    fig = px.bar(data3, x='voyage_no', y='co2',
            labels={'co2': 'Total CO2', 'voyage_no': 'Voyage Number'},
            title='Total CO2',
            height=500, width=800)

    # Add value labels above the bars
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')

    # Customize the layout if needed
    fig.update_traces(marker=dict(color='orange'))
    fig.update_layout(
    xaxis_title_text='Voyage Number',
    yaxis_title_text='Total CO2',
    title=dict(
        text='Total CO2',
        font=dict(family="Roboto, sans-serif", size=20, color="black"),
        x=0.5,  # Center the title horizontally
    ),
    font=dict(family="Roboto, sans-serif", size=15, color="black"),  # Larger font size and stylish font
    xaxis=dict(showgrid=False),  # Hide x-axis grid
    yaxis=dict(showgrid=False),
    width=1070,
    height=600

    )

    # Show the plot
    plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    #3rd Graph Fuel & Voyage Number

    fig = px.bar(data3, x='voyage_no', y='totalfo',
                labels={'totalfo': 'Total FO', 'voyage_no': 'Voyage Number'},
                title='Total FO Consumption',
                height=500, width=800)

    # Add value labels above the bars
    
    fig.update_traces(texttemplate='%{y}', textposition='outside')

    # Customize the layout if needed
    fig.update_traces(marker=dict(color='gold'))
    fig.update_layout(
    xaxis_title_text='Voyage Number',
    yaxis_title_text='Total FO',
    title=dict(
        text='Total FO Consumption',
        font=dict(family="Roboto, sans-serif", size=20, color="black"),
        x=0.5,  # Center the title horizontally
    ),
    font=dict(family="Roboto, sans-serif", size=15, color="black"),  # Larger font size and stylish font
    xaxis=dict(showgrid=False),  # Hide x-axis grid
    yaxis=dict(showgrid=False),
    width=1080,
    height=560
    )

    # Show the plot
    plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    html_table = "<table border='1'>\n"
    # Create table header
    html_table += "<tr>"
    for col in data1.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr>\n"

    # Iterate over rows
    for index, row in data1.iterrows():
        html_table += "<tr>"
        for value in row:
            html_table += f"<td>{value}</td>"
        html_table += "</tr>\n"

    html_table += "</table>"

    html_table2 = "<table border='1'>\n"
    # Create table header
    html_table2 += "<tr>"
    for col in data2.columns:
        html_table2 += f"<th>{col}</th>"
    html_table2 += "</tr>\n"

    # Iterate over rows
    for index, row in data2.iterrows():
        html_table2 += "<tr>"
        for value in row:
            html_table2 += f"<td>{value}</td>"
        html_table2 += "</tr>\n"

    html_table2 += "</table>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ANNUAL VOYAGE REPORT</title>
        <style>
            body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            h1 {{
                color: #193185;
                font-size: 36px;
                margin-bottom: 20px;
            }}
            h2{{
                color: #193185;
                font-size: 30px; 

            }}
            img {{
                width: 100px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 16px;
                font-weight: bold;
            }}
            
            .second-info{{ margin-left: 100px;}}
            table {{
                margin: 20px auto;
                    width: 65%;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            
                table, tr, td {{height: 30px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%;
                        display: flex;
                        justify-content: center;
            }}
            
            hr {{
                border-width: 3px;
                border-color: #33;
                margin-top: 20px;
                border-style: solid; /* Add border style */
            }}
            
                
            th {{
        background: blue;
        color: white;
        height: 41px;
    }}
        </style>
    </head>
    <body>
        {image_tag}
        <br>
        <br>
        <br>
        <br>
        <h1>ANNUAL VOYAGE REPORT </h1>    <hr>
        <div class="info">
            <div class='first-info'>
                <p style="font-size: 18px;">VESSEL NAME: {vessel_name}</p>
                <p style="font-size: 18px;">CALENDAR YEAR: {year}</p>
            </div>
        </div>
        <hr>
        <br>
        <h2>FUEL CONSUMPTION DETAILS</h2>
        <!-- Add the centered and bigger table -->
        {html_table}
        <br>
        <br>
        {html_table2}
        <br>
        <br>
        <br>
        <h2>VOYAGE VS EEOI</h2>
        <div class="plot_div">
            {plot_div}
        </div>
        <br>
        <br>
        <h2>VOYAGE VS EEOI TEU</h2>
        <div class="plot_div">
            {plot_div4}
        </div>
        <br>
        <br>
        <h2>VOYAGE VS CO2</h2>
        <div class="plot_div">
            {plot_div2}
        </div>
        <br>
        <br>
        <h2>VOYAGE VS FO CONSUMPTION</h2>
        <div class="plot_div">
            {plot_div3}
        </div>    
        <br>
    </body>
    </html>
    """
    
    file_name = 'eeoi_yearwise_emission'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)

@router.post('/api/v1/html/nox/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None ,tabname:str = None, selection:str = None,method:str =None,start_date:str = None ,end_date:str = None, year:str = None,fleet:str =None,types:str = None,vsl:str=None):
    import pandas as pd
    s = await info.json()
    if year=='null':
        start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d %b %Y')
        end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d %b %Y')

        date  = start_date + " TO " + end_date
    else:
        date=year
    
    #html

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


    import plotly.express as px
    import plotly.graph_objects as go

    fig = go.Figure()

    for column in pivoted_data1.columns[1:]:
        color = 'green' if 'AE' in column else 'red'
        fig.add_trace(go.Bar(x=pivoted_data1['date_month'], y=pivoted_data1[column], name=column,marker_color=color))

    fig.update_layout(
        barmode='stack',
        xaxis_tickangle=-45,
        xaxis=dict(tickmode='linear', tick0=0, dtick=2),
        xaxis_title='Date',
        yaxis_title='Total NOx Daily (MT)',
        legend_title=None,
        #font=dict(weight='bold'),
        width=1200,
        height=600
    )

    plot_div1 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    #done 1

    data2 = pd.DataFrame.from_dict(s['data']['ae_me']['monthly_data_me_ae'])
    data2 = data2.replace([0], np.nan)
    pivoted_data2 = data2.pivot(index='date_month',columns='category',values='nox_value').reset_index()
    pivoted_data2['month_number'] = pivoted_data2['date_month'].apply(lambda x: datetime.strptime(x, "%Y-%B").month)
    pivoted_data2['year'] = pivoted_data2['date_month'].apply(lambda x: datetime.strptime(x, "%Y-%B").year)
    pivoted_data2 = pivoted_data2.sort_values(by=['year','month_number'])
    pivoted_data2 = pivoted_data2.drop(['year','month_number'],axis=1)



    import plotly.graph_objects as go
    import pandas as pd

    # Assuming pivoted_data2 is a DataFrame with the necessary data

    fig = go.Figure()

    for column in pivoted_data2.columns[1:]:
        color = 'green' if 'AE' in column else 'red'
        fig.add_trace(go.Bar(
            x=pivoted_data2['date_month'],
            y=pivoted_data2[column],
            name=str(column),marker_color=color
        ))

    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=pivoted_data2['date_month'],
            #ticktext=pivoted_data2['date_month'].dt.strftime('%Y-%m-%d'),
            tickangle=-45,
        ),
        yaxis=dict(title='Total NOx Monthly (MT)'),
        barmode='stack',
        showlegend=True,
    )

    fig.update_xaxes(type='category')  # Specify that 'date_month' should be treated as a category
    fig.update_layout(
        width=1200,
        height=600)
    # Show the figure
    plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    #done 2

    data3 = pd.DataFrame.from_dict(s['data']['ae_me']['daily_data_ae'])
    data3 = data3.replace([0], np.nan)
    data3 = data3[(data3['category']=='AE 1') | (data3['category']=='AE 2')| (data3['category']=='AE 3')| (data3['category']=='AE 4')|(data3['category']=='AE 5')]
    pivoted_data3 = data3.pivot(index='date_month',columns='category',values='ae_nox_value').reset_index()
    lst = data3['date_month'].unique().tolist()
    pivoted_data3 = pivoted_data3.set_index('date_month')
    pivoted_data3 = pivoted_data3.loc[lst] 
    pivoted_data3 = pivoted_data3.reset_index()

    fig = go.Figure()

    for column in pivoted_data3.columns[1:]:
        if 'AE 1' in column:
            color = 'red'
        elif 'AE 2' in column:
            color = 'green'
        elif 'AE 3' in column:
            color = 'blue'
        elif 'AE 4' in column:
            color = 'yellow'
        else:
            color = 'violet'
        fig.add_trace(go.Bar(
            x=pivoted_data3['date_month'],
            y=pivoted_data3[column],
            name=str(column),marker_color=color
        ))

    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=pivoted_data3['date_month'],
            #ticktext=pivoted_data3['date_month'].dt.strftime('%Y-%m-%d'),
            tickangle=-45,
        ),
        yaxis=dict(title='Total NOx Daily (MT)'),
        barmode='stack',
        showlegend=True,
    )

    fig.update_xaxes(type='category')  # Specify that 'date_month' should be treated as a category
    fig.update_layout(
        width=1200,
        height=600)
    # Show the figure
    plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
    #done 3

    data4 = pd.DataFrame.from_dict(s['data']['ae_me']['monthly_data_ae'])
    data4 = data4.replace([0], np.nan)
    pivoted_data4 = data4.pivot(index='date_month',columns='category',values='ae_nox_value').reset_index()
    pivoted_data4['month_number'] = pivoted_data4['date_month'].apply(lambda x: datetime.strptime(x, "%Y-%B").month)
    pivoted_data4['year'] = pivoted_data4['date_month'].apply(lambda x: datetime.strptime(x, "%Y-%B").year)


    pivoted_data4 = pivoted_data4.sort_values(by=['year','month_number'])
    pivoted_data4 = pivoted_data4.drop(['year','month_number'],axis=1)


    fig = go.Figure()

    for column in pivoted_data4.columns[1:]:
        if 'AE 1' in column:
            color = 'red'
        elif 'AE 2' in column:
            color = 'green'
        elif 'AE 3' in column:
            color = 'blue'
        elif 'AE 4' in column:
            color = 'yellow'
        else:
            color = 'violet'
        fig.add_trace(go.Bar(
            x=pivoted_data4['date_month'],
            y=pivoted_data4[column],
            name=str(column),marker_color=color
        ))

    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=pivoted_data4['date_month'],
            #ticktext=pivoted_data4['date_month'].dt.strftime('%Y-%m-%d'),
            tickangle=-45,
        ),
        yaxis=dict(title='Total NOx Monthly (MT)'),
        barmode='stack',
        showlegend=True,
    )

    fig.update_xaxes(type='category')  # Specify that 'date_month' should be treated as a category
    fig.update_layout(
        width=1200,
        height=600)
    # Show the figure
    plot_div4 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    #done 4





    # url="http://192.168.54.16:5200/api/v1/nox/emission/9625970"  #emission data
    # p=requests.get(url , headers =  headers).json()

    data5 = pd.DataFrame.from_dict(s['data']['emission']['data'])
    data5.fillna('', inplace=True)
    # data5['name'] = vsl

    data5 = data5[['imo','vessel_name','nox_me_ev','nox_ae1_ev','nox_ae2_ev','nox_ae3_ev','nox_ae4_ev','nox_ae5_ev']]
    data5.rename(columns = {'imo':'IMO No', 'vessel_name':'Vessel Name','nox_me_ev':'Main Engine','nox_ae1_ev':'AE 1','nox_ae2_ev':'AE 2','nox_ae3_ev':'AE 3','nox_ae4_ev':'AE4','nox_ae5_ev':'AE 5'}, inplace = True)
    data5 = data5.astype('str')
    print("777777777777777")



    if 'wise' in s['data'] and 'data' in s['data']['wise'] and s['data']['wise']['data']:
        # Check if 'latest' key exists and contains records
        if 'latest' in s['data']['wise']['data'][0] and s['data']['wise']['data'][0]['latest']:
            data6 = pd.DataFrame.from_dict([s['data']['wise']['data'][0]['latest']])
            data6.fillna('', inplace=True)
            data6 = data6.transpose().reset_index()
            data7 = pd.DataFrame.from_dict([s['data']['wise']['data'][0]['monthly']])
            data7 = data7.transpose().reset_index()
            data8 = pd.DataFrame.from_dict([s['data']['wise']['data'][0]['yearly']])
            data8 = data8.transpose().reset_index()
            data6['NOx this Month'] = data7[0]
            data6['NOx this Year'] = data8[0]
            data6.rename(columns = {0:'NOx latest', 'index':'Name'}, inplace = True)
            latest_date = data6['NOx latest'].values[0]
            latest_month = data6['NOx this Month'].values[0]
            latest_year = data6['NOx this Year'].values[0]
            data6.rename(columns={'NOx latest': str('NOx latest') + ' ' +latest_date+ '(MT)','NOx this Month': str('NOx this Month') + ' ' +latest_month+ '(MT)','NOx this Year': str('Nox this Year') + ' ' +latest_year+ '(MT)'},inplace = True)
            data6 = data6.iloc[1:]
            data6['Name'] = data6['Name'].replace(['me_total_nox_imo','ae_total_nox_imo', 'ae1_nox_imo','ae2_nox_imo','ae3_nox_imo','ae4_nox_imo','ae5_nox_imo'], ['Main Engine', 'AE Total', 'AE 1','AE 2','AE 3','AE 4','AE 5'])
            data6 = data6.reindex([2,1,3,4,5,6,7])
            data6 = data6.astype('str')

            print("Latest records exist")
        else:
            pass
    else:
        pass



    #html table

    if 'data6' in locals() or 'data6' in globals():
        html_table6 = "<table border='1'>\n"
        # Create table header
        html_table6 += "<tr>"
        for col in data6.columns:
            html_table6 += f"<th>{col}</th>"
        html_table6 += "</tr>\n"
        # Iterate over rows
        for index, row in data6.iterrows():
            html_table6 += "<tr>"
            for value in row:
                html_table6 += f"<td>{value}</td>"
            html_table6 += "</tr>\n"

        html_table6 += "</table>"
        print("Data exists:", data6)
    else:
        d1 = {
        'Name': ['Main Engine', 'AE Total', 'AE 1', 'AE 2', 'AE 3', 'AE 4', 'AE 5'],
        'NOx latest': '' * 7,
        'NOx this month': '' * 7,
        'NOx this year': '' * 7
        }

        df = pd.DataFrame(d1)

        df
        html_table6 = "<table border='1'>\n"
        # Create table header
        html_table6 += "<tr>"
        for col in df.columns:
            html_table6 += f"<th>{col}</th>"
        html_table6 += "</tr>\n"
        # Iterate over rows
        for index, row in df.iterrows():
            html_table6 += "<tr>"
            for value in row:
                html_table6 += f"<td>{value}</td>"
            html_table6 += "</tr>\n"

        html_table6 += "</table>"
        
        pass
        # Your code to execute if data6 does not exist
        print("Data does not exist. Passing...")





    html_table5 = "<table border='1'>\n"
    # Create table header
    html_table5 += "<tr>"
    for col in data5.columns:
        html_table5 += f"<th>{col}</th>"
    html_table5 += "</tr>\n"

    # Iterate over rows
    for index, row in data5.iterrows():
        html_table5 += "<tr>"
        for value in row:
            html_table5 += f"<td>{value}</td>"
        html_table5 += "</tr>\n"

    html_table5 += "</table>"

        
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>nox_report</title>
        <style>
            body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            h1 {{
                color: #193185;
                font-size:36px;
                margin-bottom: 20px;
            }}
            h2{{
                color: #193185;
                font-siz: 30px;
            }}
            
            
            
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 18px;/* Increase font size for the information */
            }}
            .second-info{{ margin-left: 100px;}}
            table {{
                margin: 20px auto;
                    width: 511px;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            .graph{{margin-center}}
            
                table, tr, td {{height: 34px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%; /*increase width of plot_div */
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin: auto; /* center the plot_div
            }}
                .rectangles-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;  /* Optional margin between rectangles and table */
            }}
            hr {{border-width: 3px;}}
            .rectangle {{
                min-width: 200px;
                #height: 100px;
                padding: 12px;
                border: 2px solid;
                margin-right: 20px;  /* Optional margin between rectangles */
                color: white;
                #display: flex;
                #flex-direction: row;
                #align-items: 'center';
                #justify-content: 'center'
                text-align: 'center';
            }}
            /* Apply additional styles based on conditions */
            .gain-positive {{
                background-color: #17d41a;
                border-color: #008000;
            }}
            .gain-negative {{
                background-color: #ff0000;
                border-color: #800000;
            }}
            th {{
        background: blue;
        color: white;
        height: 41px;
    }}
    </style>
    </head>

    <body>
        <br>
        {image_tag}
        <br>
        <h1>
            {'NOx Report'}
        </h1>
        <hr>
        <!--add information in html format -->
    <div class="info">
            
    <pstyle ="font-size:18px">
    {f'Fleet: {fleet}' if tabname == 'Fleet' else
        f'Vessel Name: {vessel_name}' if tabname == 'Vessel' else
        f'Type: {types}' if tabname == 'All' else
        f'Vessel: {vessel_name}'}</p>
    <p style="font-size:18px">Monitoring Period: {date}</p>
    <p style="font-size:18px">Method: {method}</p>

                
        
        </div>
        <hr>
        <br>
        <h2>ME - AE Daily NOx</h2>
        <div class='plot_div'>
    
        
        {plot_div1}
        </div>
        
        <br>
        <br>
        
        
        <div class='plot_div'>
    
        
        {plot_div2}
        </div>
        
        <br>
        <br>

        
        <h2>AE Daily NOx</h2>
        <div class='plot_div'>
    
        
        {plot_div3}
        </div>
        
        <br>
        <br>
        
        <h2>AE Monthly NOx</h2>
        <div class='plot_div'>
    
        
        {plot_div4}
        </div>
        
        <br>
        <br>


        
        <h2>{method} Method Data</h2>
        <!-- Add the centered and bigger table -->
        {html_table6}


        
        
        
        <br>
        <br>
        
        
        <h2>NOx Values</h2>
        
        <!-- Add the centered and bigger table -->
        {html_table5}
        
        
        

        
        <br>
        <br>
        <br>
        

        
        
        
        
    
        
            
        <!-- ... (rest of the body content) ... -->




    </body>
    </html>
    """
    
    
    file_name = 'nox_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)


@router.post('/api/v1/html/datamonitoring/relational/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None ,report_type:str = None, group:str = None,mindate:str = None ,maxdate:str = None, x:str = None,y:str =None,x_axis:str = None,y_axis:str = None,Type:str = None, method:str =None,vdm_db: AsyncSession = Depends(get_vdm_db_async)):
    try:
        imos = vessel_name[-7:]
        if isinstance(imos,[len(imos)==7,int]) == True:
            pass
    except:
        pass  
    s = await info.json()
    
    period=mindate + " to " + maxdate
    
    
    Group_Number=group

    # period="2021-01-01 to 2022-02-01"
    x_input_None=x.upper()
    y_input_None=y.upper()
    None_Heading=x_input_None+" Vs "+y_input_None+" REPORT"
    None_Heading = None_Heading.replace('_', ' ')






    # token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTAwLCJpZGVudGlmaWVyIjoiYWRtaW5AbXNjLmNvbSIsImNzaWQiOiI0ZDRhYzMwNi0zMDBjLTRhOWQtOGUwZC0yM2VjOWQyOWM3NjAiLCJpYXQiOjE3MDY1ODU1ODAsImV4cCI6MTcwNjY3MTk4MH0.XUQdvCqZULEu0PLv3xH81eTpGMKqlkDN9Hr1fLA-24I"
    # headers = {'Authorization': "Bearer {}".format(token)}
    # url_single = "https://msc.oceanix.cloud/api/v1/datamonitoring/data=vrs/group=vessel/period=D/mindate=2023-10-24/maxdate=2024-01-22/imo=9625970"
    # s=requests.get(url_single , headers =  headers).json()
    # s=json.loads(s)



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

    colorPallet=await vessel_color(vdm_db)
    if report_type == "vessel":
        if method!='both':
            for i in s['data']:
                imo = i
            # if column_mapping[x_axis] and column_mapping[y_axis]:
            #     x_axis = column_mapping[x_axis]
            #     y_axis = column_mapping[y_axis]

            DataTable_df = pd.DataFrame.from_dict(s['data'][imos])
            DataTable_df = DataTable_df[DataTable_df[x_axis] != 0]
            DataTable_df = DataTable_df.dropna(subset=[x_axis])
            #DataTable_df = DataTable_df.dropna(subset=[y_axis])
            vessel_name_single_None = DataTable_df[["vessel_name"]]

            color=colorPallet[imos]

            # Create the scatter plot using Plotly Express


            fig = px.scatter(DataTable_df, x=x_axis, y=y_axis, color="vessel_name", 
            color_discrete_map=colorPallet,
            title=f"{x} Vs {y}", labels={x_axis: x, y_axis: y}, size_max=18)


            if Type == "None" or  Type is None:
                fig = px.scatter()

                data = pd.DataFrame.from_dict(s['data'][imos])
                data = data[data[x_axis] != 0]

                fig.update_layout(
                    xaxis_title=x,
                    yaxis_title=y
                )

                fig.add_trace(
                px.scatter(data, x=x_axis, y=y_axis, color="vessel_name",color_discrete_map=colorPallet).update_traces(
                    marker=dict(size=5),
                    selector=dict(mode='markers')
                ).data[0]
            )

                plot_div = fig.to_html(full_html=False)
            elif Type == "Linear":
                # Add linear regression line
                fig.update_traces(marker=dict(size=5))

                fig.update_layout(shapes=[
                dict(
                    type='line',
                    x0=DataTable_df[x_axis].min(),
                    x1=DataTable_df[x_axis].max(),
                    y0=DataTable_df[y_axis].min(),
                    y1=DataTable_df[y_axis].max(),
                    line=dict(color=color, width=3)
                 )
                ])

                fig.update_layout(
                        xaxis_title=x,
                        yaxis_title=y
                    )     
                                                          
                plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            elif Type == "2nd Degree Polynomial" or Type == 'Quad':
                    color = colorPallet[imos]
                    fig.update_traces(marker=dict(size=5))

                    # Create a scatter plot for unique vessel names
                    for vessel_name, group in DataTable_df.groupby("vessel_name"):
                        scatter_trace = go.Scatter(
                            x=group[x_axis],
                            y=group[y_axis],
                            mode='markers',
                            marker=dict(color=colorPallet[vessel_name], size=5),
                            name=vessel_name,  # Replace underscores with spaces for the legend
                            showlegend=False  # Show legend for unique vessel names
                        )
                        fig.add_trace(scatter_trace)

                    # Update layout to change the legend title
                    fig.update_layout(legend_title_text='Vessel') 

                    # Add the quadratic regression line
                    poly_coeffs = np.polyfit(DataTable_df[x_axis], DataTable_df[y_axis], 2)
                    x_vals = np.linspace(DataTable_df[x_axis].min(), DataTable_df[x_axis].max(), 100)
                    y_vals = np.polyval(poly_coeffs, x_vals)

                    line_trace = go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='lines',
                        line=dict(color=color),
                        name='Quadratic Fit',  # Name for the regression line
                        showlegend=False  # Hide from legend
                    )
                    fig.add_trace(line_trace)

                    # Show the figure
                    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

            elif Type == "3rd Degree Polynomial":
                    color = colorPallet[imos]

                    fig.update_traces(marker=dict(size=5))

                    # Create a scatter plot for unique vessel names
                    for vessel_name, group in DataTable_df.groupby("vessel_name"):
                        scatter_trace = go.Scatter(
                            x=group[x_axis],
                            y=group[y_axis],
                            mode='markers',
                            marker=dict(color=colorPallet[vessel_name], size=5),
                            name=vessel_name,
                            showlegend=False  # Set to True to show the legend for unique vessel names
                        )
                        fig.add_trace(scatter_trace)

                    # Update layout to change the legend title
                    fig.update_layout(legend_title_text='Vessel')  # Change this to your desired title

                    # Add the cubic regression line
                    poly_coeffs = np.polyfit(DataTable_df[x_axis], DataTable_df[y_axis], 3)
                    x_vals = np.linspace(DataTable_df[x_axis].min(), DataTable_df[x_axis].max(), 100)
                    y_vals = np.polyval(poly_coeffs, x_vals)

                    line_trace = go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='lines',
                        line=dict(color=color),
                        name='Cubic Fit',  # Name for the regression line
                        showlegend=False  # Hide from legend
                    )

                    fig.add_trace(line_trace)

                    # Show the figure
                    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        else:
            

            for i in s['data']:
                imo = i
                try:
                    DataTable_df = pd.DataFrame.from_dict(s['data'][imos])
                    DataTable_df = DataTable_df[DataTable_df[x_axis] != 0]
                except:
                    continue
                vessel_name_single_None = DataTable_df[["vessel_name"]]
                vrs_data = DataTable_df[DataTable_df['type'] == 'VRS Data']
                ada_data = DataTable_df[DataTable_df['type'] == 'ADA Data']

            fig = px.scatter(DataTable_df, x=x_axis, y=y_axis,size_max=18)

            if Type == "None" or Type is None:
                fig = px.scatter()

                fig.add_trace(
                    go.Scatter(
                        x=ada_data[x_axis],
                        y=ada_data[y_axis],
                        mode='markers',
                        marker=dict(color='red', size=5),
                        name='ADA Data'
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=vrs_data[x_axis],
                        y=vrs_data[y_axis],
                        mode='markers',
                        marker=dict(color='green', size=5),
                        name='VRS Data'
                    )
                )

            elif Type == "Linear":
                fig.add_trace(
                    go.Scatter(
                        x=ada_data[x_axis],
                        y=ada_data[y_axis],
                        mode='markers',
                        marker=dict(color='red', size=5),
                        name='ADA Data'
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=vrs_data[x_axis],
                        y=vrs_data[y_axis],
                        mode='markers',
                        marker=dict(color='green', size=5),
                        name='VRS Data'
                    )
                )

                # Add linear regression lines
                for data, color in [(ada_data, 'red'), (vrs_data, 'green')]:
                    coeffs = np.polyfit(data[x_axis], data[y_axis], 1)
                    x_vals = np.linspace(data[x_axis].min(), data[x_axis].max(), 100)
                    y_vals = np.polyval(coeffs, x_vals)
                    fig.add_trace(
                        go.Scatter(
                            x=x_vals,
                            y=y_vals,
                            mode='lines',
                            line=dict(color=color),
                            name=''
                        )
                    )

            elif Type == "2nd Degree Polynomial" or Type == 'Quad':
                fig.add_trace(
                    go.Scatter(
                        x=ada_data[x_axis],
                        y=ada_data[y_axis],
                        mode='markers',
                        marker=dict(color='red', size=5),
                        name='ADA Data'
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=vrs_data[x_axis],
                        y=vrs_data[y_axis],
                        mode='markers',
                        marker=dict(color='green', size=5),
                        name='VRS Data'
                    )
                )

                # Add quadratic regression lines
                for data, color in [(ada_data, 'red'), (vrs_data, 'green')]:
                    coeffs = np.polyfit(data[x_axis], data[y_axis], 2)
                    x_vals = np.linspace(data[x_axis].min(), data[x_axis].max(), 100)
                    y_vals = np.polyval(coeffs, x_vals)
                    fig.add_trace(
                        go.Scatter(
                            x=x_vals,
                            y=y_vals,
                            mode='lines',
                            line=dict(color=color),name=''
                            
                        )
                    )
                fig.show()

            elif Type == "3rd Degree Polynomial":
                fig.add_trace(
                    go.Scatter(
                        x=ada_data[x_axis],
                        y=ada_data[y_axis],
                        mode='markers',
                        marker=dict(color='red', size=5),
                        name='ADA Data'
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=vrs_data[x_axis],
                        y=vrs_data[y_axis],
                        mode='markers',
                        marker=dict(color='green', size=5),
                        name='VRS Data'
                    )
                )

                # Add cubic regression lines
                for data, color in [(ada_data, 'red'), (vrs_data, 'green')]:
                    coeffs = np.polyfit(data[x_axis], data[y_axis], 3)
                    x_vals = np.linspace(data[x_axis].min(), data[x_axis].max(), 100)
                    y_vals = np.polyval(coeffs, x_vals)
                    fig.add_trace(
                        go.Scatter(
                            x=x_vals,
                            y=y_vals,
                            mode='lines',
                            line=dict(color=color)
                            ,name=''
                        )
                    )
                fig.show()

            plot_div = fig.to_html(full_html=False)

            




        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relational</title>
            <style>
                body {{
                    text-align: center;
                }}
                h1 {{
                    color: #193185;
                }}
                h2{{
                    color: #193185;
                }}
                img {{
                    width: 80px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;

                }}



                .plot_div{{
                            width: 100%;

                            justify-content: center;
                }}



                hr {{border-width: 3px;}}



            </style>
        </head>
        <body>
            {image_tag}
            <h1>
                {None_Heading} 
            </h1>
            <br>
            <br>
            <hr>
            <div class='info'>
            <p> Vessel: {vessel_name_single_None['vessel_name'].values[0]}  </p>
            <p>Monitoring period : {period} </p>

            </div>
            <hr>
            {plot_div}
            </body>
        </html>
        """

        # Save the HTML content to a file
        file_name = 'retational_'+imo+'.html'
        output_file = download_path +file_name
        with open(output_file, 'w',encoding='utf-8') as html_file:
            html_file.write(html_content)

        return FileResponse(path = output_file,filename=file_name)

        
        
        
        

    elif report_type=="teu" or report_type == 'class':
        imo_lst = [i for i in s['data']]
        len_imo_lst = len(imo_lst)
        color_mapping = colorPallet  
        count = 0
        j = 0
        if Type == 'None':
            fig = px.scatter()  # Initialize an empty figure

            for imo in imo_lst:
                clr = color_mapping.get(imo, 'blue')  # Get the color from colorPallet based on the IMO
                
                try:
                    # Extract data for the current IMO and convert to DataFrame
                    data = pd.DataFrame(s['data'][imo])
                    print(f"Processing IMO: {imo}")
                    
                    # Check if x_axis exists in the data
                    if x_axis in data.columns:
                        data = data[data[x_axis] != 0]
                    else:
                        print(f"Column '{x_axis}' not found in data for IMO {imo}. Skipping...")
                        continue

                    # Add scatter trace for the current IMO
                    fig.add_trace(
                        px.scatter(
                            data, 
                            x=x_axis, 
                            y=y_axis, 
                            color="vessel_name", 
                            color_discrete_sequence=[clr]
                        ).update_traces(
                            marker=dict(size=5), 
                            selector=dict(mode='markers')
                        ).data[0]
                    )
                except Exception as e:
                    print(f"Error processing IMO {imo}: {e}")
                    continue

            plot_div = fig.to_html(full_html=False)
                

        elif Type == 'Linear':
            
            fig = px.scatter()

            # count = 0
            # j = 0

            for vessel_name in imo_lst:
                clr = colorPallet.get(vessel_name, 'blue')  # Get color from colorPallet based on IMO
                data = pd.DataFrame.from_dict(s['data'][vessel_name])
                data = data[data[x_axis] != 0]

                scatter = px.scatter(
                    data,
                    x=x_axis,
                    y=y_axis,
                    color='vessel_name',
                    color_discrete_sequence=[clr],
                    opacity=0.7,
                    size_max=20,
                    labels={'vessel_name': 'Vessel Name'}
                )
                fig.add_trace(scatter.data[0])

                regression_line = px.scatter(
                    data,
                    x=x_axis,
                    y=y_axis,
                    trendline='ols',
                    trendline_color_override=clr,
                    opacity=0.7
                )

                #fig.add_trace(scatter['data'][0])
                fig.add_trace(regression_line['data'][1])

                count += 1
                j += 1

            fig.update_layout(
                xaxis=dict(title_text=x_axis),
                yaxis=dict(title_text=y_axis),
                title=dict(text=f"{x} Vs {y}"),
                legend=dict(title=dict(text='Vessel Name')),
                showlegend=True
            )

            plot_div = fig.to_html(full_html=False)

        elif Type == '2nd Degree Polynomial' or Type == 'Quad':
            fig = go.Figure()
            count = 0
            j = 0

            for vessel_name in imo_lst:
                clr = colorPallet.get(vessel_name, 'blue')  # Get color from colorPallet based on IMO
                data = pd.DataFrame.from_dict(s['data'][vessel_name])
                data = data.dropna(subset=[x_axis, y_axis])
                data = data[(data[x_axis] != 0) & (data[y_axis] != 0)]

                if data.empty:
                    print(f"Warning: No valid data for {vessel_name}. Skipping.")
                    continue

                # Scatter plot
                scatter_trace = go.Scatter(
                    x=data[x_axis],
                    y=data[y_axis],
                    mode='markers',
                    marker=dict(color=clr, size=5),name=data['vessel_name'].iloc[0],
                        text=data['vessel_name'] 
                )
                fig.add_trace(scatter_trace)

                # Regression line
                try:
                    reg_coeffs = np.polyfit(data[x_axis], data[y_axis], 2)
                    x_vals = np.linspace(data[x_axis].min(), data[x_axis].max(), 100)
                    y_vals = np.polyval(reg_coeffs, x_vals)

                    reg_line_trace = go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='lines',
                        line=dict(color=clr),
                        name="",
                        showlegend=False
                    )
                    fig.add_trace(reg_line_trace)
                except Exception as e:
                    print(f"Error fitting polynomial regression for {vessel_name}: {e}")
                    continue

                count += 1
                j += 1

            fig.update_layout(
                xaxis=dict(title_text=x_axis),
                yaxis=dict(title_text=y_axis),
                title=dict(text=f"{x} Vs {y}"),
                legend=dict(title=dict(text='Vessel Name')),
                showlegend=True
            )
            # Update traces settings
            fig.update_traces(marker=dict(size=5))

                # Generate the plot
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        

            

        elif Type == '3rd Degree Polynomial':
            fig = go.Figure()
            count = 0
            j = 0

            for vessel_name in imo_lst:
                clr = colorPallet.get(vessel_name, 'blue')  # Get color from colorPallet based on IMO
                data = pd.DataFrame.from_dict(s['data'][vessel_name])
                data = data[data[x_axis] != 0]
                data = data.dropna(subset=[x_axis])
                if data.empty:
                    print(f"Warning: No valid data for {vessel_name}. Skipping.")
                    continue

                # Scatter plot
                scatter_trace = px.scatter(data, x=x_axis, y=y_axis, color='vessel_name', color_discrete_sequence=[clr]).update_traces(name=f'{data["vessel_name"].iloc[0]}')
                fig.add_trace(scatter_trace.data[0])

                # Polynomial fit
                try:
                    poly_coeffs = np.polyfit(data[x_axis], data[y_axis], 3)
                    x_vals = np.linspace(data[x_axis].min(), data[x_axis].max(), 100)
                    y_vals = np.polyval(poly_coeffs, x_vals)

                    line_trace = go.Scatter(x=x_vals, y=y_vals, mode='lines', line=dict(color=clr),name='',showlegend=False)
                    fig.add_trace(line_trace)

                    j += 1
                except Exception as e:
                    print(f"Error fitting polynomial regression for {i}: {e}")
                    continue

            # Update layout
            fig.update_layout(
                xaxis=dict(title_text=x_axis),
                yaxis=dict(title_text=y_axis),
                title=dict(text=f"{x} Vs {y}"),
                legend=dict(title=dict(text='Vessel Name')),
                showlegend=True
            )

            # Show the plot
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relational</title>
            <style>
                body {{
                    text-align: center;
                }}
                h1 {{
                    color: #193185;
                }}
                h2{{
                    color: #193185;
                }}
                img {{
                    width: 80px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;

                }}



                
                .plot_div{{
                            width: 100%;

                            justify-content: center;
                }}



                hr {{border-width: 3px;}}



            </style>
        </head>
        <body>
            {image_tag}
            <h1>
                {None_Heading} 
            </h1>
            <br>
            <br>
            <hr>
            <div class='info'>
            
            {'TEU Value  :' if report_type == 'teu' else 'Class Name  :'} {Group_Number}
            <p>Monitoring period : {period} </p>
            <p>X-axis :{x}</p>
            <p>Y-axis :{y}</p>

            </div>
            <hr>
            {plot_div}
            </body>
        </html>
        """
    # Save the HTML content to a file
        file_name = 'retational_'+imo+'.html'
        output_file = download_path +file_name
        with open(output_file, 'w',encoding='utf-8') as html_file:
            html_file.write(html_content)

        return FileResponse(path = output_file,filename=file_name)
        

    elif report_type=="multi":
        #pdf_name = vessel_name + "DR_Multi_Vessel.pdf"

        # url_multi="https://msc.oceanix.cloud/api/sysapi/api/v1/datamonitoring/data=vrs/group=multi/mindate=2021-01-01/maxdate=2022-02-01/period=D/imo=9228320,9626302,9345908,9360946,9689897,9610640/voycond=Both/status=At Sea/draftmin=5/draftmax=30/sogmin=5/sogmax=35/sfocmin=50/sfocmax=350/seastatemin=0/seastatemax=9/mcrmin=500/mcrmax=100000/slipmin=-30/slipmax=30/stwmin=5/stwmax=35/steamingtimemin=1/steamingtimemax=26/rpmmin=-500/rpmmax=500/loadmin=10/loadmax=100"   
        # s=requests.get(url_multi , headers =  headers).json()
    #.....................................................IMO & COLOR setting......................................................#
        imo_lst = [i for i in s['data']]
        len_imo_lst = len(imo_lst)
        color_mapping = colorPallet  
    #   count=0
    # j=0
        #vessel_name
        count_1 = 0
        for i in s['data']:
            data = pd.DataFrame.from_dict(s['data'][i]) 

            if count_1 != 0:
                data1 = pd.concat([data1,data],axis=0)
            else:
                data1 = data
            count_1 = count_1+1
        data_new=data1[["vessel_name",x_axis,y_axis]]



        data_Vessel_name=data_new["vessel_name"].unique().tolist()
        a = ''
        for l in data_Vessel_name:
            a = a+l+","+" "
        #For removing , 
        b = a.rstrip(" ")
        vessels_name = b.rstrip(",")

        count=0
        j=0
        
        if Type == 'None':
            fig = px.scatter()
            count = 0
            j = 0

            for i, imo in enumerate(imo_lst):
                clr = color_mapping.get(imo, 'blue')  # Get the color from colorPallet based on the IMO
                data = pd.DataFrame.from_dict(s['data'][imo])
                data = data[data[x_axis] != 0]
                
                fig.add_trace(
                    px.scatter(data, x=x_axis, y=y_axis, color="vessel_name", color_discrete_sequence=[clr]).update_traces(
                        marker=dict(size=5),
                        selector=dict(mode='markers')
                    ).data[0]
                )
                count += 1
                j += 1

            # Update layout
            fig.update_layout(
                xaxis=dict(title_text=x_axis),
                yaxis=dict(title_text=y_axis),
                showlegend=True
            )

            # Show the plot
            plot_div = fig.to_html(full_html=False)

        elif Type == 'Linear':
            fig = px.scatter()

            count = 0
            j = 0

            for vessel_name in imo_lst:
                clr = colorPallet.get(vessel_name, 'blue')  # Get color from colorPallet based on IMO
                data = pd.DataFrame.from_dict(s['data'][vessel_name])
                data = data[data[x_axis] != 0]

                # Scatter plot
                scatter = px.scatter(
                    data,
                    x=x_axis,
                    y=y_axis,
                    color='vessel_name',
                    color_discrete_sequence=[clr],
                    opacity=0.7,
                    size_max=20,
                    labels={'vessel_name': 'Vessel Name'}
                )

                regression_line = px.scatter(
                    data,
                    x=x_axis,
                    y=y_axis,
                    trendline='ols',
                    trendline_color_override=clr,
                    opacity=0.7
                )

                fig.add_trace(scatter['data'][0])
                fig.add_trace(regression_line['data'][1])

                count += 1
                j += 1

            fig.update_layout(
                xaxis=dict(title_text=x_axis),
                yaxis=dict(title_text=y_axis),
                title=dict(text=f"{x} Vs {y}"),
                legend=dict(title=dict(text='Vessel Name')),
                showlegend=True
            )

            plot_div = fig.to_html(full_html=False)
        if Type == '2nd Degree Polynomial' or Type == 'Quad':
            
            fig = go.Figure()

            count = 0
            j = 0

            for vessel_name in imo_lst:
                clr = colorPallet.get(vessel_name, 'blue')  # Get color from colorPallet based on IMO
                data = pd.DataFrame.from_dict(s['data'][vessel_name])
                data = data.dropna(subset=[x_axis, y_axis])
                data = data[(data[x_axis] != 0) & (data[y_axis] != 0)]
                
                
                # Scatter plot
                scatter_trace = go.Scatter(
                    x=data[x_axis],
                    y=data[y_axis],
                    mode='markers',
                    marker=dict(color=clr, size=5),name=data['vessel_name'].iloc[0],
                        text=data['vessel_name'] 
                )
                fig.add_trace(scatter_trace)

                # Regression line
                reg_coeffs = np.polyfit(data[x_axis], data[y_axis], 2)
                x_vals = np.linspace(data[x_axis].min(), data[x_axis].max(), 100)
                y_vals = np.polyval(reg_coeffs, x_vals)

                reg_line_trace = go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='lines',
                        line=dict(color=clr),
                        name="",
                        showlegend=False
                    )
                fig.add_trace(reg_line_trace)

                count += 1
                j += 1
            fig.update_layout(
            xaxis=dict(title_text=x_axis),
            yaxis=dict(title_text=y_axis),
            title=dict(text=f"{x} Vs {y}"),
            legend=dict(title=dict(text='Vessel Name')),
            showlegend=True
        )
            # Update traces settings
            fig.update_traces(marker=dict(size=5))

            # Generate the plot
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        if Type == '3rd Degree Polynomial':
            fig = go.Figure()
            count = 0
            j = 0

            for vessel_name in imo_lst:
                clr = colorPallet.get(vessel_name, 'blue')  # Get color from colorPallet based on IMO
                data = pd.DataFrame.from_dict(s['data'][vessel_name])
                data = data[data[x_axis] != 0]
                data = data.dropna(subset=[x_axis])


                # Scatter plot
                scatter_trace = px.scatter(data, x=x_axis, y=y_axis, color='vessel_name', color_discrete_sequence=[clr]).update_traces(name=f'{data["vessel_name"].iloc[0]}')
                fig.add_trace(scatter_trace.data[0])

                # Polynomial fit
                poly_coeffs = np.polyfit(data[x_axis], data[y_axis], 3)
                x_vals = np.linspace(data[x_axis].min(), data[x_axis].max(), 100)
                y_vals = np.polyval(poly_coeffs, x_vals)

                line_trace = go.Scatter(x=x_vals, y=y_vals, mode='lines', line=dict(color=clr),name='',showlegend=False)
                fig.add_trace(line_trace)

                j += 1

            # Update layout
            fig.update_layout(
                xaxis=dict(title_text=x_axis),
                yaxis=dict(title_text=y_axis),
                title=dict(text=f"{x} Vs {y}"),
                legend=dict(title=dict(text='Vessel Name')),
                showlegend=True
            )

            # Show the plot
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
    
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title></title>
                <style>
                    body {{
                        text-align: center;
                    }}
                    h1 {{
                        color: #193185;
                    }}
                    h2{{
                        color: #193185;
                    }}
                    img {{
                        width: 80px;
                        float: right;
                    }}
                    .info {{
                        text-align: left;
                        margin-left: 20px;

                    }}



                        
                    .plot_div{{
                                width: 100%;

                                justify-content: center;
                    }}



                    hr {{border-width: 3px;}}



                </style>
            </head>
            <body>
                {image_tag}
                <h1>
                    {None_Heading} 
                </h1>
                <br>
                <br>
                <hr>
                <div class='info'>

                <p>Vessel Names: {vessels_name}</p>
                <p>Monitoring period : {period} </p>
                <p>X-axis :{x}</p>
                <p>Y-axis :{y}</p>

                </div>
                <hr>
                {plot_div}
                </body>
            </html>
            """
    
        file_name = 'retational_'+imo+'.html'
        output_file = download_path +file_name
        with open(output_file, 'w',encoding='utf-8') as html_file:
            html_file.write(html_content)

        return FileResponse(path = output_file,filename=file_name)


# ---------------------------------------------relational multi parameter------------------------------------------------
@router.post('/api/v1/html/datamonitoring/relational_multi')
async def index(info:Request,vessel_name:str = None ,mindate:str = None ,maxdate:str = None, x:str = None,y:str =None,x_axis:str = None,y_axis:str = None):
    print("starting................")

    Multi_Parameter_Relational = await info.json()
    mindate = datetime.strptime(mindate,'%Y-%m-%d').strftime('%d %b %Y')
    maxdate = datetime.strptime(maxdate,'%Y-%m-%d').strftime('%d %b %Y')
    date_obj = [mindate + " TO " + maxdate]

    #__________Input Parameter _________________
    x_input_None=x.upper()
    y_input_None=y.upper()
    None_Heading=x_input_None+" Vs "+y_input_None+" REPORT"
    None_Heading = None_Heading.replace('_', ' ')

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
    multi_data =    Multi_Parameter_Relational['data']

    first_pair = next(iter((multi_data.items())) )

    first_pair[0]



    Parameter_len= len(Y_axis_selection)

    data_1 = pd.DataFrame.from_dict(Multi_Parameter_Relational['data'][first_pair[0]])

    color_lst = ['blue','yellow','red','violet','green','cyan','pink','gray','orange','purple','indigo','magenta']
    new_color_lst_1 = []

    for z in range (0,Parameter_len):
        color_sel = color_lst[z]
        new_color_lst_1.append(color_sel)
    new_color_lst_1 
    #_________Graph______________#
    if input_data_mode =="Single Vessel" and Multi_paramter== "True" :
        fig = go.Figure()

        j = 0
        i = 0
        while i < Parameter_len:
            clr = new_color_lst_1[j]

            fig.add_trace(go.Scatter(x=data_1[X_axis_selection], y=data_1[Y_axis_selection[i]], mode='markers', name=Y_axis_selection[i], marker=dict(color=clr)))

            i += 1
            j += 1

        fig.update_layout(
            xaxis=dict(title=x, titlefont=dict(size=14, color='black', family='Arial, sans-serif'), showgrid=True),
            yaxis=dict(title='Value', titlefont=dict(size=14, color='black', family='Arial, sans-serif'), showgrid=True),
            width=1500,
            height=700
        )
        # 
        plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        
    else:
        print("Wrong Input")

        
        
        
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title></title>
        <style>
            body {{
                text-align: center;
            }}
            h1 {{
                color: #193185;
            }}
            h2{{
                color: #193185;
            }}
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;

            }}



                
            .plot_div{{
                        width: 100%;

                        justify-content: center;
            }}



            hr {{border-width: 3px;}}



        </style>
    </head>
    <body>
        {image_tag}
        <h1>
            RELATIONAL PARAMETER REPORT
        </h1>
        <br>
        <br>
        <hr>
        <div class='info'>

        <p>Vessel Names: {vessel_name}</p>
        <p>Monitoring period : {b} </p>

        </div>
        <hr>
        {plot_div}
        </body>
    </html>
    """
    print(html_content)
    # Save the HTML content to a file
    file_name = 'Retational_Multi_Parameter'+vessel_name+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)


@router.post('/api/v1/html/datamonitoring/data/operationalprofile/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None ,report_type:str = None, group:str = None,mindate:str = None ,maxdate:str = None, x:str = None,y:str =None,x_axis:str = None,y_axis:str = None,Type:str = None,class_name:str = None,date:str = None,types:str=None,vdm_db: AsyncSession = Depends(get_vdm_db_async)):
    import pandas as pd
    mindate = datetime.strptime(mindate,'%Y-%m-%d').strftime('%d %b %Y')
    maxdate = datetime.strptime(maxdate,'%Y-%m-%d').strftime('%d %b %Y')
    date=str(mindate) + " to " + str(maxdate)
    s = await info.json()
    colorPallet= await vessel_color(vdm_db)
        
    plot_div1=None
    plot_div2=None
    plot_div3=None
    plot_div4=None
    plot_div5=None
    plot_div6=None

    if report_type == 'vessel':
        for i in s['data']:
            a = i

        data1 = pd.DataFrame.from_dict(s['data'][a][0]['sog'])
        if 'vesselname' not in data1.columns:
            
            no="No data available."
        else:
            data1['vesselname'] = data1['vesselname'].fillna(data1['vesselname'].mode()[0])
            try:
                data1 = data1[['range','value','vesselname']]
            except:
                pass
            data1 = data1.dropna()
            vessel = data1['vesselname'].values[0]
            color = colorPallet.get(vessel, '#000000') 
            #speed
            fig = px.bar(data1, x="range", y="value", color="range",
                        labels={"range": "Speed (kn)", "value": "Percentage (%)"},
                     
                        template="plotly",
                        color_discrete_sequence=[color],
                        width=800, height=400)
            fig.update_layout(xaxis=dict(tickangle=-45),showlegend=False)
            fig.update_layout(font=dict(family="Arial", size=16, color="RebeccaPurple"))
            
            plot_div1 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        no = None
        data2 = pd.DataFrame.from_dict(s['data'][a][0]['draft'])
        if 'vesselname' not in data2.columns:
            
            no="No data available."
            print(no)
        else:
            data2['vesselname'] = data2['vesselname'].fillna(data2['vesselname'].mode()[0])
            try:
                data2 = data2[['range','value','vesselname']]
            except:
                pass
            data2 = data2.dropna()
            vessel = data1['vesselname'].values[0]
            color = colorPallet.get(vessel, '#000000')
    
            #draft
            fig = px.bar(data2, x="range", y="value", color="vesselname",
                        labels={"range": "Draft (m)", "value": "Percentage (%)"},
                        color_discrete_sequence=[color],
                        template="plotly",
                        width=800, height=400)
            xaxis=dict(tickangle=-45)

            fig.update_layout(font=dict(family="Arial", size=16, color="RebeccaPurple"))
    
            
    
            plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        no = None
        data3 = pd.DataFrame.from_dict(s['data'][a][0]['power'])
  

        
        if 'vesselname' not in data3.columns:
            
            no="No data available."
            print(no)
        else:
            try:
                data3 = data3[['range','value','vesselname']]
            except:
                pass
            data3['vesselname'] = data3['vesselname'].fillna(data3['vesselname'].mode()[0])
            data3 = data3.dropna()
            vessel = data1['vesselname'].values[0]
            color = colorPallet.get(vessel, '#000000')
    
            # Plot if data is available
            fig = px.bar(data3, x="range", y="value", color="vesselname",
                        labels={"range": "Power (kW)", "value": "Percentage (%)"},
                        color_discrete_sequence=[color],
                        template="plotly",
                        width=800, height=400)

            fig.update_layout(font=dict(family="Arial", size=16, color="RebeccaPurple"))
            fig.update_layout(xaxis=dict(tickangle=-45))
            
            plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        
        no = None
        data4 = pd.DataFrame.from_dict(s['data'][a][0]['seastate'])
        
        if 'vesselname' not in data4.columns:
            no="No data available."
            print(no)
        else:
            data4['vesselname'] = data4['vesselname'].fillna(data4['vesselname'].mode()[0])
            try:
                data4 = data4[['range','value','vesselname']]
            except:
                pass
            data4 = data4.dropna()
            vessel = data1['vesselname'].values[0]
            color = colorPallet.get(vessel, '#000000')
    
            #sea state
            fig = px.bar(data4, x="range", y="value", color="vesselname",
                        labels={"range": "SeaState", "value": "Percentage (%)"},
                        color_discrete_sequence=[color],
                        template="plotly",
                        width=800, height=400)

            fig.update_layout(font=dict(family="Arial", size=16, color="RebeccaPurple"))

            
            plot_div4 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        no=None
        data5 = pd.DataFrame.from_dict(s['data'][a][0]['load'])
    
        
        if 'vesselname' not in data5.columns:
            no="No data available."
            print(no)
            
        else:
            data5['vesselname'] = data5['vesselname'].fillna(data5['vesselname'].mode()[0])
            try:
                data5 = data5[['range','value','vesselname']]
            except:
                pass
            data5 = data5.dropna()
            vessel = data1['vesselname'].values[0]
            color = colorPallet.get(vessel, '#000000')
    
            #slip
            fig = px.bar(data5, x="range", y="value", color="vesselname",
                        labels={"range": "Slip", "value": "Percentage (%)"},
                        color_discrete_sequence=[color],
                        template="plotly",
                        width=800, height=400)

            fig.update_layout(font=dict(family="Arial", size=16, color="RebeccaPurple"))
            fig.update_layout(xaxis=dict(tickangle=-45))
            
            plot_div5 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        no=None
        data6 = pd.DataFrame.from_dict(s['data'][a][0]['rpm'])
        print(no)
        if 'vesselname' not in data6.columns:
            no="No data available."
        else:
            data6['vesselname'] = data6['vesselname'].fillna(data6['vesselname'].mode()[0])
            try:
                data6 = data6[['range','value','vesselname']]
            except:
                pass
            data6 = data6.dropna()
            vessel = data1['vesselname'].values[0]
            color = colorPallet.get(vessel, '#000000')
    
            #RPM
            fig = px.bar(data6, x="range", y="value", color="vesselname",
                        labels={"range": "RPM", "value": "Percentage (%)"},
                        color_discrete_sequence=[color],
                        template="plotly",
                        width=800, height=400)

            fig.update_layout(font=dict(family="Arial", size=16, color="RebeccaPurple"))
            fig.update_layout(xaxis=dict(tickangle=-45))
            
            plot_div6 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


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
            data7_org = data7_org.astype('str')
            
            html_table = "<table border='1'>\n"
            # Create table header
            html_table += "<tr>"
            for col in data7_org.columns:
                html_table += f"<th>{col}</th>"
            html_table += "</tr>\n"
            # Iterate over rows
            for index, row in data7_org.iterrows():
                html_table += "<tr>"
                for value in row:
                    html_table += f"<td>{value}</td>"
                html_table += "</tr>\n"

            html_table += "</table>"

        else:

            data8 = pd.DataFrame.from_dict(s['data'][a][0][types]['columns'])
            data8[0] = data8[0].astype('str')
            lst = data8[0].values.tolist()
            data9 = pd.DataFrame.from_dict(s['data'][a][0][types]['index'])
            data9.rename(columns = {0:'Speed/Draft'}, inplace = True)
            data9 = data9.astype('str')
            data10 = pd.DataFrame.from_dict(s['data'][a][0][types]['data'])
            data10.columns = lst
            data10 = data10.astype('str')
            data11 = pd.concat([data9, data10], axis=1, join='inner')
            for i in lst:
                data11[i] = data11[i].apply(lambda x: str(x) + '%')
            data11 = data11.astype('str')
            
            html_table = "<table border='1'>\n"
            # Create table header
            html_table += "<tr>"
            for col in data11.columns:
                html_table += f"<th>{col}</th>"
            html_table += "</tr>\n"
            # Iterate over rows
            for index, row in data11.iterrows():
                html_table += "<tr>"
                for value in row:
                    html_table += f"<td>{value}</td>"
                html_table += "</tr>\n"

            html_table += "</table>"
            
            
    elif report_type == 'class': 

        #input parameters
        # period_start = '2021-01-01'
        # period_end = '2022-02-01'
        # class_name = 'ADITI'

        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NzIsImlkZW50aWZpZXIiOiJhZG1pbkBtdG0uY29tIiwiY3NpZCI6ImEyYjE5NjliLTA1ZjEtNGVkOC1hMDYwLTRmODQzMWI1MjQwZCIsImlhdCI6MTY3MTI1MTY0NSwiZXhwIjoxNjcxMzM4MDQ1fQ.4De3ezhyJ0aiV-5_Gm3uZEUGkR0Hg0_UpfEsuK_SJ7k"
        # headers = {'Authorization': "Bearer {}".format(token)}
        # url="https://msc.oceanix.cloud/api/v1/datamonitoring/operationalprofile/vrs/class/2018-01-02/2018-02-01/ADITI/Both/AT%20SEA/5/30/5/35/50/350/0/9/500/100000/-30/30/5/35/1/26/-500/500/10/100"
        # s=requests.get(url , headers =  headers).json()
        import plotly.graph_objects as go
        import pandas as pd
        count = 0
        for i in s['data']:
            data1 = pd.DataFrame.from_dict(s['data'][i][0]['sog'])
            data1['vesselname'] = data1['vesselname'].fillna(data1['vesselname'].mode()[0])
            try:
                data1 = data1[['range','value','vesselname']]
            except:
                pass
            data1 = data1.dropna()
            vessel = data1['vesselname'].values[0]
            color = colorPallet.get(vessel, '#000000') 
            if count != 0:
                df_sog = pd.concat([df_sog,data1],axis=0)
            else:
                df_sog = data1
            count = count+1

    #     pivoted_sog = df_sog.pivot(index='range',columns='vesselname',values='value').reset_index()   
        df_sog = df_sog.fillna(0)
        list_vsl_sog = df_sog['vesselname'].unique().tolist()

    #     melted_sog = pd.melt(pivoted_sog, id_vars=['range'], value_vars=list_vsl_sog, var_name='vesselname', value_name='value')
        fig = px.bar(df_sog, x='range', y='value', color='vesselname', barmode='group',
                    labels={'range': 'Speed (kn)', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        

        plot_div1 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        

        count = 0
        for i in s['data']:
            data2 = pd.DataFrame.from_dict(s['data'][i][0]['draft'])
            data2['vesselname'] = data2['vesselname'].fillna(data2['vesselname'].mode()[0])
            try:
                data2 = data2[['range','value','vesselname']]
            except:
                pass
            data2 = data2.dropna()
            if count != 0:
                df_draft = pd.concat([df_draft,data2],axis=0)
            else:
                df_draft = data2
            count = count+1

    #     pivoted_draft = df_draft.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_draft = df_draft.fillna(0)   
        list_vsl_draft = df_draft['vesselname'].unique().tolist()

    #     melted_draft = pd.melt(pivoted_draft, id_vars=['range'], value_vars=list_vsl_draft, var_name='vesselname', value_name='value')
        fig = px.bar(df_draft, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Draft (m)', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        
        
        plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data3 = pd.DataFrame.from_dict(s['data'][i][0]['power'])
            data3['vesselname'] = data3['vesselname'].fillna(data3['vesselname'].mode()[0])
            try:
                data3 = data3[['range','value','vesselname']]
            except:
                pass
            data3 = data3.dropna()
            if count != 0:
                df_power = pd.concat([df_power,data3],axis=0)
            else:
                df_power = data3
            count = count+1

    #     pivoted_power = df_power.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_power = df_power.fillna(0)    
        list_vsl_power = df_power['vesselname'].unique().tolist()

    #     melted_power = pd.melt(pivoted_power, id_vars=['range'], value_vars=list_vsl_power, var_name='vesselname', value_name='value')
        fig = px.bar(df_power, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Power (kW)', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data4 = pd.DataFrame.from_dict(s['data'][i][0]['seastate'])
            data4['vesselname'] = data4['vesselname'].fillna(data4['vesselname'].mode()[0])
            try:
                data4 = data4[['range','value','vesselname']]
            except:
                pass
            data4 = data4.dropna()
            if count != 0:
                df_seastate = pd.concat([df_seastate,data4],axis=0)
            else:
                df_seastate = data4
            count = count+1

    #     pivoted_seastate = df_seastate.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_seastate = df_seastate.fillna(0)
        list_vsl_seastate = df_seastate['vesselname'].unique().tolist()
    
    #     melted_seastate = pd.melt(pivoted_seastate, id_vars=['range'], value_vars=list_vsl_seastate, var_name='vesselname', value_name='value')
        fig = px.bar(df_seastate, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'SeaState', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        

        plot_div4 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    

        count = 0
        for i in s['data']:
            data5 = pd.DataFrame.from_dict(s['data'][i][0]['load'])
            data5['vesselname'] = data5['vesselname'].fillna(data5['vesselname'].mode()[0])
            try:
                data5 = data5[['range','value','vesselname']]
            except:
                pass
            data5 = data5.dropna()
            if count != 0:
                df_load = pd.concat([df_load,data5],axis=0)
            else:
                df_load = data5
            count = count+1

    #     pivoted_load = df_load.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_load = df_load.fillna(0)    
        list_vsl_load = df_load['vesselname'].unique().tolist()


    
    #     melted_load = pd.melt(pivoted_load, id_vars=['range'], value_vars=list_vsl_load, var_name='vesselname', value_name='value')
        fig = px.bar(df_load, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Slip', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div5 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data6 = pd.DataFrame.from_dict(s['data'][i][0]['rpm'])
            data6['vesselname'] = data6['vesselname'].fillna(data6['vesselname'].mode()[0])
            try:
                data6 = data6[['range','value','vesselname']]
            except:
                pass
            data6 = data6.dropna()
            if count != 0:
                df_rpm = pd.concat([df_rpm,data6],axis=0)
            else:
                df_rpm = data6
            count = count+1

    #     pivoted_rpm = df_rpm.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_rpm = df_rpm.fillna(0)   
        list_vsl_rpm = df_rpm['vesselname'].unique().tolist()
        
    #     melted_rpm = pd.melt(pivoted_rpm, id_vars=['range'], value_vars=list_vsl_rpm, var_name='vesselname', value_name='value')
        fig = px.bar(df_rpm, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'RPM', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div6 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        
        count = 0
        for i in s['data']:
            #clr = new_color_lst[j]
            data7 = pd.DataFrame.from_dict(s['data'][i][0][types])
            data7['vesselname'] = data7['vesselname'].fillna(data7['vesselname'].mode()[0])
            try:
                data7 = data7[['range','value','vesselname']]
            except:
                pass
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
        pivoted_parameter = pivoted_parameter.astype('str')
        
        html_table = "<table border='1'>\n"
            # Create table header
        html_table += "<tr>"
        for col in pivoted_parameter.columns:
            html_table += f"<th>{col}</th>"
        html_table += "</tr>\n"
        # Iterate over rows
        for index, row in pivoted_parameter.iterrows():
            html_table += "<tr>"
            for value in row:
                html_table += f"<td>{value}</td>"
            html_table += "</tr>\n"
        html_table += "</table>"


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
            try:
                data1 = data1[['range','value','vesselname']]
            except:
                pass
            data1 = data1.dropna()
            if count != 0:
                df_sog = pd.concat([df_sog,data1],axis=0)
            else:
                df_sog = data1
            count = count+1

    #     pivoted_sog = df_sog.pivot(index='range',columns='vesselname',values='value').reset_index()   
        df_sog = df_sog.fillna(0)
        list_vsl_sog = df_sog['vesselname'].unique().tolist()



    #     melted_sog = pd.melt(pivoted_sog, id_vars=['range'], value_vars=list_vsl_sog, var_name='vesselname', value_name='value')
        fig = px.bar(df_sog, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Speed (kn)', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div1 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        a = ''
        for i in list_vsl_sog:
            a = a+i+","+" "

        b = a.rstrip(" ")
        vessels = b.rstrip(",")    

        count = 0
        for i in s['data']:
            data2 = pd.DataFrame.from_dict(s['data'][i][0]['draft'])
            data2['vesselname'] = data2['vesselname'].fillna(data2['vesselname'].mode()[0])
            try:
                data2 = data2[['range','value','vesselname']]
            except:
                pass
            data2 = data2.dropna()
            if count != 0:
                df_draft = pd.concat([df_draft,data2],axis=0)
            else:
                df_draft = data2
            count = count+1

    #     pivoted_draft = df_draft.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_draft = df_draft.fillna(0)   
        list_vsl_draft = df_draft['vesselname'].unique().tolist()



    #     melted_draft = pd.melt(pivoted_draft, id_vars=['range'], value_vars=list_vsl_draft, var_name='vesselname', value_name='value')
        fig = px.bar(df_draft, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Draft (m)', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data3 = pd.DataFrame.from_dict(s['data'][i][0]['power'])
            data3['vesselname'] = data3['vesselname'].fillna(data3['vesselname'].mode()[0])
            try:
                data3 = data3[['range','value','vesselname']]
            except:
                pass
            data3 = data3.dropna()
            if count != 0:
                df_power = pd.concat([df_power,data3],axis=0)
            else:
                df_power = data3
            count = count+1

    #     pivoted_power = df_power.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_power = df_power.fillna(0)   
        list_vsl_power = df_power['vesselname'].unique().tolist()



    #     melted_power = pd.melt(pivoted_power, id_vars=['range'], value_vars=list_vsl_power, var_name='vesselname', value_name='value')
        fig = px.bar(df_power, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Power (kW)', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data4 = pd.DataFrame.from_dict(s['data'][i][0]['seastate'])
            data4['vesselname'] = data4['vesselname'].fillna(data4['vesselname'].mode()[0])
            try:
                data4 = data4[['range','value','vesselname']]
            except:
                pass
            data4 = data4.dropna()
            if count != 0:
                df_seastate = pd.concat([df_seastate,data4],axis=0)
            else:
                df_seastate = data4
            count = count+1

    #     pivoted_seastate = df_seastate.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_seastate = df_seastate.fillna(0)  
        list_vsl_seastate = df_seastate['vesselname'].unique().tolist()



    #     melted_seastate = pd.melt(pivoted_seastate, id_vars=['range'], value_vars=list_vsl_seastate, var_name='vesselname', value_name='value')
        fig = px.bar(df_seastate, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'SeaState', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div4 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data5 = pd.DataFrame.from_dict(s['data'][i][0]['load'])
            data5['vesselname'] = data5['vesselname'].fillna(data5['vesselname'].mode()[0])
            try:
                data5 = data5[['range','value','vesselname']]
            except:
                pass
            data5 = data5.dropna()
            if count != 0:
                df_load = pd.concat([df_load,data5],axis=0)
            else:
                df_load = data5
            count = count+1

    #     pivoted_load = df_load.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_load = df_load.fillna(0)
        list_vsl_load = df_load['vesselname'].unique().tolist()
        

    #     melted_load = pd.melt(pivoted_load, id_vars=['range'], value_vars=list_vsl_load, var_name='vesselname', value_name='value')
        fig = px.bar(df_load, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Slip', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div5 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})




        count = 0
        for i in s['data']:
            data6 = pd.DataFrame.from_dict(s['data'][i][0]['rpm'])
            data6['vesselname'] = data6['vesselname'].fillna(data6['vesselname'].mode()[0])
            try:
                data6 = data6[['range','value','vesselname']]
            except:
                pass
            data6 = data6.dropna()
            if count != 0:
                df_rpm = pd.concat([df_rpm,data6],axis=0)
            else:
                df_rpm = data6
            count = count+1

    #     pivoted_rpm = df_rpm.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_rpm = df_rpm.fillna(0)    
        list_vsl_rpm = df_rpm['vesselname'].unique().tolist()


        
    #     melted_rpm = pd.melt(pivoted_rpm, id_vars=['range'], value_vars=list_vsl_rpm, var_name='vesselname', value_name='value')
        fig = px.bar(df_rpm, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'RPM', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div6 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    

        count = 0
        for i in s['data']:
            data7 = pd.DataFrame.from_dict(s['data'][i][0][types])
            data7['vesselname'] = data7['vesselname'].fillna(data7['vesselname'].mode()[0])
            try:
                data7 = data7[['range','value','vesselname']]
            except:
                pass
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
        pivoted_parameter = pivoted_parameter.astype('str')
        
        html_table = "<table border='1'>\n"
            # Create table header
        html_table += "<tr>"
        for col in pivoted_parameter.columns:
            html_table += f"<th>{col}</th>"
        html_table += "</tr>\n"
        # Iterate over rows
        for index, row in pivoted_parameter.iterrows():
            html_table += "<tr>"
            for value in row:
                html_table += f"<td>{value}</td>"
            html_table += "</tr>\n"
        html_table += "</table>"


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
            try:
                data1 = data1[['range','value','vesselname']]
            except:
                pass
            data1 = data1.dropna()
            if count != 0:
                df_sog = pd.concat([df_sog,data1],axis=0)
            else:
                df_sog = data1
            count = count+1

    #     pivoted_sog = df_sog.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_sog = df_sog.fillna(0)
        list_vsl_sog = df_sog['vesselname'].unique().tolist()


    #     melted_sog = pd.melt(pivoted_sog, id_vars=['range'], value_vars=list_vsl_sog, var_name='vesselname', value_name='value')
        fig = px.bar(df_sog, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Speed (kn)', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div1 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data2 = pd.DataFrame.from_dict(s['data'][i][0]['draft'])
            data2['vesselname'] = data2['vesselname'].fillna(data2['vesselname'].mode()[0])
            try:
                data2 = data2[['range','value','vesselname']]
            except:
                pass
            data2 = data2.dropna()
            if count != 0:
                df_draft = pd.concat([df_draft,data2],axis=0)
            else:
                df_draft = data2
            count = count+1

    #     pivoted_draft = df_draft.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_draft = df_draft.fillna(0)    
        list_vsl_draft = df_draft['vesselname'].unique().tolist()


    #     melted_draft = pd.melt(pivoted_draft, id_vars=['range'], value_vars=list_vsl_draft, var_name='vesselname', value_name='value')
        fig = px.bar(df_draft, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Draft (m)', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data3 = pd.DataFrame.from_dict(s['data'][i][0]['power'])
            data3['vesselname'] = data3['vesselname'].fillna(data3['vesselname'].mode()[0])
            try:
                data3 = data3[['range','value','vesselname']]
            except:
                pass
            data3 = data3.dropna()
            if count != 0:
                df_power = pd.concat([df_power,data3],axis=0)
            else:
                df_power = data3
            count = count+1

    #     pivoted_power = df_power.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_power = df_power.fillna(0)   
        list_vsl_power = df_power['vesselname'].unique().tolist()

    #     melted_power = pd.melt(pivoted_power, id_vars=['range'], value_vars=list_vsl_power, var_name='vesselname', value_name='value')
        fig = px.bar(df_power, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Power (kW)', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data4 = pd.DataFrame.from_dict(s['data'][i][0]['seastate'])
            data4['vesselname'] = data4['vesselname'].fillna(data4['vesselname'].mode()[0])
            try:
                data4 = data4[['range','value','vesselname']]
            except:
                pass
            data4 = data4.dropna()
            if count != 0:
                df_seastate = pd.concat([df_seastate,data4],axis=0)
            else:
                df_seastate = data4
            count = count+1

    #     pivoted_seastate = df_seastate.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_seastate = df_seastate.fillna(0)    
        list_vsl_seastate = df_seastate['vesselname'].unique().tolist()
    #     melted_seastate = pd.melt(pivoted_seastate, id_vars=['range'], value_vars=list_vsl_seastate, var_name='vesselname', value_name='value')
        fig = px.bar(df_seastate, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'SeaState', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div4 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data5 = pd.DataFrame.from_dict(s['data'][i][0]['load'])
            data5['vesselname'] = data5['vesselname'].fillna(data5['vesselname'].mode()[0])
            try:
                data5 = data5[['range','value','vesselname']]
            except:
                pass
            data5 = data5.dropna()
            if count != 0:
                df_load = pd.concat([df_load,data5],axis=0)
            else:
                df_load = data5
            count = count+1

    #     pivoted_load = df_load.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_load = df_load.fillna(0)   
        list_vsl_load = df_load['vesselname'].unique().tolist()


    #     melted_load = pd.melt(pivoted_load, id_vars=['range'], value_vars=list_vsl_load, var_name='vesselname', value_name='value')
        fig = px.bar(df_load, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'Slip', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div5 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        count = 0
        for i in s['data']:
            data6 = pd.DataFrame.from_dict(s['data'][i][0]['rpm'])
            data6['vesselname'] = data6['vesselname'].fillna(data6['vesselname'].mode()[0])
            try:
                data6 = data6[['range','value','vesselname']]
            except:
                pass
            data6 = data6.dropna()
            if count != 0:
                df_rpm = pd.concat([df_rpm,data6],axis=0)
            else:
                df_rpm = data6
            count = count+1

    #     pivoted_rpm = df_rpm.pivot(index='range',columns='vesselname',values='value').reset_index()
        df_rpm = df_rpm.fillna(0)   
        list_vsl_rpm = df_rpm['vesselname'].unique().tolist()


    #     melted_rpm = pd.melt(pivoted_rpm, id_vars=['range'], value_vars=list_vsl_rpm, var_name='vesselname', value_name='value')
        fig = px.bar(df_rpm, x='range', y='value', color='vesselname', barmode='group', 
                    labels={'range': 'RPM', 'value': 'Percentage (%)'}, 
                    text='value', hover_name='vesselname')
        fig.update_xaxes(type='category', tickangle=-45)
        fig.update_layout(width=1000, height=700)
        
        plot_div6 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        # types = 'draft' #input parameter

        count = 0
        for i in s['data']:
            data7 = pd.DataFrame.from_dict(s['data'][i][0][types])
            data7['vesselname'] = data7['vesselname'].fillna(data7['vesselname'].mode()[0])
            try:
                data7 = data7[['range','value','vesselname']]
            except:
                pass
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
        pivoted_parameter = pivoted_parameter.astype('str')
        
        html_table = "<table border='1'>\n"
            # Create table header
        html_table += "<tr>"
        for col in pivoted_parameter.columns:
            html_table += f"<th>{col}</th>"
        html_table += "</tr>\n"
        # Iterate over rows
        for index, row in pivoted_parameter.iterrows():
            html_table += "<tr>"
            for value in row:
                html_table += f"<td>{value}</td>"
            html_table += "</tr>\n"
        html_table += "</table>"
    no='No data available.'
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>operational_profile_report</title>
        <style>
            body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            h1 {{
                color: #193185;
                font-size:36px;
                margin-bottom: 20px;
            }}
            h2{{
                color: #193185;
                font-siz: 30px;
            }}
            
            
            
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 16px;/* Increase font size for the information */
            }}
            .second-info{{ margin-left: 100px;}}
            table {{
                margin: 20px auto;
                    width: 90%;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            .graph{{margin-center}}
            
                table, tr, td {{height: 34px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%; /*increase width of plot_div */
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin: auto; /* center the plot_div
            }}
                .rectangles-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;  /* Optional margin between rectangles and table */
            }}
            hr {{border-width: 3px;}}
            .rectangle {{
                min-width: 200px;
                #height: 100px;
                padding: 12px;
                border: 2px solid;
                margin-right: 20px;  /* Optional margin between rectangles */
                color: white;
                #display: flex;
                #flex-direction: row;
                #align-items: 'center';
                #justify-content: 'center'
                text-align: 'center';
            }}
            /* Apply additional styles based on conditions */
            .gain-positive {{
                background-color: #17d41a;
                border-color: #008000;
            }}
            .gain-negative {{
                background-color: #ff0000;
                border-color: #800000;
            }}
            th {{
        background: blue;
        color: white;
        height: 41px;
    }}
    </style>
    </head>

    <body>
        {image_tag}
        <h1>
            Operational Profile Report
        </h1>
        <br>
        <br>
        <hr>
        <!--add information in html format -->
    <div class="info">
            <div class='first-info'>
    <p style="font-size:18px">
        {f'Class: {class_name}' if report_type == 'class' else
        f'Vessel Name: {vessel_name}' if report_type == 'vessel' else
        f'Teu Group: {class_name}' if report_type == 'teu' else
        f'Multi vessel'}
    </p>
    <p style="font-size:18px">Monitoring Period: {date}</p>


                
        </div>
        </div>
        <hr>
        <br>
        <h2>Speed</h2>
        <div class='plot_div'>
    
        {f'{plot_div1}' if plot_div1 else f' {no}'}
    
        </div>
        
        <br>
        <br>
        
        <h2>Draft</h2>
        <div class='plot_div'>
    
        {f'{plot_div2}' if plot_div2  else  f'{no}'}
        
        </div>
        
        <br>
        <br>

        
        <h2>Power</h2>
        <div class='plot_div'>
    
        {f'{plot_div3}' if plot_div3  else f'{no}'}
    
        </div>
        
        <br>
        <br>
        
        <h2>Sea State</h2>
        <div class='plot_div'>
    
        {f'{plot_div4}' if plot_div4  else  f'{no}'}
        
        </div>
        
        <br>
        <br>
        
        <h2>Slip</h2>
        <div class='plot_div'>
    
        {f'{plot_div5}' if plot_div5  else f'{no}'}
        
        </div>
        
        <br>
        <br>
        <h2>RPM</h2>
        <div class='plot_div'>
    
        {f'{plot_div6}' if plot_div6 else f'{no}'}
    
        </div>
        
        <br>
        <br>
        
        <h2>{types.upper()}</h2>
        
        
        {html_table}
        
        <br>
        <br>
        
        <br>
        <br>
        <br>
        

        
        
        
        
    
        
            
        <!-- ... (rest of the body content) ... -->




    </body>
    </html>
    """
    file_name = 'operational_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)


@router.post('/api/v1/html/performanceresult/curve/{imo}')
async def index(info:Request, imo:str =None,sea_state:str = None ,vessel_name:str = None, date:str = None):
    
    s = await info.json()
    
    fo_table = pd.DataFrame.from_dict(s['performance_result']["tab1"]["table1"])
    po_table = pd.DataFrame.from_dict(s['performance_result']["tab1"]["table2"])
    fo_Chart = pd.DataFrame.from_dict(s['performance_result']["tab1"]["chart1"])
    po_Chart = pd.DataFrame.from_dict(s['performance_result']["tab1"]["chart2"])

    import plotly.offline as pyo
    import plotly.graph_objects as go

    html_table = "<table border='1'>\n"
    # Create table header
    html_table += "<tr>"
    for col in fo_table.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr>\n"
    # Iterate over rows
    for index, row in fo_table.iterrows():
        html_table += "<tr>"
        for value in row:
            html_table += f"<td>{value}</td>"
        html_table += "</tr>\n"

    html_table += "</table>"

    html_table2 = "<table border='1'>\n"
    # Create table header
    html_table2 += "<tr>"
    for col in po_table.columns:
        html_table2 += f"<th>{col}</th>"
    html_table2 += "</tr>\n"

    # Iterate over rows
    for index, row in po_table.iterrows():
        html_table2 += "<tr>"
        for value in row:
            html_table2 += f"<td>{value}</td>"
        html_table2 += "</tr>\n"

    html_table2 += "</table>"


    fig = go.Figure()
    fig = px.line(fo_Chart, x='speed', y='fo_consumption', color='category',
                markers=True, line_shape='linear', 
                labels={'speed': 'Speed (knots)', 'fo_consumption': 'FO/24 Hrs (tonne)','category':'Draft'},
                title='FO Calculator Chart')
    fig.update_layout(
        width=1000,
        height=700)


    # Show the plot
    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    fig = px.line(po_Chart, x='speed', y='fo_consumption', color='category',
                markers=True, line_shape='linear', 
                labels={'speed': 'Speed (knots)', 'fo_consumption': 'Power (KW)','category':'Draft'},
                title='Power Calculator Chart')
    fig.update_layout(
        width=1000,
        height=700)


    # Show the plot
    plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>performance_result</title>
        <style>
            body {{
                text-align: center;
            }}
            h1 {{
                color: #193185;
                font-size:36px;
                margin-bottom:20px;
            }}
            h2{{
                color: #193185;
                font-size:30px;
            }}
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size:16px;/*increase font size for the information*/
            }}
            .second-info{{ margin-left: 100px;}}
            table {{
                margin: 20px auto;
                    width: 511px;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            .graph{{margin-center}}
            
                table, tr, td {{height: 34px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%;/*increase width of the plot_div*/
                        display: flex;
                        justify-content: center;
                        align-items:center;
                        margin:auto;*/center the plot_div*/
            }}
                .rectangles-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;  /* Optional margin between rectangles and table */
            }}
            hr {{border-width: 3px;}}
            .rectangle {{
                min-width: 200px;
                #height: 100px;
                padding: 12px;
                border: 2px solid;
                margin-right: 20px;  /* Optional margin between rectangles */
                color: white;
                #display: flex;
                #flex-direction: row;
                #align-items: 'center';
                #justify-content: 'center'
                text-align: 'center';
            }}
            /* Apply additional styles based on conditions */
            .gain-positive {{
                background-color: #17d41a;
                border-color: #008000;
            }}
            .gain-negative {{
                background-color: #ff0000;
                border-color: #800000;
            }}
            th {{
        background: blue;
        color: white;
        height: 41px;
    }}
        </style>
    </head>
    <body>
        {image_tag}
        <h1>
            {'PERFORMANACE RESULTS'}
        </h1>
        <br>
        <br>
        <hr>
        <!--add information in html format -->
    <div class="info">
            <div class='first-info'>
                <pstyle = "font-size:18px">Vessel Name:{vessel_name} </p>
                <pstyle="font-size:18px">Date: {date}</p>
                </div>
                </div>
                <hr>
        
        <br>
        <h2>FO Calculator Table</h2>
        
        <h3>Sea State : {sea_state}</h3>
        <!-- Add the centered and bigger table -->
        
        {html_table}
        </div>
        <br>
        <br>
        <br>
        <div class="plot_div">
        {plot_div}
        </div>
        
        <br>
        <br>
        <h2>Power Calculator Table</h2>
        
        <!-- Add the centered and bigger table -->
        {html_table2}
        <br>
        <br>
        <br>
        <div class="plot_div">
        {plot_div2}
        </div>
        
        
        
        
    
        
            
        <!-- ... (rest of the body content) ... -->




    </body>
    </html>
    """

    
    
    file_name = 'performance_curve_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)


@router.post('/api/v1/html/electricalreport/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None ,types:str = None, period:str = None, engine:str = None, classes:str = None, fleet:str = None):

    s = await info.json()
    if types == 'vessel':
        
            
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

        fig = px.bar(data2_ae_engine_data, x="date", y="value",color="New_column",
                    labels={'value': '%LOAD', 'date': 'Date','New_column': 'Noon Report Date'},
                    title='Auxiliary Electrical Load')

        if 'Test Load' in data2_ae_engine_data.columns:
            fig.add_trace(go.Scatter(x=data2_ae_engine_data['date'],
                                    y=data2_ae_engine_data['Test Load'],
                                    mode='lines',
                                    line=dict(color='yellow'),
                                    name='Tested Load'))
            fig.add_trace(go.Scatter(x=data2_ae_engine_data['date'],
                                    y=data2_ae_engine_data['line1'],
                                    mode='lines',
                                    line=dict(color='red'),
                                    name='Max Load'))

        fig.update_layout(
            xaxis=dict(tickangle=45),
            yaxis=dict(),
            xaxis_title='Date',
            yaxis_title='%LOAD',

        )
        plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        html_table ="<table border='1'>\n"
        # Create table header
        html_table += "<tr>"
        for col in data12.columns:
            html_table += f"<th>{col}</th>"
        html_table += "</tr>\n"

        # Iterate over rows
        for index, row in data12.iterrows():
            html_table += "<tr>"
            for value in row:
                html_table += f"<td>{value}</td>"
            html_table += "</tr>\n"

        html_table += "</table>"



        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title></title>
            <style>
                body {{
                    text-align: center;
                }}
                h1 {{
                    color: #193185;
                    text-align: center
                }}
                h2{{
                    color: #193185;
                }}
                img {{
                    width: 80px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;
                    display: flex;
                }}

                .second-info{{ margin-left: 100px;}}
                table {{
                    margin: 20px auto;
                        width: 1300px;
                        border-collapse: collapse;
                        border: solid;

                }}

                    table, tr, td {{height: 34px;
                        border: 1px solid;
                    }}
                .plot_div{{

                            display: flex;
                            justify-content: center;
                }}



                hr {{border-width: 3px;}}

                /* Apply additional styles based on conditions */

                th {{
            background: blue;
            color: white;
            height: 41px;
        }}
            </style>
        </head>
        <body>
            {image_tag}
            <h1>
                Monthly Electrical Report 
            </h1>
            <br>
            <br>
            <hr>

            <div class="info">
                <div class='first-info'>
                    <p>Vessel: {vessel_name} </p>
                    <p>Monitoring period : {period}</p>

                </div>

            </div>
            <hr>
            {html_table}
            <br>
            <br>
            <br>
            <br>
            <h2>Auxiliary Engine Selected : {engine}</h2>
                {plot_div}



            </body>
        </html>
        """
    
    file_name = 'electrical_report_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)



@router.post('/api/v1/html/me/sfoc/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None ,class_name:str = None, fleet:str = None, fleet_tree:str = None, report_type:str = None, month:str = None, no_of_previous_months:str = None):
    s = await info.json()

    d=pd.DataFrame.from_dict(s['data'])
    d.drop(['remarks','location'],axis=1,inplace=True)


    fig = px.scatter(d, x='tested_date', y='sfoc_gm_kwhr', title='SFOC vs Tested Date',
                    labels={'sfoc_gm_kwhr': 'SFOC (g/kW-hr)', 'tested_date': 'Date'})
    min_sfoc = 175
    fig.add_trace(go.Scatter(x=d['tested_date'], y=[min_sfoc]*len(d), mode='lines', name='Min SFOC (175)',
                            line=dict(color='red')))
    # Add a label for the minimum SFOC line
    fig.add_annotation(
        go.layout.Annotation(
            x=d['tested_date'].iloc[0],
            y=min_sfoc,
            text='175',
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40
        )
    )

    # Add a line for maximum SFOC (203)
    max_sfoc = 203
    fig.add_trace(go.Scatter(x=d['tested_date'], y=[max_sfoc]*len(d), mode='lines', name='Max SFOC (203)',
                            line=dict(color='blue')))
    fig.add_annotation(
        go.layout.Annotation(
            x=d['tested_date'].iloc[0],
            y=max_sfoc,
            text='203',
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40
        )
    )

    fig.update_layout(
        yaxis=dict(title='SFOC (g/kW-hr)', range=[0, max_sfoc + 10]),
        xaxis=dict(title='Date'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1 ),
        height=400,  
        width=600
    )

    plot_div1 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    fig = px.scatter(d, x='tested_date', y='percentage_of_mcr', title='Scatter Plot of Load vs Tested Date',
                    labels={'percentage_of_mcr': 'Load', 'tested_date': 'Date'})

    # Add a line for minimum Load (85)
    min_load = 85
    fig.add_trace(go.Scatter(x=d['tested_date'], y=[min_load]*len(d), mode='lines', name='Min Load (85)',
                            line=dict(color='red')))
    # Add a label for the minimum Load line
    fig.add_annotation(
        go.layout.Annotation(
            x=d['tested_date'].iloc[0],
            y=min_load,
            text='85',
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40
        )
    )

    # Add a line for maximum Load (100)
    max_load = 100
    fig.add_trace(go.Scatter(x=d['tested_date'], y=[max_load]*len(d), mode='lines', name='Max Load (100)',
                            line=dict(color='blue')))
    # Add a label for the maximum Load line
    fig.add_annotation(
        go.layout.Annotation(
            x=d['tested_date'].iloc[0],
            y=max_load,
            text='100',
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40
        )
    )

    fig.update_layout(
        yaxis=dict(title='Load', range=[0, 120]),
        xaxis=dict(title='Date'),legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=400,
        width=600
    )

    plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    fig = px.scatter(d, x='tested_date', y='scoc_gm_kwhr', title='SCOC vs Tested Date',
                    labels={'scoc_gm_kwhr': 'SCOC (g/kW-hr)', 'tested_date': 'Date'})
    min_scoc = 0.6
    fig.add_trace(go.Scatter(x=d['tested_date'], y=[min_scoc]*len(d), mode='lines', name='Min SCOC (0.6)',
                            line=dict(color='red')))
    fig.add_annotation(
        go.layout.Annotation(
            x=d['tested_date'].iloc[0],
            y=min_scoc,
            text='0.6',
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40
        )
    )

    max_scoc = 1.2
    fig.add_trace(go.Scatter(x=d['tested_date'], y=[max_scoc]*len(d), mode='lines', name='Max SCOC (1.2)',
                            line=dict(color='blue')))
    fig.add_annotation(
        go.layout.Annotation(
            x=d['tested_date'].iloc[0],
            y=max_scoc,
            text='1.2',
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40
        )
    )

    fig.update_layout(
        yaxis=dict(title='SCOC (g/kW-hr)', range=[0, 3]),
        xaxis=dict(title='Date'),legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=400, 
        width=600
    )


    plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    d = d.rename(columns={
        'imo': 'IMO',
        'name': 'Name',
        'sister_group': 'Sister Group',
        'fleet': 'Fleet',
        'teu': 'TEU',
        'built_year': 'Built Year',
        'me_maker': 'ME Maker',
        'me_model': 'ME Model',
        'mcr_kw': 'MCR(KW)',
        'new_mcr_kw': 'New MCR(after retrofit)',
        'new_rpm': 'New RPM(after retrofit)',
        'tested_date': 'Tested Date',
        'lub_type': 'Type of Lubicant',
        'sulphur': 'S%',
        'tested_kw_mid_month': 'TESTED KW',
        'mcr_rpm': 'MCR RPM',
        'test_rpm': 'TESTED RPM',
        'percentage_of_mcr': '% of MCR',
        'percentage_of_rpm': '% of RPM',
        'average_draft': 'Average Draft',
        'vessel_speed': 'Vessel Speed',
        'pmax': 'Avg P Max',
        'pcom': 'Avg P Comp',
        'fule_consumtion_ton_24hr': 'Fuel Consumption (ton /24 hr)',
        'cyl_oil_cons_ltr_24hr': 'CYL Oil (gm/Kwhr)',
        'sfoc_gm_kwhr': 'SFOC (gm/kwhr)',
        'scoc_gm_kwhr': 'SCOC (gm/kwhr)'
    })

    html_table1 = "<table border='1'>\n"
    # Create table header
    html_table1 += "<tr>"
    for col in d.columns:
        html_table1 += f"<th>{col}</th>"
    html_table1 += "</tr>\n"

    # Iterate over rows
    for index, row in d.iterrows():
        html_table1 += "<tr>"
        for value in row:
            html_table1 += f"<td>{value}</td>"
        html_table1 += "</tr>\n"

    html_table1 += "</table>"




    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ME_Sfoc-Scoc_report</title>
        <style>
            body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            h1 {{
                color: #193185;
                font-size:36px;
                margin-bottom: 20px;
            }}
            h2{{
                color: #193185;
                font-siz: 30px;
            }}
            
            
            
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 18px;/* Increase font size for the information */
            }}
            .second-info{{ margin-left: 100px;}}
            table {{
                margin: 20px auto;
                    width: 511px;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            .graph{{margin-center}}
            
                table, tr, td {{height: 34px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%; /*increase width of plot_div */
                        justify-content: center;
                        align-items: center;
                        margin: auto; /* center the plot_div
                        flex-direction: column;
                        
            }}
                .rectangles-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;  /* Optional margin between rectangles and table */
            }}
            hr {{border-width: 3px;}}
            .rectangle {{
                min-width: 200px;
                #height: 100px;
                padding: 12px;
                border: 2px solid;
                margin-right: 20px;  /* Optional margin between rectangles */
                color: white;
                #display: flex;
                #flex-direction: row;
                #align-items: 'center';
                #justify-content: 'center'
                text-align: 'center';
            }}
            /* Apply additional styles based on conditions */
            .gain-positive {{
                background-color: #17d41a;
                border-color: #008000;
            }}
            .gain-negative {{
                background-color: #ff0000;
                border-color: #800000;
            }}
            th {{
        background: blue;
        color: white;
        height: 41px;
    }}
        .parent_plot_div{{
            display: flex;
            
        }}
        
    </style>
    </head>

    <body>
        {image_tag}
        <br>
        <h1>
            {'ME SFOC & SCOC REPORT'}
        </h1>
        <hr>
        <!--add information in html format -->
    <div class="info">
            
    <pstyle ="font-size:18px">
    {f'Class: {class_name}' if report_type == 'class' else
        f'Vessel Name: {vessel_name}' if report_type == 'vessel' else
        f'Fleet: {fleet}' if report_type == 'fleet' else
        f'Fleet Tree: {fleet_tree}'}
    </p>
    <p style="font-size:18px">Month: {month}</p>
    </p>
    <p style="font-size:18px">Number of Previous Months: {no_of_previous_months}</p>
    </p>

        </div>
        <hr>
        <br>
        
    
        
        <div class='parent_plot_div'>
            <div class='plot_div'>
            <h2>SFOC </h2>
            {plot_div1}
        </div>
        
        <div class='plot_div'>
            <h2>Load (%-MCR)</h2>
            {plot_div2}
        </div>
    
        <div class='plot_div'>
            <h2>SCOC</h2>
            {plot_div3}
        </div>
        
        
        </div>
        
        <br>
        <br>

        
        
        
        <br>
        <br>
        
        
        <!-- Add the centered and bigger table -->
        {html_table1}
        
        
        

        
        <br>
        <br>
        <br>
        

        
        
        
        
    
        
            
        <!-- ... (rest of the body content) ... -->




    </body>
    </html>
    """

    
    
    file_name = 'me_sfoc_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)



@router.post('/api/v1/html/datamonitoring/sfoc/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None ,period_start:str = None, period_end:str = None,period_comparison:bool = True ,period_comp_start:str = None, period_comp_end:str = None,method:str =None):
    s = await info.json()
    
    date= period_start + ' TO ' + period_end
    print(method)
    print(period_comparison)
    if method == 'vrs' or method == 'egoship':

        print(period_comparison)
        if period_comparison == True:

        
            if method == 'vrs':
                method = 'VRS Data'
            else:
                method = 'ADA Data'
    
            for i in s['data']['data']:
                a=i

            data1 = pd.DataFrame.from_dict(s['data']['data'][a])

            data2 = pd.DataFrame.from_dict(s['data']['shoptrialData'])
            data2['load'] = data2['load'].astype('float64')
            data2['sfoc'] = data2['sfoc'].astype('float64')
            data2['sfoc_corrected'] = data2['sfoc_corrected'].astype('float64')

        
            print(s)

            data3 = pd.DataFrame.from_dict(s['data']['periodComparisonData'][a])
            

            fig = px.scatter(data1, x="me_load", y="sfoc", color_discrete_sequence=['orange'], labels={'sfoc': 'SFOC (g/kWhr)', 'me_load': '% LOAD'})
            fig.add_trace(px.scatter(data3, x="me_load", y="sfoc", color_discrete_sequence=['blue']).data[0])

            # Line plots for data2 and data2_corrected
            fig.add_trace(go.Scatter(x=data2['load'], y=data2['sfoc'], mode='lines+markers', line=dict(color='green'), name='SFOC', marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=data2['load'], y=data2['sfoc_corrected'], mode='lines+markers', line=dict(color='red'), name='Corrected SFOC', marker=dict(size=8)))

            # Layout adjustments
            fig.update_layout(
                xaxis_title='% LOAD',
                yaxis_title='SFOC (g/kWhr)',
              
                font=dict(size=20),
                legend=dict(title=None),
                showlegend=True,
                autosize=False,
                width=1000,  
                height=700   
            )
            
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


            

        elif period_comparison == False:
            #input parameters

            if method == 'vrs':
                method_color = 'green'
                method = 'VRS Data'
            else:
                method_color = 'red'
                method = 'ADA Data'
    
            for i in s['data']['data']:
                a=i

            data1 = pd.DataFrame.from_dict(s['data']['data'][a])


            data2 = pd.DataFrame.from_dict(s['data']['shoptrialData'])
            data2['load'] = data2['load'].astype('float64')
            data2['sfoc'] = data2['sfoc'].astype('float64')
            data2['sfoc_corrected'] = data2['sfoc_corrected'].astype('float64')
            print(method)
    
            scatter = go.Scatter(
                x=data1["me_load"],
                y=data1["sfoc"],
                mode='markers',
                marker=dict(color=method_color),  # Set color based on method
                name=method
            )
            fig = go.Figure(scatter)

            fig.add_trace(go.Scatter(x=data2['load'], y=data2['sfoc'], mode='lines+markers', line=dict(color='green'), name='SFOC', marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=data2['load'], y=data2['sfoc_corrected'], mode='lines+markers', line=dict(color='red'), name='Corrected SFOC', marker=dict(size=8)))


            fig.update_layout(
                xaxis_title='% LOAD',
                yaxis_title='SFOC (g/kWhr)',
               
                font=dict(size=20),
                legend=dict(title=None),
                showlegend=True,
                autosize=False,
                width=1000,  
                height=700   
            )
            fig.update_yaxes(range=[150, 300])
    
            # Show the plot
            plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})




    else:
    
        #input parameters

        # period_start = '2018-01-02'

        # period_end = '2018-02-01'
    
    
        for i in s['data']['data']:

            a=i
    
        data1 = pd.DataFrame.from_dict(s['data']['data'][a])
    
        data2 = pd.DataFrame.from_dict(s['data']['shoptrialData'])

        data2['load'] = data2['load'].astype('float64')

        data2['sfoc'] = data2['sfoc'].astype('float64')

        data2['sfoc_corrected'] = data2['sfoc_corrected'].astype('float64')
    
        vrs_data = data1[data1['type']=='VRS Data']

        ada_data = data1[data1['type']=='ADA Data']
    
        vrs_scatter = go.Scatter(x=vrs_data["me_load"], y=vrs_data["sfoc"], mode='markers', marker=dict(color='green'), name='VRS Data')
    
        ada_scatter = go.Scatter(x=ada_data["me_load"], y=ada_data["sfoc"], mode='markers', marker=dict(color='red'), name='ADA Data')
    
        fig = go.Figure()

        fig.add_trace(vrs_scatter)

        fig.add_trace(ada_scatter)

        fig.add_trace(go.Scatter(x=data2['load'], y=data2['sfoc'], mode='lines+markers', line=dict(color='green'), name='SFOC', marker=dict(size=8)))

        fig.add_trace(go.Scatter(x=data2['load'], y=data2['sfoc_corrected'], mode='lines+markers', line=dict(color='red'), name='Corrected SFOC', marker=dict(size=8)))
    
    
        fig.update_layout(

            xaxis_title='% LOAD',

            yaxis_title='SFOC (g/kWhr)',

            font=dict(size=20),

            legend=dict(title=None),

            showlegend=True,

            autosize=False,

            width=1000,  

            height=700   

        )

        plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        
        
        
        
        
        
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>sfoc_devaition</title>
        <style>
            body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            h1 {{
                color: #193185;
                font-size:36px;
                margin-bottom: 20px;
            }}
            h2{{
                color: #193185;
                font-siz: 30px;
            }}
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 16px;/* Increase font size for the information */
            }}
            .second-info{{ margin-left: 100px;}}
            table {{
                margin: 20px auto;
                    width: 511px;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            .graph{{margin-center}}
            
                table, tr, td {{height: 34px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%; /*increase width of plot_div */
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin: auto; /* center the plot_div
            }}
                .rectangles-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;  /* Optional margin between rectangles and table */
            }}
            hr {{border-width: 3px;}}
            .rectangle {{
                min-width: 200px;
                #height: 100px;
                padding: 12px;
                border: 2px solid;
                margin-right: 20px;  /* Optional margin between rectangles */
                color: white;
                #display: flex;
                #flex-direction: row;
                #align-items: 'center';
                #justify-content: 'center'
                text-align: 'center';
            }}
            /* Apply additional styles based on conditions */
            .gain-positive {{
                background-color: #17d41a;
                border-color: #008000;
            }}
            .gain-negative {{
                background-color: #ff0000;
                border-color: #800000;
            }}
            th {{
        background: blue;
        color: white;
        height: 41px;
    }}
    </style>
    </head>

    <body>
                {image_tag}

        <h1>
            {'SFOC Deviation Report'}
        </h1>
        <br>
        <br>
        <hr>
        <!--add information in html format -->
    <div class="info">
            <div class='first-info'>
                <p style = "font-size:18px">Vessel Name:{vessel_name} </p>
                <p style="font-size:18px">Monitoring Period: {date}</p>
        </div>
        </div>
        <hr>
        <br>
        <h2>SFOC Deviation</h2>
        <div class='plot_div'>
    
        
        {plot_div}
        </div>
        
        <br>
        <br>
        
        <br>
        <br>
        <br>
        

        
        
        
        
    
        
            
        <!-- ... (rest of the body content) ... -->




    </body>
    </html>
    """
    
    file_name = 'datamonitoring_sfoc_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)
    
    
@router.post('/api/v1/html/period_comparison/{imo}')
async def index(info:Request,first_period_min:str = None, second_period_min : str =None, first_Period_max:str = None ,imo:str =None,vessel_name:str = None ,report_type:str = None, first_Period:str = None,second_Period:str = None , first_period_max:str = None,second_period_max:str = None , fleet:str = None ,  moving_average:str = None , class_name:str=None):
    print(info)
    s = await info.json()
    
    # vsl_name=pd.DataFrame.from_dict(s['vessel_data'])
    # vsl_name.head()
    # col_vsl= dict(zip(vsl_name['imo'], vsl_name['name']))
    # s=s['data']
    if first_Period !='null'and  second_Period !='null':
        Heading="YEAR"+"  "+first_Period+" - "+second_Period+"  "+"EEOI ANALYSIS"
        first_Period_year, second_Period_year = first_Period, second_Period
        
    else:
        
        date_object_first_Period = datetime.strptime(first_period_max, '%Y-%m-%d')
        first_Period_year = date_object_first_Period.year
        date_object_second_Period = datetime.strptime(second_period_max, '%Y-%m-%d')
        second_Period_year = date_object_second_Period.year
        Heading="YEAR"+"  "+str(first_Period_year)+" - "+str(second_Period_year)+"  "+"EEOI ANALYSIS"
        
    print("fleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeet",report_type)    

    if report_type == 'vessel':
        vsl_name = pd.DataFrame.from_dict(s['vessel_data'])
        col_vsl = dict(zip(vsl_name['imo'], vsl_name['name']))
        #s = s['data']

        Table1 = pd.DataFrame.from_dict(s['data']['table1']['table1']).fillna(0)
        Table1['improvement'] = Table1['improvement'].astype(float).astype(int)
        Table1_str = Table1[['index', 'year1', 'year2', 'improvement']].astype(str)
        Table1_str['improvement'] = Table1_str['improvement'] + ' %'

        Table_1_head_Year = [['Year', first_Period, second_Period, '% Improvement']] if all((first_Period, second_Period)) else [['Year', str(first_Period_year), str(second_Period_year), '% Improvement']]
        Table_1_Year = Table_1_head_Year + Table1_str.values.tolist()

        # 2nd Table
        Table_2 = Table1.set_index(['index'])
        Table_2 = Table_2.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]].reset_index()

        Table_2 = Table_2.rename({'improvement': 'Improvement (%)', 'year1': first_Period, 'year2': second_Period, 'index': 'Year'}, axis=1) if all((first_Period, second_Period)) else Table_2.rename({'improvement': 'Improvement (%)', 'year1': str(first_Period_year), 'year2': str(second_Period_year), 'index': 'Year'}, axis=1)

        Table_2_new = Table_2.T.reset_index().T.set_index(0).T
        Table_2_str = Table_2_new.astype(str)


        MVG_Total_sum = 0
        MVG_Total_TEU_sum = 0

        mvg_year1 = pd.DataFrame.from_dict(s['data']['year1']['moving data average'])
        mvg_year2 = pd.DataFrame.from_dict(s['data']['year2']['moving data average'])

        if not mvg_year1.empty and not mvg_year2.empty:
            MVG_Total_sum = mvg_year1["EEOI For Cargo [MT]"].sum() + mvg_year2["EEOI For Cargo [MT]"].sum()
            Mvg_Legend_Year1 = f"{moving_average} Moving Avg {first_Period}" if all((first_Period, second_Period)) else f"{moving_average} Moving Avg {first_Period_year}"
            Mvg_Legend_Year2 = f"{moving_average} Moving Avg {second_Period}" if all((first_Period, second_Period)) else f"{moving_average} Moving Avg {second_Period_year}"


            # Moving Average - Graph 3
            trace1 = go.Scatter(
                x=mvg_year1["S.No"],
                y=mvg_year1["EEOI For Cargo [MT]"],
                mode='lines+markers',
                name=Mvg_Legend_Year1,
                line=dict(color='green', width=2),
                marker=dict(size=8)
            )

            trace2 = go.Scatter(
                x=mvg_year2["S.No"],
                y=mvg_year2["EEOI For Cargo [MT]"],
                mode='lines+markers',
                name=Mvg_Legend_Year2,
                line=dict(color='orange', width=2),
                marker=dict(size=8)
            )

            trace3 = go.Scatter(
                x=mvg_year1["S.No"],
                y=mvg_year1["EEOIGOALMT"],
                mode='lines',
                name='EEOI GOAL MT',
                line=dict(color='blue', width=2, dash='dash')
            )

            # Set layout
            layout = go.Layout(
                xaxis=dict(
                    title=' ',
                    tickfont=dict(size=13),
                    showgrid=False  # Correct syntax for showgrid
                ),
                yaxis=dict(
                    title='Moving Average',
                    tickfont=dict(size=13),
                    showgrid=False  # Correct syntax for showgrid
                ),
                showlegend=True,
                legend=dict(
                    x=1,  # Adjust the x position of the legend
                    y=1,  # Adjust the y position of the legend
                    font=dict(size=10),  # Adjust the font size of the legend
                    bgcolor='rgba(0, 0, 0, 0)'  # Make the legend background transparent
                ),
                width=1000,
                height=500
            )

            # Create figure
            fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)

            #fig.show()
            plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

            MVG_Total_TEU_sum = mvg_year1["EEOI For Cargo [TEU]"].sum() + mvg_year2["EEOI For Cargo [TEU]"].sum()

            Mvg_Legend_Year1 = f"{moving_average} Moving Avg {first_Period}" if all((first_Period, second_Period)) else f"{moving_average} Moving Avg {first_Period_year}"
            Mvg_Legend_Year2 = f"{moving_average} Moving Avg {second_Period}" if all((first_Period, second_Period)) else f"{moving_average} Moving Avg {second_Period_year}"

            if mvg_year1.empty and mvg_year2.empty:
                print('No Data Available')
            else:
                pass

            # Moving average graph 4
            trace1 = go.Scatter(
                x=mvg_year1["S.No"],
                y=mvg_year1["EEOI For Cargo [TEU]"],
                mode='lines+markers',
                name=Mvg_Legend_Year1,
                line=dict(color='green', width=2),
                marker=dict(size=8)
            )

            trace2 = go.Scatter(
                x=mvg_year2["S.No"],
                y=mvg_year2["EEOI For Cargo [TEU]"],
                mode='lines+markers',
                name=Mvg_Legend_Year2,
                line=dict(color='orange', width=2),
                marker=dict(size=8)
            )

            trace3 = go.Scatter(
                x=mvg_year1["S.No"],
                y=mvg_year1["EEOIGOALTEU"],
                mode='lines',
                name='EEOI GOAL TEU',
                line=dict(color='blue', width=2, dash='dash')
            )

            # Set layout
            layout = go.Layout(
                xaxis=dict(
                    title=' ',
                    tickfont=dict(size=13),
                    showgrid=False  # Correct syntax for showgrid
                ),
                yaxis=dict(
                    title='Moving Average',
                    tickfont=dict(size=13),
                    showgrid=False  # Correct syntax for showgrid
                ),
                showlegend=True,
                legend=dict(
                    x=1,  # Adjust the x position of the legend
                    y=1,  # Adjust the y position of the legend
                    font=dict(size=12),  # Adjust the font size of the legend
                    bgcolor='rgba(0, 0, 0, 0)'  # Make the legend background transparent
                ),
                width=1000,
                height=500
            )

            fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)

            ##fig.show()
            plot_div4 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        else:
            print('No Data Available')

        Year1_Graph = pd.DataFrame.from_dict(s['data']['year1']['finaldata']).round(2)
        Year2_Graph = pd.DataFrame.from_dict(s['data']['year2']['finaldata']).round(2)
        EEOI_Analysis = Table1.set_index(['index'])
        EEOI_Analysis = EEOI_Analysis.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        EEOI_Analysis = EEOI_Analysis[['year1', 'year2']]

        EEOI_Analysis_new = EEOI_Analysis.rename({"year1": first_Period, 'year2': second_Period}, axis=1) if all((first_Period, second_Period)) else EEOI_Analysis.rename({"year1": str(first_Period_year), 'year2': str(second_Period_year)}, axis=1)

        # EEOI_Analysis_Graph = EEOI_Analysis_new.plot.bar(rot=0, color={first_Period: "#588aee", second_Period: "#61d8a8"}, width=0.8, figsize=(10, 6))

        EEOI_Analysis = Table1.set_index(['index'])
        EEOI_Analysis = EEOI_Analysis.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        EEOI_Analysis = EEOI_Analysis[['year1', 'year2']]

        EEOI_Analysis_1 = EEOI_Analysis_new.columns[0]
        EEOI_Analysis_2 = EEOI_Analysis_new.columns[1]

        # Create a bar chart for each trace with values above the bars
        trace1 = go.Bar(
            x=EEOI_Analysis.index,
            y=EEOI_Analysis['year1'],
            text=EEOI_Analysis['year1'].round(2),  # Adjust rounding as needed
            textposition='outside',  # Display text labels outside the bars
            name=EEOI_Analysis_1,
            marker=dict(color="#588aee")
        )

        trace2 = go.Bar(
            x=EEOI_Analysis.index,
            y=EEOI_Analysis['year2'],
            text=EEOI_Analysis['year2'].round(2),
            textposition='outside',
            name=EEOI_Analysis_2,  # Use the dynamically generated legend label
            marker=dict(color="#61d8a8")
        )

        layout = go.Layout(
            xaxis=dict(
                title=' ',
                tickfont=dict(size=17),
                showgrid=False  # Correct syntax for showgrid
            ),
            yaxis=dict(
                title='Value',
                tickfont=dict(size=17),
                showgrid=False  # Correct syntax for showgrid
            ),
            showlegend=True,
            legend=dict(
                x=1,  # Adjust the x position of the legend
                y=1,  # Adjust the y position of the legend
                font=dict(size=15),  # Adjust the font size of the legend
                bgcolor='rgba(0, 0, 0, 0)'  # Make the legend background transparent
            ),
            width=1050,
            height=600
        )

        fig = go.Figure(data=[trace1, trace2], layout=layout)
        #fig.show()
        plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        Improvement_Percent = Table1.set_index(['index'])
        Improvement_Percent = Improvement_Percent.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        Improvement_Percent = Improvement_Percent[['improvement']].reset_index()
        Improvement_Percent = Improvement_Percent.set_index(['index'])

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=Improvement_Percent.index,
            y=Improvement_Percent['improvement'],
            text=Improvement_Percent['improvement'].astype('str') + '%',
            textposition='outside',  # Display text outside the bar
            marker=dict(color='#808080')  
        ))

        layout = go.Layout(
            xaxis=dict(
                title='',
                tickfont=dict(size=17),
                showgrid=False  # Correct syntax for showgrid
            ),
            yaxis=dict(
                title='% Improvement',
                tickfont=dict(size=17),
                showgrid=False  # Correct syntax for showgrid
            ),
            showlegend=False,
            width=1000,
            height=600
        )
        # Format y-axis tick labels as percentages
        layout['yaxis']['tickformat'] = '.3f%'
        fig.update_layout(layout)
        #fig.show()
        plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        #Total cargo
        Total_Cargo = Year1_Graph[['imo', 'cargomt']]
        
        if second_Period:
            Total_Cargo[second_Period] = Total_Cargo['imo'].map(Year2_Graph.set_index('imo')['cargomt'])
            Total_Cargo = Total_Cargo.sort_values(by=second_Period)
        else:
            Total_Cargo[str(second_Period_year)] = Total_Cargo['imo'].map(Year2_Graph.set_index('imo')['cargomt'])
            Total_Cargo = Total_Cargo.sort_values(by=str(second_Period_year))
        Total_Cargo['Vessel Name'] = Total_Cargo['imo'].map(col_vsl)
        Total_Cargo['Vessel - IMO'] = Total_Cargo['Vessel Name']
        
        if first_Period:
            Total_Cargo = Total_Cargo.rename({'cargomt': first_Period}, axis=1)
            melted_data = pd.melt(Total_Cargo, id_vars=['Vessel - IMO'], value_vars=[first_Period, second_Period] if second_Period else [first_Period], var_name='Year', value_name='Total_Cargo')
        else:
            Total_Cargo = Total_Cargo.rename({'cargomt': str(first_Period_year)}, axis=1)
            melted_data = pd.melt(Total_Cargo, id_vars=['Vessel - IMO'], value_vars=[str(first_Period_year), str(second_Period_year)] if second_Period else [str(first_Period_year)], var_name='Year', value_name='Total_Cargo')
        # Drop rows with NaN values in 'Total_Cargo'
        melted_data.dropna(subset=['Total_Cargo'], inplace=True)
        Total_Cargo_Graph = px.bar(
            melted_data,
            x='Vessel - IMO',
            y='Total_Cargo',
            barmode='group', 
            color='Year',
            color_discrete_sequence=['#c44332', '#1a75c1'] if second_Period else ['#c44332'],
            labels={'Total_Cargo': 'Total Cargo (metric-Tonne)'},
            title='Total Cargo',
        )
        layout_total_cargo = go.Layout(
            title=dict(
                text='Total Cargo',
                font=dict(size=20, family='Roboto, sans-serif', color='black'),
                x=0.5
            ),
            xaxis=dict(
                title='Vessel Name',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False
            ),
            yaxis=dict(
                title='Total Cargo (metric-Tonne)',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False
            ),
            legend=dict(
                title='',
                font=dict(size=15),
                bgcolor='rgba(0, 0, 0, 0)'
            ),
            width=1050,
            height=650
        )
        Total_Cargo_Graph.update_layout(layout_total_cargo)
        #Total_Cargo_Graph.show()
        plot_div7 = pyo.plot(Total_Cargo_Graph, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


         
        if second_Period:
            Total_Cargo['Difference'] = Total_Cargo[second_Period] - Total_Cargo[first_Period]
        else:
            Total_Cargo['Difference'] = Total_Cargo[str(second_Period_year)] - Total_Cargo[str(first_Period_year)]
 
        Total_Cargo = Total_Cargo.sort_values(by='Difference', ascending=False)
 
 
        # Plotly bar chart for Total Cargo - Period wise difference
        Total_Cargo_diff_graph = px.bar(
            Total_Cargo,
            x='Vessel - IMO',
            y='Difference',
            barmode='group', 
            color_discrete_sequence=['#c44332'],
            labels={'Difference': 'Total Cargo Difference (metric-Tonne)'},
        )
 
        # Update the layout
        Total_Cargo_diff_graph.update_layout(
            xaxis=dict(title='Vessel Name', tickfont=dict(size=18, family='Times New Roman')),
            yaxis=dict(title='Total Cargo Difference (metric-Tonne)', tickfont=dict(size=18, family='Times New Roman')),
            showlegend=False,
            width=1000,
            height=600
        )
 
        # Show the figure
        #Total_Cargo_diff_graph.show()
        plot_div8 = pyo.plot(Total_Cargo_diff_graph, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
 
 
        # Total Distance
        Total_Distance = Year1_Graph[['imo', 'average_distance']]
 
        if second_Period:
            Total_Distance[second_Period] = Total_Distance['imo'].map(Year2_Graph.set_index('imo')['average_distance'])
            Total_Distance = Total_Distance.sort_values(by=second_Period)
        else:
            Total_Distance[str(second_Period_year)] = Total_Distance['imo'].map(Year2_Graph.set_index('imo')['average_distance'])
            Total_Distance = Total_Distance.sort_values(by=str(second_Period_year))
        
        Total_Distance['Vessel Name'] = Total_Distance['imo'].map(col_vsl)
        Total_Distance['Vessel - IMO'] = Total_Distance['Vessel Name']
        
        if first_Period:
            Total_Distance = Total_Distance.rename({'average_distance': first_Period}, axis=1)
            melted_data = pd.melt(Total_Distance, id_vars=['Vessel - IMO'], value_vars=[first_Period, second_Period] if second_Period else [first_Period], var_name='Year', value_name='Total_Distance')
        else:
            Total_Distance = Total_Distance.rename({'average_distance': str(first_Period_year)}, axis=1)
            melted_data = pd.melt(Total_Distance, id_vars=['Vessel - IMO'], value_vars=[str(first_Period_year), str(second_Period_year)] if second_Period else [str(first_Period_year)], var_name='Year', value_name='Total_Distance')
        
        # Drop rows with NaN values in 'Total_Distance'
        melted_data.dropna(subset=['Total_Distance'], inplace=True)
        
        Total_Distance_Graph = px.bar(
            melted_data,
            x='Vessel - IMO',
            y='Total_Distance',
            barmode='group', 
            color='Year',
            color_discrete_sequence=['#c44332', '#1a75c1'],
            labels={'Total_Distance': 'Total Distance (Nm)'},
            title='Total Distance',
        )
        
        layout_total_distance = go.Layout(
            title=dict(
                text='Total Distance',
                font=dict(size=20, family='Roboto, sans-serif', color='black'),
                x=0.5
            ),
            xaxis=dict(
                title='Vessel Name',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False
            ),
            yaxis=dict(
                title='Total Distance (Nm)',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False
            ),
            legend=dict(
                title='',
                font=dict(size=15),
                bgcolor='rgba(0, 0, 0, 0)'
            ),
            width=1000,
            height=600
        )
        
        Total_Distance_Graph.update_layout(layout_total_distance)
        plot_div9 = pyo.plot(Total_Distance_Graph, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        
        
        # Total Distance Period Wise Difference
        if (first_Period and second_Period) != None:
            Total_Distance['Difference'] = Total_Distance[second_Period] - Total_Distance[first_Period]
        else:
            Total_Distance['Difference'] = Total_Distance[str(second_Period_year)] - Total_Distance[str(first_Period_year)]
 
       
        Total_Distance = Total_Distance.sort_values(by='Difference', ascending=False)
 
 
 
        # Plotly bar chart for Total Distance Period Wise Difference
        Total_Distance_diff_graph = px.bar(
            Total_Distance,
            x='Vessel - IMO',
            y='Difference',
            barmode='group', 
            labels={'Difference': 'Total Distance Difference (Nm)'},
            color_discrete_sequence=['#c44332'] * len(Total_Distance),  # Assign the color to each bar
        )
 
        # Update the layout
        Total_Distance_diff_graph.update_layout(
            xaxis=dict(title='Vessel Name', tickfont=dict(size=18, family='Times New Roman')),
            yaxis=dict(title='Total Distance Difference (Nm)', tickfont=dict(size=18, family='Times New Roman')),
            showlegend=False,
            width=1000,
            height=600
        )
 
        # Save or display the figure
        #Total_Distance_diff_graph.show()
        plot_div10 = pyo.plot(Total_Distance_diff_graph, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
       
 
        html_table = "<table border='1'>\n"
        # Create table header
        html_table += "<tr>"
        for col in Table_1_Year[0]:
            html_table += f"<th>{col}</th>"
        html_table += "</tr>\n"

        # Iterate over rows
        for row in Table_1_Year[1:]:
            html_table += "<tr>"
            for value in row:
                html_table += f"<td>{value}</td>"
            html_table += "</tr>\n"

        html_table += "</table>"

        html_table2 = "<table border='1'>\n"
        # Create table header
        html_table2 += "<tr>"
        for col in Table_2_new.columns:
            html_table2 += f"<th>{col}</th>"
        html_table2 += "</tr>\n"

        # Iterate over rows
        for index, row in Table_2_new.iterrows():
            html_table2 += "<tr>"
            for value in row:
                html_table2 += f"<td>{value}</td>"
            html_table2 += "</tr>\n"

        html_table2 += "</table>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title> YEAR 2023-2024 EEOI ANALYSIS </title>
            <style>
                body {{
                    text-align: center;
                    font-family: 'Roboto', sans-serif;
                    color: #333;
                    background-color: #fff;
                }}
                h1 {{
                    color: #193185;
                    font-size: 36px;
                    margin-bottom: 20px;
                }}
                h2{{
                    color: #193185;
                    font-size: 30px; 

                }}
                img {{
                    width: 100px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;
                    display: flex;
                    font-size: 16px;
                    font-weight: bold;
                }}

                .second-info{{ margin-left: 100px;}}
                table {{
                    margin: 20px auto;
                        width: 65%;
                        border-collapse: collapse;
                        border: solid;

                }}

                    table, tr, td {{height: 30px;
                        border: 1px solid;
                    }}
                .plot_div{{
                            width: 100%;
                            display: flex;
                            justify-content: center;
                }}

                hr {{
                    border-width: 3px;
                    border-color: #33;
                    margin-top: 20px;
                    border-style: solid; /* Add border style */
                }}


                th {{
            background: blue;
            color: white;
            height: 41px;
        }}
            </style>
        </head>
        <body>

            <br>
            <br>
            <br>
            <br>
            <br>
            <h1>YEAR 2023-2024 EEOI ANALYSIS </h1>  
            <hr>
            <br>
            <div class="info">
             
                <div class='first-info'>
                <p>Vessel Name:{vessel_name} </p>
                {   
                    "<p>First Period: "+ first_Period + "</p><p> Second Period: " + second_Period + "</p>" if first_Period and second_Period != 'null' else
                    "<p>First Period: " + first_period_min + " to " + first_period_max  + "</p>"
                    "<p>Second Period: " + second_period_min + " to " + second_period_max + "</p>"}        
                </div>
            </div>
            <hr>
            <br>
            {html_table}
            <br>
            <h2>YEARLY EEOI ANALYSIS</h2>
            <!-- Add the centered and bigger table -->
            <br>
            {html_table2}
            <br>
            <br>
            <br>
            <h2>EEOI ANALYSIS</h2>
            <div class="plot_div">
                {plot_div}
            </div>
            <br>
            <br>
            <h2>YEARLY % IMPROVEMENT- EEOI ANALYSIS</h2>
            <div class="plot_div">
                {plot_div2}
            </div>
            <br>
            <br>
            <h2>TOTAL CARGO</h2>
            <div class="plot_div">
                {plot_div7}
            </div>
            <h2>TOTAL CARGO PERIOD WISE DIFFERENCE </h2>
            <div class="plot_div">
                {plot_div8}
            </div>
            <h2>TOTAL DISATNCE</h2>
            <div class="plot_div">
                {plot_div9}
            </div>
            <h2>TOTAL DISTANCE PERIOD WISE DIFFERENCE </h2>
            <div class="plot_div">
                {plot_div10}
            </div>
            <h2>YEARLY EEOI MOVING AVERAGE [MT]</h2>
            <div class="plot_div">
                {plot_div3}
            </div>    
            <h2>YEARLY EEOI MOVING AVERAGE [TEU]</h2>
            <div class="plot_div">
                {plot_div4}
            </div> 
            <br>
        </body>
        </html>
        """

        
        
        
        
        
        
        
        
        
        
        
        
        

    elif report_type == "fleet":
        Table1 = pd.DataFrame.from_dict(s['data']['table1']['table1']).fillna(0)
        Table1['improvement'] = Table1['improvement'].astype(float).astype(int)
        Table1_str = Table1[['index', 'year1', 'year2', 'improvement']].astype(str)
        Table1_str['improvement'] = Table1_str['improvement'] + ' %'

        Table_1_head_Year = [['Year', first_Period, second_Period, '% Improvement']] if all((first_Period, second_Period)) else [['Year', str(first_Period_year), str(second_Period_year), '% Improvement']]
        Table_1_Year = Table_1_head_Year + Table1_str.values.tolist()

        # 2nd Table
        Table_2 = Table1.set_index(['index'])
        Table_2 = Table_2.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]].reset_index()

        Table_2 = Table_2.rename({'improvement': 'Improvement (%)', 'year1': first_Period, 'year2': second_Period, 'index': 'Year'}, axis=1) if all((first_Period, second_Period)) else Table_2.rename({'improvement': 'Improvement (%)', 'year1': str(first_Period_year), 'year2': str(second_Period_year), 'index': 'Year'}, axis=1)

        Table_2_new = Table_2.T.reset_index().T.set_index(0).T
        Table_2_str = Table_2_new.astype(str)


        FirstPeriodData = pd.DataFrame.from_dict(s['data']['FirstPeriodData'])
        FirstPeriodData_1 = FirstPeriodData[['Vessel Name', 'Cargo Total (MT)', 'Cargo Total (TEU)', 'Distance (NM)','Number of Voyages','Total CO2 (MT)',
                                        'Equivalent HFO (MT)','EEOI (gm/MT-NM)', 'EEOI (gm/TEU-NM)','Fuel per Miles(Kg/NM)','Distance per Voyage (NM)',
                                        'Fuel Consumption per Voyage (MT)']].round(2)
        # FirstPeriodData_1['eeoi_mt'] = FirstPeriodData_1['eeoi_mt'].astype('float32')
        # FirstPeriodData_1['eeoi_teu'] = FirstPeriodData_1['eeoi_teu'].astype('float32')
        FirstPeriodData_str = FirstPeriodData_1.astype(str)
        SecondPeriodData = pd.DataFrame.from_dict(s['data']['SecondPeriodData'])
        SecondPeriodData['Vessel Name'].nunique()
        SecondPeriodData_1 = SecondPeriodData[['Vessel Name', 'Cargo Total (MT)', 'Cargo Total (TEU)', 'Distance (NM)','Number of Voyages','Total CO2 (MT)',
                                        'Equivalent HFO (MT)','EEOI (gm/MT-NM)', 'EEOI (gm/TEU-NM)','Fuel per Miles(Kg/NM)','Distance per Voyage (NM)',
                                        'Fuel Consumption per Voyage (MT)']].round(2)
        SecondPeriodData_str = SecondPeriodData_1.astype(str)


        vsl_name = pd.DataFrame.from_dict(s['vessel_data'])
        col_vsl = dict(zip(vsl_name['imo'], vsl_name['name']))
        #s = s['data']

        Year1_Graph = pd.DataFrame.from_dict(s['data']['year1']['finaldata']).round(2)
        Year2_Graph = pd.DataFrame.from_dict(s['data']['year2']['finaldata']).round(2)
        EEOI_Analysis = Table1.set_index(['index'])
        EEOI_Analysis = EEOI_Analysis.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        EEOI_Analysis = EEOI_Analysis[['year1', 'year2']]

        EEOI_Analysis_new = EEOI_Analysis.rename({"year1": first_Period, 'year2': second_Period}, axis=1) if all((first_Period, second_Period)) else EEOI_Analysis.rename({"year1": str(first_Period_year), 'year2': str(second_Period_year)}, axis=1)

        # EEOI_Analysis_Graph = EEOI_Analysis_new.plot.bar(rot=0, color={first_Period: "#588aee", second_Period: "#61d8a8"}, width=0.8, figsize=(10, 6))

        EEOI_Analysis = Table1.set_index(['index'])
        EEOI_Analysis = EEOI_Analysis.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        EEOI_Analysis = EEOI_Analysis[['year1', 'year2']]

        EEOI_Analysis_1 = EEOI_Analysis_new.columns[0]
        EEOI_Analysis_2 = EEOI_Analysis_new.columns[1]

        # Create a bar chart for each trace with values above the bars
        trace1 = go.Bar(
            x=EEOI_Analysis.index,
            y=EEOI_Analysis['year1'],
            text=EEOI_Analysis['year1'].round(2),  # Adjust rounding as needed
            textposition='outside',  # Display text labels outside the bars
            name=EEOI_Analysis_1,
            marker=dict(color="#588aee")
        )

        trace2 = go.Bar(
            x=EEOI_Analysis.index,
            y=EEOI_Analysis['year2'],
            text=EEOI_Analysis['year2'].round(2),
            textposition='outside',
            name=EEOI_Analysis_2,  # Use the dynamically generated legend label
            marker=dict(color="#61d8a8")
        )

        layout = go.Layout(
            xaxis=dict(
                title=' ',
                tickfont=dict(size=17),
                showgrid=False  # Correct syntax for showgrid
            ),
            yaxis=dict(
                title='Value',
                tickfont=dict(size=17),
                showgrid=False  # Correct syntax for showgrid
            ),
            showlegend=True,
            legend=dict(
                x=1,  # Adjust the x position of the legend
                y=1,  # Adjust the y position of the legend
                font=dict(size=15),  # Adjust the font size of the legend
                bgcolor='rgba(0, 0, 0, 0)'  # Make the legend background transparent
            ),
            width=1050,
            height=600
        )

        fig_eeoi = go.Figure(data=[trace1, trace2], layout=layout)
        #fig.show()
        plot_div = pyo.plot(fig_eeoi, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        Improvement_Percent = Table1.set_index(['index'])
        Improvement_Percent = Improvement_Percent.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        Improvement_Percent = Improvement_Percent[['improvement']].reset_index()
        Improvement_Percent = Improvement_Percent.set_index(['index'])

        fig_improvement = go.Figure()

        fig_improvement.add_trace(go.Bar(
            x=Improvement_Percent.index,
            y=Improvement_Percent['improvement'],
            text=Improvement_Percent['improvement'].astype('str') + '%',
            textposition='outside',  # Display text outside the bar
            marker=dict(color='#808080')  
        ))

        layout = go.Layout(
            xaxis=dict(
                title='',
                tickfont=dict(size=17),
                showgrid=False  # Correct syntax for showgrid
            ),
            yaxis=dict(
                title='% Improvement',
                tickfont=dict(size=17),
                showgrid=False  # Correct syntax for showgrid
            ),
            showlegend=False,
            width=1000,
            height=600
        )
        # Format y-axis tick labels as percentages
        layout['yaxis']['tickformat'] = '.3f%'

        fig_improvement.update_layout(layout)
        plot_div2 = pyo.plot(fig_improvement, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        Energy_Efficiency = Year1_Graph[['imo', 'eeoi_mt']].rename(columns={'eeoi_mt': str(first_Period_year)})
        Energy_Efficiency[str(second_Period or second_Period_year)] = Energy_Efficiency['imo'].map(
            Year2_Graph.set_index('imo')['eeoi_mt']
        )
        Energy_Efficiency['Vessel Name'] = Energy_Efficiency['imo'].map(col_vsl)

        # Melt the data for easy plotting
        melted_data = pd.melt(
            Energy_Efficiency, 
            id_vars=['Vessel Name'], 
            value_vars=[str(first_Period_year), str(second_Period or second_Period_year)],
            var_name='Year', 
            value_name='Energy_Efficiency'
        )

        # Create the bar plot
        fig_energy = px.bar(
            melted_data,
            x='Vessel Name',
            y='Energy_Efficiency',
            color='Year',
            color_discrete_sequence=['#c44332', '#1a75c1'],
            title='Energy Efficiency'
        )

        # Customize the layout
        layout = go.Layout(
            title=dict(text='Energy Efficiency', font=dict(size=20), x=0.5),
            xaxis=dict(title='Vessel Name', tickfont=dict(size=18)),
            yaxis=dict(title='Energy Efficiency (g/Ton-Nm)', tickfont=dict(size=18)),
            legend=dict(font=dict(size=15), bgcolor='rgba(0, 0, 0, 0)'),
            barmode='group',
            width=1050,
            height=750
        )

        # Apply layout to the figure
        fig_energy.update_layout(layout)

        # Display the figure
        #fig3.show()    
        plot_div5 = pyo.plot(fig_energy, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        Total_Cargo = Year1_Graph[['imo', 'cargomt']].rename(columns={'cargomt': str(first_Period_year)})

        # Adding data from the second period (if available)
        Total_Cargo[str(second_Period or second_Period_year)] = Total_Cargo['imo'].map(
            Year2_Graph.set_index('imo')['cargomt']
        )

        # Mapping the vessel name based on IMO
        Total_Cargo['Vessel Name'] = Total_Cargo['imo'].map(col_vsl)

        # Melting the data for easy plotting
        melted_data_cargo = pd.melt(
            Total_Cargo, 
            id_vars=['Vessel Name'], 
            value_vars=[str(first_Period_year), str(second_Period or second_Period_year)],
            var_name='Year',  # Using 'Year' as the column name
            value_name='Total_Cargo'
        )

        # Create the bar plot with melted data
        fig_cargo = px.bar(
            melted_data_cargo,
            x='Vessel Name',
            y='Total_Cargo',
            color='Year',  # Using 'Year' as the color column
            color_discrete_sequence=['#c44332', '#1a75c1'],
            title='Total Cargo'
        )

        # Customize the layout
        layout_cargo = go.Layout(
            title=dict(text='Total Cargo', font=dict(size=20), x=0.5),
            xaxis=dict(title='Vessel Name', tickfont=dict(size=18), tickangle=-90),
            yaxis=dict(title='Total Cargo (metric-Tonne)', tickfont=dict(size=18)),
            legend=dict(font=dict(size=15), bgcolor='rgba(0, 0, 0, 0)'),
            barmode='group',
            width=1050,
            height=750
        )

        # Apply layout to the figure
        fig_cargo.update_layout(layout_cargo)

        plot_div7 = pyo.plot(fig_cargo, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        # Total Distance
        Total_Distance = Year1_Graph[['imo', 'average_distance']].rename(columns={'average_distance': str(first_Period_year)})

        # Adding second period data if available
        if second_Period:
            Total_Distance[str(second_Period)] = Total_Distance['imo'].map(
                Year2_Graph.set_index('imo')['average_distance']
            )
        else:
            Total_Distance[str(second_Period_year)] = Total_Distance['imo'].map(
                Year2_Graph.set_index('imo')['average_distance']
            )

        # Mapping Vessel Names based on IMO numbers
        Total_Distance['Vessel Name'] = Total_Distance['imo'].map(col_vsl)

        # Renaming the period column to the first period year
        if first_Period != 'null':
            Total_Distance = Total_Distance.rename({str('average_distance'): first_Period}, axis=1)
        else:
            Total_Distance = Total_Distance.rename({str('average_distance'): str(first_Period_year)}, axis=1)

        # Melting the data for easy plotting
        melted_data_distance = pd.melt(
            Total_Distance,
            id_vars=['Vessel Name'],
            value_vars=[str(first_Period), str(second_Period or second_Period_year)],
            var_name='Year',  # This will label the period/year column as 'Year'
            value_name='Total_Distance'
        )

        # Create the bar plot using Plotly Express
        fig_distance = px.bar(
            melted_data_distance,
            x='Vessel Name',
            y='Total_Distance',
            color='Year',  # Color bars based on the 'Year' column
            color_discrete_sequence=['#c44332', '#1a75c1'],
            title='Total Distance'
        )

        # Customize the layout for the graph
        layout_total_distance = go.Layout(
            title=dict(
                text='Total Distance', 
                font=dict(size=20, family='Roboto, sans-serif', color='black'),
                x=0.5  # Center the title horizontally
            ),
            xaxis=dict(
                title='Vessel Name',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False,
                tickangle=-90# Hides the gridlines for the x-axis
            ),
            yaxis=dict(
                title='Total Distance (Nm)',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False  # Hides the gridlines for the y-axis
            ),
            legend=dict(
                title='',  # Remove legend title
                font=dict(size=15),  # Adjust the font size of the legend
                bgcolor='rgba(0, 0, 0, 0)'  # Make the legend background transparent
            ),
            barmode='group',  # Group bars for each vessel
            width=1000,
            height=600
        )

        # Apply layout to the figure
        fig_distance.update_layout(layout_total_distance)

        # Save or display the figure
        plot_div9 = pyo.plot(fig_distance, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        Table_3_head_Year=[['Vessel Name','Cargomt','Cargoteu','Distance','EEOI_Voy_no','Totalco2_mt','Totalco2_kgnm',
                                                        'EEOI_mt', 'EEOI_teu','Fuelkg_nm','Average Distance','Average Fuelcons']]

        Table_3_Year1 =Table_3_head_Year+ FirstPeriodData_str.values.tolist()

        Table_4_head_Year=[['Vessel Name','Cargomt','Cargoteu','Distance','EEOI_Voy_no','Totalco2_mt','Totalco2_kgnm',
                                            'EEOI_mt', 'EEOI_teu','Fuelkg_nm','Average Distance','Average Fuelcons']]


        Table_4_Year2 =Table_4_head_Year+ SecondPeriodData_str.values.tolist()
        
        
        html_table = "<table border='1'>\n"
        # Create table header
        html_table += "<tr>"
        for col in Table_1_Year[0]:
            html_table += f"<th>{col}</th>"
        html_table += "</tr>\n"

        # Iterate over rows
        for row in Table_1_Year[1:]:
            html_table += "<tr>"
            for value in row:
                html_table += f"<td>{value}</td>"
            html_table += "</tr>\n"

        html_table += "</table>"

        html_table2 = "<table border='1'>\n"
        # Create table header
        html_table2 += "<tr>"
        for col in Table_2_new.columns:
            html_table2 += f"<th>{col}</th>"
        html_table2 += "</tr>\n"

        # Iterate over rows
        for index, row in Table_2_new.iterrows():
            html_table2 += "<tr>"
            for value in row:
                html_table2 += f"<td>{value}</td>"
            html_table2 += "</tr>\n"

        html_table2 += "</table>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title> YEAR 2023-2024 EEOI ANALYSIS </title>
            <style>
                body {{
                    text-align: center;
                    font-family: 'Roboto', sans-serif;
                    color: #333;
                    background-color: #fff;
                }}
                h1 {{
                    color: #193185;
                    font-size: 36px;
                    margin-bottom: 20px;
                }}
                h2{{
                    color: #193185;
                    font-size: 30px; 

                }}
                img {{
                    width: 100px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;
                    display: flex;
                    font-size: 16px;
                    font-weight: bold;
                }}

                .second-info{{ margin-left: 100px;}}
                table {{
                    margin: 20px auto;
                        width: 65%;
                        border-collapse: collapse;
                        border: solid;

                }}

                    table, tr, td {{height: 30px;
                        border: 1px solid;
                    }}
                .plot_div{{
                            width: 100%;
                            display: flex;
                            justify-content: center;
                }}

                hr {{
                    border-width: 3px;
                    border-color: #33;
                    margin-top: 20px;
                    border-style: solid; /* Add border style */
                }}


                th {{
            background: blue;
            color: white;
            height: 41px;
        }}
            </style>
        </head>
        <body>
            <br>
            <br>
            {image_tag}
            
            <br>
            <br>
            <br>
            <h1>YEAR 2023-2024 EEOI ANALYSIS </h1>  
            <hr>
            <br>
            <div class="info">
                <div class='first-info'>
                <p>Fleet:{fleet}</p>
                {
                    "<p>First Period: "+ first_Period + "</p><p> Second Period: " + second_Period + "</p>" if first_Period and second_Period != 'null' else
                    "<p>First Period: " + first_period_min + " to " + first_period_max  + "</p>"
                    "<p>Second Period: " + second_period_min + " to " + second_period_max + "</p>"}        
                </div>
            </div>
            <hr>
            <br>
            {html_table}
            <br>
            <h2>YEARLY EEOI ANALYSIS</h2>
            <!-- Add the centered and bigger table -->
            <br>
            {html_table2}
            <br>
            <br>
            <br>
            <h2>EEOI ANALYSIS</h2>
            <div class="plot_div">
                {plot_div}
            </div>
            <br>
            <br>
            <h2>YEARLY % IMPROVEMENT- EEOI ANALYSIS</h2>
            <div class="plot_div">
                {plot_div2}
            </div>
            <br>
            <br>
            <h2>ENERGY EFFICENCY (GM/TONNE-MILE)</h2>
            <div class="plot_div">
                {plot_div5}
            </div>
            <br>
            <br>
            <h2>TOTAL CARGO</h2>
            <div class="plot_div">
                {plot_div7}
            </div>

            <h2>TOTAL DISATNCE</h2>
            <div class="plot_div">
                {plot_div9}
            </div>
            <br>
        </body>
        </html>
        """
        print("fleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeet")
        print("fleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeet",report_type)


    else: #class
        vsl_name = pd.DataFrame.from_dict(s['vessel_data'])
        col_vsl = dict(zip(vsl_name['imo'], vsl_name['name']))
        #s = s['data']

        Table1 = pd.DataFrame.from_dict(s['data']['table1']['table1']).fillna(0)
        Table1['improvement'] = Table1['improvement'].astype(float).astype(int)
        Table1_str = Table1[['index', 'year1', 'year2', 'improvement']].astype(str)
        Table1_str['improvement'] = Table1_str['improvement'] + ' %'

        Table_1_head_Year = [['Year', first_Period, second_Period, '% Improvement']] if all((first_Period, second_Period)) else [['Year', str(first_Period_year), str(second_Period_year), '% Improvement']]
        Table_1_Year = Table_1_head_Year + Table1_str.values.tolist()

        # 2nd Table
        Table_2 = Table1.set_index(['index'])
        Table_2 = Table_2.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]].reset_index()

        Table_2 = Table_2.rename({'improvement': 'Improvement (%)', 'year1': first_Period, 'year2': second_Period, 'index': 'Year'}, axis=1) if all((first_Period, second_Period)) else Table_2.rename({'improvement': 'Improvement (%)', 'year1': str(first_Period_year), 'year2': str(second_Period_year), 'index': 'Year'}, axis=1)

        Table_2_new = Table_2.T.reset_index().T.set_index(0).T
        Table_2_str = Table_2_new.astype(str)
        
        FirstPeriodData = pd.DataFrame.from_dict(s['data']['FirstPeriodData'])
        FirstPeriodData_1 = FirstPeriodData[['Vessel Name', 'Cargo Total (MT)', 'Cargo Total (TEU)', 'Distance (NM)','Number of Voyages','Total CO2 (MT)',
                                        'Equivalent HFO (MT)','EEOI (gm/MT-NM)', 'EEOI (gm/TEU-NM)','Fuel per Miles(Kg/NM)','Distance per Voyage (NM)',
                                        'Fuel Consumption per Voyage (MT)']].round(2)
        # FirstPeriodData_1['eeoi_mt'] = FirstPeriodData_1['eeoi_mt'].astype('float32')
        # FirstPeriodData_1['eeoi_teu'] = FirstPeriodData_1['eeoi_teu'].astype('float32')
        FirstPeriodData_str = FirstPeriodData_1.astype(str)
        SecondPeriodData = pd.DataFrame.from_dict(s['data']['SecondPeriodData'])
        SecondPeriodData['Vessel Name'].nunique()
        SecondPeriodData_1 = SecondPeriodData[['Vessel Name', 'Cargo Total (MT)', 'Cargo Total (TEU)', 'Distance (NM)','Number of Voyages','Total CO2 (MT)',
                                        'Equivalent HFO (MT)','EEOI (gm/MT-NM)', 'EEOI (gm/TEU-NM)','Fuel per Miles(Kg/NM)','Distance per Voyage (NM)',
                                        'Fuel Consumption per Voyage (MT)']].round(2)
        SecondPeriodData_str = SecondPeriodData_1.astype(str)


        Year1_Graph = pd.DataFrame.from_dict(s['data']['year1']['finaldata']).round(2)
        Year2_Graph = pd.DataFrame.from_dict(s['data']['year2']['finaldata']).round(2)
        EEOI_Analysis = Table1.set_index(['index'])
        EEOI_Analysis = EEOI_Analysis.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        EEOI_Analysis = EEOI_Analysis[['year1', 'year2']]

        EEOI_Analysis_new = EEOI_Analysis.rename({"year1": first_Period, 'year2': second_Period}, axis=1) if all((first_Period, second_Period)) else EEOI_Analysis.rename({"year1": str(first_Period_year), 'year2': str(second_Period_year)}, axis=1)

            # EEOI_Analysis_Graph = EEOI_Analysis_new.plot.bar(rot=0, color={first_Period: "#588aee", second_Period: "#61d8a8"}, width=0.8, figsize=(10, 6))

        EEOI_Analysis = Table1.set_index(['index'])
        EEOI_Analysis = EEOI_Analysis.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        EEOI_Analysis = EEOI_Analysis[['year1', 'year2']]

        EEOI_Analysis_1 = EEOI_Analysis_new.columns[0]
        EEOI_Analysis_2 = EEOI_Analysis_new.columns[1]

        # Create a bar chart for each trace with values above the bars
        trace1 = go.Bar(
        x=EEOI_Analysis.index,
        y=EEOI_Analysis['year1'],
        text=EEOI_Analysis['year1'].round(2),  # Adjust rounding as needed
        textposition='outside',  # Display text labels outside the bars
        name=EEOI_Analysis_1,
        marker=dict(color="#588aee")
        )

        trace2 = go.Bar(
        x=EEOI_Analysis.index,
        y=EEOI_Analysis['year2'],
        text=EEOI_Analysis['year2'].round(2),
        textposition='outside',
        name=EEOI_Analysis_2,  # Use the dynamically generated legend label
        marker=dict(color="#61d8a8")
        )

        layout = go.Layout(
        xaxis=dict(
            title=' ',
            tickfont=dict(size=17),
            showgrid=False  # Correct syntax for showgrid
        ),
        yaxis=dict(
            title='Value',
            tickfont=dict(size=17),
            showgrid=False  # Correct syntax for showgrid
        ),
        showlegend=True,
        legend=dict(
            x=1,  # Adjust the x position of the legend
            y=1,  # Adjust the y position of the legend
            font=dict(size=15),  # Adjust the font size of the legend
            bgcolor='rgba(0, 0, 0, 0)'  # Make the legend background transparent
        ),
        width=1050,
        height=600
        )

        fig = go.Figure(data=[trace1, trace2], layout=layout)
        #fig.show()
        plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

        Improvement_Percent = Table1.set_index(['index'])
        Improvement_Percent = Improvement_Percent.loc[["CO2[MT/NM]", "EEOI for Cargo [TEU]",'EEOI for Cargo [MT]',"Total equiv. HFO [Kilo MT]"]]
        Improvement_Percent = Improvement_Percent[['improvement']].reset_index()
        Improvement_Percent = Improvement_Percent.set_index(['index'])

        fig = go.Figure()

        fig.add_trace(go.Bar(
        x=Improvement_Percent.index,
        y=Improvement_Percent['improvement'],
        text=Improvement_Percent['improvement'].astype('str') + '%',
        textposition='outside',  # Display text outside the bar
        marker=dict(color='#808080')  
        ))

        layout = go.Layout(
        xaxis=dict(
            title='',
            tickfont=dict(size=17),
            showgrid=False  # Correct syntax for showgrid
        ),
        yaxis=dict(
            title='% Improvement',
            tickfont=dict(size=17),
            showgrid=False  # Correct syntax for showgrid
        ),
        showlegend=False,
        width=1000,
        height=600
        )
        # Format y-axis tick labels as percentages
        layout['yaxis']['tickformat'] = '.3f%'

        fig.update_layout(layout)

        #fig.show()

        plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
        
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

        if (first_Period and second_Period) != None:
           melted_data = pd.melt(Energy_Efficiency, id_vars=['Vessel - IMO'], value_vars=[first_Period, second_Period], var_name='Period', value_name='Energy_Efficiency')
           Energy_Efficiency_graph = px.bar(
                melted_data,
                x='Vessel - IMO',
                y='Energy_Efficiency',
                color='Period',
                color_discrete_sequence=['#c44332', '#1a75c1'],  # Medium red and blue
                labels={'value': 'Energy Efficiency (g/Ton-Nm)'},
                title='Energy Efficiency',
            )

        else:
            Energy_Efficiency_graph = px.bar(
                Energy_Efficiency,
                x='Vessel - IMO',
                y=[str(first_Period_year), str(second_Period_year)],
                color_discrete_sequence=['#c44332', '#1a75c1'],  # Medium red and blue
                labels={'value': 'Energy Efficiency (g/Ton-Nm)'},
                title='Energy Efficiency',
            )


        # Update the layout
        layout = go.Layout(
        title=dict(
            text='Energy Efficiency',
            font=dict(size=20, family='Roboto, sans-serif', color='black'),
            x=0.5  # Center the title horizontally
        ),
        xaxis=dict(
            title='Vessel Name',
            tickfont=dict(size=18, family='Roboto, sans-serif'),
            showgrid=False  # Correct syntax for showgrid
        ),
        yaxis=dict(
            title='Energy Efficiency (g/Ton-Nm)',
            tickfont=dict(size=18, family='Roboto, sans-serif'),
            showgrid=False  # Correct syntax for showgrid
        ),
        legend=dict(
            title='',  # Set an empty string to remove the legend title
            font=dict(size=15),  # Adjust the font size of the legend
            bgcolor='rgba(0, 0, 0, 0)'  # Make the legend background transparent
        ),
        barmode='group',  # 'group' for grouped bars
        width=1050,
        height=750
        )

        Energy_Efficiency_graph.update_layout(layout)

        plot_div5 = pyo.plot(Energy_Efficiency_graph, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        Total_Cargo = Year1_Graph[['imo', 'cargomt']]
        
        # Handle the second period's data
        if second_Period:
            Total_Cargo[str(second_Period_year)] = Total_Cargo['imo'].map(Year2_Graph.set_index('imo')['cargomt'])
            Total_Cargo = Total_Cargo.sort_values(by=str(second_Period_year))
        else:
            Total_Cargo[str(second_Period_year)] = Total_Cargo['imo'].map(Year2_Graph.set_index('imo')['cargomt'])
            Total_Cargo = Total_Cargo.sort_values(by=str(second_Period_year))
        
        # Map Vessel Names
        Total_Cargo['Vessel Name'] = Total_Cargo['imo'].map(col_vsl)
        Total_Cargo['Vessel - IMO'] = Total_Cargo['Vessel Name']

        
        
        # Handle the first period column renaming
        if first_Period != 'null':
            Total_Cargo = Total_Cargo.rename({'cargomt': first_Period}, axis=1)
            y_columns = [first_Period, str(second_Period_year)] if second_Period else [first_Period]
            color_sequence = ['#c44332', '#1a75c1'] if second_Period else ['#c44332']
        else:
            Total_Cargo = Total_Cargo.rename({'cargomt': str(first_Period_year)}, axis=1)
            y_columns = [str(first_Period_year), str(second_Period_year)] if second_Period else [str(first_Period_year)]
            color_sequence = ['#c44332', '#1a75c1'] if second_Period else ['#c44332']

        # Melt the DataFrame for Plotly
        Total_Cargo_melted = Total_Cargo.melt(
            id_vars=['Vessel - IMO'], 
            value_vars=y_columns, 
            var_name='Year', 
            value_name='Total Cargo (metric-Tonne)'
        )
        
        # Update the 'Year' column to ensure it contains proper labels
        Total_Cargo_melted['Year'] = Total_Cargo_melted['Year'].astype(str)
        
        # Create the grouped bar chart
        Total_Cargo_Graph = px.bar(
            Total_Cargo_melted,
            x='Vessel - IMO',
            y='Total Cargo (metric-Tonne)',
            color='Year',  # Use 'Year' as the legend and hover variable
            barmode='group',
            color_discrete_sequence=color_sequence,
            labels={
                'Total Cargo (metric-Tonne)': 'Total Cargo (metric-Tonne)',  # Adjust y-axis label
                'Year': 'Year'  # Legend and hover label for years
            },
            title='Total Cargo'
        )

        
        # Update layout
        layout_total_cargo = go.Layout(
            title=dict(
                text='Total Cargo',
                font=dict(size=20, family='Roboto, sans-serif', color='black'),
                x=0.5
            ),
            xaxis=dict(
                title='Vessel Name',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False
            ),
            yaxis=dict(
                title='Total Cargo (metric-Tonne)',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False
            ),
            legend=dict(
                title='',
                font=dict(size=15),
                bgcolor='rgba(0, 0, 0, 0)'
            ),
            width=1050,
            height=650
        )
        
        # Apply layout and display the chart
        Total_Cargo_Graph.update_layout(layout_total_cargo)
        plot_div7 = pyo.plot(Total_Cargo_Graph, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


        # Total Distance
        Total_Distance = Year1_Graph[['imo', 'average_distance']]
        
        if second_Period:
            Total_Distance[str(second_Period_year)] = Total_Distance['imo'].map(Year2_Graph.set_index('imo')['average_distance'])
            Total_Distance = Total_Distance.sort_values(by=str(second_Period_year))
        else:
            Total_Distance[str(second_Period_year)] = Total_Distance['imo'].map(Year2_Graph.set_index('imo')['average_distance'])
            Total_Distance = Total_Distance.sort_values(by=str(second_Period_year))
        
        # Map Vessel Names
        Total_Distance['Vessel Name'] = Total_Distance['imo'].map(col_vsl)
        Total_Distance['Vessel - IMO'] = Total_Distance['Vessel Name']
        
        # Handle the first period column renaming
        if first_Period != 'null':
            Total_Distance = Total_Distance.rename({'average_distance': first_Period}, axis=1)
            y_columns = [first_Period, str(second_Period_year)] if second_Period else [first_Period]
            color_sequence = ['#c44332', '#1a75c1'] if second_Period else ['#c44332']
        else:
            Total_Distance = Total_Distance.rename({'average_distance': str(first_Period_year)}, axis=1)
            y_columns = [str(first_Period_year), str(second_Period_year)] if second_Period else [str(first_Period_year)]
            color_sequence = ['#c44332', '#1a75c1'] if second_Period else ['#c44332']
        
        # Melt the DataFrame for Plotly
        Total_Distance_melted = Total_Distance.melt(
            id_vars=['Vessel - IMO'], 
            value_vars=y_columns, 
            var_name='Year', 
            value_name='Total Distance (Nm)'
        )
        
        # Update the 'Year' column to ensure it contains proper labels
        Total_Distance_melted['Year'] = Total_Distance_melted['Year'].astype(str)
        
        # Plotly bar chart for Total Distance
        Total_Distance_Graph = px.bar(
            Total_Distance_melted,
            x='Vessel - IMO',
            y='Total Distance (Nm)',
            color='Year',  # Use 'Year' as the legend and hover variable
            barmode='group',
            color_discrete_sequence=color_sequence,
            labels={
                'Total Distance (Nm)': 'Total Distance (Nm)',  # Adjust y-axis label
                'Year': 'Year'  # Legend and hover label for years
            },
            title='Total Distance'
        )
        
        # Update the layout
        layout_total_distance = go.Layout(
            title=dict(
                text='Total Distance',
                font=dict(size=20, family='Roboto, sans-serif', color='black'),
                x=0.5  # Center the title horizontally
            ),
            xaxis=dict(
                title='Vessel Name',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False  # Remove grid lines
            ),
            yaxis=dict(
                title='Total Distance (Nm)',
                tickfont=dict(size=18, family='Roboto, sans-serif'),
                showgrid=False  # Remove grid lines
            ),
            legend=dict(
                title='',  # Remove the legend title
                font=dict(size=15),  # Adjust the font size of the legend
                bgcolor='rgba(0, 0, 0, 0)'  # Transparent legend background
            ),
            width=1000,
            height=600
        )
        
        # Apply layout to the graph
        Total_Distance_Graph.update_layout(layout_total_distance)
        # Save or display the figure
        plot_div9 = pyo.plot(Total_Distance_Graph, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})




        Table_3_head_Year=[['Vessel Name','Cargomt','Cargoteu','Distance','EEOI_Voy_no','Totalco2_mt','Totalco2_kgnm',
                                                    'EEOI_mt', 'EEOI_teu','Fuelkg_nm','Average Distance','Average Fuelcons']]

        Table_3_Year1 =Table_3_head_Year+ FirstPeriodData_str.values.tolist()

        Table_4_head_Year=[['Vessel Name','Cargomt','Cargoteu','Distance','EEOI_Voy_no','Totalco2_mt','Totalco2_kgnm',
                                        'EEOI_mt', 'EEOI_teu','Fuelkg_nm','Average Distance','Average Fuelcons']]


        Table_4_Year2 =Table_4_head_Year+ SecondPeriodData_str.values.tolist()
        
        
        
        html_table = "<table border='1'>\n"
        # Create table header
        html_table += "<tr>"
        for col in Table_1_Year[0]:
            html_table += f"<th>{col}</th>"
        html_table += "</tr>\n"

        # Iterate over rows
        for row in Table_1_Year[1:]:
            html_table += "<tr>"
            for value in row:
                html_table += f"<td>{value}</td>"
            html_table += "</tr>\n"

        html_table += "</table>"

        html_table2 = "<table border='1'>\n"
        # Create table header
        html_table2 += "<tr>"
        for col in Table_2_new.columns:
            html_table2 += f"<th>{col}</th>"
        html_table2 += "</tr>\n"

        # Iterate over rows
        for index, row in Table_2_new.iterrows():
            html_table2 += "<tr>"
            for value in row:
                html_table2 += f"<td>{value}</td>"
            html_table2 += "</tr>\n"

        html_table2 += "</table>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title> YEAR 2023-2024 EEOI ANALYSIS </title>
            <style>
                body {{
                    text-align: center;
                    font-family: 'Roboto', sans-serif;
                    color: #333;
                    background-color: #fff;
                }}
                h1 {{
                    color: #193185;
                    font-size: 36px;
                    margin-bottom: 20px;
                }}
                h2{{
                    color: #193185;
                    font-size: 30px; 

                }}
                img {{
                    width: 100px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;
                    display: flex;
                    font-size: 16px;
                    font-weight: bold;
                }}

                .second-info{{ margin-left: 100px;}}
                table {{
                    margin: 20px auto;
                        width: 65%;
                        border-collapse: collapse;
                        border: solid;

                }}

                    table, tr, td {{height: 30px;
                        border: 1px solid;
                    }}
                .plot_div{{
                            width: 100%;
                            display: flex;
                            justify-content: center;
                }}

                hr {{
                    border-width: 3px;
                    border-color: #33;
                    margin-top: 20px;
                    border-style: solid; /* Add border style */
                }}


                th {{
            background: blue;
            color: white;
            height: 41px;
        }}
            </style>
        </head>
        <body>

            <br>
            <br>
            <br>
            <br>
            <br>
            <h1>YEAR 2023-2024 EEOI ANALYSIS </h1>  
            <hr>
            <br>
            <div class="info">
                <div class='first-info'>
                <p>Class: {class_name} </p>
                 {
                   "<p>First Period: "+ first_Period + "</p><p> Second Period: " + second_Period + "</p>" if first_Period and second_Period != 'null' else
                    "<p>First Period: " + first_period_min + " to " + first_period_max  + "</p>"
                    "<p>Second Period: " + second_period_min + " to " + second_period_max + "</p>"}        
                </div>
            </div>
            <hr>
            <br>
            {html_table}
            <br>
            <h2>YEARLY EEOI ANALYSIS</h2>
            <!-- Add the centered and bigger table -->
            <br>
            {html_table2}
            <br>
            <br>
            <br>
            <h2>EEOI ANALYSIS</h2>
            <div class="plot_div">
                {plot_div}
            </div>
            <br>
            <br>
            <h2>YEARLY % IMPROVEMENT- EEOI ANALYSIS</h2>
            <div class="plot_div">
                {plot_div2}
            </div>
            <br>
            <br>
            <h2>ENERGY EFFICENCY (GM/TONNE-MILE)</h2>
            <div class="plot_div">
                {plot_div5}
            </div>
            <br>
            <br>
            <h2>TOTAL CARGO</h2>
            <div class="plot_div">
                {plot_div7}
            </div>

            <h2>TOTAL DISATNCE</h2>
            <div class="plot_div">
                {plot_div9}
            </div>
            <br>
        </body>
        </html>
        """

            
        #######################################################################################################################################################################
       
    file_name = 'period_comparison_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)
    return FileResponse(path = output_file,filename=file_name)




@router.post('/api/v1/html/voy/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None ,date_start:str = None, date_end:str = None,pid:str = None , vcode:str = None ):
    s = await info.json()
    
    fo_cnsptn_details = pd.DataFrame.from_dict(s['table1'])
    fo_cnsptn_details = fo_cnsptn_details[['index','Fuel(HS)', 'Fuel (LS)', 'Fuel (MDO)', 'Fuel (MGO)' ]]
    reported_data = pd.DataFrame.from_dict(s['reported_data'])

    reported_data= reported_data[["index","Value"]]
    voy_condtn = pd.DataFrame.from_dict(s['pie_chart'])
    Char_data = pd.DataFrame.from_dict(s['EECHARTDATA'])

    fo_cnsptn_details_object =fo_cnsptn_details.astype(str)

    reported_data_object =reported_data.astype(str)


    voy_condtn["voyage_no"] = pd.to_numeric(voy_condtn["voyage_no"], errors='coerce', downcast='integer')
    color =  [ '#0066CC',"#AC2EB5","#663300","#F1F50C"]

    max_info = voy_condtn.groupby('voy_condition')['voyage_no'].max().reset_index()

    info = ""
    for index, row in max_info.iterrows():
        info += f"The voyage condition of {row['voyage_no']}: {row['voy_condition']}\n"


    fo_cnsptn_details_head = [['Fuel Consumption Details','Fuel(HS)', 'Fuel (LS)', 'Fuel (MDO)', 'Fuel (MGO)' ]]
    fo_cnsptn_details_values = fo_cnsptn_details_head+fo_cnsptn_details_object.values.tolist()

    reported_data_head = [["Parameter","Value"]]
    reported_data_values = reported_data_head+reported_data_object.values.tolist()


    fig_voy1 = go.Figure()


    fig_voy1.add_trace(go.Bar(
        x=Char_data['date'],
        y=Char_data['eeoi'],
        marker_color='#EB222D',
        text=Char_data['eeoi'],  # Use actual values for data labels
        texttemplate='%{text:.2f}',  # Format the data labels
        textposition='outside'
    ))

    # Customize the layout
    layout = go.Layout(
        xaxis=dict(
            title='Date',
            #tickfont=dict(size=14, family='Times New Roman'),
            showgrid=False  # Correct syntax for showgrid
        ),
        yaxis=dict(
            title='Energy Efficiency (grams/TEU-mile)',
            #tickfont=dict(size=14, family='Times New Roman'),
            showgrid=False  # Correct syntax for showgrid
        ),
        #font=dict(family="Roboto, sans-serif", size=15, color="black"),
        showlegend=False,  # Assuming you don't want a legend
        width=700,
        height=600
    )

    fig_voy1.update_layout(layout)# Show the plot
    #fig_voy1.show()
    plot_div2 = pyo.plot(fig_voy1, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    fig_voy2 = go.Figure()

    fig_voy2.add_trace(go.Bar(
        x=Char_data['date'],
        y=Char_data['eeoit'],
        marker_color='#EB222D',
        text=Char_data['eeoit'],  # Display text on the bars
        textposition='outside',  # Display text outside the bars
    ))

    layout = go.Layout(
        xaxis=dict(
            title='Date',
            tickfont=dict(size=14, family='Times New Roman'),
            showgrid=False  # Correct syntax for showgrid
        ),
        yaxis=dict(
            title='EEEOIT (grams/TEU-mile)',
            tickfont=dict(size=14, family='Times New Roman'),
            showgrid=False  # Correct syntax for showgrid
        ),
        #font=dict(family="Roboto, sans-serif", size=15, color="black"),
        showlegend=False,  # Assuming you don't want a legend
        width=700,
        height=600
    )

    fig_voy2.update_layout(layout)

    #fig_voy2.show()
    plot_div3 = pyo.plot(fig_voy2, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    fig_voy3 = go.Figure()

    fig_voy3.add_trace(go.Bar(
        x=Char_data['date'],
        y=Char_data['total_co_2'],
        marker_color='#EF521D',
        text=Char_data['total_co_2'],  # Display text on the bars
        textposition='outside',  # Display text outside the bars
    ))

    layout = go.Layout(
        xaxis=dict(
            title="Date",
            tickfont=dict(size=14, family='Times New Roman'),
            showgrid=False  # Correct syntax for showgrid
        ),
        yaxis=dict(
            title='CO2 (tonnes)',
            tickfont=dict(size=14, family='Times New Roman'),
            showgrid=False  # Correct syntax for showgrid
        ),
        #font=dict(family="Roboto, sans-serif", size=15, color="black"),
        showlegend=False,  # Assuming you don't want a legend
        width=700,
        height=600
    )

    fig_voy3.update_layout(layout)

    # Show the plot
    
    plot_div4 = pyo.plot(fig_voy3, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    fig_voy4 = go.Figure()

    fig_voy4.add_trace(go.Bar(
        x=Char_data['date'],
        y=Char_data['foc'],
        marker_color='#EF8717',
        text=Char_data['foc'],  # Use actual values for data labels
        texttemplate='%{text:.2f}',  # Format the data labels
        textposition='outside'
    ))

    # Customize the layout
    layout = go.Layout(
        xaxis=dict(
            title="Date",
            tickfont=dict(size=14, family='Times New Roman'),
            showgrid=False  # Correct syntax for showgrid
        ),
        yaxis=dict(
            title='FO (tonnes)',
            tickfont=dict(size=14, family='Times New Roman'),
            showgrid=False  # Correct syntax for showgrid
        ),
        #font=dict(family="Roboto, sans-serif", size=15, color="black"),
        showlegend=False,  # Assuming you don't want a legend
        width=700,
        height=600
    )

    fig_voy4.update_layout(layout)

    # Show the plot
    fig_voy4.show()

    # If you still want the Plotly div output
    plot_div5 = pyo.plot(fig_voy4, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})



    html_table = "<table border='1'>\n"
    # Create table header
    html_table += "<tr>"
    for col in fo_cnsptn_details_values[0]:
        html_table += f"<th>{col}</th>"
    html_table += "</tr>\n"

    # Iterate over rows
    for row in fo_cnsptn_details_values[1:]:
        html_table += "<tr>"
        for value in row:
            html_table += f"<td>{value}</td>"
        html_table += "</tr>\n"

    html_table += "</table>"



    html_table2 = "<table border='1'>\n"
    # Create table header
    html_table2 += "<tr>"
    for col in reported_data_values[0]:
        html_table2 += f"<th>{col}</th>"
    html_table2 += "</tr>\n"

    # Iterate over rows
    for row in reported_data_values[1:]:
        html_table2 += "<tr>"
        for value in row:
            html_table2 += f"<td>{value}</td>"
        html_table2 += "</tr>\n"

    html_table2 += "</table>"

    html_content = f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Voyage Wise Report</title>
        <style>
        body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            
            h1 {{
                color: #193185;
                font-size: 36px;
                margin-bottom: 20px;
            }}

            h2 {{
                color: #193185;
                font-size: 30px; 
            }}
            
            h3 {{
                color: #333;
                font-size: 30px; 
            }}
            

            img {{
                width: 100px; /* Make the image larger */
                float: right;
            }}

            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 16px; /* Increase font size for the information */
                font-weight: bold;
            }}


            .second-info {{
                margin-left: 100px;
            }}
            
            table {{
                margin: 20px auto;
                    width: 70%;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            
                table, tr, td {{height: 30px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%;
                        display: flex;
                        justify-content: center;
            }}

            hr {{
                border-width: 2px;
                border-color: #33;
                margin-top: 20px;
                border-style: solid; /* Add border style */
            }}
            
            th {{
                background: blue;
                color: white;
                height: 41px;
            }}
        </style>
    </head>

    <body>
        <br>
            <br>
                    {image_tag}

        <br>
        <br>
        <br>
        <br>
        <br>
        <h1>VOYAGE WISE REPORT</h1>
        <hr>
        <!-- Add information in HTML format -->
        <div class="info">
            <div class='first-info'>
                <p style="font-size: 18px;">VESSEL NAME:{vessel_name}</p>
                <p style="font-size: 18px;">DATE RANGE: {date_start} TO {date_end}</p>
                <p style="font-size: 18px;">VOYAGE CODE: {vcode}</p>
                <p style="font-size: 18px;">PASSAGE ID: {pid}</p>
            </div>
        </div>
        <hr>
        <h2>Voyage Condition</h2>
        <div class='second-info'>
                <h3>{info}</h3>
        </div>
        <h2>Fuel Consumption Details</h2>
        <br>
        {html_table}
        <br>
        {html_table2}
        <br>
        <h2>Date vs EEOI (grams/tonne-mile)</h2>
        <div class="plot_div">
        {plot_div2}
        </div>
        <br>
        <br>
        <h2>Date vs EEOI (gm/TEU-mile)</h2>
        <div class="plot_div">
        {plot_div3}
        </div>
        <br>
        <h2>Date vs CO2 Emission</h2>
        <div class="plot_div">
        {plot_div4}
        </div>
        <br>
        <h2>Date vs FO Consumption</h2>
        <div class="plot_div">
        {plot_div5}
        </div>
        <br>
        <br>
    </body>

    </html>
    """

    
    file_name = 'voyage_report'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)

@router.post('/api/v1/html/slipreport_class_fleet/{mode}')
async def index(info:Request, chart_type:str =None,prop_type:str = None , mode:str = None,start_date:str = None , end_date:str = None):
    slip_data = await info.json()
    
    slip_chart = pd.DataFrame.from_dict(slip_data['data']["slipReportChartData"]['chartData1'])
    slip_chart = slip_chart.drop_duplicates(keep='first')
    print("chart_type",chart_type)

    if chart_type == 'class':
        slip_chart = pd.DataFrame.from_dict(slip_data['data']["slipReportChartData"]['chartData1'])
        slip_chart = slip_chart.drop_duplicates(keep='first')

        if prop_type == "All":
            slip_chart1 = slip_chart
        elif prop_type == "CPP":
            slip_chart1 = slip_chart[slip_chart["prop_type"] == "CPP"]
        elif prop_type == "FPP":   
            slip_chart1 = slip_chart[slip_chart["prop_type"] == "FPP"]
        else:
            pass
        
        slip_chart_1 = slip_chart1.pivot(index="vessel_name", columns="type", values="value").reset_index()
        slip_chart_1_data = slip_chart_1.melt(id_vars='vessel_name', var_name='type', value_name='value')

        fig1 = go.Figure()
        for vessel, group in slip_chart_1_data.groupby('type'):
            fig1.add_trace(go.Bar(x=group['vessel_name'], y=group['value'], name=vessel, text=group['value'], textposition='outside', textfont=dict(size=16)))

        fig1.update_layout(
            xaxis=dict(title='Vessel', tickangle=-45),
            yaxis=dict(title='% Slip'),
            legend=dict(title=None, orientation='h', x=0.1, y=1.1),
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            width=1000,
            height=700,
            #title='Slip report'
        )

        #fig1.show()
        plot_div = pyo.plot(fig1, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    else:
        slip_chart2 = pd.DataFrame.from_dict(slip_data['data']["slipReportChartData"]['chartData1'])
        slip_chart2 = slip_chart2.drop_duplicates(keep='first')
        
        if prop_type == "All":
            slip_chart2a = slip_chart2
        elif prop_type == "CPP":
            slip_chart2a = slip_chart2[slip_chart2["prop_type"] == "CPP"]
        elif prop_type == "FPP":   
            slip_chart2a = slip_chart2[slip_chart2["prop_type"] == "FPP"]
        else:
            pass
        
        slip_chart_2 = slip_chart2a.pivot(index="vessel_name", columns="type", values="value").reset_index()
        slip_chart_2_data = slip_chart_2.melt(id_vars='vessel_name', var_name='type', value_name='value')

        fig2 = go.Figure()
        for vessel, group in slip_chart_2_data.groupby('type'):
            fig2.add_trace(go.Bar(x=group['vessel_name'], y=group['value'], name=vessel, text=group['value'], textposition='outside', textfont=dict(size=16)))

        fig2.update_layout(
            xaxis=dict(title='Vessel', tickangle=-45),
            yaxis=dict(title='% Deviation'),
            legend=dict(title=None, orientation='h', x=0.1, y=1.1),
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            width=1000,
            height=700,
            #title='Slip report'
        )

        #fig2.show()
        plot_div = pyo.plot(fig2, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    print("/api/v1/html/slipreport_class_fleet/",mode)
    html_content = f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Slip Report</title>
        <style>
        body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            
            h1 {{
                color: #193185;
                font-size: 36px;
                margin-bottom: 20px;
            }}

            h2 {{
            color: #193185;
            font-size: 30px;
            text-align: center;

            }}

            img {{
                width: 200px; /* Make the image larger */
                float: right;
            }}

            .info {{
                text-align: left;
                margin-left: 20px;
                font-size: 16px; /* Increase font size for the information */
                font-weight: bold
            }}

            
            .plot_div {{
                width: 70%; /* Increase width of the plot_div */
                display: flex;
                justify-content: center;
                align-items: center;
                margin: auto; /* Center the plot_div */
            }}


            hr {{
                border-width: 3px;
                border-color: #33;
                margin-top: 25px;
                border-style: solid; /* Add border style */
            }}
            
            th {{
                background: blue;
                color: white;
                height: 41px;
            }}
        </style>
    </head>

    <body>
        <br>
            <br>
        {image_tag}
        <br>
        <br>
        <br>
        <h1>Slip Report</h1>
        <hr>
        <!-- Add information in HTML format --> 
        <div class="info">
            <div class="info">
        {"<p>Class: " + mode + "</p>" if chart_type == "class" else "<p>Fleet: " + mode + "</p>" if chart_type == "fleet" else ""}
        <p>Monitoring Period: {start_date} to {end_date}</p>
    </div>
        <hr>
        <br>    
        
        <div class="plot_div">
            {plot_div}
        </div>
        <div class="plot_div">
            {plot_div}
        </div>
        <br>
        <br>
        <br>
    </body>

    </html>
    """
    file_name = 'slip_report_class'+mode+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)

@router.post('/api/v1/html/slipreport/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None , parameter:str = None,graph_type:str = None , report_type:str = None ,date:str = None,min_date:str=None,max_date:str = None,data:str = None):
    slip_data_ada = await info.json()
    
    input_para_slip = {
    "Parameter": [parameter],
    "Graph_Type": [graph_type],
    "Data": [data],
    "Vessel_name": [vessel_name],
    "Report_Type": [report_type] 
    }

    input_data = pd.DataFrame.from_dict(input_para_slip)


    # Slip_data = pd.DataFrame.from_dict(
        # slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["data"])
    print("======================================================================")
    print(data)
    print("======================================================================")
    
    if data == "VRS Data":
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
    
        # #######pdf values#####
        slip_vessel_meta_data = pd.DataFrame.from_dict(
            slip_data_ada["data"]["metadata"][input_data["Parameter"].item()])
        benchmark_avg_slip = str(slip_vessel_meta_data["average_slip"].values[0])
        benchmark_period = slip_vessel_meta_data["selection_period"].values[0]
        benchmark_keydate = slip_vessel_meta_data["key_dates"].values[0]
        prop_pitch = str(slip_vessel_meta_data["propeller_pitch"].values[0])
        ##############################
        Slip_data_vrs = pd.DataFrame.from_dict(
            slip_data_ada["data"]["chartData"][input_data["Parameter"].item()][input_data["Report_Type"].item()]["data"])
        if input_data["Report_Type"].item() == "daily":
            Slip_data["date"] = pd.to_datetime(Slip_data["date"], format='%d %b %Y')
            Slip_data['date'] = Slip_data['date'].dt.strftime('%d-%m-%Y')
        elif input_data["Report_Type"].item() == "monthly":
            pass
    
        fig = go.Figure()
    
        # Add scatter or line trace depending on 'Graph_Type'
        graph_type = input_data["Graph_Type"].item()
        if graph_type == "Line":
            fig.add_trace(go.Scatter(x=Slip_data['date'], y=Slip_data['value'],
                                    mode='lines+markers',
                                    marker=dict(color='brown'),
                                    name=Slip_data["type"].values[0]))
        elif graph_type == "Scatter":
            fig.add_trace(go.Scatter(x=Slip_data['date'], y=Slip_data['value'],
                                    mode='markers',
                                    marker=dict(color='brown'),
                                    name=Slip_data["type"].values[0]))
    
        # Add horizontal lines for benchmark and hydraulic slip
        y_value1_vrs = slip_vessel_anno_vrs["benchmark"].values[0]
        y1_vrs = slip_vessel_anno_vrs["hyd_slip"].values[0]
    
        fig.add_hline(y=y_value1_vrs, line=dict(color='yellow', width=2), name='Average Benchmark Slip')
        fig.add_hline(y=y1_vrs, line=dict(color='green', width=2, dash='dash'), name='Fitted Hydraulic Slip')
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='yellow', width=2), name='Average Benchmark Slip'))
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='green', width=2, dash='dash'), name='Fitted Hydraulic Slip'))
    
        # Update layout
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='% Slip',
            width=1000,
            height=700,
            yaxis=dict(range=[0, 100], tickmode='array', tickvals=list(range(0, 101, 10))),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
    
        # Save the figure using Plotly's built-in function
        #fig.write_image('slip_report_vessel.png', width=800, height=600)
        # fig.show()
        
        plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            
    elif data== 'EGOSHIP Data':
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
        benchmark_avg_slip = str(slip_vessel_meta_data["average_slip"].values[0])
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
    
    
        fig = go.Figure()
    
        # Add scatter or line trace depending on 'Graph_Type'
        graph_type = input_data["Graph_Type"].item()
        if graph_type == "Line":
            fig.add_trace(go.Scatter(x=Slip_data['date'], y=Slip_data['value'],
                                    mode='lines+markers',
                                    marker=dict(color='brown'),
                                    name=Slip_data["type"].values[0]))
        elif graph_type == "Scatter":
            fig.add_trace(go.Scatter(x=Slip_data['date'], y=Slip_data['value'],
                                    mode='markers',
                                    marker=dict(color='brown'),
                                    name=Slip_data["type"].values[0]))
    
        # Add horizontal lines for benchmark and hydraulic slip
        y_value1_ego = slip_vessel_anno_ego["benchmark"].values[0]
        y1_ego = slip_vessel_anno_ego["hyd_slip"].values[0]
    
        fig.add_hline(y=y_value1_ego, line=dict(color='yellow', width=2), name='Average Benchmark Slip')
        fig.add_hline(y=y1_ego, line=dict(color='green', width=2, dash='dash'), name='Fitted Hydraulic Slip')
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='yellow', width=2), name='Average Benchmark Slip'))
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='green', width=2, dash='dash'), name='Fitted Hydraulic Slip'))
    
        # Update layout
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='% Slip',
            yaxis=dict(range=[0, 100], tickmode='array', tickvals=list(range(0, 101, 10))),
            width=1000,
            height=700,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
    
        # Update x-axis tick angle
        fig.update_xaxes(tickangle=-45)
    
        # Save the figure
        # fig.write_image('slip_report_vessel.png')
        
        plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
    
        daily_avg_slip_vrs = ''
    elif data == 'data_comparison':
        selected_period_deviation_vrs = str(
            slip_data_ada["data"]["VRS DATA"]["chartData"][input_data["Parameter"][0]][input_data["Report_Type"][0]]["metadata"]
        )
        Slip_data_vrs = pd.DataFrame.from_dict(
            slip_data_ada["data"]['VRS DATA']["chartData"][input_data["Parameter"][0]][input_data["Report_Type"][0]]["data"]
        )
        slip_vessel_anno_vrs = pd.DataFrame.from_dict(
            slip_data_ada["data"]['VRS DATA']["chartData"][input_data["Parameter"][0]][input_data["Report_Type"][0]]["annotation"]
        )
        daily_avg_slip_vrs = str(slip_vessel_anno_vrs["average_hydro_slip"].values[0])
        y1_vrs = slip_vessel_anno_vrs["hyd_slip"].values[0]
        y2_vrs = slip_vessel_anno_vrs["hyd_slip"].values[1]

        try:
            Slip_data_ego = pd.DataFrame.from_dict(
                slip_data_ada["data"]["EGOSHIP DATA"]["chartData"][input_data["Parameter"][0]][input_data["Report_Type"][0]]["data"]
            )
            selected_period_deviation_ego = str(
                slip_data_ada["data"]["EGOSHIP DATA"]["chartData"][input_data["Parameter"][0]][input_data["Report_Type"][0]]["metadata"]
            )
            slip_vessel_anno_ego = pd.DataFrame.from_dict(
                slip_data_ada["data"]["EGOSHIP DATA"]["chartData"][input_data["Parameter"][0]][input_data["Report_Type"][0]]["annotation"]
            )
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
            slip_data_ada["data"]["metadata"][input_data["Parameter"][0]]
        )
        benchmark_avg_slip_vrs = str(slip_vessel_meta_data["average_slip"].values[0])
        benchmark_avg_slip_ada = str(slip_vessel_meta_data["average_slip_ada"].values[0])
        benchmark_period = slip_vessel_meta_data["selection_period"].values[0]
        benchmark_keydate = slip_vessel_meta_data["key_dates"].values[0]
        prop_pitch = str(slip_vessel_meta_data["propeller_pitch"].values[0])

        # Convert date columns to datetime
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

        # Create Plotly figure
        fig = go.Figure()

        # Plot VRS data
        fig.add_trace(go.Scatter(x=Slip_data_vrs['date'], y=Slip_data_vrs['value'],
                                mode='lines+markers',
                                name="Hydrodynamic Slip (VRS)",
                                line=dict(color='green'),
                                marker=dict(color='green')))

        # Plot ADA data if available
        if ego_ship == "Yes" and not Slip_data_ego.empty:
            fig.add_trace(go.Scatter(x=Slip_data_ego['date'], y=Slip_data_ego['value'],
                                    mode='lines+markers',
                                    name="Hydrodynamic Slip (ADA)",
                                    line=dict(color='red'),
                                    marker=dict(color='red')))

        # Plot Average Benchmark Slip for VRS data
        fig.add_trace(go.Scatter(x=[Slip_data_vrs['date'].min(), Slip_data_vrs['date'].max()],
                                y=[slip_vessel_anno_vrs["benchmark"].values[0]] * 2,
                                mode='lines',
                                name='Average Benchmark Slip (VRS)',
                                line=dict(color='green', dash='solid')))

        # Plot Average Benchmark Slip for ADA data if available
        if ego_ship == "Yes" and not slip_vessel_anno_ego.empty:
            fig.add_trace(go.Scatter(x=[Slip_data_ego['date'].min(), Slip_data_ego['date'].max()],
                                    y=[slip_vessel_anno_ego["benchmark"].values[0]] * 2,
                                    mode='lines',
                                    name='Average Benchmark Slip (ADA)',
                                    line=dict(color='red', dash='solid')))

        # Plot Fitted Hydraulic Slip for VRS data
        fig.add_trace(go.Scatter(x=[Slip_data_vrs['date'].min(), Slip_data_vrs['date'].max()],
                                y=[y1_vrs, y2_vrs],
                                mode='lines',
                                name='Fitted Hydraulic Slip (VRS)',
                                line=dict(color='green', dash='dash')))

        # Plot Fitted Hydraulic Slip for ADA data if available
        if ego_ship == "Yes" and not slip_vessel_anno_ego.empty:
            fig.add_trace(go.Scatter(x=[Slip_data_ego['date'].min(), Slip_data_ego['date'].max()],
                                    y=[y1_ego, y2_ego],
                                    mode='lines',
                                    name='Fitted Hydraulic Slip (ADA)',
                                    line=dict(color='red', dash='dash')))

            
        
        # Update layout
        fig.update_layout(
        xaxis_title='Date',
        yaxis_title='% Slip',
        xaxis=dict(
            tickformat='%b %Y' if report_type != 'daily' else '%d %b %Y',  # Conditional formatting based on report type
            tickangle=-45,
            title_font=dict(size=14),
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        legend=dict(
            x=1,  # Position the legend to the right of the plot
            y=1,
            traceorder='normal',
            orientation='v',
            title_font=dict(size=14),
            font=dict(size=12),
            bordercolor='Black',
            borderwidth=1
        ),
        width=1200,  # Width of the plot
        height=800   # Height of the plot
    )
        #fig.show()
        #fig.write_image('slip_report_vessel.png', width=800, height=600)
        plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            

   
    html_content = f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Slip Report</title>
        <style>
        body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            
            h1 {{
                color: #193185;
                font-size: 36px;
                margin-bottom: 20px;
            }}

            h2 {{
                color: #193185;
                font-size: 30px; 
            }}

            img {{
                width: 200px; /* Make the image larger */
                float: right;
            }}

            .info {{
                text-align: left;
                margin-left: 20px;
                font-size: 16px; /* Increase font size for the information */
                font-weight: bold
            }}

            .first-info {{
                text-align: left;
                margin-left: 20px;
                font-size: 16px; /* Increase font size for the information */
                font-weight: bold
            }}

            .second-info {{
                text-align: left;
                margin-left: 20px;
                font-size: 16px; /* Increase font size for the information */
                font-weight: bold
            }}
            
                .third-info {{
                text-align: left;
                margin-left: 20px;
                font-size: 16px; /* Increase font size for the information */
                font-weight: bold
            }}
            
            .plot_div {{
                width: 70%; /* Increase width of the plot_div */
                display: flex;
                justify-content: center;
                align-items: center;
                margin: auto; /* Center the plot_div */
            }}


            hr {{
                border-width: 3px;
                border-color: #33;
                margin-top: 20px;
                border-style: solid; /* Add border style */
            }}
            
            th {{
                background: blue;
                color: white;
                height: 41px;
            }}
        </style>
    </head>

    <body>
        <br>
            <br>
                    {image_tag}

        <br>
        <br>
        <br>
        <h1>Slip Report</h1>
        <hr>
        <!-- Add information in HTML format -->
        <div class="second-info">
            <p>Vessel Name: {vessel_name}</p>
            <p>Monitoring Period: {min_date} to {max_date}</p>
            <p>Propeller Pitch: {prop_pitch}</p>
        </div>
        <div class="third-info">
            <p>Benchmark keydate: {benchmark_keydate}</p>
            <p>Benchmark Period: {benchmark_period}</p>
            {"<p> Average Benchmark Slip (VRS): "+benchmark_avg_slip_vrs+"</p><p> Average Benchmark Slip (ADA): "+benchmark_avg_slip_ada+ "</p>" if data == 'data_comparison' else "<p> Average Benchmark Slip :" +benchmark_avg_slip+ "</p>"}
        </div>  
        <div class="info">
        {"<p> Deviation for Selected Period (VRS): " + selected_period_deviation_vrs + "</p><p> Deviation for Selected Period (ADA): " + selected_period_deviation_ego + "</p>" if data == 'data_comparison' else
        "<p> Deviation for Selected Period: " + selected_period_deviation_vrs + "</p>" if data == "VRS Data" else
        "<p> Deviation for Selected Period: " + selected_period_deviation_ego + "</p>"}
        {"<p> Daily Average Hydrodynamic Slip(VRS): " + daily_avg_slip_vrs + "</p><p> Daily Average Hydrodynamic Slip(ADA): " + daily_avg_slip_ego + "</p>" if data == 'data_comparison' else
        "<p> Daily Average Hydrodynamic Slip(VRS)" + daily_avg_slip_vrs + "</p>" if data == "VRS Data" else
        "<p> Daily Average Hydrodynamic Slip(ADA)" + daily_avg_slip_ego + "</p>"}
        </div>
        <hr>
        <br>
        <h2>Slip Report</h2>
        <div class="plot_div">
            {plot_div}
        </div>
        <br>
        <br>
        <br>
    </body>

    </html>
    """
    
    
    file_name = 'slip_report'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)



@router.post('/api/v1/html/sox/{imo}')
async def index(info:Request, imo:str =None,vessel_name:str = None , tabname:str = None,types:str = None , selection:str = None ,method:str = None,year:str=None,start_date:str = None,end_date:str = None,fleet:str=None):
    s = await info.json()

    
    from datetime import datetime
    if year  is None  or year == 'null' : 
        start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d %b %Y')
        end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d %b %Y')
        period=start_date+ " TO " +end_date
    else:
        period=year

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

    print("=================",s['data'])
    print("================33333333333333333333333333=",s['data']['ae_me'])
    
    print("s['data']['ae_me']['daily_data']",s['data']['ae_me']['daily_data'])
    data1 = pd.DataFrame.from_dict(s['data']['ae_me']['daily_data'])
    data1 = data1.replace([0], np.nan)
    pivoted_data1 = data1.pivot(index='date_month',columns='category',values='ae_sox_value').reset_index()
    lst = data1['date_month'].unique().tolist()
    pivoted_data1 = pivoted_data1.set_index('date_month')
    pivoted_data1 = pivoted_data1.loc[lst]   
    pivoted_data1 = pivoted_data1.reset_index()

    fig = go.Figure()

    for column in pivoted_data1.columns[1:]:
        fig.add_trace(go.Bar(
            x=pivoted_data1['date_month'],
            y=pivoted_data1[column],
            name=column
        ))

    fig.update_layout(
 
        xaxis=dict(title='Date', tickangle=-45, tickfont=dict(size=14), titlefont=dict(size=18)),
        yaxis=dict(title='Total SOx Daily (MT)', titlefont=dict(size=18)),
        barmode='stack',
        width=1500,
        height=600)
    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    data2 = pd.DataFrame.from_dict(s['data']['ae_me']['monthly_data'])
    data2 = data2.replace([0], np.nan)
    pivoted_data2 = data2.pivot(index='date_month',columns='category',values='ae_sox_value').reset_index()
    pivoted_data2['Month'] = pd.to_datetime(pivoted_data2['date_month'], format='%Y-%B')

    pivoted_data2 = pivoted_data2.sort_values('Month')

    pivoted_data2 = pivoted_data2.drop(['Month'],axis=1)

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    fig = go.Figure()

    for column in pivoted_data2.columns[1:]:
        fig.add_trace(go.Bar(
            x=pivoted_data2['date_month'],
            y=pivoted_data2[column],
            name=column
        ))

    fig.update_layout(
   
        xaxis=dict(title='Date', tickangle=-45, tickfont=dict(size=14), titlefont=dict(size=16)),
        yaxis=dict(title='Total SOx Monthly (MT)', titlefont=dict(size=16)),
        barmode='stack',
        width=1000,
        height=500
    )

    plot_div2 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    data3 = pd.DataFrame.from_dict(s['data']['ae_me']['daily_sox'])
    data3 = data3.replace([0], np.nan)
    pivoted_data3 = data3.pivot(index='date_month',columns='category',values='ae_sox_value').reset_index()
    lst = data3['date_month'].unique().tolist()
    pivoted_data3 = pivoted_data3.set_index('date_month')
    pivoted_data3 = pivoted_data3.loc[lst]   
    pivoted_data3 = pivoted_data3.reset_index()

    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"

    fig = go.Figure()

    for column in pivoted_data3.columns[1:]:
        fig.add_trace(go.Bar(
            x=pivoted_data3['date_month'],
            y=pivoted_data3[column],
            name=column
        ))

    fig.update_layout(
 
        xaxis=dict(title='Date', tickangle=-45, tickfont=dict(size=14), titlefont=dict(size=16)),
        yaxis=dict(title='Total SOx Daily (MT)', titlefont=dict(size=16)),
        barmode='stack',
        width=1500,
        height=600
    )

    plot_div3 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


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
    fig = go.Figure()

    for column in pivoted_data4.columns[1:]:
        fig.add_trace(go.Bar(
            x=pivoted_data4['date_month'],
            y=pivoted_data4[column],
            name=column
        ))

    fig.update_layout(
     
        xaxis=dict(title='Date', tickangle=-45, tickfont=dict(size=14), titlefont=dict(size=16)),
        yaxis=dict(title='Total SOx Monthly (MT)', titlefont=dict(size=16)),
        barmode='stack',
        width=1000,
        height=500
    )

    plot_div4 = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

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


    html_table1 ="<table border='1'>\n"
    # Create table header
    html_table1 += "<tr>"
    for col in df_main.columns:
        html_table1 += f"<th>{col}</th>"
    html_table1 += "</tr>\n"

    # Iterate over rows
    for index, row in df_main.iterrows():
        html_table1 += "<tr>"
        for value in row:
            html_table1 += f"<td>{value}</td>"
        html_table1 += "</tr>\n"

    html_table1 += "</table>"


    html_table2 ="<table border='1'>\n"
    # Create table header
    html_table2 += "<tr>"
    for col in df_fuel_types.columns:
        html_table2 += f"<th>{col}</th>"
    html_table2 += "</tr>\n"

    # Iterate over rows
    for index, row in df_fuel_types.iterrows():
        html_table2 += "<tr>"
        for value in row:
            html_table2 += f"<td>{value}</td>"
        html_table2 += "</tr>\n"

    html_table2 += "</table>"






    # Start building the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SOx</title>
        <style>
            body {{
                text-align: center;
            }}
            h1 {{
                color: #193185;
            }}
            h2 {{
                color: #193185;
            }}
            img {{
                width: 80px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
            }}
            .second-info{{ margin-left: 100px;}}
                table {{
                    margin: 20px auto;
                        width: 1300px;
                        border-collapse: collapse;
                        border: solid;

                }}
        

                    table, tr, td {{height: 34px;
                        border: 1px solid;
                    }}
                    th{{
                        background: blue;
                        color: white;
                    }}
            .plot_div {{
                width: 100%;
                justify-content: center;
            }}
            hr {{
                border-width: 3px;
            }}
            .center{{
                width: 100%;
                display: flex;
                flex-direction: column;
                text-align: center;
            }}
            
            .chart{{
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
            }}
        </style>
    </head>
    <body>
        
        <h1>SOx Report</h1>
        <br>
        <br>
        <hr>
        <div class='info'>
            {"<p>Vessel: " + vessel_name + "</p>" if tabname == 'Vessel' else
            "<p>Fleet: " + fleet + "</p>" if tabname == 'Fleet' else
            "<p>Type: " + types + "</p>" if tabname == 'All' else ""}
            <p>Monitoring period : {period}</p>
            <p>Method : {method}</p>
        </div>
        <hr>
        <div class='center'>
            <div class='chart'>
                <h2>Daily SOx</h2>
                {plot_div}
            </div>
            <br>
            <br>
            <br>
            <br>
            
            <div class='chart' >
                <h2>Monthly SOx</h2>
                {plot_div2}
            </div>
            <br>
            <br>
            <br>
            <br>
            
            <div class='chart' >
                <h2>Fuel Type Daily SOx</h2>
                {plot_div3}
            </div>
            <br>
            <br>
            <br>
            <br>
            
            <div class='chart' >
                <h2>Fuel Type Monthly SOx</h2>
                {plot_div4}
            </div>
            <br>
            <br>
            <br>
            <br>
        </div>
        
        <br>
        <br>
   
        <br>
        <br>
        <h2>SOx Data Table</h2>
        {html_table1}
        {html_table2}
        
    </body>
    </html>
    """

    file_name = 'sox_'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)


# -----------------------------------------EEXI-------------------------------------------------------------------------------



@router.post('/api/v1/html/eexi_report_html/{imo}')
async def index(info:Request,imo:str=None,vessel_name:str =None,type:str =None,deadweight:str=None):
    s = await info.json()
    DWT=deadweight
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
    
    mydict = dict(zip(df4['name'], df4['value_unit']))
    def get_main_engine_data(mydict,r, general_info):
        # Initialize dictionaries to store data
        generaldata = {}
        vesseldata = {}
        medata = {}
        aedata = {}


    mydict = dict(zip(zip(df4['name'], df4['attribute_id']), df4['value_unit']))


    def create_info_dataframe(attributeList, df4, mydict):
        selected_data = {}
        attribute_names = [key[0] for key in mydict.keys() if isinstance(key, (list, tuple)) and key]  # Check if key is a list or tuple and not empty

        for attribute_id in attributeList:
            if attribute_id in df4['attribute_id'].values:
                attribute_name = df4[df4['attribute_id'] == attribute_id]['name'].iloc[0]
                if attribute_name in attribute_names:
                    value_unit = mydict[(attribute_name, attribute_id)]
                    selected_data[attribute_name] = value_unit

        info_df = pd.DataFrame(selected_data.items(), columns=['Particulars', 'Details'])
        return info_df

    # General Info DataFrame
    attributeList_general = [65, 1, 168, 62, 4]
    General_info = create_info_dataframe(attributeList_general, df4, mydict)
    General_info

    # Vessel Info DataFrame
    attributeList_vessel = [14, 15, 16, 18, 83, 8]
    Principal_particulars = create_info_dataframe(attributeList_vessel, df4, mydict)
    Principal_particulars

    # Main Engine DataFrame
    attribute_lst_ae = 542
    me_count = df4.loc[df4['attribute_id'] == 334, 'value'].values[0]
    if len(me_count) > 0 and me_count[0] != '':
        me_count = int(me_count[0])
    else:
        me_count = 0  # or any other default value you consider appropriate

    if me_count > 1:
        attributeList_me = [147, 916, 915, 914, 333, 917, 918, 919, 149, 926, 927, 928, 576, 929, 930, 931, 721, 959, 960, 961]
    else:
        attributeList_me = [147, 333, 149, 721, 576]

    ME = create_info_dataframe(attributeList_me, df4, mydict)


    # Auxiliary Engine DataFrame
    attribute_lst_ae = 542
    ae_count = df4.loc[df4['attribute_id'] == 542, 'value'].values[0]
    if len(ae_count) > 0 and ae_count[0] != '':
        ae_count = int(ae_count[0])
    else:
        ae_count = 0  # or any other default value you consider appropriate
    if ae_count > 1:# Assuming this is the list containing attribute IDs related to AE count
        attributeList_ae = [153, 185, 188, 723, 724 ,201, 203,206,725,726,279, 282, 285, 727, 728,369,370,373,729,730,375,376,379,731,732]
    else:
        attributeList_ae = [153, 185, 188, 723, 724]

    AE = create_info_dataframe(attributeList_ae, df4, mydict)

    selected_attributes = ['required_eexi', 'attained_eexi', 'Maximum Speed']
    selected_data = {}

    for attribute in selected_attributes:
        if attribute in graph_data:
            selected_data[attribute] = graph_data[attribute]

    # DataFrame from the selected EEXI data
    df = pd.DataFrame([selected_data]).transpose().reset_index()
    df.columns = ['Particulars', 'Details']

    # Additional processing for ship speed data (if available)
    selected_attributes = ['Maximum Speed']
    selected_data = {}

    for i in  attributes_data:

        if i['name'] in selected_attributes:
            filtered_values = list(filter(lambda x: x['attribute_id'] == i['id'], general_info))
            if filtered_values:
                value = filtered_values[0]['value']
                unit = i['unit']
                selected_data[i['name']] = f"{value} {unit}"

    ss = pd.DataFrame(selected_data.items(), columns=['Particulars', 'Details'])

    # Combine both dataframes
    combined_df = pd.concat([df, ss], ignore_index=True)
    combined_df


    # Define 'Particulars' for required, attained EEXI and ship speed
    combined_df['Particulars'][0] = 'Required EEXI'
    combined_df['Particulars'][1] = 'Attained EEXI'
    combined_df['Particulars'][2] = 'Ship Speed'

    # Calculate EEXI Result
    required_eexi = combined_df.loc[combined_df['Particulars'] == 'Required EEXI', 'Details'].iloc[0]
    attained_eexi = combined_df.loc[combined_df['Particulars'] == 'Attained EEXI', 'Details'].iloc[0]
    if attained_eexi != None and required_eexi != None :
        eexi_result = 'PASS' if attained_eexi <= required_eexi else 'FAIL'
    else:
        eexi_result = None

    new_row = pd.DataFrame({'Particulars': ['EEXI Result'], 'Details': [eexi_result]})

    # Concatenate the original DataFrame with the new DataFrame
    combined_df = pd.concat([combined_df, new_row], ignore_index=True)
    combined_df


    #return General_info, Principal_particulars, ME, AE, combined_df
    #General_info, Principal_particulars, ME, AE, combined_df = create_info_dataframe(mydict,graph_data,general_info)

    required_eexi= s['data']['graphData']['required_eexi']
    attained_eexi= s['data']['graphData']['attained_eexi']
    d=pd.DataFrame.from_dict(s['data']['graphData']['graph_data'])

    required_values = combined_df.loc[combined_df['Particulars'] == 'Required EEXI', 'Details'].values[0]
    attained_values = combined_df.loc[combined_df['Particulars'] == 'Attained EEXI', 'Details'].values[0]


    # fig = go.Figure()

        

    # annotations = [
    #     dict(
    #         x=DWT,
    #         y=attained_values,
    #         xref="x",
    #         yref="y",
    #         text=f'Required EEXI: {required_values}<br>Attained EEXI: {attained_values}',
    #         showarrow=False,
    #         font=dict(size=12, color='black'),
    #         xshift=-20,
    #         yshift=10
    #     )
    # # ]
    y_min = min(d["value"]) - 1  # Adding a bit of padding
    y_max = max(d["value"]) + 1  # Adding a bit of padding

    d=d.dropna()

    # Convert year and value to numeric
    d["year"] = pd.to_numeric(d["year"], errors='coerce')
    d["value"] = pd.to_numeric(d["value"], errors='coerce')

    # Define DWT and values for spike exclusion
    DWT = int(deadweight)  # Replace with your DWT value
    value_to_exclude = required_eexi

    # Filter the DataFrame to exclude the spike point
    d_filtered = d[~((d["year"] == DWT) & (d["value"] == value_to_exclude))]

    fig = go.Figure()

    # Adding the attained EEXI marker
    fig.add_trace(go.Scatter(
        x=[DWT],
        y=[attained_eexi],
        mode='markers',
        name='Attained EEXI',
        marker=dict(color='magenta', size=10)
    ))

    # Adding the line trace for Required EEXI values
    fig.add_trace(go.Scatter(
        x=d_filtered["year"],
        y=d_filtered["value"],
        mode='lines',
        line=dict(color='blue', width=2),
        name='Required EEXI Values'
    ))

    # Adding annotations for Attained EEXI and Deadweight
    annotations = [
        dict(
            x=DWT,
            y=attained_eexi,
            xref="x",
            yref="y",
            text=f'Deadweight: {DWT} MT<br>Required EEXI: {required_eexi}<br>Attained EEXI: {attained_eexi}',
            showarrow=False,
            font=dict(size=12, color='black'),
            xshift=-20,
            yshift=10
        )
    ]

    fig.update_layout(
        title="EEXI Comparison",
        xaxis=dict(
            title='Deadweight', 
            titlefont=dict(size=20, color='black'), 
            tickfont=dict(size=14), 
            tickformat=',d',
            range=[0, max(d_filtered["year"]) + 10]  # Ensuring the x-axis starts at 0 and adding a bit of padding to the maximum value
        ),
        yaxis=dict(
            title='EEXI Value (gCO2/Tonne-Nm)', 
            titlefont=dict(size=20, color='black'), 
            tickfont=dict(size=14), 
            range=[y_min, y_max]
        ),
        annotations=annotations,
        height=700,
        width=1000,
    )

    # Show the figure
    fig.show()

    # Show the figure
    # fig.show()

    # # Export plot to HTML div
    # plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    data = s['data']['graphData']['eexi_calc']
    if isinstance(data, dict):
        data = [data]
    eng_details = pd.DataFrame(data)
    eng_details

    mcr_pwr = eng_details['mcrpower'].iloc[0]
    mcr_rpm = eng_details['mcrrpm'].iloc[0]
    new_mcr_pwr = eng_details['newmcrpower'].iloc[0]
    new_mcr_rpm = eng_details['newmcrrpm'].iloc[0]

    mcr_pwr = str(mcr_pwr)
    mcr_rpm = str(mcr_rpm)
    new_mcr_pwr = str(new_mcr_pwr)
    new_mcr_rpm = str(new_mcr_rpm)  

    # fig.show()

    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    html_table = "<table border='1'>\n"
    # Create table header
    html_table += "<tr>"
    for col in General_info.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr>\n"

    # Iterate over rows
    for index, row in General_info.iterrows():
        html_table += "<tr>"
        for value in row:
            html_table += f"<td>{value}</td>"
        html_table += "</tr>\n"

    html_table += "</table>"

    html_table2 = "<table border='1'>\n"
    # Create table header
    html_table2 += "<tr>"
    for col in Principal_particulars.columns:
        html_table2 += f"<th>{col}</th>"
    html_table2 += "</tr>\n"

    # Iterate over rows
    for index, row in Principal_particulars.iterrows():
        html_table2 += "<tr>"
        for value in row:
            html_table2 += f"<td>{value}</td>"
        html_table2 += "</tr>\n"

    html_table2 += "</table>"

    html_table3 = "<table border='1'>\n"
    # Create table header
    html_table3 += "<tr>"
    for col in ME.columns:
        html_table3 += f"<th>{col}</th>"
    html_table3 += "</tr>\n"

    # Iterate over rows
    for index, row in ME.iterrows():
        html_table3 += "<tr>"
        for value in row:
            html_table3 += f"<td>{value}</td>"
        html_table3 += "</tr>\n"

    html_table3 += "</table>"

    html_table4 = "<table border='1'>\n"
    # Create table header
    html_table4 += "<tr>"
    for col in AE.columns:
        html_table4 += f"<th>{col}</th>"
    html_table4 += "</tr>\n"

    # Iterate over rows
    for index, row in AE.iterrows():
        html_table4 += "<tr>"
        for value in row:
            html_table4 += f"<td>{value}</td>"
        html_table4 += "</tr>\n"

    html_table4 += "</table>"

    html_table5 = "<table border='1'>\n"
    # Create table header
    html_table5 += "<tr>"
    for col in combined_df.columns:
        html_table5 += f"<th>{col}</th>"
    html_table5 += "</tr>\n"

    # Iterate over rows
    for index, row in combined_df.iterrows():
        html_table5 += "<tr>"
        for value in row:
            html_table5 += f"<td>{value}</td>"
        html_table5 += "</tr>\n"

    html_table5 += "</table>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EEXI REPORT</title>
        <style>
            body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            h1 {{
                color: #193185;
                font-size: 36px;
                margin-bottom: 20px;
            }}
            h2{{
                color: #193185;
                font-size: 30px; 

            }}
            img {{
                width: 100px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 16px;
                font-weight: bold;
            }}
            
            .second-info{{ margin-left: 100px;}}
            table {{
                margin: 20px auto;
                    width: 65%;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            .card {{
                background-color: #193185; /* Light orange color */
                border: 1px solid #ccc;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                margin: 10px auto;
                padding: 15px;
                width: 250px; /* Fixed width */
                height: 50px; /* Fixed height */
                max-width: 400px;
                text-align: left;
                border-radius: 10px;
                color: white;
                align-items: center; /* Center the text vertically */
                justify-content: center; /* Center the text horizontally */
                text-align: center; /* Center the text */
            }}
            
                table, tr, td {{height: 30px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%;
                        display: flex;
                        justify-content: center;
            }}
            
            hr {{
                border-width: 3px;
                border-color: #33;
                margin-top: 20px;
                border-style: solid; /* Add border style */
            }}
            
                
            th {{
        background: blue;
        color: white;
        height: 41px;
    }}
        </style>
    </head>
    <body>
        {image_tag}
        <br>
        <br>
        <br>
        <br>
        <h1>EEXI REPORT </h1>    <hr>
        <div class="info">
            <div class='first-info'>
                <p style="font-size: 18px;">VESSEL NAME: {vessel_name}</p>
            </div>
        </div>
        <hr>
        <br>
            <h2>EEXI</h2>
        <div class="plot_div">
            {plot_div}
        </div>
        <br>
        <br>
            <h2>RESULT</h2>
        {html_table5}
        <br>
        <br>
        <div class="info">
            <div class="card">
                <p>Enginee Power: {mcr_pwr} kW</p>
            </div>
            <div class="card">
                <p>RPM: {mcr_rpm}</p>
            </div>
            <div class="card">
                <p>Engine Power limit: {new_mcr_pwr} kW</p>
            </div>
            <div class="card">
                <p>RPM limit : {new_mcr_rpm}</p>
            </div>
        </div>
        <br>
        <br>
        <h2>GENERAL INFORMATION</h2>
        <!-- Add the centered and bigger table -->
        {html_table}
        <br>
        <br>
        <h2>PRINCIPAL PARTICULARS</h2>
        {html_table2}
        <br>
        <br>
        <h2>MAIN ENGINE</h2>
        {html_table3}
        <br>
        <br>
        <h2>AUXILIARY ENGINE</h2>
        {html_table4}
        <br>
        <br>
        <br>
    </body>
    </html>
    """


    file_name = 'EEXI'+imo+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)




@router.post('/api/v1/html/intervention_html')
async def index(info:Request,imo:str=None,vessel_name:str =None):
    s = await info.json()
    s1 = s['data1']
    s2 = s['data2']
    Table1 = pd.DataFrame.from_dict([s1]).astype(str)
    VSL_Name = Table1['vessel'].values[0]
    Intervention = Table1['intervention'].values[0]
    Intervention_Date = Table1['date'].values[0]
    monitoring_period = s['monitoring_period']

    #Monitoring_period
    draft =  Table1['draft'].values[0]
    seastate =  Table1['seastate'].values[0]
    Power_gain_int = s2['power']
    Power_gain = str(round(s2['power'],2))
    Fo_gain = str(round(s2['fo'],2))
    Fo_gain_int = s2['fo']
    # Data 2: Speed-FO Curve
    data1 = pd.DataFrame.from_dict(s2['fo_chart'])
    data1 = data1.rename({'before': 'pre_fo', 'after': 'post_fo', 'index': 'speed'}, axis=1)

    fig1 = go.Figure()

    fig1.add_trace(go.Scatter(x=data1['speed'], y=data1['pre_fo'], mode='lines+markers',
                            marker=dict(size=7),
                            name='Pre Analysis', line=dict(color='blue')))
    fig1.add_trace(go.Scatter(x=data1['speed'], y=data1['post_fo'], mode='lines+markers',
                            marker=dict(size=7),
                            name='Post Analysis', line=dict(color='green')))

    fig1.update_layout(
        xaxis_title='Speed (knots)',
        yaxis_title='FO/24HR (Tonne)',
        font=dict( size=12),
        title_font=dict(size=15),
        width=1000,  # Set the desired width
        height=800 
    )

    #fig1.show()
    #fig1.write_image('speed_power_intervention.png')
    plot_div = pyo.plot(fig1, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    # Data 2: Speed-FO Curve
    data2 = pd.DataFrame.from_dict(s2['power_chart'])
    data2 = data2.rename({'before': 'pre_power', 'after': 'post_power', 'index': 'speed'}, axis=1)

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(x=data2['speed'], y=data2['pre_power'], mode='lines+markers',
                            marker=dict(size=7),
                            name='Pre Analysis', line=dict(color='blue')))
    fig2.add_trace(go.Scatter(x=data2['speed'], y=data2['post_power'], mode='lines+markers',
                            marker=dict(size=7),
                            name='Post Analysis', line=dict(color='green')))

    fig2.update_layout(
        xaxis_title='Speed (knots)',
        yaxis_title='Power (kW)',
        font=dict( size=12),
        title_font=dict(size=15),
        width=1000,  # Set the desired width
        height=800 
)


    #fig2.write_image('speed_fo_intervention.png')
    #fig2.show()

    plot_div1 = pyo.plot(fig2, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})


    html_content = f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Load Diagram Report</title>
        <style>
        body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            
            h1 {{
                color: #193185;
                font-size: 36px;
                margin-bottom: 20px;
            }}

            h2 {{
                color: #193185;
                font-size: 30px; 
            }}

            img {{
                width: 200px; /* Make the image larger */
                float: right;
            }}

            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 16px;
            }}

            .second-info {{
                margin-left: 100px;
            }}

            .plot_div {{
                width: 70%; /* Increase width of the plot_div */
                display: flex;
                justify-content: center;
                align-items: center;
                margin: auto; /* Center the plot_div */
            }}

            .rectangles-container {{
                display: flex;
                justify-content: space-evenly;
                align-items: center;
                margin-bottom: 20px;
            }}

            hr {{
                border-width: 3px;
                border-color: #33;
                margin-top: 20px;
                border-style: solid; /* Add border style */
            }}
            
            .rectangle {{
                min-width: 200px;
                padding: 15px;
                border: 2px solid #193185;
                margin-right: 20px;
                color: white;
                text-align: center;
                border-radius: 8px;
                box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.2);
            }}

            th {{
                background: blue;
                color: white;
                height: 41px;
            }}
        </style>
    </head>

    <body>
        {image_tag}
        <br>
        <br>
        <h1>INTERVENTION REPORT</h1>
        <hr>

        <!-- Add information in HTML format -->
        <div class="info">
            <div class='first-info'>
                <p style="font-size: 18px;">Vessel Name: {VSL_Name}</p>
                <p style="font-size: 18px;">Intervention: {Intervention}</p>
                <p style="font-size: 18px;">Intervention Date: {Intervention_Date}</p>
                <p style="font-size: 18px;">Monitoring Period: {monitoring_period}</p>

            </div>
        </div>
        <hr>
        <div class='second-info' style="display: flex; justify-content: flex-start; gap: 100px;">
            <p style="font-size: 18px; font-weight: bold;">Draft: {draft} meters</p>
            <p style="font-size: 18px; font-weight: bold;">Seastate: {seastate}</p>
        </div>
        <br>
        <h2>FO Comparison</h2>
        <div class="plot_div">
            {plot_div}
        </div>
    """

    # Add conditional content for FO gain or loss
    if Fo_gain_int >= 0:
        html_content += f"""
        <div class="rectangles-container">
            <div class="rectangle engine-power" style="background-color: #008000; border-color: #008000;">
                <p>Gain in FO: {Fo_gain} %</p>
            </div>
        </div>
        """
    else:
        html_content += f"""
        <div class="rectangles-container">
            <div class="rectangle engine-rpm" style="background-color: #FF0000; border-color: #FF0000;">
                <p>Loss in FO: {Fo_gain} %</p>
            </div>
        </div>
        """

    # Continue with the rest of the HTML content
    html_content += f"""
        <h2>Power Comparison</h2>
        <div class="plot_div">
            {plot_div1}
        </div>
    """

    # Add conditional content for Power gain or loss
    if Power_gain_int >= 0:
        html_content += f"""
        <div class="rectangles-container">
            <div class="rectangle engine-power" style="background-color: #008000; border-color: #008000;">
                <p>Gain in Power: {Power_gain} %</p>
            </div>
        </div>
        """
    else:
        html_content += f"""
        <div class="rectangles-container">
            <div class="rectangle engine-rpm" style="background-color: #FF0000; border-color: #FF0000;">
                <p>Loss in Power: {Power_gain} %</p>
            </div>
        </div>
        """

    # Save the HTML content to a file
    file_name = 'Intervention'+VSL_Name+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)    


@router.post('/api/v1/html/imodcs')
async def index(info:Request,vessel_name:str=None,year:str =None):
    s = await info.json()
    ship_particulars_df = pd.DataFrame(list(s["data"]["ship_particulars"].items()), columns=['Particular', 'Detail'])
    ship_particulars_df['Particular'].replace({
        'vessel_name': 'Name of the ship',
        'imo': 'IMO Number',
        'company': 'Company',
        'flag': 'Flag',
        'ship_type': 'Ship Type',
        'gross_tonage': 'Gross Tonage',
        'nt': 'NT',
        'dwt': 'DWT',
        'eedi': 'EEDI',
        'ice_class': 'Ice Class'
    }, inplace=True)

    # Period
    period_df = pd.DataFrame([s["data"]["period"]]).rename(columns={
        'Period_Start': 'Period Start',
        'Period_End': 'Period End',
        'hours': 'Hours Underway (h)',
        'distance': 'Distance Travelled (Nm)'
    })

    # Fuel consumption
    fuel_consp_df = pd.DataFrame(s["data"]["fuel_concumption"]).rename(columns={
        'fuel_type': 'Fuel Type',
        'amount': 'Total Fuel',
        'Emission_factor': 'Emission Factor [t(CO2)/t(fuel)]',
        'monitoring_method': 'Monitoring Method'
    })

    # Engine power
    engine_power_df = pd.DataFrame(list(s["data"]["engine_power"].items()), columns=['Machinery', 'Rated Power in kW'])
    engine_power_df['Machinery'].replace({
        'main_engine': 'Main Engine',
        'aux1': 'Aux 1',
        'aux2': 'Aux 2',
        'aux3': 'Aux 3',
        'aux4': 'Aux 4',
        'aux5': 'Aux 5',
        'turbo_generator': 'Turbo Generator',
        'shaft_generator': 'Shaft Generator'
    }, inplace=True)



    html_table = "<table border='1'>\n"
    # Create table header
    html_table += "<tr>"
    for col in ship_particulars_df.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr>\n"

    # Iterate over rows
    for index, row in ship_particulars_df.iterrows():
        html_table += "<tr>"
        for value in row:
            html_table += f"<td>{value}</td>"
        html_table += "</tr>\n"

    html_table += "</table>"

    html_table2 = "<table border='1'>\n"
    # Create table header
    html_table2 += "<tr>"
    for col in period_df.columns:
        html_table2 += f"<th>{col}</th>"
    html_table2 += "</tr>\n"

    # Iterate over rows
    for index, row in period_df.iterrows():
        html_table2 += "<tr>"
        for value in row:
            html_table2 += f"<td>{value}</td>"
        html_table2 += "</tr>\n"

    html_table2 += "</table>"

    html_table3 = "<table border='1'>\n"
    # Create table header
    html_table3 += "<tr>"
    for col in fuel_consp_df.columns:
        html_table3 += f"<th>{col}</th>"
    html_table3 += "</tr>\n"

    # Iterate over rows
    for index, row in fuel_consp_df.iterrows():
        html_table3 += "<tr>"
        for value in row:
            html_table3 += f"<td>{value}</td>"
        html_table3 += "</tr>\n"

    html_table3 += "</table>"

    html_table4 = "<table border='1'>\n"
    # Create table header
    html_table4 += "<tr>"
    for col in engine_power_df.columns:
        html_table4 += f"<th>{col}</th>"
    html_table4 += "</tr>\n"

    # Iterate over rows
    for index, row in engine_power_df.iterrows():
        html_table4 += "<tr>"
        for value in row:
            html_table4 += f"<td>{value}</td>"
        html_table4 += "</tr>\n"

    html_table4 += "</table>"

    #-------------------------------------------------------HTML--------------------------------------------------------------#

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>IMO DCS REPORT</title>
        <style>
            body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            h1 {{
                color: #193185;
                font-size: 36px;
                margin-bottom: 20px;
            }}
            h2{{
                color: #193185;
                font-size: 30px; 

            }}
            img {{
                width: 100px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 16px;
                font-weight: bold;
            }}
            
            .second-info{{ margin-left: 100px;}}
            table {{
                margin: 20px auto;
                    width: 65%;
                    border-collapse: collapse;
                    border: solid;
                        
            }}
            
                table, tr, td {{height: 30px;
                    border: 1px solid;
                }}
            .plot_div{{
                        width: 100%;
                        display: flex;
                        justify-content: center;
            }}
            
            hr {{
                border-width: 3px;
                border-color: #33;
                margin-top: 20px;
                border-style: solid; /* Add border style */
            }}
            
                
            th {{
        background: blue;
        color: white;
        height: 41px;
    }}
        </style>
    </head>
    <body>
        {image_tag}
        <br>
        <br>
        <br>
        <br>
        <br>
        <br><br>
        <br>
        <br>
        <br>
        <br>
        <h1>ANNUAL EMISSION REPORT </h1>    <hr>
        <div class="info">
            <div class='first-info'>
                <p style="font-size: 18px;">Vessel Name: {vessel_name} </p>
                <p style="font-size: 18px;"> Year: {year} </p>

            </div>
        </div>
        <hr>
            <br>
        <h2>SHIP PARTICULARS</h2>
        <!-- Add the centered and bigger table -->
        {html_table}
        <br>
        <br>
        <h2>PERIOD, HOURS AND DISTANCE REPORT</h2>
        {html_table2}
        <br>
        <br>
        <h2>FUEL CONSUMPTION REPORT</h2>
        {html_table3}
        <br>
        <br>
        <h2>ENGINE POWER</h2>
        {html_table4}
        <br>
        <br>
        <br>
    </body>
    </html>
    """


    # Save the HTML content to a file
    file_name = 'IMO_DSC_'+vessel_name+year+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)    

@router.post('/api/v1/aemissing_vessels')
async def index(info:Request=None,period:str=None,fleet_name:str=None,count:str=None):
    s = await info.json()
    chart = pd.DataFrame(s['data']['chartData'])
    labels = chart['type']
    sizes = chart['value']
    colors = ['green', 'blue']  # Custom colors

    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, marker=dict(colors=colors))])
    fig.update_traces(textinfo='value')
    # fig.write_image('electrical_graph_fleet.png')
    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

    df = pd.DataFrame(s['data']['tableData'])
    df.rename(columns={'fleet': 'FLEET', 'class': 'CLASS', 'missing_vessels': 'MISSING VESSELS', 'imo': "IMO", 'engine_maker': "ENGINE MAKER"}, inplace=True)
    df.insert(0, 'SL No.', range(1, len(df) + 1))
    df

    html_table = "<table border='1'>\n"
    # Create table header
    html_table += "<tr>"
    for col in df.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr>\n"

    # Iterate over rows
    for index, row in df.iterrows():
        html_table += "<tr>"
        for value in row:
            html_table += f"<td>{value}</td>"
        html_table += "</tr>\n"

    html_table += "</table>"

    #------------------------------------------------------html------------------------------------------------------------#

    if fleet_name == 'All Fleets':
        fleet_info = f"<strong>Total Vessels in All Fleets: {count}</strong>"
    else:
        fleet_info = f"<strong>Total Vessels in {fleet_name}: {count}</strong>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AE Missing Vessels Report</title>
        <style>
            body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            h1 {{
                color: #193185;
                font-size: 36px;
                margin-bottom: 20px;
            }}
            h2 {{
                color: #193185;
                font-size: 30px; 
            }}
            img {{
                width: 100px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 16px;
                font-weight: bold;
            }}
            .second-info{{ margin-left: 100px; }}
            table {{
                margin: 20px auto;
                width: 75%;
                border-collapse: collapse;
                border: solid;
            }}
            table, tr, td, th {{
                border: 1px solid;
                height: 30px;
            }}
            td, th {{
                padding: 5px;
                width: 90px; /* Set the desired width for cells */
            }}
            .plot_div{{
                width: 100%;
                display: flex;
                justify-content: center;
            }}
            hr {{
                border-width: 3px;
                border-color: #33;
                margin-top: 20px;
                border-style: solid; /* Add border style */
            }}
            th {{
                background: blue;
                color: white;
                height: 30px;
            }}
            .fleet-info {{
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                color: #333;
            }}
        </style>
    </head>
    <body>
        {image_tag}
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>
        <h1>AE Missing Vessels Report</h1>    
        <hr>
        <div class="info">
            <div class='first-info'>
                <p style="font-size: 18px;">Fleet: {fleet_name}</p>
                <p style="font-size: 18px;">Month: {period}</p>
            </div>
        </div>
        <hr>
        <br>
        <br>
        <div class="fleet-info">
            {fleet_info}
        </div>
        <div class="plot_div">
            {plot_div}
        </div>
        <br>
        <br>
        <!-- Add the centered and bigger table -->
        {html_table}
        <br>
        <br>
    </body>
    </html>
    """
    file_name = 'AE_MIssing_VESSELS'+fleet_name+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)  




@router.post('/api/v1/cii')
async def index(info:Request=None,tab_name:str=None,report_type:str=None,vessel_name:str=None,year:str=None,start_date:str=None,end_date:str=None):
    s = await info.json()



    if tab_name == 'CII Daily Analysis':
        if report_type == 'Year':

            data1 = pd.DataFrame.from_dict(s['data']['daily_chart'])
            cl_map = {'A':'green','B':'lightgreen','C':'yellow','D':'orange','E':'red', None: 'white'}
            data1['color_col'] = data1['cii_rating'].map(cl_map)
            data3 = pd.DataFrame.from_dict(s['data']['table_data_1'])
            table_data = data3[['date', 'total_fuel', 'total_co2', 'miles_by_gps', 'cii_rating', 'required_cii', 'attained_cii', 'current_cii']]
            dict_date = pd.Series(data3['required_cii'].values, index=data3['date']).to_dict()
            data1['required_cii'] = data1['date'].apply(lambda x: dict_date.get(x, np.nan))

        


            fig = go.Figure()

            # Add data traces with legend entries
            fig.add_trace(go.Scatter(
                x=data1['date'], y=data1['current_cii'],
                mode='lines', name='Current CII', line=dict(color='cyan'),
                showlegend=True  # Show this trace in the legend
            ))
            fig.add_trace(go.Scatter(
                x=data1['date'], y=data1['required_cii'],
                mode='lines', name='Required CII', line=dict(color='blue', dash='dash'),
                showlegend=True  # Show this trace in the legend
            ))
            fig.add_trace(go.Bar(
                x=data1['date'], y=data1['attained_cii'],
                marker_color=data1['color_col'],
                name='Attained CII',
                showlegend=False  # Show this trace in the legend
            ))

            # Add custom legend entries with specific colors
            legend_entries = {
                'A': 'green',
                'B': 'lightgreen',
                'C': 'yellow',
                'D': 'orange',
                'E': 'red'
            }

            for entry, color in legend_entries.items():
                fig.add_trace(go.Scatter(
                    x=[None],  # Dummy data
                    y=[None],  # Dummy data
                    mode='markers',  # Use markers to show color
                    name=entry,
                    marker=dict(color=color, size=10),  # Color for the legend entry
                    showlegend=True  # Show this trace in the legend
                ))

            # Update layout
            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Attained CII (g-Co2/ T-Nm)',
                xaxis=dict(tickangle=-45, tickmode='array'),
                legend_title=None,
                font=dict(size=13),
                autosize=True,
                height=800,
                width=1500
            )
            # fig.write_image('msc_environment_cii_year.png')
            # fig.show()
            plot_div_year = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            
            html_table = "<table border='1'>\n"
            # Create table header
            html_table += "<tr>"
            for col in table_data.columns:
                html_table += f"<th>{col}</th>"
            html_table += "</tr>\n"

            # Iterate over rows
            for index, row in table_data.iterrows():
                html_table += "<tr>"
                for value in row:
                    html_table += f"<td>{value}</td>"
                html_table += "</tr>\n"

            html_table += "</table>"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CII Daily Trend Report</title>
                    <style>
                body {{
                    text-align: center;
                    font-family: 'Roboto', sans-serif;
                    color: #333;
                    background-color: #fff;
                }}
                h1 {{
                    color: #193185;
                    font-size: 36px;
                    margin-bottom: 20px;
                }}
                h2 {{
                    color: #193185;
                    font-size: 30px; 
                }}
                img {{
                    width: 100px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;
                    display: flex;
                    font-size: 16px;
                    font-weight: bold;
                }}
                .second-info{{ margin-left: 100px; }}
                table {{
                    margin: 20px auto;
                    width: 75%;
                    border-collapse: collapse;
                    border: solid;
                }}
                table, tr, td, th {{
                    border: 1px solid;
                    height: 30px;
                }}
                td, th {{
                    padding: 5px;
                    width: 90px; /* Set the desired width for cells */
                }}
                .plot_div{{
                    width: 100%;
                    display: flex;
                    justify-content: center;
                }}
                hr {{
                    border-width: 3px;
                    border-color: #33;
                    margin-top: 20px;
                    border-style: solid; /* Add border style */
                }}
                th {{
                    background: blue;
                    color: white;
                    height: 30px;
                }}
                .fleet-info {{
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    color: #333;
                }}
            </style>
            </head>
            <body>
                {image_tag}
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <h1>CII Daily Trend Report</h1>
                <hr>
                <div class="info">
                    <div class='first-info'>
                        <p style="font-size: 18px;">Vessel: {vessel_name}</p>
                        <p style="font-size: 18px;">Year: {year} </p>
                    </div>
                </div>
                <hr>
                <h2>CII Daily Trend Report</h2>
                <div class="plot_div">
                    {plot_div_year}
                </div>
                <br>
                <br>
                {html_table}
            </body>
            </html>
            """

        elif report_type == 'Date':
            # Example API request and data processing
            # f = requests.get(date_url, headers=headers).json()
            
            data1 = pd.DataFrame.from_dict(s['data']['daily_chart'])
            cl_map = {'A':'green','B':'lightgreen','C':'yellow','D':'orange','E':'red', None: 'white'}
            data1['color_col'] = data1['cii_rating'].map(cl_map)
            data3 = pd.DataFrame.from_dict(s['data']['table_data_1'])
            table_data = data3[['date', 'total_fuel', 'total_co2', 'miles_by_gps', 'cii_rating', 'required_cii', 'attained_cii', 'current_cii']]
            dict_date = pd.Series(data3['required_cii'].values, index=data3['date']).to_dict()
            data1['required_cii'] = data1['date'].apply(lambda x: dict_date.get(x, np.nan))

            fig = go.Figure()

            # Add data traces with legend entries
            fig.add_trace(go.Scatter(
                x=data1['date'], y=data1['current_cii'],
                mode='lines', name='Current CII', line=dict(color='cyan'),
                showlegend=True  # Show this trace in the legend
            ))
            fig.add_trace(go.Scatter(
                x=data1['date'], y=data1['required_cii'],
                mode='lines', name='Required CII', line=dict(color='blue', dash='dash'),
                showlegend=True  # Show this trace in the legend
            ))
            fig.add_trace(go.Bar(
                x=data1['date'], y=data1['attained_cii'],
                marker_color=data1['color_col'],
                name='Attained CII',
                showlegend=False  # Show this trace in the legend
            ))

            # Add custom legend entries with specific colors
            legend_entries = {
                'A': 'green',
                'B': 'lightgreen',
                'C': 'yellow',
                'D': 'orange',
                'E': 'red'
            }

            for entry, color in legend_entries.items():
                fig.add_trace(go.Scatter(
                    x=[None],  # Dummy data
                    y=[None],  # Dummy data
                    mode='markers',  # Use markers to show color
                    name=entry,
                    marker=dict(color=color, size=10),  # Color for the legend entry
                    showlegend=True  # Show this trace in the legend
                ))

            # Update layout
            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Attained CII (g-Co2/ T-Nm)',
                xaxis=dict(tickangle=-45, tickmode='array'),
                legend_title=None,
                font=dict(size=13),
                autosize=True,
                height=800,
                width=1500
            )

            # Save and show the plot
            

            # Generate the HTML div for embedding
            plot_div_date = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            
            html_table = "<table border='1'>\n"
            # Create table header
            html_table += "<tr>"
            for col in table_data.columns:
                html_table += f"<th>{col}</th>"
            html_table += "</tr>\n"

            # Iterate over rows
            for index, row in table_data.iterrows():
                html_table += "<tr>"
                for value in row:
                    html_table += f"<td>{value}</td>"
                html_table += "</tr>\n"

            html_table += "</table>"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CII Daily Trend Report</title>
                <style>
                body {{
                    text-align: center;
                    font-family: 'Roboto', sans-serif;
                    color: #333;
                    background-color: #fff;
                }}
                h1 {{
                    color: #193185;
                    font-size: 36px;
                    margin-bottom: 20px;
                }}
                h2 {{
                    color: #193185;
                    font-size: 30px; 
                }}
                img {{
                    width: 100px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;
                    display: flex;
                    font-size: 16px;
                    font-weight: bold;
                }}
                .second-info{{ margin-left: 100px; }}
                table {{
                    margin: 20px auto;
                    width: 75%;
                    border-collapse: collapse;
                    border: solid;
                }}
                table, tr, td, th {{
                    border: 1px solid;
                    height: 30px;
                }}
                td, th {{
                    padding: 5px;
                    width: 90px; /* Set the desired width for cells */
                }}
                .plot_div{{
                    width: 100%;
                    display: flex;
                    justify-content: center;
                }}
                hr {{
                    border-width: 3px;
                    border-color: #33;
                    margin-top: 20px;
                    border-style: solid; /* Add border style */
                }}
                th {{
                    background: blue;
                    color: white;
                    height: 30px;
                }}
                .fleet-info {{
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    color: #333;
                }}
            </style>
            </head>
            <body>
                {image_tag}
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <h1>CII Daily Trend Report</h1>
                <hr>
                <div class="info">
                    <div class='first-info'>
                        <p style="font-size: 18px;">Vessel: {vessel_name}</p>
                        <p style="font-size: 18px;">Monitoring period: {start_date} to {end_date}</p>
                    </div>
                </div>
                <hr>
                <h2>CII Daily Trend Report</h2>
                <div class="plot_div">
                    {plot_div_date}
                </div>
                <br>
                <br>
                {html_table}
            </body>
            </html>
            """
            

    else:
        if report_type == 'Year':    
            
            data3 = pd.DataFrame.from_dict(s['data']['chart_data'])
            cl_map = {'A':'green','B':'lightgreen','C':'yellow','D':'orange','E':'red'}
            data3['color_col'] = data3['attained_rating'].map(cl_map)

            #TABLE
            data4 = pd.DataFrame.from_dict(s['data']['table_data'])
            table_data = data4[['week_number', 'total_co2','sailed_distance', 'attained_cii','attained_rating']]

            table_data.rename(columns={'week_number':'Week Number','total_co2':
            'Total CO2','sailed_distance':
            'Total Distance','attained_cii':
            'Attained CII','attained_rating':
            'CII Rating'},inplace=True)




            # Weekly trend line chart
            fig_weekly = go.Figure()

            # Add traces with legend entries
            fig_weekly.add_trace(go.Scatter(
                x=data3['week_number'], y=data3['current_cii'],
                mode='lines', name='Current CII', line=dict(color='cyan'))
            )
            fig_weekly.add_trace(go.Scatter(
                x=data3['week_number'], y=data3['required_cii'],
                mode='lines', name='Required CII', line=dict(color='blue', dash='dash'))
            )
            fig_weekly.add_trace(go.Bar(
                x=data3['week_number'], y=data3['attained_cii'],
                marker_color=data3['color_col'], showlegend=False)  # Exclude from legend
            )

            legend_entries = {
                'A': 'green',
                'B': 'lightgreen',
                'C': 'yellow',
                'D': 'orange',
                'E': 'red'
            }

            for entry, color in legend_entries.items():
                fig_weekly.add_trace(go.Scatter(
                    x=[None],  # Dummy data
                    y=[None],  # Dummy data
                    mode='markers',  # Use markers to show color
                    name=entry,
                    marker=dict(color=color, size=10),  # Color for the legend entry
                    showlegend=True  # Show this trace in the legend
                ))

            fig_weekly.update_layout(
                xaxis_title='Week number',
                yaxis_title='Attained CII (g-Co2/ T-Nm)',
                xaxis=dict(tickangle=-45),
                legend_title=None,
                font=dict(size=13),
                autosize=True,
                height=800,
                width=1500
            )
            # fig_weekly.write_image('msc_environment_cii_week_year.png')
            # fig_weekly.show()
            plot_div_weekly = pyo.plot(fig_weekly, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

            # Weekly pie chart
            value_counts = data3[data3['attained_rating'] != 0]['attained_rating'].value_counts()

            colors = [cl_map.get(c, 'white') for c in value_counts.index]  # Map colors based on ratings

            fig_pie = go.Figure(data=[go.Pie(
                labels=value_counts.index,
                values=value_counts.values,
                marker=dict(colors=colors)
            )])
            fig_pie.update_layout(
                legend_title=None,
                font=dict(size=13),
                height = 600,
                width = 600
            )
            
            plot_div_pie = pyo.plot(fig_pie, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})
            
            html_table = "<table border='1'>\n"
            # Create table header
            html_table += "<tr>"
            for col in table_data.columns:
                html_table += f"<th>{col}</th>"
            html_table += "</tr>\n"

            # Iterate over rows
            for index, row in table_data.iterrows():
                html_table += "<tr>"
                for value in row:
                    html_table += f"<td>{value}</td>"
                html_table += "</tr>\n"

            html_table += "</table>"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CII Weekly Analysis Report</title>
                <style>
                body {{
                    text-align: center;
                    font-family: 'Roboto', sans-serif;
                    color: #333;
                    background-color: #fff;
                }}
                h1 {{
                    color: #193185;
                    font-size: 36px;
                    margin-bottom: 20px;
                }}
                h2 {{
                    color: #193185;
                    font-size: 30px; 
                }}
                img {{
                    width: 100px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;
                    display: flex;
                    font-size: 16px;
                    font-weight: bold;
                }}
                .second-info{{ margin-left: 100px; }}
                table {{
                    margin: 20px auto;
                    width: 75%;
                    border-collapse: collapse;
                    border: solid;
                }}
                table, tr, td, th {{
                    border: 1px solid;
                    height: 30px;
                }}
                td, th {{
                    padding: 5px;
                    width: 90px; /* Set the desired width for cells */
                }}
                .plot_div{{
                    width: 100%;
                    display: flex;
                    justify-content: center;
                }}
                hr {{
                    border-width: 3px;
                    border-color: #33;
                    margin-top: 20px;
                    border-style: solid; /* Add border style */
                }}
                th {{
                    background: blue;
                    color: white;
                    height: 30px;
                }}
                .fleet-info {{
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    color: #333;
                }}
            </style>
            </head>
            <body>
                {image_tag}
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <h1>CII Weekly Analysis Report</h1>
                <hr>
                <div class="info">
                    <div class='first-info'>
                        <p style="font-size: 18px;">Vessel: {vessel_name}</p>
                        <p style="font-size: 18px;">Year: {year}</p>
                    </div>
                </div>
                <hr>
                <h2>CII Weekly Trend {year}</h2>
                <div class="plot_div">
                    {plot_div_weekly}
                </div>
                <br>
                <br>
                <br>
                <h2>CII Weekly Trend</h2>
                <div class="plot_div">
                    {plot_div_pie}
                </div>
                <br>
                <br>
                {html_table}
            </body>
            </html>
            """

        elif report_type == 'Date':
            data3 = pd.DataFrame.from_dict(s['data']['chart_data'])
            data3['attained_cii'] = data3['attained_cii'].astype('float64')

            # Color mapping
            cl_map = {'A':'green', 'B':'lightgreen', 'C':'yellow', 'D':'orange', 'E':'red'}
            data3['color_col'] = data3['attained_rating'].map(cl_map)

            # Line and Bar Plot
            fig = go.Figure()

            # Add Current CII line trace
            fig.add_trace(go.Scatter(
                x=data3['week_number'],
                y=data3['current_cii'],
                mode='lines',
                name='Current CII',
                line=dict(color='cyan')
            ))

            # Add Required CII line trace
            fig.add_trace(go.Scatter(
                x=data3['week_number'],
                y=data3['required_cii'],
                mode='lines',
                name='Required CII',
                line=dict(color='blue', dash='dash')
            ))

            # Add Attained CII bar trace
            fig.add_trace(go.Bar(
                x=data3['week_number'],
                y=data3['attained_cii'],
                marker_color=data3['color_col'],
                name='Attained CII'
            ))

            # Add custom legend entries for colors
            for rating, color in cl_map.items():
                fig.add_trace(go.Scatter(
                    x=[None],  # Dummy data
                    y=[None],  # Dummy data
                    mode='markers',
                    name=str(rating),
                    marker=dict(color=color, size=10),
                    showlegend=True
                ))

            # Update layout for line/bar plot
            fig.update_layout(
                xaxis_title='Week number',
                yaxis_title='Attained CII (g-Co2/ T-Nm)',
            xaxis=dict(tickangle=-45),
                font=dict(size=13, family='Arial'),
                autosize=True,
                height=800,
                width=1500
            )

            # Save and show the line/bar plot
           
            # Convert the figure to a Plotly HTML div
            plot_div_weekly = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

            # Pie Chart
            value_counts = data3['attained_rating'].value_counts(dropna=True, sort=False).reset_index()
            value_counts.columns = ['attained_rating', 'count']
            value_counts['color_col'] = value_counts['attained_rating'].map(cl_map)

            fig_pie = go.Figure()

            # Add pie chart trace without center hole
            fig_pie.add_trace(go.Pie(
                labels=value_counts['attained_rating'],
                values=value_counts['count'],
                marker=dict(colors=value_counts['color_col']),
                textinfo='label+percent',
                insidetextorientation='horizontal',
                showlegend=True  # Ensure legend is shown
            ))

            # Update layout for pie chart
            fig_pie.update_layout(
                font=dict(size=13, family='Arial'),
                autosize=True,
                height=600,
                width=600,
                showlegend=True,  # Ensure legend is shown
                legend_title=None,  # Remove title from legend
                legend=dict(
                    traceorder='normal',
                    orientation='v'  # Horizontal orientation for the legend
                ),
                xaxis=dict(showgrid=False),  # Remove grid lines from x-axis
                yaxis=dict(showgrid=False)   # Remove grid lines from y-axis
            )

            # Save and show the pie chart
            
            # Convert the pie chart to a Plotly HTML div
            plot_div_pie = pyo.plot(fig_pie, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})

            # HTML Content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>CII Weekly Analysis Report</title>
                <style>
                body {{
                    text-align: center;
                    font-family: 'Roboto', sans-serif;
                    color: #333;
                    background-color: #fff;
                }}
                h1 {{
                    color: #193185;
                    font-size: 36px;
                    margin-bottom: 20px;
                }}
                h2 {{
                    color: #193185;
                    font-size: 30px; 
                }}
                img {{
                    width: 100px;
                    float: right;
                }}
                .info {{
                    text-align: left;
                    margin-left: 20px;
                    display: flex;
                    font-size: 16px;
                    font-weight: bold;
                }}
                .second-info{{ margin-left: 100px; }}
                table {{
                    margin: 20px auto;
                    width: 75%;
                    border-collapse: collapse;
                    border: solid;
                }}
                table, tr, td, th {{
                    border: 1px solid;
                    height: 30px;
                }}
                td, th {{
                    padding: 5px;
                    width: 90px;
                }}
                .plot_div{{
                    width: 100%;
                    display: flex;
                    justify-content: center;
                }}
                hr {{
                    border-width: 3px;
                    border-color: #333;
                    margin-top: 20px;
                    border-style: solid;
                }}
                th {{
                    background: blue;
                    color: white;
                    height: 30px;
                }}
                .fleet-info {{
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    color: #333;
                }}
                </style>
            </head>
            <body>
                {image_tag}
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <br>
                <h1>CII Weekly Analysis Report</h1>
                <hr>
                <div class="info">
                    <div class='first-info'>
                        <p style="font-size: 18px;">Vessel: {vessel_name}</p>
                        <p style="font-size: 18px;">Monitoring Period: {start_date} to {end_date}</p>
                    </div>
                </div>
                <hr>
                <h2>CII Weekly Trend {year}</h2>
                <div class="plot_div">
                    {plot_div_weekly}
                </div>
                <br>
                <br>
                <br>
                <h2>CII Weekly Trend</h2>
                <div class="plot_div">
                    {plot_div_pie}
                </div>
                <br>
            </body>
            </html>
            """
    file_name = 'CII Weekly Analysis'+vessel_name+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)  





@router.post('/api/v1/me/missingvessel')
async def index(info:Request=None,fleet:str=None,month:str=None,vessel_name:str=None,period:str=None):
    s = await info.json()

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

    data1 = pd.DataFrame.from_dict(s['data']['tableData_All'])
    data1 = data1.astype(str)
    data1 = data1.drop(columns=['remark_mid', 'remark_end'])
    data1=data1.rename(columns={"imo":"IMO","fleet":"FLEET","class":"CLASS","missing_vessels":"MISSING VESSELS","engine_maker":"ENGINE MAKER","missing_date":"MISSING DATE","email_id":"EMAIL ID"})
    data1.insert(0, 'Sl.No', range(1, len(data1) + 1))
    data1 




    ################################## Image ################################################################################################
    # Create subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{'colspan': 2}, None], [{'type': 'indicator'}, {'type': 'indicator'}]],
        subplot_titles=("ME Reports Submission Progress", "", ""),
        row_heights=[0.3, 0.7],
        vertical_spacing=0.1,
    )

    # Horizontal stacked bar
    fig.add_trace(go.Bar(
        y=[f'Fleet {fleet}'],
        x=[both_missing],
        name='Both missing',
        orientation='h',
        marker=dict(color='rgb(239, 83, 80)'),
        text=[str(both_missing)],
        textposition='auto',
        width=0.4,
        hovertext=f'{both_missing} vessels have both reports missing'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        y=[f'Fleet {fleet}'],
        x=[mid_missing],
        name='Mid missing',
        orientation='h',
        marker=dict(color='rgb(255, 152, 0)'),
        text=[str(mid_missing)],
        textposition='auto',
        width=0.4,
        hovertext=f'{mid_missing} vessels have only mid reports missing'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        y=[f'Fleet {fleet}'],
        x=[end_missing],
        name='End missing',
        orientation='h',
        marker=dict(color='rgb(255, 235, 59)'),
        text=[str(end_missing)],
        textposition='auto',
        width=0.4,
        hovertext=f'{end_missing} vessels have only end reports missing'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        y=[f'Fleet {fleet}'],
        x=[both_available],
        name='Both available',
        orientation='h',
        marker=dict(color='rgb(76, 175, 80)'),
        text=[str(both_available)],
        textposition='auto',
        width=0.4,
        hovertext=f'{both_available} vessels have both reports available'
    ), row=1, col=1)

    # Mid Report Missing Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=total_mid_missing,
        title={'text': "Mid Report Missing", 'font': {'size': 16, 'color': 'black'}},
        gauge={
            'axis': {'range': [0, total_vessels], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, total_mid_missing], 'color': "rgb(239, 83, 80)"},  # Missing - red
                {'range': [total_mid_missing, total_vessels], 'color': "rgb(76, 175, 80)"}  # Available - green
            ],
        },
        number={'font': {'size': 28, 'color': 'black'}, 'suffix': f" / {total_vessels}"},
    ), row=2, col=1)

    # End Report Missing Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=total_end_missing,
        title={'text': "End Report Missing", 'font': {'size': 16, 'color': 'black'}},
        gauge={
            'axis': {'range': [0, total_vessels], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "rgba(0,0,0,0)"},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, total_end_missing], 'color': "rgb(239, 83, 80)"},  # Missing - red
                {'range': [total_end_missing, total_vessels], 'color': "rgb(76, 175, 80)"}  # Available - green
            ],
        },
        number={'font': {'size': 28, 'color': 'black'}, 'suffix': f" / {total_vessels}"},
    ), row=2, col=2)

    # Update layout
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        barmode='stack',
        showlegend=True,
        height=750,
        width=800,
        margin=dict(b=100),
        xaxis={'showgrid': False, 'showticklabels': False, 'range': [0, total_vessels]},
        yaxis={'showgrid': False, 'showticklabels': False},
        legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 0.74, 'xanchor': 'center', 'x': 0.5, 'font': {'color': 'black'}, 'bgcolor': 'rgba(0,0,0,0)'},
    )

    # Add explanatory text annotations for Mid and End Reports
    fig.add_annotation(
        text=f"Report Submission Status for {format_month(month)} : Out of {total_vessels} vessels, {both_missing} vessels have both reports missing.",
        xref="paper", yref="paper",
        x=0.5, y=0.70,
        showarrow=False,
        font=dict(color='black', size=12),
        align='center'
    )

    # Mid Reports text - left corner
    fig.add_annotation(
        text=f"{total_mid_missing} Mid Reports are missing",
        xref="paper", yref="paper",
        x=0.10, y=0.02,
        showarrow=False,
        font=dict(color='black', size=12),
        align='left'
    )

    # End Reports text - right corner
    fig.add_annotation(
        text=f"{total_end_missing} End Reports are missing",
        xref="paper", yref="paper",
        x=0.92, y=0.02,
        showarrow=False,
        font=dict(color='black', size=12),
        align='right'
    )

    # Legend below gauges (for both Mid and End Missing)
    fig.add_annotation(
        text="Available",  # Text for "Available"
        xref="paper", yref="paper",
        x=0.47, y=-0.1,  # Positioning the legend in the center below the gauges
        showarrow=False,
        font=dict(color='black', size=12),
        align='center'
    )

    # Add color box for "Available" (Green)
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.40, y=-0.1,  # Position for the green box
        showarrow=False,
        font=dict(size=1),
        align='left',
        bgcolor="rgb(76, 175, 80)",  # Green color box
        width=13, height=13  # Size of the box
    )

    # Legend for "Missing" below the gauges
    fig.add_annotation(
        text="Missing",  # Text for "Missing"
        xref="paper", yref="paper",
        x=0.62, y=-0.1,  # Position in the center
        showarrow=False,
        font=dict(color='black', size=12),
        align='center'
    )

    # Add color box for "Missing" (Red)
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.56, y=-0.1,  # Position for the red box
        showarrow=False,
        font=dict(size=1),
        align='left',
        bgcolor="rgb(239, 83, 80)",  # Red color box
        width=13, height=13  # Size of the box
    )

    fig.show()
    # fig.write_image('me_missing_vessels.png')
    plot_div = pyo.plot(fig, include_plotlyjs=True, output_type='div', config={'displayModeBar': False})





    html_table = "<table border='1'>\n"
    # Create table header
    html_table += "<tr>"
    for col in data1.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr>\n"

    # Iterate over rows
    for index, row in data1.iterrows():
        html_table += "<tr>"
        for value in row:
            html_table += f"<td>{value}</td>"
        html_table += "</tr>\n"

    html_table += "</table>"


    #--------------------------------------------------html--------------------------------------------------------------------#

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ME Missing Vessels Report</title>
        <style>
            body {{
                text-align: center;
                font-family: 'Roboto', sans-serif;
                color: #333;
                background-color: #fff;
            }}
            h1 {{
                color: #193185;
                font-size: 36px;
                margin-bottom: 20px;
            }}
            h2{{
                color: #193185;
                font-size: 30px; 
            }}
            img {{
                width: 100px;
                float: right;
            }}
            .info {{
                text-align: left;
                margin-left: 20px;
                display: flex;
                font-size: 12px;
                font-weight: normal;
            }}
            .second-info{{ margin-left: 100px; }}
            table {{
                margin: 20px auto;
                width: 65%;
                border-collapse: collapse;
                border: solid;
            }}
            table, tr, td, th {{
                border: 1px solid;
                height: 30px;
            }}
            td, th {{
                padding: 5px;
                width: 100px; /* Set the desired width for cells */
            }}
            .plot_div{{
                width: 100%;
                display: flex;
                justify-content: center;
            }}
            .fleet-info {{
                text-align: center;
                font-size: 24px;
                font-weight: normal;
                margin-bottom: 20px;
                color: #333;
            }}
            hr {{
                border-width: 1px;
                border-color: #33;
                margin-top: 20px;
                border-style: solid; /* Add border style */
            }}
            th {{
                background: blue;
                color: white;
                height: 30px;
    }}
        </style>
    </head>
    <body>
        {image_tag}
        <br>
        <br>
        <br>
        <br>
        <br>
        <br><br>
        <br>
        <br>
        <br>
        <br>
        <h1>ME Missing Vessels Report</h1>    <hr>
        <div class="info">
            <div class='first-info'>
                <p style="font-size: 18px;">Fleet: {fleet}(Total Vessels: {total_vessels}) </p>
                <p style="font-size: 18px;"> Month: {format_month(month)} </p>
            </div>
        </div>
        <hr>
            <br>  
        </div>
        <br>
        <div class="plot_div">
            {plot_div}
        </div>
        <br>
        <h2>ME Missing Vessels Table</h2>
        <!-- Add the centered and bigger table -->
        {html_table}
        <br>
        <br>
    </body>
    </html>
    """

    file_name = 'ME MISSING VESSEL FLEET'+vessel_name+'.html'
    output_file = download_path +file_name
    with open(output_file, 'w',encoding='utf-8') as html_file:
        html_file.write(html_content)

    return FileResponse(path = output_file,filename=file_name)