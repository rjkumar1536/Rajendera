from flask import Flask, request
import mysql.connector
import logging

def get_Logger(loggerName,fileName):
	logger = logging.getLogger(loggerName)
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler(fileName)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger

logger = get_Logger("StagingWebhookApi","StagingWebhookApi.log")


app = Flask(__name__)
@app.route('/FreeApplication',methods = ['POST'])
def free_application():
	try:	
		print "hello world"
		form_data = request.json
		if form_data['ref_type'] == 'branch':
			logger.info("Brnach %s deleted on github" % (form_data['ref']))
			conn = mysql.connector.connect(host='172.16.0.26', port=3306, user='cwadmin', passwd='cwadmin', db='CI')
			cur = conn.cursor()
			update_query = "UPDATE StagingWebsitePool SET OccupancyStatus = 0 where branchname = '%s' "  % (form_data['ref'])	
			print update_query
			# cur_write.execute(update_query)
			# conn.commit()
			conn.close()
		return ("Branch %s reomved from staging" % (form_data['ref']))
	except:
		exc_type ,exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		logger.error('EXCEPTION IN ({}, LINE {} ): {}'.format(filename, lineno, exc_obj))		
		logger.debug(traceback.print_tb(tb))

if __name__ == '__main__':
	app.run('172.16.0.15','10001')