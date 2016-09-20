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
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        data = json.loads(self.data_string)
        # get the chunk number list
        previous_uploads=data['previous_uploads']
        
        speed_list=[]
        chunknumber_list=[]
        x_list=[]
        for k in previous_uploads:
            speed_list+=k['speed_mbps'],
            chunknumber=k['file_size']/k['chunk_size']
            chunknumber_list+=chunknumber,
            chunknumber_log=math.log(chunknumber, 200)
            x_list.append([1,chunknumber_log,chunknumber_log**2])

        print "chunknumbers are:"+str(chunknumber_list)
        chunknumber_array=np.array(chunknumber_list)

        X=np.array(x_list)
        Y=np.array(speed_list)
        X_tans=np.transpose(X)
        Theta=np.dot( np.dot(inv(np.dot(X_tans,X)), X_tans), Y)

        print "Theta is:"+str(Theta)

        predictions=np.dot(X,Theta)
        print "input are      :"+str(speed_list)
        print "predictions are:"+str(predictions)
        diag=[]
        for i in xrange(1,371):
            pro=float(1)/6400*i
            xx=np.array([1, pro, pro**2, 1/pro, math.exp(pro)])
            prediction=np.dot(xx, Theta)
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