import click
import itertools
import threading
import time

def _style_unimportant(string):
    return click.style(string, fg='white', dim=True)

def _style_up(string):
    return click.style(string, fg='bright_magenta', bold=True)

def _style_ynab(string):
    return click.style(string, fg='bright_blue', bold=True)

def _style_highlight(string):
    return click.style(string, fg='yellow')

def _style_success(string):
    return click.style('✓ ', fg='green') + string

def _style_error(string):
    return click.style('✗ ', fg='red') + string

def _style_fatal(string):
    return click.style('✗ ', fg='bright_red') + click.style(string, fg='red')

def _style_header(string,):
    return click.style('» ', fg='blue') + click.style(string, bold=True)


class EchoInProgress:
    def __init__(self, in_progress_message, level=0):
        self.in_progress_message = _style_unimportant(in_progress_message)
        self.spinner_cycle = itertools.cycle(u'⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏')
        self.stop = threading.Event()
        self.spin_thread = None
        self.level = level

    def _spin(self):
        while not self.stop.is_set():
            next_char = next(self.spinner_cycle)
            click.echo(f'\r{4*self.level*" "}{next_char} {self.in_progress_message}', nl=False)
            time.sleep(0.05)
    
    def _stop(self):
        assert self.spin_thread is not None
        self.stop.set()
        self.spin_thread.join()

    def start(self):
        self.spin_thread = threading.Thread(target=self._spin)
        self.spin_thread.start()
        return self
    
    def finish(self, message):
        self._stop()
        click.echo(f'\r{4*self.level*" "}{message: <{4*self.level + len(self.in_progress_message) + 11}}')
    
    def pause(self):
        self._stop()
        click.echo(f'\r{4*self.level*" "}⠪ {self.in_progress_message}')


class EchoManager:
    def __init__(self):
        self.current_level = 0
        self.in_progress = None
    
    def _level_echo(self, string):
        click.echo(4*self.current_level*" " + string)

    def section(self, header):
        self._level_echo(_style_header(header))
        self.current_level += 1
    
    def end_section(self):
        click.echo()
        self.current_level -= 1
    
    def start_task(self, message):
        if self.in_progress is not None:
            raise RuntimeError('Another task is already in progress')
        self.in_progress = EchoInProgress(message, level=self.current_level)
        self.in_progress.start()
    
    def task_success(self, message):
        if self.in_progress is None:
            raise RuntimeError('No task is currently in progress')
        self.in_progress.finish(_style_success(message))
        self.in_progress = None
    
    def task_error(self, message):
        if self.in_progress is None:
            raise RuntimeError('No task is currently in progress')
        self.in_progress.finish(_style_error(message))
        self.in_progress = None
    
    def success(self, message):
        self._level_echo(_style_success(message))
    
    def error(self, message):
        self._level_echo(_style_error(message))
    
    def fatal(self, message):
        if self.in_progress is not None:
            self.in_progress.pause()
        self.current_level = 0
        click.echo()
        click.echo(_style_fatal(message))