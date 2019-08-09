# Item Catalog

This project is an application providing a list of items within a variety of categories. It provides a user authentication and authorization system. Registered users have the ability to post, edit, and delete their own items.

## Prerequisites

### Getting the Virtual Machine Set Up
1. Install vagrant at https://www.vagrantup.com/
2. Install virtual machine at https://www.virtualbox.org/wiki/Download_Old_Builds_5_1
3. Install and unzip https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip
4. cd into the vagrant directory and use the command __*vagrant up*__ and then __*vagrant ssh*__ in the terminal

### Getting the Data Ready
1. Download and unzip ItemCatalogProject.zip
2. Place the ItemCatalogProject folder within the vagrant directory
3. Within the terminal from the vagrant directory, use the command __*cd /vagrant/ItemCatalogProject*__
    *Since the files include the database setup and population, it is not necessary to run these files to access data

### Getting Helpers Installed
1. Install Flask using the command  __*pip install flask*__ from the terminal
2. Install SQLAlchemy using the command  __*pip install SQLAlchemy*__ from the terminal
3. Install the OAuth2Client using the command __*pip install oauth2client*__ from the terminal
4. Install HTTPLib2 using the command __*pip install httplib2*__ from the terminal


## Running the Program:
1. If not already done, within the terminal from the vagrant directory, use the command __*cd /vagrant/ItemCatalogProject*__
2. Run the command __*python final_project.py*__
3. To access the project from your browser, go to __*localhost:5000/*__ or __*localhost:5000/artist/*__
    * To access JSON endpoints, go to __*localhost:5000/artist/JSON*__ or __*localhost:5000/artist/#/JSON*__
        * Note that the # can be any number so long as the number is within the number of categories

## Authors

* Nidhi Panchal - Initial work