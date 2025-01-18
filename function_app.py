import azure.functions as func
import logging
import requests
import json
import os
from datetime import datetime, timezone

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
        
        # Log some basic information about what we received
        logging.info('Successfully retrieved alerts')
        logging.info(f'Response contains {len(str(alerts))} characters')
        
        # Check if we shoudl save this response
        # You can set this environment variable to 'true' when you want to save a sample
        if os.getenv('SAVE_RESPONSE', 'false').lower() == 'true':
            sample_file = 'sample_response.json'
            logging.info(f'Saving sample response to {sample_file}')

            try:
                # Save JSON with nice formatting for readability
                with open(sample_file, 'w') as f:
                    json.dump(alerts, f, indent=2)
                logging.info('Sample response saved successfully')
            except IOError as e:
                logging.error('Failed to save sample response: %s', str(e))
        
    except requests.exceptions.RequestException as e:
        logging.error('Failed to fetch alerts: %s', str(e))
    except ValueError as e:
        logging.error('Failed to parse JSON response: %s', str(e))
    except Exception as e:
        logging.error('Unexpected error: %s', str(e))
    
    logging.info('Alert check completed at: %s', datetime.now(timezone.utc).isoformat())