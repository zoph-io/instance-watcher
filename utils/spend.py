#!/usr/bin/python3
# -*- coding: utf-8 -*-

def spending():
    try:
        logging.info("Getting MTD Spending")
        # Retreive current spend for this month
        monthly_cost = boto3.client('ce', region_name='us-east-1')
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        firstdayofmonth = datetime.today().replace(day=1).strftime('%Y-%m-%d')
        cost = monthly_cost.get_cost_and_usage(
        TimePeriod={
            'Start': firstdayofmonth,
            'End': yesterday
        },
        Granularity='MONTHLY',
        Metrics=[
            'AmortizedCost',
        ]
        )

        for r in cost['ResultsByTime']:
            usd = r['Total']['AmortizedCost']['Amount']
            usd = round(float(usd), 2)

        return usd
    except Exception as e:
        logging.error("Failed to get spending with error: %s", e)