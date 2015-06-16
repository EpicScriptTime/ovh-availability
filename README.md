ovh-availability
================

[![Travis](https://img.shields.io/travis/EpicScriptTime/ovh-availability.svg)](https://travis-ci.org/EpicScriptTime/ovh-availability)
[![Release](https://img.shields.io/github/release/EpicScriptTime/ovh-availability.svg)](https://github.com/EpicScriptTime/ovh-availability/releases)
[![MIT License](https://img.shields.io/badge/license-MIT-8469ad.svg)](https://tldrlegal.com/license/mit-license)

Simple python script that sends a SMS notification when an OVH server offer becomes available.

Requirements
------------

* Python3, `pip` and `virtualenv` installed
* Twilio account credentials (for SMS)

Setup
-----

1. Clone this repository
2. Setup the virtualenv and activate it
4. Install the requirements
3. Configure the settings to fit your needs

Crontab
-------

Install this crontab to run the script every minute:

    * * * * * /path/to/env/bin/python /path/to/ovh-availability/ovhavailability/check.py --sold-out --quiet
