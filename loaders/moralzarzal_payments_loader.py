# -*- coding: UTF-8 -*-
from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget
import dateutil.parser

class MoralzarzalPaymentsLoader(PaymentsLoader):

    # Parse an input line into fields
    def parse_item(self, budget, line):
        # First two digits of the programme make the policy id
        # But what we want as area is the policy description
        policy_id = line[2].strip()[:2]
        policy = Budget.objects.get_all_descriptions(budget.entity)['functional'][policy_id]

        # We use dateutil.parser to parse the date no matter which format is used and then set
        # the format to the one expected by the item loader
        date = line[5].strip()
        date = dateutil.parser.parse(date).strftime("%Y-%m-%d")

        # Normalize payee data
        payee = line[7].strip()
        payee = self._titlecase(payee)

        # We truncate the description to the maximum length supported in the data model
        # and fix enconding errors
        description = line[8].strip()[:300]
        description = description.decode('utf-8','ignore').encode('utf-8')

        # Parse amount
        amount = line[9].strip()
        amount = self._read_english_number(amount)

        return {
            'area': policy,
            'programme': None,
            'fc_code': None,  # We don't try (yet) to have foreign keys to existing records
            'ec_code': None,
            'date': date,
            'contract_type': None,
            'payee': payee,
            'anonymized': False,
            'description': description,
            'amount': amount
        }
