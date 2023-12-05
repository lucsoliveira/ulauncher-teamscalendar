from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import requests
import logging
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)

class DaysBetweenDatesExtension(Extension):

    def __init__(self):
        super(DaysBetweenDatesExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):
    
    def formatDate(self, eventDate, utc_offset_minutes):
        actual_date = datetime.strptime(eventDate[:19], '%Y-%m-%dT%H:%M:%S')
        offset_timedelta = timedelta(minutes=utc_offset_minutes)
        actual_date += offset_timedelta
        today = datetime.utcnow() + offset_timedelta
        time_difference = actual_date - today
        if actual_date.day == today.day:
            if time_difference.days == -1:
                formatted_time = f'[COMPLETED] {actual_date.strftime("%H:%M")}'
            else:
                formatted_time = f'Today at {actual_date.strftime("%H:%M")}'
        else:
            formatted_time = actual_date.strftime("%d/%m/%y %H:%M")
        return formatted_time

    def buildQueryString(self, filter_type):

        if filter_type == "today":
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif filter_type == "tomorrow":
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            end_date = start_date + timedelta(days=1)
        elif filter_type == "week":
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(weeks=1)
        else:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)

        querystring = {
            "StartDate": start_date.isoformat() + "Z",
            "EndDate": end_date.isoformat() + "Z"
        }
        return querystring

    def getCalendarEvents(self, items, filter):
        
        url = "https://teams.microsoft.com/api/mt/part/amer-02/beta/me/calendarEvents"
        headers = {"Authorization": "Bearer " + self.apikey}
        querystring = self.buildQueryString(filter)
        response = requests.get(url, headers=headers, params=querystring)
        obj = response.json()
        events = obj["value"]
 
        for event in events:
            urlEvent = ""
            if "skypeTeamsMeetingUrl" in event:
                urlEvent = event["skypeTeamsMeetingUrl"]
    
            eventName = event["subject"]
            startDate =  event["startTime"]
            utcOffset =  event["utcOffset"]
            formatted_time = self.formatDate(startDate, utcOffset)
            desc = formatted_time 
            ev = ExtensionResultItem(name=eventName, description=desc, on_enter=OpenUrlAction(urlEvent))
            items.append(ev)
                
    
    def on_event(self, event, extension):
        items = []
        query = event.get_argument()
        
        if not query:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/calendar-days-solid.svg', name='Enter today, tomorrow or week.', on_enter=HideWindowAction())
            ])
        self.apikey = extension.preferences["api_key"]
            
        if "today" in query:
            self.getCalendarEvents(items, query)
        elif "tomorrow" in query:
            self.getCalendarEvents(items, query)
        elif "week" in query:
            self.getCalendarEvents(items, query)
        else: 
            return 0
        
        return RenderResultListAction(items)
        

if __name__ == '__main__':
    DaysBetweenDatesExtension().run()
