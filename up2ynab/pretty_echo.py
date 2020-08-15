import click

def unimportant(string):
    return click.style(string, fg='white', dim=True)

def up(string):
    return click.style(string, fg='bright_magenta', bold=True)

def ynab(string):
    return click.style(string, fg='bright_blue', bold=True)

def key(string):
    return click.style(string, fg='yellow')

def success(string):
    return click.style('Success: ', fg='green') + string

class EchoInProgress:
    def __init__(self, in_progress):
        self.in_progress = unimportant(in_progress)

    def start(self):
        click.echo(self.in_progress, nl=False)
        return self
    
    def finish(self, finish_string):
        click.echo(f'\r{finish_string: <{len(self.in_progress)}}')
