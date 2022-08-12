import config.nc_webhook as data_nc
import pymsteams

class TEAMS_CORE():
    dwt = data_nc.dict_webhook_tiendas
    dst = data_nc.dict_sharepoint_tiendas
    dct = data_nc.ciudades_tiendas

    def get_data_nc(self):
        return self.dwt, self.dst, self.dct

    def send_msg(self,tienda, webhook, url_sp, ciudad, qty, sum, date):
        myTeamsMessage = pymsteams.connectorcard(webhook, verify=False)
        myTeamsMessage.title(f"Reporte de notas crédito | {date}")
        myTeamsMessage.text(f'Tienda: {tienda} - {ciudad}')
        section_1 = pymsteams.cardsection()
        section_1.addFact("Cantidad:", qty)
        section_1.addFact("Costo total:", sum)
        myTeamsMessage.addSection(section_1)
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
