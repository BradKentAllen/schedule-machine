## README

**schedule_machine** is a general purpose timer package for scheduling functions to be run at specific intervals or times.  

Python can pose a number of challenges when running timed processes on machines.  With the appropriate warnings though, a simple timer with a well thought out control system can control machines with timing of 100 millisecond intervals and where occassionally lost functions are not disastrous.  Understanding how schedule_machine works will allow you to perform data acquisition, timing tasks, and machine control with reasonable reliability.

**WARNING - Python is not a great real-time control:** Python has serious limitations for real-time processes.  It is not true multi-threading and has a garbage collector which can be called at any time that will block all threads.  This will disrupt the process.  

**WARNING - YOUR CODE HAS TO WORK:** Timing systems are notorious hiders of bugs and glitches.  Significat testig is required to validate their reliability and, even then, they frequently are victims of oddball issues such as daylight savings time errors.  **DO NOT USE FOR SAFETY-CRITICAL or LIFE-CONTROLLING PROCESSES.**



### Attributes

* simple API with timers defined as tuples (e.g. create_timer('every second', <my_func>))
* operates on local time
* timer is run every 100 milliseconds (.1 seconds), referred to as a poll.
* threading is used to give the 'every poll' timers priority
  * 'every poll' timers run sequentially in the primary thread.  As such, they are a blocker.  If the total process time for all  'every poll' timers exceeds 100 milliseconds then it will push out the primary thread.  Eventually it will miss a poll and less than 10 polls will occur in a second.
  * All other timers are run in a separate thread.  A thread lock limits these timers to a single thread.  If the chrono_thread (all non-every poll timers) is still running when a second chrono_thread is called, the second one will be ignored.



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

'schedule' timers have an additional parameter, the time they are to be called.  This time must be a string in 24 hour format 'HH:MM'.

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







```

#### timer parameters
func:		# function
T_mode:		# Timer mode
mark:		# optional, HH:MM, or HH:MM:SS
```





```
from schedule_machine.chrono import Chronograph, Timers

#### Create Timers
# create schedule_jobs to create timers and place in schedule_maker.timer_jobs
schedule_maker = Timers()

schedule_maker.create_timer('every poll', demo_job)
schedule_maker.create_timer('schedule',  demo_job, '17:52')


#### Instantiate the Chronograph
# create chrono with list of timer_jobs and time zone
chrono = Chronograph(schedule_maker.timer_jobs, 'US/Pacific')

# 'US/Aleutian', 'US/Hawaii', 'US/Alaska', 'US/Arizona', 'US/Michigan'
# 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern', 'UTC'

#### run the Chronograph timers
chrono.run_timers()
```



