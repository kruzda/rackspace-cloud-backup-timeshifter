#!/usr/bin/env python
import json, urllib2

# -=-= Configure here to use =-=- #
username=''
apikey=''
datacenter='lon'
dry_run=True
adjustment_in_hours = 0
# -=-= end of configurable bits =-=- #


api_endpoint=''
auth_header = {"Content-type": "application/json"}
auth_data = {"auth": {"RAX-KSKEY:apiKeyCredentials": {"username": "" + username + "", "apiKey": "" + apikey + ""}}}
auth_request = urllib2.Request("https://identity.api.rackspacecloud.com/v2.0/tokens", headers=auth_header, data=json.dumps(auth_data))
auth_response = json.load(urllib2.urlopen(auth_request))

for i in auth_response['access']['serviceCatalog']:
    for e in i['endpoints']:
        if e.has_key('region') and e['region'] == datacenter.upper() and ((e.has_key('type') and e['type'] == 'rax:backup') or 'backup' in e['publicURL']):
            api_endpoint = e['publicURL']

if api_endpoint == '':
    exit('backup endpont not found - likely ' + datacenter + ' is not a valid datacenter for this account')

auth_token = auth_response['access']['token']['id']

backups_header={"X-Auth-Token": auth_token, "Content-type": "application/json"}
backups_request = urllib2.Request(api_endpoint + "/backup-configuration", headers=backups_header)
backups_data = json.load(urllib2.urlopen(backups_request))
print 'Printing debug information since dry_run==' + str(dry_run) + "\n\n" if dry_run else "Started adjusting StartTimeHours...\n"
for i in backups_data:
    print str(i) + "\n" if dry_run else 'loading ' + i['BackupConfigurationName']
    # removing keys that are not allowed in an update API query
    i.pop('EncryptionKey')
    i.pop('MachineName')
    i.pop('IsDeleted')
    i.pop('Datacenter')
    i.pop('NextScheduledRunTime')
    i.pop('IsEncrypted')
    i.pop('LastRunBackupReportId')
    i.pop('Exclusions')
    i.pop('Flavor')
    i.pop('BackupPostscript')
    i.pop('BackupPrescript')
    i.pop('MissedBackupActionId')
    i.pop('LastRunTime')
    i['TimeZoneId'] = 'UTC'
    if i['StartTimeHour'] != None:
        adjustment = adjustment_in_hours
        StartTimeHour24 = ((i['StartTimeAmPm'] == 'PM') * 12 + i['StartTimeHour'] ) if i['StartTimeHour'] != 12 else ((i['StartTimeAmPm'] == 'AM') * 12 + i['StartTimeHour']) % 24
        NewStartTimeHour24 = (StartTimeHour24 + adjustment) % 24
        i['StartTimeHour'] = ((NewStartTimeHour24 - (12 < NewStartTimeHour24) * 12) + 11) % 12 + 1
        i['StartTimeAmPm'] = 'AM' if NewStartTimeHour24 < 11 else 'PM'
        if i['DayOfWeekId'] != None:
            i['DayOfWeekId'] = (i['DayOfWeekId'] + ((StartTimeHour24 + adjustment or abs(adjustment)/adjustment)/24)) % 7
    config_update_request = urllib2.Request(api_endpoint + "/backup-configuration/" + str(i.pop('BackupConfigurationId')), headers=backups_header, data=json.dumps(i))
    config_update_request.get_method = lambda: 'PUT'
    print str(i) + "\n\n" if dry_run else 'changing ' + i['BackupConfigurationName'] + ' ' + urllib2.urlopen(config_update_request).read()
        

'''
sample contents of one backup config after removing cruft
{'BackupConfigurationName': 'initial backup', 'NotifyRecipients': 'zoltan.ver@rackspace.co.uk', 'NotifySuccess': False, 'StartTimeAmPm': '', 'DayOfWeekId': None, 'VersionRetention': 0, 'TimeZoneId': 'GMT Standard Time', 'BackupConfigurationScheduleId': 61640, 'HourInterval': None, 'StartTimeHour': None, 'inclusions': [{'FileItemType': 'Folder', 'FilePathEncoded': None, 'FilePath': 'C:\\Users\\Administrator', 'Filter': 'Include', 'ParentId': 62333, 'FileId': 259653}], 'StartTimeMinute': None, 'NotifyFailure': True, 'Frequency': 'Manually', 'MachineAgentId': 190328, 'IsActive': True}

http://docs.rackspace.com/rcbu/api/v1.0/rcbu-devguide/content/PUT_updateBackupConfig_v1.0__tenant_id__backup-configuration__backupConfigurationId__backupConfig.html

'''
