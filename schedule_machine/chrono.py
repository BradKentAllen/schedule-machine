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

# Rev 0.0.1 - initial
# Rev 0.0.2 - bug fix: added append to schedule call

__version__ = 'vZ.0.1'
# Z is non-production developmental rev

from datetime import datetime
from time import time, sleep
import pytz
import threading

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
            'schedule': [],  # (function, 'HH:MM')
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
            try:
                self.timer_jobs[timer_mode].append(func)
            except KeyError:
                raise ValueError(f'Attempted to use non-timer: {T_mode}')

        elif timer_mode == 'schedule':
            if type(mark[:2]) == str and type(mark[-2:]) == str:
                try:
                    int(mark[:2])
                except ValueError:
                    raise ValueError(f'Schedule time format issue, are hours in 24 hour format? e.g. 07:02')
                try:
                    int(mark[-2:])
                except ValueError:
                    raise ValueError(f'Schedule time format issue, are minutes two digits? e.g. 17:02')
                
                if 0 <= int(mark[:2]) < 25 and 0 <= int(mark[-2:]) < 60:
                    self.timer_jobs['schedule'].append((func, mark))
                else:
                    raise ValueError(f'Attempted to schedule time not in format HH:MM {func[1]}')
            else:
                raise ValueError(f'Attempted to schedule time that is not a string {func[1]}')

        else:
            raise ValueError(f'Attempted to use non-timer: {T_mode}')


class Chronograph:
    def __init__(self, jobs, local_time_zone='UTC'):
        print(f'init Timer: {local_time_zone}')
        self.jobs = jobs
        self.POLL_MILLIS = 100  # .1 seconds
        self.local_time_zone = local_time_zone

    def run_timers(self):
        #### set up last varables
        (last_hour, last_minute, last_second) = get_time(self.local_time_zone)
        last_milli = 0
        start_milli = time() * 1000

        # this only allows one thread to run at a time
        self.thread_lock = False

        while True:
            milli = (time() * 1000) - start_milli

            #### deal with millis rolling
            # this should never happen
            if milli < 0:
                milli = (time() * 1000)
                last_milli = 0

            #### jobs are run in two threads
            # every poll jobs are run in the main thread
            # all others are grouped and run in a separate thread
            self.thread_jobs = []

            if (milli - last_milli) >= self.POLL_MILLIS:
                HHMMSS = get_time(self.local_time_zone)

                # note: every poll jobs are run after thread_jobs is
                # sent off (see below)

                #### Second ####
                if last_second != HHMMSS[2]:
                    #### Every second jobs ####
                    for job in self.jobs['every second']:
                        job()
                    last_second = HHMMSS[2]

                    #### On second jobs ####
                    if int(HHMMSS[2])%5 == 0 or int(HHMMSS[2]) == 0:
                        for job in self.jobs['on the 5 second']:
                            self.thread_jobs.append(job)

                    if int(HHMMSS[2])%15 == 0 or int(HHMMSS[2]) == 0:
                        for job in self.jobs['on the 15 second']:
                            self.thread_jobs.append(job)

                    if int(HHMMSS[2])%30 == 0 or int(HHMMSS[2]) == 0:
                        for job in self.jobs['on the 30 second']:
                            self.thread_jobs.append(job)

                    #### Minute ####
                    if last_minute != HHMMSS[1]:
                        #### Every minute jobs ####
                        for job in self.jobs['every minute']:
                            self.thread_jobs.append(job)
                        last_minute = HHMMSS[1]

                        #### On minute jobs ####
                        if int(HHMMSS[1])%5 == 0 or int(HHMMSS[1]) == 0:
                            for job in self.jobs['on the 5 minute']:
                                self.thread_jobs.append(job)

                        if int(HHMMSS[1])%15 == 0 or int(HHMMSS[1]) == 0:
                            for job in self.jobs['on the 15 minute']:
                                self.thread_jobs.append(job)

                        if int(HHMMSS[1])%30 == 0 or int(HHMMSS[1]) == 0:
                            for job in self.jobs['on the 30 minute']:
                                self.thread_jobs.append(job)

                        #### schedule jobs
                        if self.jobs['schedule'] != []:
                            for details in self.jobs['schedule']:
                                if details[1][:2] == HHMMSS[0] and details[1][-2:] == HHMMSS[1]:
                                    self.thread_jobs.append(details[0])


                        #### Hour ####
                        if last_hour != HHMMSS[0]:
                            #### Every hour jobs ####
                            for job in self.jobs['every hour']:
                                self.thread_jobs.append(job)
                            last_hour = HHMMSS[0]

                #### Run all jobs but poll in separate thread
                if self.thread_lock == False:
                    chrono_thread = threading.Thread(target=self.run_thread_jobs, daemon=True)
                    chrono_thread.start()
                else:
                    if self.thread_jobs == []:
                        pass
                    else:
                        print('>>> LOCKED missed chrono_thread <<<')

                #### polling marker
                last_milli = milli

                #### Run Every poll jobs ####
                if self.jobs['every poll'] != []:
                    for job in self.jobs['every poll']:
                        job()


    def run_thread_jobs(self):
        self.thread_lock = True
        for job in self.thread_jobs:
            job()
        self.thread_lock = False
        



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





