# The Discord Auto Calendar Script
# Dependencies: pyautogui, Pillow, and opencv_python
# Created by Jacky Liang
calendarId = ''
apiKey = ''
timeZone = 'America/New_York'
timeOffset = '-05:00'
retina = True

# Script dependencies.
from datetime import date, datetime, timedelta
import pyautogui, os, ssl, urllib.request, urllib.parse, json, re

# Welcome message.
print('==========================================')
print('||   THE DISCORD AUTO CALENDAR SCRIPT   ||')
print('||      ~ CREATED BY JACKY LIANG ~      ||')
print('||    ACTIONS LOGGED, CTRL+C TO EXIT    ||')
print('==========================================')

# Configure pyautogui.
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 2

# Locate "Calendar" channel text box.
calendarTextBox = pyautogui.locateCenterOnScreen('calendarTextBox.png', grayscale = False, confidence = 0.9)
print('"Calendar" channel text box location:', calendarTextBox)

# Attempt to open "Calendar" channel text box.
if calendarTextBox == None:
    print('ERROR: "Calendar" channel text box not found.')
    exit()
else:
    print('Clicking "Calendar" channel text box ...')

    if retina == True:
        pyautogui.click(x = calendarTextBox.x / 2, y = calendarTextBox.y / 2)
    else:
        pyautogui.click(x = calendarTextBox.x, y = calendarTextBox.y)

# Open calendar data url as calendarDict.
googleApi = 'https://www.googleapis.com/calendar/v3/calendars/'
calendarEvents = '/events'
urlArguments = '?singleEvents=true&timeMin=' + date.today().strftime('%Y-%m-%d') + 'T00:00:00' + timeOffset + '&timeZone=' + timeZone + '&alt=json&key=' + apiKey
googleUrl = googleApi + urllib.parse.quote(calendarId) + calendarEvents + urlArguments

try:
    with urllib.request.urlopen(googleUrl) as url:
        calendarDict = json.loads(url.read().decode())
except urllib.error.HTTPError:
    print('ERROR: Google Calendar API could not be retrieved. Copy link below and paste in browser to see error:')
    print(googleUrl)
    exit()

# Navigate into calendarDict["items"].
calendarDictItems = calendarDict['items']

# Loop through calendarDict.items and post in "Calendar" channel.
for calendarDictItem in calendarDictItems:
    summary = calendarDictItem['summary']

    try:
        rawStartDateTime = calendarDictItem['start']['dateTime']
        rawEndDateTime = calendarDictItem['end']['dateTime']

        # Start date, hour, minute.
        startDate = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})T([\d]{2}):([\d]{2}):([\d]{2})(Z|[-+]{1}[\d]{2}:[\d]{2})', r'\2-\3-\1', rawStartDateTime)
        startHour = int(re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})T([\d]{2}):([\d]{2}):([\d]{2})(Z|[-+]{1}[\d]{2}:[\d]{2})', r'\4', rawStartDateTime))
        startMinute = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})T([\d]{2}):([\d]{2}):([\d]{2})(Z|[-+]{1}[\d]{2}:[\d]{2})', r'\5', rawStartDateTime)

        # End date, hour, minute.
        endDate = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})T([\d]{2}):([\d]{2}):([\d]{2})(Z|[-+]{1}[\d]{2}:[\d]{2})', r'\2-\3-\1', rawEndDateTime)
        endHour = int(re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})T([\d]{2}):([\d]{2}):([\d]{2})(Z|[-+]{1}[\d]{2}:[\d]{2})', r'\4', rawEndDateTime))
        endMinute = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})T([\d]{2}):([\d]{2}):([\d]{2})(Z|[-+]{1}[\d]{2}:[\d]{2})', r'\5', rawEndDateTime)

        if startDate != endDate:
            print('SKIPPING "' + summary + '" because multi-day timed events are not supported ...')
            continue

        # Determine if start hour is AM or PM.
        if startHour >= 12:
            startAmOrPm = 'pm'
            startHour = 12 if startHour == 12 else startHour - 12
        else:
            startAmOrPm = 'am'
            startHour = 12 if startHour == 0 else startHour

        # Determine if end hour is AM or PM.
        if endHour >= 12:
            endAmOrPm = 'pm'
            endHour = 12 if endHour == 12 else endHour - 12
        else:
            endAmOrPm = 'am'
            endHour = 12 if endHour == 0 else endHour

        print('Creating "' + summary + '" calendar event on ' + startDate + ' from ' + str(startHour) + ':' + startMinute + startAmOrPm + ' to ' + str(endHour) + ':' + endMinute + endAmOrPm + ' ...')
        pyautogui.write('!create "' + summary + '" on ' + startDate + ' from ' + str(startHour) + ':' + startMinute + startAmOrPm + ' to ' + str(endHour) + ':' + endMinute + endAmOrPm)
        pyautogui.press('enter')
    except KeyError:
        rawStartDate = calendarDictItem['start']['date']
        rawEndDate = calendarDictItem['end']['date']

        # Split start date into Year, Month, and Day.
        startYear = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})', r'\1', rawStartDate)
        startMonth = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})', r'\2', rawStartDate)
        startDay = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})', r'\3', rawStartDate)

        # Create start date with format: MM-DD-YYYY.
        startDate = str(startMonth) + '-' + str(startDay) + '-' + str(startYear)

        # Split end date into Year, Month, and Day.
        endYear = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})', r'\1', rawEndDate)
        endMonth = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})', r'\2', rawEndDate)
        endDay = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})', r'\3', rawEndDate)

        # Subtract 1 day from end date.
        subtractDays = timedelta(1)
        subtractEndDateOld = date(int(endYear), int(endMonth), int(endDay))
        subtractEndDateNew = subtractEndDateOld - subtractDays
        endYear = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})', r'\1', str(subtractEndDateNew))
        endMonth = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})', r'\2', str(subtractEndDateNew))
        endDay = re.sub(r'([\d]{4})-([\d]{2})-([\d]{2})', r'\3', str(subtractEndDateNew))

        # Create end day with format: MM-DD-YYYY.
        endDate = str(endMonth) + '-' + str(endDay) + '-' + str(endYear)

        # If start and end date is different.
        if startDate != endDate:
            # !create SUMMARY from MM-DD-YYYY to MM-DD-YYYY.
            print('Creating "' + summary + '" calendar event from ' + startDate + ' to ' + endDate + ' ...')
            pyautogui.write('!create "' + summary + '" from ' + startDate + ' to ' + endDate)
            pyautogui.press('enter')
        else:
            # !create SUMMARY on MM-DD-YYYY.
            print('Creating "' + summary + '" calendar event on ' + startDate + ' ...')
            pyautogui.write('!create "' + summary + '" on ' + startDate)
            pyautogui.press('enter')

# Task finished message.
print('============================================')
print('|| SUPPORTED EVENTS ADDED, IF YOU LIKE MY ||')
print('||     SCRIPT, PLEASE STAR & SPONSOR!     ||')
print('============================================')
