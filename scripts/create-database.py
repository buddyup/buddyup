Script started on Mon 19 Aug 2013 07:04:26 PM PDT
]0;thang@ubuntu: ~/Desktop/capstone/sp2013cs487-team-gthang@ubuntu:~/Desktop/capstone/sp2013cs487-team-g$ ./scripts/create-database.py  
bash: ./scripts/create-database.py: Text file busy
]0;thang@ubuntu: ~/Desktop/capstone/sp2013cs487-team-gthang@ubuntu:~/Desktop/capstone/sp2013cs487-team-g$ ls
[0m[01;34mbuddyup[0m  [01;34mhomepage[0m  Procfile          [01;32mrunserver.py[0m  [01;34mthang_temp[0m
[01;34mdoc[0m      [01;34mmockcas[0m   requirements.txt  [01;34mscripts[0m       [01;34mvenv[0m
]0;thang@ubuntu: ~/Desktop/capstone/sp2013cs487-team-gthang@ubuntu:~/Desktop/capstone/sp2013cs487-team-g$ c[K. venv/bin/activate
(venv)]0;thang@ubuntu: ~/Desktop/capstone/sp2013cs487-team-gthang@ubuntu:~/Desktop/capstone/sp2013cs487-team-g$ ls
[0m[01;34mbuddyup[0m  [01;34mhomepage[0m  Procfile          [01;32mrunserver.py[0m  [01;34mthang_temp[0m
[01;34mdoc[0m      [01;34mmockcas[0m   requirements.txt  [01;34mscripts[0m       [01;34mvenv[0m
(venv)]0;thang@ubuntu: ~/Desktop/capstone/sp2013cs487-team-gthang@ubuntu:~/Desktop/capstone/sp2013cs487-team-g$ ls. venv/bin/activatels[K./scripts/create-databaase.py 
bash: ./scripts/create-database.py: Text file busy
(venv)]0;thang@ubuntu: ~/Desktop/capstone/sp2013cs487-team-gthang@ubuntu:~/Desktop/capstone/sp2013cs487-team-g$ ./scripts/create-databaase.py [K[K[K[K[K[K[K[A[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[K
[K[A[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[C[K[K[K[K[K[K[K[K[K[K[K[K[K[K[K[K[K[K[Kmockcas/mockcas.py 
 * Running on http://127.0.0.1:5000/
Traceback (most recent call last):
  File "./mockcas/mockcas.py", line 81, in <module>
    runner.run()
  File "/home/thang/Desktop/capstone/sp2013cs487-team-g/venv/local/lib/python2.7/site-packages/flask_runner.py", line 46, in run
    self.app.run(**args)
  File "/home/thang/Desktop/capstone/sp2013cs487-team-g/venv/local/lib/python2.7/site-packages/flask/app.py", line 772, in run
    run_simple(host, port, self, **options)
  File "/home/thang/Desktop/capstone/sp2013cs487-team-g/venv/local/lib/python2.7/site-packages/werkzeug/serving.py", line 710, in run_simple
    inner()
  File "/home/thang/Desktop/capstone/sp2013cs487-team-g/venv/local/lib/python2.7/site-packages/werkzeug/serving.py", line 692, in inner
    passthrough_errors, ssl_context).serve_forever()
  File "/home/thang/Desktop/capstone/sp2013cs487-team-g/venv/local/lib/python2.7/site-packages/werkzeug/serving.py", line 486, in make_server
    passthrough_errors, ssl_context)
  File "/home/thang/Desktop/capstone/sp2013cs487-team-g/venv/local/lib/python2.7/site-packages/werkzeug/serving.py", line 410, in __init__
    HTTPServer.__init__(self, (host, int(port)), handler)
  File "/usr/lib/python2.7/SocketServer.py", line 408, in __init__
    self.server_bind()
  File "/usr/lib/python2.7/BaseHTTPServer.py", line 108, in server_bind
    SocketServer.TCPServer.server_bind(self)
  File "/usr/lib/python2.7/SocketServer.py", line 419, in server_bind
    self.socket.bind(self.server_address)
  File "/usr/lib/python2.7/socket.py", line 224, in meth
    return getattr(self._sock,name)(*args)
socket.error: [Errno 98] Address already in use
(venv)]0;thang@ubuntu: ~/Desktop/capstone/sp2013cs487-team-gthang@ubuntu:~/Desktop/capstone/sp2013cs487-team-g$ exit
exit

Script done on Mon 19 Aug 2013 07:06:09 PM PDT
