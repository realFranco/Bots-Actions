=======================
Bot Actions - Internal Page
=======================

===========
Description
===========

This web-project will be builded using this stack:

1. Bootstrap, jsGrid

2. Flask Microframework (python)

3. DynamoDB


The finally of this "internal" web-page is inform to the users of 
the bot, what are the activities related about their using.

======================
Public Subdomain
======================

**botactions.systemagency.com**: List of all of the mother agencies where the Scouting bot (v1 & v2) has access

================================
Instructions for Run the server
================================

0. Clone the repo. 

    $ git clone git@github.com:realFranco/Bots-Actions.git
    $ git clone https://github.com/realFranco/Bots-Actions.git

1. Install the dependecies. (Previusly you need to have 
    python3 installed on your system.)

    $ pip3 install -r requeriments.txt

2. Run the web-server.

    $ python3 app.py

2.1 If you need to close the terminal where the script it is running, do this.

    $ nohup python3 app.py &

This will output a numbers, that becomes in the pID of the script.

Actually you can find that process using this command:

    $ ps -fa | grep python

And kill it using:

    $ kill -9 pID 
    
Where pID is the number returned on after nohup or the ps command.

=================================================================
If your pourpose it is to host this web app into an ec2 instance
=================================================================

0. Step initial
    
    Open the port 80 & 443 for transfer data from the instance to the public requests.
    Initially, using just $ nohup sudo python3 app.py & can serve the app

1. Install this packeages
   
   $ sudo apt-get install nginx
   $ sudo ap-get install gunicorn3

1. Inside to the ec2 instance write this lines, and edit/create son configuration files, for run unicon like a service

    $ cd /etc/systemd/system/
    $ sudo nano gunicorn3.service

    [Unit]
    Description=Gunicorn service
    After=network.target
    
    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/bots/Bots-Actions
    ExecStart=/usr/bin/gunicorn3 --workers 1 --bind unix:flaskapp.sock -m 007 app:app    
    
    # Reload the deamon
    $ sudo systemctl daemon-reload

    # Start the service
    $ sudo service gunicorn3 start

    # Check the service
    $ sudo service gunicorn3 status

    $ cd /etc/nginx/sites-enabled/

    # Write the configuration file for the server
    $ sudo nano flaskapp
    
    server{
        listen 80;
        server_name 52.23.187.181; # or the public ipv4 that you have for the instance

        location / {
            proxy_pass http://unix:/home/ubuntu/bots/Bots-Actions/flaskapp.sock;
        } 
    }

    $ sudo service nginx restart
    $ sudo service gunicorn3 restart
    
For more information, follow this videos series:
    https://www.youtube.com/channel/UCwDlyuX3Fkg5WNBufLnH6dw

================================
Add a subdomain in a Hosted Zone
================================

Edit the A record (under the DNS Management, for example, Route53 on was) with the name of the subdomain and a the ip public of the instance that serve the flask app

