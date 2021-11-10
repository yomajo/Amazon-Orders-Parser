from excel_utils import get_last_used_row_col
from parser_utils import alert_VBA_duplicate_mapping_sku
import openpyxl
import os
import logging


class SKUMapping():
    '''class reads excel file to output a sku_mapping dictionary.
    Main method: read_sku_mapping_to_dict
    
    arg: SKU_mapping excel file abs path'''

    def __init__(self, sku_mapping_fpath:str):
        self.sku_mapping_fpath = sku_mapping_fpath

    def read_sku_mapping_to_dict(self) -> dict:
            '''reads mapping wb contents to dictionary. Output dict:
            {amazon_sku1: custom_label_1,
            amazon_sku2: custom_label_2,
            amazon_sku3: custom_label_3,
            ...}'''
            try:
                wb = openpyxl.load_workbook(self.sku_mapping_fpath)
                self.ws = wb['Mapping']
                self.check_ws_integrity()        
                sku_mapping = self.read_mapping_ws_to_dict()
                wb.close()
                return sku_mapping
            except Exception as e:
                logging.critical(f'Errors getting mapping dict inside read_sku_mapping_to_dict . Err: {e}. Closing mapping wb; returning empty mapping dict')
                wb.close()
                return {}
        
    def check_ws_integrity(self):
        '''ensures mapping workbook was not structuraly tampered with:
        3 columns, ws name, minimum 50 used rows, header titles'''        
        ws_limits = get_last_used_row_col(self.ws)
        last_col = ws_limits['max_col']
        self.last_row = ws_limits['max_row']
        assert self.last_row > 30, f'Less than 30 rows in SKU Mapping file. Last row used in \'Mapping\' ws: {self.last_row}'
        assert last_col == 3, f'Unexpected number of used columns in SKU Mapping file. Expected 3, got {last_col}'
        
        a1value = self.ws['A1'].value
        b1value = self.ws['B1'].value
        c1value = self.ws['C1'].value
        assert a1value == 'Amazon SKU', f'Unexpected value {a1value} in SKU Mapping active sheet A1 cell. Expected: Amazon SKU'
        assert b1value == 'Shop4Top Custom Label', f'Unexpected value {b1value} in SKU Mapping active sheet A1 cell. Expected: Shop4Top Custom Label'
        assert c1value == 'Item Title', f'Unexpected value {c1value} in SKU Mapping active sheet A1 cell. Expected: Item Title'

    def read_mapping_ws_to_dict(self) -> dict:
        '''iterates though data rows [2:self.last_row] in self.ws and returns sku_mapping dict:
        {sku1:custom_label1, sku2:custom_label2, ...}'''
        sku_mapping = {}
        for r in range(2, self.last_row + 1):
            sku, custom_label = self._get_mapping_row_data(r)            
            if sku not in sku_mapping.keys():
                sku_mapping[sku] = custom_label
            else:
                alert_VBA_duplicate_mapping_sku(sku)
        logging.info(f'Current sku mapping dict has {len(sku_mapping.keys())} entries')
        return sku_mapping

    def _get_mapping_row_data(self, r:int):
        '''returns amazon_sku, custom_label from columns A,B in self.ws on r (arg) row'''
        sku = self.ws.cell(r, 1).value
        custom_label = self.ws.cell(r, 2).value
        return sku, custom_label


if __name__ == "__main__":
    pass