from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import requests
import subprocess
import logging
from datetime import datetime, timedelta
import gettext
import os
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
logger = logging.getLogger(__name__)

class DaysBetweenDatesExtension(Extension):

    def __init__(self):
        super(DaysBetweenDatesExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):
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
            # Default to a custom date range or handle as needed
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)

        querystring = {
            "StartDate": start_date.isoformat() + "Z",
            "EndDate": end_date.isoformat() + "Z"
        }
        return querystring

    def getCalendarEvents(self, items, filter):
        
        
        
        url = "https://teams.microsoft.com/api/mt/part/amer-02/beta/me/calendarEvents"
        # querystring = {"StartDate":"2023-12-04T14:13:09.307Z","EndDate":"2023-12-07T14:13:09.307Z"}
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
            desc = "Starts in: " + startDate
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
