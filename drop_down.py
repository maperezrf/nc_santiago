import pandas as pd
from datetime import date, time
import xlsxwriter
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl import load_workbook
from openpyxl.workbook.protection import WorkbookProtection
from openpyxl.styles import Protection 
from importlib import import_module
from datetime import datetime, timedelta
from os import listdir
import plotly.express as px
from os.path import isfile, join
import numpy as np
import sys

class DROP_DOWN():
    def drop_down_block(libro,self):
        self.hoja=libro.active
        dv = DataValidation(type="list", formula1='"SI,NO"', allow_blank=True)
        self.hoja.add_data_validation(dv)
        dv.add('o2:o1048576')
        dv.add('p2:p1048576')
        dv.add('q2:q1048576')
        self.hoja.protection.sheet = True
        for col in ['o', 'p','q','r']:
            for cell in self.hoja[col]:
                cell.protection = Protection(locked=False)
    
    def format_(fecha,self):
        with open('config\path.txt', "r") as tf:
                path = tf.read()
                path = path.replace("\\","/")
        tf.close()

        for i in listdir(path):
            files_store= pd.DataFrame()
            if i.startswith('JPPs - Análisis de notas crédito - '):
                new_path= f"{path}/{i}"
                files_names = [f for f in listdir(new_path) if isfile(join(new_path, f))]
                for j in (files_names):
                    if j.endswith('.xlsx'):
                        for i in [fecha]:
                            if j.startswith(i):
                                if '_cm' in j:
                                    pass
                                else:
                                        libro = load_workbook(f'{new_path}/{j}')
                                        self.drop_down_block(libro)
                                        libro.save(f'{new_path}/{j}')
        

