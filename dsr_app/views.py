from __future__ import division
from flask import render_template
from flask import request
from flask import send_file
from dsr_app import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from a_Model import ModelIt
import random
import matplotlib.pyplot as plt
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvasimport io
import numpy as np

user = 'nathanvc' 
pswd = '5698'
dbname = 'dsr_db2'
con = None
con = psycopg2.connect(database = dbname, user = user, host='localhost', password=pswd, port=5432)
W = np.load('LMNN_mat1.npy')
print W.shape

#@app.route('/')
#@app.route('/index')
#def index():
#    return render_template("index.html",
#       title = 'Home', user = { 'nickname': 'Everyone!' },
#       )

#@app.route('/db')
#def rawquery_page():
#    sql_query = """                                                                       
#                SELECT * FROM dsr_db2 WHERE bankid = 'TSBC';          
#                """
#    query_results = pd.read_sql_query(sql_query,con)
#    results = ""
#    for i in range(0,10):
#        results += str(query_results.iloc[i]['weight'])
#        results += str("<br>")
#    return results
        
#@app.route('/db_fancy')
#def rawquery_page_fancy():
#    sql_query = """
#               SELECT bankid, donorid, offspcnt FROM dsr_db2 WHERE bankid = 'TSBC';
#                """
#    query_results=pd.read_sql_query(sql_query,con)
#    output = []
#    for i in range(0,query_results.shape[0]):
#        output.append(dict(bankid=query_results.iloc[i]['bankid'], donorid=query_results.iloc[i]['donorid'], offspcnt=str(query_results.iloc[i]['offspcnt'])))
#    return render_template('dsr_initial.html',donors=output)

@app.route('/')     
@app.route('/input')
def donor_input():
    return render_template("input.html")

@app.route('/presentation')     
def pres_page():
    return render_template("presentation.html")


@app.route('/myplot')
def getplot():
    fig = plt.figure()
    plt.plot(range(3))
    canvas = FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')  
    
@app.route('/donorplot')
def getdonorplot():
    bank = request.args.get('bank_id')
    id = request.args.get('donor_id')
    
    fig = plt.figure()
    
    query = "SELECT bankid, donorid, offspcnt, bloodtype, weight FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id) 
  
    query_results=pd.read_sql_query(query,con)
    
    # eye color value for this donor
    eyes_sp=query_results['eyes'][0]
  
    # calculate proportion of donors with this eye color 
    # (only among donors with eye color reported)
    don_eye_num_query = "SELECT COUNT(eyes) FROM dsr_db1 WHERE eyes = '%s' " % eyes_sp
    don_eye_num_from_sql = pd.read_sql_query(don_eye_num_query, con)
    
    don_eye_num = don_eye_num_from_sql['count'][0]

    don_eye_den_query = """
    SELECT COUNT(eyes) FROM dsr_db2 WHERE eyes IS NOT NULL
    """
    don_eye_den_from_sql = pd.read_sql_query(don_eye_den_query, con)
    don_eye_den = don_eye_den_from_sql['count'][0]
    
    don_val = don_eye_num / don_eye_den
    
    # calculate proportion of offspring conceived via donors with this eye color 
    # (only among donors with eye color reported)
    off_eye_num_query = "SELECT SUM(offspcnt) FROM dsr_db1 WHERE eyes = '%s' " % eyes_sp
    print off_eye_num_query
    off_eye_num_from_sql = pd.read_sql_query(off_eye_num_query, con)
    off_eye_num = off_eye_num_from_sql['sum'][0]

    off_eye_den_query = """
    SELECT SUM(offspcnt) FROM dsr_db1 WHERE eyes IS NOT NULL
    """
    print off_eye_den_query
    off_eye_den_from_sql = pd.read_sql_query(off_eye_den_query, con)
    off_eye_den = off_eye_den_from_sql['sum'][0]
    
    off_val = off_eye_num / off_eye_den

    plt.plot([don_val, off_val])
    
    ylim([0,1])
    
    canvas = FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')     


@app.route('/output')
def donor_output():
  #pull in the donor input fields and store
  bank = request.args.get('bank_id')
  id = request.args.get('donor_id')

  query = "SELECT bankid, donorid, offspcnt, weight FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id) 
  
  query_results=pd.read_sql_query(query,con)

  if len(query_results)==0:
        message = 'This donor is not in our database'
        return render_template("errorpage.html", detection_message = message)
  else: 

      output = []
      for i in range(0,query_results.shape[0]):
          output.append(dict(bankid=query_results.iloc[i]['bankid'], donorid=query_results.iloc[i]['donorid'], weight=str(query_results.iloc[i]['weight']), offspcnt=str(query_results.iloc[i]['offspcnt'])))
  
      minweight=str(query_results.iloc[i]['weight']-5)
      maxweight=str(query_results.iloc[i]['weight']+5)
  
      query_sim = "SELECT bankid, donorid, offspcnt, weight FROM dsr_db2 WHERE weight BETWEEN '%s' AND '%s'" % (minweight, maxweight)
      query_sim_results=pd.read_sql_query(query_sim, con)

      # run model
      d_orig_q = "SELECT * FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id) 
      d_orig = pd.read_sql_query(d_orig_q,con)
  
      prs_d=d_orig
      prs_d = prs_d.drop('index', 1)
      prs_d = prs_d.drop('offspcnt', 1)
      prs_d = prs_d.drop('super', 1)
      prs_d = prs_d.drop('alltext', 1)
      prs_d = prs_d.drop('bankid', 1)
      prs_d = prs_d.drop('donorid', 1)
      prs_d = prs_d.drop('eyeexist', 1)  
      prs_d=np.array(prs_d)
  
      d_all_q = "SELECT * FROM dsr_db2"
      d_all = pd.read_sql_query(d_all_q,con)
  
      prs_a=d_all
      prs_a = prs_a.drop('index', 1)
      prs_a = prs_a.drop('offspcnt', 1)
      prs_a = prs_a.drop('super', 1)
      prs_a = prs_a.drop('alltext', 1)
      prs_a = prs_a.drop('bankid', 1)
      prs_a = prs_a.drop('donorid', 1)
      prs_a = prs_a.drop('eyeexist', 1)
      prs_a=np.array(prs_a)
  
      # donor info
      prs_dinfo = pd.concat([d_all['bankid'], d_all['donorid']], axis=1)
      #print prs_dinfo.head
  
      # Calculate all distances  
      dist_cv=[]
      prs_a_df=prs_a
      prs_a=np.array(prs_a)
      for i in range(prs_a.shape[0]):
        dist=prs_d[:]-prs_a[i,:] 
        lmnn_dist=float(np.sqrt(np.dot(dist,np.dot(W,dist.T))))
        dist_cv.append(lmnn_dist)
  
      dist_dict={}
      dist_dict['distance']=dist_cv
      df_temp=pd.DataFrame.from_dict(dist_dict)
  
      prs_dinfo=pd.concat([prs_dinfo,df_temp],axis=1)
  
      print prs_dinfo.columns.values
  
      # sort by smallest distance
      prs_report = np.array(prs_dinfo.sort_values(by='distance').iloc[1:12])

      #del output_sim
      output_sim=[]
      for i in range(10):
        print '*'
        print prs_report
        dict_temp=dict(bankid=prs_report[i,0], donorid=prs_report[i,1], distance=prs_report[i,2])
        print dict_temp
        output_sim.append(dict_temp)
            #print(i, output_sim[i])
  
      if prs_report[0,2] < 2:
        message = 'Your donor has a possible match'
      else:
        message = 'Your donor does not have a likely match'  
  
      #the_result = ModelIt(patient,births)
      return render_template("output.html", donors = output, donors_sim = output_sim, detection_message = message, the_result = [])    
    
  
    
