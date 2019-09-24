=======================
Bot Actions - Internal Page
=======================

===========
Description
===========

This web-project will be builded using this stack:

1. Bootstrap

2. Flask Microframework (python)

3. DynamoDB


The finally of this "internal" web-page is for inform to the users of 
the bot, what are the activities related over the using it.

======================
Public Subdomain
======================

**botactions.systemagency.com**: List of all of the mother agencies where the Scouting bot (v1 & v2) has access

================================
Instructions for Run the server
================================

0. CLone the repo. 

    $ git clone git@github.com:realFranco/Bots-Actions.git

1. Install the dependecies. (Previusly you need to have 
    python3 installed on your system.)

    $ pip3 install -r requeriments.txt

2. Run the web-server.

    $ python3 app.py

2.1 If you need to close the terminal where the script it is running,
    do this.

    $ nohup python3 app.py &
    This will output a numbers, that becomes in the pID of the script.

    Actually you can find that process using this command:

    $ ps -fa | grep python

    And kill it using:

    $ kill -9 pID (where pID is the number returned on after 
    nohup or the ps command).

===========================================================
If your pourpose it is run this under a subdomain, do this:
===========================================================

0. Step initial

    $ nohup python3 app.py &
