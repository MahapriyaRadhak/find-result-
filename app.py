from flask import Flask,flash, render_template, request,url_for,redirect,Response,session,send_file,send_from_directory
from flask_mysqldb import MySQL
from functools import wraps
from werkzeug.utils import secure_filename


import os
import csv
import random

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'UPLOAD_FOLDER')

UPLOAD_FOLDER='static/images'
FILE_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app=Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='db_result'
app.config['MYSQL_CURSORCLASS']='DictCursor'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

mysql=MySQL(app)

def allowed_extensions(file_name):
    return '.' in file_name and file_name.rsplit('.',1)[1].lower() in FILE_EXTENSIONS



@app.route("/")
@app.route("/home")
@is_logged_in
def home():
	return render_template("home.html")
    
@app.route("/admin_login_page")
def admin_login_page():
	return render_template("admin_login_page.html")
    
@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=='POST':
        if request.form["submit"]=="Login":
            a=request.form["uname"]
            b=request.form["password"]
            cur=mysql.connection.cursor()
            cur.execute("select * from tbl_admin where aname=%s and apass=%s",(a,b))
            data=cur.fetchone()
            if data:
                session['logged_in']=True
                session['aid']=data["aid"]
                session['aname']=data["aname"]
                session['apass']=data["apass"]
                flash('Login Successfully','success')
                return redirect('admin_login_page')
            else:
                flash('Invalid Login. Try Again','danger')
    return render_template("admin.html") 

def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login','danger')
			return redirect(url_for('home'))
	return wrap
    
@app.route("/student_login_page")
def student_login_page():
	return render_template("student_login_page.html")
    
@app.route('/student',methods=['POST','GET'])
def student():
    if request.method=='POST':
        if request.form["submit"]=="Login":
            a=request.form["uname"]
            b=request.form["password"]
            cur=mysql.connection.cursor()
            cur.execute("select * from tbl_addstudent where sname=%s and srollno=%s",(a,b))
            data=cur.fetchone()
            if data:
                session['logged_in']=True
                session['sid']=data["stid"]
                session['sname']=data["sname"]
                session['spass']=data["srollno"]
                flash('Login Successfully','success')
                return redirect('student_login_page')
            else:
                flash('Invalid Login. Try Again','danger')
    return render_template("student.html" )
    
@app.route('/add_department',methods=['POST','GET'])
@is_logged_in
def add_department():
    if request.method=='POST':
        if request.form["submit"]=="ADD":
            a=request.form["udep"]
            b=request.form["uyear"]
            c=request.form["usem"]
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_department(dname,dyear,sem) values(%s,%s,%s)" ,(a,b,c))
            mysql.connection.commit()
            cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department")
    data=cur.fetchall()	
    cur.close()
    return render_template("add_department.html",datas=data)
       
@app.route('/edit_add_department/<string:did>',methods=['POST','GET'])
def edit_add_department(did):
    if request.method=='POST':
        a=request.form["udep"]
        b=request.form["uyear"]
        c=request.form["usem"]
        cur=mysql.connection.cursor()
        cur.execute("UPDATE tbl_department SET dname=%s,dyear=%s,sem=%s where did=%s" ,(a,b,c,did))
        mysql.connection.commit()
        cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department where did=%s",(did,))
    data=cur.fetchone()	
    return render_template("edit_add_department.html",datas=data) 
 
    
@app.route('/delete_add_department/<string:did>',methods=['POST','GET'])
def delete_add_department(did):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_department where did=%s",(did,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("add_department"))

@app.route('/add_subject',methods=['POST','GET'])
@is_logged_in
def add_subject():
    if request.method=='POST':
        if request.form["submit"]=="ADD":
            a=request.form["usub"]
            b=request.form["usem"]
            c=request.form["did"]
            d=request.form["ucode"]
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_subject(sbname,ssem,did,sbcode) values(%s,%s,%s,%s)" ,(a,b,c,d))
            mysql.connection.commit()
            cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_subject a inner join tbl_department d on a.did=d.did")
    data=cur.fetchall()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department")
    data1=cur.fetchall()
    return render_template("add_subject.html",datas=data,dept=data1)
    
@app.route('/edit_add_subject/<string:sbid>',methods=['POST','GET'])
def edit_add_subject(sbid):
    if request.method=='POST':
        a=request.form["usub"]
        b=request.form["usem"]
        c=request.form["udep"]
        d=request.form["ucode"]
        cur=mysql.connection.cursor()
        cur.execute("UPDATE tbl_subject SET sbname=%s,ssem=%s,did=%s,sbcode=%s where sbid=%s" ,(a,b,c,d,sbid))
        mysql.connection.commit()
        cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_subject where sbid=%s",(sbid,))
    data=cur.fetchone()	
    return render_template("edit_add_subject.html",datas=data) 

@app.route('/delete_add_subject/<string:sbid>',methods=['POST','GET'])
def delete_add_subject(sbid):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_subject where sbid=%s",(sbid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("add_subject"))
    
@app.route('/add_student',methods=['POST','GET'])
@is_logged_in
def add_student():
    if request.method=='POST':
        if request.form["submit"]=="ADD":
            a=request.form["uname"]
            b=request.form["did"]
            c=request.form["uemail"]
            d=request.form["umob"]
            e=request.form["uroll"]
            file=request.files["file"]
            if file and allowed_extensions(file.filename):
                filename, file_extension = os.path.splitext(file.filename)
                new_filename = secure_filename(str(random.randint(10000,99999))+"."+file_extension)
                file.save(os.path.join(UPLOAD_FOLDER, new_filename)) 
                cur=mysql.connection.cursor()
                cur.execute("INSERT INTO tbl_addstudent(sname,did,semail,smobile,srollno,simage) values(%s,%s,%s,%s,%s,%s)" ,(a,b,c,d,e,new_filename))
                mysql.connection.commit()
                cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_addstudent")
    data=cur.fetchall()
    cur.close()
    
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department")
    data1=cur.fetchall()
    return render_template("add_student.html",datas=data,dept=data1)
    
@app.route('/edit_add_student/<string:stid>',methods=['POST','GET'])
def edit_add_student(stid):
    if request.method=='POST':
        a=request.form["uname"]
        b=request.form["udep"]
        c=request.form["uemail"]
        d=request.form["umob"]
        e=request.form["uroll"]
        cur=mysql.connection.cursor()
        cur.execute("UPDATE tbl_addstudent SET sname=%s,did=%s,semail=%s,smobile=%s,srollno=%s  where stid=%s" ,(a,b,c,d,e,stid))
        mysql.connection.commit()
        cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_addstudent where stid=%s",(stid,))
    data=cur.fetchone()	
    return render_template("edit_add_student.html",datas=data)
    
@app.route('/delete_add_student/<string:stid>',methods=['POST','GET'])
def delete_add_student(stid):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_addstudent where stid=%s",(stid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("add_student"))
    
@app.route("/add_view_student")
def add_view_student():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_addstudent a inner join tbl_department d on a.did=d.did")
    data=cur.fetchall()	
    return render_template("view_student.html",datas=data)
  
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))
    
@app.route("/add_mark",methods=['POST','GET'])
@is_logged_in
def add_mark():
    if request.method=='POST':
        if request.form["submit"]=="submit":
            a=request.form["did"]
            b=request.form["asem"]
            file = request.files['file']
            filename, file_extension = os.path.splitext(file.filename)
            new_filename = "data.csv"
            file.save(os.path.join(UPLOAD_FOLDER, new_filename))

            cur = mysql.connection.cursor()

            with open(UPLOAD_FOLDER+'/data.csv',encoding="utf8") as csv_file:

                csv_reader = csv.reader(csv_file, delimiter=',')
                i=0
                for row in csv_reader:
                    if i>0:
                        cur.execute("insert into tbl_addmark(did,sem,srollno,s1,s2,s3,s4,s5,status) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(a,b,row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
                    i+=1
            cur.close()
    mysql.connection.commit()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_department")
    dept = cur.fetchall()
    cur.close()
    return render_template("add_mark.html",datas=dept)
    
#@app.route("/view_mark")
#def view_mark():
#    cur=mysql.connection.cursor()
#    cur.execute("select * from tbl_addmark a inner join tbl_department d on a.did=d.did ")
 #   data=cur.fetchall()	
  #  return render_template("view_mark.html",datas=data)
  
@app.route("/view_mark", methods=['POST', 'GET'])
def view_mark():
    dept = []
    
    if request.method=='POST':
        if request.form["submit"]=="submit":
            a=request.form["did"]
            b=request.form["usem"]
            cur=mysql.connection.cursor()
            cur.execute("select * from tbl_addmark a inner join tbl_addstudent d on a.srollno=d.srollno inner join tbl_department t on t.did=a.did and a.did=d.did where a.sem=%s and a.did=%s",(b,a))
            dept=cur.fetchall()
            cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department")
    data1=cur.fetchall()
    cur.close()
    return render_template("view_mark.html",status=dept,depta=data1)
    
@app.route('/view_profile')
def view_profile():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_addstudent a inner join tbl_department d on a.did=d.did where a.stid=%s",(session["sid"],))
    data=cur.fetchall()	
    return render_template("view_profile.html",datas=data)
    
@app.route('/view_result')
def view_result():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_addmark m inner join tbl_subject s on m.sem=s.ssem and m.did=s.did inner join tbl_department d inner join tbl_addstudent t on d.did=t.did and t.srollno=m.srollno and d.did=m.did where t.stid=%s",(session["sid"],))
    data=cur.fetchall()
    return render_template("view_result.html",status=data)
  
@app.route('/Logout')
def Logout():
    session.clear()
    return redirect(url_for("admin"))

@app.route('/Logoutt')
def Logoutt():
    session.clear()
    return redirect(url_for("student"))    

if __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)