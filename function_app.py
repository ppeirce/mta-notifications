import azure.functions as func
import logging
import requests
import json
import os
from datetime import datetime, timezone

def filter_seven_train_alerts(alerts_data):
    """
    Filters the alerts data to only include alerts related to the 7 train.
    
    This function looks through each entity in the alerts data and checks if any
    of its informed_entity objects have a sort_order matching "MTASBWY:7:20".
    
    Args:
        alerts_data (dict): The complete alerts JSON response from the MTA API
    
    Returns:
        list: A list of alert entities that are relevant to the 7 train
    """
    seven_train_alerts = []

    # the alerts are in the 'entity' array
    entities = alerts_data.get('entity', [])

    for entity in entities:
        # each entity should have an 'alert' object
        alert = entity.get('alert', {})

        # each alert should have an array of 'informed_entity' objects
        informed_entities = alert.get('informed_entity', [])

        # check each informed_entity for the 7 train sort_order
        for informed_entity in informed_entities:
            # the sort order is nested inside mercury_entity_selector
            mercury_entity_selector = informed_entity.get('transit_realtime.mercury_entity_selector', {})
            sort_order = mercury_entity_selector.get('sort_order', '')

            # if we find a match, add the entire entity to our results
            if sort_order == 'MTASBWY:7:20':
                seven_train_alerts.append(entity)
                break

    return seven_train_alerts

# Create a function app instance
app = func.FunctionApp()

# Register the function with the app
@app.function_name(name="mta_alert_check")
@app.schedule(schedule="0 */1 * * * *", arg_name="mytimer", run_on_startup=True)
def mta_alert_check(mytimer: func.TimerRequest) -> None:
    """
    Fetches MTA subway alerts and optionally saves them to a file for analysis.
    The JSON data is saved if the SAVE_RESPONSE environment variable is set to 'true'.
    """
    # Log when our function starts
    utc_timestamp = datetime.now(timezone.utc).isoformat()
    logging.info('Alert check starting at: %s', utc_timestamp)

    try:
        # The MTA's public alerts API endpoint
        url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts.json"
        
        logging.info('Fetching alerts from MTA...')
        response = requests.get(url)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Get the raw JSON response
        alerts = response.json()

        seven_train_alerts = filter_seven_train_alerts(alerts)

        logging.info(f'Found {len(seven_train_alerts)} alerts for the 7 train.')
        
        
    except requests.exceptions.RequestException as e:
        logging.error('Failed to fetch alerts: %s', str(e))
    except ValueError as e:
        logging.error('Failed to parse JSON response: %s', str(e))
    except Exception as e:
        logging.error('Unexpected error: %s', str(e))
    
    logging.info('Alert check completed at: %s', datetime.now(timezone.utc).isoformat())