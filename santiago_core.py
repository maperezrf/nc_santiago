from datetime import datetime
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
        self.last_date = self.df_nc.Dcompra_nvo.max()
        # alertas = self.alertas()
        # locales = self.df_nc.Desc_local.unique().tolist() 
        # for local in locales:
        #     self.guardar_res_tienda(alertas[0], alertas[1], alertas[2], alertas[3], local)

    def unir_ncs(self):
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
        self.nc_df.to_csv('input/consolidado_nc.csv', index=False)

    def load_files(self):
        self.ep = pd.read_excel('input/211020_empleados_planta.xlsx', dtype=str) 
        self.ep['nombre_completo'] = self.ep['Apell_Paterno'] + ' ' +  self.ep['Apell_Materno'] + ' ' + self.ep['Nombre']  
        self.ep = self.ep[const.cols_emp_planta]
        self.et = pd.read_excel('input/211020_empleados_temporales.xlsx', dtype=str ,usecols= const.cols_emp_temp)
        self.et.rename(columns={'SUCURSAL':'Sucursal', 'APELLIDOS Y NOMBRES':'nombre_completo', 'DOCUMENTO':'Num_Documento', 'FECHA INGRESO':'FecInicioContrato', 'CARGO':'Cargo', 'TDA_AREA':'Departamento'}, inplace=True)
        self.df_nc = pd.read_csv('input/consolidado_nc.csv', dtype='object', usecols= const.cols_consolidado_ventas)
        self.df_nc.rename(columns={'Mventa_nc':'Costo_NC-Empleado'}, inplace=True)
        self.df_v = pd.read_excel('input/consolidado_ventas_21.xlsx', dtype=str) # Ventas
        self.df_v = self.df_v.loc[~self.df_v.Local.isin(const.local_excluir_ventas)]
        self.df_v.rename(columns={'Número de Vendedor (Cod.)':'Cod_Empleado', 'Local':'Desc_local', 'Venta en $':'Costo_Venta-Empleado' }, inplace=True)

    def change_format(self):
        self.df_nc.Qcantidad = pd.to_numeric(self.df_nc.Qcantidad)
        self.df_nc.Cvendedor = pd.to_numeric(self.df_nc.Cvendedor)
        self.df_nc["Costo_NC-Empleado"]= -pd.to_numeric(self.df_nc["Costo_NC-Empleado"])
        self.df_nc.Hora = pd.to_numeric(self.df_nc.Hora)
        self.ep.Cod_Empleado  = pd.to_numeric(self.ep.Cod_Empleado)
        self.df_v['Cod_Empleado'] = pd.to_numeric(self.df_v['Cod_Empleado'])
        self.df_v['Costo_Venta-Empleado'] = pd.to_numeric(self.df_v['Costo_Venta-Empleado'])
    
    def change_format_date(self):
        self.df_nc.Dcompra_nvo = self.df_nc.Dcompra_nvo.str.replace('oct', '10')
        self.df_nc.Dcompra_nvo = self.df_nc.Dcompra_nvo.str.replace('nov', '11')
        self.df_nc.Dcompra_nvo = self.df_nc.Dcompra_nvo.str.replace('dic', '12')
        self.df_nc.Dcompra_nvo = self.df_nc.Dcompra_nvo.str.replace('ene', '01')
        self.df_nc.Dcompra_nvo = self.df_nc.Dcompra_nvo.str.replace('feb', '02')
        self.df_nc.Dcompra_nvo = pd.to_datetime(self.df_nc.Dcompra_nvo, format='%d-%m-%Y') # TODO arreglar para español 
        self.df_v['Día'] = pd.to_datetime(self.df_v['Día'], format='%d/%m/%Y')
    
    def set_filter(self): #TODO revisar orden en el que se llama el metodo
        self.df_nc = self.df_nc.loc[self.df_nc['Tipo_trx']=='NC'] # Transaction type 
        self.df_nc = self.df_nc.loc[~self.df_nc.Local_creacion.isin(const.local_excluir)] # Local number 
        self.df_nc.loc[self.df_nc['Desc_local']=='MARTINA COLINA', 'Desc_local'] = 'COLINA'
        self.df_nc.loc[self.df_nc['Desc_local']=='MARTINA FONTANAR', 'Desc_local'] = 'FONTANAR'
        self.df_nc.loc[self.df_nc['Desc_local']=='EXPO HAYUELOS', 'Desc_local'] = 'HAYUELOS'
        self.df_teams = self.df_nc.copy()
        # self.df_nc = self.df_nc.loc[self.df_nc['Cvendedor']!=47708] # Default seller 

    def get_df_teams(self):
        df_ld = self.df_teams[self.df_teams.Dcompra_nvo == self.last_date]
        ld_str = self.last_date.strftime('%d-%b-%y')
        res = df_ld.groupby(['Desc_local']).agg({'Cautoriza':'nunique', 'Mventa_nc':'sum'})
        return res, ld_str
    
    def alertas(self):
        lista_hojas = []
        for i in enumerate([self.initial_date,self.last_date]):
            nc_t = self.df_nc.loc[self.df_nc.Dcompra_nvo >= i[1]]
            df_v = self.df_v.loc[self.df_v['Día']>= i[1]]
            # Merging files  
            nme = nc_t.merge(self.ep, how='left', left_on=['Cvendedor'], right_on=['Cod_Empleado'])
            nme2 = nme.loc[nme.Num_Documento.notna()]
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
        alertas = pd.concat([mayores_cienmil,alertas_x_hora,alert_x_ced])
        alertas = alertas.reindex(columns=["Tipo alerta","Cautoriza","Desc_local","Dcompra_nvo","Nterminal_nvo","Nsecuencia_nvo","Hora","Cod_Empleado","Num_Documento","nombre_completo","Cargo","SKU","Qcantidad","Costo_NC-Empleado","Grabación?","Cliente?","Producto?"])
        lista_hojas.append(alertas)
        lista_hojas.append(nc_t)
        return lista_hojas

    def guardar_res_tienda(self,df_mes, df_dia, alertas, df_nc_daily, tienda):
       date_str = self.last_date.strftime('%y%m%d')
       path = f'{self.path}\JPPs - Análisis de notas crédito - {tienda} - {tienda}'
       writer = pd.ExcelWriter(f'{path}/{date_str} {tienda}prueba.xlsx', engine='xlsxwriter')
       alertas.loc[alertas.Desc_local == tienda].to_excel(writer, sheet_name='Alertas', index=False)
       df_dia.loc[df_dia.Desc_local == tienda].to_excel(writer, sheet_name='Empleados x Día', index=False)
       df_mes.loc[df_mes.Desc_local == tienda].to_excel(writer, sheet_name='Empleados x Mes', index=False)
       df_nc_daily.loc[df_nc_daily.Desc_local==tienda].to_excel(writer, sheet_name=f'NCs {date_str}', index=False)
       writer.save()


    

