from flask import Flask, render_template, url_for, json, request, redirect, jsonify
from es import ES
from es2 import ES2
import json
from pprint import pprint


app = Flask(__name__, static_url_path='/static')


@app.route('/')
def main():
   return render_template('index.html')
@app.route('/index')
def index():
   return render_template('index.html')

@app.route('/example')
def example():
   return render_template('example.html')

@app.route('/search', methods=['POST'])
def search():
	# var1 is the input of form -- query
	# es = Elasticsearch()
    
    DEBUG_FLAG = True

    query = request.form['inputData']

	# if input is empty, then stay on first page 
    if query == '':
        return render_template('index.html')
	
    # Start elasticsearch index
    # index_name = "citerseer_index" # for local testing
    index_name = "pubmed_0305" # for server
    es2 = ES2(index_name)

    if DEBUG_FLAG:
        print "Raw query:", query

    highlight_term_list = es2.entity_detection(query)
    if DEBUG_FLAG:
        print "Highlist term list:", highlight_term_list
    
    highlight_term_list_w_color = es2.entity_typing(highlight_term_list)
    if DEBUG_FLAG:
        print "Highlist term list with color:", highlight_term_list_w_color   
         
    search_body = es2.generate_search_body(highlight_term_list)

    res = es2.search(search_body) # res is a dict
    res["highlight_term_list"] = highlight_term_list_w_color
	# print res
	
	# json styple txt output (20170304: change back from "test_output" to "res")
    res_json = json.dumps(res, ensure_ascii = False)

	# json format output 
    h_json_out = json.loads(res_json)

    return render_template("result.html", results = res_json, output_json = h_json_out)

@app.route('/result')
def result():
    filename = app.static_folder + '/data/sample.json'  # using sample data currently
    with open(filename) as data_file:    
        data = json.load(data_file)
    return render_template('result.html', data = data)

@app.route('/sampledata', methods=['GET','POST'])
def sampledata():
    return render_template('data/sample.json')

if __name__ == '__main__':
    # app.run(debug=True) # for local testing
    app.run(host='0.0.0.0', port = 5002) # for server