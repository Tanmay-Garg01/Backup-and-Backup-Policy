import os
import time
import glob
from dateutil import parser

time_parse = lambda t, timezone_offset=int(5.5*60*60): int(time.mktime(parser.parse(t).timetuple()))+timezone_offset
recurse_paths = lambda dir_path: sorted(list(glob.glob(dir_path+"/**/*", recursive=True)))

def recursive_file_list(ftp, path='.', modify_times=True):
	final_list = []
	dirs = []
	for item in ftp.mlsd(path):
		if item[1]['type'] == 'dir':
			dirs.append(item[0])
		else:
			nondir = os.path.join(path,item[0])
			if modify_times:
				nondir = (nondir, time_parse(item[1]['modify'])) 
			final_list.append(nondir)
	for subdir in sorted(dirs):
		final_list += recursive_file_list(ftp, os.path.join(path,subdir), modify_times)
	if modify_times:
		final_list.sort(key = lambda x: x[0])
	else:
		final_list.sort()
	return final_list

def copy_file_from_remote(ftp, src, dst=None):
	filename = os.path.split(src)[-1]
	if dst is None:
		dst = './'+filename
	with open(dst, 'wb') as f:
		ftp.retrbinary('RETR ' + src, f.write)

def copy_file_to_remote(ftp, src, dst=None):
	filename = os.path.split(src)[-1]
	if dst is None:
		dst = './'+filename
	with open(src, 'rb') as f:
		ftp.storbinary('STOR ' + dst, f)

def copy_dir_from_remote(ftp, src, dst=None):
	filename = os.path.split(src)[-1]
	if dst is None:
		dst = './'+filename
	li = recursive_file_list(ftp, src, modify_times=False)
	n = len(src)+(src[-1] not in '\\/')
	for filepath in li:
		file_dir, file_name = os.path.split(filepath)
		file_dir = os.path.join(dst, file_dir[n:])
		dst_filepath = os.path.join(file_dir,file_name)
		if not os.path.exists(file_dir):
			os.makedirs(file_dir)
		copy_file_from_remote(ftp, filepath, dst_filepath)

def ftp_makedirs(ftp, path):
	try:
		ftp.mkd(path)
	except Exception as e:
		if str(e) == '550 File exists.':
			return
		ftp_makedirs(ftp, os.path.split(path)[0])
		ftp.mkd(path)

def copy_dir_to_remote(ftp, src, dst=None):
	filename = os.path.split(src)[-1]
	if dst is None:
		dst = './'+filename
	li = recurse_paths(src)
	n = len(src)+(src[-1] not in '\\/')
	for filepath in li:
		if os.path.isdir(filepath):
			continue
		file_dir, file_name = os.path.split(filepath)
		file_dir = os.path.join(dst, file_dir[n:])
		dst_filepath = os.path.join(file_dir,file_name)
		ftp_makedirs(ftp, file_dir)
		copy_file_to_remote(ftp, filepath, dst_filepath)