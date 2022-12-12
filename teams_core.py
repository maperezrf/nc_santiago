import config.nc_webhook as data_nc
import pymsteams

class TEAMS_CORE():
    dwt = data_nc.dict_webhook_tiendas
    dst = data_nc.dict_sharepoint_tiendas
    dct = data_nc.ciudades_tiendas

    def get_data_nc(self):
        return self.dwt, self.dst, self.dct

    def send_msg(self, tienda, webhook, url_sp, ciudad, qty_nc, sum_nc, date, qty_cm ,sum_cm):
        myTeamsMessage = pymsteams.connectorcard(webhook, verify=False)
        myTeamsMessage.title(f"<strong>Reporte notas crédito {date}</strong>")
        myTeamsMessage.text(f'Tienda: {tienda} - {ciudad}')
        section_1 = pymsteams.cardsection()
        section_1.title('<FONT SIZE=3><strong>Notas crédito</strong></font>')
        section_1.addFact("Cantidad:", qty_nc)
        section_1.addFact("Costo total:", sum_nc)
        myTeamsMessage.addSection(section_1)
        section_2 = pymsteams.cardsection()
        section_2.title('<FONT SIZE=3><strong>Códigos maestros</strong></font>')
        section_2.addFact("Cantidad:", qty_cm)
        section_2.addFact("Costo total:", sum_cm)
        myTeamsMessage.addSection(section_2)
        myTeamsMessage.addLinkButton("Más información", url_sp)
        myTeamsMessage.send()

    def send_msg_general(self,webhook, qty, sum, date):
        myTeamsMessage = pymsteams.connectorcard(webhook, verify=False)
        myTeamsMessage.title(f"Reporte de notas crédito | {date}")
        myTeamsMessage.text('Resumen tiendas')
        section_1 = pymsteams.cardsection()
        section_1.addFact("Cantidad:", qty)
        section_1.addFact("Costo total:", sum)
        myTeamsMessage.addSection(section_1)
        myTeamsMessage.send()
    
    def send_msg_cm(self, webhook, url_sp, qty_nc, sum_nc, date, listado):
        myTeamsMessage = pymsteams.connectorcard(webhook, verify=False)
        myTeamsMessage.title(f"<strong>Códigos maestros {date}</strong>")
        myTeamsMessage.summary("popo")
        section_1 = pymsteams.cardsection()
        section_1.addFact("Cantidad:", qty_nc)
        section_1.addFact("Costo total:", sum_nc)
        myTeamsMessage.addSection(section_1)
        if len(listado) > 0:
            section_2 = pymsteams.cardsection()
            section_2.title('Tiendas')
            section_2.text(listado)
            myTeamsMessage.addSection(section_2)
        myTeamsMessage.addLinkButton("Más información", url_sp)
        myTeamsMessage.send()