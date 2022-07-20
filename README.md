<div style="text-align:center;"><b>DFS Project | Group-5 | Team-1</b></div>

---

# Backup Policy and Backup
<br>
<b>Contributors:</b>
<br>
2018101033 - Jay Sharma
<br>
2018102021 - Tanmay Garg
<br>
2018112006 - Vedant Mundheda
<br>
<b>Concerned TA:</b> Santhosh Reddy Mylaram
<br>

## Overview
Create a sub-system for backing up the datasets stored.

## How to run
To start an FTP server on the system containing the datasets, run
```bash
python3 ftp_server.py
```

To start the Flask server on the system containing the backups, run
```bash
python3 flask_app.py
```
- This serves as the UI for backing up datasets and recovering from backups. Make sure to keep the files ```backup_utils.py``` and ```ftp_utils.py```, and the folder ```templates``` in the same directory as the ```flask_app.py```.

- Enter the flask app URL in the browser, enter the FTP address, username and password (default username='user', password='pass').
- You will be taken to a page where you can view datasets (stored on dataset server) and backups (stored on backup server).
- You can view the contents of a dataset and a backup like on a normal file explorer.
- To backup any dataset, click the button "Backup this directory". You will be taken to a page where you can specify whether a full backup (saves on recovery time) or partial backup (saves on storage space) is needed.
- To recover from a backup, go to "View Backups", select any dataset backup folder, and click "Recover from this backup". You will be taken to a page where you can specify the output folder, and time before which you need the dataset state.
- Have a folder named "dataset_folder" (which contains the datasets) inside the directory you're running ```ftp_server.py``` from. Have a folder named "backup_folder" (can be left empty) inside the directory you're running ```flask_app.py``` from.
- You can also use the API's directly without the flask server, by using the functions from ```backup_utils.py```.
#### Automatic Backups
For a automatic backup every 'n' seconds, just write a simple script that looks like:
```python
ftp = FTP(ftp_address)
ftp.login('user', 'pass')
while True:
	make_backup(ftp, backup_path, dataset_path)
	sleep(n)
```
#### For MySQL database backup:
Backup the IBD file folder using the make_backup API call. Then, to restore, call recover_backup to the MySQL data folder (default location is `C:\ProgramData\MySQL\MySQL Server 8.0\Data`).
To make MySQL recognise those files, open the MySQL shell, 
type `USE db_name`, and for each table type:
```sql
ALTER TABLE table_name DISCARD TABLESPACE
ALTER TABLE table_name IMPORT TABLESPACE
```
Note that if you lose these files due to corruption, they can be restored. However, the database can’t be restored `DROP TABLE`, `TRUNCATE TABLE`, or `DROP DATABASE` commands are used.
#### For MINIO object backup:
If the data is stored in a distributed manner, it would be tough to back it up with this, consider using backup utilities catered to MINIO. [use `mc mirror` command or a utility like Restic/Rclone]
If the data is only local and data is stored in a MINIO data bucket, then the functions `make_backup` and `recover_backup` can be called at the location where the bucket is stored. (the location is `mount_name/bucket_name`).
For example, if you started MINIO server by typing `minio server /tmp`, and created a bucket named `jarvis`, then the data can be found in (and be backed up from) the path `/tmp/jarvis`.

#### For LabelStudio annotations backup:
The same functions `make_backup` and `recover_backup` can be called in whatever location the data is exported to.
The data can be exported using “Export” feature in Label-Studio. A path is specified to export the data to, same path can be used for backup.
If the annotations are not complete, use the “Create New Snapshot” feature in Label-Studio. A path is specified to store the snapshot, same path can be used for backup.

## Functionalities
- `make_backup` function: Makes full backup or partial backup if the dataset has been backed up before. In a partial backup, only changes are stored (added/modified/deleted files). It takes care of all the low-level OS and FTP functionalities under the hood, and enables version history.
- `recover_backup` function: Recovers from existing backups of a dataset, dataset state before a specified time. If no time is specified, it returns the state of dataset after last backup. It also takes low level OS and FTP functionalities under the hood.
- There is a flask based UI for non-programmers to backup their datasets, but there is also the possibility of making an automatic backup as shown in above section.
- These can be used to backup MySQL databases, MINIO objects and LabelStudio annotations & annotation snapshots. As shown in the above section.
- The functions `make_backup` and `recover_backup` are agnostic to file type, hence they can be used for backing up anything (like a react-app), not necessarily a dataset.