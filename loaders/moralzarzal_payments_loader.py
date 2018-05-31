# -*- coding: UTF-8 -*-
from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget

import dateutil.parser
import re


payments_mapping = {
    'default': {'fc_code': 2, 'date': 5, 'payee': 7, 'description': 8, 'amount': 9},
    '2017': {'fc_code': 1, 'date': 3, 'payee': 5, 'description': 6, 'amount': 7},
}


class MoralzarzalPaymentsCsvMapper:
    def __init__(self, year):
        mapping = payments_mapping.get(str(year))

        if not mapping:
            mapping = payments_mapping.get('default')

        self.fc_code = mapping.get('fc_code')
        self.date = mapping.get('date')
        self.payee = mapping.get('payee')
        self.description = mapping.get('description')
        self.amount = mapping.get('amount')


class MoralzarzalPaymentsLoader(PaymentsLoader):
    # Parse an input line into fields
    def parse_item(self, budget, line):
        # Mapper
        mapper = MoralzarzalPaymentsCsvMapper(budget.year)

        # First two digits of the programme make the policy id
        # But what we want as area is the policy description
        policy_id = line[mapper.fc_code].strip()[:2]
        policy = Budget.objects.get_all_descriptions(budget.entity)['functional'][policy_id]

        # We use dateutil.parser to parse the date no matter which format is used and then set
        # the format to the one expected by the item loader
        date = line[mapper.date].strip()
        date = dateutil.parser.parse(date, dayfirst=True).strftime("%Y-%m-%d")

        # Normalize payee data
        # remove triling spaces
        payee = line[mapper.payee].strip()
        # remove commas
        payee = payee.replace(', ', ' ').replace(',', ' ')
        # normalize company types
        payee = re.sub(r'SL$', 'S.L.', payee)
        payee = re.sub(r'SLL$', 'S.L.L.', payee)
        payee = re.sub(r'SLU$', 'S.L.U.', payee)
        payee = re.sub(r'SA$', 'S.A.', payee)
        payee = re.sub(r'S A$', 'S.A.', payee)
        payee = re.sub(r'S.A.OK$', 'S.A.', payee)
        payee = re.sub(r'SAU$', 'S.A.U.', payee)
        # titleize to avoid all caps
        payee = self._titlecase(payee)
        # put small words in lower case
        payee = re.sub(r' E ', ' e ', payee)
        payee = re.sub(r' De ', ' de ', payee)
        payee = re.sub(r' Del ', ' del ', payee)
        payee = re.sub(r' Y ', ' y ', payee)
        # put abbreviatons in upper case
        payee = re.sub(r'^Jc ', 'JC ', payee)
        payee = re.sub(r'^Mgs ', 'MGS ', payee)
        payee = re.sub(r' Ii ', ' II ', payee)
        payee = re.sub(r' Sdg ', ' SDG ', payee)
        # amend remaining
        payee = re.sub(r'de Isidro', 'De Isidro', payee)
        payee = re.sub(r'Canal Isabel', 'Canal de Isabel', payee)

        # We truncate the description to the maximum length supported in the data model
        # and fix enconding errors
        description = line[mapper.description].strip()[:300]
        description = description.decode('utf-8','ignore').encode('utf-8')

        # Parse amount
        amount = line[mapper.amount].strip()
        amount = self._read_english_number(amount)

        return {
            'area': policy,
            'programme': None,
            'ic_code': None,
            'fc_code': None,
            'ec_code': None,
            'date': date,
            'payee': payee,
            'anonymized': False,
            'description': description,
            'amount': amount
        }
