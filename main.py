from santiago_core import SANTIAGO_CORE
from teams_core import TEAMS_CORE

sant = SANTIAGO_CORE()
teams = TEAMS_CORE() 
alertas = sant.alertas()
res, ld_str = sant.get_df_teams()
dwt, dst, dct = teams.get_data_nc()

for tienda, row in res.iterrows():
        cantidad_nc = f'{row["Cautoriza_nc"]:,.0f}'
        monto_nc = f'$ {row["Costo_NC-Empleado_nc"]/1e6:,.1f} M'
        cantidad_cm = f'{row["Cautoriza_cm"]:,.0f}'
        monto_cm = f'$ {row["Costo_NC-Empleado_cm"]/1e6:,.1f} M'
        teams.send_msg(tienda, dwt[tienda],dst[tienda], dct[tienda], cantidad_nc, monto_nc, ld_str, cantidad_cm, monto_cm)
        sant.guardar_res_tienda(alertas[0], alertas[1], alertas[2], alertas[3], tienda)

cm = res.loc[res.Cautoriza_cm > 0].index
cm_cant = f'{res["Cautoriza_cm"].sum():,.0f}'
cm_mont = f'$ {res["Costo_NC-Empleado_cm"].sum()/1e6:,.1f} M'
if cm.shape[0] > 0:
    listado = '<ul>'
    for i in cm.values.tolist():
        listado += f'<li>{i}</li>'
    listado += '</ul>'
else:
    listado = []

teams.send_msg_cm(dwt['CODIGO_MAESTRO'], dst['CODIGO_MAESTRO'], cm_cant, cm_mont, ld_str, listado)
sant.save_res_cod_m()

qty = str(res['Cautoriza_nc'].sum())
monto = f'$ {round(res["Costo_NC-Empleado_nc"].sum()/1e6)} M'
teams.send_msg_general(dwt['GENERAL'], qty, monto, ld_str)