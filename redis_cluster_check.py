#!/usr/bin/python
### Check if nodes redis cluster is in a correct status
###
import subprocess
import sys
import os

def check(option):
    try:
        command = "redis-cli info | grep %s" % option
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output, err = p.communicate()
        return output.split(':')[1].rstrip()
    except:
        #print "ERROR: redis-cli command failed"
	print "2:0:redis-cli command failed, redis is not responsive."
        exit()

def save(role): 
    try:
    	with open('redis_status', 'w') as f:
            f.write(role)
    except:
       print "ERROR: can not save role to file"

def check_prev(role):
    ### Read previous role
    try:
        with open('redis_status', 'r') as f:
            role = f.readline().strip()
    except IOError:
        #print "WARNING: can not open file"
        role=""
    return role

#### 

### check previous and current role
prevRole = check_prev('')
currRole = check('role')

if prevRole == "" :
    #print "WARNING: Redis Role Was not collected yet."
    print "0:0:Redis Role Was not collected yet."
    ## save current role to file
    save(currRole)

elif currRole == "":
    #print "ERROR: Failed to collect redis role"
    print  "2:0:Failed to collect redis role"
    exit()

elif currRole != prevRole :
    #print "WARNING: Switchover detected. previous role [%s] changed to [%s]" % (prevRole, currRole)
    print "2:0:Switchover detected. Redis Role Changed from %s to %s" % (prevRole, currRole)

    ## save current role to file
    save(currRole)

elif currRole == prevRole :
    if currRole == 'master':
        # Check master status up
        slaves = check('connected_slaves')
        if slaves > "0":
            #print "INFO: Master redis and %s slaves connected." % slaves
            print "0:0:Master redis and %s slaves connected." % slaves
        else:
            #print "ERROR: Master redis with not slave connected"
            print "2:0:Master redis with not slave connected"
    elif currRole == 'slave':
        # is asociated and read only?
        mls = check('master_link_status')
        sro = check('slave_read_only')
        master = check("master_host")
        if mls == 'up' and sro == '1':
            #print "INFO: Slave Redis read only and master (%s) redis is up" % master
            print "0:0:Slave Redis read only and master (%s) redis is up" % master
        else:
            #print "ERROR: Slave redis is not connected to master or not marked like read_only"
            print "2:0:Slave redis is not connected to master or not marked like read_only"
    else:
        #print "ERROR: Unknown role %s " % currRole
        print "2:0:Unknown role %s" % currRole

else:
    #print "ERROR: Unexpected error"
    print "2:0:Unexpected error"
    exit()
