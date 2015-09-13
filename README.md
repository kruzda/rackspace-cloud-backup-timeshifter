# rackspace-cloud-backup-timeshifter

## Things to keep in mind when running this script:
1. The script will operate as if it would be a client residing in the UTC time-zone
2. All your backups will now be defined in UTC, but will still be shown in your local time zone in the Cloud Control Panel
3. By default the dry_run variable is set to False, unless you change it to True, there will be no changes made to your schedules

## To use, edit the file and set the variables on the beginning
1. You will need your username and api key
2. The datacentre (set to 'lon' by default)
3. Change the dry_run variable to False to arm
4. Enter a value for the adjustmen_in_hours variable in the format of +n or -n, where n is the number of hours you wish to shift your backups with. (The default 0 will not change the times at all.)
