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


The finally of this "internal" web-page is to make easiset the way
to create signatures for every member and to interact with
some of the bots data extractors.

=========
Microservices
=========

- **Web Scouting**: List of all of the mother agencies where the Scouting bot (v1 & v2) has access

- **Instagram Follow Members**: List of the ig users to check new followers https://github.com/realFranco/phantombuster_new_followings

- **Instagram Biography Checks**: List of ig user to track changes on biograhpy https://github.com/realFranco/ig_bot

- **System Agency Signatures**: Set of tools that make easily the way creation step of an email signature.

======================
Public Subdomain
======================

**botactions.systemagency.com**

================================
Instructions for Run the server
================================

0. Clone the repo. 
    
    .. code-block:: console
    
       $: git clone git@github.com:realFranco/Bots-Actions.git
       $: git clone https://github.com/realFranco/Bots-Actions.git

1. Install the dependecies.

    .. code-block:: console
    
       $: pip3 install -r requeriments.txt

2. Run the web-server.
    
    .. code-block:: console
    
       $: python3 app.py

2.1. If you need to close the terminal where the script it is running, do this.

    .. code-block:: console
    
       $: nohup python3 app.py &

This will output a numbers, that becomes in the pID of the script.

Actually you can find that process using this command:
    
    .. code-block:: console
    
       $: ps -fa | grep python

And kill it using:

    .. code-block:: console
    
       $: kill -9 pID 
    
Where pID is the number returned on after nohup or the ps command.

=================================================================
If your pourpose it is to host this web app into an ec2 instance
=================================================================

0. Step initial
    
    Open the port 80 & 443 for transfer data from the instance to the public requests.
    Initially, using just:
    
    .. code-block:: console
    
       $: nohup sudo python3 app.py

1. Install this packeages
   
   .. code-block:: console
   
      $: sudo apt-get install nginx
      $: sudo apt-get install gunicorn3

2. Inside to the ec2 instance write this lines, and edit/create some configuration files, for run unicon as a service
    
    .. code-block:: console
    
       $: cd /etc/systemd/system/
       $: sudo nano gunicorn3.service

       [Unit]
       Description=Gunicorn service
       After=network.target
    
       [Service]
       User=ubuntu
       Group=www-data
       WorkingDirectory=/home/...
       ExecStart=/usr/bin/gunicorn3 --workers 1 --bind unix:flaskapp.sock -m 007 app:app    
    
       # Reload the deamon
       $: sudo systemctl daemon-reload

       # Start the service
       $: sudo service gunicorn3 start

       # Check the service
       $: sudo service gunicorn3 status

       $: cd /etc/nginx/sites-enabled/

       # Write the configuration file for the server
       $: sudo nano flaskapp
    
       server{
           listen 80;
           server_name xxx.xxx.xxx.xxx; # or the public ipv4 that you have for the instance

           location / {
               proxy_pass http://unix:/home/....sock;
           } 
       }

       $: sudo service nginx restart
       $: sudo service gunicorn3 restart
    
    # For more information, follow this videos series:
    https://www.youtube.com/channel/UCwDlyuX3Fkg5WNBufLnH6dw
    

================================
Add a subdomain in a Hosted Zone
================================

Edit the A record (under the DNS Management, for example, AWS Route53) with the name of the subdomain and add the  public ip of the instance that serve the flask app.
