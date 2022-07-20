from ftp_utils import *
from datetime import datetime

filter_empty = lambda li: [i for i in li if i.strip()!='']
def write_file(filepath, strf):
	with open(filepath, "w") as f:
		f.write(strf)
def append_file(filepath, strf):
	with open(filepath, "a") as f:
		f.write(strf)
def read_file(filepath):
	strf = None
	with open(filepath, "r") as f:
		strf = f.read()
	return strf
def write_paths(paths, filepath):
	strf = '\n'.join([f'{i[0]} {i[1]}' for i in paths])
	write_file(filepath, strf)
def read_paths(filepath):
	paths = []
	for i in read_file(filepath).splitlines():
		li = i.split(' ')
		paths.append((' '.join(li[:-1]), int(li[-1])))
	return paths

def binary_search(li, x):
	minn = 0
	maxx = len(li)-1
	while minn<=maxx:
		mid = (minn+maxx) // 2
		if x[0]>li[mid][0]:
			minn = mid+1
		elif x[0]<li[mid][0]:
			maxx = mid-1
		else:
			return True
	return False

def check_modify(last_backup_time, paths_new):
	modified_list = []
	for path, t in paths_new:
		if t > last_backup_time:
			modified_list.append(path)
	return modified_list

def check_add(paths_old, paths_new):
	added_list = []
	for i in paths_new:
		if not binary_search(paths_old, i):
			added_list.append(i[0])
	return added_list

def check_delete(paths_old, paths_new):
	deleted_list = []
	for i in paths_old:
		if not binary_search(paths_new, i):
			deleted_list.append(i[0])
	return deleted_list


def make_backup(ftp, backup_path, dataset_path, full=False):
	if not os.path.exists(backup_path):
		os.makedirs(backup_path)
		write_file(os.path.join(backup_path, "full_backup_indices.txt"), "0\n")
	backups = os.listdir(backup_path)
	n = len(backups)-1
	new_backup_folder_path = os.path.join(backup_path, f"backup_{n}")
	os.mkdir(new_backup_folder_path)
	paths_new = recursive_file_list(ftp, dataset_path)
	write_paths(paths_new, os.path.join(new_backup_folder_path, "paths.txt"))
	write_file(os.path.join(new_backup_folder_path, "backup_time.txt"), str(int(time.time())))
	if n==0 or full:
		if full:
			append_file(os.path.join(backup_path, "full_backup_indices.txt"), f"{n}\n")
		whole_data_path = os.path.join(new_backup_folder_path, "data")
		copy_dir_from_remote(ftp, dataset_path, whole_data_path)
	else:
		last_backup_folder_path = os.path.join(backup_path, f"backup_{n-1}")
		paths_old = read_paths(os.path.join(last_backup_folder_path, "paths.txt"))
		last_backup_time = int(read_file(os.path.join(last_backup_folder_path, "backup_time.txt")))

		modified_list = check_modify(last_backup_time, paths_new)
		added_list = check_add(paths_old, paths_new)
		deleted_list = check_delete(paths_old, paths_new)

		write_file(os.path.join(new_backup_folder_path, "modified_list.txt"), '\n'.join(modified_list))
		write_file(os.path.join(new_backup_folder_path, "added_list.txt"), '\n'.join(added_list))
		write_file(os.path.join(new_backup_folder_path, "deleted_list.txt"), '\n'.join(deleted_list))

		modified_dir = os.path.join(new_backup_folder_path, "modified")
		added_dir = os.path.join(new_backup_folder_path, "added")
		os.mkdir(modified_dir)
		os.mkdir(added_dir)
		for i, src_path in enumerate(modified_list):
			copy_file_from_remote(ftp, src_path, os.path.join(modified_dir, f"{i}"))
		for i, src_path in enumerate(added_list):
			copy_file_from_remote(ftp, src_path, os.path.join(added_dir, f"{i}"))

def recover_backup(ftp, backup_path, dataset_path, out_folder, backup_id=None, req_time=None):
	if req_time is None:
		if backup_id is None:
			backup_id = len(os.listdir(backup_path))-2
	else:
		if isinstance(req_time, datetime):
			req_time = time.mktime(req_time.timetuple())
		for e,i in enumerate(os.listdir(backup_path)):
			backup_folder = os.path.join(backup_path, i)
			if os.path.isfile(backup_folder):
				continue
			backup_time = int(read_file(os.path.join(backup_folder, "backup_time.txt")))
			if req_time < backup_time:
				backup_id = int(i.split('_')[-1])-1
				if backup_id<0:
					print("No backups found before the given date")
					return
				break
		if backup_id is None:
			backup_id = len(os.listdir(backup_path))-2
	print("Selecting backup id:", backup_id)
	last_full_backup_id = 0
	for i in read_file(os.path.join(backup_path, "full_backup_indices.txt")).splitlines():
		if i=='':
			continue
		if backup_id < int(i):
			break
		last_full_backup_id = int(i)
	copy_dir_to_remote(ftp, os.path.join(backup_path, f"backup_{last_full_backup_id}/data"), out_folder)
	for i in range(last_full_backup_id+1,backup_id+1):
		backup_folder = os.path.join(backup_path, f"backup_{i}")
		deleted_list = filter_empty(read_file(os.path.join(backup_folder, "deleted_list.txt")).splitlines())
		added_list = filter_empty(read_file(os.path.join(backup_folder, "added_list.txt")).splitlines())
		modified_list = filter_empty(read_file(os.path.join(backup_folder, "modified_list.txt")).splitlines())
		for j in deleted_list:
			ftp.delete(out_folder+j[len(dataset_path):])
		for e,j in enumerate(added_list):
			copy_file_to_remote(ftp, os.path.join(backup_folder, "added", f"{e}"), out_folder+j[len(dataset_path):])
		for e,j in enumerate(modified_list):
			copy_file_to_remote(ftp, os.path.join(backup_folder, "modified", f"{e}"), out_folder+j[len(dataset_path):])