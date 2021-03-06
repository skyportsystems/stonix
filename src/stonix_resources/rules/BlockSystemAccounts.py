###############################################################################
#                                                                             #
# Copyright 2015.  Los Alamos National Security, LLC. This material was       #
# produced under U.S. Government contract DE-AC52-06NA25396 for Los Alamos    #
# National Laboratory (LANL), which is operated by Los Alamos National        #
# Security, LLC for the U.S. Department of Energy. The U.S. Government has    #
# rights to use, reproduce, and distribute this software.  NEITHER THE        #
# GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY,        #
# EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  #
# If software is modified to produce derivative works, such modified software #
# should be clearly marked, so as not to confuse it with the version          #
# available from LANL.                                                        #
#                                                                             #
# Additionally, this program is free software; you can redistribute it and/or #
# modify it under the terms of the GNU General Public License as published by #
# the Free Software Foundation; either version 2 of the License, or (at your  #
# option) any later version. Accordingly, this program is distributed in the  #
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the     #
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    #
# See the GNU General Public License for more details.                        #
#                                                                             #
###############################################################################
'''
Created on Apr 2, 2013

The BlockSystemAccounts rule will search through /etc/passwd to determine if
there are any system accounts which currently allow login. If any are found
which do allow login, the fix method will append :/dev/null to the end of
the entry in /etc/passwd preventing future login from them. One exception is
the 'root' account which will not be blocked due access to it being required
by administrators in certain situations.

@author: bemalmbe
@change: 01/29/2014 dwalker revised
@change: 02/12/2014 ekkehard Implemented self.detailedresults flow
@change: 02/12/2014 ekkehard Implemented isapplicable
@change: 02/19/2014 ekkehard Make sure report always runs
@change: 04/18/2014 dkennel Updated to new style configuration item.
@change: 2014/10/17 ekkehard OS X Yosemite 10.10 Update
@change: 2015/04/14 dkennel Updated for new style isApplicable
'''

from __future__ import absolute_import
import os
import re
import traceback

from ..rule import Rule
from ..configurationitem import ConfigurationItem
from ..logdispatcher import LogPriority
from ..stonixutilityfunctions import readFile, writeFile, iterate, checkPerms
from ..stonixutilityfunctions import setPerms, resetsecon


class BlockSystemAccounts(Rule):
    '''
    classdocs
    '''


    def __init__(self, config, enviro, logger, statechglogger):
        '''
        Constructor
        @change: 04/18/2014 dkennel Updated to new style configuration item.
        '''
        Rule.__init__(self, config, enviro, logger, statechglogger)
        self.logger = logger
        self.rulenumber = 40
        self.rulename = 'BlockSystemAccounts'
        self.formatDetailedResults("initialize")
        self.compliant = False
        self.mandatory = True
        self.helptext = '''The BlockSystemAccounts rule will search through \
/etc/passwd to determine if there are any system accounts which currently \
allow login. If any are found which do allow login, the fix method will \
append :/dev/null to the end of the entry in /etc/passwd preventing future \
login from them. One exception is the 'root' account which will not be \
blocked due access to it being required by administrators in certain \
situations and local user accounts will not be blocked.'''
        self.rootrequired = True
        datatype = 'bool'
        key = 'blocksysaccounts'
        instructions = '''If you have system accounts that need to have valid \
shells set the value of this to False, or No.'''
        default = True
        self.applicable = {'type': 'white',
                           'family': ['linux', 'solaris', 'freebsd'],
                           'os': {'Mac OS X': ['10.9', 'r', '10.10.10']}}
        self.ci = self.initCi(datatype, key, instructions,
                                               default)
        self.guidance = ['CIS', 'NSA(2.3.1.4)', 'cce-3987-5', '4525-2',
                         '4657-3', '4661-5', '4807-4', '4701-9', '4669-8',
                         '4436-2', '4815-7', '4696-1', '4216-8', '4758-9',
                         '4621-9', '4515-3', '4282-0', '4802-5', '4806-6',
                         '4471-9', '4617-7', '4418-0', '4810-8', '3955-2',
                         '3834-9', '4408-1', '4536-9', '4809-0', '3841-4']
        self.iditerator = 0

    def report(self):
        '''
        The report method examines the current configuration and determines
        whether or not it is correct. If the config is correct then the
        self.compliant, self.detailed results and self.currstate properties are
        updated to reflect the system status. self.rulesuccess will be updated
        if the rule does not succeed.

        @return bool
        @author bemalmbe
        @change: dwalker
        '''
        try:
            self.detailedresults = ""
            retval = True
            contents = readFile("/etc/passwd", self.logger)
            if contents:
                for line in contents:
                    if re.search("^#", line) or re.match("^\s*$", line):
                        continue
                    templine = line.strip().split(":")
                    if not len(templine) >= 6:
                        self.detailedresults = "your /etc/passwd file is \
in bad format"
                        self.compliant = False
                        self.rulesuccess = False
                        return False
                    try:
                        if int(templine[2]) >= 500 or templine[2] == "0":
                            continue
                        if not re.search(":/sbin/nologin$|:/dev/null$", line):
                            retval = False
                    except IndexError:
                        debug = traceback.format_exc()
                        debug += "Index out of range"
                        self.logger.log(LogPriority.INFO, debug)
                        self.rulesuccess = False
                        return False
                if retval:
                    self.compliant = True
                else:
                    self.compliant = False
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.detailedresults += "\n" + traceback.format_exc()
            self.logger.log(LogPriority.ERROR, self.detailedresults)
            retval = False
        self.formatDetailedResults("report", self.compliant,
                                                          self.detailedresults)
        self.logdispatch.log(LogPriority.INFO, self.detailedresults)
        return self.compliant
    
###############################################################################

    def fix(self):
        '''
        The fix method will apply the required settings to the system.
        self.rulesuccess will be updated if the rule does not succeed.

        @author bemalmbe
        @change: dwalker
        '''
        try:
            if not self.ci.getcurrvalue():
                return True
            self.detailedresults = ""
            
            #clear out event history so only the latest fix is recorded
            self.iditerator = 0
            eventlist = self.statechglogger.findrulechanges(self.rulenumber)
            for event in eventlist:
                self.statechglogger.deleteentry(event)
                
            success = True
            path = "/etc/passwd"
            contents = readFile(path, self.logger)
            tempstring = ""
            tmpfile = path + ".tmp"
            if contents:
                if not checkPerms(path, [0, 0, 420], self.logger):
                    self.iditerator += 1
                    myid = iterate(self.iditerator, self.rulenumber)
                    if not setPerms(path, [0, 0, 420], self.logger,
                                                    self.statechglogger, myid):
                        success = False
                for line in contents:
                    if re.match('^#', line) or re.match(r'^\s*$', line):
                        tempstring += line
                        continue
                    templine = line.strip().split(":")
                    if not len(templine) >= 6:
                        self.detailedresults = "your /etc/passwd file is " + \
                        "in bad format"
                        self.rulesuccess = False
                        self.formatDetailedResults("fix", self.rulesuccess,
                                   self.detailedresults)
                        self.logdispatch.log(LogPriority.INFO,
                                             self.detailedresults)
                        return False
                    try:
                        if int(templine[2]) >= 500 or templine[2] == "0":
                            tempstring += line
                            continue
                        elif not re.search(":/sbin/nologin$|:/dev/null$", line.strip()):
                            if len(templine) == 6:
                                templine.append("/sbin/nologin")
                            elif len(templine) == 7:
                                templine[6] = "/sbin/nologin"
                            templine = ":".join(templine)
                            tempstring += templine + "\n"
                        else:
                            tempstring += line
                    except IndexError:
                        raise
                    except Exception:
                        self.detailedresults = traceback.format_exc()
                        self.detailedresults += "Index out of range"
                        self.logger.log(LogPriority.ERROR, self.detailedresults)
                        self.rulesuccess = False
                        self.formatDetailedResults("fix", self.rulesuccess,
                                   self.detailedresults)
                        self.logdispatch.log(LogPriority.INFO,
                                             self.detailedresults)
                        self.formatDetailedResults("fix", self.rulesuccess,
                                   self.detailedresults)
                        self.logdispatch.log(LogPriority.INFO,
                                             self.detailedresults)
                        return False
                if writeFile(tmpfile, tempstring, self.logger):
                    self.iditerator += 1
                    myid = iterate(self.iditerator, self.rulenumber)
                    event = {'eventtype': 'conf',
                             'filepath': path}
                    self.statechglogger.recordchgevent(myid, event)
                    self.statechglogger.recordfilechange(path, tmpfile, myid)
                    os.rename(tmpfile, path)
                    os.chown(path, 0, 0)
                    os.chmod(path, 420)
                    resetsecon(path)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.rulesuccess = False
            self.detailedresults += "\n" + traceback.format_exc()
            self.logger.log(LogPriority.ERROR, self.detailedresults)
        self.formatDetailedResults("fix", self.rulesuccess, 
                                   self.detailedresults)
        self.logdispatch.log(LogPriority.INFO, self.detailedresults)
        return self.rulesuccess