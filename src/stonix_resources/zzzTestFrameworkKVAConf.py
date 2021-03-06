#!/usr/bin/python
'''
Created on Jun 13, 2013

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

@author: dwalker
'''
import KVEditorStonix
import KVEditor
import unittest
class zzzTestFrameworkKVAConf(unittest.TestCase):

    def setUp(self):
        self.edit = KVEditor.KVEditor()
        self.editor = KVEditorStonix.KVEditorStonix('16')

    def tearDown(self):
        pass

    def testSimple(self):
        self.failUnlessEqual(self.editor.setPath("/etc/sysctl.bak"), True,
                              "Set Path Failed")
        self.failUnlessEqual(self.editor.setTmpPath("/etc/sysctl.bak.tmp"),
                             True,"SetTmpPath Failed")
        self.failUnlessEqual(self.editor.setType("conf"), True,
                              "Set Type Failed")
        self.failUnlessEqual(self.editor.setData(\
                {'net.ipv4.conf.all.secure_redirects':0,                  
                'net.ipv4.conf.all.accept_redirects':0,  
                'net.ipv4.conf.all.rp_filter':1,     
                'net.ipv4.conf.all.log_martians':1,     
                'net.ipv4.conf.all.accept_source_route':0,
                'net.ipv4.conf.default.accept_redirects':0, 
                'net.ipv4.conf.default.secure_redirects':0,
                'net.ipv4.conf.default.rp_filter':1,
                'net.ipv4.conf.default.accept_source_route':0,    
                'net.ipv4.icmp_ignore_bogus_error_messages':1,           
                'net.ipv4.tcp_syncookies':1,                             
                'net.ipv4.icmp_echo_ignore_broadcasts':1,                  
                'net.ipv4.tcp_max_syn_backlog':4096
                }
                ), True, "Set Data Failed")
        self.failUnlessEqual(self.editor.report(), True,
                              "Set Validate Failed")
        self.failUnlessEqual(self.editor.fix(),True,
                              "Update Failed")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()