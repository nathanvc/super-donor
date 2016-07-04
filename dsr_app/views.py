from __future__ import division
from flask import render_template
from flask import request
from flask import send_file
from dsr_app import app
import gen_dicts as gd
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import numpy as np

# Postgres database connection
user = 'nathanvc' 
pswd = '5698'
dbname = 'dsr_db5'
con = None
con = psycopg2.connect(database = dbname, user = user, host='localhost', password=pswd, port=5433)

# Load metric-learning transformation of vector space
W = np.load('LMNN_mat5.npy')

# Generate dictionaries used to convert database values
# to display values
bank_dict = gd.gen_bank_dict()
word_dict = gd.gen_word_dict()

# return revised word if it is in dictionary (to correct for stemming readability)
def get_full_word(e):
    if e in word_dict:
        return word_dict[e]
    else:
        return e

# pull eye color for a particular donor
def eye_out(bank, id, con):
    label = ''
    query = "SELECT blue, brown, green, hazel FROM dsr_db4 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    eye_temp = pd.read_sql_query(query,con)
    eye_list = ['blue','brown','green','hazel']
    for i,e in enumerate(eye_list):
        if np.array(eye_temp[e])==1:
            if len(label) > 1:
                label = label + ', '
            label = label + e
        print label
    return label

# predict match or not (here simple threshold)
def match_out(dist, wordcount, wordcount_2):
    if dist < 2 and wordcount >=6 and wordcount_2 >= 6:
        return 'Likely'
    if dist < 2 and wordcount >= 4 and wordcount_2 >= 4:
        return 'Possibly'
    elif dist > 2:
        return 'Unlikely' 
    elif wordcount_2 < 4 or wordcount < 4:
        return 'Not enough info'

# pull weight only for a particular donor
def weight_out(bank, id, con):
    label = ''
    query = "SELECT weight FROM dsr_db5 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    weight_temp = pd.read_sql_query(query,con)
    return int(round(float(weight_temp['weight'])))

# pull offspring birth year for a particular donor
def year_out(bank, id, con):
    label = ''
    query = "SELECT offspyr FROM dsr_db5 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    year_temp = pd.read_sql_query(query,con)
    return int(round(float(year_temp['offspyr'])))
    
# pull offspring count for a particular donor
def offsp_out(bank, id, con):
    label = ''
    query = "SELECT offspcnt FROM dsr_db5 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    offsp_temp = pd.read_sql_query(query,con)
    return int(round(float(offsp_temp['offspcnt'])))

# pull bloodtype for a particular donor
def blood_out(bank, id, con):
    label = ''
    query = """SELECT "a+", "b+", "o+", "ab+", "a-", "b-", "o-", "ab-" FROM dsr_db5 WHERE bankid='%s' AND donorid='%s'""" % (bank, id)
    #query = "SELECT 'bloodtype=a+' FROM dsr_db2 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    blood_temp = pd.read_sql_query(query,con)
    blood_list = ['a+', 'b+', 'o+', 'ab+', 'a-', 'b-', 'o-', 'ab-']
    for i,e in enumerate(blood_list):
        if np.array(blood_temp[e])==1:
            if len(label) > 0:
                label = label + ', ' 
            label = label + e.upper()
        print label
    return label

# function to pop non-word fields from the dataframe
# when loaded as '*'
def pop_nonwords(word_temp):
    word_temp = word_temp.drop('index', 1)
    word_temp = word_temp.drop('offspcnt', 1)
    word_temp = word_temp.drop('super', 1)
    word_temp = word_temp.drop('alltext', 1)
    word_temp = word_temp.drop('bankid', 1)
    word_temp = word_temp.drop('donorid', 1)
    word_temp = word_temp.drop('eyeexist', 1)
    word_temp = word_temp.drop('a+', 1)
    word_temp = word_temp.drop('b+', 1)
    word_temp = word_temp.drop('o+', 1)
    word_temp = word_temp.drop('ab+', 1)
    word_temp = word_temp.drop('a-', 1)
    word_temp = word_temp.drop('b-', 1)
    word_temp = word_temp.drop('o-', 1)
    word_temp = word_temp.drop('ab-', 1)
    word_temp = word_temp.drop('blue', 1)
    word_temp = word_temp.drop('brown', 1)
    word_temp = word_temp.drop('green', 1)
    word_temp = word_temp.drop('hazel', 1)
    word_temp = word_temp.drop('offspyr', 1)
    word_temp = word_temp.drop('aa', 1)
    word_temp = word_temp.drop('jewish', 1)
    word_temp = word_temp.drop('latino', 1)
    word_temp = word_temp.drop('weight', 1)
    word_temp = word_temp.drop('wordcount', 1)
    return word_temp

# pull description words for a particular donor
def words_out(bank, id, con):
    label = ''
    query = "SELECT * FROM dsr_db5 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
    whole_vect = pd.read_sql_query(query,con)
    word_temp = pop_nonwords(whole_vect)

    wordcount = 0
    for i,e in enumerate(word_temp.columns.values):
        if np.array(word_temp[e])==1:
            if len(label) > 0:
                label = label + ', '
            fw = get_full_word(e)
            label = label + fw
            wordcount = wordcount+1
    return (label, wordcount)

# Count words in description actually included in our word space
# Does not run query, need to input whole vector
def words_count_noquery(whole_vect):
    word_temp = pop_nonwords(whole_vect)
    wordcount = 0
    for i,e in enumerate(word_temp.columns.values):
        if np.array(word_temp[e])==1:
            if len(label) > 0:
                label = label + ', '
            fw = get_full_word(e)
            label = label + fw
            wordcount = wordcount+1
    return (wordcount)

# render the donor input page
@app.route('/')     
@app.route('/input')
def donor_input():
    return render_template("input.html")

# render presentation page
@app.route('/presentation')     
def pres_page():
    return render_template("presentation.html")

# function to select out donor id's for drop down display
# selects only donors with description word count > 4
@app.route('/getIDs')
def pullbank():
    bankid = request.args.get('pullbank')
    query = "SELECT bankid, donorid FROM dsr_db5 WHERE bankid='%s'" % (bankid)

    restr_id_df=pd.read_sql_query(query, con)
    id_button_list=''
    for id in restr_id_df['donorid'].sort_values():
        (words_lab, wordcount) = words_out(bankid, id, con)
        if wordcount > 4:
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
    
@app.route('/output')
def donor_output():
  #pull in the donor input fields and store
  bank = request.args.get('bank_id')
  id = request.args.get('donor_id')

  query = "SELECT bankid, donorid, offspcnt, weight FROM dsr_db5 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
  print query
  
  query_results=pd.read_sql_query(query,con)
  
  eye_lab = eye_out(bank, id, con)
  (words_lab, wordcount) = words_out(bank, id, con)
  bank_lab = bank_dict[bank]
  blood_lab = blood_out(bank, id, con)
  year_lab = year_out(bank, id, con)
  weight_lab = weight_out(bank, id, con)
  
  #blood_lab = ''

  if len(query_results)==0:
        message = 'This donor is not in our database'
        return render_template("errorpage.html", detection_message = message)

  else: 
      output = []
      for i in range(0,query_results.shape[0]):
          output.append(dict(bankid=bank_lab, donorid=query_results.iloc[i]['donorid'], weight=weight_lab, eyecolor = eye_lab, offspcnt=str(query_results.iloc[i]['offspcnt']), words=words_lab, bloodtype=blood_lab, year=year_lab))
  
      minweight=str(query_results.iloc[i]['weight']-5)
      maxweight=str(query_results.iloc[i]['weight']+5)
  
      query_sim = "SELECT bankid, donorid, offspcnt, weight FROM dsr_db5 WHERE weight BETWEEN '%s' AND '%s'" % (minweight, maxweight)
      query_sim_results=pd.read_sql_query(query_sim, con)

      # run model
      d_orig_q = "SELECT * FROM dsr_db5 WHERE bankid='%s' AND donorid='%s'" % (bank, id)
      d_orig = pd.read_sql_query(d_orig_q,con)
  
      prs_d=d_orig
      prs_d = prs_d.drop('index', 1)
      prs_d = prs_d.drop('offspcnt', 1)
      prs_d = prs_d.drop('super', 1)
      prs_d = prs_d.drop('alltext', 1)
      prs_d = prs_d.drop('bankid', 1)
      prs_d = prs_d.drop('donorid', 1)
      prs_d = prs_d.drop('eyeexist', 1)
      prs_d = prs_d.drop('wordcount', 1)

      print prs_d.columns.values
       
      prs_d=np.array(prs_d)
  
      d_all_q = "SELECT * FROM dsr_db5"
      d_all = pd.read_sql_query(d_all_q,con)
  
      prs_a=d_all
      prs_a = prs_a.drop('index', 1)
      prs_a = prs_a.drop('offspcnt', 1)
      prs_a = prs_a.drop('super', 1)
      prs_a = prs_a.drop('alltext', 1)
      prs_a = prs_a.drop('bankid', 1)
      prs_a = prs_a.drop('donorid', 1)
      prs_a = prs_a.drop('eyeexist', 1)
      prs_a = prs_a.drop('wordcount', 1)
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
        blood_lab = blood_out(bank, id, con)
        year_lab = year_out(bank, id, con)
        (words_lab, wordcount_2) = words_out(bank, id, con)
        dist_lab=round(prs_report[i,2],2)
        match_lab = match_out(prs_report[i,2], wordcount, wordcount_2) 
        
        dict_temp=dict(bankid=bank_dict[bank], donorid=id, weight=weight_lab, eyecolor=eye_lab, offspcnt=offsp_lab, distance=dist_lab, words=words_lab, bloodtype=blood_lab, year=year_lab, match=match_lab)
        print dict_temp
        output_sim.append(dict_temp)
            #print(i, output_sim[i])
  
      if wordcount <= 4:
         message = 'There is not enough information to predict a match'
  
      elif prs_report[0,2] < 2:
        message = 'Your donor has a possible match'
      
      else:
        message = 'Your donor does not have a likely match'  
  
      #the_result = ModelIt(patient,births)
      return render_template("output.html", donors = output, donors_sim = output_sim, detection_message = message, the_result = [])    
    
  
    
