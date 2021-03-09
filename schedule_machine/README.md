## README

**schedule_machine** is a general purpose timer package for scheduling functions to be run at specific intervals or times.  It is useful for:

* Data acquisition, where rates are 10 hz or less
* Environment control such as for terrariums, animal habitats, etc.
* Light and appliance controls
* Surface-based drones such as slow moving wheeled and tracked vehicles, boats, model boats, etc.
* Testing machine controls
* Working with Raspberry Pi GPIO (we highly recommend using gpiozero)

Python can pose a number of challenges when running timed processes on machines.  With the appropriate warnings though, a simple timer with a well thought out control system can control machines with timing of 100 millisecond intervals and where occassionally lost functions are not disastrous.  Understanding how schedule_machine works will allow you to perform data acquisition, timing tasks, and machine control with reasonable reliability.

**WARNING - Python is not the best real-time machine control:** Python has limitations for real-time processes.  It is not true multi-threading and has a garbage collector which can be called at any time and will block all threads.  This will disrupt the process.  

**WARNING - YOUR CODE HAS TO WORK:** Timing systems are notorious hiders of bugs and glitches.  Significat testig is required to validate their reliability and, even then, they frequently are victims of oddball issues such as daylight savings time errors.  **DO NOT USE FOR SAFETY-CRITICAL or LIFE-CONTROLLING PROCESSES.**



### Attributes

* simple API with timers defined as tuples (e.g. create_timer('every second', <my_func>))
* operates on local time
* timer is run every 100 milliseconds (.1 seconds), referred to as a poll.
* threading is used to give the 'every poll' timers priority
  * 'every poll' timers run sequentially in the primary thread.  As such, they are a blocker.  If the total process time for all  'every poll' timers exceeds 100 milliseconds then it will push out the primary thread.  Eventually it will miss a poll and less than 10 polls will occur in a second.
  * All other timers are run in two separate threads.  One has timers that are called every second.  All other timers are in a second thread.  Thread locks limits these timers to a single thread.  If the every second thread is running when the next every second is called, the next one will be ignored.  The same is true for the thread with all other timers.
  * Every second timers operate much like every poll.  So if they total to more than a second in operation time, the next every second action will be ignored.  Since python does not parallel process, these timers will affect each other across the threads.



## Installation

```
pip install schedule_machine
pip3 install schedule_machine

# on Raspberry Pi using GPIO, install as root/super user:
sudo pip3 install schedule_machine
```



## Quick Start

Every timer must have an associated function.

```
#### import the Timers and Chronograph classes
from schedule_machine import Timers, Chronograph

#### instantiate a maker app to create timers
maker = Timers()

#### define a function to use in the timer
def sample_function():
	return 'this is my sample, scheduled function'
	
#### create the timer
# note the format of (<timer mode>, <function object>)
# the function object is passed without ()
maker.create_timer('every second', sample_function)

#### instantiate the chronograph
# pass the dictionary of timers created by your maker
# designate the timezone.
# timer will start running (see below for delaying start)
Chronograph(maker.timer_jobs, 'US/Pacific')
```



### Timers

Note that each timer has the format (<timer mode>, <function>)

**timer mode** must be a string (e.g. 'every second') and exactly match one of the 11 timers below.

**function** must be an already created function and passed as a function object without brackets ()

```
def demo_job:
	print('this is a demo job')

# will run every 100 milliseconds (polling)
maker.create_timer('every poll', demo_job)

# will run every second
maker.create_timer('every second', demo_job)

# will run on specific times during a minute
maker.create_timer('on the 5 second', demo_job)
maker.create_timer('on the 15 second', demo_job)
maker.create_timer('on the 30 second', demo_job)

# will run each minute on the 00 seconds
maker.create_timer('every minute', demo_job)

# will run on specific minutes durin an hour
maker.create_timer('on the 5 minute', demo_job)
maker.create_timer('on the 15 minute', demo_job)
maker.create_timer('on the 30 minute', demo_job)

# will run each hour on the 00 minutes
maker.create_timer('every hour', demo_job)

# will run at a specific local time during the day
maker.create_timer('schedule', test_function, '17:52')
```



### 'schedule' timers

'schedule' timers call a function at a specific time.  They have an additional parameter, the time they are to be called.  This time must be a string in 24 hour format 'HH:MM'.

```
#### examples of good schedule timers
maker.create_timer('schedule', test_function, '07:00')
maker.create_timer('schedule', test_function, '23:30')

#### examples of bad timer calls
maker.create_timer('schedule', test_function(), '17:52')  # function has ()
maker.create_timer('schedule', test_function, '6:52') # not in HH:MM format
maker.create_timer('schedule', test_function, '24:00')	# midnight is 00:00
```



### Time Zones

You can use any time zone included in the python pytz library (XXXX - link to library list of timezones).  XXXX - how to use UTC.

Some examples of US timezones are:

```
# 'US/Aleutian', 'US/Hawaii', 'US/Alaska', 'US/Arizona', 'US/Michigan'
# 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern'
```



### Delay Starting the Chronograph

You may wish to instantiate the Chronograph object then either wait or pass it before starting.  You can do that as follows:

```
# create chrono object but indicate wait_to_run
chrono = Chronograph(maker.timer_jobs, 'US/Pacific', wait_to_run=True)

# start chrono directly
chrono.run_timers()
```



## Live Demo of Various Timers

This demo allows you to play around with how various timer functions interact.  It is set up initially with a long enough sleep in the 'every 15 second' function to cause the next chrono_thread to be called before the first one is complete.  The debug will show when this happens.

```
from schedule_machine.chrono import Chronograph, Timers, get_time_stamp, job_function_tester

from time import sleep

global poll_count
poll_count = 0

def poll_test():
	global poll_count
	print(poll_count, end='')
	poll_count +=1

def poll_test2():
	print('-', end='')
	sleep(.07)

def second_function():
	global poll_count
	print(get_time_stamp('US/Pacific'))
	poll_count = 0

def five_second_function():
	print('5 second function')

def fifteen_second_function():
	print('start 15 second function')
	sleep(10)
	print('end 15 second function')

def minute_function():
	print('minute function runs')

def test_function():
	print('this is the test function')

print('test run')

#### Create Timers
maker = Timers()

maker.create_timer('every poll', poll_test)
maker.create_timer('every poll', poll_test2)
maker.create_timer('every second', second_function)
maker.create_timer('on the 5 second', five_second_function)
maker.create_timer('on the 15 second', fifteen_second_function)
maker.create_timer('every minute', minute_function)

maker.create_timer('schedule', test_function, '17:32')

#### helper method to check function times
''' # explained below
job_function_tester(maker.timer_jobs)
exit()
'''

#### Run Chronograph
#Chronograph(maker.timer_jobs, 'US/Pacific')
chrono = Chronograph(maker.timer_jobs, 'US/Pacific', wait_to_run=True)

# 'US/Aleutian', 'US/Hawaii', 'US/Alaska', 'US/Arizona', 'US/Michigan'
# 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern'
chrono.run_timers(debug=True)
```



# Utilities

### Optimize Operation (job_function_tester)

A key step in optimizing a system of timers is understanding how long each called function takes.  A utility method in schedule_machine allows you to quickly get the processing time for each function.  Simply run job_function_tester(jobs) after creating timers using the Timer class.  The method is shown in context but commented out above, in the Live Demo. 

```
from schedule_machine.chrono import job_function_tester

'''
code to create timers here
'''

#### helper method to check function times
job_function_tester(maker.timer_jobs)
exit()
```



### get_time, get_time_stamp

If time information is needed in other aspects of your project you can access it using these two methods:

```
from schedule_machine.chrono import get_time, get_time_stamp

string_time_info = get_time(<time zone>)
string_time[0]	# hour as HH in 24 hour format
string_time[1]	# minute as MM
string_time[2]	# seconds as SS

time_stamp = get_time_stamp(<time zone>)  # returns time as string in HH:MM format

time_stamp = get_time_stamp(<time zone>, time_format='HMS')  # returns time as string in HH:MM:SS format
```

