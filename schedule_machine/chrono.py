#!/usr/bin/env python
# -*- coding: utf-8 -*-
# chron.py

'''primary code for schedule-machine
Simple schedule package for managing timed functions in a python
based machine such as Raspberry Pi.  Target is to get reasonably 
consistent timing to .1 seconds.

AditNW LLC, Redmond , WA
www.AditNW.com
'''
__author__ = 'Brad Allen, AditNW LLC'
__all__ = ['chronograph',]

#### letter revision update requires update to config files

# Rev 0.0.1 - initial
# Rev 0.0.2 - bug fix: added append to schedule call
# Rev 0.0.3 - debug/neaten, add wait_to_run, redid validations
# Rev 0.0.4 - change function check to hasattr(func, '__call__')
# Rev 0.0.5 - add thread1 for every second timers
# Rev 0.0.6 - add variable poll_millis

__version__ = 'vZ.0.5'
# Z is non-production developmental rev

from datetime import datetime
from time import time, sleep
import pytz
import threading
import types
import timeit


class Timers:
    '''Class to create dictionary of timers for use in Chronograph.
    '''
    def __init__(self):
        '''self.timer_jobs is the primary resource in Timers
        This is filled by Timers
        It is then accessed by the source
        and served to Chronograph
        '''
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

    def create_timer(self, T_mode, func, mark=None):
        '''Add a timer to self.timer_jobs
        'on' and 'every' timers require a function
        'schedule' timers require function and a time
        Time must be a string in 24 hr format

        Two types of timers (T-mode):
        1) 'on' and 'every' set up regular timers
        2) 'schedule' timers occur at a specific, local time
        '''
        #### validate timer
        # allow capitalization in timers
        timer_mode = T_mode.lower()

        # is a string
        if not isinstance(timer_mode, str):
            raise ValueError(f'Timer mode must be in quotes (a string). e.g. "on the 5 seconds"')

        # check if timer is in timer_jobs
        if timer_mode not in list(self.timer_jobs.keys()):
            raise ValueError(f'Attempted to use non-timer: "{T_mode}", available timers are: {list(self.timer_jobs.keys())}')

        #### validate function
        #if not isinstance(func, types.FunctionType):
        if not hasattr(func, '__call__'):
            raise ValueError(f'Timer\'s function must be a function object, it should not have () on the end. e.g. myfunction, not myfunction()')

        if timer_mode[:2] == 'on' or timer_mode[:5] == 'every':
            #### on and every can be directly placed in timer_jobs
            self.timer_jobs[timer_mode].append(func)


        elif timer_mode == 'schedule':
            #### check format of the schedule time
            # is 24 hour format string
            if not isinstance(mark, str) or len(mark) != 5:
                raise ValueError(f'Schedule time ({mark}) must be a string in 24 hour format. e.g. "07:02"')

            # validate timer hours and minutes are formatted correctly
            try:
                # validate hours
                int(mark[:2])
            except ValueError:
                raise ValueError(f'Schedule time format issue, are hours in 24 hour format? e.g. "07:02"')
            try:
                # validate minutes
                int(mark[-2:])
            except ValueError:
                raise ValueError(f'Schedule time ({mark}) format issue, are minutes two digits? e.g. 17:02')
            
            #### add schedule timer to timer_jobs
            if 0 <= int(mark[:2]) < 24 and 0 <= int(mark[-2:]) < 60:
                self.timer_jobs['schedule'].append((func, mark))
            else:
                # error caused by hours or minutes not within range
                raise ValueError(f'Scheduled time ({mark}) not in 24 hour format HH:MM')
            
        else:
            # error for not being on, every, or schedule (this should never happen)
            raise ValueError(f'Attempted to use non-timer: {T_mode}')


class Chronograph:
    def __init__(self, jobs, local_time_zone='UTC', poll_millis=100, wait_to_run=False):
        '''Chronograph object runs timers
        Standard Polling is .1 seconds
        every poll timers run in primary thread
        every second timers run in thread1
        A separate thread (chrono_thread) is created for all other timers
        chrono_thread has a lock so only one can run at a time
        If chrono_thread is locked, the next chrono_thread will be skipped
        This effectively gives every_poll timers priority
        '''
        # self.jobs are all of the timers
        # it is a dictionary created by the Timers class
        self.jobs = jobs

        # polling time in milliseconds
        self.POLL_MILLIS = poll_millis  
        self.local_time_zone = local_time_zone

        if wait_to_run == False:
            self.run_timers()



    def run_timers(self, debug=False):
        #### set up last varables
        (last_hour, last_minute, last_second) = get_time(self.local_time_zone)
        last_milli = 0
        start_milli = time() * 1000

        # this only allows one thread to run at a time
        self.thread_lock = False
        self.thread1_lock = False

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
            self.thread1_jobs = []

            if (milli - last_milli) >= self.POLL_MILLIS:
                HHMMSS = get_time(self.local_time_zone)

                # note: every poll jobs are run after thread_jobs is
                # sent off (see below)

                #### Second ####
                if last_second != HHMMSS[2]:
                    #### Every second jobs ####
                    for job in self.jobs['every second']:
                        #job()
                        self.thread1_jobs.append(job)
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

                #### Run all jobs but poll in separate threads
                # self.thread1 has the every second jobs
                if self.thread1_lock == False:
                    chrono_thread1 = threading.Thread(target=self.run_thread1_jobs, daemon=True)
                    chrono_thread1.start()
                else:
                    if self.thread1_jobs == []:
                        pass
                    else:
                        if debug == True: print('>>> chrono_thread1 over-run, missed a 1 sec <<<')
                        pass

                # self.thread has all other jobs
                if self.thread_lock == False:
                    chrono_thread = threading.Thread(target=self.run_thread_jobs, daemon=True)
                    chrono_thread.start()
                else:
                    if self.thread_jobs == []:
                        pass
                    else:
                        if debug == True: print('>>> chrono_thread over-run, missed jobs call <<<')
                        pass


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

    def run_thread1_jobs(self):
        self.thread1_lock = True
        for job in self.thread1_jobs:
            job()
        self.thread1_lock = False
        



def job_function_tester(jobs):
    '''runs each function in the timer_jobs dictionary and 
    returns the run time required for each'''
    time_results = {}
    print('\n\n Evaluate each functions time to run:')
    print(f'function name                run time')
    def elapsed_time(millis):
        if millis < 1000:
            return f'{millis:.3f} milliseconds'
        else:
            return f'{(millis/1000):.2f} seconds'

    for key, details in jobs.items():
        for job in details:
            # check for function to find on and every timers
            if isinstance(job, types.FunctionType):
                print('\n')
                start_milli = (time() * 1000) 
                job()
                total_milli = ((time() * 1000) - start_milli)
                print(f'{job.__name__}: {elapsed_time(total_milli)}')

            # check for tuple to find schedule timers
            elif isinstance(job, tuple):
                print('\n')
                start = timeit.timeit()
                job[0]()
                end = timeit.timeit()
                print(f'{job[0].__name__}: {elapsed_time(total_milli)}')

            else:
                print('\nimproper timer')



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





