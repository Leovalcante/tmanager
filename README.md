# Tool Manager
##### *tman v1.0.0*


## What is tman?
*tman* is a command line utility that allows to manage repositories, files, and tools you need on a daily basis or those you need most.  

The tool is able to handle any kind of local files, either executable files, compressed archives, entire project folders, and so forth.
Soon you will notice that the terms localfifles and tools are used interchangeably and they're both supposed to mean a file, or a directory, that is stored onto
your file system.

*tman* is easy to use and quite simple to understand, with *tman* you can handle repositories and local files 'centrally', using just one tool.  
You will be able to add tools to the tman configuration file so that they won't be forgotten or lost anymore, and you will
 be able to find, import and export your tools quickly from one system to another.
*tman* will allow you to pull/clone repository automatically or on demand and it can also schedule cronjob(s) for you, to keep your tools always up-to-date.

*tman* requires a Python interpreter (at least version 3, 2.X is not supported) and some additional module to work as intended.  
It has been developed for Unix-like systems but we're planning to make it usable on Windows too.

## Installation
- `git clone https://github.com/ssh3ll/tmanager.git`
- `cd tmanager`
- `sudo ./install.sh`

Notes:
- The default installation directory is `$YOUR_HOME_DIR/.tman/`, though it can be modified 


## Usage 

tman [OPTIONS] command [ARGS]     


Tman offers the following command:   
    
- `add`: Add new tool(s) to tman
- `config`: Manage Tman configurations
- `delete`: Delete tools
- `export-conf`: Export configuration file and tools.
- `find`: Find tools
- `import-conf`: Import configuration file and tools
- `install`: Install added tools
- `modify`: Modify installation directory, add/modify/rm tags and more.
- `scan`: Scan filesystem seeking repositories.
- `update`: Update added tools

Run `tman [command_name] -h` to see 
## Why tman?
Some useful use-cases

1. A simple, though effective, centralized mean to manage repos and local files too!

2. Keep your repos up-to-date, with no effort  
    - `tman config --cron-job create`

3. Bring your own tool and repo everywhere, with just 2 lines of code.
    - `tman export-conf -o conf.zip`
    - `tman import-conf -i conf.zip`  
    
    Or import/export your tools by tag and/or type:  
    - `tman export-conf -o conf.zip --tags work,pentest --types git,local`
    - `tman import-conf -i conf.zip --tags work,photos --types git`  

4. Tag your tools and find them quickly
    - `tman add https://github.com/PowerShellMafia/PowerSploit -t win,privesc,enum`
    - `tman find -t win,privesc`


#### Examples:

`tman add https://github.com/PowerShellMafia/PowerSploit -d /custom/installation/directory -t windows`

In order to add one repo/tool specifying the installation directory and the desired tags.  

`tman modify PowerSploit -tA work,pentest,powershell`

To add more tags to a specific repository or localfile.  

`tman modify PowerSploit -tM powershell,PS`

To modify an existing tag for a specific repository or localfile.  


`tman find -t windows -p git`

To find all the repositories with tag 'windows' or, for instance, 

`tman find -t exploit,privesc -p local`

to find all the local tools which have the tags 'exploit' and 'privesc'.


`tman delete -i /path/to/file`

To delete more tools at once, the file must contain one tool name per line.  


`tman update --all`

To update every installed repository.    
  
  
`tman config -d /custom/installation/directory`

To change the default installation directory.

`tman config --auto-install [on/off]`

To turn on/off automatic_install.

`tman config -j [create/update/delete/status]`

To create, update, delete and check the status of the created cronjob.




---


# Next Features

- Windows support
- Handle repository branches
- Multithread support

- Store configuration files in the cloud
- SVN repositories and arbitrary online tools support (actually, tman is able to manage arbitrary local tools only)  


# Next Release

Error code 404.  
Message: File not found.   

# Bug report
At the time of writing, of course there's no public bug bounty for this tool.  
However, since Any software may have flaws, we strongly invite you to report any kind of issue you find or may experience using tman. Feel free to open a issue whenever you think it's required and, when You think it's more appropriate, 
contact us privately.

- ssh3ll at protonmail.com
- valerio.preti.tman at gmail.com
