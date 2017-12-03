*******
Charlie
*******

:Author: Samuel R. Mathias
:Contact: samuel.mathias@gmail.com
:Web site: http://www.srmathias.com
:Github: http://github.com/sammosummo/Charlie
:Version: 0.2.0

Introduction
============

Charlie is a free, open-source, cross-platform neurocognitive test battery
written in Python. It is currently being used to collect data for a project
from our laboratory, but may be used freely by all. Although all of the tests
are functional and there are some nice features (see below), Charlie is still
under development. I'm continually adding more features and fixing bugs as they
arise.

What works
==========

* Charlie currently contains 22 neurocognitive tests, with more planned. Each
  test has a docstring with citations; have a look in the `charlie/tests`
  folder to see what's available.

* Data are recorded after each trial. This means that you have access to
  trial-specific data rather than just the summary data. It also means that the
  tests are resumable; that is, the progress of each subject is retained. This
  prevents a subject from performing a test twice, and allows them to pick up
  where they left off, if a test gets interrupted.

* Summary statistics are automatically computed after a subject completes a
  test. All of the data (summary and trial-specific) are stored within various
  formats, including within human-readable CSVs, "pickled" Python objects, and
  within an SQLite database.

* Tests can be run individually or in batches.

* Because Charlie is written in Python, it is easy to modify or add new tests.

* Charlie is cross-platform. So long as your system can run Python 2.7 (most
  can), you can use Charlie.

What sort-of works
==================

* Charlie can administer self-report questionnaires prior to a test or battery
  of tests. This feature is functional, but has not been debugged as
  extensively tested as the cognitive tests.

* At the end of a test or batch, the data stored locally can be automatically
  backed up to a remote server via sftp. This feature is currently very crude.
  I plan to refine it and add more backup options in the future.

What doesn't work (i.e., future plans)
======================================

* Charlie is written in Python and uses various third-party packages. In the
  future, I plan to create a stand-alone version.

* Charlie is a command-line program. It has a GUI, but I haven't figured out
  how to make it work with tests run in batch mode. (This has proven to be a
  great source of frustration for me.)

* Charlie isn't currently a regular Python package, so isn't installable via
  `pip`. I haven't yet decided whether to do this.

Installation instructions (Windows)
===================================

Charlie uses Python as a number of its third-party pacakges: `numpy`, `scipy`,
`pandas`, `pygame`, `web.py`, `paramiko`, and `pyside`/`pyqt`. If you are an
experienced Python user, simply install all of these in whatever way you
prefer. If you are not a Python user and are on Windows, do the following:

1. Download and install Miniconda from here: https://repo.continuum.io/miniconda/Miniconda-latest-Windows-x86.exe

2. Open a command prompt, and type the following commands, one by one:
   ::
      conda update conda
      conda install pip numpy scipy pandas pyside paramiko
      pip install web.py

3. Download and install Pygame: http://pygame.org/ftp/pygame-1.9.2a0.win32-py2.7.msi

4. Download Charlie: https://github.com/sammosummo/Charlie/archive/master.zip

Installation instructions (Mac)
===============================

If you are on Mac, do the following instead:

1. Download the Miniconda bash script: https://repo.continuum.io/miniconda/Miniconda-latest-MacOSX-x86_64.sh

2. Execute the script by opening a terminal window, setting the current
   directory to your downloads folder using the `cd` command, and typing the
   line:
   ::
      sudo bash Miniconda-latest-MacOSX-x86_64.sh

3. Restart your terminal and type these commands:
   ::
      conda update conda
      conda install pip numpy scipy pandas pyside paramiko binstar
      pip install web.py
      ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
      brew install sdl sdl_ttf sdl_image sdl_mixer portmidi
      conda install -c https://conda.binstar.org/quasiben pygame

4. Download Charlie: https://github.com/sammosummo/Charlie/archive/master.zip

Running Charlie
===============

If you downloaded the zip file (step 4 above), unzip it somewhere on your
computer, it shouldn't matter where. Then open a command window/terminal, and
`cd` to the `Charlie-master/charlie` directory. There should be a file called
`run.py` in that directory.

Tests and batches are run from the command line by executing the `run.py`
script. Options are supplied Unix-style. To get a list of all available
options, type:
::
   python run.py -h
The help string should be clear, but if you have any difficulties, feel free to
drop me an email.
