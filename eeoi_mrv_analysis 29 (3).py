from statistics import mean
from typing_extensions import assert_type
from fastapi import APIRouter, Depends
from sqlalchemy import values
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import json
from fastapi import Request
from storage import querydata, vessel
from storage import database
from storage.database import get_db
from storage.vdm_database import get_vdm_db
from cache import cache_set, utility
from common.configuration import CACHEKEY
from authentication.authorization import get_token
from datetime import datetime , date, timedelta
from typing import Union
import pandas as pd
import numpy as np

CACHEKEY=CACHEKEY()
router = APIRouter()


@router.get('/api/v1/eeoi_mrv/vessels/{vtype}')
def index(vtype:str,db:Session = Depends(get_vdm_db),token : Session = Depends(get_token)):
    vessels=cache_set.get_vdm_type_vessel(vtype,db)
    return vessels


@router.get('/api/v1/eeoi_mrv/vwr/voyages/{imo}')
def index(emtypevf:str=None,imo:str=None,date1:date=None,date2:date=None,db:Session = Depends(get_vdm_db),m_db= Depends(get_db),token : Session = Depends(get_token)):

    voyages=  cache_set.get_voyages_imo_wise(m_db,imo) 
    if not voyages:
        return {"Voyage_number":[]} 
    if emtypevf=="All Voyages":
        voyages=list(filter(lambda x:str(x['report_type'])!='REFL',voyages))

    else:
        # pass
        voyages=list(filter(lambda x:(str(x['report_type'])!='REFL') and str(x['eu'])=='Y',voyages))
    if not voyages:
        return {"Voyage_number":[]}
        
    voyages=list(filter(lambda x:str(x['corrected_date'])>=str(date1) and str(x['corrected_date'])<=str(date2),voyages))
    data_list = set([str(int(float(i['voyage_order'])))  for i in voyages])
    return {"Voyage_number":sorted(data_list)}



@router.get('/api/v1/eeoi_mrv/vwr/voyage_name/{imo}')
def index(imo:str=None,date1:date=None,date2:date=None,pas_id:str=None,db:Session = Depends(get_vdm_db),m_db= Depends(get_db),token : Session = Depends(get_token)):
    voyages =  cache_set.get_voyages_imo_wise(m_db,imo)  
    #print(float(int(pas_id)))
    if not voyages:
        return {"Voyage_number":[] }
    voyages=list(filter(lambda x:str(x['corrected_date'])>=str(date1) and str(x['corrected_date'])<=str(date2) and (x['voyage_order']==str(float(int(pas_id)))),voyages))
    data_list = set([str(i['voyage_code'])  for i in voyages])          
    

    return  {"Voyage_name":data_list} 
    
@router.get('/api/v1/eeoi_mrv/data/{imo}')
def index(imo:str=None,date1:date=None,date2:date=None,vdm_db:Session = Depends(get_vdm_db),db= Depends(get_db),token : Session = Depends(get_token)):
    
   
    data = utility.get_data(key=CACHEKEY.NOONDATADATA_HSTRC_NEW+str(imo))
    cache = False
    if data is not None:
        cache = True
    else:
        data = querydata.get_viewr_report(db,imo)
        data = json.dumps(jsonable_encoder(data))

        try:
            if data is not None:
                cache = False
                state = utility.set_data(key=CACHEKEY.NOONDATADATA_HSTRC_NEW+str(imo), value=data)
                if state is True:
                    print('Cache Set Successfully') 
        except:
            print('cache set failure')

    data = json.loads(data)
    if not data:
        return {"data":[]}
    data = list(filter(lambda x : x['corrected_date'] >= str(date1) and x['corrected_date'] <= str(date2) , data))
    df = pd.DataFrame(data)
    if df.empty:
        return {"data": []}
    mcr=cache_set.get_mcr_filter(vdm_db)
    mcr= list(filter(lambda x:x['imo'] == imo , mcr))

    print(mcr[1])
    df['Vessel']=mcr[0]['name']
    df['Fleet']=mcr[0]['fleet']
    # df['Class']=mcr[0]['class']

    df['Miles by GPS(Nm)'] = pd.to_numeric(df['miles_by_gps'])
    df['Voyage order'] = pd.to_numeric(df['voyage_order'])
    df['Cargo total(MT)'] = pd.to_numeric(df['cargo_total'])
    df['Cargo total TEU(MT)'] = pd.to_numeric(df['cargo_total_teu'])
    df['Manvrng miles by gps(Nm)'] = pd.to_numeric(df['manvrng_miles_by_gps'])
    df['Fuel HS(MT)'] = pd.to_numeric(df['fuel_hs'])
    df['Fuel LS(MT)'] = pd.to_numeric(df['fuel_ls'])
    df['Fuel MDO(MT)'] = pd.to_numeric(df['fuel_mdo'])
    df['Fuel MGO(MT)'] = pd.to_numeric(df['fuel_mgo'])
    df['TEU full'] = pd.to_numeric(df['teu_full'])
    df['TEU empty'] = pd.to_numeric(df['teu_empty'])
    df['Fuel MGO LS(MT)'] = pd.to_numeric(df['fuel_mgo_ls'])
    df['me_fuel_only_steaming_time'] = pd.to_numeric(df['me_fuel_only_steaming_time'])

    df=df[['Vessel','imo','Fleet','Voyage order','voyage_code','voy_condition','corrected_date','report_type','status','eu','Cargo total(MT)','Cargo total TEU(MT)','Miles by GPS(Nm)','Manvrng miles by gps(Nm)','fuel_aux_dstlt_uls','fuel_me_dstlt_uls','fuel_boiler_tnktnr_dstlt_vls','fuel_aux_tnktnr_dstlt_vls','fuel_me_tnktnr_dstlt_vls','fuel_boiler_dstlt_vls','fuel_boiler_dstlt_uls','fuel_aux_dstlt_vls','fuel_me_dstlt_vls','fuel_boiler_rsdl_hs','fuel_boiler_rsdl_uls','fuel_aux_rsdl_uls','fuel_me_rsdl_uls','fuel_boiler_rsdl_vls','fuel_aux_rsdl_vls','fuel_me_rsdl_vls','fuel_aux_rsdl_hs','fuel_me_rsdl_hs','Fuel HS(MT)','Fuel LS(MT)','Fuel MDO(MT)','Fuel MGO(MT)','TEU full','TEU empty','Fuel MGO LS(MT)','me_fuel_only_steaming_time']]
    df.rename(columns={'fuel_aux_dstlt_uls':'Fuel aux dstlt uls (MT)','fuel_me_dstlt_uls':'fuel_me_dstlt_uls (MT)','fuel_boiler_tnktnr_dstlt_vls':'fuel_boiler_tnktnr_dstlt_vls (MT)','fuel_aux_tnktnr_dstlt_vls': 'fuel_aux_tnktnr_dstlt_vls (MT)','fuel_me_tnktnr_dstlt_vls':'fuel_me_tnktnr_dstlt_vls (MT)','fuel_boiler_dstlt_vls': 'fuel_boiler_dstlt_vls(MT)','fuel_boiler_dstlt_uls':'fuel_boiler_dstlt_uls(MT)','fuel_aux_dstlt_vls':'fuel_aux_dstlt_vls(MT)','fuel_me_dstlt_vls':'fuel_me_dstlt_vls(MT)','fuel_boiler_rsdl_hs':'fuel_boiler_rsdl_hs(MT)','fuel_boiler_rsdl_uls':'fuel_boiler_rsdl_uls(MT)','fuel_aux_rsdl_uls':'fuel_aux_rsdl_uls(MT)','fuel_me_rsdl_uls':'fuel_me_rsdl_uls(MT)','fuel_boiler_rsdl_vls':'fuel_boiler_rsdl_vls(MT)','fuel_aux_rsdl_vls':'fuel_aux_rsdl_vls(MT)','fuel_me_rsdl_vls':'fuel_me_rsdl_vls(MT)','fuel_aux_rsdl_hs':'fuel_aux_rsdl_hs(MT)','fuel_me_rsdl_hs':'fuel_me_rsdl_hs(MT)','me_fuel_only_steaming_time':'ME fuel only steaming time'}, inplace = True)

    df['corrected_date']=pd.to_datetime(df['corrected_date']).dt.strftime('%d %b %Y')
    
    data = df.to_json(orient='records')
    data = json.loads(data)
    return {"data":data}
    

@router.get('/api/v1/eeoi_mrv/{imo}')
def index(imo:str,db:Session = Depends(get_vdm_db),token : Session = Depends(get_token)):
    # at_id=[8,567,74,4,1,19,5,328,65]
    
    vessels=cache_set.get_mcr_filter(db)
    vessels=list(filter(lambda x:x['imo']==str(imo),vessels))

    dict={} 
    if not dict:
        dict['imo']=imo
        # dict['gt']=vessels[0]['grt']
        dict['vessel_name']=vessels[0]['name']

    try:
        vessel_id=list(filter(lambda x:x['imo']==str(imo),vessels))[0]['id']
    except:
        vessel_id=None
    # vessel_attribute=cache_set.get_all_table_vessel_attribute(vessel_id,at_id,db)
    try:
        dict['gt']=list(filter(lambda x:x['attribute_id']==83 ,vessels))[0]['value']
    except:
        dict['gt']=None
    try:
        dict['fl']=list(filter(lambda x:x['attribute_id']==74 ,vessels))[0]['value']
    except:
        dict['fl']=None
    try:
        dict['home_port']=list(filter(lambda x:x['attribute_id']==74 ,vessels))[0]['value']
    except:
        dict['home_port']=None
    try:
        dict['Name_of_Ship_Owner']=list(filter(lambda x:x['attribute_id']==65 ,vessels))[0]['value']
    except:
        dict['Name_of_Ship_Owner']=None
    try:
        dict['Registered_Owner_ID_number']=list(filter(lambda x:x['attribute_id']==567 ,vessels))[0]['value']
    except:
        dict['Registered_Owner_ID_number']=None
    try:
        dict['vessel_dwt']=list(filter(lambda x:x['attribute_id']==8 ,vessels))[0]['value']
    except:
        dict['vessel_dwt']=None
    try:
        dict['class_society']=list(filter(lambda x:x['attribute_id']==5 ,vessels))[0]['value']
    except:
        dict['class_society']=None
    try:
        dict['vessel_type']=list(filter(lambda x:x['attribute_id']==4 ,vessels))[0]['value']
    except:
        dict['vessel_type']=None
    if dict['vessel_type'] == '1':
        dict['vessel_type'] = 'Container'
    elif dict['vessel_type'] == '2':
        dict['vessel_type'] = 'Bulk Carrier'
    elif dict['vessel_type'] == '3':
        dict['vessel_type'] = 'PCTC'
    elif dict['vessel_type'] == '4':
        dict['vessel_type'] = 'PAX'
    elif dict['vessel_type'] == '5':
        dict['vessel_type'] = 'ROPAX'
    elif dict['vessel_type'] == '6':
        dict['vessel_type'] = 'TUG'
    
    return { "data": dict}


@router.get('/api/v1/eeoi_mrv/ywer/{imo}',status_code=200)
def index(imo:str = None,m_db= Depends(get_db),year:int = None,data_type:str=None,vessel_type:str=None,db : Session = Depends(get_db),token : Session = Depends(get_token)):    
    

    
    # voyages=  cache_set.get_voyages(m_db,imo,year,year)
    # voyages=  querydata.get_voyages(m_db,imo,year,year)
    # voyages=list(set(voyages)) 
    # if voyages:
    #     voyages = list(set([i['voyage_order'] for i in voyages]))


    data = utility.get_data(key=CACHEKEY.NOONDATADATA_HSTRC+str(imo)+str(year))
    cache = False
    if data is not None:
        data = json.loads(data)
        cache = True
    else:
        # start_year = end_year = i
        # #print(year1,year2)
        data = querydata.get_NoonDatas_voyages(m_db,imo,year)
        data = json.dumps(jsonable_encoder(data))
    
        # #print("data ::::::::" , data)

        try:
            if data is not None:
                cache = False
                state = utility.set_data(key=CACHEKEY.NOONDATADATA_HSTRC+str(imo)+str(year), value=data)
                if state is True:
                    print('Cache Set Successfully') 
        except:
            print('cache set failure')
        data = json.loads(data)
    # #print(data)
    if year != "":
        startdate = str(date(year ,1 ,1))
        enddate =str(date(year ,12 ,31))
        #print("startdate:",startdate , "enddate:",enddate)        
    else:
        # startdate = datetime.now() - timedelta(days = 90)
        startdate = datetime.now()
        #print("now:",startdate)
        enddate = datetime.now() - timedelta(days = 90)

       
    cargo=pd.DataFrame()
    df = pd.DataFrame(data)
    columns_to_exclude = ['voyage_order']

    df = df.apply(lambda col: col.fillna(0) if col.name not in columns_to_exclude else col)
    if df.empty:
        return {"data":[]}
    # #print("RRRRRRRRRRRRRRR",df)
    # y$Transport_Work = (as.numeric(as.character(y$MILES_BY_GPS)) + as.numeric(as.character(y$MANVRNG_MILES_BY_GPS))) * as.numeric(as.character(y$CARGO_TOTAL))
    # y$Transport_Work_TEU = (as.numeric(as.character(y$MILES_BY_GPS)) + as.numeric(as.character(y$MANVRNG_MILES_BY_GPS))) * as.numeric(as.character(y$CARGO_TOTAL_TEU))
    # y
    # exit()
    df['total_steaming_time'] = df['total_steaming_time'].replace(np.nan, 0)
    df['cargo_total'] = pd.to_numeric(df['cargo_total'], errors='coerce').fillna(0)
    df['cargo_total_teu'] = pd.to_numeric(df['cargo_total_teu'], errors='coerce').fillna(0)
    df['miles_by_gps'] = pd.to_numeric(df['miles_by_gps'], errors='coerce').fillna(0)
    df['manvrng_miles_by_gps'] = pd.to_numeric(df['manvrng_miles_by_gps'], errors='coerce').fillna(0)

    if year < 2020:
        df['hs'] = df['fuel_me_hs'] + df['fuel_aux_hs'] + df['fuel_boiler_hs']
        df['ls'] = df['fuel_me_ls']+df['fuel_aux_ls']+df['fuel_boiler_ls']
        df['mdo'] = df['fuel_me_mdo']+df['fuel_aux_mdo']+df['fuel_boiler_mdo']
        df['mgo'] = df['fuel_me_mgo']+df['fuel_aux_mgo']+df['fuel_boiler_mgo']+df['fuel_me_mgo_ls']+df['fuel_boiler_mgo_ls']+df['fuel_aux_mgo_ls']
    else:
        df['fuel_hs']=pd.to_numeric(df['fuel_me_rsdl_hs'])+pd.to_numeric(df['fuel_aux_rsdl_hs'])+pd.to_numeric(df['fuel_boiler_rsdl_hs'])
    
        df['fuel_ls']=pd.to_numeric(df['fuel_me_rsdl_vls']) + pd.to_numeric(df['fuel_aux_rsdl_vls']) +pd.to_numeric(df['fuel_boiler_rsdl_vls']) + pd.to_numeric(df['fuel_me_rsdl_uls']) + pd.to_numeric(df['fuel_aux_rsdl_uls']) + pd.to_numeric(df['fuel_boiler_rsdl_uls'])
        
        df['fuel_mgo']=pd.to_numeric(df['fuel_me_dstlt_vls']) + pd.to_numeric(df['fuel_aux_dstlt_vls']) + pd.to_numeric(df['fuel_boiler_dstlt_vls']) + pd.to_numeric(df['fuel_me_dstlt_uls']) + pd.to_numeric(df['fuel_aux_dstlt_uls']) + pd.to_numeric(df['fuel_boiler_dstlt_uls'])+pd.to_numeric(df['fuel_me_tnktnr_dstlt_vls']) + pd.to_numeric(df['fuel_aux_tnktnr_dstlt_vls']) + pd.to_numeric(df['fuel_boiler_tnktnr_dstlt_vls'])
    df['fuel_mdo'] = np.where(pd.to_numeric(year) < 2020, df['fuel_mdo'], None)
    df['fuel_mgo_ls'] = np.where(pd.to_numeric(year) < 2020, df['fuel_mgo_ls'], None)
    
        
    df['transport_work']=(df['miles_by_gps'].astype(float)+df['manvrng_miles_by_gps'].astype(float))*df['cargo_total'].astype(float)
    df['transport_work_teu']=(df['miles_by_gps'].astype(float)+df['manvrng_miles_by_gps'].astype(float))*df['cargo_total_teu'].astype(float)
    df['voyage_order']=df['voyage_order'].ffill().bfill()
    df['cargo_total'] = pd.to_numeric(df['cargo_total'], errors='coerce').fillna(0)

    df['cargo_total']=df['cargo_total'].ffill().bfill()
    if year < 2020:
        m=[3.1144,3.151,3.206,3.206,3.206]
        n=[4.5,3.5,1.5,1.5,1.5]
    else:
        m=[3.1144,3.151,0,3.206,0]
        n=[4.5,3.5,0,1.5,0]
    
    o = [
    round(df['fuel_hs'].astype(float).sum(),2),
    round(df['fuel_ls'].astype(float).sum(),2),
    round(df['fuel_mdo'].astype(float).sum(),2),
    round(df['fuel_mgo'].astype(float).sum(),2),
    round(df['fuel_mgo_ls'].astype(float).sum(),2)]
    # df=df['fuel_ls'].to_json()
    # df=json.loads(df)
    # return df
    # exit()
    sea=df[df['status'] == 'AT SEA']

    q=[round(sea['fuel_hs'].astype(float).sum(),2)
    ,round(sea['fuel_ls'].astype(float).sum(),2)
    ,round(sea['fuel_mdo'].astype(float).sum(),2)
    ,round(sea['fuel_mgo'].astype(float).sum(),2),
    round(sea['fuel_mgo_ls'].astype(float).sum(),2)]

    port=df[(df['status'] == 'IN PORT') | (df['status'] == 'DRIFTING')]

    p=[round(port['fuel_hs'].astype(float).sum(),2)
    ,round(port['fuel_ls'].astype(float).sum(),2)
    ,round(port['fuel_mdo'].astype(float).sum(),2)
    ,round(port['fuel_mgo'].astype(float).sum(),2),
    round(port['fuel_mgo_ls'].astype(float).sum(),2)]


    r= list(np.multiply(m,o))
    r=list(np.around(np.array(r), 2))
    # r=round(r,2)
    s=list(np.multiply(n,o)*20/1000)
    s=list(np.around(np.array(s), 2))

    new_array=[m,n,o,p,q,r,s]
    # #print("RRRRRRRRRRRRrr")
    # #print(new_array)
    df1 = pd.DataFrame(data=new_array,index=["Emission factor (Ton-CO2/Ton-Fuel)", "Sulphur content [%]",  "Total Fuel (Ton)",  "Fuel at Berth (Ton)",  "Fuel at Sea (Ton)",  "Total CO2 (Ton)", "Total SOx (Ton)"], columns=["Fuel(HS)","Fuel (LS)","Fuel (MDO)","Fuel (MGO)","Fuel (MGO)LS"])
   
    new=[]



    # new=[]



    # if vessel_type=="Container":
    new.append(round(sum(o),2))
    new.append(round(sum(q)))
    new.append(round(sum(p)))
    new.append(round(sum(r)))
    new.append(round(sum(list(np.multiply(q,m)))))
    new.append(round(sum(list(np.multiply(p,m)))))
    new.append(round(sum(pd.to_numeric(df['miles_by_gps']) + pd.to_numeric(df['manvrng_miles_by_gps'])),2))
    m_e_fuel_only_steaming_tim=round(sum(pd.to_numeric(sea['me_fuel_only_steaming_time'])/24),2)
       
    if not m_e_fuel_only_steaming_tim:
        m_e_fuel_only_steaming_tim="0.0"
    # #print("420",m_e_fuel_only_steaming_tim)
    new.append(m_e_fuel_only_steaming_tim)
   

    tcargo=df.groupby(['imo'])['cargo_total'].unique().reset_index()
    print("dfjdhfdjfh",tcargo)
    # tcargo=tcargo['cargo_total'].sum()
    try:
        new.append(round(np.sum(tcargo['cargo_total'][0]),2))
    except:
        new.append(0.0)

    if vessel_type=="Container":
        teucargo=df.groupby(['imo'])['cargo_total_teu'].unique().reset_index()
        new.append(round(np.sum(teucargo['cargo_total_teu'][0]),2))
   
    try:
        new.append(round(sum(np.sum(tcargo['cargo_total'][0])*(df['miles_by_gps'] + pd.to_numeric(df['manvrng_miles_by_gps']))),2))
    except:
        new.append(0.0)
    # print(sum(np.sum(tcargo['cargo_total'][0])*(df['miles_by_gps'] + pd.to_numeric(df['manvrng_miles_by_gps']))))
    if vessel_type=="Container":
        try:
            cargo_teu=np.sum(teucargo['cargo_total_teu'][0])
            new.append(round(np.sum(round(cargo_teu,2)*df['miles_by_gps'] + pd.to_numeric(df['manvrng_miles_by_gps'])),2))
        except:
            new.append(0.0)
    
    try:    
        new.append(round(np.sum(float(new[0]))/sum(df['miles_by_gps'] + pd.to_numeric(df['manvrng_miles_by_gps'])),2))
    except:
        new.append(0.0)

    try:
        new.append(round((float(new[0])*1000000/float(new[9])),2))
    except:
        new.append(0.0)
    try:
        new.append(round((float(new[3])*1000000)/float(new[6]),2))
    except:
        new.append(0.0)

    try:
        new.append(round((float(new[3])*1000000)/float(new[9]),2))
    except:
        new.append(0.0)
    if vessel_type == 'Container':
        new.append(round(float(new[3])*1000000)/float(new[11]))
        df2 = pd.DataFrame(data=new,index=["Total Fuel Consumption",
      "Total Fuel Consumption at Sea(Ton)",
      "Total Fuel Consumption at Berth(Ton)",
      "Total CO2 Emission (Ton)",
      "CO2 Emissions at sea (Ton)",
      "CO2 Emission at Berth (Ton)",
      'Total Distance Sailed (Nm)',
      "Total time at sea (days)",
      "Total Cargo (Ton)",
      "Total Cargo (TEU)",
      "Total Transport Work (Ton-Nm)",
      "Total Transport Work (TEU-Nm)",
      "Fuel consumption per distance (Ton/Nm)",
      "Fuel consumption per transport work (freight transport) (g/Ton*Nm)",
      "CO2 Emission per Distance (g/Nm)",
      "CO2 Emission per transport work (g/Ton*Nm)",
      "CO2 Emission per transport work (g/TEU*Nm)"], columns=["Value"])
    else:
        df2 = pd.DataFrame(data=new,index=[ "Total Fuel Consumption",
      "Total Fuel Consumption at Sea(Ton)",
      "Total Fuel Consumption at Berth(Ton)",
      "Total CO2 Emission (Ton)",
      "CO2 Emissions at sea (Ton)",
      "CO2 Emission at Berth (Ton)",
      'Total Distance Sailed (Nm)',
      "Total time at sea (days)",
      "Total Cargo (Ton)",
      "Total Transport Work (Ton-Nm)",
      "Fuel consumption per distance (Ton/Nm)",
      "Fuel consumption per transport work (freight transport) (g/Ton*Nm)",
      "CO2 Emission per Distance (g/Nm)",
      "CO2 Emission per transport work (g/Ton*Nm)"], columns=["Value"])
    df['total_co2'] = round((df['fuel_hs'].astype(float) * 3.1144 )+ (df['fuel_ls'].astype(float) * 3.151) + (df['fuel_mgo'].astype(float) * 3.206),2)
    df['totalfo'] =pd.to_numeric(df['fuel_hs']) + pd.to_numeric(df['fuel_ls']) + pd.to_numeric(df['fuel_mgo']) 
    df['co2'] = round(df['total_co2'].astype(float),2)
    result = df.groupby('voyage_order').agg({'totalfo':np.sum,'cargo_total_teu':np.mean,'total_co2': np.sum,'miles_by_gps': np.sum,'cargo_total':np.mean,'manvrng_miles_by_gps': np.sum}).reset_index()
    result['distance']=result['miles_by_gps']+result['manvrng_miles_by_gps']
    result['eeoi']= round((pd.to_numeric(result['total_co2']) * (10 ** 6)) /( pd.to_numeric(result['distance']) * pd.to_numeric(result['cargo_total'])),2)
    result['eeoiTEU']= round((pd.to_numeric(result['total_co2']) * (10 ** 6)) /( pd.to_numeric(result['distance']) * pd.to_numeric(result['cargo_total_teu'])),2)
    df1['fuel_cons_details']=df1.index

    df1 = df1.to_json(orient="records")
    table1 = json.loads(df1)
    df2['index']=df2.index
    df2 = df2.to_json(orient="records")
    reported_data = json.loads(df2)
    result.rename(columns={'voyage_order':'voyage_no','total_co2':'co2'}, inplace = True)

    result = result.to_json(orient="records")
    eechart = json.loads(result)

    return {"table1":table1,"reported_data":reported_data,"eechartdata":eechart}


    
    

    
    
    
    
        







    #     cargometric=pd.DataFrame()
      
    #     xcargo= sea.groupby(['imo','voyage_order'])['cargo_total'].mean().reset_index()
    #     # xcargo['cargo_total'] = xcargo['cargo_total'].apply(', '.join)

    #     # xcargo['cargo_total']=xcargo['cargo_total'].tolist()
    #     #print("xcargo['cargo_total']",xcargo['cargo_total'])
    #     xcargo['cargo_total']=pd.to_numeric(xcargo['cargo_total'])
    #     #print("-------------------------------------------------------")
    #     #print("-------------------------------------------------------")

    #     #print(xcargo['cargo_total'])
    #     #print("-------------------------------------------------------")

    #     #print("-------------------------------------------------------")

    #     cargometric['cargo_total']=xcargo['cargo_total'].sum()
     
    #     # teu_cargo= cargo.groupby(["vsl","voyage_order"])['teu_full','teu_empty'].unique().reset_index()
    #     # teu_full= sea.groupby(['imo','voyage_order'])['teu_full','teu_empty'].unique().reset_index()
    #     teu_full = sea.groupby(['imo', 'voyage_order']).agg({'teu_full': pd.Series.unique, 'teu_empty': pd.Series.unique}).reset_index()
    #     #print(teu_full['teu_full'])

    #     teu_full['teu_full'] = teu_full['teu_full'].apply(lambda x: ','.join(map(str, x)))
        
    #     teu_full['teu_full'] = pd.to_numeric(teu_full['teu_full'], errors='coerce').fillna(0)
    #     teu_full['teu_empty'] = teu_full['teu_empty'].apply(lambda x: ','.join(map(str, x)))
        
    #     teu_full['teu_empty'] = pd.to_numeric(teu_full['teu_empty'], errors='coerce').fillna(0)
        
    #     cargometric['teu_full']=teu_full['teu_full'].sum()

    #     # teu_empty= sea.groupby(['imo','voyage_order'])['teu_empty'].unique().reset_index()
    #     # teu_full['teu_full']=pd.to_numeric(teu_full['teu_full'])

    #     cargometric['teu_empty']=teu_full['teu_empty'].sum()
    #     df['cargo_total_teu'] = pd.to_numeric(df['cargo_total_teu'], errors='coerce').fillna(0)
    #     df['miles_by_gps'] = pd.to_numeric(df['miles_by_gps'], errors='coerce').fillna(0)
    #     df['manvrng_miles_by_gps'] = pd.to_numeric(df['manvrng_miles_by_gps'], errors='coerce').fillna(0)
    #     df['transport_work'] = pd.to_numeric(df['transport_work'], errors='coerce').fillna(0)
    #     df['transport_work_teu'] = pd.to_numeric(df['transport_work_teu'], errors='coerce').fillna(0)
    #     df['cargo_total'] = pd.to_numeric(df['cargo_total'], errors='coerce').fillna(0)

    #     if data_type == "All Voyages":
    
    #         df =df[df['report_type'] != "REFL"]
    #     else :
        
    #         df = df[df['report_type'] != "REFL"]
    #         df = df[df['eu'] != "Y"]
    #         # subset(y, y$EU == "Y")
    #     #   }
    #         # y['voycond'] = ifelse(y['cargo_total'] == "0", "Ballast", "Laden")
    #         # y['voycond'] =  "Ballast" if y['cargo_total'] == "0" else "Laden"
    #         # y['voycond'] = ("Ballast","Laden")[y['cargo_total']=="0"]
    #     df['vodfcond'] =df['cargo_total'].apply(lambda x: 'Ballast' if x == "0" else 'Laden')
    #     df = df.replace({np.nan:None})
    #     # y = y.replace({np.'null':None})
    
    #     # y[is.null(y)] <- 0
    #     df['transport_work'] = df['miles_by_gps'].astype(float) + df['manvrng_miles_by_gps'].astype(float) *df['cargo_total'].astype(float)
    #     df['transport_work_teu'] = df['miles_by_gps'].astype(float) + df['manvrng_miles_by_gps'].astype(float) * df['cargo_total_teu'].astype(float)
    #     if df.empty:
    #         return {"data":[]}
    #     # #print(teu_full,teu_empty)
    #     cargometric['cargoteu'] = cargometric['teu_full'].astype(float)+cargometric['teu_empty'].astype(float)
    #     cargometric['imo']=teu_full['imo']
    #     cargometric['voyage_order']=teu_full['voyage_order']
      
    #     cargometric.sort_values(by='voyage_order', inplace=True)
    #     totalcargobyvessel=pd.DataFrame()
    #     tcargo=cargometric.groupby(['imo'])['cargo_total'].sum().reset_index()
    #     totalcargobyvessel['tcargo']=tcargo['cargo_total']
    #     cargoteu=cargometric.groupby(['imo'])['cargoteu'].sum().reset_index()
    #     totalcargobyvessel['cargoteu'] =cargoteu['cargoteu']
    #     voyages=cargometric.groupby(['imo'])['voyage_order'].count().reset_index()
    #     totalcargobyvessel['voyages'] = voyages['voyage_order']
    
    #     if sum(pd.to_numeric(df['miles_by_gps'])+pd.to_numeric(df['manvrng_miles_by_gps']))!=0:
    #         cargotot=sum(pd.to_numeric(df['cargo_total_teu'])*pd.to_numeric(df['miles_by_gps'])+pd.to_numeric(df['manvrng_miles_by_gps'])/sum(pd.to_numeric(df['miles_by_gps'])+pd.to_numeric(df['manvrng_miles_by_gps'])))
    #     else:
    #         cargotot=0.0
    #     if sum(pd.to_numeric(df['miles_by_gps'])+pd.to_numeric(df['manvrng_miles_by_gps'])):
    #     # #print("4444420",pd.to_numeric(df['cargo_total_teu'])*pd.to_numeric(df['miles_by_gps']),df['manvrng_miles_by_gps'])
    #         cargototeu=sum(pd.to_numeric(df['cargo_total_teu'])*pd.to_numeric(df['miles_by_gps'])+pd.to_numeric(df['manvrng_miles_by_gps']))/sum(pd.to_numeric(df['miles_by_gps'])+pd.to_numeric(df['manvrng_miles_by_gps']))
    #     else:
    #         cargototeu=0.0
       
    #     m_e_fuel_only_steaming_tim=round(sum(pd.to_numeric(sea['me_fuel_only_steaming_time'])/24),2)
       
    #     if not m_e_fuel_only_steaming_tim:
    #         m_e_fuel_only_steaming_tim="0.0"
    #     # #print("420",m_e_fuel_only_steaming_tim)
    #     new.append(m_e_fuel_only_steaming_tim)
       
    #     new.append(round(totalcargobyvessel['tcargo'].astype(float).sum(),2))
    #     new.append(round(totalcargobyvessel['cargoteu'].astype(float).sum(),2))
    #     # #print("nnewwwwwwwwwwwwwwwwwwwwwwww",new)
    #     new.append(round(sum(pd.to_numeric(df['transport_work'])),2))
    #     # #print("sum(df['transport_work_teu'])",)
    #     new.append(round(df['transport_work_teu'].astype(float).round(2).sum(),2))
    #     # new.append(df['transport_work'].astype(float).sum())
    #     # #print("start",new[1])
    #     if new[6]!=0:
    #         new.append(round((new[1]/new[6]),2))
    #     else:
    #         new.append(0)
    #     if new[10]!=0:
    #         new.append(round((new[1]*10**6)/new[10],2))
    #     else:
    #         new.append(0)
    #     if new[6]!=0: 
    #         new.append(round((new[3]*10**6)/new[6],2))
    #     else:
    #         new.append(0)
    #     if new[10]!=0:
    #         new.append(round(new[3]*10**6/new[10],2))
    #     else:
    #         new.append(0)
    #     if new[11]!=0:
    #         new.append(round(new[3]*10**6/new[11],2))
    #     else:
    #         new.append(0)
    # # n[15] = round((n[4] * 10 ^ 6 / n[7]), 2)
    # # n[16] = round((n[4] * 10 ^ 6 / n[11]), 2)
    # # n[17] = round((n[4] * 10 ^ 6 / n[12]), 2)
    #     # #print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRr")
    #     # #print(new)
    #     df2 = pd.DataFrame(data=new,index=["Total Fuel Consumption",
    #   "Total Fuel Consumption at Sea(Ton)",
    #   "Total Fuel Consumption at Berth(Ton)",
    #   "Total CO2 Emission (Ton)",
    #   "CO2 Emissions at sea (Ton)",
    #   "CO2 Emission at Berth (Ton)",
    #   'Total Distance Sailed (Nm)',
    #   "Total time at sea (days)",
    #   "Total Cargo (Ton)",
    #   "Total Cargo (TEU)",
    #   "Total Transport Work (Ton-Nm)",
    #   "Total Transport Work (TEU-Nm)",
    #   "Fuel consumption per distance (Ton/Nm)",
    #   "Fuel consumption per transport work (freight transport) (g/Ton*Nm)",
    #   "CO2 Emission per Distance (g/Nm)",
    #   "CO2 Emission per transport work (g/Ton*Nm)",
    #   "CO2 Emission per transport work (g/TEU*Nm)"], columns=["Value"])
    # else:
    #     t=df[df['status'] == 'IN PORT']
    #     new=[]
    #     #print("other")
    #     new.append(round(sum(o),2))
    #     # #print("two",new[0])
    #     new.append(round(sum(q),2))
    #     new.append(round(sum(p),2))
    #     new.append(round(sum(r),2))
    #     new.append(round(sum(list(np.multiply(q,m))),2))
    #     new.append(round(sum(list(np.multiply(p,m))),2))
    #     new.append(round(sum(df['miles_by_gps'].astype(float) + df['manvrng_miles_by_gps'].astype(float)),2))
    #     cargometric=pd.DataFrame()
    #     # #print(sea)
    #     sea=df[df['status'] == 'AT SEA']
    #     xcargo= sea.groupby(['imo','voyage_order'])['cargo_total'].mean().reset_index()
    #     # #print('485',df)
    #     # #print("sssssssss",xcargo)
    #     cargometric['imo']=xcargo['imo']
    #     # cargometric['cargo_total']=xcargo['cargo_total'].apply(sum)
    #     cargometric['voyage_order']=xcargo['voyage_order']
    #     # #print("416",cargometric)
    #     cargometric.sort_values(by='voyage_order', inplace=True)
    #     totalcargobyvessel=pd.DataFrame()
    #     # tcargo=cargometric.groupby(['id_vessel'])['cargo_total'].sum().reset_index()
    #     cargometric['tcargo']=xcargo['cargo_total']
    #     voyage=cargometric.groupby(['imo'])['voyage_order'].count().reset_index()
    #     print(sea)
    #     tcargo=sea.groupby(['imo'])['cargo_total'].unique().reset_index()
    #     print("490",tcargo)
        
    #     tcargo=tcargo['cargo_total'].sum()
    #     # totalcargobyvessel['tcargo']=pd.to_numeric(tcargo['cargo_total'])
    #     print(tcargo)
    #     totalcargobyvessel['voyages']=voyage['voyage_order']
    #     cargotot=(df['cargo_total_teu'].astype(float)*df['miles_by_gps'].astype(float)+(df['manvrng_miles_by_gps'].astype(float))/(df['miles_by_gps'].astype(float))+df['manvrng_miles_by_gps'].astype(float))
    #     # #print("4444420",cargotot)
    #     # cargototeu=df['cargo_total_teu'].astype(float)*(df['miles_by_gps'].astype(float)+df['manvrng_miles_by_gps'].astype(float))/(df['miles_by_gps'].astype(float)+df['manvrng_miles_by_gps'].astype(float))
    #     # totalcargobyvessel['cargoteu']=cargototeu

    #     #print(sea['me_fuel_only_steaming_time'])
    #     sea['me_fuel_only_steaming_time'] = sea['me_fuel_only_steaming_time'].replace({np.nan:None})
    #     #print(sea['me_fuel_only_steaming_time'])

    #     m_e_fuel_only_steaming_tim=sum(pd.to_numeric(sea['me_fuel_only_steaming_time'])/24)
    #     # if not m_e_fuel_only_steaming_tim:
    #     #     m_e_fuel_only_steaming_tim="0.0"
    #     #print("509",m_e_fuel_only_steaming_tim)
    #     new.append(round(m_e_fuel_only_steaming_tim,2))
  
    #     try:
    #         new.append(sum(pd.to_numeric(tcargo)))
    #     except:
    #         new.append(0)
    #     # new.append(totalcargobyvessel['cargoteu'].astype(float).sum())
    #     new.append(round(df['transport_work'].astype(float).sum(),2))
    #     # new.append(df['transport_work_teu'].astype(float).sum())
    #     # new.append(df['transport_work'].astype(float).sum())
    #     # new.append(new[1]/new[6])
    #     new.append(round(new[1]/new[6],2))
    #     new.append(round(new[3]*10**6/new[9],2))
    #     new.append(round(new[3]*10**6/new[6],2))
    #     #print(round(new[3]*10**6/new[6]))
    #     new.append(round((new[3]*10**6)/new[9],2))
    #     #print(new[3]*10**6/new[9])
    #     # #print("437",new)




    # # totalcargobyvessel['cargoteu']=cargometric
    # # #print("392",xcargo)
    # # data = data.to_json(orient="records")
    # # data = json.loads(data)
    #     df2 = pd.DataFrame(data=new,index=[ "Total Fuel Consumption",
    #   "Total Fuel Consumption at Sea(Ton)",
    #   "Total Fuel Consumption at Berth(Ton)",
    #   "Total CO2 Emission (Ton)",
    #   "CO2 Emissions at sea (Ton)",
    #   "CO2 Emission at Berth (Ton)",
    #   'Total Distance Sailed (Nm)',
    #   "Total time at sea (days)",
    #   "Total Cargo (Ton)",
    #   "Total Transport Work (Ton-Nm)",
    #   "Fuel consumption per distance (Ton/Nm)",
    #   "Fuel consumption per transport work (freight transport) (g/Ton*Nm)",
    #   "CO2 Emission per Distance (g/Nm)",
    #   "CO2 Emission per transport work (g/Ton*Nm)"], columns=["Value"])
    # #print("fdfdfdff",df2)
    #     df['fuel_hs'] = df['fuel_hs'].replace({None:0})
    # df['fuel_ls'] = df['fuel_ls'].replace({None:0})
    # df['fuel_mgo'] = df['fuel_mgo'].replace({None:0})
    # df['total_co2'] = round((df['fuel_hs'].astype(float) * 3.1144 )+ (df['fuel_ls'].astype(float) * 3.151) + (df['fuel_mgo'].astype(float) * 3.206),2)
    # print(df[['total_co2','fuel_hs','fuel_ls','fuel_mgo']])
   
    # #print("total_co2",df['total_co2'])
    # df['totalfo'] =pd.to_numeric(df['fuel_hs']) + pd.to_numeric(df['fuel_ls']) + pd.to_numeric(df['fuel_mgo']) 
    # df['co2'] = round(df['total_co2'].astype(float),2)
    # ycargo=df[df['status']=='IN PORT']
    # ucg=pd.DataFrame()
    # df[['total_co2','cargo_total','cargo_total_teu','miles_by_gps','manvrng_miles_by_gps','totalfo','transport_work','transport_work_teu']]=df[['total_co2','cargo_total','cargo_total_teu','miles_by_gps','manvrng_miles_by_gps','totalfo','transport_work','transport_work_teu']].apply(pd.to_numeric)
 
    # # xcargo1= df.groupby(['voyage_order'])['cargo_total'].sum().reset_index()
    # # df['totalfo'] = pd.to_numeric(df['totalfo'], errors='coerce').fillna(0)
    # # df['total_co2'] = pd.to_numeric(df['total_co2'], errors='coerce').fillna(0)
    # # df['transport_work'] = pd.to_numeric(df['transport_work'], errors='coerce').fillna(0)
    # # df['cargo_total_teu'] = pd.to_numeric(df['cargo_total_teu'], errors='coerce').fillna(0)
    # # df['miles_by_gps'] = pd.to_numeric(df['miles_by_gps'], errors='coerce').fillna(0)

    # result = df.groupby('voyage_order').agg({'totalfo':np.sum,'cargo_total_teu':np.mean,'total_co2': np.sum,'miles_by_gps': np.sum,'cargo_total':np.mean,'manvrng_miles_by_gps': np.sum}).reset_index()
    # # result_df = df.groupby('voyage_order')['cargo_total','transport_work'].mean().reset_index()
    # # result_df1 = df.groupby('voyage_order')['miles_by_gps','total_co2'].sum().reset_index()
    # result['distance1']=result['miles_by_gps']+result['manvrng_miles_by_gps']
    # result['distance2']=result['miles_by_gps']
    # result['distance'] = np.where(pd.to_numeric(year) <= 2019, result['distance1'], result['distance2'])
    # result['eeoi']= round((pd.to_numeric(result['total_co2']) * (10 ** 6)) /( pd.to_numeric(result['distance']) * pd.to_numeric(result['cargo_total'])),2)
    # result['eeoiTEU']= round((pd.to_numeric(result['total_co2']) * (10 ** 6)) /( pd.to_numeric(result['distance']) * pd.to_numeric(result['cargo_total_teu'])),2)


    # # ucg['cargo'] = pd.to_numeric(xcargo1['cargo_total'])
    # # teu_cargo= cargo.groupby(["vsl","voyage_order"])['teu_full','teu_
    # # empty'].unique().reset_index()
    # # ycargo['cargo_total_teu'] = pd.to_numeric(ycargo['cargo_total_teu'])
    # # teu_cargo= ycargo.groupby(['voyage_order'])['cargo_total_teu'].sum().reset_index()
    # # ucg['cargot'] = teu_cargo['cargo_total_teu']
    # # ucg['voyage_order']=teu_cargo['voyage_order']
    # #print(ucg)
    # uc=pd.DataFrame()
    # u=pd.DataFrame()
    # df['miles_by_gps'] = pd.to_numeric(df['miles_by_gps'])
    # df['manvrng_miles_by_gps'] = pd.to_numeric(df['manvrng_miles_by_gps'])

    # miles_by_gps=df.groupby(['voyage_order'])[['miles_by_gps','manvrng_miles_by_gps']].sum().reset_index()
    # #print("488",miles_by_gps)
    # # manvrng_miles_by_gps=df.groupby(['voyage_order'])['manvrng_miles_by_gps'].sum().reset_index()
    # # uc['mil']=pd.to_numeric(miles_by_gps['miles_by_gps'])+pd.to_numeric(miles_by_gps['manvrng_miles_by_gps'])
    # # tw=df.groupby(['voyage_order'])['transport_work'].sum().reset_index()
    # # uc['tw']=tw['transport_work']
    # # twt=df.groupby(['voyage_order'])['transport_work_teu'].sum().reset_index()
    # # uc['twt']=twt['transport_work_teu']
    # # uc['voyage_order']=tw['voyage_order']
    # #print("492",uc)
    
    # # uxc=pd.merge(ucg,uc,on='voyage_order')
    # # co=df.groupby(['eeoi_voyage_no'])['co2'].sum().reset_index()
    # # totalfo=df.groupby(['eeoi_voyage_no'])['totalfo'].sum().reset_index()
    # # u['co']=co['co2']
    # # u['totalfo']=totalfo['totalfo']
    # # u['eeoi_voyage_no']=totalfo['eeoi_voyage_no']
    # # new_df = pd.merge(A_df, B_df,  how='left', left_on=['A_c1','c2'], right_on = ['B_c1','c2'])

    # # ux=pd.merge(uxc,u,left_on='voyage_order',right_on='eeoi_voyage_no')

    # # ux = merge(uxc, u, by.x = "Voyage_Order", by.y = "EEOI_Voyage_no")
    # # ux['EEOI'] = (pd.to_numeric(ux['co']) * (10 ** 6)) / pd.to_numeric(ux['mil']) * pd.to_numeric(ux['cargo'])
    # # #print(ux['mil'],ux['cargot'],ux['co'])
    # # ux['eeoit'] = (pd.to_numeric(ux['co']) * (10 ** 6)) / pd.to_numeric(ux['mil'])*pd.to_numeric(ux['cargot'])
    # # u['ee_polt11'] =ux.groupby('voyage_order')['co'].transform(lambda x: (x*(10**6)).sum())
    # # u['eeoi']=round(ux['EEOI'],2)
    # # u['eeoit']=round(ux['eeoit'],2)

    # #  ddply(y, .(Voyage_Order), summarize, ee =j (co * 10 ^ 6) / tw)
    # # u['ee_polt12'] =ux.groupby('voyage_order')['co','twt'].transform(lambda x,y: (x.sum()*10**6)/y)

    # # u['ee_polt11']=pd.to_numeric(u['ee_polt11'])/pd.to_numeric(twt['transport_work_teu'])
    # # print("dddddddddd",u)
   
    # df1=df1.round(2)
    # df1['fuel_cons_details']=df1.index

    # df1 = df1.to_json(orient="records")
    # table1 = json.loads(df1)
    # df2['index']=df2.index
    # df2 = df2.replace({np.nan:None})
    
    # df2=df2.round(2)
    # df2 = df2.to_json(orient="records")
    # reported_data = json.loads(df2)
    # #print(u)
    # # eechart = u
    # # eechart['ee_polt11'] = round(eechart['ee_polt11'],2)
    # result.rename(columns={'voyage_order':'voyage_no','total_co2':'co2'}, inplace = True)
    # eechart=result.to_json(orient="records")
    # eechart = json.loads(eechart)
   

    # return {"table1":table1,"reported_data":reported_data,"eechartdata":eechart}

    
@router.get('/api/v1/eeoi_mrv/vwr/{imo}')#, response_model=vessel_schema.Response
def index(v_db:Session = Depends(get_vdm_db),db:Session= Depends(get_db),imo:str=None,date1:date=None,date2:date=None,emtypevf:str=None,passage:str=None,EMvoyageno:str=None,vtype:str=None,vessel_type:str=None,token : Session = Depends(get_token)):
    data = cache_set.get_viewr_report(db,imo)
 
    if not data:
        return []
    # return data

    viewer=pd.DataFrame(data)
    #print("1",viewer)
    viewer['report_date_time']=pd.to_datetime(viewer['report_date_time']).dt.strftime('%Y-%m-%d')
    
    viewer=viewer[(pd.to_datetime(viewer['report_date_time']) >= pd.to_datetime(str(date1))) & (pd.to_datetime(viewer['report_date_time']) <= pd.to_datetime(date2))]

    viewer=viewer[(viewer['voyage_order']!="") | (viewer['voyage_order']!=None)]
    viewer['year'] = pd.to_datetime(viewer['corrected_date']).dt.year
    viewer['report_date_time']=pd.to_datetime(viewer['report_date_time']).dt.strftime('%d %b %Y')

    if emtypevf=="All Voyages":
        viewer=viewer[viewer['report_type']!="REFL"]

    else:
        viewer=viewer[(viewer['report_type']!="REFL") & (viewer['eu']=="Y")]
    
    viewer.loc[pd.to_numeric(viewer['cargo_total']) == 0, 'voy_condition'] = 'Ballast' 
    viewer.loc[pd.to_numeric(viewer['cargo_total'])  !=0, 'voy_condition'] = 'Laden' 
    viewer=viewer[viewer['voyage_order']==str(float(EMvoyageno))]
    if len(viewer)==0:
        return []
      
    viewer=viewer[viewer['voyage_code']==str(passage)]
    if len(viewer)==0:
        return []
    
    viewer['manvrng_miles_by_gps'] = viewer['manvrng_miles_by_gps'].replace({np.nan:0})
    viewer['miles_by_gps'] = viewer['miles_by_gps'].replace({np.nan:0})
    viewer['manvrng_miles_by_gps'] = viewer['manvrng_miles_by_gps'].replace({np.nan:0})
    viewer=viewer.fillna(0)
    viewer['fuel_hs'] =  pd.to_numeric(viewer['fuel_me_hs']) + pd.to_numeric(viewer['fuel_aux_hs']) + pd.to_numeric(viewer['fuel_boiler_hs'])
    viewer['fuel_ls'] =  pd.to_numeric(viewer['fuel_me_ls'])+  pd.to_numeric(viewer['fuel_aux_ls'])+  pd.to_numeric(viewer['fuel_boiler_ls'])
    viewer['fuel_mdo'] = pd.to_numeric(viewer['fuel_me_mdo'])+ pd.to_numeric(viewer['fuel_aux_mdo'])+ pd.to_numeric(viewer['fuel_boiler_mdo'])
    viewer['fuel_mgo'] = pd.to_numeric(viewer['fuel_me_mgo'])+ pd.to_numeric(viewer['fuel_aux_mgo'])+ pd.to_numeric(viewer['fuel_boiler_mgo'])+ pd.to_numeric(viewer['fuel_me_mgo_ls'])+ pd.to_numeric(viewer['fuel_boiler_mgo_ls'])+ pd.to_numeric(viewer['fuel_aux_mgo_ls'])
    viewer['fuel_mdo'] = np.where(pd.to_numeric(viewer['fuel_mdo']) < 2020, viewer['fuel_mdo'], None)
    viewer['fuel_mgo_ls'] = np.where(pd.to_numeric(viewer['fuel_mdo']) < 2020, viewer['fuel_mgo_ls'], None)
    
    
    
    m=[3.114, 3.151, 3.206, 3.206, 3.206]
    n=[4.5, 3.5, 1.5, 1.5, 1.5]
    #print(viewer['fuel_hs'],viewer['fuel_ls'],viewer['fuel_mdo'],viewer['fuel_mgo'],viewer['fuel_mgo_ls'])
    o = [
    round(pd.to_numeric(viewer['fuel_hs']).sum(),2),
    round(pd.to_numeric(viewer['fuel_ls']).sum(),2),
    round(pd.to_numeric(viewer['fuel_mdo']).sum(),2),
    round(pd.to_numeric(viewer['fuel_mgo']).sum(),2),
    round(pd.to_numeric(viewer['fuel_mgo_ls']).sum(),2)]
   
    sea=viewer[viewer['status'] == 'AT SEA']

    q=[
    round(pd.to_numeric(sea['fuel_hs']).sum(),2),
    round(pd.to_numeric(sea['fuel_ls']).sum(),2),
    round(pd.to_numeric(sea['fuel_mdo']).sum(),2),
    round(pd.to_numeric(sea['fuel_mgo']).sum(),2),
    round(pd.to_numeric(sea['fuel_mgo_ls']).sum(),2)]

    port=viewer[(viewer['status'] == 'IN PORT') | (viewer['status'] == 'DRIFTING')]

    p=[
    round(pd.to_numeric(port['fuel_hs']).sum(),2),
    round(pd.to_numeric(port['fuel_ls']).sum(),2),
    round(pd.to_numeric(port['fuel_mdo']).sum(),2),
    round(pd.to_numeric(port['fuel_mgo']).sum(),2),
    round(pd.to_numeric(port['fuel_mgo_ls']).sum(),2)]


    r= np.multiply(m,o)
    # r=round(r,2)
    s=np.multiply(n,o)*20/1000
    s=np.around(np.array(s), 2)

    new_array=[m,n,o,p,q,r,s]
    df1 = pd.DataFrame(data=new_array,index=["Emission factor (Ton-CO2/Ton-Fuel)", "Sulphur content [%]",  "Total Fuel (Ton)",  "Fuel at Berth (Ton)",  "Fuel at Sea (Ton)",  "Total CO2 (Ton)", "Total SOx (Ton)"], columns=["Fuel(HS)","Fuel (LS)","Fuel (MDO)","Fuel (MGO)","Fuel (MGO)LS"])
    



   
    new=[]
    # if vessel_type=="Container":
    new.append(round(sum(o),2))
    new.append(round(sum(q),2))
    new.append(round(sum(p),2))
    new.append(round(sum(r),2))
    new.append(round(sum(np.multiply(q,m)),2))
    new.append(round(sum(np.multiply(p,m)),2))
    new.append(sum(pd.to_numeric(viewer['miles_by_gps']) + pd.to_numeric(viewer['manvrng_miles_by_gps'])))
    m_e_fuel_only_steaming_tim=round(sum(pd.to_numeric(sea['me_fuel_only_steaming_time'])/24),2)
 
    if not m_e_fuel_only_steaming_tim:
        m_e_fuel_only_steaming_tim="0.0"
    # #print("420",m_e_fuel_only_steaming_tim)
    new.append(m_e_fuel_only_steaming_tim)
    #print("dfdff",new)
    viewer['cargo_total']=pd.to_numeric(viewer['cargo_total'])
    #print(viewer['miles_by_gps']+viewer['manvrng_miles_by_gps'],viewer['cargo_total'])
    viewer['transport_work'] =(pd.to_numeric(viewer['miles_by_gps']) + pd.to_numeric(viewer['manvrng_miles_by_gps'])) * pd.to_numeric(viewer['cargo_total'])
    viewer['transport_work_teu'] = (pd.to_numeric(viewer['miles_by_gps']) +  pd.to_numeric(viewer['manvrng_miles_by_gps'])) * pd.to_numeric(viewer['cargo_total_teu'])
    viewer['transport_work_teu'] = viewer['transport_work_teu'].replace({np.nan:0})
    viewer['fuel_hs'] = viewer['fuel_hs'].replace({np.nan:0})
    viewer['fuel_ls'] = viewer['fuel_ls'].replace({np.nan:0})
    viewer['fuel_mdo'] = viewer['fuel_mdo'].replace({np.nan:0})
    viewer['fuel_mgo'] = viewer['fuel_mgo'].replace({np.nan:0})
    viewer['fuel_mgo_ls'] = viewer['fuel_mgo_ls'].replace({np.nan:0})


    viewer['total_co2'] = pd.to_numeric(viewer['fuel_hs']) * 3.1144 + pd.to_numeric(viewer['fuel_ls']) * 3.151 + pd.to_numeric(viewer['fuel_mdo']) + pd.to_numeric(viewer['fuel_mgo']) + pd.to_numeric(viewer['fuel_mgo_ls']) * 3.206
    viewer['totalfo'] =pd.to_numeric(viewer['fuel_hs']) + pd.to_numeric(viewer['fuel_ls']) + pd.to_numeric(viewer['fuel_mdo']) + pd.to_numeric(viewer['fuel_mgo']) +pd.to_numeric(viewer['fuel_mgo_ls'])
    # viewer['cargo_total_teu'] = pd.to_numeric(viewer['cargo_total_teu'], errors='coerce')
    viewer['total_co2'] = viewer['total_co2'].replace({np.nan:0})
   
# Convert columns to numeric, coercing non-convertible values to NaN
    viewer['transport_work'] = pd.to_numeric(viewer['transport_work'], errors='coerce')
    viewer['transport_work_teu'] = pd.to_numeric(viewer['transport_work_teu'], errors='coerce')
    viewer['cargo_total_teu'] = pd.to_numeric(viewer['cargo_total_teu'], errors='coerce')
    viewer['total_co2'] = pd.to_numeric(viewer['total_co2'], errors='coerce')
    viewer['miles_by_gps'] = pd.to_numeric(viewer['miles_by_gps'], errors='coerce')
    viewer['cargo_total'] = pd.to_numeric(viewer['cargo_total'], errors='coerce')
    viewer['manvrng_miles_by_gps'] = pd.to_numeric(viewer['manvrng_miles_by_gps'], errors='coerce')
    viewer['totalfo'] = pd.to_numeric(viewer['totalfo'], errors='coerce')
    viewer['teu_full'] = pd.to_numeric(viewer['teu_full'], errors='coerce')
    viewer['teu_empty'] = pd.to_numeric(viewer['teu_empty'], errors='coerce')


   

   

    # Group by specified columns and aggregate functions
    cargometric = viewer.groupby(['imo', 'voyage_order', 'report_date_time']).agg({
        'transport_work': np.sum,
        'transport_work_teu': np.sum,
        'cargo_total_teu': np.mean,  # Assuming this is the column with issues
        'total_co2': np.sum,
        'miles_by_gps': np.sum,
        'cargo_total': np.mean,
        'manvrng_miles_by_gps': np.sum,
        'totalfo': np.sum,
        'teu_full': np.mean,
        'teu_empty': np.mean
    }).reset_index()
    # cargometric = viewer.groupby(['imo','voyage_order','report_date_time']).agg({'transport_work':np.sum,'transport_work_teu':np.sum ,'cargo_total_teu':np.mean,'total_co2': np.sum,'miles_by_gps': np.sum,'cargo_total':np.mean,'manvrng_miles_by_gps': np.sum,'totalfo': np.sum,'teu_full':np.mean,'teu_empty':np.mean}).reset_index()
    cargometric['eeoi']=round((pd.to_numeric(cargometric['total_co2']) * (10 ** 6)) / (pd.to_numeric(cargometric['miles_by_gps']) *pd.to_numeric(cargometric['cargo_total'])),2)
    cargometric['eeoit'] = round((pd.to_numeric(cargometric['total_co2']) * (10 ** 6)) / (pd.to_numeric(cargometric['miles_by_gps']) * pd.to_numeric(cargometric['cargo_total_teu'])),2)
    print(cargometric)
    new.append(round(cargometric['cargo_total'][0],2))
    if vessel_type == 'Container':
        new.append(round(cargometric['cargo_total_teu'][0],2))
    new.append(round(float(cargometric['transport_work'].sum()),2))
    if vessel_type == 'Container':
        new.append(round(float(cargometric['transport_work_teu'].sum()),2))
    try:
        new.append(round(new[0]/new[6],2))
    except:
        new.append(0.0)
    if vessel_type == 'Container':
    
        try:
            new.append(round(new[0]*(10**6)/new[10],2))
        except:
            new.append(0.0)
    else:
        try:
            new.append(round(new[0]*(10**6)/new[9],2))
        except:
            new.append(0.0)
    
    try:
        new.append(round((new[3]*(10**6))/new[6],2))
    except:
        new.append(0.0)
    if vessel_type == 'Container':
    
        try:
            new.append(round((new[3]*(10**6))/new[10],2))
        except:
            new.append(0.0)
    else:
        try:
            new.append(round((new[3]*(10**6))/new[9],2))
        except:
            new.append(0.0)

    if vessel_type == 'Container':
        try:
            new.append(round((new[3]*(10**6))/new[11],2))
        except:
            new.append(0.0)
    
    
        df2 = pd.DataFrame(data=new,index=["Total Fuel Consumption",
      "Total Fuel Consumption at Sea(Ton)",
      "Total Fuel Consumption at Berth(Ton)",
      "Total CO2 Emission (Ton)",
      "CO2 Emissions at sea (Ton)",
      "CO2 Emission at Berth (Ton)",
      'Total Distance Sailed (Nm)',
      "Total time at sea (days)",
      "Total Cargo (Ton)",
      "Total Cargo (TEU)",
      "Total Transport Work (Ton-Nm)",
      "Total Transport Work (TEU-Nm)",
      "Fuel consumption per distance (Ton/Nm)",
      "Fuel consumption per transport work (freight transport) (g/Ton*Nm)",
      "CO2 Emission per Distance (g/Nm)",
      "CO2 Emission per transport work (g/Ton*Nm)",
      "CO2 Emission per transport work (g/TEU*Nm)"], columns=["Value"])
    else:
        df2 = pd.DataFrame(data=new,index=[ "Total Fuel Consumption",
      "Total Fuel Consumption at Sea(Ton)",
      "Total Fuel Consumption at Berth(Ton)",
      "Total CO2 Emission (Ton)",
      "CO2 Emissions at sea (Ton)",
      "CO2 Emission at Berth (Ton)",
      'Total Distance Sailed (Nm)',
      "Total time at sea (days)",
      "Total Cargo (Ton)",
      "Total Transport Work (Ton-Nm)",
      "Fuel consumption per distance (Ton/Nm)",
      "Fuel consumption per transport work (freight transport) (g/Ton*Nm)",
      "CO2 Emission per Distance (g/Nm)",
      "CO2 Emission per transport work (g/Ton*Nm)"], columns=["Value"])
    pie=pd.DataFrame()
    pie['voy_condition']=viewer['voy_condition'].unique()
    pie['voyage_no']=pd.to_numeric(viewer['voyage_order'].unique())
    
    cargometric.rename(columns={'report_date_time':'date','total_co2':'total_co_2','totalfo':'foc'}, inplace = True)
    df1['index']=df1.index
    df2['index']=df2.index
    df2 = df2.to_json(orient="records")
    reported_data = json.loads(df2)
    df1 = df1.to_json(orient="records")

    table1 = json.loads(df1)
    ee = cargometric[['eeoit','eeoi','date','total_co_2','foc']].round(2).to_json(orient="records")
    ee = json.loads(ee)
    pie = pie.to_json(orient="records")
    pie = json.loads(pie)
    return {"table1":table1,"reported_data":reported_data,"EECHARTDATA":ee,"pie_chart":pie}

    



    #     viewer['transport_work'] =( (pd.to_numeric(viewer['miles_by_gps']) + pd.to_numeric(viewer['manvrng_miles_by_gps'])) * pd.to_numeric(viewer['cargo_total']))
    #     viewer['transport_work_teu'] = (pd.to_numeric(viewer['miles_by_gps']) +  pd.to_numeric(viewer['manvrng_miles_by_gps'])) * pd.to_numeric(viewer['cargo_total_teu'])
    #     viewer['transport_work_teu'] = viewer['transport_work_teu'].replace({np.nan:0})
    
    #     cargometric=pd.DataFrame()
    #     # xcargo= sea.groupby(['imo','voyage_order'])['cargo_total'].mean().reset_index()

    #     # cargometric['cargo_total']=xcargo['cargo_total']
    #     # cargometric['imo']=xcargo['imo']
    #     sea['teu_full']=pd.to_numeric(sea['teu_full'])
    #     sea['teu_empty']=pd.to_numeric(sea['teu_empty'])
    #     sea['cargoteu'] = sea['teu_full'].astype(float)+sea['teu_empty'].astype(float)
    #     sea['totalfo'] =pd.to_numeric(sea['fuel_hs']) + pd.to_numeric(sea['fuel_ls']) + pd.to_numeric(sea['fuel_mdo']) + pd.to_numeric(sea['fuel_mgo']) +pd.to_numeric(sea['fuel_mgo_ls'])

    #     sea['total_co2'] = pd.to_numeric(sea['fuel_hs']) * 3.1144 + pd.to_numeric(sea['fuel_ls']) * 3.151 + pd.to_numeric(sea['fuel_mdo']) + pd.to_numeric(sea['fuel_mgo']) + pd.to_numeric(sea['fuel_mgo_ls']) * 3.206
        
    #     cargometric = sea.groupby(['imo','voyage_order']).agg({'transport_work':np.sum,'transport_work_teu':np.sum ,'cargoteu':np.mean,'total_co2': np.sum,'miles_by_gps': np.sum,'cargo_total':np.mean,'manvrng_miles_by_gps': np.sum,'totalfo': np.sum,'teu_full':np.mean,'teu_empty':np.mean}).reset_index()
    #     m_e_fuel_only_steaming_tim=round(sum(pd.to_numeric(sea['me_fuel_only_steaming_time'])/24),2)
    #     # teu_full= sea.groupby(['imo','voyage_order'])['teu_full'].mean().reset_index()
    #     # cargometric['teu_full']=teu_full['teu_full']

    #     # teu_empty= sea.groupby(['imo','voyage_order'])['teu_empty'].mean().reset_index()
    #     # cargometric['teu_empty']=teu_empty['teu_empty']

    #     # cargometric['cargoteu'] = teu_full['teu_full'].astype(float)+teu_empty['teu_empty'].astype(float)
    #     # cargometric['imo']=teu_full['imo']
    #     # cargometric['voyage_order']=teu_full['voyage_order']
   
    #     cargometric.sort_values(by='voyage_order', inplace=True)
    #     totalcargobyvessel=pd.DataFrame()
        
    #     # tcargo=cargometric.groupby(['imo'])['cargo_total'].mean().reset_index()
    #     # totalcargobyvessel['tcargo']=tcargo['cargo_total']
    #     # cargoteu=cargometric.groupby(['imo'])['cargoteu'].mean().reset_index()
    #     # totalcargobyvessel['cargoteu'] =cargoteu['cargoteu']
    #     # voyages=cargometric.groupby(['imo'])['voyage_order'].count().reset_index()
    #     # totalcargobyvessel['voyages'] = voyages['voyage_order']
    #     totalcargobyvessel = cargometric.groupby(['imo']).agg({'transport_work':np.sum,'transport_work_teu':np.sum ,'cargoteu':np.mean,'total_co2': np.sum,'miles_by_gps': np.sum,'cargo_total':np.mean,'manvrng_miles_by_gps': np.sum,'totalfo': np.sum,'voyage_order': 'count'}).reset_index()
        

    #     new.append(round(totalcargobyvessel['cargo_total'].astype(float).sum(),2))
    #     new.append(round(totalcargobyvessel['cargoteu'].astype(float).sum(),2))
    #     new.append(round(sum(pd.to_numeric(viewer['transport_work'])),2))
    #     new.append(round(sum(pd.to_numeric(viewer['transport_work_teu'])),2))
    #     # new.append(df['transport_work'].astype(float).sum())
    #     try:
    #         new.append(round(new[1]/new[6],2))
    #     except:
    #         new.append(0.0)
    #     try:
    #         new.append(round((new[1]*10**6)/new[10],2))
    #     except:
    #         new.append(0.0)
    #     try:
    #         new.append(round((new[3]*10**6)/new[6],2))
    #     except:
    #         new.append(0.0)
    #     try:
    #         new.append(round(new[3]*10**6/new[10],2))
    #     except:
    #         new.append(0.0)
    #     try:
    #         new.append(round((new[3]*10**6)/new[11],2))
    #     except:
    #         new.append(0.0)
        
    
    #     df2 = pd.DataFrame(data=new,index=["Total Fuel Consumption",
    #   "Total Fuel Consumption at Sea(Ton)",
    #   "Total Fuel Consumption at Berth(Ton)",
    #   "Total CO2 Emission (Ton)",
    #   "CO2 Emissions at sea (Ton)",
    #   "CO2 Emission at Berth (Ton)",
    #   'Total Distance Sailed (Nm)',
    #   "Total time at sea (days)",
    #   "Total Cargo (Ton)",
    #   "Total Cargo (TEU)",
    #   "Total Transport Work (Ton-Nm)",
    #   "Total Transport Work (TEU-Nm)",
    #   "Fuel consumption per distance (Ton/Nm)",
    #   "Fuel consumption per transport work (freight transport) (g/Ton*Nm)",
    #   "CO2 Emission per Distance (g/Nm)",
    #   "CO2 Emission per transport work (g/Ton*Nm)",
    #   "CO2 Emission per transport work (g/TEU*Nm)"], columns=["Value"])
    # else:
    #     t=viewer[viewer['status'] == 'IN PORT']
    #     new=[]
    #     new.append(round(sum(o),2))

    #     new.append(round(sum(q),2))
    #     new.append(round(sum(p),2))
    #     new.append(round(sum(r),2))
    #     new.append(round(sum(list(np.multiply(q,m))),2))
    #     new.append(round(sum(list(np.multiply(p,m))),2))
    #     new.append(round(sum(viewer['miles_by_gps'].astype(float) + viewer['manvrng_miles_by_gps'].astype(float)),2))
    #     cargometric=pd.DataFrame()
    #     # #print(sea)
    #     sea=viewer[viewer['status'] == 'AT SEA']
        
    #     sea['cargo_total']=pd.to_numeric(sea['cargo_total'])
    #     xcargo= sea.groupby(['voyage_order','imo'])['cargo_total'].sum().reset_index()
    #     #print(xcargo)
    #     cargometric['imo']=xcargo['imo']
    #     # cargometric['cargo_total']=xcargo['cargo_total'].apply(sum)
    #     cargometric['voyage_order']=xcargo['voyage_order']
       
    #     cargometric.sort_values(by='voyage_order', inplace=True)
    #     totalcargobyvessel=pd.DataFrame()
        
    #     cargometric['tcargo']=xcargo['cargo_total']
    #     voyage=cargometric.groupby(['imo'])['voyage_order'].count().reset_index()
    #     # xcargo['cargo_total']=pd.to_numeric(xcargo['cargo_total'])
    #     # tcargo=xcargo.groupby(['imo'])['cargo_total'].unique().sum()
    #     sea['cargo_total']=pd.to_numeric(sea['cargo_total'])
    #     xcargo= sea.groupby(['imo','voyage_order'])['cargo_total'].unique().reset_index()

    #     cargometric['cargo_total']=xcargo['cargo_total'].apply(sum)
    #     tcargo=cargometric.groupby(['imo'])['cargo_total'].sum().reset_index()
    #     # print("fffffffffffffgggggggggggggttttttttttt",tcargo['cargo_total'])
    #     # tcargo['cargo_total'] = tcargo['cargo_total'].apply(', '.join).apply(lambda x: ','.join(map(str, x)))
    #     # teu_full['teu_full'] = teu_full['teu_full'].apply(lambda x: ','.join(map(str, x)))

    #     totalcargobyvessel['voyages']=voyage['voyage_order']
    #     totalcargobyvessel['tcargo']=tcargo['cargo_total']
    #     cargotot=(viewer['cargo_total_teu'].astype(float)*viewer['miles_by_gps'].astype(float)+(viewer['manvrng_miles_by_gps'].astype(float))/(viewer['miles_by_gps'].astype(float))+viewer['manvrng_miles_by_gps'].astype(float))
   
    #     sea['me_fuel_only_steaming_time'] = sea['me_fuel_only_steaming_time'].replace({np.nan:None})
       

    #     m_e_fuel_only_steaming_tim=sum(pd.to_numeric(sea['me_fuel_only_steaming_time'])/24)
    #     # tcargo['cargo_total']=pd.to_numeric(tcargo['cargo_total'])

    #     new.append(round(m_e_fuel_only_steaming_tim,2))
      
    #     try:
    #         new.append(round(pd.to_numeric(totalcargobyvessel['tcargo']).sum(),2))
    #     except:
    #         new.append(0)
       
    #     new.append(round(viewer['transport_work'].astype(float).sum(),2))
       
    #     new.append(round(new[1]/new[6],2))
    #     new.append(round(new[3]*10**6/new[9],2))
    #     if new[3] and new[6]:
    #         new.append(round(new[3]*10**6/new[6],2))
    #     else:
    #         new.append(0)
       
    #     new.append(round((new[3]*10**6)/new[9],2))
       
     
    #     df2 = pd.DataFrame(data=new,index=[ "Total Fuel Consumption",
    #   "Total Fuel Consumption at Sea(Ton)",
    #   "Total Fuel Consumption at Berth(Ton)",
    #   "Total CO2 Emission (Ton)",
    #   "CO2 Emissions at sea (Ton)",
    #   "CO2 Emission at Berth (Ton)",
    #   'Total Distance Sailed (Nm)',
    #   "Total time at sea (days)",
    #   "Total Cargo (Ton)",
    #   "Total Transport Work (Ton-Nm)",
    #   "Fuel consumption per distance (Ton/Nm)",
    #   "Fuel consumption per transport work (freight transport) (g/Ton*Nm)",
    #   "CO2 Emission per Distance (g/Nm)",
    #   "CO2 Emission per transport work (g/Ton*Nm)"], columns=["Value"])
      
    #     viewer['total_co2'] = pd.to_numeric(viewer['fuel_hs']) * 3.1144 + pd.to_numeric(viewer['fuel_ls']) * 3.151 + pd.to_numeric(viewer['fuel_mdo']) + pd.to_numeric(viewer['fuel_mgo']) + pd.to_numeric(viewer['fuel_mgo_ls']) * 3.206
    #     viewer['totalfo'] =pd.to_numeric(viewer['fuel_hs']) + pd.to_numeric(viewer['fuel_ls']) + pd.to_numeric(viewer['fuel_mdo']) + pd.to_numeric(viewer['fuel_mgo']) + pd.to_numeric(viewer['fuel_mgo_ls'])
    #     viewer['co2'] = pd.to_numeric(viewer['total_co2'])
    #     ycargo=viewer.copy()
    #     ycargo=ycargo[ycargo['status']=='IN PORT']
    #     ucg=pd.DataFrame()
    #     ycargo['cargo_total']=pd.to_numeric(ycargo['cargo_total'])
    #     xcargo1= ycargo.groupby(['voyage_order'])['cargo_total'].mean().reset_index()
    #     ucg['cargo'] = pd.to_numeric(xcargo1['cargo_total'])
        
    # viewer['total_co2'] = pd.to_numeric(viewer['fuel_hs']) * 3.1144 + pd.to_numeric(viewer['fuel_ls']) * 3.151 + pd.to_numeric(viewer['fuel_mdo']) + pd.to_numeric(viewer['fuel_mgo']) + pd.to_numeric(viewer['fuel_mgo_ls']) * 3.206
    # viewer['totalfo'] =pd.to_numeric(viewer['fuel_hs']) + pd.to_numeric(viewer['fuel_ls']) + pd.to_numeric(viewer['fuel_mdo']) + pd.to_numeric(viewer['fuel_mgo']) +pd.to_numeric(viewer['fuel_mgo_ls'])
    # # viewer['co2'] =pd.to_numeric(viewer['total_co2'])
    # #print(viewer['status'])
    # ycargo = viewer[viewer['status'] == "AT SEA"]
    
    # ycargo['cargo_total_teu'] = pd.to_numeric(ycargo['cargo_total_teu'])
    # ycargo['cargo_total'] = pd.to_numeric(ycargo['cargo_total'])
    # ycargo[['cargo_total_teu','cargo_total','miles_by_gps','manvrng_miles_by_gps','transport_work','transport_work_teu']] = ycargo[['cargo_total_teu','cargo_total','miles_by_gps','manvrng_miles_by_gps','transport_work','transport_work_teu']].apply(pd.to_numeric)
    # #print(ycargo)
    # if ycargo.empty:
    #     return []
    # # cargoteu  = ycargo.groupby(['voyage_order'])[['cargo_total','cargo_total_teu','miles_by_gps','manvrng_miles_by_gps','transport_work','transport_work_teu']].sum().reset_index()
    # cargoteu = ycargo.groupby(['voyage_order','corrected_date']).agg({'transport_work':np.sum,'transport_work_teu':np.sum ,'cargo_total_teu':np.mean,'total_co2': np.sum,'miles_by_gps': np.sum,'cargo_total':np.mean,'manvrng_miles_by_gps': np.sum,'totalfo': np.sum}).reset_index()
    # #print("cargoteu",cargoteu['miles_by_gps'])
    # # cargoteu[['cargo_total_teu','cargo_total','miles_by_gps','manvrng_miles_by_gps','transport_work','transport_work_teu']] = cargoteu[['cargo_total_teu','cargo_total','miles_by_gps','manvrng_miles_by_gps','transport_work','transport_work_teu']].apply(pd.to_numeric)
    # cargoteu['cargo']=cargoteu['cargo_total']
    # cargoteu['cargot']=cargoteu['cargo_total_teu']
    # cargoteu['mil'] = np.where(cargoteu['miles_by_gps'] == cargoteu['manvrng_miles_by_gps'], cargoteu['miles_by_gps'] + cargoteu['manvrng_miles_by_gps'], cargoteu['miles_by_gps'])
    # # cargoteu['mil']=pd.to_numeric(cargoteu['miles_by_gps'])+pd.to_numeric(cargoteu['manvrng_miles_by_gps'])
    # cargoteu['tw']=pd.to_numeric(cargoteu['transport_work'])
    # cargoteu['twt']=pd.to_numeric(cargoteu['transport_work_teu'])
   
    # # u  = ycargo.groupby(['eeoi_voyage_no','corrected_date'])[['co2','totalfo']].sum().reset_index()
    
    # # ux = pd.merge(u, cargoteu,how='left', left_on=['eeoi_voyage_no'], right_on = ['voyage_order'])

    # cargoteu['eeoi']=round((pd.to_numeric(cargoteu['total_co2']) * (10 ** 6)) / (pd.to_numeric(cargoteu['mil']) *pd.to_numeric(cargoteu['cargo'])),2)
    # cargoteu['eeoit'] = round((pd.to_numeric(cargoteu['total_co2']) * (10 ** 6)) / (pd.to_numeric(cargoteu['mil']) * pd.to_numeric(cargoteu['cargot'])),2)
    # cargoteu.rename(columns={'corrected_date':'date','total_co2':'total_co_2','totalfo':'foc'}, inplace = True)
   
    # pie=pd.DataFrame()
    # pie['voy_condition']=ycargo['voy_condition'].unique()
    # pie['voyage_no']=pd.to_numeric(ycargo['eeoi_voyage_no'].unique())
    # cargoteu = round(cargoteu,2)
    # df1=df1.round(2)
    # df1['index']=df1.index
    # df1 = df1.to_json(orient="records")
    # table1 = json.loads(df1)
    # df2['index']=df2.index
    # df2 = df2.to_json(orient="records")
    # reported_data = json.loads(df2)
  
    # cargoteu['date']=pd.to_datetime(cargoteu['date']).dt.strftime('%d %b %Y')
   
    # ee = cargoteu[['eeoit','eeoi','date','total_co_2','foc']].to_json(orient="records")
    # ee = json.loads(ee)
    # pie = pie.to_json(orient="records")
    # pie = json.loads(pie)
   
    # return {"table1":table1,"reported_data":reported_data,"EECHARTDATA":ee,"pie_chart":pie}

# =======================new

def get_yearanalysis_wise(df1,year1,eeoigoalmt,moving_average):
    df1['corrected_date'] = pd.to_datetime(df1['corrected_date'])
    # df=df[(pd.to_datetime(df['corrected_date']) >= pd.to_datetime(pdate1)) & (pd.to_datetime(df['corrected_date']) <= pd.to_datetime(pdate2))]
    #print(df1.count())
    df1=df1[df1['report_type']!="REFL"]
    

    
    df1=df1[(df1['corrected_date'].dt.year)==int(year1)]
    df1['corrected_date']=df1['corrected_date'].dt.strftime('%Y-%m-%d')
    if  df1.empty:
        return df1 
    df1['voyage_order']=df1['voyage_order'].ffill().bfill()
    
    # plot['teu_transport_work'] = np.where(new['eeoitype'] == "1", new['teu_transport_work'], None)
    cargometric=pd.DataFrame()
    eeoidata=pd.DataFrame()
    df1['cargo_total'] = df1['cargo_total'].replace({np.nan:0})
    df1['cargo_total']=pd.to_numeric(df1['cargo_total'])
    df1['cargo_total_teu']=pd.to_numeric(df1['cargo_total_teu'], errors='coerce')
    # df1['teu_full'] = pd.to_numeric(df1['teu_full'], errors='coerce').fillna(0)

    # df1.rename(columns={'eeoigoalteu1':'eeoigoalteu2'}, inplace = True)
    
    

    # Further group by 'imo' and sum the cargo metrics
    




    # Obtain unique values
    # teucargo = df1.groupby(['imo', 'voyage_order'])[['teu_full', 'teu_empty']].agg(lambda x: x.unique().tolist()).reset_index()

    # Combine unique values into a new column
    # teucargo['teucargo'] = teucargo.apply(lambda row: sum(row['teu_full']) + sum(row['teu_empty']), axis=1)

    # Group by 'imo' and 'voyage_order' and calculate the sum of the new column
    # df1['cargo_total_teu']=pd.to_numeric(df1['cargo_total_teu'])

    # teucargo= df1.groupby(['imo','voyage_order'])['cargo_total_teu'].unique().reset_index()
    # # xcargo=xcargo[xcargo['imo']=='9062984']
    # cargometric['teucargo'] =teucargo['cargo_total_teu'].apply(sum)

    
    # teucargo= df1.groupby(['imo', 'voyage_order'])['cargo_total_teu'].mean().reset_index()
    

    # cargometric['teucargo']=teucargo['teu_full'] 
    
    df1[['distance_covered', 'manvrng_miles_by_gps','miles_by_gps','cargo_transport_work','fuel_hs','fuel_ls','fuel_mdo','fuel_mgo','fuel_mgo_ls','teu_transport_work','fuel_me_rsdl_hs','fuel_aux_rsdl_hs','fuel_boiler_rsdl_hs','fuel_me_rsdl_vls','fuel_aux_rsdl_vls','fuel_boiler_rsdl_vls','fuel_me_rsdl_uls','fuel_boiler_rsdl_uls','fuel_aux_rsdl_uls','fuel_me_dstlt_vls','fuel_aux_dstlt_uls','fuel_boiler_dstlt_uls','fuel_me_tnktnr_dstlt_vls','fuel_aux_tnktnr_dstlt_vls','fuel_boiler_tnktnr_dstlt_vls','fuel_aux_dstlt_vls','fuel_boiler_dstlt_vls','fuel_me_dstlt_uls','cargo_total']] = df1[['distance_covered', 'manvrng_miles_by_gps','miles_by_gps','cargo_transport_work','fuel_hs','fuel_ls','fuel_mdo','fuel_mgo','fuel_mgo_ls','teu_transport_work','fuel_me_rsdl_hs','fuel_aux_rsdl_hs','fuel_boiler_rsdl_hs','fuel_me_rsdl_vls','fuel_aux_rsdl_vls','fuel_boiler_rsdl_vls','fuel_me_rsdl_uls','fuel_boiler_rsdl_uls','fuel_aux_rsdl_uls','fuel_me_dstlt_vls','fuel_aux_dstlt_uls','fuel_boiler_dstlt_uls','fuel_me_tnktnr_dstlt_vls','fuel_aux_tnktnr_dstlt_vls','fuel_boiler_tnktnr_dstlt_vls','fuel_aux_dstlt_vls','fuel_boiler_dstlt_vls','fuel_me_dstlt_uls','cargo_total']].apply(pd.to_numeric, errors='coerce')
    # df1=pd.merge(df1,vessel,on='imo')
# Initialize EEOIData DataFrame
    EEOIData = pd.DataFrame()
    df1=pd.merge(df1,eeoigoalmt,on='imo')
    print(eeoigoalmt)
    print("dhgshdgsdg",df1)

    # Define fuel columns for different periods
    if int(year1) > 2019:
        hfo_columns = ['fuel_me_rsdl_hs', 'fuel_aux_rsdl_hs', 'fuel_boiler_rsdl_hs']
        lfo_columns = ['fuel_me_rsdl_vls', 'fuel_aux_rsdl_vls', 'fuel_boiler_rsdl_vls',
                    'fuel_me_rsdl_uls', 'fuel_aux_rsdl_uls', 'fuel_boiler_rsdl_uls']
        mdo_mgo_columns = ['fuel_me_dstlt_vls', 'fuel_aux_dstlt_vls', 'fuel_boiler_dstlt_vls',
                        'fuel_me_dstlt_uls', 'fuel_aux_dstlt_uls', 'fuel_boiler_dstlt_uls',
                        'fuel_me_tnktnr_dstlt_vls', 'fuel_aux_tnktnr_dstlt_vls', 'fuel_boiler_tnktnr_dstlt_vls']
    else:
        hfo_columns = ['fuel_me_hs', 'fuel_aux_hs', 'fuel_boiler_hs']
        lfo_columns = ['fuel_me_ls', 'fuel_aux_ls', 'fuel_boiler_ls']
        mdo_mgo_columns = ['fuel_me_mdo', 'fuel_aux_mdo', 'fuel_boiler_mdo', 
                        'fuel_me_mgo', 'fuel_aux_mgo', 'fuel_boiler_mgo',
                        'fuel_me_mgo_ls', 'fuel_aux_mgo_ls', 'fuel_boiler_mgo_ls']

    
# Sum the respective columns for each fuel type
    df1['HFO'] = df1[hfo_columns].apply(pd.to_numeric).sum(axis=1)
    df1['LFO'] = df1[lfo_columns].apply(pd.to_numeric).sum(axis=1)
    df1['MDO_MGO'] = df1[mdo_mgo_columns].apply(pd.to_numeric).sum(axis=1)
    df1['totalco2']=pd.to_numeric(df1['HFO'])*3.114+pd.to_numeric(df1['LFO'])*3.151+pd.to_numeric(df1['MDO_MGO'])*3.206
    df1[['miles_by_gps','manvrng_miles_by_gps']]=df1[['miles_by_gps','manvrng_miles_by_gps']].fillna(0)

    df1['distance'] = np.round(
        np.where(df1['miles_by_gps'] != df1['manvrng_miles_by_gps'],
                df1['miles_by_gps'] + df1['manvrng_miles_by_gps'],
                df1['miles_by_gps']), 2)
    # df1['distance']=df1['miles_by_gps']+df1['manvrng_miles_by_gps']
    # df1['tranpo']=
    print("df1_new",df1)
    df1['distance']=pd.to_numeric(df1['distance'], errors='coerce')
    df1_new =df1.groupby(['imo','vessel_name','voyage_order','fleet','class','eeoitype']).sum().round(2).reset_index()
    # print(df1_new['voyage_order'])
    df1_new = df1_new.drop('cargo_total', axis=1)
    df1_new = df1_new.drop('cargo_total_teu', axis=1)
    print("df1_new.......................sdgysgdysgdy",df1_new.columns)
    
    # df1_new = df1_new.drop(columns=['cargo_total', 'cargo_total_teu'])
    # df1['teu_empty']=pd.to_numeric(df1['teu_empty'])
    df = df1.drop_duplicates(subset=['imo', 'voyage_order', 'cargo_total', 'cargo_total_teu'])

    # Group by 'imo' and 'voyage_order', summing 'cargo_total' and 'cargo_total_teu'
    xcargo = df.groupby(['imo', 'voyage_order'])[['cargo_total', 'cargo_total_teu']].sum().reset_index()
    print(xcargo.columns)
    final_new=pd.merge(df1_new,xcargo,on=['imo', 'voyage_order'])
    final_new['cargo_transport_work'] = final_new['cargo_total'] * final_new['distance']
    final_new['teu_transport_work']=final_new['cargo_total_teu'] * final_new['distance']
    
    print(final_new.columns)
    final_new[['distance_covered', 'fuel_boiler_dstlt_uls', 'fuel_aux_dstlt_uls',
       'teu_transport_work', 'cargo_transport_work',
        'miles_by_gps', 'manvrng_miles_by_gps', 'fuel_hs',
       'fuel_ls', 'fuel_mdo', 'fuel_mgo', 'fuel_mgo_ls', 
       'me_fuel_only_steaming_time', 'fuel_me_hs', 'fuel_aux_hs',
       'fuel_boiler_hs', 'fuel_me_ls', 'fuel_aux_ls', 'fuel_boiler_ls',
       'fuel_me_mdo', 'fuel_aux_mdo', 'fuel_boiler_mdo', 'fuel_me_mgo',
       'fuel_aux_mgo', 'fuel_boiler_mgo', 'fuel_me_mgo_ls',
       'fuel_boiler_mgo_ls', 'fuel_aux_mgo_ls',
       'eeoigoalmt1', 'eeoigoalmt2', 'HFO', 'LFO', 'MDO_MGO', 'totalco2',
       'distance', 'cargo_total', 'cargo_total_teu']]=final_new[['distance_covered', 'fuel_boiler_dstlt_uls', 'fuel_aux_dstlt_uls',
       'teu_transport_work', 'cargo_transport_work',
        'miles_by_gps', 'manvrng_miles_by_gps', 'fuel_hs',
       'fuel_ls', 'fuel_mdo', 'fuel_mgo', 'fuel_mgo_ls', 
       'me_fuel_only_steaming_time', 'fuel_me_hs', 'fuel_aux_hs',
       'fuel_boiler_hs', 'fuel_me_ls', 'fuel_aux_ls', 'fuel_boiler_ls',
       'fuel_me_mdo', 'fuel_aux_mdo', 'fuel_boiler_mdo', 'fuel_me_mgo',
       'fuel_aux_mgo', 'fuel_boiler_mgo', 'fuel_me_mgo_ls',
       'fuel_boiler_mgo_ls', 'fuel_aux_mgo_ls',
       'eeoigoalmt1', 'eeoigoalmt2', 'HFO', 'LFO', 'MDO_MGO', 'totalco2',
       'distance', 'cargo_total', 'cargo_total_teu']].apply(pd.to_numeric, errors='coerce')
    numeric_columns = final_new.select_dtypes(include='number').columns
    
    finaldata = final_new.groupby(['imo', 'vessel_name', 'fleet', 'class'])[numeric_columns].sum().reset_index()

    
    print("final_new...............",final_new.columns)
    # exit(0)
    cargometric = xcargo.groupby('imo').agg(
    cargo_total_sum=('cargo_total', 'sum'),
    cargo_total_teu_sum=('cargo_total_teu', 'sum'),
    voyages=('voyage_order', 'count')
    ).reset_index()
    
    print("dfdfdfdf",cargometric)
    # finaldata = finaldata.drop('voyage_order', axis=1)
    finaldata=pd.merge(finaldata,cargometric,on=['imo'])

    print(finaldata)

    # EEOIData[['imo','vessel_name','fleet','class','miles_by_gps','manvrng_miles_by_gps','HFO','LFO','MDO_MGO']]=  df1[['imo','vessel_name','fleet','class','miles_by_gps','manvrng_miles_by_gps','HFO','LFO','MDO_MGO']]
    # finaldata =EEOIData.groupby(['imo','vessel_name','fleet','class']).sum().round(2).reset_index()
    
    finaldata['equivalent_hfo'] = round((finaldata['HFO'] + (finaldata['LFO'] + finaldata['MDO_MGO'])* 1.05 ), 2)
    finaldata['totalco2_kgnm'] =round((finaldata['totalco2'] ) / finaldata['distance'], 2)
    finaldata['totalco2_total'] =round((finaldata['totalco2'] ).sum(), 2)
    finaldata['totalco2_kgnm_total'] =round((finaldata['totalco2_kgnm']).sum(), 2)
    finaldata['equivalent_hfo_total'] = round(finaldata['equivalent_hfo'].sum(), 2)
    finaldata['eeoi_mt'] = round((round(finaldata['totalco2'],2) * 10 ** 6) / round(finaldata['cargo_transport_work'],2), 2)
    finaldata['eeoi_teu'] = round((pd.to_numeric(finaldata['totalco2']) * 10 ** 6 )/ (pd.to_numeric(finaldata['teu_transport_work'])), 2)
    finaldata['eeoi_mt_total'] = round(finaldata['eeoi_mt'].fillna(0).sum(), 2)
    finaldata['eeoi_teu_total'] = round(finaldata['eeoi_teu'].fillna(0).sum(), 2)
    finaldata['fuelkg_nm'] = round(((finaldata['equivalent_hfo'] * 1000) / finaldata['distance']), 2)
    finaldata['fuelkg_nm_total'] = round(finaldata['fuelkg_nm'].sum(), 2)
    finaldata['average_perteu'] = round(finaldata['cargo_total_teu'] / pd.to_numeric(finaldata['voyages']),2)
    finaldata['average_perteu_total'] = round(finaldata['average_perteu'].sum(),2)
    finaldata['average_permt'] = round(finaldata['cargo_total'] / pd.to_numeric(finaldata['voyages']),2)
    finaldata['average_distance'] = round(finaldata['distance'] / pd.to_numeric(finaldata['voyages']),2)
    finaldata['average_fuelcons'] =round( finaldata['equivalent_hfo'] / pd.to_numeric(finaldata['voyages']),2)
    finaldata['total_voyages'] =round(finaldata['voyages'].sum(),2)
    finaldata['average_distance_total'] =round(finaldata['average_distance'].sum(),2)
    finaldata['average_fuelcons_total'] =round(finaldata['average_fuelcons'].sum(),2)
    finaldata['average_permt_total'] =round(finaldata['average_permt'].sum(),2)

    finaldata['hfo_total'] =round(finaldata['HFO'].sum(),2)
    finaldata['lfo_total'] =round(finaldata['LFO'].sum(),2)
    finaldata['MDO_MGO_total'] =round(finaldata['MDO_MGO'].sum(),2)
    finaldata['cargomt']=round(finaldata['cargo_total'].sum(),2)
    finaldata['TotalCo2_mt_total']=round(finaldata['totalco2'].sum(),2)
    finaldata['teu_cargo_total']=round(finaldata['cargo_total_teu'].sum(),2)
    finaldata['distance_total']=round(finaldata['distance'].sum(),2)
    finaldata['year']=year1
    return finaldata
    print(finaldata)
    print("The End ")
    exit()
    df1_new =df1.groupby(['imo','eeoi_voyage_no','']).sum().round(2).reset_index()

    # df1.rename(columns={'value':'class'}, inplace = True)
    #print(df1[['fleet','class']])
    # df1['totalco2']=round(((pd.to_numeric(df1['fuel_me_rsdl_hs'])+pd.to_numeric(df1['fuel_aux_rsdl_hs'])+pd.to_numeric(df1['fuel_boiler_rsdl_hs']))*3.114)+((pd.to_numeric(df1['fuel_me_rsdl_vls'])+pd.to_numeric(df1['fuel_aux_rsdl_vls'])+pd.to_numeric(df1['fuel_boiler_rsdl_vls'])+pd.to_numeric(df1['fuel_me_rsdl_uls'])+pd.to_numeric(df1['fuel_aux_rsdl_uls'])+pd.to_numeric(df1['fuel_boiler_rsdl_uls']))*3.151)   +((pd.to_numeric(df1['fuel_me_dstlt_vls'])+pd.to_numeric(df1['fuel_aux_dstlt_vls'])+pd.to_numeric(df1['fuel_boiler_dstlt_vls'])+pd.to_numeric(df1['fuel_me_dstlt_uls'])+pd.to_numeric(df1['fuel_aux_dstlt_uls'])+pd.to_numeric(df1['fuel_boiler_dstlt_uls'])+pd.to_numeric(df1['fuel_me_tnktnr_dstlt_vls'])+pd.to_numeric(df1['fuel_aux_tnktnr_dstlt_vls'])+pd.to_numeric(df1['fuel_boiler_tnktnr_dstlt_vls']))*3.206),2)
    
    # df1['totalco2']=(df1['fuel_hs'])*3.114+(df1['fuel_ls'])*3.151+(df1['fuel_mdo']+df1['fuel_mgo']+df1['fuel_mgo_ls'])*3.206
   
    # df1['totalco2']=pd.to_numeric(df1['totalco2'])
    
    new = df1.groupby(['voyage_order', 'imo']).sum().reset_index()
    
    # new=pd.merge(new,eeoigoalmt,on='imo')
    # new.rename(columns={'value':'eeoitype'}, inplace = True)
   
    # new=pd.merge(new,vessel,on='imo')
    new['xcargo']=cargometric['xcargo']

    
    # new.rename(columns={'value':'class','fleet_y':'fleets','fleet_x':'fleet'}, inplace = True)
   
    new=pd.merge(new,eeoigoalmt,on='imo')
   
   
   
    # new.rename(columns={'eeoigoalmt1':'eeoigoalmt2'}, inplace = True)
   
    plot=pd.DataFrame()
    new['eeoigoalteu1'] = np.where(new['eeoitype_y'] == "1", pd.to_numeric(new['eeoigoalmt1_y'])*14, 0) 
    # cargometric['distance'] = np.where(pd.to_numeric(cargometric['year']) <= 2019, cargometric['distance1'], cargometric['distance2'])
    new['eeoigoalteu2'] = np.where(new['eeoitype_y'] == "1", (pd.to_numeric(new['eeoigoalmt2_y'])*14), 0)
    plot['teu_transport_work'] = np.where(new['eeoitype_y'] == "1", pd.to_numeric(new['teu_transport_work'])*14, 0)
    df1['miles_by_gps'] = df1['miles_by_gps'].replace({np.nan:0})
    df1['manvrng_miles_by_gps'] = df1['manvrng_miles_by_gps'].replace({np.nan:0})
    
    distance1=df1.groupby(['imo'])[['miles_by_gps','manvrng_miles_by_gps']].sum().reset_index()
    cargometric['distance1']=distance1['miles_by_gps']+distance1['manvrng_miles_by_gps']
    
    cargometric['voyage_order']=new['voyage_order']
  
    #print(pd.to_numeric(df1['manvrng_miles_by_gps']).sum())
    df1['distance_covered']=pd.to_numeric(df1['distance_covered'])
    # df1['miles_by_gps']=pd.to_numeric(df1['miles_by_gps'])
    distance2=df1.groupby(['imo'])[['distance_covered']].sum().reset_index()
    cargometric['distance2']=distance2['distance_covered']
 


    cargometric['year']=year1
    
    cargometric['totalco2']=pd.to_numeric(new['totalco2'])
   
    
    plot['transportation_mt']=new['cargo_transport_work']

    plot['voyage_order']=new['voyage_order']
    
    # plot['teu_transport_work']=new['teu_transport_work']
    plot['voyage_order']=new['voyage_order']

    # mt  = df1.groupby(['imo','voyage_order'])['cargo_transport_work'].sum().reset_index()
    df1_new =df1.groupby(['imo','eeoi_voyage_no']).sum().round(2).reset_index()
    df1_new=pd.merge(df1_new,eeoigoalmt,on='imo')

    # df1_new.rename(columns={'value':'eeoitype'}, inplace = True)
    # df1_new=pd.merge(df1_new,eeoigoalmt1,on='imo')
   
    # df1_new.rename(columns={'eeoigoalmt1':'eeoigoalmt2'}, inplace = True)
    df1_new['eeoigoalteu2'] = np.where(df1_new['eeoitype_y'] == "1", (pd.to_numeric(df1_new['eeoigoalmt2_x'])*14), 0)

     
    cargometric['mt']=new['cargo_transport_work']

    # fuel_hs  = df1.groupby(['imo','eeoi_voyage_no'])['fuel_hs'].sum().reset_index()
    EEOIData=pd.DataFrame()

    df1['fuel_me_rsdl_hs']=pd.to_numeric(df1['fuel_me_rsdl_hs'])
    df1['fuel_aux_rsdl_hs']=pd.to_numeric(df1['fuel_aux_rsdl_hs'])
    df1['fuel_boiler_rsdl_hs']=pd.to_numeric(df1['fuel_boiler_rsdl_hs'])
    
    fuel_ls  = df1.groupby(['fleet','class','imo'])[['fuel_hs','fuel_ls','fuel_mdo','fuel_mgo','fuel_mgo_ls','cargo_transport_work','teu_transport_work','miles_by_gps','manvrng_miles_by_gps','distance_covered','fuel_me_rsdl_hs','fuel_aux_rsdl_hs','fuel_boiler_rsdl_hs']].sum().reset_index()

    fuel_ls=pd.merge(fuel_ls,eeoigoalmt,on='imo')
    # fuel_ls.rename(columns={'value':'eeoitype'}, inplace  = True)
    dis=pd.DataFrame()
    # dis=df1.groupby(['fleet','class','imo'])[['miles_by_gps','manvrng_miles_by_gps','distance_covered']].apply(lambda x: x.nunique().sum()).reset_index()
    df1['distance2']=df1['miles_by_gps']
    miles_by_gps= df1.groupby(['fleet','class','imo'])['distance1'].sum().reset_index()
    EEOIData['distance1'] = round(miles_by_gps['distance1'],2)
    distance2= df1.groupby(['fleet','class','imo'])['distance2'].sum().reset_index()
    EEOIData['distance2'] = round(distance2['distance2'],2)
    
   
    # EEOIData['HFO']=fuel_ls['fuel_me_rsdl_hs']+fuel_ls['fuel_aux_rsdl_hs']+fuel_ls['fuel_boiler_rsdl_hs']
    EEOIData['class']=fuel_ls['class_x']
    EEOIData['imo']=fuel_ls['imo']
    EEOIData['fleet']=fuel_ls['fleet_x']
   
    # EEOIData['LFO']=df1_new['fuel_me_rsdl_vls'] + df1_new['fuel_aux_rsdl_vls'] +df1_new['fuel_boiler_rsdl_vls'] +df1_new['fuel_me_rsdl_uls'] +df1_new['fuel_aux_rsdl_uls'] +df1_new['fuel_boiler_rsdl_uls']
    
    EEOIData['year']=year1
    
    EEOIData['distance'] = np.where(pd.to_numeric(EEOIData['year']) <= 2019, EEOIData['distance1'], EEOIData['distance2'])
    # EEOIData['MDO_MGO']=df1_new['fuel_me_dstlt_vls'] + df1_new['fuel_aux_dstlt_vls'] + df1_new['fuel_boiler_dstlt_vls'] + df1_new['fuel_me_dstlt_uls'] + df1_new['fuel_aux_dstlt_uls'] + df1_new['fuel_boiler_dstlt_uls']+df1_new['fuel_me_tnktnr_dstlt_vls'] + df1_new['fuel_aux_tnktnr_dstlt_vls'] + df1_new['fuel_boiler_tnktnr_dstlt_vls']
    
    # #print(df1_new['imo'])
    # #print(df1_new['TotalCo2_mt'])
    # #print(df1_new[['fuel_ls','fuel_mdo','fuel_mgo','fuel_mgo_ls']])
    # EEOIData['TotalCo2_mt']=df1_new['TotalCo2_mt']
    EEOIData['eeoi_voyage_no']=df1_new['eeoi_voyage_no']
    # EEOIData['eeoi_voyage_no']=df1_new['eeoi_voyage_no']
    EEOIData['EEOIGOALMT']=np.NaN
    EEOIData['EEOIGOALTEU']=np.NaN
    # EEOIData['vessel_name']=df1_new['name']         
    EEOIData['mt']=fuel_ls['cargo_transport_work']
    EEOIData['tue']=fuel_ls['teu_transport_work']
    #print(EEOIData)
    
    
    # df1_new1=df1_new[(df1_new['transportation_mt']!=0) & (df1_new['teu_transport_work']!=0)]
    # df1_new=df1_new[[df1_new['teu_transport_work']!=0]]
    # EEOIData['EEOI_MT'] = round(df1_new1['TotalCo2_mt'] * 10 ** 6 / Finaldata_plot['transportation_mt'], 2)
    # EEOIData['EEOI_TEU'] = df1_new['EEOI_TEU']
    # Finaldata_plot =  pd.merge(EEOIData, plot, how='left', left_on= "eeoi_voyage_no",  right_on = "voyage_order")
    # # #print(Finaldata_plot)6
    # Finaldata_plot['EEOI_MT'] = round(EEOIData['TotalCo2_mt'] * 1000000 / sum(Finaldata_plot['transportation_mt']), 2)
                                               
    # Finaldata_plot =  pd.merge(Finaldata_plot, eeoigoal,how='left', left_on = "VSL", right_on =  "imo")
    # if eeoitype=='1':
    #     Finaldata_plot=Finaldata_plot[[Finaldata_plot['transportation_mt']!=0]]
    #     Finaldata_plot=Finaldata_plot[[Finaldata_plot['teu_transport_work']!=0]]
    #     Finaldata_plot['EEOI_MT'] = round(Finaldata_plot['TotalCo2_mt'] * 10 ** 6 / Finaldata_plot['transportation_mt'], 2)
    #     Finaldata_plot['EEOI_TEU'] = round(Finaldata_plot['TotalCo2_mt'] * 10 ** 6 / Finaldata_plot['teu_transport_work'],2)
  

 
    # Finaldata_plot['year']=year1
    # movingaveragedata1=Finaldata_plot[['eeoi_voyage_no','EEOIGOALMT','EEOIGOALTEU','EEOI_MT','EEOI_TEU','year']]
    # movingaveragedata1['EEOI For Cargo [MT]'] =Finaldata_plot['EEOI_MT']
    # movingaveragedata1['EEOI For Cargo [TEU]']=Finaldata_plot['EEOI_TEU']
    # if not movingaveragedata1.empty:
    #     moving_average=int(moving_average)
    #     movingaveragedata1['movingavgmt']=movingaveragedata1['EEOI For Cargo [MT]'].rolling(moving_average).mean()
    #     movingaveragedata1['movingavg2mt'] = movingaveragedata1['EEOI For Cargo [TEU]'].rolling(moving_average).mean()
    # else:
    #     moving_average=0
    # movingaveragedata1['S.No']=movingaveragedata1.index
    #print(new['imo'])
    # teu  =df1.groupby(['imo','voyage_order'])['teu_transport_work'].sum().reset_index()
    cargometric['imo']=new['imo']
    cargometric['teu']=new['teu_transport_work']
    cargometric['eeoi_voyage_no']=df1_new['eeoi_voyage_no']
    # for i in range(0,len(cargometric)):
    #     if int(cargometric['year'][i]) <= 2019:
    #         cargometric['distance'] =  cargometric['distance1']
        
    #     else:
    #         cargometric['distance'] =  cargometric['distance2']
    cargometric['distance'] = np.where(pd.to_numeric(cargometric['year']) <= 2019, cargometric['distance1'], cargometric['distance2'])

    #print(eeoidata)

    # hfo = df1.groupby(['eeoi_voyage_no', 'imo'])['fuel_me_rsdl_hs','fuel_aux_rsdl_hs','fuel_boiler_rsdl_hs'].sum().reset_index()
    eeoidata['eeoi_voyage_no']=df1_new['eeoi_voyage_no']
    # eeoidata['vessel_name']=df1_new['name']
    eeoidata['eeoigoalteu2']=df1_new['eeoigoalteu2']
    if int(year1) > 2019:
        EEOIData['HFO']=df1_new['fuel_me_rsdl_hs']+df1_new['fuel_aux_rsdl_hs']+df1_new['fuel_boiler_rsdl_hs']
        
        EEOIData['LFO'] = df1_new['fuel_me_rsdl_vls'] + df1_new['fuel_aux_rsdl_vls'] +df1_new['fuel_boiler_rsdl_vls'] +df1_new['fuel_me_rsdl_uls'] +df1_new['fuel_aux_rsdl_uls'] +df1_new['fuel_boiler_rsdl_uls']
        EEOIData['MDO_MGO'] =df1_new['fuel_me_dstlt_vls'] + df1_new['fuel_aux_dstlt_vls'] + df1_new['fuel_boiler_dstlt_vls'] + df1_new['fuel_me_dstlt_uls'] + df1_new['fuel_aux_dstlt_uls'] + df1_new['fuel_boiler_dstlt_uls']+df1_new['fuel_me_tnktnr_dstlt_vls'] + df1_new['fuel_aux_tnktnr_dstlt_vls'] + df1_new['fuel_boiler_tnktnr_dstlt_vls']
    else:
        EEOIData['HFO'] = pd.to_numeric(df1_new['fuel_me_hs'])+ pd.to_numeric(df1_new['fuel_aux_hs']) + pd.to_numeric(df1_new['fuel_boiler_hs'])
        EEOIData['LFO'] = pd.to_numeric(df1_new['fuel_me_ls'])+pd.to_numeric(df1_new['fuel_aux_ls'])+pd.to_numeric(df1_new['fuel_boiler_ls'])
        EEOIData['MDO_MGO'] = pd.to_numeric(df1_new['fuel_me_mdo'])+pd.to_numeric(df1_new['fuel_aux_mdo'])+pd.to_numeric(df1_new['fuel_boiler_mdo'])+ pd.to_numeric(df1_new['fuel_me_mgo']) +pd.to_numeric(df1_new['fuel_aux_mgo']) + pd.to_numeric(df1_new['fuel_boiler_mgo']) + pd.to_numeric(df1_new['fuel_me_mgo_ls']) + pd.to_numeric(df1_new['fuel_boiler_mgo_ls']+df1_new['fuel_aux_mgo_ls'])

    # mdo_mgo = df1.groupby(['eeoi_voyage_no', 'imo'])['fuel_me_dstlt_vls','fuel_aux_dstlt_vls','fuel_boiler_dstlt_vls','fuel_me_dstlt_uls','fuel_aux_dstlt_uls','fuel_boiler_dstlt_uls','fuel_me_tnktnr_dstlt_vls','fuel_aux_tnktnr_dstlt_vls','fuel_boiler_tnktnr_dstlt_vls'].sum().reset_index()
    # eeoidata['eeoi_voyage_no']=df1_new['eeoi_voyage_no']
    # eeoidata['eeoigoalmt2']=df1_new['eeoigoalmt2_x']


    # eeoidata['imo']=df1_new['imo']
    EEOIData['TotalCo2_mt']=round(EEOIData['HFO'] * 3.114+EEOIData['LFO'] * 3.151+EEOIData['MDO_MGO']* 3.206,2)
    EEOIData['EEOI_TEU'] = np.where(fuel_ls['eeoitype'] == "1", round(EEOIData['TotalCo2_mt']  * 1000000 / sum(fuel_ls['teu_transport_work']), 2),np.NaN)

    totalcargobyvessel = cargometric.groupby(['imo']).sum().round(2).reset_index()
    totalcargobyvessel=pd.merge(totalcargobyvessel,eeoigoalmt,on='imo')
    #print(totalcargobyvessel)
    # totalcargobyvessel['vessel_name']=merge_imos['name']
    totalcargobyvessel['cargomt']=totalcargobyvessel['xcargo']
    # totalcargobyvessel['eeoigoalteu2']=merge_imo['eeoigoalteu2']
    # merge_data=merge_data[merge_data['year']==year1] 
    # cargomt = merge_data.groupby(['imo'])['xcargo'].sum().reset_index()
    # totalcargobyvessel['cargomt']=merge_imo['xcargo']
    # totalcargobyvessel['vessel_name']=merge_imo['vessel_name']
    # cargoteu  = merge_data.groupby(['imo'])['teucargo'].sum().reset_index()
    totalcargobyvessel['cargoteu']=totalcargobyvessel['teucargo']
    # voyages  = cargometric.groupby(['imo'])['eeoi_voyage_no'].count().reset_index()
    voyages = df1.groupby(['imo'])['eeoi_voyage_no'].nunique().reset_index()

    totalcargobyvessel['voyages']=voyages['eeoi_voyage_no']
    totalcargobyvessel['total_voyages']=(totalcargobyvessel['voyages']).sum()


    # distance  = merge_data.groupby(['imo'])['distance'].sum().reset_index()
    # totalcargobyvessel['distance']=merge_imo['distance']
    totalcargobyvessel['year']=year1
    # mt  = merge_data.groupby(['imo'])['mt'].sum().reset_index()
    # totalcargobyvessel['mt']=merge_imo['mt']
    # teu  = merge_data.groupby(['imo'])['teu'].sum().reset_index()
    # totalcargobyvessel['teu']=merge_imo['teu']
    # hfo = merge_data.groupby(['imo'])['hfo'].sum().reset_index()
    # totalcargobyvessel['hfo']=merge_imo['hfo']
    # lfo = merge_data.groupby(['imo'])['lfo'].sum().reset_index()
    # totalcargobyvessel['lfo'] = merge_imo['lfo']
    # totalcargobyvessel['eeoigoalmt2'] = merge_imo['eeoigoalmt2']
    
    # mdo_mgo = merge_data.groupby(['imo'])['mdo_mgo'].sum().reset_index()
    # totalcargobyvessel['mdo_mgo']=merge_imo['mdo_mgo']
    #print(totalcargobyvessel)
    
    totalcargobyvessel['totalco2'] = totalcargobyvessel['totalco2'].replace({np.nan:0})
    # totalcargobyvessel['voyages']=totalcargobyvessel['eeoi_voyage_no']

    # totalco2  = merge_data.groupby(['imo'])['totalco2'].sum().reset_index()
    # totalcargobyvessel['imo']=merge_imo['imo']
    # totalcargobyvessel['totalco2']=merge_imo['totalco2']
    # totalcargobyvessel['vessel_name']=merge_imo['vessel_name']

    finaldata = pd.merge(EEOIData,totalcargobyvessel, on= 'imo')
    finaldata = finaldata.sort_values(by=['imo'], ascending=True)
    # finaldata['voyages']=finaldata['imo'].count()
    # finaldata['voyages']=finaldata['eeoi_voyage_no'].count()

    #print(finaldata)
    # finaldata['totalco2_mt'] = finaldata['totalco2']
    finaldata['hfo_total']=finaldata['HFO'].sum()
    finaldata['lfo_total']=finaldata['LFO'].sum()
    finaldata['MDO_MGO_total']=finaldata['MDO_MGO'].sum()
    finaldata['TotalCo2_mt_total']=finaldata['TotalCo2_mt'].sum()
    finaldata['distance_total']=finaldata['distance_x'].sum()
    finaldata['mt_total']=finaldata['mt_x'].sum()
    finaldata['teu_total']=finaldata['teu'].sum()
    finaldata['teu_cargo_total']=finaldata['teucargo'].sum()

    finaldata['totalco2_kgnm_total'] =round((finaldata['TotalCo2_mt_total'] ) / finaldata['distance_total'], 2)

    finaldata['totalco2_kgnm'] =round((finaldata['TotalCo2_mt'] ) / finaldata['distance_x'], 2)
    finaldata['equivalent_hfo_total'] = round((finaldata['hfo_total'] + (finaldata['lfo_total'] + finaldata['MDO_MGO_total'])* 1.05 )/1000, 2)
    finaldata['equivalent_hfo'] = round((finaldata['HFO'] + (finaldata['LFO'] + finaldata['MDO_MGO'])* 1.05 )/1000, 2)

    finaldata['equip_nm'] =  round((finaldata['equivalent_hfo'] * 1000) / finaldata['distance_x'], 2)
    finaldata['eeoi_mt'] = round((round(finaldata['TotalCo2_mt'],2) * 10 ** 6) / round(finaldata['mt_x'],2), 2)
    finaldata['eeoi_teu'] = round((round(finaldata['TotalCo2_mt'],2) * 10 ** 6 )/ round(finaldata['teu'],2), 2)
    finaldata['eeoi_mt_total'] = round((round(finaldata['TotalCo2_mt_total'],2) * 10 ** 6) / round(finaldata['mt_total'],2), 2)
    finaldata['eeoi_teu_total'] = round((round(finaldata['TotalCo2_mt_total'],2) * 10 ** 6 )/ round(finaldata['teu_total'],2), 2)
    finaldata['eeoi_mt'] =pd.to_numeric(finaldata['eeoi_mt'])
    finaldata['eeoi_teu']=pd.to_numeric(finaldata['eeoi_teu'])
    
    # finaldata['eeoi_mt'] = round((finaldata['totalco2_mt'] * 1000000) / sum(finaldata['mt']), 2)
    # finaldata['eeoi_teu'] = round((finaldata['totalco2_mt'] * 1000000 ) / sum(finaldata['teu']), 2)
    #print(finaldata['eeoi_mt'])
    #print(finaldata['eeoi_teu'])
    
    finaldata['fuelkg_nm'] = round(((finaldata['equivalent_hfo'] * 1000) / finaldata['distance_x']), 2)
    # finaldata=pd.merge(finaldata, eeoigoal,how='left', left_on=['imo'], right_on = ['vesselname'])
    finaldata['average_perteu'] = round(finaldata['teucargo'] / pd.to_numeric(finaldata['voyages']),2)
    finaldata['average_perteu_total'] = round(finaldata['teu_cargo_total'] / pd.to_numeric(finaldata['total_voyages']),2)

    finaldata['average_permt'] = round(finaldata['cargomt'] / pd.to_numeric(finaldata['voyages']),2)
    finaldata['average_distance'] = round(finaldata['distance_x'] / pd.to_numeric(finaldata['voyages']),2)
    finaldata['average_fuelcons'] =round( finaldata['equivalent_hfo'] / pd.to_numeric(finaldata['voyages']),2)
    # finaldata['eeoideviationmt'] = round(((finaldata['eeoi_mt'] - finaldata['eeoigoalmt2']) /finaldata['eeoigoalmt2']), 2)
    # finaldata['eeoideviationteu'] = round(((finaldata['eeoi_teu'] - finaldata['eeoigoalteu2']) /finaldata['eeoigoalteu2']), 2)
    #print(finaldata)
    # exit(0)
    finaldata = finaldata.replace({np.nan:None})
    # old_final=finaldata
    # finaldata_samp = finaldata.to_json(orient="records")
    # finaldata_samp = json.loads(finaldata_samp)
    # total_cargo = totalcargobyvessel.to_json(orient="records")
    # total_cargo = json.loads(total_cargo)
   
    
    return finaldata

# ===================================================================
def get_yearanalysis(df1,year1,eeoitype,eeoimt2,eeoiteu2,type,moving_average):
    df1['corrected_date']=pd.to_datetime(df1['corrected_date']).dt.strftime('%Y-%m-%d')
    # df=df[(pd.to_datetime(df['corrected_date']) >= pd.to_datetime(pdate1)) & (pd.to_datetime(df['corrected_date']) <= pd.to_datetime(pdate2))]
    df1=df1[df1['report_type']!="REFL"]
    df1=df1[(pd.to_datetime(df1['corrected_date']).dt.year)==int(year1)]

    if  df1.empty:
        return df1 , df1
    cargometric=pd.DataFrame()
    totalcargobyvessel=pd.DataFrame()
    eeoidata=pd.DataFrame()
    # cargo = df1
    
    df1['voyage_order']=df1['voyage_order'].ffill().bfill()
    
    
    # fuel_aux_rsdl_vls
    # fuel_boiler_rsdl_vls
    df1['cargo_total']=pd.to_numeric(df1['cargo_total'])
    df1['cargo_total'] = df1['cargo_total'].replace({np.nan:0})
    xcargo= df1.groupby(['voyage_order','imo'])['cargo_total'].unique().reset_index()
    xcargo= xcargo['cargo_total'].apply(sum).reset_index()
    
    # xcargo['cargo_total'] = xcargo['cargo_total'].apply(', '.join)
    # # try:
    # if int(year1) < 2020:
    #     df1['fuel_hs'] = df1['fuel_me_hs'] + df1['fuel_aux_hs'] + df1['fuel_boiler_hs']
    #     df1['fuel_ls'] = df1['fuel_me_ls']+df1['fuel_aux_ls']+df1['fuel_boiler_ls']
    #     df1['fuel_mgo'] = df1['fuel_me_mdo']+df1['fuel_aux_mdo']+df1['fuel_boiler_mdo']+ df1['fuel_me_mgo']+df1['fuel_aux_mgo']+df1['fuel_boiler_mgo']+df1['fuel_me_mgo_ls']+df1['fuel_boiler_mgo_ls']+df1['fuel_aux_mgo_ls']
    # else:
    #     df1['fuel_hs']=pd.to_numeric(df1['fuel_me_rsdl_hs'])+pd.to_numeric(df1['fuel_aux_rsdl_hs'])+pd.to_numeric(df1['fuel_boiler_rsdl_hs'])
    
    #     df1['fuel_ls']=pd.to_numeric(df1['fuel_me_rsdl_vls']) + pd.to_numeric(df1['fuel_aux_rsdl_vls']) +pd.to_numeric(df1['fuel_boiler_rsdl_vls']) + pd.to_numeric(df1['fuel_me_rsdl_uls']) + pd.to_numeric(df1['fuel_aux_rsdl_uls']) + pd.to_numeric(df1['fuel_boiler_rsdl_uls'])
        
    #     df1['fuel_mgo']=pd.to_numeric(df1['fuel_me_dstlt_vls']) + pd.to_numeric(df1['fuel_aux_dstlt_vls']) + pd.to_numeric(df1['fuel_boiler_dstlt_vls']) + pd.to_numeric(df1['fuel_me_dstlt_uls']) + pd.to_numeric(df1['fuel_aux_dstlt_uls']) + pd.to_numeric(df1['fuel_boiler_dstlt_uls'])+pd.to_numeric(df1['fuel_me_tnktnr_dstlt_vls']) + pd.to_numeric(df1['fuel_aux_tnktnr_dstlt_vls']) + pd.to_numeric(df1['fuel_boiler_tnktnr_dstlt_vls'])
    # # df1['totalco2']=((pd.to_numeric(df1['fuel_me_rsdl_hs'])+pd.to_numeric(df1['fuel_aux_rsdl_hs'])+pd.to_numeric(df1['fuel_boiler_rsdl_hs']))*3.114)+((pd.to_numeric(df1['fuel_me_rsdl_vls'])+pd.to_numeric(df1['fuel_aux_rsdl_vls'])+pd.to_numeric(df1['fuel_boiler_rsdl_vls'])+pd.to_numeric(df1['fuel_me_rsdl_uls'])+pd.to_numeric(df1['fuel_aux_rsdl_uls'])+pd.to_numeric(df1['fuel_boiler_rsdl_uls']))*3.151)   +((pd.to_numeric(df1['fuel_me_dstlt_vls'])+pd.to_numeric(df1['fuel_aux_dstlt_vls'])+pd.to_numeric(df1['fuel_boiler_dstlt_vls'])+pd.to_numeric(df1['fuel_me_dstlt_uls'])+pd.to_numeric(df1['fuel_aux_dstlt_uls'])+pd.to_numeric(df1['fuel_boiler_dstlt_uls'])+pd.to_numeric(df1['fuel_me_tnktnr_dstlt_vls'])+pd.to_numeric(df1['fuel_aux_tnktnr_dstlt_vls'])+pd.to_numeric(df1['fuel_boiler_tnktnr_dstlt_vls']))*3.206)
    # df1['totalco2']=df1['fuel_ls'] * 3.114 +df1['fuel_hs'] * 3.114 +df1['fuel_mgo'] * 3.206 
        # EEOIData['TotalCo2_mt']=EEOIData['HFO'] * 3.114+EEOIData['LFO'] * 3.114+EEOIData['MDO_MGO']* 3.206
    
    # ===================================================================================
    df1['distance1']=pd.to_numeric(df1['miles_by_gps'])+pd.to_numeric(df1['manvrng_miles_by_gps'])
    df1[['fuel_me_hs','fuel_aux_hs','fuel_boiler_hs','fuel_me_ls','fuel_aux_ls','fuel_boiler_ls','fuel_me_mdo','fuel_aux_mdo','fuel_boiler_mdo','fuel_me_mgo','fuel_aux_mgo','fuel_boiler_mgo','fuel_me_mgo_ls','fuel_boiler_mgo_ls','fuel_aux_mgo_ls','distance1','teu_full', 'teu_empty', 'manvrng_miles_by_gps','miles_by_gps','cargo_transport_work','fuel_hs','fuel_ls','fuel_mdo','fuel_mgo','fuel_mgo_ls','teu_transport_work','fuel_me_rsdl_hs','fuel_aux_rsdl_hs','fuel_boiler_rsdl_hs','fuel_me_rsdl_vls','fuel_aux_rsdl_vls','fuel_boiler_rsdl_vls','fuel_me_rsdl_uls','fuel_boiler_rsdl_uls','fuel_aux_rsdl_uls','fuel_me_dstlt_vls','fuel_aux_dstlt_uls','fuel_boiler_dstlt_uls','fuel_me_tnktnr_dstlt_vls','fuel_aux_tnktnr_dstlt_vls','fuel_boiler_tnktnr_dstlt_vls','fuel_aux_dstlt_vls','fuel_boiler_dstlt_vls','fuel_me_dstlt_uls','cargo_total']] = df1[['fuel_me_hs','fuel_aux_hs','fuel_boiler_hs','fuel_me_ls','fuel_aux_ls','fuel_boiler_ls','fuel_me_mdo','fuel_aux_mdo','fuel_boiler_mdo','fuel_me_mgo','fuel_aux_mgo','fuel_boiler_mgo','fuel_me_mgo_ls','fuel_boiler_mgo_ls','fuel_aux_mgo_ls','distance1','teu_full', 'teu_empty', 'manvrng_miles_by_gps','miles_by_gps','cargo_transport_work','fuel_hs','fuel_ls','fuel_mdo','fuel_mgo','fuel_mgo_ls','teu_transport_work','fuel_me_rsdl_hs','fuel_aux_rsdl_hs','fuel_boiler_rsdl_hs','fuel_me_rsdl_vls','fuel_aux_rsdl_vls','fuel_boiler_rsdl_vls','fuel_me_rsdl_uls','fuel_boiler_rsdl_uls','fuel_aux_rsdl_uls','fuel_me_dstlt_vls','fuel_aux_dstlt_uls','fuel_boiler_dstlt_uls','fuel_me_tnktnr_dstlt_vls','fuel_aux_tnktnr_dstlt_vls','fuel_boiler_tnktnr_dstlt_vls','fuel_aux_dstlt_vls','fuel_boiler_dstlt_vls','fuel_me_dstlt_uls','cargo_total']].apply(pd.to_numeric)
    new =df1.groupby(['imo','voyage_order'])[['teu_full','teu_empty']].mean().round(2).reset_index()
    
    new = df1.groupby(['imo','voyage_order']).mean(numeric_only=True).reset_index()
    new1 = df1.groupby(['imo','voyage_order']).sum().reset_index()
   
    cargometric['distance1']=pd.to_numeric(new1['miles_by_gps'])+pd.to_numeric(new1['manvrng_miles_by_gps'])
    #print("11111111111111111111111111111111111",cargometric)
    if new.empty==False:
    
        new = new.replace({np.nan:0})
        
        # ===================================================================================
        
        # #print(xcargo)
        df1['cargo_total']=pd.to_numeric(df1['cargo_total'])
        # teucargo1=df1.groupby(['imo','voyasge_order'])['teu_full','teu_empty'].mean().reset_index()
        cargometric['cargo_total']=xcargo['cargo_total']
        cargometric['teucargo']=new['teu_full']+new['teu_empty']
        # distance1=df1.groupby(['imo','voyage_order'])['miles_by_gps','manvrng_miles_by_gps'].sum().reset_index()
        cargometric['voyage_order']=new['voyage_order']
        # cargometric['distance1']=new['distance1']
        
        
        # cargometric['voyage_order']=new['voyage_order']
        distance2=df1.groupby(['imo','voyage_order'])['miles_by_gps'].sum().reset_index()
        cargometric['distance2']=distance2['miles_by_gps']
        cargometric['year']=year1
        cargometric['imo']=new['imo']
        # cargometric['totalco2']=pd.to_numeric(new1['totalco2'])
        
        df1['teu_transport_work']=pd.to_numeric(df1['teu_transport_work'])
        plot_new =df1.groupby(['voyage_order']).sum().reset_index()
        
        #print("ooooooooooookkkkkkkkkkkkkkkkkkkkkk")
        plot=pd.DataFrame()
        if eeoitype=="1.0":
            #print("*******container*********************************")
            # plot_mt  = df1.groupby(['voyage_order'])['cargo_transport_work'].sum().reset_index()
            plot['transportation_mt']=plot_new['cargo_transport_work']
            # plot_teu  =df1.groupby(['voyage_order'])['teu_transport_work'].sum().reset_index()
            plot['teu_transport_work']=plot_new['teu_transport_work']
            plot['voyage_order']=plot_new['voyage_order']
            #print("plot1",plot)
            
        else:
            #print("*******else*********************************")
            
            # plot_teu  =df1.groupby(['voyage_order'])['cargo_transport_work'].sum().reset_index()
            plot['transportation_mt']=plot_new['cargo_transport_work']

            plot['teu_transport_work']=plot_new['teu_transport_work']
            plot['voyage_order']=plot_new['voyage_order']
            
            # plot['voyage_order']=new['voyage_order']

        # mt  = df1.groupby(['imo','voyage_order'])['cargo_transport_work'].sum().reset_index()
        cargometric['mt'] = new1['cargo_transport_work'].apply(lambda x: '{:.0f}'.format(x))
        cargometric['mt']=pd.to_numeric(cargometric['mt'])

        
        #print("cargometriccargometriccargometric",cargometric['mt'])
        df1_new =df1.groupby(['imo','voyage_order']).sum().reset_index()
        #print("dfdjfhdfdjfh",df1_new['fuel_me_hs'])
        EEOIData=pd.DataFrame()
        if int(year1) < 2020:
            EEOIData['HFO'] = pd.to_numeric(df1_new['fuel_me_hs'])+ pd.to_numeric(df1_new['fuel_aux_hs']) + pd.to_numeric(df1_new['fuel_boiler_hs'])
            EEOIData['LFO'] = pd.to_numeric(df1_new['fuel_me_ls'])+pd.to_numeric(df1_new['fuel_aux_ls'])+pd.to_numeric(df1_new['fuel_boiler_ls'])
            EEOIData['MGO'] = pd.to_numeric(df1_new['fuel_me_mdo'])+pd.to_numeric(df1_new['fuel_aux_mdo'])+pd.to_numeric(df1_new['fuel_boiler_mdo'])+ pd.to_numeric(df1_new['fuel_me_mgo']) +pd.to_numeric(df1_new['fuel_aux_mgo']) + pd.to_numeric(df1_new['fuel_boiler_mgo']) + pd.to_numeric(df1_new['fuel_me_mgo_ls']) + pd.to_numeric(df1_new['fuel_boiler_mgo_ls']+df1_new['fuel_aux_mgo_ls'])
        else:
            EEOIData['HFO']=pd.to_numeric(df1_new['fuel_me_rsdl_hs'])+pd.to_numeric(df1_new['fuel_aux_rsdl_hs'])+pd.to_numeric(df1_new['fuel_boiler_rsdl_hs'])
            EEOIData['LFO']=pd.to_numeric(df1_new['fuel_me_rsdl_vls']) + pd.to_numeric(df1_new['fuel_aux_rsdl_vls']) + pd.to_numeric(df1_new['fuel_boiler_rsdl_vls']) + pd.to_numeric(df1_new['fuel_me_rsdl_uls']) + pd.to_numeric(df1_new['fuel_aux_rsdl_uls']) + pd.to_numeric(df1_new['fuel_boiler_rsdl_uls'])
            EEOIData['MGO']=pd.to_numeric(df1_new['fuel_me_dstlt_vls']) + pd.to_numeric(df1_new['fuel_aux_dstlt_vls']) + pd.to_numeric(df1_new['fuel_boiler_dstlt_vls']) + pd.to_numeric(df1_new['fuel_me_dstlt_uls']) + pd.to_numeric(df1_new['fuel_aux_dstlt_uls']) + pd.to_numeric(df1_new['fuel_boiler_dstlt_uls'])+pd.to_numeric(df1_new['fuel_me_tnktnr_dstlt_vls']) + pd.to_numeric(df1_new['fuel_aux_tnktnr_dstlt_vls']) + pd.to_numeric(df1_new['fuel_boiler_tnktnr_dstlt_vls'])
    # df1['totalco2']=((pd.to_numeric(df1['fuel_me_rsdl_hs'])+pd.to_numeric(df1['fuel_aux_rsdl_hs'])+pd.to_numeric(df1['fuel_boiler_rsdl_hs']))*3.114)+((pd.to_numeric(df1['fuel_me_rsdl_vls'])+pd.to_numeric(df1['fuel_aux_rsdl_vls'])+pd.to_numeric(df1['fuel_boiler_rsdl_vls'])+pd.to_numeric(df1['fuel_me_rsdl_uls'])+pd.to_numeric(df1['fuel_aux_rsdl_uls'])+pd.to_numeric(df1['fuel_boiler_rsdl_uls']))*3.151)   +((pd.to_numeric(df1['fuel_me_dstlt_vls'])+pd.to_numeric(df1['fuel_aux_dstlt_vls'])+pd.to_numeric(df1['fuel_boiler_dstlt_vls'])+pd.to_numeric(df1['fuel_me_dstlt_uls'])+pd.to_numeric(df1['fuel_aux_dstlt_uls'])+pd.to_numeric(df1['fuel_boiler_dstlt_uls'])+pd.to_numeric(df1['fuel_me_tnktnr_dstlt_vls'])+pd.to_numeric(df1['fuel_aux_tnktnr_dstlt_vls'])+pd.to_numeric(df1['fuel_boiler_tnktnr_dstlt_vls']))*3.206)
        EEOIData['TotalCo2_mt']=pd.to_numeric(EEOIData['LFO']) * 3.114 + pd.to_numeric(EEOIData['HFO']) * 3.114 + pd.to_numeric(EEOIData['MGO']) * 3.206 

        # fuel_hs  = df1.groupby(['imo','eeoi_voyage_no'])['fuel_hs'].sum().reset_index()
        
        # EEOIData['HFO']=df1_new['fuel_me_rsdl_hs']+df1_new['fuel_aux_rsdl_hs']+df1_new['fuel_boiler_rsdl_hs']
        
        # # fuel_ls  = df1.groupby(['imo','eeoi_voyage_no'])['fuel_ls'].sum().reset_index()
        # EEOIData['LFO']=df1_new['fuel_me_rsdl_vls'] + df1_new['fuel_aux_rsdl_vls'] +df1_new['fuel_boiler_rsdl_vls'] +df1_new['fuel_me_rsdl_uls'] +df1_new['fuel_aux_rsdl_uls'] +df1_new['fuel_boiler_rsdl_uls']
        # # MDO_MGO=df1.groupby(['imo','eeoi_voyage_no'])['fuel_mdo','fuel_mgo','fuel_mgo_ls'].sum().reset_index() 
        # EEOIData['MDO_MGO']=df1_new['fuel_me_dstlt_vls'] + df1_new['fuel_aux_dstlt_vls'] + df1_new['fuel_boiler_dstlt_vls'] + df1_new['fuel_me_dstlt_uls'] + df1_new['fuel_aux_dstlt_uls'] + df1_new['fuel_boiler_dstlt_uls']+df1_new['fuel_me_tnktnr_dstlt_vls'] + df1_new['fuel_aux_tnktnr_dstlt_vls'] + df1_new['fuel_boiler_tnktnr_dstlt_vls']
        # EEOIData['TotalCo2_mt']=EEOIData['HFO'] * 3.114+EEOIData['LFO'] * 3.114+EEOIData['MDO_MGO']* 3.206
        EEOIData['voyage_order']=df1_new['voyage_order']
        EEOIData['EEOIGOALMT']=eeoimt2
        EEOIData['EEOIGOALTEU']=eeoiteu2
       
        
        Finaldata_plot =  pd.merge(EEOIData, plot, how='left', left_on= "voyage_order",  right_on = "voyage_order")

        # Finaldata_plot =  pd.merge(Finaldata_plot, eeoigoal,how='left', left_on = "VSL", right_on =  "imo")
        #print("}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}",eeoitype)
        if eeoitype=='1.0' or eeoitype == '1':
            print("*****************************************************************************")
            Finaldata_plot=Finaldata_plot[Finaldata_plot['transportation_mt']!=0]
            Finaldata_plot=Finaldata_plot[Finaldata_plot['teu_transport_work']!=0]
            # Finaldata_plot['EEOI_MT'] = round(pd.to_numeric(Finaldata_plot['TotalCo2_mt']) * 10 ** 6 / pd.to_numeric(Finaldata_plot['transportation_mt']), 2)
            Finaldata_plot['EEOI_MT'] = round(pd.to_numeric(Finaldata_plot['TotalCo2_mt']) * 10 ** 6 / pd.to_numeric(Finaldata_plot['transportation_mt']), 2)
            
            #print("pareekshana++++++++++++++++++++++++++++++++++++",Finaldata_plot)
            Finaldata_plot['EEOI_TEU'] = round(pd.to_numeric(Finaldata_plot['TotalCo2_mt']) * 10 ** 6 / pd.to_numeric(Finaldata_plot['teu_transport_work']),2)
        else:
            Finaldata_plot=Finaldata_plot[Finaldata_plot['transportation_mt']!=0]
            Finaldata_plot['EEOI_TEU'] = np.NaN
            Finaldata_plot['EEOI_MT'] = round(pd.to_numeric(Finaldata_plot['TotalCo2_mt']) * 10 ** 6 / pd.to_numeric(Finaldata_plot['transportation_mt']), 2)

        Finaldata_plot['year']=year1
        movingaveragedata1=Finaldata_plot[['voyage_order','EEOIGOALMT','EEOIGOALTEU','EEOI_MT','EEOI_TEU','year']]
        movingaveragedata1['EEOI For Cargo [MT]'] =Finaldata_plot['EEOI_MT']
        movingaveragedata1['EEOI For Cargo [TEU]']=Finaldata_plot['EEOI_TEU']
        # if not movingaveragedata1.empty:
        #     moving_average=int(moving_average)
        #     movingaveragedata1['movingavgmt']=movingaveragedata1['EEOI For Cargo [MT]'].rolling(moving_average).mean()
        #     movingaveragedata1['movingavg2mt'] = movingaveragedata1['EEOI For Cargo [TEU]'].rolling(moving_average).mean()
        # else:
        #     movingaveragedata1=[]
        # movingaveragedata1['S.No']=movingaveragedata1.index

        # teu  =df1.groupby(['imo','voyage_order'])['teu_transport_work'].sum().reset_index()
        cargometric['imo']=new['imo']
        cargometric['teu']=new1['teu_transport_work']
        
        cargometric['distance'] = np.where(pd.to_numeric(cargometric['year']) <= 2019, cargometric['distance1'], cargometric['distance2'])
        #print("cargometric")
        #print(cargometric)
        # for i in range(0,len(cargometric)):
        #     #print("274",i)
        #     if int(cargometric['year'][i]) <= 2019:
        #         cargometric['distance'] =  cargometric['distance1']   
            
        #     else:
        #         cargometric['distance'] =  cargometric['distance2']
        # hfo = df1.groupby(['eeoi_voyage_no', 'imo'])['fuel_me_rsdl_hs','fuel_aux_rsdl_hs','fuel_boiler_rsdl_hs'].sum().reset_index()
        eeoidata['voyage_order']=df1_new['voyage_order']
            # try:
        if int(year1) < 2020:
            eeoidata['hfo'] = df1_new['fuel_me_hs'] + df1_new['fuel_aux_hs'] + df1_new['fuel_boiler_hs']
            eeoidata['lfo'] = df1_new['fuel_me_ls']+df1_new['fuel_aux_ls']+df1_new['fuel_boiler_ls']
            eeoidata['mgo'] = df1_new['fuel_me_mdo']+df1_new['fuel_aux_mdo']+df1_new['fuel_boiler_mdo']+ df1_new['fuel_me_mgo']+df1_new['fuel_aux_mgo']+df1_new['fuel_boiler_mgo']+df1_new['fuel_me_mgo_ls']+df1_new['fuel_boiler_mgo_ls']+df1_new['fuel_aux_mgo_ls']
        else:
            eeoidata['hfo']=pd.to_numeric(df1_new['fuel_me_rsdl_hs'])+pd.to_numeric(df1_new['fuel_aux_rsdl_hs'])+pd.to_numeric(df1_new['fuel_boiler_rsdl_hs'])
        
            eeoidata['lfo']=pd.to_numeric(df1_new['fuel_me_rsdl_vls']) + pd.to_numeric(df1_new['fuel_aux_rsdl_vls']) +pd.to_numeric(df1_new['fuel_boiler_rsdl_vls']) + pd.to_numeric(df1_new['fuel_me_rsdl_uls']) + pd.to_numeric(df1_new['fuel_aux_rsdl_uls']) + pd.to_numeric(df1_new['fuel_boiler_rsdl_uls'])
            
            eeoidata['mgo']=pd.to_numeric(df1_new['fuel_me_dstlt_vls']) + pd.to_numeric(df1_new['fuel_aux_dstlt_vls']) + pd.to_numeric(df1_new['fuel_boiler_dstlt_vls']) + pd.to_numeric(df1_new['fuel_me_dstlt_uls']) + pd.to_numeric(df1_new['fuel_aux_dstlt_uls']) + pd.to_numeric(df1_new['fuel_boiler_dstlt_uls'])+pd.to_numeric(df1_new['fuel_me_tnktnr_dstlt_vls']) + pd.to_numeric(df1_new['fuel_aux_tnktnr_dstlt_vls']) + pd.to_numeric(df1_new['fuel_boiler_tnktnr_dstlt_vls'])
    # df1['totalco2']=((pd.to_numeric(df1['fuel_me_rsdl_hs'])+pd.to_numeric(df1['fuel_aux_rsdl_hs'])+pd.to_numeric(df1['fuel_boiler_rsdl_hs']))*3.114)+((pd.to_numeric(df1['fuel_me_rsdl_vls'])+pd.to_numeric(df1['fuel_aux_rsdl_vls'])+pd.to_numeric(df1['fuel_boiler_rsdl_vls'])+pd.to_numeric(df1['fuel_me_rsdl_uls'])+pd.to_numeric(df1['fuel_aux_rsdl_uls'])+pd.to_numeric(df1['fuel_boiler_rsdl_uls']))*3.151)   +((pd.to_numeric(df1['fuel_me_dstlt_vls'])+pd.to_numeric(df1['fuel_aux_dstlt_vls'])+pd.to_numeric(df1['fuel_boiler_dstlt_vls'])+pd.to_numeric(df1['fuel_me_dstlt_uls'])+pd.to_numeric(df1['fuel_aux_dstlt_uls'])+pd.to_numeric(df1['fuel_boiler_dstlt_uls'])+pd.to_numeric(df1['fuel_me_tnktnr_dstlt_vls'])+pd.to_numeric(df1['fuel_aux_tnktnr_dstlt_vls'])+pd.to_numeric(df1['fuel_boiler_tnktnr_dstlt_vls']))*3.206)
        eeoidata['totalco2']=eeoidata['lfo'] * 3.114 +eeoidata['hfo'] * 3.114 +eeoidata['mgo'] * 3.206 

        # eeoidata['hfo']=df1_new['fuel_me_rsdl_hs']+df1_new['fuel_aux_rsdl_hs']+df1_new['fuel_boiler_rsdl_hs']
      

        # eeoidata['lfo'] = df1_new['fuel_me_rsdl_vls'] + df1_new['fuel_aux_rsdl_vls'] +df1_new['fuel_boiler_rsdl_vls'] +df1_new['fuel_me_rsdl_uls'] +df1_new['fuel_aux_rsdl_uls'] +df1_new['fuel_boiler_rsdl_uls']
        # eeoidata['mdo_mgo'] =df1_new['fuel_me_dstlt_vls'] + df1_new['fuel_aux_dstlt_vls'] + df1_new['fuel_boiler_dstlt_vls'] + df1_new['fuel_me_dstlt_uls'] + df1_new['fuel_aux_dstlt_uls'] + df1_new['fuel_boiler_dstlt_uls']+df1_new['fuel_me_tnktnr_dstlt_vls'] + df1_new['fuel_aux_tnktnr_dstlt_vls'] + df1_new['fuel_boiler_tnktnr_dstlt_vls']
        eeoidata['imo']=df1_new['imo']     
        merge_data = pd.merge(eeoidata, cargometric,how='left', left_on=['voyage_order','imo'], right_on = ['voyage_order','imo'])
        merge_data['totalco2'] = merge_data['totalco2'].replace({np.nan:0})

        # merge_data=merge_data[merge_data['year']==year1] 
        merge_data['cargo_total']=pd.to_numeric(merge_data['cargo_total'])
        merge_data['cargo_distance']=pd.to_numeric(pd.to_numeric(merge_data['cargo_total'])*pd.to_numeric(merge_data['distance']))
        merge_imo = merge_data.groupby(['imo']).sum().reset_index()
        #print(merge_imo['cargo_distance'])
        totalcargobyvessel['cargo_distance']=merge_imo['cargo_distance']
        # cargomt = merge_data.groupby(['imo'])['cargo_total'].sum().reset_index()
        totalcargobyvessel['cargomt']=merge_imo['cargo_total']
        # cargoteu  = merge_data.groupby(['imo'])['teucargo'].sum().reset_index()
        totalcargobyvessel['cargoteu']=merge_imo['teucargo']
        
        totalcargobyvessel['voyages']  = len(merge_data['voyage_order'].unique())
        # totalcargobyvessel['voyages']=voyages['voyage_order']
        # distance  = merge_data.groupby(['imo'])['distance'].sum().reset_index()
        totalcargobyvessel['distance']=merge_imo['distance']
        totalcargobyvessel['year']=year1
        # mt  = merge_data.groupby(['imo'])['mt'].sum().reset_index()
        totalcargobyvessel['mt']=merge_imo['mt']
        # teu  = merge_data.groupby(['imo'])['teu'].sum().reset_index()
        totalcargobyvessel['teu']=merge_imo['teu']
        # hfo = merge_data.groupby(['imo'])['hfo'].sum().reset_index()
        totalcargobyvessel['hfo']=merge_imo['hfo']
        # lfo = merge_data.groupby(['imo'])['lfo'].sum().reset_index()
        totalcargobyvessel['lfo'] = merge_imo['lfo']
        # mdo_mgo = merge_data.groupby(['imo'])['mdo_mgo'].sum().reset_index()
        totalcargobyvessel['mdo_mgo']=merge_imo['mgo']
        merge_data['totalco2'] = merge_imo['totalco2'].replace({np.nan:0})

        # totalco2  = merge_data.groupby(['imo'])['totalco2'].sum().reset_index()
        totalcargobyvessel['imo']=merge_imo['imo']
        totalcargobyvessel['totalco2']=merge_imo['totalco2']
        
        finaldata = totalcargobyvessel.sort_values(by=['imo'], ascending=True)
        finaldata['totalco2_mt'] = finaldata['totalco2']
        #print("finaldata",finaldata)
        finaldata['totalco2_kgnm'] =round((finaldata['totalco2_mt'] ) / finaldata['distance'], 2)
        finaldata['equivalent_hfo'] = round(((finaldata['hfo'] + finaldata['lfo'] + finaldata['mdo_mgo'] )* 1.05)/1000, 2)
        finaldata['equip_nm'] =  round((finaldata['equivalent_hfo'] ) / finaldata['distance'], 2)
        finaldata['eeoi_mt'] = (pd.to_numeric(finaldata['totalco2_mt']) * (10 ** 6)) / finaldata['cargo_distance']
        finaldata['eeoi_teu'] = round(round(finaldata['totalco2_mt'],2) * (10 ** 6 )/ round(finaldata['teu'],2), 2)
        #print("finaldata['eeoi_mt']finaldata['eeoi_mt']",finaldata['eeoi_mt'])
        finaldata['fuelkg_nm'] = round(((finaldata['equivalent_hfo'] ) / finaldata['distance']), 2)
        # finaldata=pd.merge(finaldata, eeoigoal,how='left', left_on=['imo'], right_on = ['vesselname'])
        finaldata['average_perteu'] = finaldata['cargoteu'] / finaldata['voyages']
        finaldata['average_permt'] = finaldata['cargomt'] / finaldata['voyages']
        finaldata['average_distance'] = finaldata['distance'] / finaldata['voyages']
        finaldata['average_fuelcons'] = finaldata['equivalent_hfo'] / finaldata['voyages']
        # finaldata['eeoi_mt']=pd.to_numeric(finaldata['eeoi_mt'])
        finaldata['eeoi_mt']=round(float(finaldata['eeoi_mt'][0]),2)
        finaldata['eeoi_teu']=round(float(finaldata['eeoi_teu'][0]),2)
        if not movingaveragedata1.empty:
            moving_average=int(moving_average)
            # movingaveragedata1['EEOI For Cargo [MT]']=movingaveragedata1['EEOI For Cargo [MT]'].replace({np.nan:None})
         
            movingaveragedata1['movingavgmt']=movingaveragedata1['EEOI For Cargo [MT]'].rolling(moving_average).mean()
            movingaveragedata1['movingavg2mt'] = movingaveragedata1['EEOI For Cargo [TEU]'].rolling(moving_average).mean()
            #print(movingaveragedata1['movingavgmt'])
            
        else:
            movingaveragedata1=pd.DataFrame()
        print("1487",movingaveragedata1)
        if not movingaveragedata1.empty:
            movingaveragedata1['S.No']=range(1,len(movingaveragedata1)+1)
        

        # movingaveragedata1 = movingaveragedata1.dropna()
        #print(finaldata['eeoi_mt'][0])
        #print(finaldata['eeoi_teu'])
        finaldata = finaldata.replace({np.nan:None})
        
        finaldata_samp = finaldata.to_json(orient="records")
        finaldata_samp = json.loads(finaldata_samp)
        total_cargo = totalcargobyvessel.to_json(orient="records")
        total_cargo = json.loads(total_cargo)
    
        
        return finaldata,movingaveragedata1
    else:
        return new,new
@router.get('/api/v1/eeoi_mrv/period_comparison/wise')#, response_model=vessel_schema.Response
def index(vdm_db:Session = Depends(get_vdm_db),db= Depends(get_db),imo:str=None,year1:str=None,year2:str=None,type:str=None,fleet:str=None,moving_average:str=None,classs:str=None,first_Period_min:str=None,first_Period_max:str=None,second_Period_min:str=None,second_Period_max:str=None,token : Session = Depends(get_token)):
    cache_data = 0
    if year1 is None and year2 is None:
       cache_data = 1
       first_Period_min 
       first_Period_max 
       second_Period_min
       second_Period_max
       
       
       first_Period_min = datetime.strptime(first_Period_min,"%Y-%m-%d")   
       year1 = first_Period_min.year
       
       second_Period_max = datetime.strptime(second_Period_max,"%Y-%m-%d")   
       year2 = second_Period_max.year
       final_data = utility.get_data(key=CACHEKEY.PERIOD_COMPARISON+str(year1)+str(year2)+str(fleet)+str(first_Period_min)+str(first_Period_max)+str(second_Period_min)+str(second_Period_max)+str(classs)+str(imo)+str(moving_average)+str(type))
    else:
       final_data = utility.get_data(key=CACHEKEY.PERIOD_COMPARISON+str(fleet)+str(year1)+str(year2)+str(classs)+str(imo)+str(moving_average)+str(type))
        
    
    if final_data is not None:

        cache = True
    else:
        t1=datetime.now()
        
        if type=='2':
            if fleet == '0' or fleet == 'All':
                vessels = cache_set.get_vdm_vessels(vdm_db) 
                
            else:  
                vessels = cache_set.get_fleet_wise(vdm_db , fleet)
            
        elif type=='3':
            # #print(classs)
            vessels=cache_set.get_imos_by_class(vdm_db,classs)
        # #print(vessels)  
        imo=[]
        if vessels:
            for i in vessels:
                if i not in imo:
                    imo.append(str(i['imo']))
        
        # imo = [str(i['imo']) for i in vessels if str(i['imo']) not in imo]
        # #print(imo)
            # imo=set(imo)
        t1=datetime.now()
        print("Starting")

        vdm_vessel_data = cache_set.get_mcr_filter(vdm_db)
        vdm_vessel_data=pd.DataFrame(vdm_vessel_data)
        vdm_vessel_data = vdm_vessel_data[vdm_vessel_data['imo'].isin(imo)]
        vdm_vessel_data = vdm_vessel_data.to_json(orient="records")
        vdm_vessel_data = json.loads(vdm_vessel_data)


        t2=datetime.now()
 
        # retur
        t1=datetime.now()
        data = utility.get_data(key=CACHEKEY.VESSEL_ATTRIBUTE)
        if data  is not None :
            cache = True
            print("from cache")
        else:
            data=open('stub/vessel_attribute.json',encoding="utf8")
            # data1 = json.load(data, strict=False)
            try:

                if data is not None:

                    cache = False

                    data = json.dumps(jsonable_encoder(data))

                    state = utility.set_data(key=CACHEKEY.VESSEL_ATTRIBUTE, value= data,seconds = 2.628e+6)


                    if state is True:

                            print('Cache Set Successfully')

            except Exception as e:
                    print(e)

                    print('cache set failure')
        data = json.loads(data)
        
        t2=datetime.now()
  
        final=[]
        yob=[]
        eeoitype=[]
        vessel1=[]
        # for i in imo:
        #     # #print(i)
        #     vessel_data1=list(filter(lambda x:x['imo'] == str(i) and (x['attribute_id'] ==  7 ), vdm_vessel_data))
        #     # #print(vessel_data1[0])
        #     if vessel_data1:
        #         yob.append(vessel_data1[0])
        #     final1=list(filter(lambda x:x['imo'] == int(i) and (x['attribute_id'] == 823  ), data1))
        #     if final1:
        #         # #print(final1[0])
        #         final.append(final1[0])
            
        #     type=list(filter(lambda x:x['imo'] == str(i) and  x['attribute_id'] == 4, vdm_vessel_data))
        #     if type:
        #         eeoitype.append(type[0])
        #     vessel=list(filter(lambda x:x['imo'] == str(i) and (x['attribute_id'] ==  580 ), vdm_vessel_data))
        #     # #print(vessel_data1[0])
        #     if vessel:
        #         vessel1.append(vessel[0])

        data_list =[]
        eeoigoalmt1=[]
        # vdm_vessel_data = list(filter(lambda x: x['attribute_id'] ==  7 or x['attribute_id'] == 4 or x['attribute_id'] == 823, vdm_vessel_data))
      
        if vdm_vessel_data:
            yob_data = list(filter(lambda x: x['attribute_id'] ==  7, vdm_vessel_data))
            eeoitype_data = list(filter(lambda x:x['attribute_id'] == 4, vdm_vessel_data))
            data1 = list(filter(lambda x: x['attribute_id'] ==  823, vdm_vessel_data)) 
            for i in imo:
                data_dict = {}
                data_dict['imo'] = i
                if yob_data:
                    vessel_data1=list(filter(lambda x:x['imo'] == str(i) , yob_data))
                else:
                    vessel_data1=None
                if vessel_data1:
                    data_dict['yob'] = vessel_data1[0]['value']
                    data_dict['vessel_name']=vessel_data1[0]['name']
                    data_dict['fleet']=vessel_data1[0]['fleet']
                else:
                    data_dict['yob'] = None
                    data_dict['vessel_name']=None
                    data_dict['fleet']=None

                final1=list(filter(lambda x:x['imo'] == str(i) , data1))
                if final1:
                    # #print(final1[0])
                    data_dict['final'] = final1[0]['value']
                else:
                    data_dict['final'] = None

                
                eeoitype=list(filter(lambda x:x['imo'] == str(i) , eeoitype_data))
                if eeoitype:
                    data_dict['eeoitype'] = eeoitype[0]['value']
                else:
                    data_dict['eeoitype'] = None
                    
                # vessel=list(filter(lambda x:x['imo'] == str(i) , yob_data))
                if eeoitype:
                    data_dict['class'] = eeoitype[0]['sister_code']
                    # data_dict['name']=vessel[0]['name']
                else:
                    data_dict['class'] = None
                if data_dict['yob'] and( data_dict['final'] and data_dict['final']!='NA' and data_dict['final']!='No'):
                    data_dict['eeoigoalmt1'] = round((float(data_dict['final']) + ((float(year1) - float(data_dict['yob'])))/100)*float(data_dict['final']),2)
                    data_dict['eeoigoalmt2'] = round((float(data_dict['final']) + ((float(year2) - float(data_dict['yob'])))/100)*float(data_dict['final']),2)

                else:
                    data_dict['eeoigoalmt1'] = 0
                    data_dict['eeoigoalmt2'] = 0

                data_list.append(data_dict)
            else:
                pass
      
        print("After Here")

        vessel_df = pd.DataFrame.from_dict(data_list)

        #print('4227:')
            
        # #print(vessel1)
        # vessel_df_1 = pd.DataFrame.from_dict(final)
        
        # # pri
        # vessel_df_2 = pd.DataFrame.from_dict(yob)
    
        # vessel_df_3 = pd.DataFrame.from_dict(eeoitype)
        # vessel_df_4 = pd.DataFrame.from_dict(vessel1)
        # #print(4230)
        # #print('before vesseldf4')
        # # #print(vessel_df_4['imo'].unique())
        # result =pd.merge(vessel_df_1,vessel_df_2, left_index=True, right_index=True, how='outer')
        # # #print(vessel_df_1,vessel_df_2)
        # # #print(result)
        # eeoigoalmt1=pd.DataFrame()
        # eeoigoalmt2=pd.DataFrame()

        # if not result.empty:
            
        #     eeoigoalmt1['eeoigoalmt1'] = round(pd.to_numeric(result['value_y']) + (((float(year1) - pd.to_numeric(result['value_x']))/100)*pd.to_numeric(result['value_y'])),2)
        #     eeoigoalmt1['imo']=imo
        # else:
        #     eeoigoalmt1=0.0

        # if not result.empty:
        #     eeoigoalmt2['eeoigoalmt2'] = round(pd.to_numeric(result['value_y']) + (((float(year2) - pd.to_numeric(result['value_x']))/100)*pd.to_numeric(result['value_y'])),2)
        #     eeoigoalmt2['imo']=imo
        # else:
        #     eeoigoalmt2=0.0 
        t2=datetime.now()
        # exit()


        t1=datetime.now()
        if type=='2':
            data = cache_set.get_NoonDatas_list(db,imo,year1,year2,fleet) 
        elif type=='3':
            data = cache_set.get_NoonDatas_list(db,imo,year1,year2,classs) 
        if first_Period_min and first_Period_max and  second_Period_min and second_Period_max:
            first_Period_min = str(first_Period_min)
            first_Period_max = str(first_Period_max) + " 23:59:59"
            second_Period_min = str(second_Period_min) + " 00:00:00"
            second_Period_max = second_Period_max.date()
            second_Period_max = str(second_Period_max) + " 23:59:59"
            data = list(filter(lambda x:(first_Period_min <= x['corrected_date'] <= first_Period_max) or (second_Period_min <= x['corrected_date'] <= second_Period_max),data ))
        t2=datetime.now()

        

        if not data:
            return {"data": []}
        t1=datetime.now()
        df=pd.DataFrame(data) 
        if df.empty:
            return {"data": []} 
        t2=datetime.now()
        t1=datetime.now()
    
        finaldata1=get_yearanalysis_wise(df,year1,vessel_df,moving_average)
       
        finaldata2=get_yearanalysis_wise(df,year2,vessel_df,moving_average)

        t2=datetime.now()

        t1=datetime.now()
        if not finaldata1.empty:
            finaldata1=finaldata1.round(2)
        # moving_average1=moving_average1.round(2)
        print("gfdsgf",finaldata2)
        if not finaldata2.empty:
            finaldata2=finaldata2.round(2)
        # moving_average2=moving_average2.round(2)
        
        data_list = []
        finaldata1 = finaldata1.replace({np.inf:None})
        finaldata2=finaldata2.replace({np.inf:None})
        finaldata1.rename(columns={'class_x':'class'}, inplace = True)
        finaldata2.rename(columns={'class_x':'class'}, inplace = True)


        t1=datetime.now()
        for index, row in finaldata1.iterrows():
            

            data_dict = {}
            data_dict['vesselname'] = row['imo']
            data_dict['year1'] = row['eeoi_mt']
            data_dict['index'] = 'EEOI for Cargo [mt]'
            data_list.append(data_dict)

        

            data_dict = {}
            data_dict['vesselname'] = row['imo']
            data_dict['year1'] = row['totalco2']
            data_dict['index'] = 'CO2[mt]'
            data_list.append(data_dict)



            data_dict = {}
            data_dict['vesselname'] = row['imo']
            data_dict['year1'] = row['cargo_total']
            data_dict['index'] = 'Cargo[mt]'
            data_list.append(data_dict)

            data_dict = {}
            data_dict['vesselname'] = row['imo']
            data_dict['year1'] = row['distance']
            data_dict['index'] = 'Total Distance(Nm)'
            
            data_list.append(data_dict)

            

            
            data_dict = {}
            data_dict['vesselname'] = row['imo']
            data_dict['year1'] = row['year']
            data_dict['index'] = 'Year' 
            data_list.append(data_dict)
  
           
        
            

        

        data_list_2 = []
        for index, row in finaldata2.iterrows():
            voyages_data =  list(filter(lambda x:x['index'] == 'Voyages' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['voyages']
                data_list_2.append(i)
        # i['imo']==row['imo']) and (i['index']=='EEOI for Cargo [mt]
            # for i in voyages_data:
            
            voyages_data =  list(filter(lambda x:x['index'] == 'EEOI for Cargo [mt]' and x['vesselname'] == row['imo'] , data_list))
            for i in voyages_data:
                i['year2'] = row['eeoi_mt']
                data_list_2.append(i)
            
            # for i in voyages_data:
            # for i in voyages_data:
            #     i['year2'] = row['voyages']
            #     data_list_2.append(i)

                
                

            voyages_data =  list(filter(lambda x:x['index'] == 'EEOI for Cargo [TEU]' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['eeoi_teu']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'CO2[mt]' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['totalco2']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'CO2[kg/nm]' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['totalco2_kgnm']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'Cargo[mt]' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['cargo_total']
                data_list_2.append(i)
            
            
            voyages_data =  list(filter(lambda x:x['index'] == 'EEOI for Cargo [TEU]' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['equivalent_hfo']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'HFO' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['hfo']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'LFO' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['lfo']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'MDO_MGO' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['mdo_mgo']
                data_list_2.append(i)
        
            
            voyages_data =  list(filter(lambda x:x['index'] == 'Total equiv.    HFO [mt]' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['equivalent_hfo']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'Avg. [TEU] Per Voyage' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['average_perteu']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'Avg. [mt] Per Voyage' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['average_permt']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'Year' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['year']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'Avg. Distance Per Voyage' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['average_distance']
                data_list_2.append(i)
            
            voyages_data =  list(filter(lambda x:x['index'] == 'Total Distance(Nm)' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['distance']
                data_list_2.append(i)
            voyages_data =  list(filter(lambda x:x['index'] == 'Avg. Consumption Per Voyage' and x['vesselname'] == row['imo'] , data_list))
            # for i in voyages_data:
            for i in voyages_data:
                i['year2'] = row['average_fuelcons']
                data_list_2.append(i)

            


        # if len(finaldata1) > len(finaldata2):
        table1=pd.merge(finaldata1,finaldata2, left_index=True, right_index=True, how='outer')
        # else:  
        #     table1=pd.merge(finaldata2,finaldata1, left_index=True, right_index=True, how='outer')
        
        
        if not finaldata1.empty and not finaldata2.empty:
            voyages=[float(table1['total_voyages_x'][0]),float(table1['total_voyages_y'][0])]
            eeoi_mt=[table1['eeoi_mt_total_x'][0],table1['eeoi_mt_total_y'][0]]
            eeoi_teu=[table1['eeoi_teu_total_x'][0],table1['eeoi_teu_total_y'][0]]
            totalco2_mt=[table1['TotalCo2_mt_total_x'][0],table1['TotalCo2_mt_total_y'][0]]
            # totalco2_mt=[table1['TotalCo2_mt_x'][0],table1['TotalCo2_mt_y'][0]]
            totalco2_kgnm=[table1['totalco2_kgnm_total_x'][0],table1['totalco2_kgnm_total_y'][0]]
            cargomt=[table1['cargomt_x'][0],table1['cargomt_y'][0]]
            cargoteu=[table1['teu_cargo_total_x'][0],table1['teu_cargo_total_y'][0]]
            equivalent_hfo=[table1['equivalent_hfo_total_x'][0],table1['equivalent_hfo_total_y'][0]]
            hfo=[table1['hfo_total_x'][0],table1['hfo_total_y'][0]]
            lfo=[table1['lfo_total_x'][0],table1['lfo_total_y'][0]]
            mdo_mgo=[table1['MDO_MGO_total_x'][0],table1['MDO_MGO_total_y'][0]]
            # equivalent_hfo=[table1['equivalent_hfo_x'][0],table1['equivalent_hfo_y'][0]]
            average_perteu=[table1['average_perteu_total_x'][0],table1['average_perteu_total_y'][0]]
            average_permt=[table1['average_permt_total_x'][0],table1['average_permt_total_y'][0]]
            year=[table1['year_x'][0],table1['year_y'][0]]
            total_distance=[table1['distance_total_x'][0],table1['distance_total_y'][0]]
            average_distance=[table1['average_distance_total_x'][0],table1['average_distance_total_y'][0]]
            average_fuelcons=[table1['average_fuelcons_total_x'][0],table1['average_fuelcons_total_y'][0]]
        elif not finaldata1.empty and finaldata2.empty:
            voyages=[float(table1['total_voyages'][0]),0]
            eeoi_mt=[table1['eeoi_mt_total'][0],0]
            eeoi_teu=[table1['eeoi_teu_total'][0],0]
            totalco2_mt=[table1['TotalCo2_mt_total'][0],0]
            # totalco2_mt=[table1['TotalCo2_mt'][0],0]
            totalco2_kgnm=[table1['totalco2_kgnm_total'][0],0]
            cargomt=[table1['cargomt'][0],0]
            cargoteu=[table1['teu_cargo_total'][0],0]
            # equivalent_hfo=[table1['equivalent_hfo'][0],0]
            hfo=[table1['hfo_total'][0],0]
            lfo=[table1['lfo_total'][0],0]
            mdo_mgo=[table1['MDO_MGO_total'][0],0]
            equivalent_hfo=[table1['equivalent_hfo_total'][0],0]
            average_perteu=[table1['average_perteu_total'][0],0]
            average_permt=[table1['average_permt_total'][0],0]
            year=[table1['year_x'][0],0]
            total_distance=[table1['distance_total'][0],0]
            average_distance=[table1['distance_total'][0],0]
            average_distance=[table1['average_distance_total'][0],0]
            average_fuelcons=[table1['average_fuelcons_total'][0],0]
        elif finaldata1.empty and not finaldata2.empty:
            voyages=[0,int(table1['total_voyages'][0])]
            eeoi_mt=[0,table1['eeoi_mt_total'][0]]
            eeoi_teu=[0,table1['eeoi_teu_total'][0]]
            totalco2_mt=[0,table1['TotalCo2_mt_total'][0]]
            # totalco2_mt=[0,table1['TotalCo2_mt'][0]]
            totalco2_kgnm=[0,table1['totalco2_kgnm_total'][0]]
            cargomt=[0,table1['cargomt'][0]]
            cargoteu=[0,table1['teu_cargo_total'][0]]
            # equivalent_hfo=[0,table1['equivalent_hfo'][0]]
            hfo=[0,table1['hfo_total'][0]]
            lfo=[0,table1['lfo_total'][0]]
            mdo_mgo=[0,table1['MDO_MGO_total'][0]]
            equivalent_hfo=[0,table1['equivalent_hfo_total'][0]]
            average_perteu=[0,table1['average_perteu_total'][0]]
            average_permt=[0,table1['average_permt_total'][0]]
            year=[0,table1['year_x'][0]]
            total_distance=[0,table1['distance_total_y'][0]]
            average_distance=[0,table1['distance_total'][0]]
            average_distance=[0,table1['average_distance_total'][0]]
            average_fuelcons=[0,table1['average_fuelcons_total'][0]]
           
            
        else:
            return []
        # imo=[table1['imo_x'][0],table1['imo_y'][0]]
        
      
        try:
            total_distance.append(round((total_distance[1]-total_distance[0])*100/total_distance[0],0))
        except:
            total_distance.append('0.0')
        try:
            average_distance.append(round((average_distance[1]-average_distance[0])*100/average_distance[0],0))
        except:
            average_distance.append('0.0')
        # eeoi_mt=[table1['eeoi_mt_x'][0],table1['eeoi_mt_y'][0]]
        # equip_nm=[table1['equip_nm_x'][0],table1['equip_nm_y'][0]]
        # distance=[table1['distance_x'][0],table1['distance_y'][0]]
        try:
            average_perteu.append(round((average_perteu[1]-average_perteu[0])*100/average_perteu[0],0))
        except:
            average_perteu.append('0.0')
        try:
            average_permt.append(round((average_permt[1]-average_permt[0])*100/average_permt[0],0))
        except:
            average_permt.append('0.0')
        try:
            lfo.append(round((lfo[1]-lfo[0])*100/lfo[0],0))
        except:
            lfo.append('0.0')
        try:
            mdo_mgo.append(round((mdo_mgo[1]-mdo_mgo[0])*100/mdo_mgo[0],0))
        except:
            mdo_mgo.append('0.0')
        try:
            hfo.append(round((hfo[1]-hfo[0])*100/hfo[0],0))
        except:
            hfo.append('0.0')
        try:
            equivalent_hfo.append(round((equivalent_hfo[1]-equivalent_hfo[0])*100/equivalent_hfo[0],0))
        except:
            equivalent_hfo.append('0.0')
        try:
            cargomt.append(round((cargomt[1]-cargomt[0])*100/cargomt[0],0))
        except:
            cargomt.append('0.0')
        try:
            cargoteu.append(round((cargoteu[1]-cargoteu[0])*100/cargoteu[0],0))
        except:
            cargoteu.append('0.0')
        try:
            totalco2_kgnm.append(round((totalco2_kgnm[1]-totalco2_kgnm[0])*100/totalco2_kgnm[0],0))
        except:
            totalco2_kgnm.append('0.0')
        totalco2_mt.append(round((totalco2_mt[1]-totalco2_mt[0])*100/totalco2_mt[0],0))
        try:
            # print(voyages[1],voyages[0])
            voyages.append(round((voyages[1]-voyages[0])*100/voyages[0],0))
        except:
            voyages.append('0.0')
        try:
            eeoi_mt.append(round((eeoi_mt[1]-eeoi_mt[0])*100/eeoi_mt[0],0))
        except:
            eeoi_mt.append('0.0')
        try:
            eeoi_teu.append(round((eeoi_teu[1]-eeoi_teu[0])*100/eeoi_teu[0],0))
        except:
            eeoi_teu.append('0.0')
        try:
            year.append(round((year[1]-year[0])*100/year[0],0))
        except:
            year.append('0.0')
        try:
            average_fuelcons.append(round((average_fuelcons[1]-average_fuelcons[0])*100/average_fuelcons[0],0))
        except:
            average_fuelcons.append('0.0')
        new1=pd.DataFrame(data=[cargoteu,cargomt,totalco2_mt,totalco2_kgnm,eeoi_teu,eeoi_mt,equivalent_hfo,total_distance,hfo,lfo,mdo_mgo,voyages,average_perteu,average_permt,average_distance,average_fuelcons],index=["Cargo [TEU]",
        "Cargo[MT]",
        "CO2[MT]"    ,
        "CO2[MT/NM]",
        "EEOI for Cargo [TEU]",
        "EEOI for Cargo [MT]",
        "Total equiv. HFO [Kilo MT]",
        "TotalDistance",
        "HFO",
        "LFO"    ,
        "MDO_MGO",     
        "Voyages",
        "Avg. [TEU] Per Voyage" ,
        "Avg. [MT] Per Voyage"  ,
        "Avg. Distance Per Voyage",
        "Avg. Consumption Per Voyage"])
        col=['year1','year2','improvement']
    
        new1=new1.round(2)
        new1.columns=np.array(col)
        new1['index']=new1.index

    
        new1 = new1.to_json(orient="records")
        table2 = json.loads(new1)
        # return finaldata1
        
       

        # if not finaldata1.empty:

        #     finaldata1['TotalCo2_mt'] = pd.to_numeric(finaldata1['totalco'])
        # if not finaldata2.empty:
        #     finaldata2['TotalCo2_mt'] = pd.to_numeric(finaldata2['TotalCo2_mt'])
        
        finaldata_1 = finaldata1.round(2)
        finaldata_1 = finaldata_1.to_json(orient="records")
        finaldata_1 = json.loads(finaldata_1)
        
        finaldata2 = finaldata2.round(2)

        finaldata_2 = finaldata2.to_json(orient="records")
        finaldata_2 = json.loads(finaldata_2)
        # if not finaldata1.empty and finaldata2.empty:
        #     secondperiod={}
            
        #     finaldata1[['xcargo','teucar go','distance1','distance2','HFO','LFO','MDO_MGO','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','equip_nm','equivalent_hfo','totalco2_kgnm','cargomt','mt','fleet','distance','cargoteu','eeoi_teu','totalco2_mt']].apply(pd.to_numeric).round(2)
        #     firstperiod=finaldata1[['imo','vessel_name','fleet','class','year','xcargo','teucargo','HFO','LFO','MDO_MGO','TotalCo2_mt','eeoi_voyage_no','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','equip_nm','equivalent_hfo','totalco2_kgnm','cargomt','mt_x','distance_x','cargoteu','eeoi_teu','totalco2_mt']]
        #     firstperiod['TotalCo2_mt'] = pd.to_numeric(firstperiod['TotalCo2_mt'])
        # if not finaldata1.empty and  finaldata2.empty:
        #     finaldata1[['xcargo','teucargo','HFO','LFO','MDO_MGO','TotalCo2_mt','eeoi_voyage_no_x','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','equip_nm','equivalent_hfo','totalco2_kgnm','cargomt','mt_x','distance_x','cargoteu','eeoi_teu','totalco2_mt']].apply(pd.to_numeric).round(2)
        # if not finaldata2.empty and finaldata1.empty:
        #     finaldata2[['xcargo','teucargo','HFO','LFO','MDO_MGO','TotalCo2_mt','eeoi_voyage_no_x','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','equip_nm','equivalent_hfo','totalco2_kgnm','cargomt','mt_x','distance_x','cargoteu','eeoi_teu','totalco2_mt']].apply(pd.to_numeric).round(2)
        # elif not finaldata2.empty and not finaldata1.empty:
        #     finaldata1[['xcargo','teucargo','HFO','LFO','MDO_MGO','TotalCo2_mt','eeoi_voyage_no_x','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','equip_nm','equivalent_hfo','totalco2_kgnm','cargomt','mt_x','distance_x','cargoteu','eeoi_teu','totalco2_mt']].apply(pd.to_numeric).round(2)
        #     finaldata2[['xcargo','teucargo','HFO','LFO','MDO_MGO','TotalCo2_mt','eeoi_voyage_no_x','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','equip_nm','equivalent_hfo','totalco2_kgnm','cargomt','mt_x','distance_x','cargoteu','eeoi_teu','totalco2_mt']].apply(pd.to_numeric).round(2)
        if finaldata1.empty and not finaldata2.empty:
            firstperiod=[]
            # firstperiod=firstperiod.round(2)
            finaldata2[['cargo_total','cargo_total_teu','HFO','LFO','MDO_MGO','totalco2_kgnm','totalco2','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','eeoi_teu','equivalent_hfo','cargo_transport_work','teu_transport_work','distance']].apply(pd.to_numeric)
            secondperiod=finaldata2[['vessel_name','imo','fleet','class','voyages','cargo_total','cargo_total_teu','HFO','LFO','MDO_MGO','totalco2_kgnm','totalco2','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','eeoi_teu','equivalent_hfo','cargo_transport_work','teu_transport_work','distance']]
            secondperiod.rename(columns={'LFO':'LFO (MT)','HFO':'HFO (MT)','cargo_total':'Cargo Total (MT)','cargo_total_teu':'Cargo Total (TEU)','fuelkg_nm':'Fuel per Miles(Kg/NM)','equivalent_hfo':'Equivalent HFO (MT)','cargo_transport_work':'Cargo TranSport Work (MT-NM)','distance':'Distance (NM)','fleet':'Fleet','eeoi_teu':'EEOI (gm/TEU-NM)','voyages':'Number of Voyages','totalco2':'Total CO2 (MT)','MDO_MGO':'MGO (MT)','average_fuelcons':'Fuel Consumption per Voyage (MT)','totalco2_kgnm':'CO2 per Miles (MT/NM)','vessel_name':'Vessel Name','eeoi_mt':'EEOI (gm/MT-NM)','average_perteu':'Cargo per Voyage (TEU)','average_permt':'Cargo per Voyage (MT)','imo':'IMO','class':'Class','teu_transport_work':'Cargo Transport Work (TEU-NM)','average_distance':'Distance per Voyage (NM)'}, inplace = True)
            
          
            
            secondperiod=secondperiod.round(2)
            secondperiod=secondperiod.to_json(orient="records")
            secondperiod = json.loads(secondperiod)
            # firstperiod = firstperiod.round(2)
            # firstperiod=firstperiod.to_json(orient="records")
            # firstperiod = json.loads(firstperiod)
            # secondperiod=secondperiod.to_json(orient="records")
            # secondperiod = json.loads(secondperiod)
        elif not finaldata1.empty and finaldata2.empty:
            secondperiod=[]
            finaldata1[['cargo_total','cargo_total_teu','HFO','LFO','MDO_MGO','totalco2_kgnm','totalco2','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','eeoi_teu','equivalent_hfo','cargo_transport_work','teu_transport_work','distance']].apply(pd.to_numeric)
            firstperiod=finaldata1[['vessel_name','imo','fleet','class','voyages','cargo_total','cargo_total_teu','HFO','LFO','MDO_MGO','totalco2_kgnm','totalco2','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','eeoi_teu','equivalent_hfo','cargo_transport_work','teu_transport_work','distance']]
            firstperiod.rename(columns={'LFO':'LFO (MT)','HFO':'HFO (MT)','cargo_total':'Cargo Total (MT)','cargo_total_teu':'Cargo Total (TEU)','fuelkg_nm':'Fuel per Miles(Kg/NM)','equivalent_hfo':'Equivalent HFO (MT)','cargo_transport_work':'Cargo TranSport Work (MT-NM)','distance':'Distance (NM)','fleet':'Fleet','eeoi_teu':'EEOI (gm/TEU-NM)','voyages':'Number of Voyages','totalco2':'Total CO2 (MT)','MDO_MGO':'MGO (MT)','average_fuelcons':'Fuel Consumption per Voyage (MT)','totalco2_kgnm':'CO2 per Miles (MT/NM)','vessel_name':'Vessel Name','eeoi_mt':'EEOI (gm/MT-NM)','average_perteu':'Cargo per Voyage (TEU)','average_permt':'Cargo per Voyage (MT)','imo':'IMO','class':'Class','teu_transport_work':'Cargo Transport Work (TEU-NM)','average_distance':'Distance per Voyage (NM)'}, inplace = True)
            
          
            firstperiod = firstperiod
            firstperiod=firstperiod.to_json(orient="records")
            firstperiod = json.loads(firstperiod)
            # firstperiod=firstperiod.to_json(orient="records")
            # firstperiod = json.loads(firstperiod)
        elif not finaldata2.empty and not finaldata1.empty:
            finaldata1[['cargo_total','cargo_total_teu','HFO','LFO','MDO_MGO','totalco2_kgnm','totalco2','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','eeoi_teu','equivalent_hfo','cargo_transport_work','teu_transport_work','distance']].apply(pd.to_numeric)
            firstperiod=finaldata1[['vessel_name','imo','fleet','class','voyages','cargo_total','cargo_total_teu','HFO','LFO','MDO_MGO','totalco2_kgnm','totalco2','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','eeoi_teu','equivalent_hfo','cargo_transport_work','teu_transport_work','distance']]
            firstperiod.rename(columns={'LFO':'LFO (MT)','HFO':'HFO (MT)','cargo_total':'Cargo Total (MT)','cargo_total_teu':'Cargo Total (TEU)','fuelkg_nm':'Fuel per Miles(Kg/NM)','equivalent_hfo':'Equivalent HFO (MT)','cargo_transport_work':'Cargo TranSport Work (MT-NM)','distance':'Distance (NM)','fleet':'Fleet','eeoi_teu':'EEOI (gm/TEU-NM)','voyages':'Number of Voyages','totalco2':'Total CO2 (MT)','MDO_MGO':'MGO (MT)','average_fuelcons':'Fuel Consumption per Voyage (MT)','totalco2_kgnm':'CO2 per Miles (MT/NM)','vessel_name':'Vessel Name','eeoi_mt':'EEOI (gm/MT-NM)','average_perteu':'Cargo per Voyage (TEU)','average_permt':'Cargo per Voyage (MT)','imo':'IMO','class':'Class','teu_transport_work':'Cargo Transport Work (TEU-NM)','average_distance':'Distance per Voyage (NM)'}, inplace = True)
           

            firstperiod = firstperiod.round(2)
           
            # secondperiod['TotalCo2_mt'] = pd.to_numeric(secondperiod['TotalCo2_mt'])

            firstperiod=firstperiod.to_json(orient="records")
            firstperiod = json.loads(firstperiod)
            # firstperiod.rename(columns={'distance1_x':'distance1','distance2_x':'distance2','distance_x':'distance','mt_x':'mt','year_x':'year','fleet_x':'fleet'}, inplace = True)
           
            finaldata2[['cargo_total','cargo_total_teu','HFO','LFO','MDO_MGO','totalco2_kgnm','totalco2','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','eeoi_teu','equivalent_hfo','cargo_transport_work','teu_transport_work','distance']].apply(pd.to_numeric)
            secondperiod=finaldata2[['vessel_name','imo','fleet','class','voyages','cargo_total','cargo_total_teu','HFO','LFO','MDO_MGO','totalco2_kgnm','totalco2','average_fuelcons','average_distance','average_permt','average_perteu','fuelkg_nm','eeoi_mt','eeoi_teu','equivalent_hfo','cargo_transport_work','teu_transport_work','distance']]
            secondperiod.rename(columns={'LFO':'LFO (MT)','HFO':'HFO (MT)','cargo_total':'Cargo Total (MT)','cargo_total_teu':'Cargo Total (TEU)','fuelkg_nm':'Fuel per Miles(Kg/NM)','equivalent_hfo':'Equivalent HFO (MT)','cargo_transport_work':'Cargo TranSport Work (MT-NM)','distance':'Distance (NM)','fleet':'Fleet','eeoi_teu':'EEOI (gm/TEU-NM)','voyages':'Number of Voyages','totalco2':'Total CO2 (MT)','MDO_MGO':'MGO (MT)','average_fuelcons':'Fuel Consumption per Voyage (MT)','totalco2_kgnm':'CO2 per Miles (MT/NM)','vessel_name':'Vessel Name','eeoi_mt':'EEOI (gm/MT-NM)','average_perteu':'Cargo per Voyage (TEU)','average_permt':'Cargo per Voyage (MT)','imo':'IMO','class':'Class','teu_transport_work':'Cargo Transport Work (TEU-NM)','average_distance':'Distance per Voyage (NM)'}, inplace = True)

            secondperiod=secondperiod.round(2)

            # secondperiod.rename(columns={'distance1_x':'distance1','distance2_x':'distance2','distance_x':'distance','mt_x':'mt','year_x':'year','fleet_x':'fleet'}, inplace = True)
            # firstperiod['TotalCo2_mt'] = pd.to_numeric(firstperiod['TotalCo2_mt'])
            secondperiod=secondperiod.to_json(orient="records")
            secondperiod = json.loads(secondperiod)
            # firstperiod = firstperiod.round(2)
            # firstperiod=firstperiod.to_json(orient="records")
            # firstperiod = json.loads(firstperiod)
            # firstperiod=firstperiod.to_json(orient="records")
            # firstperiod = json.loads(firstperiod)
        #  # finaldata1['vessel_name'] = finaldata1['name']
        # try:
        #     if not firstperiod.empty:
             
        #         firstperiod.rename(columns={'LFO':'LFO (MT)','HFO':'HFO (MT)','teucargo':'Teucargo','cargomt':'Cargo Total (MT)','cargoteu':'Cargo TEU','fuelkg_nm':'fuel (KgNm)','equivalent_hfo':'Equivalent HFO','mt_x':'Cargo Tranport Work (MT)','distance_x':'Distance (Nm)','year_x':'Year','fleet_x':'Fleet','eeoi_teu':'EEOI Teu','eeoi_voyage_no_x':'Voyage number','xcargo':'Cargo Total','TotalCo2_mt':'Total CO2 (MT)','MDO_MGO':'MGO (MT)','average_fuelcons':'Average fuel consumption','totalco2_kgnm':'Total CO2 (KgNM)','vessel_name':'Vessel Name','eeoi_mt':'EEOI (gm/MTNm)','mt':'MT','average_perteu':'Average Per TEU','average_permt':'Average Per MT','imo':'IMO','class':'Class'}, inplace = True)
        #         firstperiod=firstperiod.to_json(orient="records")
        #         firstperiod = json.loads(firstperiod)
        # except:
        #     print("Exeption1")
        #     pass
        # # try:
        # if not secondperiod.empty:  
        #     secondperiod.rename(columns={'LFO':'LFO (MT)','HFO':'HFO (MT)','teucargo':'Teucargo','cargomt':'Cargo Total (MT)','cargoteu':'Cargo TEU','fuelkg_nm':'fuel (KgNm)','equivalent_hfo':'Equivalent HFO','mt_x':'Cargo Tranport Work (MT)','distance_x':'Distance (Nm)','year_x':'Year','fleet_x':'Fleet','eeoi_teu':'EEOI Teu','eeoi_voyage_no_x':'Voyage number','xcargo':'Cargo Total','TotalCo2_mt':'Total CO2 (MT)','MDO_MGO':'MGO (MT)','average_fuelcons':'Average fuel consumption','totalco2_kgnm':'Total CO2 (KgNM)','vessel_name':'Vessel Name','eeoi_mt':'EEOI (gm/MTNm)','mt':'MT','average_perteu':'Average Per TEU','average_permt':'Average Per MT','imo':'IMO','class':'Class'}, inplace = True)

        #     secondperiod=secondperiod.to_json(orient="records")
        #     secondperiod = json.loads(secondperiod)
        # except:
            # print("Exeption2")
            
            # pass        

        df=df.to_json(orient="records")
        data = json.loads(df)
        # moving_average1=moving_average1.replace({np.inf:None})
        # moving_average2=moving_average2.replace({np.inf:None})
        
        # # #print(moving_average1)
        # moving_average1 = moving_average1.round(2)
        # moving_average1 = moving_average1.to_json(orient="records")
        # moving_average1 = json.loads(moving_average1)
        # moving_average2 = moving_average2.round(2)
        # moving_average2 = moving_average2.to_json(orient="records")
        # moving_average2 = json.loads(moving_average2)
        t2=datetime.now()
    
        result= {
            

            
            "year1":{
                "finaldata":finaldata_1,

            },
            "year2":
            {
                "finaldata":finaldata_2,

            },
            "table1":{
                "table1":table2
                },
            "classorfleetdata":data_list_2,
            "FirstPeriodData" : firstperiod,
            "SecondPeriodData" : secondperiod
                
                }
        try:
                
                if result is not None:
                    cache = False
                    final_data = json.dumps(jsonable_encoder(result))
                    
                    if cache_data == 1:
                        state = utility.set_data(key=CACHEKEY.PERIOD_COMPARISON+str(fleet)+str(year1)+str(year2)+str(first_Period_min)+str(first_Period_max)+str(second_Period_min)+str(second_Period_max)+str(classs)+str(imo), value= final_data)
                    else:
                        state = utility.set_data(key=CACHEKEY.PERIOD_COMPARISON+str(fleet)+str(year1)+str(year2)+str(classs)+str(imo)+str(moving_average)+str(type), value= final_data)
                    
                    
                
                    if state is True:
                            print('Cache Set Successfully') 

        except:
                
                print('cache set failure')

    try:
        final_data
    except:
        final_data = []


    data = json.loads(final_data)

    return data



    
    
@router.get('/api/v1/eeoi_mrv/period_comparison/{imo}')#, response_model=vessel_schema.Response
def index(db:Session = Depends(get_vdm_db),m_db= Depends(get_db),imo:str=None,year1:str=None,year2:str=None,moving_average:str=None,first_Period_min:str=None,first_Period_max:str=None,second_Period_min:str=None,second_Period_max:str=None,token : Session = Depends(get_token)):
    # vessel_attribute=cache_set.get_all_table_vessel_attribute(vessel_id,at_id,db)
    if year1 is None and year2 is None:
       first_Period_min 
       first_Period_max 
       second_Period_min
       second_Period_max
       
       
       first_Period_min = datetime.strptime(first_Period_min,"%Y-%m-%d")   
       year1 = first_Period_min.year
       
       second_Period_max = datetime.strptime(second_Period_max,"%Y-%m-%d")   
       year2 = second_Period_max.year
       
    vdm_vessel_data = cache_set.get_mcr_filter(db)
    vdm_vessel_data = list(filter(lambda x:x['imo'] == str(imo) , vdm_vessel_data))

   
    # try:

    #     classname = list(filter(lambda x:x['imo'] == str(imo) and x['attribute_id'] == 580 , vdm_vessel_data))[0]['value']
    # except:
    #     classname=None

    # try:
    #     fleet= float(list(filter(lambda x:x['imo'] ==  str(imo) and x['attribute_id'] == 515 , vdm_vessel_data))[0]['value'])

    # except:
    #     fleet=None
    # try:
    #     draft_scantling = float(list(filter(lambda x:x['imo'] ==  str(imo) and x['attribute_id'] == 20 , vdm_vessel_data))[0]['value'])
        
    # except:
    #     draft_scantling=None
    # try:
    #     max_speed = float(list(filter(lambda x:x['imo'] ==  str(imo) and x['attribute_id'] == 16 , vdm_vessel_data))[0]['value'])
        
    # except:
    #     max_speed=None
    # try:
    #     prtype = float(list(filter(lambda x:x['imo'] ==  str(imo) and x['attribute_id'] == 196 , vdm_vessel_data))[0]['value'])
        
    # except:
    #     prtype=None
    # try:
    #     propeller_pitchincludes_new= float(list(filter(lambda x:x['imo'] ==  str(imo) and x['attribute_id'] == 739 , vdm_vessel_data))[0]['value'])

    # except:
    #     propeller_pitchincludes_new=None
    # try:
    #     vesselname = float(list(filter(lambda x:x['imo'] ==  str(imo) and x['attribute_id'] == 61 , vdm_vessel_data))[0]['value'])
        
    # except:
    #     vesselname=None
    try:
        yob = float(list(filter(lambda x:x['attribute_id'] == 7 , vdm_vessel_data))[0]['value'])

    except:
        yob=None

    data=open('stub/vessel_attribute.json',encoding="utf8")
    data1 = json.load(data, strict=False)
    
    try:
        final = list(filter(lambda x:x['attribute_id'] == 823 , vdm_vessel_data))[0]['value']

    except:
        final=0
    try:
        eeoitype= float(list(filter(lambda x:x['attribute_id'] == 4 , vdm_vessel_data))[0]['value'])

    except:
        eeoitype=None
    data=open('stub/vessel_attribute.json',encoding="utf8")
    data1 = json.load(data, strict=False)
    
    try:
        final = list(filter(lambda x:x['imo'] == int(imo) and x['attribute_id'] == 823 , data1))[0]['value']
        #print(final)
    except:
        final=0.0
    if not final or final == '':
        final=0.0
        

        # eeoigoal['final']=list(filter(lambda x:x['attribute_id']==823 and x['imo']==int(imo),data1))[0]['value']
    
    #print("eeeeeeeeeeeeeeeeeee")
    #print(classname,final,year1,yob)
    # final=4.57
    try:
        eeoigoalmt1 = round(float(final) + (((float(year1) - float(yob))/100)*float(final)),2)
    except:
        eeoigoalmt1=0

# age_group = "Minor" if age < 18 else "Adult"
# --------------------------------------------------optimize-----------------------------------------------------------------------------------------
   
    if  eeoitype == '1.0' or eeoitype == '1':
      
        eeoigoalteu1 =(float(eeoigoalmt1)*14)  
    else:
        eeoigoalteu1 =None
    try:
        eeoigoalmt2 = round(float(final) + (((float(year2) - float(yob))/100)*float(final)),2)
    except:
        eeoigoalmt2=0
    #print("eeoigoalmt2eeoigoalmt2eeoigoalmt2eeoigoalmt2",eeoigoalmt2)
    if  eeoitype == 1.0 or eeoitype == 1 :
        eeoigoalteu2 =(float(eeoigoalmt2)*14)  
    else:
        eeoigoalteu2 =None
  
    
    #print(eeoigoalmt1,eeoigoalteu1,eeoigoalmt2,eeoigoalteu2)
    

    if first_Period_min and first_Period_max and second_Period_min and second_Period_max:
        data = utility.get_data(key=CACHEKEY.NOONDATADATA_HSTRC+str(imo)+str(first_Period_min)+str(first_Period_max)+str(second_Period_min)+str(second_Period_max))
        cache = False
        if data is not None:
            data = json.loads(data)
            cache = True
        else:
            # start_year = end_year = i
            #print(year1,year2)
            
            data = querydata.get_NoonDatas(m_db,imo,year1,year2,first_Period_min , first_Period_max , second_Period_min , second_Period_max)
            data = json.dumps(jsonable_encoder(data))
        
            # #print("data ::::::::" , data)

            try:
                if data is not None:
                    cache = False
                    state = utility.set_data(key=CACHEKEY.NOONDATADATA_HSTRC+str(imo)+str(first_Period_min)+str(first_Period_max)+str(second_Period_min)+str(second_Period_max), value=data)
                    if state is True:
                        print('Cache Set Successfully') 
            except:
                print('cache set failure')
            data = json.loads(data)
    else:
        data = utility.get_data(key=CACHEKEY.NOONDATADATA_HSTRC+str(imo)+str(year1)+str(year2))
        cache = False
        if data is not None:
            data = json.loads(data)
            cache = True
        else:
            # start_year = end_year = i
            #print(year1,year2)
                
            data = querydata.get_NoonDatas(m_db,imo,year1,year2,first_Period_min =None , first_Period_max=None, second_Period_min=None , second_Period_max=None)
            data = json.dumps(jsonable_encoder(data))
        
            # #print("data ::::::::" , data)

            try:
                if data is not None:
                    cache = False
                    state = utility.set_data(key=CACHEKEY.NOONDATADATA_HSTRC+str(imo)+str(year1)+str(year2), value=data)
                    if state is True:
                        print('Cache Set Successfully') 
            except:
                print('cache set failure')
            data = json.loads(data)
        
    # return data
    # a.extend(data)
        # data = a
        # return data
    if not data:
        return {"data": []}
    df=pd.DataFrame(data)
   
        # eeoidata = pd.DataFrame()
        # eeoidata['imo'] = 0,
        # df1,year1,eeoitype,eeoimt2,eeoiteu2,type,moving_average
    finaldata1,moving_average1=get_yearanalysis(df,year1,eeoitype,eeoigoalmt1,eeoigoalteu1,eeoitype,moving_average)
    finaldata2,moving_average2=get_yearanalysis(df,year2,eeoitype,eeoigoalmt2,eeoigoalteu2,eeoitype,moving_average)
    finaldata1=finaldata1.round(2)
    finaldata2=finaldata2.round(2)
    moving_average1=moving_average1.round(2)
    moving_average2=moving_average2.round(2)
    
    # if finaldata2.empty==True or  moving_average2.empty==True :
    #     return {'data':[]}
    #print("***************************************************")
    #print(finaldata1)
    #print(finaldata2)
    #print("***************************************************")
    if finaldata1.empty==False and finaldata2.empty==False:
        table1=pd.merge(finaldata1,finaldata2, left_index=True, right_index=True, how='outer')
        voyages=[float(table1['voyages_x'][0]),float(table1['voyages_y'][0])]
        eeoi_mt=[table1['eeoi_mt_x'][0],table1['eeoi_mt_y'][0]]
        eeoi_teu=[table1['eeoi_teu_x'][0],table1['eeoi_teu_y'][0]]
        totalco2_mt=[table1['totalco2_mt_x'][0],table1['totalco2_mt_y'][0]]
        # totalco2_kgnm=[table1['totalco2_kgnm_x'][0],table1['totalco2_kgnm_y'][0]]
        
        totalco2_kgnm=[table1['totalco2_kgnm_x'][0],table1['totalco2_kgnm_y'][0]]
        cargomt=[table1['cargomt_x'][0],table1['cargomt_y'][0]]
        cargoteu=[table1['cargoteu_x'][0],table1['cargoteu_y'][0]]
        equivalent_hfo=[table1['equivalent_hfo_x'][0],table1['equivalent_hfo_y'][0]]
        hfo=[table1['hfo_x'][0],table1['hfo_y'][0]]
        lfo=[table1['lfo_x'][0],table1['lfo_y'][0]]
        mdo_mgo=[table1['mdo_mgo_x'][0],table1['mdo_mgo_y'][0]]
        equivalent_hfo=[table1['equivalent_hfo_x'][0],table1['equivalent_hfo_y'][0]]
        distance=[table1['distance_x'][0],table1['distance_y'][0]]
        average_perteu=[table1['average_perteu_x'][0],table1['average_perteu_y'][0]]
        average_permt=[table1['average_permt_x'][0],table1['average_permt_y'][0]]
        year=[table1['year_x'][0],table1['year_y'][0]]
        average_distance=[table1['average_distance_x'][0],table1['average_distance_y'][0]]
        average_fuelcons=[table1['average_fuelcons_x'][0],table1['average_fuelcons_y'][0]]

        try:
            average_distance.append(round((average_distance[1]-average_distance[0])*100/average_distance[0],0))
        except:
            average_distance.append('0.0')
        # eeoi_mt=[table1['eeoi_mt_x'][0],table1['eeoi_mt_y'][0]]
        # equip_nm=[table1['equip_nm_x'][0],table1['equip_nm_y'][0]]
        # distance=[table1['distance_x'][0],table1['distance_y'][0]]
        try:
            average_perteu.append(round((average_perteu[1]-average_perteu[0])*100/average_perteu[0],0))
        except:
            average_perteu.append('0.0')
        try:
            average_permt.append(round((average_permt[1]-average_permt[0])*100/average_permt[0],0))
        except:
            average_permt.append('0.0')
        try:
            lfo.append(round((lfo[0]-lfo[1])*100/lfo[0],0))
        except:
            lfo.append('0.0')
        try:
            mdo_mgo.append(round((mdo_mgo[0]-mdo_mgo[1])*100/mdo_mgo[0],0))
        except:
            mdo_mgo.append('0.0')
        try:
            distance.append(round((distance[1]-distance[0])*100/distance[0],0))
        except:
            distance.append('0.0')
        try:
            hfo.append(round((hfo[0]-hfo[1])*100/hfo[0],0))
        except:
            hfo.append('0.0')
        try:
            equivalent_hfo.append(round((equivalent_hfo[0]-equivalent_hfo[1])*100/equivalent_hfo[0],0))
        except:
            equivalent_hfo.append('0.0')
        try:
            cargomt.append(round((cargomt[1]-cargomt[0])*100/cargomt[0],0))
        except:
            cargomt.append('0.0')
        try:
            cargoteu.append(round((cargoteu[1]-cargoteu[0])*100/cargoteu[0],0))
        except:
            cargoteu.append('0.0')
        try:
            totalco2_kgnm.append(round((totalco2_kgnm[0]-totalco2_kgnm[1])*100/totalco2_kgnm[0],0))
        except:
            totalco2_kgnm.append('0.0')
        try:
            totalco2_mt.append(round((totalco2_mt[0]-totalco2_mt[1])*100/totalco2_mt[0],0))
        except:
            totalco2_mt.append('0.0')
        try:
            voyages.append(round((voyages[1]-voyages[0])*100/voyages[0],0))
        except:
            voyages.append('0.0')
        try:
            eeoi_mt.append(round((eeoi_mt[0]-eeoi_mt[1])*100/eeoi_mt[0],0))
        except:
            eeoi_mt.append('0.0')
        try:
            eeoi_teu.append(round((eeoi_teu[0]-eeoi_teu[1])*100/eeoi_teu[0],0))
        except:
            eeoi_teu.append('0.0')
        try:
            year.append(round((year[1]-year[0])*100/year[0],0))
        except:
            year.append('0.0')
        try:
            average_fuelcons.append(round((average_fuelcons[1]-average_fuelcons[0])*100/average_fuelcons[0],0))
        except:
            average_fuelcons.append('0.0')
        new1=pd.DataFrame(data=[cargoteu,cargomt,totalco2_mt,totalco2_kgnm,eeoi_teu,eeoi_mt,equivalent_hfo,distance,hfo,lfo,mdo_mgo,voyages,average_perteu,average_permt,average_distance,average_fuelcons],index=["Cargo [TEU]",
        "Cargo[MT]",
        "CO2[MT]"    ,
        "CO2[MT/NM]",
        "EEOI for Cargo [TEU]",
        "EEOI for Cargo [MT]",
        "Total equiv. HFO [Kilo MT]",
        # "EEOI goal [MT]",
        # "EEOI goal [TEU]"    ,
        "TotalDistance",
        "HFO",
        "LFO"    ,
        "MDO_MGO",
        # "Total equiv.    HFO [MT]"    ,
        "Voyages",
        "Avg. [TEU] Per Voyage"    ,
        "Avg. [MT] Per Voyage"    ,
        "Avg. Distance Per Voyage",
        "Avg. Consumption Per Voyage"])
        col=['year1','year2','improvement']
    
        new1=new1.round(2)
        #print(new1)
        new1.columns=np.array(col)
        new1['index']=new1.index
       
       
        new1 = new1.to_json(orient="records")
        table2 = json.loads(new1)
        finaldata1 = finaldata1.to_json(orient="records")
        finaldata1 = json.loads(finaldata1)
        finaldata2 = finaldata2.to_json(orient="records")
        finaldata2 = json.loads(finaldata2)
        df=df.to_json(orient="records")
        data = json.loads(df)

        # #print(moving_average1)
        moving_average1 = moving_average1.to_json(orient="records")
        moving_average1 = json.loads(moving_average1)
        moving_average2 = moving_average2.to_json(orient="records")
        moving_average2 = json.loads(moving_average2)
        return {
            

            
            "year1":{
                "finaldata":finaldata1,
                "moving data average":moving_average1

            },
            "year2":
            {
                "finaldata":finaldata2,
                "moving data average":moving_average2

            },
            "table1":{
                "table1":table2
                }

        }
    else:
        #print("rrrr")
        if finaldata1.empty==False and finaldata2.empty:
            voyages=[float(finaldata1['voyages'][0]),0]
            eeoi_mt=[finaldata1['eeoi_mt'][0],0]
            eeoi_teu=[finaldata1['eeoi_teu'][0],0]
            totalco2_mt=[finaldata1['totalco2_mt'][0],0]
            totalco2_mt=[finaldata1['totalco2_mt'][0],0]
            distance=[finaldata1['distance'][0],0]
            
            totalco2_kgnm=[finaldata1['totalco2_kgnm'][0],0]
            cargomt=[finaldata1['cargomt'][0],0]
            cargoteu=[finaldata1['cargoteu'][0],0]
            equivalent_hfo=[finaldata1['equivalent_hfo'][0],0]
            hfo=[finaldata1['hfo'][0],0]
            lfo=[finaldata1['lfo'][0],0]
            mdo_mgo=[finaldata1['mdo_mgo'][0],0]
            equivalent_hfo=[finaldata1['equivalent_hfo'][0],0]
            
            average_perteu=[finaldata1['average_perteu'][0],0]
            average_permt=[finaldata1['average_permt'][0],0]
            year=[finaldata1['year'][0],0]
            average_distance=[finaldata1['average_distance'][0],0]
            average_fuelcons=[finaldata1['average_fuelcons'][0],0]

            try:
                average_distance.append(round((average_distance[1]-average_distance[0])*100/average_distance[0],0))
            except:
                average_distance.append('0.0')
            # eeoi_mt=[table1['eeoi_mt_x'][0],table1['eeoi_mt_y'][0]]
            # equip_nm=[table1['equip_nm_x'][0],table1['equip_nm_y'][0]]
            # distance=[table1['distance_x'][0],table1['distance_y'][0]]
            try:
                average_perteu.append(round((average_perteu[1]-average_perteu[0])*100/average_perteu[0],0))
            except:
                average_perteu.append('0.0')
            try:
                average_permt.append(round((average_permt[1]-average_permt[0])*100/average_permt[0],0))
            except:
                average_permt.append('0.0')
            try:
                lfo.append(round((lfo[1]-lfo[0])*100/lfo[0],0))
            except:
                lfo.append('0.0')
            try:
                mdo_mgo.append(round((mdo_mgo[1]-mdo_mgo[0])*100/mdo_mgo[0],0))
            except:
                mdo_mgo.append('0.0')
            try:
                hfo.append(round((hfo[1]-hfo[0])*100/hfo[0],0))
            except:
                hfo.append('0.0')
            try:
                equivalent_hfo.append(round((equivalent_hfo[1]-equivalent_hfo[0])*100/equivalent_hfo[0],0))
            except:
                equivalent_hfo.append('0.0')
            try:
                cargomt.append(round((cargomt[1]-cargomt[0])*100/cargomt[0],0))
            except:
                cargomt.append('0.0')
            try:
                cargoteu.append(round((cargoteu[1]-cargoteu[0])*100/cargoteu[0],0))
            except:
                cargoteu.append('0.0')
            try:
                totalco2_kgnm.append(round((totalco2_kgnm[1]-totalco2_kgnm[0])*100/totalco2_kgnm[0],0))
            except:
                totalco2_kgnm.append('0.0')
            try:
                totalco2_mt.append(round((totalco2_mt[1]-totalco2_mt[0])*100/totalco2_mt[0],0))
            except:
                totalco2_mt.append('0.0')
            try:
                voyages.append(round((voyages[1]-voyages[0])*100/voyages[0],0))
            except:
                voyages.append('0.0')
            try:
                eeoi_mt.append(round((eeoi_mt[1]-eeoi_mt[0])*100/eeoi_mt[0],0))
            except:
                eeoi_mt.append('0.0')
            try:
                eeoi_teu.append(round((eeoi_teu[1]-eeoi_teu[0])*100/eeoi_teu[0],0))
            except:
                eeoi_teu.append('0.0')
            try:
                year.append(round((year[1]-year[0])*100/year[0],0))
            except:
                year.append('0.0')
            try:
                average_fuelcons.append(round((average_fuelcons[1]-average_fuelcons[0])*100/average_fuelcons[0],0))
            except:
                average_fuelcons.append('0.0')
            try:
                distance.append(round((distance[1]-distance[0])*100/distance[0],0))
            except:
                distance.append('0.0')
            new1=pd.DataFrame(data=[cargoteu,cargomt,totalco2_mt,totalco2_kgnm,eeoi_teu,eeoi_mt,equivalent_hfo,distance,hfo,lfo,mdo_mgo,voyages,average_perteu,average_permt,average_distance,average_fuelcons],index=["Cargo [TEU]",
            "Cargo[MT]",
            "CO2[MT]"    ,
            "CO2[MT/NM]",
            "EEOI for Cargo [TEU]",
            "EEOI for Cargo [MT]",
            "Total equiv. HFO [Kilo MT]",
            # "EEOI goal [MT]",
            # "EEOI goal [TEU]"    ,
            "TotalDistance",
            "HFO",
            "LFO"    ,
            "MDO_MGO",
           
            "Voyages",
            "Avg. [TEU] Per Voyage"    ,
            "Avg. [MT] Per Voyage"    ,
            "Avg. Distance Per Voyage",
            "Avg. Consumption Per Voyage"])
            col=['year1','year2','improvement']
        
            new1=new1.round(2)
            #print(new1)
            new1.columns=np.array(col)
            new1['index']=new1.index
            
        
            finaldata1 = finaldata1.to_json(orient="records")
            finaldata1 = json.loads(finaldata1)
            moving_average1 = moving_average1.to_json(orient="records")
            moving_average1 = json.loads(moving_average1)
            new1 = new1.to_json(orient="records")
            table1 = json.loads(new1)
            return {
            

            
            "year1":{
                "finaldata":finaldata1,
                "moving data average":moving_average1

            },
            "year2":
            {
                "finaldata":[],
                "moving data average":[]

            },
            "table1":{
                "table1":table1
                }

        }
        elif finaldata2.empty==False and finaldata1.empty:
            voyages=[0,float(finaldata2['voyages'][0])]
            eeoi_mt=[0,finaldata2['eeoi_mt'][0]]
            eeoi_teu=[0,finaldata2['eeoi_teu'][0]]
            totalco2_mt=[0,finaldata2['totalco2_mt'][0]]
            totalco2_mt=[0,finaldata2['totalco2_mt'][0]]
            distance=[0,finaldata2['distance'][0]]
            totalco2_kgnm=[0,finaldata2['totalco2_kgnm'][0]]
            cargomt=[0,finaldata2['cargomt'][0]]
            cargoteu=[0,finaldata2['cargoteu'][0]]
            equivalent_hfo=[0,finaldata2['equivalent_hfo'][0]]
            hfo=[0,finaldata2['hfo'][0]]
            lfo=[0,finaldata2['lfo'][0]]
            mdo_mgo=[0,finaldata2['mdo_mgo'][0]]
            equivalent_hfo=[0,finaldata2['equivalent_hfo'][0]]
            average_perteu=[0,finaldata2['average_perteu'][0]]
            average_permt=[0,finaldata2['average_permt'][0]]
            year=[0,finaldata2['year'][0]]
            average_distance=[0,finaldata2['average_distance'][0]]
            average_fuelcons=[0,finaldata2['average_fuelcons'][0]]

            try:
                average_distance.append(round((average_distance[1]-average_distance[0])*100/average_distance[0],0))
            except:
                average_distance.append('0.0')
           
            try:
                average_perteu.append(round((average_perteu[1]-average_perteu[0])*100/average_perteu[0],0))
            except:
                average_perteu.append('0.0')
            try:
                average_permt.append(round((average_permt[1]-average_permt[0])*100/average_permt[0],0))
            except:
                average_permt.append('0.0')
            try:
                lfo.append(round((lfo[1]-lfo[0])*100/lfo[0],0))
            except:
                lfo.append('0.0')
            try:
                mdo_mgo.append(round((mdo_mgo[1]-mdo_mgo[0])*100/mdo_mgo[0],0))
            except:
                mdo_mgo.append('0.0')
            try:
                hfo.append(round((hfo[1]-hfo[0])*100/hfo[0],0))
            except:
                hfo.append('0.0')
            try:
                equivalent_hfo.append(round((equivalent_hfo[1]-equivalent_hfo[0])*100/equivalent_hfo[0],0))
            except:
                equivalent_hfo.append('0.0')
            try:
                cargomt.append(round((cargomt[1]-cargomt[0])*100/cargomt[0],0))
            except:
                cargomt.append('0.0')
            try:
                cargoteu.append(round((cargoteu[1]-cargoteu[0])*100/cargoteu[0],0))
            except:
                cargoteu.append('0.0')
            try:
                totalco2_kgnm.append(round((totalco2_kgnm[1]-totalco2_kgnm[0])*100/totalco2_kgnm[0],0))
            except:
                totalco2_kgnm.append('0.0')
            try:
                totalco2_mt.append(round((totalco2_mt[1]-totalco2_mt[0])*100/totalco2_mt[0],0))
            except:
                totalco2_mt.append('0.0')
            try:
                voyages.append(round((voyages[1]-voyages[0])*100/voyages[0],0))
            except:
                voyages.append('0.0')
            try:
                eeoi_mt.append(round((eeoi_mt[1]-eeoi_mt[0])*100/eeoi_mt[0],0))
            except:
                eeoi_mt.append('0.0')
            try:
                eeoi_teu.append(round((eeoi_teu[1]-eeoi_teu[0])*100/eeoi_teu[0],0))
            except:
                eeoi_teu.append('0.0')
            try:
                year.append(round((year[1]-year[0])*100/year[0],0))
            except:
                year.append('0.0')
            try:
                average_fuelcons.append(round((average_fuelcons[1]-average_fuelcons[0])*100/average_fuelcons[0],0))
            except:
                average_fuelcons.append('0.0')
            new1=pd.DataFrame(data=[cargoteu,cargomt,totalco2_mt,totalco2_kgnm,eeoi_teu,eeoi_mt,equivalent_hfo,distance,hfo,lfo,mdo_mgo,voyages,average_perteu,average_permt,average_distance,average_fuelcons],index=["Cargo [TEU]",
            "Cargo[MT]",
            "CO2[MT]"    ,
            "CO2[MT/NM]",
            "EEOI for Cargo [TEU]",
            "EEOI for Cargo [MT]",
            "Total equiv. HFO [Kilo MT]",
            # "EEOI goal [MT]",
            # "EEOI goal [TEU]"    ,
            "TotalDistance",
            "HFO",
            "LFO"    ,
            "MDO_MGO",
            # "Total equiv.HFO [MT]"    ,
            "Voyages",
            "Avg. [TEU] Per Voyage"    ,
            "Avg. [MT] Per Voyage"    ,
            "Avg. Distance Per Voyage",
            "Avg. Consumption Per Voyage"])
            col=['year1','year2','improvement']
        
            new1=new1.round(2)
            new1.columns=np.array(col)
            new1['index']=new1.index
            
        
            finaldata1 = finaldata1.to_json(orient="records")
            finaldata1 = json.loads(finaldata1)
            moving_average1 = moving_average1.to_json(orient="records")
            moving_average1 = json.loads(moving_average1)
            new1 = new1.to_json(orient="records")
            table1 = json.loads(new1)
            return {
            

            
            "year1":{
               "finaldata":[],
                "moving data average":[]

            },
            "year2":
            {
                 "finaldata":finaldata1,
                "moving data average":moving_average1
                

            },
            "table1":{
                "table1":table1
                }

        }
            
        




   




























            
        




   
