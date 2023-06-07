#!/usr/bin/env python3
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''

 Description:

    Library of utils to run commands on NIOS console via SSH
    Can also be run as interactive CLI script

 Requirements:
   Python 3.6+ with pexpect

 Author: Chris Marrison

 Date Last Updated: 20230606

 Todo:

 Copyright (c) 2023 Chris Marrison / Infoblox

 Redistribution and use in source and binary forms,
 with or without modification, are permitted provided
 that the following conditions are met:

 1. Redistributions of source code must retain the above copyright
 notice, this list of conditions and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright
 notice, this list of conditions and the following disclaimer in the
 documentation and/or other materials provided with the distribution.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.

'''
__version__ = '0.1.1'
__author__ = 'Chris Marrison'
__author_email__ = 'chris@infoblox.com'

import sys
import logging
import argparse
import configparser
import pexpect


# Global Variables

def parseargs():
    '''
    Parse Arguments Using argparse

    Parameters:
        None

    Returns:
        Returns parsed arguments
    '''
    parse = argparse.ArgumentParser(description='NIOS Remote Comsole Access')
    parse.add_argument('-c', '--config', type=str, default='gm.ini',
                        help="Overide Config file")
    parse.add_argument('-m', '--member', type=str, required=True,
                        help="Name or IP of Grid Member")
    parse.add_argument('-C', '--command', type=str, required=True,
                        help="show command or promote_master")
    parse.add_argument('-p', '--promote', action='store_true', 
                        help="Promote GMC to GM")
    parse.add_argument('-D', '--delay', type=int, default=0,
                        help="Set delay on promotion")
    parse.add_argument('-d', '--debug', action='store_true', 
                        help="Enable debug messages")

    return parse.parse_args()


def setup_logging(debug=False, usefile=False):
    '''
     Set up logging

     Parameters:
        debug (bool): True or False.

     Returns:
        None.

    '''

    if debug:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s')
    else:
        if usefile:
            # Full log format
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s %(levelname)s: %(message)s')
        else:
            # Simple log format
            logging.basicConfig(level=logging.INFO,
                                format='%(levelname)s: %(message)s')

    return


def read_ini(ini_filename):
    '''
    Open and parse ini file

    Parameters:
        ini_filename (str): name of inifile

    Returns:
        config :(dict): Dictionary of BloxOne configuration elements

    '''
    # Local Variables
    cfg = configparser.ConfigParser()
    config = {}
    ini_keys = ['gm', 'api_version', 'valid_cert', 'user', 'pass' ]

    # Attempt to read api_key from ini file
    try:
        cfg.read(ini_filename)
    except configparser.Error as err:
        logging.error(err)

    # Look for NIOS section
    if 'NIOS' in cfg:
        for key in ini_keys:
            # Check for key in BloxOne section
            if key in cfg['NIOS']:
                config[key] = cfg['NIOS'][key].strip("'\"")
                logging.debug('Key {} found in {}: {}'.format(key, ini_filename, config[key]))
            else:
                logging.warning('Key {} not found in NIOS section.'.format(key))
                config[key] = ''
    else:
        logging.warning('No NIOS Section in config file: {}'.format(ini_filename))
        config['gm'] = ''

    return config


def run_console_command(member, user='admin', pwd='infoblox', cmd=''):
    '''
    Generic run command to capture output
    '''
    ssh_command = f"ssh {user}@{member}"
    ssh_newkey = 'Are you sure you want to continue connecting (yes/no/[fingerprint])?'
    login_failed = 'Permission denied, please try again.'
    prompt = '>'

    if cmd:
        logging.debug(f'Executing ssh command: {ssh_command}')
        ssh = pexpect.spawn(ssh_command)

        response = ssh.expect([ ssh_newkey, "password:", pexpect.EOF, pexpect.TIMEOUT ])
        if response == 0:
            logging.debug('New ssh key being accepted.')
            ssh.sendline('yes')
            response = ssh.expect([ ssh_newkey, "password:", pexpect.EOF, pexpect.TIMEOUT ])
        elif response == 1:
            ssh.sendline(pwd)
        else:
            raise Exception(f'ssh connection issue: {ssh.before}')

        response = ssh.expect([ login_failed, prompt ])
        if response == 0:
            logging.error(f'Login failed')
        elif response == 1:
            logging.debug(f'Login successful, executing command: {cmd}')
            ssh.sendline(cmd)
            ssh.expect(prompt)
            output = ssh.before.decode()
            ssh.close()
    else:
         output = 'No command specified, run aborted.'

    return output


def set_prommote_master(gmc, user='admin', pwd='infoblox', delay=0):
    '''
    Remotely execute set promote_master

    Parameters:
        gmc(str): Hostname/IP address of GMC
        user(str): Administrator username
        pwd(str): Administrator password
        delay(int): Member notification delay
    
    Returns:
        bool
    '''
    status = False
    ssh_command = f"ssh {user}@{gmc}"
    ssh_newkey = 'Are you sure you want to continue connecting (yes/no/[fingerprint])?'
    login_failed = 'Permission denied, please try again.'
    member_delay = 'Do you want a delay between notification to grid members? (y or n):'
    prompt = '>'

    # Spawn ssh
    ssh = pexpect.spawn(ssh_command)
    response = ssh.expect([ ssh_newkey, "password:", pexpect.EOF, pexpect.TIMEOUT ])
    if response == 0:
        ssh.sendline('yes')
        response = ssh.expect([ ssh_newkey, "password:", pexpect.EOF, pexpect.TIMEOUT ])
    elif response == 1:
        ssh.sendline(pwd)
    else:
        raise Exception(f'ssh connection issue: {ssh.before}')
    
    response = ssh.expect([ login_failed, prompt, pexpect.EOF, pexpect.TIMEOUT ])
    if response == 0:
        status = False
        logging.error(f'Login failed')
    elif response == 1:
        logging.debug('Login successful, sending set promote_master')
        ssh.sendline('set promote_master')

        response = ssh.expect([ member_delay, prompt, pexpect.EOF, pexpect.TIMEOUT ])
        if response == 0:
            if delay == 0:
                logging.debug('No delay set')
                ssh.sendline('n')
            else:
                logging.debug(f'Setting member delay to {delay}')
                ssh.sendline('y')
                ssh.expect('Set delay time for notification to grid member? [Default: 30s]')
                ssh.sendline(str(delay))
            
            logging.debug('Confirming promotion')
            ssh.expect('Are you sure you want to do this? (y or n):')
            ssh.sendline('y')
            ssh.expect('(y or n):')
            ssh.sendline('y')
            output = ssh.before.decode()
            logging.debug(output)
            status = True
        elif response == 1:
            status = False
            logging.error('Promotion failed')
            output = ssh.before.decode()
            logging.debug(f'{output}')
        else:
            raise Exception(f'ssh connection issue: {ssh.before}')

    else:
        status = False
        logging.error(f'Session issue')
        raise Exception(f'ssh connection issue: {ssh.before}')

    ssh.close()

    return status


def main():
    '''
    Core logic
    '''
    exitcode = 0
    commands = [ 'shutdown', 'reboot' ]

    # Parse CLI arguments
    args = parseargs()
    inifile = args.config

    setup_logging(debug=args.debug)

    # Read inifile
    config = read_ini(inifile)

    if args.command == 'promote_master':
        if args.promote:
            success = set_prommote_master(args.member,
                                        user=config.get('user'),
                                        pwd=config.get('pass'),
                                        delay=args.delay)
            if success:
                logging.info('Promotion in progress')
            else:
                logging.info(f'Failed to promote GMC {args.member}')
                exitcode = 1
        else:
            logging.warning(f'Safeguard prevented promotion')
            command = '$ ' + ' '.join(sys.argv) + " --promote"
            print(f'To activate promotion use: {command}')
            exitcode = 1
    
    elif 'show' in args.command:
        output = run_console_command(args.member,
                                  user=config.get('user'),
                                  pwd=config.get('pass'),
                                  cmd=args.command)
        print(output)

    elif args.command in commands:
        output = run_console_command(args.member,
                                  user=config.get('user'),
                                  pwd=config.get('pass'),
                                  cmd=args.command)
        print(output)

    else:
        logging.error(f'Command {args.command} not supported')
        exitcode = 1

    return exitcode


### Main ###
if __name__ == '__main__':
    exitcode = main()
    exit(exitcode)
## End Main ###