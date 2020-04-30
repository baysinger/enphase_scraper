# enphase_scraper
Downloads per-inverter data from your solar array.

These scripts will start a session with the EnlightenManager website and download
per-inverter data for the date range specified.

Note: If you only have access to MyEnlighten, but not EnlightenManager, this might not
work. I don't have the ability to test that scenario. I hope someone can test that for
me! (You can reach me by openning an issue.)

This tool is made up of three scripts:
* login.py
* logout.py
* getstats.py

Each script supports the -h and --help command line arguments to get usage information.
They also all support the --statedir argument to override the default state directory.
If not specified, the state directory will default to "~/.enphase_scraper".

## login.py
Starts a session.

This script interactively asks the user for credentials. It then starts a session on
the Enlighten website and stores the associated cookies for use by the other scripts.

Note: The username and password are not stored.

## logout.py
Ends the session.

## getstats.py
Gets per-inverter stats.

This is the main script. It will get the per-inverter stats for the date range specified,
and will save it in a subdirectory of the current directory named "data".

If invoked without any arguments, it will interactively prompt the user for the system ID,
start date, and number of days. These parameters can also be passed on the command line,
with "--sys", "--date", and "-n", repectively. If all three are passed via the command line,
the tool with run non-interactively.

Note: This tool contains some artificial delays so as to not hammer the server too hard.
Please consider carefully before changing the delays!
