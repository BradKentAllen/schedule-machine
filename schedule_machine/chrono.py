#!/usr/bin/env python
# -*- coding: utf-8 -*-
# chron_utilites.py

'''for schedule-machine

AditNW LLC, Redmond , WA
www.AditNW.com
'''
__author__ = 'Brad Allen, AditNW LLC'
__all__ = ['chronograph',]

#### letter revision update requires update to config files

# Rev 0.0.1 - DEV

__version__ = 'vZ.0.1'
# Z is non-production developmental rev

from datetime import datetime
from time import time, sleep
import pytz

class Timers:
    def __init__(self):
        #### timer job lists
        self.timer_jobs = {
            'every poll': [],
            'every second': [],
            'on the 5 second': [],
            'on the 15 second': [],
            'on the 30 second': [],
            'every minute': [],
            'on the 5 minute': [],
            'on the 15 minute': [],
            'on the 30 minute': [],
            'every hour': [],
            'schedule': [],
            }

    class Scheduled_Events:
        '''Scheduled Events are for scheduled items set 
        for a specific time.  Mark is time HH:MM:SS
        '''
        def __init__(self, T_mode, func, mark=None):
            print('init')
            self.T_mode = T_mode
            self.func = func
            self.mark = mark

    def create_timer(self, T_mode, func, mark=None):
        timer_mode = T_mode.lower()
        if timer_mode[:2] == 'on' or timer_mode[:5] == 'every':
            self.timer_jobs[timer_mode].append(func)
        elif timer_mode[:2] == 'at':
            pass
        elif timer_mode == 'schedule':
            pass
        else:
            raise ValueError(f'Attempted to use non-timer: {T_mode}')


class Chronograph:
    def __init__(self, jobs, poll_time=.1, local_time_zone='UTC', poll_priority=False):
        print(f'init Timer: {local_time_zone}')
        self.jobs = jobs
        self.POLL_MILLIS = poll_time * 1000
        self.POLL_PRIORITY = poll_priority
        self.local_time_zone = local_time_zone

    def run_timers(self):
        #### set up last varables
        (last_hour, last_minute, last_second) = get_time(self.local_time_zone)
        last_milli = 0
        start_milli = time() * 1000

        while True:
            milli = (time() * 1000) - start_milli
            if (milli - last_milli) >= self.POLL_MILLIS:
                HHMMSS = get_time(self.local_time_zone)

                #### Every poll ####
                if self.jobs['every poll'] != []:
                    self.run_poll_jobs(self.jobs['every poll'])


                #### Second ####
                if last_second != HHMMSS[2]:
                    #### Every second jobs ####
                    for job in self.jobs['every second']:
                        job()
                    last_second = HHMMSS[2]

                    #### On second jobs ####
                    if int(HHMMSS[2])%5 == 0 or int(HHMMSS[2]) == 0:
                        for job in self.jobs['on the 5 second']:
                            job()

                    if int(HHMMSS[2])%15 == 0 or int(HHMMSS[2]) == 0:
                        for job in self.jobs['on the 15 second']:
                            job()

                    if int(HHMMSS[2])%30 == 0 or int(HHMMSS[2]) == 0:
                        for job in self.jobs['on the 30 second']:
                            job()

                    #### Minute ####
                    if last_minute != HHMMSS[1]:
                        #### Every minute jobs ####
                        for job in self.jobs['every minute']:
                            job()
                        last_minute = HHMMSS[1]

                        #### On second jobs ####
                        if int(HHMMSS[1])%5 == 0 or int(HHMMSS[1]) == 0:
                            for job in self.jobs['on the 5 minute']:
                                job()

                        if int(HHMMSS[1])%15 == 0 or int(HHMMSS[1]) == 0:
                            for job in self.jobs['on the 15 minute']:
                                job()

                        if int(HHMMSS[1])%30 == 0 or int(HHMMSS[1]) == 0:
                            for job in self.jobs['on the 30 minute']:
                                job()

                        #### Hour ####
                        if last_hour != HHMMSS[0]:
                            #### Every hour jobs ####
                            for job in self.jobs['every hour']:
                                job()
                            last_hour = HHMMSS[0]

                #### polling marker
                last_milli = milli


    def run_poll_jobs(self, job_list):
        for job in job_list:
            job()



def get_time_stamp(local_time_zone='UTC', time_format='HMS'):
    now_local = datetime.now(pytz.timezone(local_time_zone))
    if time_format == 'YMD:HM':
        return now_local.strftime('%Y-%m-%d' + '-' + '%H:%M')
    else:
        return now_local.strftime('%H:%M:%S')

def get_time(local_time_zone='UTC'):
    now_local = datetime.now(pytz.timezone(local_time_zone))
    HH = now_local.strftime('%H')
    MM = now_local.strftime('%M')
    SS = now_local.strftime('%S')
    return (HH, MM, SS)





