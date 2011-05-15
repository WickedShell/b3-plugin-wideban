#
# BigBrotherBot(B3) (www.bigbrotherbot.com)
# Plugin for extra authentication of privileged users dynamically
# Copyright (C) 2010 Stephen LARROQUE (lrq3000@gmail.com) aka GrosBedo
#
# Description :
# This plugin basically fills the login and password fields in the database with !regaccount
# and when you issue a !loginaccount, it gives you the privileges associated with your old account, by either duplicating them, or either by merging your new account with the old one ( by replacing your old IP and GUID with your current one, and place your current name as an alias, so you get your privileges back while permitting the tracking of the alias).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Changelog:
#
# 2010-08-21 - v0.1 - GrosBedo
# - first public release.
# 2010-08-21 - v0.1.1 - GrosBedo
# - fixed a possible bug with empty guid or pbid.
# 2010-08-21 - v0.1.2 - GrosBedo
# - optimized the algorithm, no more action queue list overflow
# - attempts are now saved in the db as new penalty (with the new client id, ip, guid and pbid)
# 2010-09-14 - v0.1.3 - GrosBedo
# - fixed a bug with empty fields
# - register on authentication rather than on client connection, should avoid some unrecognized player bugs
# 2011-04-23 - v0.1.4 -WickedShell
# -respects the inactive field, meaning deactivated bans now work

__author__    = 'GrosBedo, WickedShell'
__version__ = '0.1.4'
__date__ = '2010-09-14'

# Version = major.minor.patches

import b3
import b3.events
import b3.plugin
from b3 import clients
from b3.querybuilder import QueryBuilder

class WidebanPlugin(b3.plugin.Plugin):

    def onLoadConfig(self):
        try:
            self.banbyip = self.config.getboolean('settings', 'banbyip') 
        except:
            self.banbyip = 0
            self.debug('Using default value (%i) for settings::banbyip', self.banbyip)
        try:
            self.banbyguid = self.config.getboolean('settings', 'banbyguid') 
        except:
            self.banbyguid = 0
            self.debug('Using default value (%i) for settings::banbyguid', self.banbyguid)
        try:
            self.banbypbid = self.config.getboolean('settings', 'banbypbid') 
        except:
            self.banbypbid = 0
            self.debug('Using default value (%i) for settings::banbypbid', self.banbypbid)
        try:
            self.publicmsg = self.config.get('settings', 'publicmsg') 
        except:
            self.publicmsg = 0
            self.debug('Using default value (%i) for settings::publicmsg', self.publicmsg)
        return


    def onStartup(self):        
        # Hook to each client's connection
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)

    def onEvent(self, event):
        if (event.type == b3.events.EVT_CLIENT_AUTH):
            self.debug('Checking for a wide ban for user %s named %s ...' % (event.client.id, event.client.name))
            # Fetching all BAN penalties or penalties for an undetermined amount of time (time_expire = -1) and join the client infos, and the infos of the admin who banned the client
            whereclient = []
            if self.banbyip:
                if len(event.client.ip) > 0 and event.client.ip is not None and event.client.ip != 'None':
                    whereclient.append('c.ip = \'' + event.client.ip + '\'')
            if self.banbyguid:
                if len(event.client.guid) > 0 and event.client.guid is not None and event.client.guid != 'None':
                    whereclient.append('c.guid = \'' + event.client.guid + '\'')
            if self.banbypbid:
                if len(event.client.pbid) > 0 and event.client.pbid is not None and event.client.pbid != 'None':
                    whereclient.append('c.pbid = \'' + event.client.pbid + '\'')

            if len(whereclient) > 0:
                whereclient = ' or '.join(whereclient)
                whereclient = ' and (' + whereclient + ')'
            else:
                whereclient = ''

            #wickedshell
            #respect inactive, no reason to check time expires on a ban
            #no reason to check time_expire
            q = "SELECT p.type as type, p.time_expire as time_expire, c.id as id, c.name as name, c.ip as ip, c.guid as guid, c.pbid as pbid, p.admin_id as admin_id, a.name as admin_name, p.reason as reason FROM penalties as p JOIN clients as c ON c.id = p.client_id LEFT JOIN clients as a ON a.id = p.admin_id WHERE (p.inactive = 0 AND p.type = 'Ban')" + whereclient
            self.debug(q)
            cursor = self.console.storage.query(q)
            
            if cursor and not cursor.EOF:
                r = cursor.getOneRow()
                # We compare each row to the current user : if the ip, or guid, or pbid match, then this means that this user is probably faking his identity, and we then reban him with his new one
                self.info('Player %s id %i with ip %s and guid %s tried to connect to the server while he is banned for reason: %s' % (event.client.name, event.client.id, event.client.ip, event.client.guid, r['reason']))
                # Try to kick/ban user
                try:
                    # Try with the standard way, with the client methods, so we can save the penalties in the database
                    event.client.kick(r['reason'], None, event.client)
                    event.client.ban(r['reason'], None, event.client)
                    event.client.save()
                except:
                    # If we can't, then we use the console wide methods, but new penalty won't be saved
                    self.console.kick(event.client, r['reason'], None, True)
                    self.console.ban(event.client, r['reason'], None, True)
                # Disconnect the user from the current memory of B3
                self.console.queueEvent(b3.events.Event(b3.events.EVT_CLIENT_BAN, r['reason'], event.client))
                event.client.disconnect()
                
                # If you want to show a public message, to show that you don't ban for nothing...
                if len(self.publicmsg)  > 0:
                    if r['admin_id'] == 0 or r['admin_name'] == None:
                        admin_name = 'SYSTEM'
                    else:
                        admin_name = r['admin_name']
                        
                    variables = { # converting them into variables to later include them in user's custom talk_msg
                        'name' : event.client.name,
                        'alias' : r['name'],
                        'ip' : event.client.ip,
                        'id' : event.client.id,
                        'guid' : event.client.guid,
                        'pbid' : event.client.pbid,
                        'adminname' : admin_name,
                        'reason' : r['reason']
                    }
                    message = b3.functions.vars2printf( self.publicmsg ) # preparing publicmsg to include variables
                    self.console.say(message % variables) # saying the ban message with the format

                # Since we re-banned the client, now we can break the database check
                return
