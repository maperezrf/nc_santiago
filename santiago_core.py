from datetime import datetime
from textwrap import indent
import pandas as pd 
import numpy as np 
import io
from datetime import timedelta, date, datetime
from os import listdir
from os.path import isfile, join
import constants as const

class SANTIAGO_CORE():
    nc_df =pd.DataFrame()
    dt_string = datetime.now().strftime('%y%m%d')
    with open('config\path.txt', "r") as tf:
        path = tf.read()
        path = path.replace("\\","/")
    tf.close()
    initial_date = pd.to_datetime(date.today() - timedelta(days=30))
    last_date = None #  = nc.Dcompra_nvo.max()
    df_teams = pd.DataFrame()
   
    def __init__(self) -> None:
        self.unir_ncs()
        self.load_files()
        self.change_format()
        self.change_format_date()
        self.set_filter()
        self.last_date = self.nc_df.Dcompra_nvo.max()
        

    def unir_ncs(self):
       print('Uniendo nc\'s...')
       path = 'input/archivo_ncs/'
       files_names = [f for f in listdir(path) if isfile(join(path, f))]
       files_store = []
       for i in files_names: 
              file = open(f'input/archivo_ncs/{i}', 'r', encoding='ISO-8859-1')
              nc_lines = file.readlines()
              file.close()
              files_store.append(pd.read_csv(io.StringIO("\n".join(nc_lines)), sep=';', dtype='object', on_bad_lines='skip'))
       self.nc_df = pd.concat(files_store)
       self.save_consolidado()
    
    def save_consolidado(self):
        print('Guardadndo nc\'s...')
        self.nc_df.to_csv('input/consolidado_nc.csv', index=False)

    def load_files(self):
        print('Cargando Archivos...')
        self.ep = pd.read_excel('input/211020_empleados_planta.xlsx', dtype=str) 
        self.ep['nombre_completo'] = self.ep['Apell_Paterno'] + ' ' +  self.ep['Apell_Materno'] + ' ' + self.ep['Nombre']  
        self.ep = self.ep[const.cols_emp_planta]
        self.et = pd.read_excel('input/211020_empleados_temporales.xlsx', dtype=str ,usecols= const.cols_emp_temp)
        self.et.rename(columns={'SUCURSAL':'Sucursal', 'APELLIDOS Y NOMBRES':'nombre_completo', 'DOCUMENTO':'Num_Documento', 'FECHA INGRESO':'FecInicioContrato', 'CARGO':'Cargo', 'TDA_AREA':'Departamento'}, inplace=True)
        self.nc_df = self.nc_df[const.cols_consolidado_ventas]
        self.nc_df.rename(columns={'Mventa_nc':'Costo_NC-Empleado'}, inplace=True)
        self.df_v = pd.read_excel('input/consolidado_ventas_21.xlsx', dtype=str) # Ventas
        self.df_v = self.df_v.loc[~self.df_v.Local.isin(const.local_excluir_ventas)]
        self.df_v.rename(columns={'Número de Vendedor (Cod.)':'Cod_Empleado', 'Local':'Desc_local', 'Venta en $':'Costo_Venta-Empleado' }, inplace=True)

    def change_format(self):
        print('Cambiando formato numeros...')
        self.nc_df.Qcantidad = pd.to_numeric(self.nc_df.Qcantidad)
        self.nc_df.Cvendedor = pd.to_numeric(self.nc_df.Cvendedor)
        self.nc_df["Costo_NC-Empleado"]= -pd.to_numeric(self.nc_df["Costo_NC-Empleado"])
        self.nc_df.Hora = pd.to_numeric(self.nc_df.Hora)
        self.ep.Cod_Empleado  = pd.to_numeric(self.ep.Cod_Empleado)
        self.df_v['Cod_Empleado'] = pd.to_numeric(self.df_v['Cod_Empleado'])
        self.df_v['Costo_Venta-Empleado'] = pd.to_numeric(self.df_v['Costo_Venta-Empleado'])
    
    def change_format_date(self):
        print('Cambiando formato fechas...')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('ene', '01')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('feb', '02')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('mar', '03')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('abr', '04')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('may', '05')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('jun', '06')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('jul', '07')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('ago', '08')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('sep', '09')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('oct', '10')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('nov', '11')
        self.nc_df.Dcompra_nvo = self.nc_df.Dcompra_nvo.str.replace('dic', '12')
        self.nc_df.Dcompra_nvo = pd.to_datetime(self.nc_df.Dcompra_nvo, format='%d-%m-%Y') # TODO arreglar para español 
        self.df_v['Día'] = pd.to_datetime(self.df_v['Día'], format='%Y/%m/%d')
    
    def set_filter(self): #TODO revisar orden en el que se llama el metodo
        print('Generando filtros...')
        self.nc_df = self.nc_df.loc[self.nc_df['Tipo_trx']=='NC'] # Transaction type 
        self.nc_df = self.nc_df.loc[~self.nc_df.Local_creacion.isin(const.local_excluir)] # Local number 
        self.nc_df.loc[self.nc_df['Desc_local']=='MARTINA COLINA', 'Desc_local'] = 'COLINA'
        self.nc_df.loc[self.nc_df['Desc_local']=='MARTINA FONTANAR', 'Desc_local'] = 'FONTANAR'
        self.nc_df.loc[self.nc_df['Desc_local']=='EXPO HAYUELOS', 'Desc_local'] = 'HAYUELOS'
        # self.df_teams = self.nc_df.copy() 

    def get_df_teams(self):
        last_date= self.nc_df.Dcompra_nvo.max()
        df_ld = self.nc_df[self.nc_df.Dcompra_nvo == last_date]
        ld_str = last_date.strftime('%d-%b-%y')
        df_nc = df_ld.loc[df_ld['Cautoriza'] != '10009'].reset_index(drop=True)
        df_cm = df_ld.loc[df_ld['Cautoriza'] == '10009'].reset_index(drop=True)
        df_nc.rename(columns = {'Cautoriza':'Cautoriza_nc','Costo_NC-Empleado' :'Costo_NC-Empleado_nc'}, inplace = True)
        df_cm.rename(columns = {'Cautoriza':'Cautoriza_cm','Costo_NC-Empleado' :'Costo_NC-Empleado_cm'}, inplace = True)
        res_nc = df_nc.groupby(['Desc_local']).agg({'Cautoriza_nc':'nunique','Costo_NC-Empleado_nc':'sum'})
        res_cm = df_cm.groupby(['Desc_local']).agg({'Cautoriza_cm':'nunique', 'Costo_NC-Empleado_cm':'sum'})
        res = pd.concat([res_nc, res_cm], axis=1 ).reset_index()
        res.fillna('0', inplace=True)
        res['Cautoriza_cm'] = pd.to_numeric(res['Cautoriza_cm'])
        res['Costo_NC-Empleado_nc'] = pd.to_numeric(res['Costo_NC-Empleado_nc'])
        res['Costo_NC-Empleado_cm'] = pd.to_numeric(res['Costo_NC-Empleado_cm'])
        res['Cautoriza_nc'] = pd.to_numeric(res['Cautoriza_nc'])
        res.set_index('Desc_local',inplace = True)
        return res, ld_str
    
    def alertas(self):
        print('Generando alertas...')
        lista_hojas = []
        for i in enumerate([self.initial_date,self.last_date]):
            nc_t = self.nc_df.loc[self.nc_df.Dcompra_nvo >= i[1]]
            df_v = self.df_v.loc[self.df_v['Día']>= i[1]]
            # Merging files  
            nme = nc_t.merge(self.ep, how='left', left_on=['Cvendedor'], right_on=['Cod_Empleado'])
            nme2 = nme.copy() #nme.loc[nme.Num_Documento.notna()]
            # Grouping by 
            gdfv = df_v.groupby(['Cod_Empleado', 'Desc_local']).agg({'Costo_Venta-Empleado':'sum'}).reset_index()
            r1 = nme2.groupby(['Cod_Empleado', 'Num_Documento','nombre_completo', 'Desc_local','Cargo']).agg({'Cautoriza':'nunique',  'Qcantidad':'sum', 'Costo_NC-Empleado':'sum'}).reset_index()
            r2 = r1.merge(gdfv, how='left', on=['Cod_Empleado', 'Desc_local'])
            r2['Costo_NC-Tienda'] = r2.groupby(['Desc_local'])['Costo_NC-Empleado'].transform('sum')
            r2['Costo_Venta-Tienda'] = r2.groupby(['Desc_local'])['Costo_Venta-Empleado'].transform('sum')
            r2['NC/Venta-Empleado'] = r2['Costo_NC-Empleado']/r2['Costo_Venta-Empleado']
            r2['Costo_NC-Empleado/Costo_NC-Tienda'] = r2['Costo_NC-Empleado']/r2['Costo_NC-Tienda']
            r2['CVenta-Empleado/CVenta-Tienda'] = r2['Costo_Venta-Empleado']/r2['Costo_Venta-Tienda']
            lista_hojas.append(r2)
        alert_x_ced = nme.loc[nme['Nrutcomprador'] == nme['Num_Documento']].reset_index()
        alert_x_ced["Tipo alerta"] = "Alerta x cedula"
        ncs_groupby = nme2.groupby(['Cautoriza', 'Desc_local', 'Dcompra_nvo', 'Nterminal_nvo','Nsecuencia_nvo', 'Hora', 'Cod_Empleado','Num_Documento', 'nombre_completo', 'Cargo']).agg({'SKU':'nunique', 'Qcantidad':'sum', 'Costo_NC-Empleado':'sum'}).reset_index()
        ncs_groupby.loc[:, ['Grabación?', 'Cliente?', 'Producto?']] = [np.nan, np.nan, np.nan]
        mayores_cienmil = ncs_groupby.loc[ncs_groupby['Costo_NC-Empleado']>=100000].reset_index()
        mayores_cienmil["Tipo alerta"] = "Alerta x monto"
        alertas_x_hora = ncs_groupby.loc[(ncs_groupby.Hora <=1000)|((ncs_groupby.Hora >=2100))].reset_index()
        alertas_x_hora["Tipo alerta"] = "Alerta x Hora"
        codm_groupby = nme2.groupby(['Cautoriza', 'Desc_local', 'Dcompra_nvo', 'Nterminal_nvo', 'Nsecuencia_nvo', 'Hora']).agg({'SKU':'nunique', 'Qcantidad':'sum', 'Costo_NC-Empleado':'sum'}).reset_index()
        alertas_cod_ma = codm_groupby.loc[codm_groupby['Cautoriza'] == "10009"].reset_index()
        if alertas_cod_ma.shape[0]> 0:
            print('--------------- Se encontraron codigos maestros ---------------')
            print(alertas_cod_ma) 
        else:
            print('--------------- No se encontraron codigos maestros ---------------')
        alertas_cod_ma.loc[:, ['Factura?', 'Doc identificación?', 'Nc?', 'Coincide NC - Factura?', 'Observaciones']] = [np.nan, np.nan, np.nan, np.nan, np.nan]
        alertas = pd.concat([mayores_cienmil,alertas_x_hora,alert_x_ced])
        alertas = alertas.reindex(columns=["Tipo alerta","Cautoriza","Desc_local","Dcompra_nvo","Nterminal_nvo","Nsecuencia_nvo","Hora","Cod_Empleado","Num_Documento","nombre_completo","Cargo","SKU","Qcantidad","Costo_NC-Empleado","Grabación?","Cliente?","Producto?","Observaciones"])
        lista_hojas.append(alertas)
        lista_hojas.append(nc_t)
        lista_hojas.append(alertas_cod_ma)
        return lista_hojas

    def guardar_res_tienda(self,df_mes, df_dia, alertas, df_nc_daily, alertas_cm, tienda):
        if tienda == "TIENDA ALEGRA":
                path = f'{self.path}\JPPs - Análisis de notas crédito - {tienda}'
        else:
            path = f'{self.path}\JPPs - Análisis de notas crédito - {tienda} - {tienda}'
        date_str = self.last_date.strftime('%y%m%d')
        writer = pd.ExcelWriter(f'{path}/{date_str} {tienda}.xlsx', engine = 'xlsxwriter')
        alertas.loc[alertas.Desc_local == tienda].to_excel(writer, sheet_name = 'Alertas', index=False)
        alertas_cm_t = alertas_cm.loc[alertas_cm.Desc_local == tienda]
        if alertas_cm_t.shape[0] > 0:
            alertas_cm_t.to_excel(writer, sheet_name = 'Codigos maestros', index=False)
        df_dia.loc[df_dia.Desc_local == tienda].to_excel(writer, sheet_name = 'Empleados x Día', index=False)
        df_mes.loc[df_mes.Desc_local == tienda].to_excel(writer, sheet_name = 'Empleados x Mes', index=False)
        df_nc_daily.loc[df_nc_daily.Desc_local == tienda].to_excel(writer, sheet_name = f'NCs {date_str}', index=False)
        writer.save()

    def save_res_cod_m(self):
        res = self.nc_df.rename(columns={'Local_creacion':'Local_nc', 'Desc_local':'Desc_local_nc', 'Dcompra_nvo':'Fecha_nc', 'Nterminal_nvo':'Nterminal_nc', 'Nsecuencia_nvo':'Nsecuencia_nc', 'Cautoriza':'Cautoriza_nc', 'Local_ant':'Local_venta','Descr_local_ant':'Descr_local_venta', 'Dcompra_ant':'Fecha_venta','Nterminal_ant':'Nterminal_venta', 'Nsecuencia_ant':'Nsecuencia_venta','Cvendedor_ant':'Cvendedor_venta', 'Xtipificacion':'motivo'})
        res = res.loc[(res['Cautoriza_nc'] == '10009') & (res['Fecha_nc'] == self.last_date) ,['Local_venta', 'Descr_local_venta','Fecha_venta', 'Nterminal_venta', 'Nsecuencia_venta', 'Cvendedor_venta','Local_nc', 'Desc_local_nc', 'Fecha_nc', 'Nterminal_nc','Nsecuencia_nc', 'Tipo_trx', 'Cautoriza_nc','Linea', 'LiDescripcion', 'SKU', 'EAN', 'PDescripcion', 'Cmarca', 'Tipo Producto', 'Nrutcomprador', 'Qcantidad','Costo_NC-Empleado', 'motivo']] 
        date_str = self.last_date.strftime('%y%m%d')
        if res.shape[0] > 0 :
            res.to_excel(f'{self.path}\JPPs - Análisis de notas crédito - General - Códigos Maestros/{date_str}_cm.xlsx', index = False)