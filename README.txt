Wideban plugin for Big Brother Bot (www.bigbrotherbot.com)
=============================================================

By GrosBedo and WickedShell (just bug fixes)


Description
-----------

This passive plugin modify the behaviour of permban : instead of looking for a matching client_id, it will look for a penalty with the same ip or same guid or same pbid (you can configure which ones are checked).

If such a client is found, this probably means that he is trying to bypass his ban. In this case, another kick/ban is issued against this client, with his new datas (like id, ip, guid and pbid) and you can say a public message to notify all users.

This plugin is totally passive : you just have to load it into your bot, and you're good to go !

Forum : http://www.bigbrotherbot.net/forums/releases/wideban/


Installation
------------

 * copy wideban.py into b3/extplugins
 * copy wideban.xml into b3/extplugins/conf
 * update your main b3 config file with :
<plugin name="wideban" config="@b3/extplugins/conf/wideban.xml"/>


Usage
-----
Just !permban someone, and the plugin will check at each client connection for the ip, guid or pbid.
It works for your already existing penalties table too (the plugin is retroactive).


Disclaimer
----------
The author of this opensource plugin endorse NO responsibility whatsoever for any problem that might arise when using this tool.


Changelog
---------

2010-08-21 - 0.1 - GrosBedo
 - first public release.

2010-08-21 - v0.1.1 - GrosBedo
 - fixed a possible bug with empty guid or pbid.

2010-08-21 - v0.1.2 - GrosBedo
 - optimized the algorithm, no more action queue list overflow
 - attempts are now saved in the db as new penalty (with the new client id, ip, guid and pbid)

2010-09-14 - v0.1.3 - GrosBedo
 - fixed a bug with empty fields
 - register on authentication rather than on client connection, should avoid some unrecognized player bugs
2011-04-23 - v0.1.4 -WickedShell
 -respects the inactive field, meaning deactivated bans now work
