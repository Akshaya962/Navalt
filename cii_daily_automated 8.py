from scipy.interpolate import interp1d
from fastapi.middleware.cors import CORSMiddleware
from fastapi import  FastAPI,  HTTPException ,Depends
from storage.database_vdm_async import get_vdm_db_async
from authentication.authorization import get_token_async
from operator import itemgetter
from storage import querydata
from sqlalchemy.orm import Session
from storage.database_async import get_db_async
from common.configuration import CACHEKEY
from cache import cache_set, utility
from fastapi.encoders import jsonable_encoder
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sklearn.linear_model import LinearRegression
from datetime import datetime , timedelta ,date
import pandas as pd
import numpy.polynomial as ps
import numpy as np
from starlette.responses import FileResponse
from fastapi import APIRouter
import warnings
warnings.filterwarnings('ignore')



CACHEKEY = CACHEKEY()
router = APIRouter()


router = APIRouter(
      prefix="",
      tags=["cii_daily_script"],
      )



@router.get('/api/v1/cii_daily_automated/')
async def Index(db : AsyncSession = Depends(get_db_async),vdm_db : AsyncSession = Depends(get_vdm_db_async),token : AsyncSession = Depends(get_token_async)):
    print("in api")
    # year = int(datetime.today().year)
    year = 2014
    # vessel = await querydata.get_noondata_for_cii_weeekly(db)
    filter_data = await cache_set.get_all_vdm_vessel_attribute(vdm_db)
    print("after filter_data")
    noondata = await querydata.get_noondata_for_cii_weeekly(db)
    print("after noondata")
    # return noondata
    # vessel_df = pd.DataFrame(vessel)
    data = pd.DataFrame(noondata)
    dead_weight = list(filter(lambda x: x['attribute_id'] == 8 , filter_data))
    vsl_type = list(filter(lambda x: x['attribute_id'] == 4 , filter_data))
    gross_ton = list(filter(lambda x: x['attribute_id'] == 83 , filter_data))


    # data = pd.DataFrame(vessel)
    deadweight = pd.DataFrame(dead_weight)
    gross_tonnage = pd.DataFrame(gross_ton)
    vessel_type = pd.DataFrame(vsl_type)
    vessel_type.loc[vessel_type["value"] == "1", "value"] = 'Container'
    vessel_type.loc[vessel_type["value"] == "2", "value"] = 'Bulk Carrier'
    vessel_type.loc[vessel_type["value"] == "3", "value"] = 'PCTC'
    vessel_type.loc[vessel_type["value"] == "4", "value"] = 'PAX'
    vessel_type.loc[vessel_type["value"] == "5", "value"] = 'ROPAX'
    vessel_type.loc[vessel_type["value"] == "6", "value"] = 'TUG'
    vessel_type.loc[vessel_type["value"] == "7", "value"] = 'RO-RO'
    vessel_type.loc[vessel_type["value"] == "0", "value"] = None

    # print(vessel_df)
    # vessel_df['dwt']
    dead_wt = dict(zip(deadweight['imo'], deadweight['value']))
    vssl_type = dict(zip(vessel_type['imo'], vessel_type['value']))
    gross_tonne = dict(zip(gross_tonnage['imo'], gross_tonnage['value']))
    data['imo'] = data['imo'].astype(str)
    data['deadweight'] = data['imo'].map(dead_wt)
    data['gross_tonnage'] = data['imo'].map(gross_tonne)
    data['vessel_type'] = data['imo'].map(vssl_type)
    data['deadweight'] = pd.to_numeric(data['deadweight'])
    data['gross_tonnage'] = pd.to_numeric(data['gross_tonnage'])
    data = data[(data['report_type'] != 'SND') & (data['report_type'] != 'REFL')].reset_index(drop=True)

    # print(vessel_df)
    print(data)

    def find_a_c(vessel_type, deadweight_or_gross_tonnage):
        print('vessel_type:',vessel_type)
        print('deadweight_or_gross_tonnage:',deadweight_or_gross_tonnage)

        #Finding a and c and capacity for required CII Calculation
        if (vessel_type == "Bulker") & (deadweight_or_gross_tonnage >= 279000):
            capacity = 279000
            a = 4745
            c = 0.622
            return (a, c)
        elif (vessel_type == "Bulker") & (deadweight_or_gross_tonnage < 279000):
            a = 4745
            c = 0.622
            return (a, c)
        elif (vessel_type == "Bulk Carrier") & (deadweight_or_gross_tonnage >= 279000):
            capacity = 279000
            a = 4745
            c = 0.622
            return (a, c)
        elif (vessel_type == "Bulk Carrier") & (deadweight_or_gross_tonnage < 279000):
            a = 4745
            c = 0.622
            return (a, c)
        elif (vessel_type == "Gas Carrier") & (deadweight_or_gross_tonnage >= 65000):
            a = 14405E7
            c = 2.071 
            return (a, c)
        elif (vessel_type == "Gas Carrier") & (deadweight_or_gross_tonnage < 65000):
            a = 8104
            c = 0.639
            return (a, c)
        elif (vessel_type == "Tanker")  :
            a = 5247
            c = 0.610    
            return (a, c)
        elif (vessel_type == "Container") | (deadweight_or_gross_tonnage == "Container Ship") :
            a = 1984
            c = 0.489
            return (a, c)
        elif (vessel_type == "General Cargo Ship") & (deadweight_or_gross_tonnage >= 20000):
            a = 31948
            c = 0.792
            return (a, c)
        elif (vessel_type == "General Cargo Ship") & (deadweight_or_gross_tonnage < 20000):
            a = 588
            c = 0.3885
            return (a, c)
        elif (vessel_type == "Refrigerated Cargo Carrier")  :
            a = 4600
            c = 0.557
            return (a, c)
        elif (vessel_type == "Combination Carrier")  :
            a = 40853
            c = 0.812
            return (a, c)
        elif (vessel_type == "LNG Carrier") & (deadweight_or_gross_tonnage >= 100000):
            a = 9.827
            c = 0
            return (a, c)
        elif (vessel_type == "LNG Carrier") & (deadweight_or_gross_tonnage < 100000) & (deadweight_or_gross_tonnage >= 65000):
            a = 14479E10
            c = 2.673    
            return (a, c)
        elif (vessel_type == "LNG Carrier") & (deadweight_or_gross_tonnage <  65000):
            a = 14479E10
            c = 2.673 
            return (a, c)
        elif (vessel_type == "Ro-Ro Cargo Ship (Vehicle Carrier)") | (vessel_type == "PCTC")   :
            a = 5739
            c = 0.631  
            return (a, c)
        elif (vessel_type == "Ro-Ro Cargo Ship") | (vessel_type == "RO-RO") :
            a = 1967
            c = 0.485
            return (a, c)
        elif (vessel_type == "Ro-Ro Passenger Ship") | (vessel_type == "ROPAX") : 
            a = 7540
            c = 0.587   
            return (a, c)
        elif (vessel_type == "Cruise Passenger Ship")  :
            a = 930
            c = 0.383   
            return (a, c)
        elif (vessel_type == 0) | (vessel_type == None):
            a = 0
            c = 0 
            return (a, c)

    def find_required_cii(a, c, capacity):
        print("a:",type(a))
        print("capacity_value:",capacity)

        print("capacity:",type(capacity))
        print("c:",type(c))

        required_cii_2019 = round(a * capacity ** (-c), 2)    
        required_cii_2020 = round(required_cii_2019 - required_cii_2019 * 0.01, 2)
        required_cii_2021 = round(required_cii_2019 - required_cii_2019 * 0.02, 2)
        required_cii_2022 = round(required_cii_2019 - required_cii_2019 * 0.03, 2)
        required_cii_2023 = round(required_cii_2019 - required_cii_2019 * 0.05, 2)
        required_cii_2024 = round(required_cii_2019 - required_cii_2019 * 0.07, 2)
        required_cii_2025 = round(required_cii_2019 - required_cii_2019 * 0.09, 2)
        required_cii_2026 = round(required_cii_2019 - required_cii_2019 * 0.11, 2)
        required_cii_2027 = round(required_cii_2019 - required_cii_2019 * 0.1375, 2)
        required_cii_2028 = round(required_cii_2019 - required_cii_2019 * 0.165, 2)
        required_cii_2029 = round(required_cii_2019 - required_cii_2019 * 0.1925, 2)
        required_cii_2030 = round(required_cii_2019 - required_cii_2019 * 0.22, 2) 

        return [required_cii_2019, required_cii_2020, required_cii_2021, required_cii_2022,required_cii_2023, required_cii_2024, required_cii_2025, required_cii_2026,
        required_cii_2027, required_cii_2028, required_cii_2029, required_cii_2030]

    def find_vectors(vessel_type, deadweight):
        # Calculation for Vectors 
        if (vessel_type == "Bulker") | (vessel_type == "Bulk Carrier"):
            d1 =  0.86
            d2 =  0.94
            d3 =  1.06
            d4 =  1.18
            return (d1, d2, d3, d4)
        elif (vessel_type == "Gas Carrier") & (deadweight >= 65000):
            d1 =  0.81
            d2 =  0.91
            d3 =  1.12
            d4 =  1.44
            return(d1, d2, d3, d4)
        elif (vessel_type == "Gas Carrier") & (deadweight < 65000):
            d1 =  0.85
            d2 =  0.95
            d3 =  1.06
            d4 =  1.25
            return(d1, d2, d3, d4)
        elif (vessel_type == "Tanker")  :
            d1 =  0.82
            d2 =  0.93
            d3 =  1.08
            d4 =  1.28
            return(d1, d2, d3, d4)
        elif (vessel_type == "Container")  | (vessel_type == "Container Ship")   :
            d1 =  0.83
            d2 =  0.94
            d3 =  1.07
            d4 =  1.19
            return(d1, d2, d3, d4)
        elif (vessel_type == "General Cargo Ship")  :
            d1 =  0.83
            d2 =  0.94
            d3 =  1.07
            d4 =  1.19   
            return(d1, d2, d3, d4)
        elif (vessel_type == "Refrigerated Cargo Carrier")  :
            d1 =  0.78
            d2 =  0.91
            d3 =  1.07
            d4 =  1.20
            return(d1, d2, d3, d4)
        elif (vessel_type == "Combination Carrier")  :
            d1 =  0.87
            d2 =  0.96
            d3 =  1.06
            d4 =  1.14
            return(d1, d2, d3, d4)
        elif (vessel_type == "LNG Carrier") & (deadweight >= 100000):
            d1 =  0.89
            d2 =  0.98
            d3 =  1.06
            d4 =  1.13
            return(d1, d2, d3, d4)
        elif (vessel_type == "LNG Carrier") & (deadweight < 100000)  :
            d1 =  0.78
            d2 =  0.92
            d3 =  1.10
            d4 =  1.37
            return(d1, d2, d3, d4)
        elif (vessel_type == "Ro-Ro Cargo Ship (Vehicle Carrier)") | (vessel_type == "PCTC")   :
            d1 =  0.86
            d2 =  0.94
            d3 =  1.06
            d4 =  1.16
            return(d1, d2, d3, d4)
        elif (vessel_type == "Ro-Ro Cargo Ship")  | (vessel_type == "RO-RO"):
            d1 =  0.76
            d2 =  0.89
            d3 =  1.08
            d4 =  1.27
            return(d1, d2, d3, d4)
        elif (vessel_type == "Ro-Ro Passenger Ship") | (vessel_type == "ROPAX") : 
            d1 =  0.72
            d2 =  0.90
            d3 =  1.12
            d4 =  1.41
            return(d1, d2, d3, d4)
        elif (vessel_type == "Cruise Passenger Ship")  :
            d1 =  0.87
            d2 =  0.95
            d3 =  1.06
            d4 =  1.16  
            return d1, d2, d3, d4 
        elif (vessel_type == 0) |(vessel_type==None) :
            d1 =  0
            d2 =  0
            d3 =  0
            d4 =  0  
            return d1, d2, d3, d4 

    def find_capacity(vessel_type, deadweight_or_gross_tonnage):
        #For Attained CII selecting capacity based on vessel type
        if vessel_type in ["Bulker" ,"Bulk Carrier" , "Combination Carrier" ,
                        "Container", "Container Ship" ,
                        "Gas Carrier" ,  "General Cargo Ship"  , "LNG Carrier"  ,
                        "Refrigerated Cargo Carrier"  , "Ro-Ro Cargo Ship" , 
                        "Tanker"]:
            capacity_attained_calc = deadweight_or_gross_tonnage

            return capacity_attained_calc

        elif vessel_type in ["Cruise Passenger Ship", "Ro-Ro Cargo Ship (Vehicle Carrier)" ,"Ro-Ro Passenger Ship" , 'ROPAX', 'PCTC','RO-RO']:
            capacity_attained_calc = deadweight_or_gross_tonnage
            return capacity_attained_calc
        else:
            return 0


    data['date_time'] = pd.to_datetime(data['report_date_time'])
    
    data['date'] = data['date_time'].dt.date 
    data['month'] = data['date_time'].dt.month 
    data['year'] = data['date_time'].dt.year 
    
    data = data[data['year'] == year]
    # data = data[data['report_type'] != 'SND']

    data = data.sort_values(by=['imo','date'],ascending=True)
    
    # Calculating Fuel
    data = data.fillna(0)
    #Total HS
    data['fuel_me_rsdl_hs'] = pd.to_numeric(data['fuel_me_rsdl_hs'])
    data['fuel_aux_rsdl_hs'] = pd.to_numeric(data['fuel_aux_rsdl_hs'])
    data['fuel_boiler_rsdl_hs'] = pd.to_numeric(data['fuel_boiler_rsdl_hs'])
    data['fuel_aux_rsdl_vls'] = pd.to_numeric(data['fuel_aux_rsdl_vls'])
    data['fuel_boiler_rsdl_vls'] = pd.to_numeric(data['fuel_boiler_rsdl_vls'])
    data['fuel_me_rsdl_uls'] = pd.to_numeric(data['fuel_me_rsdl_uls'])
    data['fuel_aux_rsdl_uls'] = pd.to_numeric(data['fuel_aux_rsdl_uls'])
    data['fuel_boiler_rsdl_uls'] = pd.to_numeric(data['fuel_boiler_rsdl_uls'])
    data['fuel_boiler_ls'] = pd.to_numeric(data['fuel_boiler_ls'])
    data['fuel_me_dstlt_vls'] = pd.to_numeric(data['fuel_me_dstlt_vls'])
    data['fuel_aux_dstlt_vls'] = pd.to_numeric(data['fuel_aux_dstlt_vls'])
    data['fuel_boiler_dstlt_vls'] = pd.to_numeric(data['fuel_boiler_dstlt_vls'])
    data['fuel_me_dstlt_uls'] = pd.to_numeric(data['fuel_me_dstlt_uls'])
    data['fuel_aux_dstlt_uls'] = pd.to_numeric(data['fuel_aux_dstlt_uls'])
    data['fuel_boiler_dstlt_uls'] = pd.to_numeric(data['fuel_boiler_dstlt_uls'])
    data['fuel_me_tnktnr_dstlt_vls'] = pd.to_numeric(data['fuel_me_tnktnr_dstlt_vls'])
    data['fuel_aux_tnktnr_dstlt_vls'] = pd.to_numeric(data['fuel_aux_tnktnr_dstlt_vls'])
    data['fuel_boiler_tnktnr_dstlt_vls'] = pd.to_numeric(data['fuel_boiler_tnktnr_dstlt_vls'])
    data['steaming_time_aux1'] = pd.to_numeric(data['steaming_time_aux1'])
    data['steaming_time_aux2'] = pd.to_numeric(data['steaming_time_aux2'])
    data['steaming_time_aux3'] = pd.to_numeric(data['steaming_time_aux3'])
    data['steaming_time_aux4'] = pd.to_numeric(data['steaming_time_aux4'])
    data['steaming_time_aux5'] = pd.to_numeric(data['steaming_time_aux5'])
    data['fuel_me_rsdl_vls'] = pd.to_numeric(data['fuel_me_rsdl_vls'])
    data['manvrng_miles_by_gps'] = pd.to_numeric(data['manvrng_miles_by_gps'])
    data['miles_by_gps'] = pd.to_numeric(data['miles_by_gps'])




    data['total_hs'] =  data[['fuel_me_rsdl_hs' , 'fuel_aux_rsdl_hs' , 'fuel_boiler_rsdl_hs']].sum(axis=1)
    
    #Total LS
    data['total_ls'] =  data[["fuel_me_rsdl_vls",'fuel_aux_rsdl_vls','fuel_boiler_rsdl_vls','fuel_me_rsdl_uls','fuel_aux_rsdl_uls','fuel_boiler_rsdl_uls']].sum(axis = 1)
    
    #Total ULS
    data['total_uls'] =  data[['fuel_me_dstlt_vls' , 'fuel_aux_dstlt_vls' , 'fuel_boiler_dstlt_vls','fuel_me_dstlt_uls' ,'fuel_aux_dstlt_uls' , 'fuel_boiler_dstlt_uls','fuel_me_tnktnr_dstlt_vls' , 'fuel_aux_tnktnr_dstlt_vls','fuel_boiler_tnktnr_dstlt_vls']].sum(axis=1)
    print(data['total_uls'])
    
    data['total_fuel'] = data[['total_hs' , 'total_ls' , 'total_uls'  ]].sum(axis=1)
    data['status'] = data['status'].ffill().str.replace("DRIFTING", "AT SEA")
 

    data['total_hs_co_2'] = (data["total_hs"])*3.114
    data['total_ls_co_2'] = data["total_ls"]*3.151
    data['total_uls_co_2'] = data["total_uls"]*3.206
    data['total_co_2_for'] = data[['total_hs_co_2', 'total_uls_co_2','total_ls_co_2'] ].sum(axis = 1)  
    
    # Calculating Fuel Consumption
    #Total ME
    data['total_me_fuel'] = data[['fuel_me_rsdl_hs' , 'fuel_me_rsdl_vls','fuel_me_rsdl_uls','fuel_me_dstlt_vls' , 'fuel_me_dstlt_uls' , 'fuel_me_tnktnr_dstlt_vls'  ]].sum(axis=1) 
    #Total LS
    data['total_ae_fuel'] =  data[['fuel_aux_rsdl_hs' , 'fuel_aux_rsdl_vls' , 'fuel_aux_rsdl_uls','fuel_aux_dstlt_vls' , 'fuel_aux_dstlt_uls' , 'fuel_aux_tnktnr_dstlt_vls']].sum(axis=1) 
    #Total Boiler
    data['total_boiler_fuel'] =  data[['fuel_boiler_rsdl_hs' , 'fuel_boiler_rsdl_vls' , 'fuel_boiler_rsdl_uls','fuel_boiler_dstlt_vls', 'fuel_boiler_dstlt_uls' , 'fuel_boiler_tnktnr_dstlt_vls'  ]].sum(axis=1)
    
    data['me_hs_co_2'] = data[['fuel_me_rsdl_hs'   ]].sum(axis=1) *3.114
    data['me_ls_co_2'] = data[['fuel_me_rsdl_vls','fuel_me_rsdl_uls']].sum(axis=1) *3.151
    data['me_uls_co_2'] = data[[ 'fuel_me_dstlt_vls' , 'fuel_me_dstlt_uls' , 'fuel_me_tnktnr_dstlt_vls'  ]].sum(axis=1) *3.206
    
    data['ae_hs_co_2'] = data[['fuel_aux_rsdl_hs'  ]].sum(axis=1) *3.114
    data['ae_ls_co_2'] = data[[ 'fuel_aux_rsdl_vls' , 'fuel_aux_rsdl_uls'  ]].sum(axis=1) *3.151
    data['ae_uls_co_2'] = data[[ 'fuel_aux_dstlt_vls' , 'fuel_aux_dstlt_uls' , 'fuel_aux_tnktnr_dstlt_vls'  ]].sum(axis=1) *3.206
    
    data['boiler_hs_co_2'] = data[['fuel_boiler_rsdl_hs'    ]].sum(axis=1)*3.114
    data['boiler_ls_co_2'] = data[[  'fuel_boiler_rsdl_vls' , 'fuel_boiler_rsdl_uls'  ]].sum(axis=1)*3.151
    data['boiler_uls_co_2'] = data[[ 'fuel_boiler_dstlt_vls' , 'fuel_boiler_dstlt_uls' , 'fuel_boiler_tnktnr_dstlt_vls'  ]].sum(axis=1)*3.206
    
    data['total_me_co_2'] = data[['me_hs_co_2' , 'me_ls_co_2', 'me_uls_co_2'] ].sum(axis = 1)
    data['total_ae_co_2'] = data[['ae_hs_co_2' , 'ae_ls_co_2', 'ae_uls_co_2'] ].sum(axis = 1)
    data['total_boiler_co_2'] = data[['boiler_hs_co_2' , 'boiler_ls_co_2', 'boiler_uls_co_2'] ].sum(axis = 1)
    data['total_aux_engine_time'] =   data[['steaming_time_aux1','steaming_time_aux2','steaming_time_aux3','steaming_time_aux4','steaming_time_aux5']].sum(axis = 1)
    
    data['miles_by_gps'] = np.where(data['miles_by_gps'] != data['manvrng_miles_by_gps'], data['miles_by_gps'] + data['manvrng_miles_by_gps'],data['miles_by_gps'])
    data['total_hs'] = pd.to_numeric(data['total_hs'])
    data['total_ls'] = pd.to_numeric(data['total_ls'])
    data['total_uls'] = pd.to_numeric(data['total_uls'])
    data['total_fuel'] = pd.to_numeric(data['total_fuel'])
    data['total_hs_co_2'] = pd.to_numeric(data['total_hs_co_2'])
    data['total_ls_co_2'] = pd.to_numeric(data['total_ls_co_2'])
    data['total_uls_co_2'] = pd.to_numeric(data['total_uls_co_2'])
    data['total_co_2_for'] = pd.to_numeric(data['total_co_2_for'])
    data['total_me_fuel'] = pd.to_numeric(data['total_me_fuel'])
    data['total_ae_fuel'] = pd.to_numeric(data['total_ae_fuel'])
    data['total_boiler_fuel'] = pd.to_numeric(data['total_boiler_fuel'])
    data['me_hs_co_2'] = pd.to_numeric(data['me_hs_co_2'])
    data['me_ls_co_2'] = pd.to_numeric(data['me_ls_co_2'])
    data['me_uls_co_2'] = pd.to_numeric(data['me_uls_co_2'])
    data['ae_hs_co_2'] = pd.to_numeric(data['ae_hs_co_2'])
    data['ae_ls_co_2'] = pd.to_numeric(data['ae_ls_co_2'])
    data['ae_uls_co_2'] = pd.to_numeric(data['ae_uls_co_2'])
    data['boiler_hs_co_2'] = pd.to_numeric(data['boiler_hs_co_2'])
    data['boiler_ls_co_2'] = pd.to_numeric(data['boiler_ls_co_2'])
    data['boiler_uls_co_2'] = pd.to_numeric(data['boiler_uls_co_2'])
    data['total_me_co_2'] = pd.to_numeric(data['total_me_co_2'])
    data['miles_by_gps'] = pd.to_numeric(data['miles_by_gps'])
    data['total_steaming_time'] = pd.to_numeric(data['total_steaming_time'])
    data['total_aux_engine_time'] = pd.to_numeric(data['total_aux_engine_time'])
    data['stw'] = pd.to_numeric(data['speed_by_log'])
    data['sog'] = pd.to_numeric(data['speed_by_gps'])
    data['rpm'] = pd.to_numeric(data['rpm'])
    data['slip'] = pd.to_numeric(data['slip'])
    data['wind_direction'] = pd.to_numeric(data['wind_direction'])
    data['draft_aft'] = pd.to_numeric(data['draft_aft'])
    data['draft_fwd'] = pd.to_numeric(data['draft_fwd'])
    data['displacement'] = pd.to_numeric(data['displacement'])
    data['course_at_sea'] = pd.to_numeric(data['course_at_sea'])
    data['deadweight'] = pd.to_numeric(data['deadweight'])
    data['draft'] = pd.to_numeric(data['draft'])
    data['wind_speed'] = pd.to_numeric(data['wind_speed'])
    data['total_boiler_co_2'] = pd.to_numeric(data['total_boiler_co_2'])
    data['reefers_positive_plugged'] = pd.to_numeric(data['reefers_positive_plugged'])
    data['reefers_negative_plugged'] = pd.to_numeric(data['reefers_negative_plugged'])
    data = data.reset_index()
    if (data['vessel_type'] == 'Container').any():
    # new 2023 calculation
        data['total_reefers'] = data[['reefers_positive_plugged', 'reefers_negative_plugged']].sum(axis = 1)
        data['total_reefers'] =pd.to_numeric(data['total_reefers']).ffill().bfill()
        # print("in line 435")
        # print(data)
        # print(data['status'])
        # print(data['total_reefers'])

        for i , j, k in zip(data.index, data['status'], data['total_reefers']):
            print('i:',i)
            if i < (len(data) - 1 ):
                # print("in if condition")
                if (j == 'AT SEA')  :
                    data.loc[i , 'arr_dep_status'] = 'AT SEA'
                elif (j == 'IN PORT') & (data.loc[abs(i-1), 'status'] == 'AT SEA') & (data.loc[i+1, 'status'] == 'IN PORT'):
                    data.loc[i, 'arr_dep_status'] = 'ARRIVAL'
                elif (j == 'IN PORT') & (data.loc[abs(i-1), 'status'] == 'AT SEA') & (data.loc[i+1, 'status'] == 'AT SEA'):
                    data.loc[i, 'arr_dep_status'] = 'ARRIVAL/DEPARTURE'
                elif (j == 'IN PORT') & (data.loc[abs(i-1), 'status'] == 'IN PORT') & (data.loc[i+1, 'status'] == 'IN PORT'):
                    data.loc[i, 'arr_dep_status'] = 'IN PORT'
                elif (j == 'IN PORT') & (data.loc[abs(i-1), 'status'] == 'IN PORT') & (data.loc[i+1, 'status'] == 'AT SEA'):
                    data.loc[i, 'arr_dep_status'] = 'DEPARTURE'
        for i, j, k in zip(data.index, data['arr_dep_status'], data['total_reefers']):
            if (j == "AT SEA") :
                data.loc[i, 'new_reefers'] = k
            elif j == 'ARRIVAL':
                # Look for next departure data
                for l, m, n in zip(data.loc[i+1: , :].index, data.loc[i+1:   ,'arr_dep_status'], data.loc[i+1:,'total_reefers']):
                    if m == 'DEPARTURE':
                        data.loc[i : l+1, 'new_reefers'] = (k+n)/2
                        break
                    else:
                        pass
            elif j == 'ARRIVAL/DEPARTURE':
                # Look for next departure data
                for l, m, n in zip(data.loc[i-1: , :].index, data.loc[i:   ,'arr_dep_status'], data.loc[i-1:   ,'total_reefers']):
                    # print(j,l,m,n,k)
                    if m == 'ARRIVAL/DEPARTURE':
                        data.loc[i : l+1, 'new_reefers'] =(k+n)/2
                        break
                    else:
                        pass
        data['reefer_fuel'] = 2.75 * 24 *190* data[ 'new_reefers']/1000000
        data['hs_reefers'] = data['reefer_fuel'] * data['total_hs'] / data['total_fuel'] 
        data['ls_reefers'] = data['reefer_fuel'] * data['total_ls'] / data['total_fuel'] 
        data['uls_reefers'] = data['reefer_fuel'] * data['total_uls'] / data['total_fuel']
        data['hs_co2_reefers'] = data['hs_reefers'] *   3.114 * 0.75
        data['ls_co2_reefers'] = data['ls_reefers'] *   3.151 * 0.75
        data['uls_co2_reefers'] = data['uls_reefers'] * 3.206 * 0.75

        data['total_co2_reefers'] = data[['hs_co2_reefers' , 'ls_co2_reefers' , 'uls_co2_reefers']].sum(axis = 1)
    
        data['Total_co_2']   = abs(data['total_co_2_for']  -  pd.to_numeric(data['total_co2_reefers'])) 
    else:
        data['Total_co_2'] =data['total_co_2_for']

    df_group_day = data.groupby(['imo','vessel_type','date']).agg({'total_hs': np.sum,'total_ls': np.sum,'total_uls': np.sum,'total_fuel': np.sum,'total_hs_co_2': np.sum,'total_ls_co_2': np.sum,'total_uls_co_2': np.sum,'total_me_fuel': np.sum,'total_ae_fuel': np.sum,'total_boiler_fuel': np.sum,'me_hs_co_2': np.sum,'me_ls_co_2': np.sum,'me_uls_co_2': np.sum,'ae_hs_co_2': np.sum,'ae_ls_co_2': np.sum,'ae_uls_co_2': np.sum,'boiler_hs_co_2': np.sum,'boiler_ls_co_2': np.sum,'boiler_uls_co_2': np.sum,'total_me_co_2': np.sum,'total_ae_co_2': np.sum,'total_boiler_co_2': np.sum,'miles_by_gps': np.sum,'total_steaming_time': np.sum,'total_aux_engine_time' : np.sum,'stw':np.mean,'sog':np.mean,'wind_speed':np.mean,'rpm' :np.mean ,'slip':np.mean,'wind_direction':np.mean,'draft_aft':np.mean,'draft_fwd' :np.mean ,'displacement':np.mean,'course_at_sea':np.mean,  'deadweight':np.mean,'draft':np.mean,'gross_tonnage':np.mean,'Total_co_2':np.sum})
    print('after grpby')
    print(df_group_day)
    df_group_day1 = df_group_day.fillna(0).round(2).reset_index()

    final_df = pd.DataFrame()

    
    for  enum,i in enumerate(df_group_day1['imo'].unique()):
        
        # vessel_type = data[data['imo'] == i]['vessel_type'].values[0]
        vessel_type = df_group_day1[df_group_day1['imo'] == i]['vessel_type'].values[0]
        df_group_day1.loc[df_group_day1['vessel_type'].isin(['ROPAX', 'PCTC','RO-RO']), 'deadweight'] = df_group_day1['gross_tonnage']

        deadweight_or_gross_tonnage = df_group_day1[df_group_day1['imo'] == i]['deadweight'].values[0]

        gross_tonnage_rop_pctc = df_group_day1[df_group_day1['imo'] == i]['gross_tonnage'].values[0]


        dft = df_group_day1[df_group_day1['imo'] == i]
        print("imo:",i)
        df1 = dft.sort_values("date")


        df1['attained_cii'] = df1['Total_co_2']*1E6/(df1['deadweight'] * df1['miles_by_gps']* 1 )
        df1['attained_cii']  = df1['attained_cii'].apply(lambda x : round(x, 2))
        
        df1['current_cii'] = 0
        for i, j, k in zip(df1.index, df1['Total_co_2'].abs(), df1['miles_by_gps'],):
            df1.loc[i, 'current_cii'] =  round((df1.loc[ :i  ,'Total_co_2'].sum()*1E6/((  df1.loc[ :i  ,'deadweight'].mean()   * df1.loc[ :i  ,'miles_by_gps'].sum())*1) ), 2)
    
        df1['date'] = pd.to_datetime(df1['date'], dayfirst = True)

        mydf = df1

        mydf['date'] = pd.to_datetime(mydf['date'], dayfirst = True)
        df_group_weekly3 =  mydf.sort_values('date').copy()    #mydf[mydf['miles_by_gps'] > 0]
        
        # Finding Capacity of Vessel
        capacity = find_capacity(vessel_type, deadweight_or_gross_tonnage )
#         print(capacity)


        # Finding Constants
        a, c = find_a_c(vessel_type, deadweight_or_gross_tonnage ) 
#         print(a)
#         print(c)


        #Finding Required CII
        required_cii_data = find_required_cii(a, c, capacity)
#         print(required_cii_data)


        # Find Vectors
        d1, d2, d3, d4 = find_vectors(vessel_type, deadweight_or_gross_tonnage)
#         print((d1, d2, d3, d4))
    
        df_group_weekly3["CII_Rating_2019"] = ''
        df_group_weekly3["CII_Rating_2020"] = ''
        df_group_weekly3["CII_Rating_2021"] = ''
        df_group_weekly3["CII_Rating_2022"] = ''
        df_group_weekly3["CII_Rating_2023"] = ''
        df_group_weekly3["cii_rating"] = ''
        # Rating CII
    
        if year == 2019:
            required_cii = required_cii_data[0]
            
            df_group_weekly3['required_cii'] = float(required_cii_data[0])
            for i, attained_value  in zip(df_group_weekly3.index,  df_group_weekly3['attained_cii'].values):
                if attained_value/required_cii  <= d1:
                    df_group_weekly3.loc[i, "CII_Rating_2019"] = "A"
                    df_group_weekly3.loc[i, "cii_rating"] = "A"
                elif (attained_value/required_cii > d1) & (attained_value/required_cii <= d2):
                    df_group_weekly3.loc[i, "CII_Rating_2019"] = "B"
                    df_group_weekly3.loc[i, "cii_rating"] = "B"
                elif (attained_value/required_cii > d2) & (attained_value/required_cii <= d3):
                    df_group_weekly3.loc[i, "CII_Rating_2019"] = "C"
                    df_group_weekly3.loc[i, "cii_rating"] = "C"
                elif (attained_value/required_cii > d3) & (attained_value/required_cii <= d4):
                    df_group_weekly3.loc[i, "CII_Rating_2019"] = "D"
                    df_group_weekly3.loc[i, "cii_rating"] = "D"
                elif (attained_value/required_cii > d4) :
                    df_group_weekly3.loc[i, "CII_Rating_2019"] = "E" 
                    df_group_weekly3.loc[i, "cii_rating"] = "E"




        if year == 2020:
            required_cii = required_cii_data[1]
            
            df_group_weekly3['required_cii'] = float(required_cii_data[1])
            
#             print('required_cii_2020', required_cii)
            for i, attained_value  in zip(df_group_weekly3.index,  df_group_weekly3['attained_cii'].values):
                if attained_value/required_cii  <= d1:
                    df_group_weekly3.loc[i, "CII_Rating_2020"] = "A"
                    df_group_weekly3.loc[i, "cii_rating"] = "A"
                elif (attained_value/required_cii > d1) & (attained_value/required_cii <= d2):
                    df_group_weekly3.loc[i, "CII_Rating_2020"] = "B"
                    df_group_weekly3.loc[i, "cii_rating"] = "B"
                elif (attained_value/required_cii > d2) & (attained_value/required_cii <= d3):
                    df_group_weekly3.loc[i, "CII_Rating_2020"] = "C"
                    df_group_weekly3.loc[i, "cii_rating"] = "C"
                elif (attained_value/required_cii > d3) & (attained_value/required_cii <= d4):
                    df_group_weekly3.loc[i, "CII_Rating_2020"] = "D"
                    df_group_weekly3.loc[i, "cii_rating"] = "D"
                elif (attained_value/required_cii > d4) :
                    df_group_weekly3.loc[i, "CII_Rating_2020"] = "E" 
                    df_group_weekly3.loc[i, "cii_rating"] = "E"




        if year == 2021:
            required_cii = required_cii_data[2]
            
            df_group_weekly3['required_cii'] = float(required_cii_data[2])
            
            
            for i, attained_value  in zip(df_group_weekly3.index,  df_group_weekly3['attained_cii'].values):
                if attained_value/required_cii  <= d1:
                    df_group_weekly3.loc[i, "CII_Rating_2021"] = "A"
                    df_group_weekly3.loc[i, "cii_rating"] = "A"
                elif (attained_value/required_cii > d1) & (attained_value/required_cii <= d2):
                    df_group_weekly3.loc[i, "CII_Rating_2021"] = "B"
                    df_group_weekly3.loc[i, "cii_rating"] = "B"
                elif (attained_value/required_cii > d2) & (attained_value/required_cii <= d3):
                    df_group_weekly3.loc[i, "CII_Rating_2021"] = "C"
                    df_group_weekly3.loc[i, "cii_rating"] = "C"
                elif (attained_value/required_cii > d3) & (attained_value/required_cii <= d4):
                    df_group_weekly3.loc[i, "CII_Rating_2021"] = "D"
                    df_group_weekly3.loc[i, "cii_rating"] = "D"
                elif (attained_value/required_cii > d4) :
                    df_group_weekly3.loc[i, "CII_Rating_2021"] = "E" 
                    df_group_weekly3.loc[i, "cii_rating"] = "E"



        if year == 2022:
            required_cii = required_cii_data[3]
            
            df_group_weekly3['required_cii'] = float(required_cii_data[3])
            
            for i, attained_value  in zip(df_group_weekly3.index,  df_group_weekly3['attained_cii'].values):
                if attained_value/required_cii  <= d1:
                    df_group_weekly3.loc[i, "CII_Rating_2022"] = "A"
                    df_group_weekly3.loc[i, "cii_rating"] = "A"
                elif (attained_value/required_cii > d1) & (attained_value/required_cii <= d2):
                    df_group_weekly3.loc[i, "CII_Rating_2022"] = "B"
                    df_group_weekly3.loc[i, "cii_rating"] = "B"
                elif (attained_value/required_cii > d2) & (attained_value/required_cii <= d3):
                    df_group_weekly3.loc[i, "CII_Rating_2022"] = "C"
                    df_group_weekly3.loc[i, "cii_rating"] = "C"
                elif (attained_value/required_cii > d3) & (attained_value/required_cii <= d4):
                    df_group_weekly3.loc[i, "CII_Rating_2022"] = "D"
                    df_group_weekly3.loc[i, "cii_rating"] = "D"
                elif (attained_value/required_cii > d4) :
                    df_group_weekly3.loc[i, "CII_Rating_2022"] = "E" 
                    df_group_weekly3.loc[i, "cii_rating"] = "E"
                    
        if year == 2023:
            required_cii = required_cii_data[4]
            
            df_group_weekly3['required_cii'] = float(required_cii_data[4])
            
            
            for i, attained_value  in zip(df_group_weekly3.index,  df_group_weekly3['attained_cii'].values):
                if attained_value/required_cii  <= d1:
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "A"
                    df_group_weekly3.loc[i, "cii_rating"] = "A"
                elif (attained_value/required_cii > d1) & (attained_value/required_cii <= d2):
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "B"
                    df_group_weekly3.loc[i, "cii_rating"] = "B"
                elif (attained_value/required_cii > d2) & (attained_value/required_cii <= d3):
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "C"
                    df_group_weekly3.loc[i, "cii_rating"] = "C"
                elif (attained_value/required_cii > d3) & (attained_value/required_cii <= d4):
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "D"
                    df_group_weekly3.loc[i, "cii_rating"] = "D"
                elif (attained_value/required_cii > d4) :
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "E" 
                    df_group_weekly3.loc[i, "cii_rating"] = "E"
                    
        if year == 2024:
            required_cii = required_cii_data[5]
            
            df_group_weekly3['required_cii'] = float(required_cii_data[5])
            
            
            for i, attained_value  in zip(df_group_weekly3.index,  df_group_weekly3['attained_cii'].values):
                if attained_value/required_cii  <= d1:
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "A"
                    df_group_weekly3.loc[i, "cii_rating"] = "A"
                elif (attained_value/required_cii > d1) & (attained_value/required_cii <= d2):
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "B"
                    df_group_weekly3.loc[i, "cii_rating"] = "B"
                elif (attained_value/required_cii > d2) & (attained_value/required_cii <= d3):
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "C"
                    df_group_weekly3.loc[i, "cii_rating"] = "C"
                elif (attained_value/required_cii > d3) & (attained_value/required_cii <= d4):
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "D"
                    df_group_weekly3.loc[i, "cii_rating"] = "D"
                elif (attained_value/required_cii > d4) :
                    df_group_weekly3.loc[i, "CII_Rating_2023"] = "E" 
                    df_group_weekly3.loc[i, "cii_rating"] = "E"
                    

        df_group_weekly4 = df_group_weekly3   #[df_group_weekly3['attained_cii'] < 15]
        print(type(final_df))
        # final_df = final_df.append(df_group_weekly4, ignore_index=True)
        final_df = pd.concat([final_df, df_group_weekly4], ignore_index=True)
#         print("Enum", enum)

        if len(final_df) == 0:
            print("Zero Printed")
    print(final_df)
    print(final_df['vessel_type'])

    final_df['c_r'] = round(pd.to_numeric(final_df['current_cii'])/pd.to_numeric(final_df['required_cii']),2)
    final_df['a_r'] = final_df['attained_cii']/(final_df['required_cii'])   



    #rating
    def rating(y,z):
        if z=='Container':
            if y>=0 and y<=0.83:
                return "A"
            elif y>0.83 and y<=0.94:
                return "B"
            elif y>0.94 and y<=1.07:
                return "C"
            elif y>1.07 and y<=1.19:
                return "D"
            else:
                return "E"
        elif z=='ROPAX':
            if y>=0 and y<=0.72:
                return "A"
            elif y>0.72 and y<=0.90:
                return "B"
            elif y>0.90 and y<=1.12:
                return "C"
            elif y>1.12 and y<=1.41:
                return "D"
            else:
                return "E"
        elif z=='Bulk Carrier':
            if y>=0 and y<=0.86:
                return "A"
            elif y>0.86 and y<=0.94:
                return "B"
            elif y>0.94 and y<=1.06:
                return "C"
            elif y>1.06 and y<=1.18:
                return "D"
            else:
                return "E"
        elif z=='PCTC':  
            if y>=0 and y<=0.86:
                return "A"
            elif y>0.86 and y<=0.94:
                return "B"
            elif y>0.94 and y<=1.06:
                return "C"
            elif y>1.06 and y<=1.16:
                return "D"
            else:
                return "E"
        else:
            pass

    
    final_df['current_cii_rating'] = final_df.apply(lambda x: rating(x.c_r,x.vessel_type), axis=1)
    print(final_df)
    # final_df['current_cii_rating'] = 
    final_df.rename(columns= {
        'imo' : 'imo',
        'vessel_type' : 'vessel_type',
        'date' : 'date',
        'total_hs' : 'total_hs',
        'total_ls' : 'total_ls',
        'total_uls' : 'total_uls',
        'Total_Fuel' : 'total_fuel',
        'total_hs_co_2' : 'total_hs_co_2',
        'total_ls_co_2' : 'total_ls_co_2',
        'total_uls_co_2' : 'total_uls_co_2',
        'Total_co_2' : 'total_co_2',
        'total_me_fuel' : 'total_me_fuel',
        'total_ae_fuel' : 'total_ae_fuel',
        'total_boiler_fuel' : 'total_boiler_fuel',
        'me_hs_co_2' : 'me_hs_co_2',
        'me_ls_co_2' : 'me_ls_co_2',
        'me_uls_co_2' : 'me_uls_co_2',
        'ae_hs_co_2' : 'ae_hs_co_2',
        'ae_ls_co_2' : 'ae_ls_co_2',
        'ae_uls_co_2' : 'ae_uls_co_2',
        'boiler_hs_co_2' : 'boiler_hs_co_2',
        'boiler_ls_co_2' : 'boiler_ls_co_2',
        'boiler_uls_co_2' : 'boiler_uls_co_2',
        'total_me_co_2' : 'total_me_co_2',
        'total_aux_co_2' : 'total_aux_co_2',
        'total_boiler_co2' : 'total_boiler_co_2',
        'miles_by_gps' : 'miles_by_gps',
        'total_steaming_time' : 'steaming_time',
        'total_aux_engine_time' : 'total_aux_engine_time',
        'stw' : 'speed_by_log',
        'sog' : 'speed_by_gps',
        'wind_speed_kn' : 'wind_speed',
        'rpm' : 'rpm',
        'slip' : 'slip',
        'wind_direction' : 'wind_direction',
        'draft_aft' : 'draft_aft',
        'draft_fwd' : 'draft_fwd',
        'displacement' : 'displacement',
        'course_at_sea' : 'course_at_sea',
        'deadweight' : 'dwt',
        'draft' : 'draft',
        'attained_cii' : 'attained_cii',
        'current_cii' : 'current_cii',
        'CII_Rating_2019' : 'CII_Rating_2019',
        'CII_Rating_2020' : 'CII_Rating_2020',
        'CII_Rating_2021' : 'CII_Rating_2021',
        'CII_Rating_2022' : 'CII_Rating_2022',
        'CII_Rating_2023' : 'CII_Rating_2023',
        'cii_rating' : 'cii_rating',
        'required_cii' : 'required_cii',
    },inplace = True)
    final_df.drop('CII_Rating_2019',inplace = True ,axis = 1)
    final_df.drop('CII_Rating_2020',inplace = True ,axis = 1)
    final_df.drop('CII_Rating_2021',inplace = True ,axis = 1)
    final_df.drop('CII_Rating_2022',inplace = True ,axis = 1)
    final_df.drop('CII_Rating_2023',inplace = True ,axis = 1)
    # final_df.drop('total_aux_co_2', inplace=True, axis=1)x
    final_df.drop('draft',inplace = True ,axis = 1)
    
    filename = 'MSC_Daily_CII_data_for_nihal.csv'
    data1 = final_df.to_csv(filename, index=False, encoding='utf-8')
    # data = final_df.to_json(orient="records")
    # finaldata = json.loads(data)
    return 'done'









