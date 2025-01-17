import requests
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
import logging
import sys
import uuid
import json
import pandas as pd
import numpy as np
from storage import querydata
from cache import cache_set  # Import necessary modules
from common.configuration import POSTGRESDB, RINA_ADA
import threading
from storage.database import engine
RINA_ADA = RINA_ADA()


# if(validated=true,0,1): validate
# if(outlier=true,0,1): outlier
# if(outlier=true& validated=true ,0,1): ISO19030_Validation
# if(me_mdo_in_use=true,ME_Total_Cons_t,0): ME_MDO_Fuel_Cons_t
# if(me_hfo_in_use=true,ME_Total_Cons_t,0): ME_HFO_HS_Fuel_Cons_t
# if(dg_mdo_in_use=true,DG_Total_Fuel_Cons_t,0): DG_MDO_Fuel_Cons_t
# if(dg_hfo_in_use=true,DG_Total_Fuel_Cons_t,0): DG_HFO_HS_Fuel_Cons_t
mapped = {
    'heading': 'HEAD_deg',
    'wind_speed_model': 'Model_Wind_Speed_Apparent_kn',
    'wind_speed': 'Sensor_Wind_Speed_Apparent_kn',
    'wind_rel_dir_model': 'Model_Wind_Dir_Apparent',
    'wind_dir': 'Sensor_Wind_Dir_Apparent',
    'voyage_phase': 'Phase',
    'speed_through_water': 'STW_kn',
    'speed_over_ground': 'SOG_kn',
    'sg1_run': 'SG_Running',
    'sea_state_doug_model': 'Model_Sea_State_D',
    'sea_curr_rel_dir_model': 'Model_Sea_Dir_Apparent',
    'sea_curr_force_model': 'Model_Current_Force_True_kn',
    'wave_hgt_model': 'Significant_Wave_Height',
    'me_sfoc_cur_total': 'SFOC_g_kWh',
    'draft_fore': 'Draft_Fore_m',
    'draft_aft': 'Draft_Aft_m',
    'dg4_run': 'Run_DG4',
    'dg4_pow': 'Pow_DG4_kW',
    'dg3_run': 'Run_DG3',
    'dg3_pow': 'Pow_DG3_kW',
    'dg2_run': 'Run_DG2',
    'dg2_pow': 'Pow_DG2_kW',
    'dg1_run': 'Run_DG1',
    'dg1_pow': 'Pow_DG1_kW',
    'dg_total_pow': 'DG_Average_Power_kW',
    'dg_run_count': 'DG_Running',
    'course_over_ground': 'COG_deg',
    'me_total_pow': 'Shaft_Power_kW',
    'area_seca': 'area_seca',
    'seca_mode': 'seca_mod',
    'latitude': 'Latitude',
    'longitude': 'Longitude'
}

no_direct_mapping = [
    'ts', # 'Date_Hour'
    'validated',
    'outlier',
    'ship_id', #vesselname -> join to get IdShip
    'prop1_slip',
    'prop2_slip',
    # Avergae(prop1_slip ,prop2_slip )': Apparent_Slip
    'dg_total_flowmeter', # /1000*(period/60): DG_Total_Fuel_Cons_t
    'me_total_flowmeter', # /1000*(period/60): ME_Total_Cons_t
    # 'me_total_flowmeter', #/1000: ME_Consumption_per_hour
    # me_sox_flw1+dg_sox_flw1+bo_sox_flw1: SOx_t_h
    'me_sox_flw1',
    'dg_sox_flw1',
    'bo_sox_flw1',
    'bo_total_flowmeter', # /1000: Boiler_Consumption_per_hour_Kg_h
    'prop1_rpm',
    'prop2_rpm',
    # Average(prop1_rpm,prop2_rpm): RPM
    'me_nox_flw1',
    'dg_nox_flw1'
    # (me_nox_flw1+dg_nox_flw1)/1000: NOx_t_h 
]

"""
UId
Displacement_t
Tons_of_Cargo_t
MCR
ME_HFO_LS_Fuel_Cons_t
ME_MGO_Fuel_Cons_t
ME_MGO_LS_Fuel_Cons_t
DG_HFO_LS_Fuel_Cons_t
DG_MGO_Fuel_Cons_t
DG_MGO_LS_Fuel_Cons_t
Boiler_Group_Running
Incinerator_Consumption_per_hour_Kg_h
Incinerator_Group_Running
filter
Corrected_Power
P_I
Ref_speed
CAA
"""





def get_adadata_insertion(db, vdm_db):
    #db = get_db_w()
    #db = next(db)
    
    #vdm_db = get_vdm_db()
    #vdm_db = next(vdm_db)
    try:
        print("process start...")
        #----------------------------------------------------------------------------------------------------------------------
        logging.basicConfig(filename='rina_api.log',
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%d-%b-%y %H-%M-%S',
                            level=logging.INFO)
        print("1")

        # username = POSTGRESDB.
        # password = POSTGRESDB.PASSWORD

        api_user = RINA_ADA.RINA_ADA_API_USER
        api_password = RINA_ADA.RINA_ADA_API_PASSWORD

        #-------------------------------------------------------------------------------------------------------------------------

        # if date:
            
        #     date = datetime.strptime(date , '%Y-%m-%d')
        # else:
        date = datetime.today()
        today_date = datetime.today()


        epoch = datetime.utcfromtimestamp(0)

        make_timestamp = lambda x: int((x - epoch).total_seconds() * 1000)
        print("Taking Vessel Data")
        # vessels = querydata.get_vdm_vessel_data_for_scripts(vdm_db)
        vessel_detail = cache_set.get_mcr_filter(vdm_db)
        # idd = querydata.get_adadata_id(db)
        # idd = json.dumps(jsonable_encoder(idd))
        # idd = json.loads(idd)
        # print("idd",idd)
        
        vessel_list_fleet= [i['imo'] for i in vessel_detail]
        vessel_list_fleet = set(vessel_list_fleet)
        imo_list = list(vessel_list_fleet)
        print("Completed")

        f = open('stub/ada_data_vessels_list.json')
        adadata_vessels = json.load(f)
        

        def get_access_token():
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            ## Modified 'grant_type' in client_credentials
            # body = {'grant_type': 'client_credentials',
            #         'client_id': f'{api_user}',
            #         'client_secret': f'{api_key}'}
            body =  {"grant_type":"password","client_id":"optimum","username":api_user,"password":api_password}
            r = requests.post("https://login.cube.rina.org/auth/realms/cube/protocol/openid-connect/token",
                            data=body,
                            headers=headers)
            r = json.loads(r.text)
            access_token = r['access_token']
            return access_token


        def insert_data():
            print("Getting Id")
            idd = querydata.get_adadata_id(db)
            idd = idd.id
            print(idd,"idd") 
            # Calculate period
            # epoch = datetime.utcfromtimestamp(0)
            # make_timestamp = lambda x: int((x - epoch).total_seconds() * 1000)
            start = make_timestamp(date - timedelta(days=1))
            end = make_timestamp(date)
            
            #Get Fields
            fields = list(mapped.keys())
            fields.extend(no_direct_mapping)

            #Get Vessels
            

            #For each vessel
            for vessel in imo_list:
                
                print(vessel)
                if not vessel:
                    continue
                
                token = get_access_token()

                # Prepare POST request Body
                body = {}
                body["filters"] = []
                body["steady_conditions"] = []
                body["periods"] = [[start,end]]
                # body["aggregation"] = "5m"
                body["fields"] = fields
                body["sort"] = [{"field":"ts","order":"asc"}]
                #Prepare POST request Headers
                headers = {'Content-type': 'application/json', 'x-company': 'MSC', 'x-solution': 'OPTIMUM', 'Authorization': 'Bearer ' + token}
                #Prepate POST request URL
                # return 0
                url = f"https://api-gw.cube.rina.org/api/v2/assets/{vessel}/data"

                #Send POST request
                r = requests.post(url,
                                data=json.dumps(body),
                                headers=headers)
                print("Url")
                print("url:",url)

                json_response = json.loads(r.text)
                # print(json_response["data"]["values"])
                # exit()
            
                try:
                    df = pd.DataFrame(json_response["data"]["values"], columns = json_response["data"]["fields"])
                except Exception as e:
                    print(r)
                    print('----------')
                    print('exiting -> response parsing error')
                    logging.error(str(e))
                    print("!!!!")
                    print(vessel)
                    print("!!!!")

                    if int(vessel) not in adadata_vessels:
                        continue
                    # continue

                #Process response
                if df.empty:
                    print("Contiune")
                    continue
                df = df.replace(np.nan, None)
                if int(vessel) not in adadata_vessels:
                    print("Adding a new vessel in adadata vessel list :" , vessel)
                    adadata_vessels.append(vessel)
                    with open("vessels_list.json", "w") as file:
                        file.write(json.dumps(adadata_vessels))

                print(vessel)
                for datapoint in df.itertuples():
                    print("In For Loop")
                    insertion_dict = {}
                    insertion_dict['imo'] = vessel
                    Latitude = getattr(datapoint, 'latitude', None)
                    Longitude = getattr(datapoint, 'longitude', None)
                    insertion_dict['latitude'] = Latitude
                    insertion_dict['longitude'] = Longitude
                    validation = getattr(datapoint, 'validation', None)
                    prop1_slip = getattr(datapoint, 'prop1_slip', None)
                    prop2_slip = getattr(datapoint, 'prop2_slip', None)
                    me_sox_flw1 = getattr(datapoint, 'me_sox_flw1', None)
                    dg_sox_flw1 = getattr(datapoint, 'dg_sox_flw1', None)
                    bo_sox_flw1 = getattr(datapoint, 'bo_sox_flw1', None)
                    bo_total_flowmeter = getattr(datapoint, 'bo_total_flowmeter', None)
                    prop1_rpm = getattr(datapoint, 'prop1_rpm', None)
                    prop2_rpm = getattr(datapoint, 'prop2_rpm', None)
                    me_nox_flw1 = getattr(datapoint, 'me_nox_flw1', None)
                    dg_nox_flw1 = getattr(datapoint, 'dg_nox_flw1', None)
                    me_total_flowmeter = getattr(datapoint, 'me_total_flowmeter', None)
                    dg_total_flowmeter = getattr(datapoint, 'dg_total_flowmeter', None)
                    me_total_cons_t = None
                    me_mdo_in_use = getattr(datapoint, 'me_mdo_in_use', None)
                    me_hfo_in_use = getattr(datapoint, 'me_hfo_in_use', None)
                    dg_mdo_in_use = getattr(datapoint, 'dg_mdo_in_use', None)
                    dg_hfo_in_use = getattr(datapoint, 'dg_hfo_in_use', None)
                    me_total_pow = getattr(datapoint, 'me_total_pow', None)
                    draft_fore = getattr(datapoint, 'draft_fore', None)
                    draft_aft = getattr(datapoint, 'draft_aft', None)

                    if validation:
                        insertion_dict['iso_19030_validation'] = '0'
                    else:
                        insertion_dict['iso_19030_validation'] = '1'
                    if (prop1_slip and not prop2_slip):
                        insertion_dict['apparent_slip'] = prop1_slip
                    if (prop2_slip and not prop1_slip):
                        insertion_dict['apparent_slip'] = prop2_slip
                    if (prop1_slip and prop2_slip):
                        insertion_dict['apparent_slip'] = (prop1_slip + prop2_slip) / 2



                    if me_total_flowmeter:
                        me_total_cons_t = me_total_flowmeter / 1000 * 5 / 60
                        insertion_dict['me_total_cons_t'] = me_total_cons_t
                        insertion_dict['me_consumption_per_hour'] = me_total_flowmeter / 1000 
                    if dg_total_flowmeter:
                        insertion_dict['dg_total_fuel_cons_t'] = dg_total_flowmeter
                    if (me_sox_flw1 and dg_sox_flw1 and bo_sox_flw1):
                        insertion_dict['sox_t_h'] = me_sox_flw1 + dg_sox_flw1 + bo_sox_flw1
                    if (prop1_rpm and not prop2_rpm):
                        insertion_dict['rpm'] = prop1_rpm
                    if (prop2_rpm and not prop1_rpm):
                        insertion_dict['rpm'] = prop2_rpm
                    if (prop1_rpm and prop2_rpm):
                        insertion_dict['rpm'] = (prop1_rpm + prop2_rpm) / 2
                    if (me_nox_flw1 and dg_nox_flw1):
                        insertion_dict['nox_t_h'] = (me_nox_flw1 + dg_nox_flw1) / 1000
                    if (me_total_cons_t and me_mdo_in_use):
                        insertion_dict['me_mdo_fuel_cons_t'] = me_total_cons_t
                    if (me_total_cons_t and me_hfo_in_use):
                        insertion_dict['me_hfo_hs_fuel_cons_t'] = me_total_cons_t
                    if (me_total_cons_t and dg_mdo_in_use):
                        insertion_dict['dg_mdo_fuel_cons_t'] = dg_total_flowmeter
                    if (me_total_cons_t and dg_hfo_in_use):
                        insertion_dict['dg_hfo_hs_fuel_cons_t'] = dg_total_flowmeter
                    if (me_total_pow):
                        
                    
                        # s = select([vesseldetail.c.mcr]).where(vesseldetail.c.idvessel==idvessel)
                        vesseldetail_mcr  = list(filter(lambda x: x['attribute_id'] == 8 and x['imo'] == vessel, vessel_detail))
                        # with db.connect() as connection:
                        #     vesseldetail_mcr = connection.execute(s).scalar()
                        if vesseldetail_mcr:
                            print(vesseldetail_mcr[0]['value'])
                            try:
                                vesseldetail_mcr = float(vesseldetail_mcr[0]['value'])
                            except:
                                vesseldetail_mcr = 0
                            try:
                                mcr = me_total_pow / vesseldetail_mcr * 100
                            except:
                                mcr = 0
                            insertion_dict['mcr'] = mcr
                    if (draft_aft and draft_fore):
                        trim = draft_fore - draft_aft
                        insertion_dict['trim_m'] = trim


                    for tag in datapoint._asdict().keys():
                        column_name = mapped.get(tag, None)
                        if column_name:
                            # print('``````',tag)
                            insertion_dict[column_name] = getattr(datapoint, tag, None)
                        else:
                            # print(',,,,,,',tag)
                            # print('no direct mapping')
                            if tag == 'ts':
                                timestamp = getattr(datapoint, tag, None)
                                timestamp = timestamp // 1000
                                date_hour = datetime.fromtimestamp(timestamp)
                                insertion_dict['date_hour'] = date_hour

                    print("Getting Id")
                    idd = querydata.get_adadata_id(db)
                    idd = idd.id
                    print(idd,"idd")
                    # print(type(id))
                    id = idd+1
                    insertion_dict['id'] = id
                    insertion_dict['head_deg'] = insertion_dict['HEAD_deg']
                    del insertion_dict['HEAD_deg']
                    insertion_dict['model_wind_speed_apparent_kn'] = insertion_dict['Model_Wind_Speed_Apparent_kn']
                    del insertion_dict['Model_Wind_Speed_Apparent_kn']
                    insertion_dict['sensor_wind_speed_apparent_kn'] = insertion_dict['Sensor_Wind_Speed_Apparent_kn']
                    del insertion_dict['Sensor_Wind_Speed_Apparent_kn']
                    insertion_dict['model_wind_dir_apparent'] = insertion_dict['Model_Wind_Dir_Apparent']
                    del insertion_dict['Model_Wind_Dir_Apparent']
                    insertion_dict['sensor_wind_dir_apparent'] = insertion_dict['Sensor_Wind_Dir_Apparent']
                    del insertion_dict['Sensor_Wind_Dir_Apparent']
                    insertion_dict['phase'] = insertion_dict['Phase']
                    del insertion_dict['Phase']
                    insertion_dict['stw_kn'] = insertion_dict['STW_kn']
                    del insertion_dict['STW_kn']
                    insertion_dict['sog_kn'] = insertion_dict['SOG_kn']
                    del insertion_dict['SOG_kn']
                    insertion_dict['sg_running'] = insertion_dict['SG_Running']
                    del insertion_dict['SG_Running']
                    insertion_dict['model_sea_state_d'] = insertion_dict['Model_Sea_State_D']
                    del insertion_dict['Model_Sea_State_D']
                    insertion_dict['model_sea_dir_apparent'] = insertion_dict['Model_Sea_Dir_Apparent']
                    del insertion_dict['Model_Sea_Dir_Apparent']
                    insertion_dict['model_current_force_true_kn'] = insertion_dict['Model_Current_Force_True_kn']
                    del insertion_dict['Model_Current_Force_True_kn']
                    insertion_dict['significant_wave_height'] = insertion_dict['Significant_Wave_Height']
                    del insertion_dict['Significant_Wave_Height']
                    insertion_dict['sfoc_g_kwh'] = insertion_dict['SFOC_g_kWh']
                    del insertion_dict['SFOC_g_kWh']
                    insertion_dict['draft_fore_m'] = insertion_dict['Draft_Fore_m']
                    del insertion_dict['Draft_Fore_m']
                    insertion_dict['draft_aft_m'] = insertion_dict['Draft_Aft_m']
                    del insertion_dict['Draft_Aft_m']
                    insertion_dict['run_dg_4'] = insertion_dict['Run_DG4']
                    del insertion_dict['Run_DG4']
                    insertion_dict['pow_dg_4_kw'] = insertion_dict['Pow_DG4_kW']
                    del insertion_dict['Pow_DG4_kW']
                    insertion_dict['run_dg_3'] = insertion_dict['Run_DG3']
                    del insertion_dict['Run_DG3']
                    insertion_dict['pow_dg_3_kw'] = insertion_dict['Pow_DG3_kW']
                    del insertion_dict['Pow_DG3_kW']
                    insertion_dict['run_dg_2'] = insertion_dict['Run_DG2']
                    del insertion_dict['Run_DG2']
                    insertion_dict['pow_dg_2_kw'] = insertion_dict['Pow_DG2_kW']
                    del insertion_dict['Pow_DG2_kW']
                    insertion_dict['run_dg_1'] = insertion_dict['Run_DG1']
                    del insertion_dict['Run_DG1']
                    insertion_dict['pow_dg_1_kw'] = insertion_dict['Pow_DG1_kW']
                    del insertion_dict['Pow_DG1_kW']
                    insertion_dict['dg_average_power_kw'] = insertion_dict['DG_Average_Power_kW']
                    del insertion_dict['DG_Average_Power_kW']
                    insertion_dict['dg_running'] = insertion_dict['DG_Running']
                    del insertion_dict['DG_Running']
                    insertion_dict['cog_deg'] = insertion_dict['COG_deg']
                    del insertion_dict['COG_deg']
                    insertion_dict['shaft_power_kw'] = insertion_dict['Shaft_Power_kW']
                    del insertion_dict['Shaft_Power_kW']
                    del insertion_dict['Latitude']
                    del insertion_dict['Longitude']

                    if insertion_dict['run_dg_1'] == True or insertion_dict['run_dg_1'] == 'true' or insertion_dict['run_dg_1'] == 'True' or insertion_dict['run_dg_1'] == ' true' or insertion_dict['run_dg_1'] == 'true ' or insertion_dict['run_dg_1'] == ' True' or insertion_dict['run_dg_1'] == 'True ':
                        print('in the if else condition run_dg_1 True :')
                        insertion_dict['run_dg_1'] = '1'
                    if insertion_dict['run_dg_1'] == False or insertion_dict['run_dg_1'] == 'false' or insertion_dict['run_dg_1'] == 'False' or insertion_dict['run_dg_1'] == 'false ' or insertion_dict['run_dg_1'] == ' false'  or insertion_dict['run_dg_1'] == ' False' or insertion_dict['run_dg_1'] == 'False ':
                        print('in the if else condition run_dg_1 False :')
                        insertion_dict['run_dg_1'] = '0'
                    if insertion_dict['run_dg_2'] == True or insertion_dict['run_dg_2'] == 'true' or insertion_dict['run_dg_2'] == 'True' or insertion_dict['run_dg_2'] == ' true' or insertion_dict['run_dg_2'] == 'true ' or insertion_dict['run_dg_2'] == ' True' or insertion_dict['run_dg_2'] == 'True ':
                        print('in the if else condition run_dg_2 True :')
                        insertion_dict['run_dg_2'] = '1'
                    if insertion_dict['run_dg_2'] == False or insertion_dict['run_dg_2'] == 'false' or insertion_dict['run_dg_2'] == 'False' or insertion_dict['run_dg_2'] == 'false ' or insertion_dict['run_dg_2'] == ' false' or insertion_dict['run_dg_2'] == ' False' or insertion_dict['run_dg_2'] == 'False ':
                        print('in the if else condition run_dg_2 False :')
                        insertion_dict['run_dg_2'] = '0'
                    if insertion_dict['run_dg_3'] == True or insertion_dict['run_dg_3'] == 'true' or insertion_dict['run_dg_3'] == 'True' or insertion_dict['run_dg_3'] == 'true ' or insertion_dict['run_dg_3'] == ' true' or insertion_dict['run_dg_3'] == ' True' or insertion_dict['run_dg_3'] == 'True ':
                        print('in the if else condition run_dg_3 True :')
                        insertion_dict['run_dg_3'] = '1'
                    if insertion_dict['run_dg_3'] == False or insertion_dict['run_dg_3'] == 'false' or insertion_dict['run_dg_3'] == 'False' or insertion_dict['run_dg_3'] == 'false ' or insertion_dict['run_dg_3'] == ' false' or insertion_dict['run_dg_3'] == ' False' or insertion_dict['run_dg_3'] == 'False ':
                        print('in the if else condition run_dg_3 False :')
                        insertion_dict['run_dg_3'] = '0'
                    if insertion_dict['run_dg_4'] == True or insertion_dict['run_dg_4'] == 'true' or insertion_dict['run_dg_4'] == 'True' or insertion_dict['run_dg_4'] == 'true ' or insertion_dict['run_dg_4'] == ' true' or insertion_dict['run_dg_4'] == ' True' or insertion_dict['run_dg_4'] == 'True ':
                        print('in the if else condition run_dg_4 True :')
                        insertion_dict['run_dg_4'] = '1'
                    if insertion_dict['run_dg_4'] == False or insertion_dict['run_dg_4'] == 'false' or insertion_dict['run_dg_4'] == 'False' or insertion_dict['run_dg_4'] == 'false ' or insertion_dict['run_dg_4'] == ' false' or insertion_dict['run_dg_4'] == ' False' or insertion_dict['run_dg_4'] == 'False ':
                        print('in the if else condition run_dg_4 False :')
                        insertion_dict['run_dg_4'] = '0'
                    print('insertion_dict:',insertion_dict)
                    insert_ada_data = querydata.post_ada(db,insertion_dict)
                    print("Inserted")
                    print(id)
                # exit()
            return {"Completed"}

        # if __name__ == '__main__':
        # try:
            # set_refresh_token()
        print("Starting..............................")
        try:
            insert_data()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
                # get the line number
                # line_num = exc_tb.tb_lineno
                # print the exception type, message and line number
            
            e = str(e)
            error = logging.error(e)
            while exc_tb is not None:
                # get the line numbe
                line_num = exc_tb.tb_lineno
                # print the exception type, message and line number
                print(f"Exception type: {exc_type.__name__}")
                print(f"Exception message: {e}")
                print(f"Line number: {line_num}")
                exc_tb = exc_tb.tb_next

            alert_error_sub = 'Error In ADA Data Insertion'
            alert_error_msg = f'There is an error occured in Ada Data Inserton Please check. <br><br> Exception type : {exc_type.__name__} <br>Exception message : {e} <br> Line number : {line_num} '
            # send_alert(alert_error_sub,alert_error_msg,request)
            raise Exception(status_code=500, detail=e)
        return {"Completed"}
    except Exception as er:
        print("Outer Exception:", er)
