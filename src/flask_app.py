from flask import Flask
from flask import render_template, redirect, request
from ftplib import FTP
import os
from backup_utils import *
from datetime import datetime

app = Flask(__name__)
ftp = [None]
# Checking 404 error
@app.errorhandler(404)
def not_found(error):
	return "Nothing found<br>Try something else.<br>"

@app.route("/", methods=["GET"])
def home_page():
	return render_template("index.html", invalid=False)

@app.route("/set_ftp_address", methods=["POST"])
def set_ftp_address():
	ftp_address = request.form['ftp_address']
	success = False
	try:
		x = FTP(ftp_address)
		x.login(request.form['user'], request.form['pass'])
		ftp[0] = x
		success = True
	except:
		pass
	if not success:
		return render_template("index.html", invalid=True)
	else:
		return redirect("/view_files")

@app.route("/view_files", methods=["GET"])
def view_files():
	return render_template(
							"view_files.html", 
							show_datasets=False,
							show_backups=False,
							datasets_listdir=[],
							backups_listdir=[],
							datasets_currdir='.',
							backups_currdir='.',
						)

@app.route("/view_files/datasets/<path>", methods=["GET"])
def view_datasets(path):
	path = path.replace('+','/')
	upper_dir = os.path.split(path)[0]
	if upper_dir=='':
		upper_dir = path
	datasets_listdir = [(upper_dir.replace('/','+'),True)]+[(i[0],i[1]['type']=='dir') for i in ftp[0].mlsd(path)]
	return render_template(
							"view_files.html", 
							show_datasets=True,
							show_backups=False,
							datasets_listdir=datasets_listdir,
							backups_listdir=[],
							datasets_currdir=path.replace('/','+'),
							backups_currdir='.',
						)

@app.route("/view_files/backups/<path>", methods=["GET"])
def view_backups(path):
	path = path.replace('+','/')
	upper_dir = os.path.split(path)[0]
	if upper_dir=='':
		upper_dir = path
	backups_listdir = [upper_dir.replace('/','+')]+os.listdir(path)
	backups_listdir = [(i,os.path.isdir(os.path.join(path,i))) for i in backups_listdir]
	return render_template(
							"view_files.html", 
							show_datasets=False,
							show_backups=True,
							datasets_listdir=[],
							backups_listdir=backups_listdir,
							datasets_currdir='.',
							backups_currdir=path.replace('/','+'),
							is_valid_backup=(os.path.split(path)[0]=='backup_folder'),
						)

@app.route("/backup/<path>", methods=["GET"])
def backup_form(path):
	return render_template("make_backup.html", dataset_path=path.replace('+','/'))

@app.route("/backup", methods=["POST"])
def backup():
	dataset_path = request.form['dataset_path']
	full = False
	if 'full' in request.form:
		full = request.form['full']=='on'
	dataset_name = os.path.split(dataset_path)[-1]
	make_backup(ftp[0], f'backup_folder/{dataset_name}', dataset_path, full)
	return redirect("/view_files")

@app.route("/recover/<path>", methods=["GET"])
def recover_form(path):
	path = path.replace('+','/')
	dataset_name = os.path.split(path)[1]
	return render_template("recover.html", backup_path=path, dataset_path=f'dataset_folder/{dataset_name}', out_folder=f'dataset_folder/{dataset_name}_recovered')

@app.route("/recover", methods=["POST"])
def recover():
	backup_path = request.form['backup_path']
	dataset_path = request.form['dataset_path']
	out_folder = request.form['out_folder']
	req_time = datetime(*list(map(int, (request.form['req_time']).split(' '))))
	recover_backup(ftp[0], backup_path, dataset_path, out_folder, req_time=req_time)
	return redirect("/view_files")

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=6000, debug=True)
    app.run(debug=True)
	# app.run()