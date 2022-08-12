from santiago_core import SANTIAGO_CORE
from teams_core import TEAMS_CORE

sant = SANTIAGO_CORE()
teams = TEAMS_CORE() 

alertas = sant.alertas()
res, ld_str = sant.get_df_teams()
dwt, dst, dct = teams.get_data_nc()

for tienda, row in res.iterrows():
    monto = f'$ {row["Costo_NC-Empleado"]/1e6:,.1f} M'
    cantidad = str(row['Cautoriza'])
    sant.guardar_res_tienda(alertas[0], alertas[1], alertas[2], alertas[3], tienda)
    teams.send_msg(tienda, dwt[tienda], dst[tienda], dct[tienda], cantidad, monto, ld_str)

qty = str(res.Cautoriza.sum())
monto = f'$ {round(res["Costo_NC-Empleado"].sum()/1e6)} M'
teams.send_msg_general(dwt['GENERAL'], qty, monto, ld_str)