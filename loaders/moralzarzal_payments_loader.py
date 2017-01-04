# -*- coding: UTF-8 -*-
import datetime

from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget

class MoralzarzalPaymentsLoader(PaymentsLoader):

    # Parse an input line into fields
    def parse_item(self, budget, line):
        # Avoid dirty lines in input data
        if line[0]=='':
            return None

        policy_id = line[5].strip()[:2] # First two digits of the programme make the policy id
        # But what we want as area is the policy description
        policy = Budget.objects.get_all_descriptions(budget.entity)['functional'][policy_id]

        return {
            'area': policy,
            'programme': None,
            'fc_code': None,  # We don't try (yet) to have foreign keys to existing records
            'ec_code': None,
            'date': datetime.datetime.strptime(line[8].strip(), "%d/%m/%Y").strftime("%Y-%m-%d"),  # We change the format to the one expected by the item loader
            'contract_type': None,
            'payee': self._titlecase(line[10].strip()),
            'anonymized': False,
            'description': line[11].strip(),
            'amount': self._read_english_number(line[12])
        }
