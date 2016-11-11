# Item catalog

_This project is part of Udacity's Full Stack Developer Nanodegree._

This project implements a web application that lets restaurant owners show their menus. It's built with:
  * Server-side: **Python** plus the **Flask** framework.
  * Database: **SQLAlchemy** backed by a **PostgreSQL** database. Also tested with **SQLite** during development.
  * Front-end: **HTML5/CSS3**, with a **Bootstrap** interface and some **jQuery**.

## Live site

https://oscardoc-restaurant-menu.herokuapp.com, hosted at [Heroku](https://www.heroku.com)

## Screenshot

![screenshot](/vagrant/restaurants/screenshot.jpg?raw=true "Project as of 29 February 2016")


# How to run the project

To run the project tests, follow these steps:

1. Install [Vagrant](https://docs.vagrantup.com/v2/installation/)  if you don't have it already.
2. Grab a copy of the project. You can either:
  * Clone the repo with git: `git clone https://github.com/OscarDoc/fullstack-nanodegree-vm.git`.
  * [Clone with GitHub Desktop](github-windows://openRepo/https://github.com/OscarDoc/fullstack-nanodegree-vm).
  * [Download the latest release](https://github.com/OscarDoc/fullstack-nanodegree-vm/archive/master.zip)
3. Open a command-line window and go to the /fullstack-nanodegree-vm/vagrant folder of the project.
4. Once in it, run `vagrant up`. That command will load the Virtual Machine, which contains the development environment.
5. SSH into the machine with the username `vagrant` and password `vagrant`. Depending on your OS:
  * **NOT** Windows: just run `vagrant ssh`.
  * Windows: Running `vagrant ssh` will mourn that it's not possible and provide you an IP/port to log in. So, to log in, download [PuTTY](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html) and follow the instructions [found here](https://github.com/Varying-Vagrant-Vagrants/VVV/wiki/Connect-to-Your-Vagrant-Virtual-Machine-with-PuTTY), which basically explain how to use the Vagrant VM certificate in PuTTY.
6. Once inside the VM, run `cd /vagrant/tournament`.
7. Instal Python dependencies; `sudo pip install -r requirements.txt`
8. To start the web, just run `python project.py`
9. Once it's started, it will be available from the brwoser at [localhost:5000](http://localhost:5000).


# What's included

Within the download you'll find the following directories and files, logically grouping common assets. You'll see something like this:
```
├── vagrant/
│   ├── restaurants/                  THIS PROJECT
│   │   ├── README.md                 THIS FILE
│   │   ├── static/                   JS and CSS files
│   │   │   ├── app.js                jQuery functionalities
│   │   │   └── style.css             Web style, based on Bootstrap
│   │   ├── templates/                Flask templates of the site
│   │   │   │── partials/             Common sub-templates (head html, navigation bar, flash messages)
│   │   │   └── *.html                The name of each template is self-descriptive
│   │   ├──database.py                SQLAlchemy-based definition of the DB
│   │   ├──lotsofmenu.py              Running this script fills the DB with demo data  
│   │   ├──daos.py                    Data-Access Objects; implement the operations on the DB through SQLAlchemy
│   │   ├──project.py                 MAIN SCRIPT. Contains the web Flask routes
│   │   ├──project_api_endpoints.py   Flask routes implementing JSON and ATOM endpoints
│   │   ├──project_oauth.py           Flask routes implementing OAuth
│   │   ├──client_secrets_fb.json     Facebook OAuth secrets file
│   │   ├──client_secrets_gc.json     Google OAuth secrets file
│   │   ├──Procfile                   Script for foreman
│   │   └──requirements.txt           Configuration for Heroku
│   ├── tournament/                   Project 2 of the Full-stack Nanodegree  
│   ├── Vagrantfile                   Virtual machine configuration  
│   └── pg_config.sh                  Script that install everything needed in the VM
└── README.md                         Repository readme file
```
