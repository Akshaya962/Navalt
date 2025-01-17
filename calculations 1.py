from dbhandler.dbhandler import executeQ

def calculations():
	q = "UPDATE NOONDATA2 SET EEOI_Voyage_no = if(Report_Type = \"SAIL\", Voyage_Order-1, Voyage_Order) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("EEOI_Voyage_no")

	q = "UPDATE NOONDATA2 SET FUEL_HS = (FUEL_M_E_HS + FUEL_AUX_HS + FUEL_BOILER_HS) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("FUEL_HS")

	q = "UPDATE NOONDATA2 SET FUEL_LS = (FUEL_M_E_LS + FUEL_AUX_LS + FUEL_BOILER_LS) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("FUEL_LS")

	q = "UPDATE NOONDATA2 SET FUEL_MDO = (FUEL_M_E_MDO + FUEL_AUX_MDO + FUEL_BOILER_MDO) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("FUEL_MDO")

	q = "UPDATE NOONDATA2 SET FUEL_MGO = (FUEL_M_E_MGO + FUEL_AUX_MGO + FUEL_BOILER_MGO) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("FUEL_MGO")

	q = "UPDATE NOONDATA2 SET FUEL_MGO_LS = (FUEL_M_E_MGO_LS + FUEL_AUX_MGO_LS + FUEL_BOILER_MGO_LS) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("FUEL_MGO_LS")

	q = "UPDATE NOONDATA2 SET Cargo_Transport_Work = ((MILES_BY_GPS + MANVRNG_MILES_BY_GPS) * CARGO_TOTAL) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("Cargo_Transport_Work")

	q = "UPDATE NOONDATA2 SET TEU_Transport_Work = ((MILES_BY_GPS + MANVRNG_MILES_BY_GPS) * (TEU_FULL + TEU_EMPTY)) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("TEU_Transport_Work")

	#Draft
	q = "UPDATE NOONDATA2 SET DRAFT = (DRAFT_AFT + DRAFT_FWD) / 2  WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("Draft")

	#FO
	q = "UPDATE NOONDATA2 SET FO_per_24Hrs = ((FUEL_M_E_LS + FUEL_M_E_HS + FUEL_M_E_MDO + FUEL_M_E_MGO + FUEL_M_E_MGO_LS)/(STEAMING_TIME_M_E_LS + STEAMING_TIME_M_E_HS + STEAMING_TIME_M_E_MDO + STEAMING_TIME_M_E_MGO + STEAMING_TIME_M_E_MGO_LS)) * 24 WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("FO_per_24Hrs")

	#SFOC
	q = "UPDATE NOONDATA2 SET NOONDATA2.SFOC = (NOONDATA2.FO_per_24Hrs * 1000000) / (NOONDATA2.POWER_KW * 24) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("SFOC")

	#CY OIL
	q = "UPDATE NOONDATA2 SET NOONDATA2.CY_OIL_gm_hr = (NOONDATA2.OIL_CYL * 900) / (STEAMING_TIME_M_E_LS + STEAMING_TIME_M_E_HS + STEAMING_TIME_M_E_MDO + STEAMING_TIME_M_E_MGO + STEAMING_TIME_M_E_MGO_LS) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("CY_OIL_gm_hr")

	#SCOC
	q = "UPDATE NOONDATA2 SET NOONDATA2.SCOC = (NOONDATA2.CY_OIL_gm_hr/ NOONDATA2.POWER_KW) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("SCOC")

	#Total FO
	q = "UPDATE NOONDATA2 SET NOONDATA2.TOTAL_FO = (NOONDATA2.FUEL_HS  + NOONDATA2.FUEL_LS + NOONDATA2.FUEL_MDO + NOONDATA2.FUEL_MGO + NOONDATA2.FUEL_MGO_LS)  WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("TOTAL_FO")

	#Total CO2
	q = "UPDATE NOONDATA2 SET NOONDATA2.TOTAL_CO2 = (((NOONDATA2.FUEL_HS + NOONDATA2.FUEL_LS)*3.114) + ((NOONDATA2.FUEL_MDO + NOONDATA2.FUEL_MGO + NOONDATA2.FUEL_MGO_LS) * 3.206)) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("TOTAL_CO2")

	#Sea Time
	q = "UPDATE NOONDATA2 SET NOONDATA2.Sea_Time = (NOONDATA2.STEAMING_TIME_M_E_HS + NOONDATA2.STEAMING_TIME_M_E_LS + NOONDATA2.STEAMING_TIME_M_E_MDO + NOONDATA2.STEAMING_TIME_M_E_MGO + NOONDATA2.STEAMING_TIME_M_E_MGO_LS) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("Sea_Time")

	q = "UPDATE NOONDATA2 SET MEcon= round(FUEL_M_E_HS + FUEL_M_E_LS +  FUEL_M_E_MDO + FUEL_M_E_MGO +  FUEL_M_E_MGO_LS,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("MEcon")
	q = "UPDATE NOONDATA2 SET AEcon= round(FUEL_AUX_HS + FUEL_AUX_LS +  FUEL_AUX_MDO + FUEL_AUX_MGO +  FUEL_AUX_MGO_LS,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("AEcon")
	q = "UPDATE NOONDATA2 SET BLcon= round(FUEL_BOILER_HS + FUEL_BOILER_LS +  FUEL_BOILER_MDO + FUEL_BOILER_MGO +  FUEL_BOILER_MGO_LS,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("BLcon")
	q = "UPDATE NOONDATA2 SET Tcon= round(MEcon + AEcon + BLcon,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("Tcon")
	q = "UPDATE NOONDATA2 SET HS= round(FUEL_M_E_HS + FUEL_AUX_HS +  FUEL_BOILER_HS,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("HS")
	q = "UPDATE NOONDATA2 SET LS= round(FUEL_M_E_LS + FUEL_AUX_LS +  FUEL_BOILER_LS,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("LS")
	q = "UPDATE NOONDATA2 SET MDO= round(FUEL_M_E_MDO + FUEL_AUX_MDO +  FUEL_BOILER_MDO,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("MDO")
	q = "UPDATE NOONDATA2 SET MGO= round(FUEL_M_E_MGO + FUEL_AUX_MGO +  FUEL_BOILER_MGO,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("MGO")
	q = "UPDATE NOONDATA2 SET MGOLS= round(FUEL_M_E_MGO_LS + FUEL_BOILER_MGO_LS +  FUEL_AUX_MGO_LS,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("MGOLS")

	q = "UPDATE NOONDATA2 SET TCO2= round(((HS + LS) * 3.114) + ((MDO + MGO + MGOLS) * 3.206),2)WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("TCO2")

	q = "UPDATE NOONDATA2 SET AETsteaming= round(STEAMING_TIME_AUX_1 + STEAMING_TIME_AUX_2 +  STEAMING_TIME_AUX_3 + STEAMING_TIME_AUX_4 +  STEAMING_TIME_AUX_5,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("AETsteaming")
	q = "UPDATE NOONDATA2 SET AEPOWER= round(STEAMING_LOAD_KW_AUX_1 + STEAMING_LOAD_KW_AUX_2 +  STEAMING_LOAD_KW_AUX_3 + STEAMING_LOAD_KW_AUX_4 +  STEAMING_LOAD_KW_AUX_5,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("AEPOWER")
	q = "UPDATE NOONDATA2 SET NOONDATA2.TRIM= round(NOONDATA2.DRAFT_AFT - NOONDATA2.DRAFT_FWD,2) WHERE NOONDATA2.idvessel = 'MUMB'"
	executeQ(q)
	setlog("TRIM")
	q = "UPDATE NOONDATA2 SET DISTANCECOVERED= round(MILES_BY_GPS + MANVRNG_MILES_BY_GPS,2) WHERE idvessel = 'MUMB'"
	executeQ(q)
	setlog("DISTANCECOVERED")
	
def setlog(msg):
	with open('log.txt', 'a') as the_file:
			print(msg)
			the_file.write(msg)

calculations()
