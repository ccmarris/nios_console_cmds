=============================
NIOS Remmote Console Commands
=============================

| Version: 0.1.2
| Author: Chris Marrison
| Email: chris@infoblox.com

Description
-----------

Demo NIOS script to execute remote (ssh) console commands using pexpect.
The script allows for the execution of show commands, shutdown/reboot, and
set promote_master.

It is implemented as a library or for use as a CLI that can be called, for
example, via the ansible command module.


Prerequisites
-------------

Python 3.7+


Installing Python
~~~~~~~~~~~~~~~~~

You can install the latest version of Python 3.x by downloading the appropriate
installer for your system from `python.org <https://python.org>`_.

.. note::

  If you are running MacOS Catalina (or later) Python 3 comes pre-installed.
  Previous versions only come with Python 2.x by default and you will therefore
  need to install Python 3 as above or via Homebrew, Ports, etc.

  By default the python command points to Python 2.x, you can check this using 
  the command::

    $ python -V

  To specifically run Python 3, use the command::

    $ python3


.. important::

  Mac users will need the xcode command line utilities installed to use pip3,
  etc. If you need to install these use the command::

    $ xcode-select --install

.. note::

  If you are installing Python on Windows, be sure to check the box to have 
  Python added to your PATH if the installer offers such an option 
  (it's normally off by default).


Modules
~~~~~~~

Non-standard modules:

    - pexpect 

Complete list of modules::

  import logging
  import sys
  import argparse
  import configparser
  import pexpect


Installation
------------

The simplest way to install and maintain the tools is to clone this 
repository::

    % git clone https://github.com/ccmarris/nios_console_cmds


Alternative you can download as a Zip file.


Basic Configuration
-------------------

The script utilise a the same gm.ini file format as the demo nios api scripts
for simplicity. However, since this connects to a specified member via remote
console, this is used only for administrator credentials.


gm.ini
~~~~~~~

The *gm.ini* file is used by the scripts to define the details to connect to
to Grid Master. A sample inifile is provided and follows the following 
format::

  [NIOS]
  gm = '192.168.1.10'
  api_version = 'v2.12'
  valid_cert = 'false'
  user = 'admin'
  pass = 'infoblox'


You can use either an IP or hostname for the Grid Master. This inifile 
should be kept in a safe area of your filesystem. 

Use the --config/-c option to override the default ini file.


Usage
-----

The script support -h or --help on the command line to access the options 
available::

  % ./nios_console_cmds.py --help 
  usage: nios_console_cmds.py [-h] [-c CONFIG] -m MEMBER -C COMMAND [-p] [-D DELAY] [-d]

  NIOS Remote Comsole Access

  optional arguments:
    -h, --help            show this help message and exit
    -c CONFIG, --config CONFIG
                          Overide Config file
    -m MEMBER, --member MEMBER
                          Name or IP of Grid Member
    -C COMMAND, --command COMMAND
                          show command or promote_master
    -p, --promote         Promote GMC to GM
    -D DELAY, --delay DELAY
                          Set delay on promotion
    -d, --debug           Enable debug messages


nios_console_cmds
~~~~~~~~~~~~~~~~~


Examples
--------

Run a show command against a Grid Member::

  % ./nios_console_cmds.py --config gm.ini -m 10.10.10.10 --command 'show status'


Enable debug::

  % ./nios_console_cmds.py --config gm.ini -m 10.10.10.10 --command 'show status' --debug


Reboot member::

  % ./nios_console_cmds.py --config gm.ini -m 10.10.10.10 --command 'reboot' --yes

.. note::

    Where a command needs a confirmation use --yes to send a confirmation to 
    proceed. Otherwise a no response will be sent in response to the command.


    
Promoting a GMC
---------------

Promoting a GMC to GM, should always be performed after a concious decision
has been made to perform a promotion. The intention here is not to allow for
a fully automated promotion of a GMC.

To use the promotion function, a specific command *promote_master* is used.
An additional safeguard must also be used to enable the command by adding the
*--promote* option.

Examples::

  % ./nios_console_cmds.py -c ~/configs/localgm.ini -m 10.101.101.101 -C 'promote_master'
  WARNING:root:Safeguard prevented promotion


  % ./nios_console_cmds.py -c ~/configs/localgm.ini -m 10.101.101.101 -C 'promote_master' --promote  
  ERROR: Promotion failed
  ERROR:  set promote_master
  Unable to promote:  This member is already the grid master


  % ./nios_console_cmds.py -c ~/configs/localgm.ini -m 10.101.101.101 -C 'promote_master' --promote  



License
-------

This project is licensed under the 2-Clause BSD License
- please see LICENSE file for details.


Aknowledgements
---------------

Thanks to Alex Del Rio for bringing the use case and testing.
