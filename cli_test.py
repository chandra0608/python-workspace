https://zetcode.com/python/click/###
##simple click###########
import click

@click.command()
def hello():
    click.echo('Hello There')

if __name__ == '__main__':
    hello()

##########################################
import click

@click.command()
@click.option('--n', type=int, default=1)
def dots(n):
    click.echo('.' * n)

if __name__ == '__main__':
    dots()
##############################################
import click

@click.command()
@click.option('-s', '--string')
def output(string):
    click.echo(string)

if __name__ == '__main__':
    output()

####################################################
import click

@click.command()
@click.option("--name", prompt="Your name", help="Provider Your Name")
def hello(name):
    click.echo(f"Hello, {name}")

if __name__ == '__main__':
    hello()

#######################################################
##click.File type########
import click

@click.command()
@click.argument('file_name', type=click.File('r'))
@click.argument('lines', default=-1, type=int)
def head(file_name, lines):

    counter = 0

    for line in file_name:

        print(line.strip())
        counter += 1

        if counter == lines: 
            break


if __name__ == '__main__':
    head()
###########################################################
import click

@click.group()
def messages():
     pass

@click.command()
def generic():
    click.echo('Hello there')


@click.command()
def welcome():
    click.echo('Welcome')

messages.add_command(generic)
messages.add_command(welcome)

if __name__ == '__main__':
    messages()
    
########################################################   
import click

@click.group()
def cli():
  pass

@cli.command(name='gen')
def generic():
    click.echo('Hello There')

@cli.command(name='wel')
def welcome():
    click.echo('Welcome')

if __name__ == '__main__':
    cli()







