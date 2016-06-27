from __future__ import division
from flask import render_template
from flask import request
from flask import send_file
from dsr_app import app
#from sqlalchemy import create_engine
#from sqlalchemy_utils import database_exists, create_database
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
con = psycopg2.connect(database = dbname, user = user, host='localhost', password=pswd, port=5433)
W = np.load('LMNN_mat1.npy')
print W.shape

# pull eye color for a particular donor
def eye_out(bank, id, con):
    label = ''
    query = "SELECT blue, brown, green, hazel FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    eye_temp = pd.read_sql_query(query,con)
    eye_list = ['blue','brown','green','hazel']
    for i,e in enumerate(eye_list):
        if np.array(eye_temp[e])==1:
            if len(label) > 1:
                label = label + ', '
            label = label + e
        print label
    return label
    
# pull eye color for a particular donor
def weight_out(bank, id, con):
    label = ''
    query = "SELECT weight FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    weight_temp = pd.read_sql_query(query,con)
    return round(float(weight_temp['weight']),2)
    
# pull eye color for a particular donor
def offsp_out(bank, id, con):
    label = ''
    query = "SELECT offspcnt FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    offsp_temp = pd.read_sql_query(query,con)
    return int(round(float(offsp_temp['offspcnt'])))

# pull eye color for a particular donor
def blood_out(bank, id, con):
    label = ''
    #query = "SELECT 'bloodtype=a+', 'bloodtype=b+', 'bloodtype=o+', 'bloodtype=ab+', 'bloodtype=a-', 'bloodtype=b-', 'bloodtype=o-', 'bloodtype=ab-'ff FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    #query = "SELECT 'bloodtype=a+' FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    blood_temp = pd.read_sql_query(query,con)
    blood_list = ['bloodtype=a+', 'bloodtype=b+', 'bloodtype=o+', 'bloodtype=ab+', 
                'bloodtype=a-', 'bloodtype=b-', 'bloodtype=o-', 'bloodtype=ab-']
    for i,e in enumerate(blood_list):
        if np.array(blood_temp[e])==1:
            if len(label) > 0:
                label = label + ', '
            label = label + e
        print label
    return label

# pull eye color for a particular donor
def words_out(bank, id, con):
    label = ''
    query = "SELECT * FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    word_temp = pd.read_sql_query(query,con)
    word_temp = word_temp.drop('index', 1)
    word_temp = word_temp.drop('offspcnt', 1)
    word_temp = word_temp.drop('super', 1)
    word_temp = word_temp.drop('alltext', 1)
    word_temp = word_temp.drop('bankid', 1)
    word_temp = word_temp.drop('donorid', 1)
    word_temp = word_temp.drop('eyeexist', 1)
    word_temp = word_temp.drop('bloodtype=a+', 1)
    word_temp = word_temp.drop('bloodtype=b+', 1)
    word_temp = word_temp.drop('bloodtype=o+', 1)
    word_temp = word_temp.drop('bloodtype=ab+', 1)
    word_temp = word_temp.drop('bloodtype=a-', 1)
    word_temp = word_temp.drop('bloodtype=b-', 1)
    word_temp = word_temp.drop('bloodtype=o-', 1)
    word_temp = word_temp.drop('bloodtype=ab-', 1)
    word_temp = word_temp.drop('blue', 1)
    word_temp = word_temp.drop('brown', 1)
    word_temp = word_temp.drop('green', 1)
    word_temp = word_temp.drop('hazel', 1)    

    wordcount = 0
    for i,e in enumerate(word_temp.columns.values):
        if np.array(word_temp[e])==1:
            if len(label) > 0:
                label = label + ', '
            label = label + e
            wordcount = wordcount+1
    print label
    return (label, wordcount)

# function to query for donor IDs by ban

@app.route('/')     
@app.route('/input')
def donor_input():
    return render_template("input.html")

@app.route('/presentation')     
def pres_page():
    return render_template("presentation.html")
    
@app.route('/getIDs')
def pullbank():
    bankid = request.args.get('pullbank')
    query = "SELECT donorid FROM dsr_db2 WHERE bankid='%s'" % (bankid) 
    
    restr_id_df=pd.read_sql_query(query, con)
    id_button_list=''
    for id in restr_id_df['donorid'].sort_values():
        id_button_list=id_button_list + '<option value="' + id + '" name="donor_id">' + id + '</option>' 
    return id_button_list

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
  print query
  
  query_results=pd.read_sql_query(query,con)
  
  eye_lab = eye_out(bank, id, con)
  words_lab, wordcount = words_out(bank, id, con)
  #blood_lab = blood_out(bank, id, con)
  #blood_lab = ''

  if len(query_results)==0:
        message = 'This donor is not in our database'
        return render_template("errorpage.html", detection_message = message)

  elif wordcount <= 4:
        message = 'There is not enough information for this donor to predict a match'
  else: 

      output = []
      for i in range(0,query_results.shape[0]):
          output.append(dict(bankid=query_results.iloc[i]['bankid'], donorid=query_results.iloc[i]['donorid'], weight=str(round(query_results.iloc[i]['weight'],2)), eyecolor = eye_lab, offspcnt=str(query_results.iloc[i]['offspcnt']), words=words_lab))
  
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
      
      print prs_d.columns.values
       
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
      for i in range(5):
        bank=prs_report[i,0]
        id=prs_report[i,1]
        eye_lab = eye_out(bank, id, con)
        weight_lab = weight_out(bank, id, con)
        offsp_lab = offsp_out(bank, id, con)
        words_lab = words_out(bank, id, con)
        dict_temp=dict(bankid=bank, donorid=id, weight=weight_lab, eyecolor=eye_lab, offspcnt=offsp_lab, distance=round(prs_report[i,2],2), words=words_lab)
        print dict_temp
        output_sim.append(dict_temp)
            #print(i, output_sim[i])
  
      if prs_report[0,2] < 2:
        message = 'Your donor has a possible match'
      else:
        message = 'Your donor does not have a likely match'  
  
      #the_result = ModelIt(patient,births)
      return render_template("output.html", donors = output, donors_sim = output_sim, detection_message = message, the_result = [])    
    
  
    
