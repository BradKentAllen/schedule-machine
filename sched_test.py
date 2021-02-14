

from schedule_machine.chrono import Chronograph, Timers, get_time_stamp
from time import sleep

def second_function():
	print(get_time_stamp('US/Pacific'))

def test_function():
	print('5 second function')

def poll_test():
	print('*', end='')

def poll_test2():
	print('-', end='')
	sleep(.07)


print('test run')

#### Create Timers
maker = Timers()

maker.create_timer('every poll', poll_test)
maker.create_timer('every poll', poll_test2)
maker.create_timer('every second', second_function)
maker.create_timer('on the 5 second', test_function)

#### Run Chronograph
chrono = Chronograph(maker.timer_jobs, .1,'US/Pacific', False)


# 'US/Aleutian', 'US/Hawaii', 'US/Alaska', 'US/Arizona', 'US/Michigan'
# 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern', 'UTC'


chrono.run_timers()




