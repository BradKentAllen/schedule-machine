## README

###### schedule_machine

package:  schedule-machine

class:  Chronograph

```

#### timer parameters
func:		# function
T_mode:		# Timer mode
mark:		# optional, HH:MM, or HH:MM:SS
```

```
def demo_job:
	print('this is a demo job')
	
maker.create_timer('every poll', demo_job)
maker.create_timer('every second', demo_job)
maker.create_timer('on the 5 second', demo_job)
maker.create_timer('on the 15 second', demo_job)
maker.create_timer('on the 30 second', demo_job)

maker.create_timer('every minute', demo_job)
maker.create_timer('on the 5 minute', demo_job)
maker.create_timer('on the 15 minute', demo_job)
maker.create_timer('on the 30 minute', demo_job)

maker.create_timer('every hour', demo_job)

maker.create_timer('schedule', test_function, '17:52')
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



