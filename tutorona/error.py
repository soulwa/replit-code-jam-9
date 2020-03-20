from flask import render_template

def handle_http_exception(e):
	error_message = e.description
	return "{}: {}".format(e.code, e.description), e.code

def handle_http_404(e):
	response = e.get_response()
	return render_template('error/404.html'), 404

# def handle_http_401(e):
# 	return '401 error', 401