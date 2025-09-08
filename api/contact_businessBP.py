from utils.contact.contact_business import contact_business
import azure.functions as func


contact_businessBP = func.Blueprint()
def get_daily_count(date):
    ''' Returns [20, 0 , 0]'''
    pass

@contact_businessBP.timer_trigger(schedule="0 */2 10-13 * * 1-5", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def daily_send(myTimer: func.TimerRequest) -> None:

    daily_count = get_daily_count(date)
    