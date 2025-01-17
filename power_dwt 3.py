from fastapi import APIRouter
from fastapi import Depends
from storage.database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from cache import cache_set
from sklearn.linear_model import LinearRegression
from authentication.authorization import get_token
from storage.vdm_database import get_vdm_db
import json
import numpy as np
import pandas as pd
from datetime import datetime


router = APIRouter(
      prefix="",
      tags=["power_dwt"],
      )

@router.get("/api/v1/power_dwt/")
def get_power_dwt(speed:int = None,sea_state:int = None,input:str=None,db : Session = Depends(get_db),vdm_db:Session = Depends(get_vdm_db),token : Session = Depends(get_token)):
    coeff_teu = cache_set.get_coefficient_teu(db)
    # imos = cache_set.get_coefficient_distinct_imo(db) 
    vessel_detail = cache_set.get_mcr_filter(vdm_db)

    vessel_lis = {i['imo'] for i in vessel_detail}

    final_data = []
    dwt_list = []
    end_list = []
    for j in vessel_lis:
        data_with_noon = [x for x in coeff_teu if x['imo'] == j and x['type'] == 'Noon']
        if not data_with_noon:
            continue

        data_with_noon = sorted(data_with_noon, key=lambda x: datetime.strptime(x['key_date'], '%Y-%m-%d'), reverse=True)
        data_with_noon[0]['x_1'] = datetime.strptime(data_with_noon[0]['x_1'], '%Y-%m-%d').strftime('%d %b %Y')
        data_with_noon[0]['x_2'] = datetime.strptime(data_with_noon[0]['x_2'], '%Y-%m-%d').strftime('%d %b %Y')

        data = {
            'TEU': data_with_noon[0]['teu'],
            'n1': round(float(data_with_noon[0]['n_1']), 2),
            'n2': round(float(data_with_noon[0]['n_2']), 2),
            'n3': round(float(data_with_noon[0]['n_3']), 2),
            'k': round(float(data_with_noon[0]['k']), 2),
            'f2': round(float(data_with_noon[0]['f_2']), 2),
            'f3': round(float(data_with_noon[0]['f_3']), 2),
            'k1': round(float(data_with_noon[0]['k_1']), 2),
            'x1': data_with_noon[0]['x_1'],
            'x2': data_with_noon[0]['x_2'],
            'TYPE': data_with_noon[0]['type'],
            'Vessel_Segment_List': data_with_noon[0]['vessel_segment_list'],
            'Bench_Mark_Analysis': data_with_noon[0]['bench_mark_analysis']
        }

        vessel_detail_filtered = list(filter(lambda x: x['imo'] == j, vessel_detail))

        try:
            data['imo'] = vessel_detail_filtered[0]['imo']
            data['Name'] = vessel_detail_filtered[0]['name']
            data['Fleet'] = vessel_detail_filtered[0]['fleet']
            data['ClassName'] = vessel_detail_filtered[0]['sister_code']
        except (IndexError, KeyError):
            data['imo'] = data['Name'] = data['Fleet'] = data['ClassName'] = None

        filtered_attributes = {8: 'DWT', 148: 'MCR', 20: 'Scantling_Draft'}
        for attr_id, attr_name in filtered_attributes.items():
            try:
                data[attr_name] = float(next(x['value'] for x in vessel_detail_filtered if x['attribute_id'] == attr_id))
            except (StopIteration, ValueError):
                data[attr_name] = None
        dwt_list.append(data['DWT'])
        if input == "power":
            for i in range(speed, speed + 4):
                name = "Power " + str(i)
                power_values = {}
                try:
                    power = round((data['Scantling_Draft'] ** data['n1']) * (i ** data['n2']) * ((10 - sea_state) ** data['n3']) * (np.exp(data['k'])))
                except:
                    power = None
                data[name] = power
                power_values['x'+str(i)] = power
                end_list.append(power_values)
        else:
            for i in range(speed, speed + 4):
                name = "Fuel " + str(i)
                fuel_values = {} 
                try:
                    fuel = round((data['Scantling_Draft'] ** data['n1']) * (i ** data['f2']) * ((10 - sea_state) ** data['f3']) * (np.exp(data['k1'])))
                except:
                    fuel = None
                data[name] = fuel
                fuel_values['x'+str(i)] = fuel
                end_list.append(fuel_values)
        final_data.append(data)

    result={}
    for item in end_list:
        key, value = list(item.items())[0]
        if key in result:
            result[key].append(value)
        else:
            result[key] = [value]
            
    reg_data = {}
    if input == "power":
        print("in power")
        for item in range(speed,speed+4):
            print(item)
            data = {'X': dwt_list, 'y': result['x'+str(item)]}
            df = pd.DataFrame(data)
            print(df)
            X = df[['X']]
            y = df['y']
            coefficients = np.polyfit(X['X'], y, 3)
            X_pred = np.arange(0, 250000, 200)
            y_pred = np.polyval(coefficients, X_pred)
            reg_data['X'] = X_pred.tolist()
            reg_data['Y'+str(item)] = np.round(y_pred,decimals=2).tolist()
    else:
        print("in fuel")
        for item in range(speed,speed+4):
            data = {'X': dwt_list, 'y': result['x'+str(item)]}
            df = pd.DataFrame(data)
            X = df[['X']]
            y = df['y']
            coefficients = np.polyfit(X['X'], y, 3)
            X_pred = np.arange(0, 250000, 200)
            y_pred = np.polyval(coefficients, X_pred)
            reg_data['X'] = X_pred.tolist()
            reg_data['Y'+str(item)] = np.round(y_pred,decimals=2).tolist()

    return {"data":
            {"main_data":final_data,
            "regd":reg_data}
            }



    # vessel_lis= [i['imo'] for i in vessel_detail]
    # vessel_lis = set(vessel_lis)
    # imo = list(vessel_lis)
    
    # final_data = []
    # for j in imo:
        

    #     data_with_noon = list(filter(lambda x: x['imo'] == j and x['type'] == 'Noon' ,coeff_teu))
    #     if not data_with_noon:
    #         continue
    #     data_with_noon = sorted(data_with_noon , key=lambda x: datetime.strptime(x['key_date'],   '%Y-%m-%d') , reverse=True)
    #     data_with_noon[0]['x_1'] = datetime.strptime(data_with_noon[0]['x_1'],'%Y-%m-%d').strftime('%d %b %Y')
    #     data_with_noon[0]['x_2'] = datetime.strptime(data_with_noon[0]['x_2'],'%Y-%m-%d').strftime('%d %b %Y')
        
       

    #     data = {}

    #     data['TEU'] = data_with_noon[0]['teu']
    #     data['n1'] = round(float(data_with_noon[0]['n_1']),2)
    #     data['n2'] = round(float(data_with_noon[0]['n_2']),2)
    #     data['n3'] = round(float(data_with_noon[0]['n_3']),2)
    #     data['k'] = round(float(data_with_noon[0]['k']),2)
    #     data['f2'] = round(float(data_with_noon[0]['f_2']),2)
    #     data['f3'] = round(float(data_with_noon[0]['f_3']),2)
    #     data['k1'] = round(float(data_with_noon[0]['k_1']),2)
    #     data['x1'] = data_with_noon[0]['x_1']
    #     data['x2'] = data_with_noon[0]['x_2']
    #     data['TYPE'] = data_with_noon[0]['type']
    #     data['Vessel_Segment_List'] = data_with_noon[0]['vessel_segment_list']
    #     data['Bench_Mark_Analysis'] = data_with_noon[0]['bench_mark_analysis']

    #     try:
    #         data['imo'] = list(filter(lambda x: x['imo'] == j, vessel_detail))[0]['imo']
    #     except:
    #         data['imo'] = None
    #     try:
    #         data['Name'] = list(filter(lambda x: x['imo'] == j, vessel_detail))[0]['name']
    #     except:
    #         data['Name'] = None
    #     try:
    #         data['Fleet'] = list(filter(lambda x: x['imo'] == j, vessel_detail))[0]['fleet']
    #     except:
    #         data['Fleet'] = None
    #     try:
    #         data['ClassName'] = list(filter(lambda x:x['imo'] == j, vessel_detail))[0]['sister_code']
    #     except:
    #         data['ClassName'] = None
    #     try:
    #         data['DWT'] = float(list(filter(lambda x:x['attribute_id'] == 8 and x['imo'] == j, vessel_detail))[0]['value'])
    #     except:
    #         data['DWT'] = None
    #     try:
    #         data['MCR'] = float(list(filter(lambda x:x['attribute_id'] == 148 and x['imo'] == j, vessel_detail))[0]['value'])
    #     except:
    #         data['MCR'] = None
    #     try:
    #         data['Scantling_Draft'] = float(list(filter(lambda x:x['attribute_id'] == 20 and x['imo'] == j, vessel_detail))[0]['value'])
    #     except:
    #         data['Scantling_Draft'] = None
        
    #     if input=="power":
    #         for i in range(speed,speed + 4):
    #             name = "Power "+str(i)   
    #             try:
    #                 power = round((data['Scantling_Draft']**data['n1'])*(i**data['n2'])*((10-sea_state)**data['n3'])*(np.exp(data['k']))) 
    #             except:
    #                 power = None
    #             data[name] = power
    #     else:
    #         for i in range(speed,speed + 4):
    #             name = "Fuel "+str(i)
    #             try:
    #                 fuel = round((data['Scantling_Draft']**data['n1'])*(i**data['f2'])*((10-sea_state)**data['f3'])*(np.exp(data['k1'])))
                   
    #             except:
    #                 fuel = None
    #             data[name] = fuel
    #     final_data.append(data)

    # return {'data':final_data}




