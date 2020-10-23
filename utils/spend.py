#!/usr/bin/python3
# -*- coding: utf-8 -*-

def spending():
    try:
        logging.info("Getting MTD Spending")
        # Retreive current spend for this month
        client = boto3.client('ce', region_name='us-east-1')
        today = datetime.now()
        todaystr = today.strftime('%Y-%m-%d')
        tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        firstdayofmonth = datetime.today().replace(day=1).strftime('%Y-%m-%d')
        lastdayofmonth = today.replace(day = calendar.monthrange(today.year, today.month)[1]).strftime('%Y-%m-%d')
        
        if firstdayofmonth != todaystr:
            mtd_cost = client.get_cost_and_usage(
                TimePeriod={
                    'Start': firstdayofmonth,
                    'End': todaystr
                },
                Granularity='MONTHLY',
                Metrics=[
                    'AmortizedCost',
                ]
                )
    
            for r in mtd_cost['ResultsByTime']:
                usd = r['Total']['AmortizedCost']['Amount']
                usd = round(float(usd), 2)
            logging.info("MTD Spend: %s", usd)
        else:
            logging.info("Spend not available (1st day of month)")
            usd = 0
        
        # Forecast
        # Disable forcast at the last day of month
        if tomorrow != lastdayofmonth:
            logging.info("Tomorrow: %s is different than lastdayofmonth: %s", tomorrow, lastdayofmonth)
            if tomorrow < lastdayofmonth:
                logging.info("Tomorrow: %s is inferior than lastdayofmonth: %s", tomorrow, lastdayofmonth)
                forecast_cost = client.get_cost_forecast(
                    TimePeriod={
                        'Start': tomorrow,
                        'End': lastdayofmonth
                    },
                    Metric='UNBLENDED_COST',
                    Granularity='MONTHLY',
                    PredictionIntervalLevel=99)
                f_usd = forecast_cost['Total']['Amount']
                f_usd = round(float(f_usd), 2)
            else:
                logging.info("Tomorrow: %s is > of lastdayofmonth: ", tomorrow, lastdayofmonth)
                f_usd = 0
        else:
            logging.info("Forecast not available (end of month)")
            f_usd = 0

        logging.info("Forecasted Spend: %s", f_usd)

        return [usd, f_usd]
    except Exception as e:
        logging.error("Failed to get spending with error: %s", e)
