'''
Module to return a bool if search word was found in the log at a given index position out with a  given time.
'''

from datetime import datetime, timedelta

def inplay_idle_check(search_word, index_possition, time_in_mins, final_return):
    '''
    Search_word will be searched in the log from last line up
    a list of lines containing search_word will be created
    a datetime object will be created for the 
    log entry in the list at the given index_possition.
    If that datetime object is older then current date time - time_in_mins
    true us returned as game is assumed to be idle.
    Final_return is bool returned if there is no entry containing search_word in the log.
    '''

    with open('logs\conection_log.log', 'r') as log:
        # Check log for instances of move.
        x = [line for line in reversed(list(log)) if search_word in line and "TEXT" in line]
        if x:
            # Crete a datetime object for the most recent instance.
            connection_time = datetime.fromisoformat(x[index_possition][0:19].replace(" ", "T"))
            # Create an time object for 10 before current time.
            allowable_idle_time = datetime.now() - timedelta(minutes=time_in_mins)
            # If no move has been made in 10 mins return idle
            if allowable_idle_time > connection_time:
                return True
            return False
        return final_return
