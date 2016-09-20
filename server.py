from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import math
import numpy as np
from numpy.linalg import inv
from scipy.optimize import leastsq
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
from scipy import interpolate

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        self._set_headers()
        print "in post method"
        print "Content length is:"+self.headers['Content-Length']
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        data = json.loads(self.data_string)
        # get the chunk number list
        previous_uploads=data['previous_uploads']
        
        chunksize_list=[]
        filesize_list=[]
        speed_list=[]
        chunknumber_list=[]
        chunknumber_log_list=[]
        chunknumber_log_sqr_list=[]
        for k in previous_uploads:
            filesize_list+=k['file_size'],
            chunksize_list+=k['chunk_size'],
            speed_list+=k['speed_mbps'],
            chunknumber_log=math.log(k['file_size']/k['chunk_size'], 320)
            chunknumber_log_list+=chunknumber_log,
            chunknumber_log_sqr_list+=chunknumber_log**2

        chunksize_array=np.array(chunksize_list)
        filesize_array=np.array(filesize_list)
        speed_array=np.array(speed_list)
        chunknumber_array=np.array(chunknumber_list)
        chunknumber_log_array=np.array(chunknumber_log_list)
        chunknumber_log_sqr_array=np.array(chunknumber_log_sqr_list)

        plt.plot(chunknumber_log_array, speed_array, 'ro', ms=5)
        spl = UnivariateSpline(chunknumber_log_array, speed_array)

        plt.plot(chunknumber_log_array, spl(chunknumber_log_array), 'g', lw=3)

        plt.show()

        predictions=[]
        for k in previous_uploads:
            fs=k['file_size']
            cs=k['chunk_size']
            pro=float(cs)/fs
            #chunk_number=fs/cs
            #chunk_number=chunk_number+1 if fs%cs else chunk_number
            xx=np.array([1, pro, pro**2, fs/cs, math.exp(pro)])
            prediction=1/(np.dot(xx, Theta))
            predictions.append(prediction)
        print "input are      :"+str(map(lambda k:k['speed_mbps'], previous_uploads))
        print "predictions are:"+str(predictions)
        diag=[]
        for i in xrange(1,371):
            pro=float(1)/6400*i
            xx=np.array([1, pro, pro**2, 1/pro, math.exp(pro)])
            prediction=1/(np.dot(xx, Theta))
            diag.append(prediction)
        plt.plot(range(1,371),diag)
        plt.show()
        current_file_size=data['current_upload']
        reply={}
        reply['chunk_size']=np.array((1,float(1)/c))
        self.wfile.write(json.dumps(reply))
        return


def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

if len(argv) == 2:
    run(port=int(argv[1]))
else:
    run()