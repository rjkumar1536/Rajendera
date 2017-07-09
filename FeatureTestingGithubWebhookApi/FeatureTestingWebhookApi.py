from flask import Flask, request
import mysql.connector
import logging
import sys
import traceback 

def get_Logger(loggerName,fileName):
	logger = logging.getLogger(loggerName)
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler(fileName)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger

logger = get_Logger("FeatureTestingWebhookApi","FeatureTestingWebhookApi.log")


app = Flask(__name__)

@app.route('/Testing')
def testing():
	return "It is Working Fine"
@app.route('/FreeApplication',methods = ['POST'])
def free_application():
	try:	
		print "hello world"
		form_data = request.json
		if form_data['ref_type'] == 'branch':
			logger.info("Branch %s deleted on github" % (form_data['ref']))
			conn = mysql.connector.connect(host='172.16.0.26', port=3306, user='cwadmin', passwd='cwadmin', db='CI')
			cur = conn.cursor()
			update_query = "UPDATE FeatureTestingWebsitePool SET OccupancyStatus = 0 where branchname = '%s' "  % (form_data['ref'])	
			print update_query
			cur.execute(update_query)
			conn.commit()
			conn.close()
		return ("Branch %s reomved from FeatureTesting" % (form_data['ref']))
	except:
		exc_type ,exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		logger.error('EXCEPTION IN ({}, LINE {} ): {}'.format(filename, lineno, exc_obj))		
		logger.debug(traceback.print_tb(tb))

if __name__ == '__main__':
	app.run('172.16.0.15','10001')