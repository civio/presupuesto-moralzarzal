# -*- coding: UTF-8 -*-
from budget_app.loaders import SimpleBudgetLoader
from budget_app.models import *
from decimal import *
import csv
import os
import re

class MoralzarzalBudgetLoader(SimpleBudgetLoader):

    # Parse an input line into fields
    def parse_item(self, filename, line):
        # Programme codes have changed in 2015, due to new laws. Since the application expects a code-programme
        # mapping to be constant over time, we are forced to amend budget data prior to 2015.
        # See https://github.com/dcabo/presupuestos-aragon/wiki/La-clasificaci%C3%B3n-funcional-en-las-Entidades-Locales
        programme_mapping = {
        # old programme: new programme
            '1340': '1350',     # Protección Civil
            '1350': '1360',     # Servicio de prevención y extinción de incendios
            '1530': '1521',     # Promoción y gestión de vivienda de protección pública
            '1550': '1530',     # Vías públicas
            '3230': '3270',     # Fomento de la convivencia ciudadana
            '3240': '3260',     # Servicios complementarios de educación
        }
    
        # On economic codes we get the first three digits (everything but last two)
        ec_code = line[2].strip()
        ec_code = ec_code[:-2]

        # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
        item_number = line[2].strip()
        item_number = item_number[-2:]

        # Institutional code (all income goes to the root node)
        ic_code = '000'

        # Description
        description = line[3].strip()

        # Type of data
        is_expense = (filename.find('gastos.csv')!=-1)
        is_actual = (filename.find('/ejecucion_')!=-1)

        # Expenses
        if is_expense:
            # We got 3- or 4- digit functional codes as input, so add a trailing zero
            fc_code = line[1].strip()
            fc_code = fc_code.ljust(4, '0')

            # For years before 2015 we check whether we need to amend the programme code
            year = re.search('municipio/(\d+)/', filename).group(1)
            if int(year) < 2015:
                fc_code = programme_mapping.get(fc_code, fc_code)

            # Parse amount
            amount = line[10 if is_actual else 7].strip()
            amount = self._parse_amount(amount)


            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code,
                'ic_code': ic_code,
                'item_number': item_number,
                'description': description,
                'amount': amount
            }

        # Income
        else:
            # Parse amount
            amount = line[7 if is_actual else 4].strip()
            amount = self._parse_amount(amount)

            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code,
                'ic_code': ic_code,
                'item_number': item_number,
                'description': description,
                'amount': amount
            }
