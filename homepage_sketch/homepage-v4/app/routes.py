from flask import Flask, render_template
 
app = Flask(__name__)      
 
@app.route('/')
def home():
  return render_template('homepage.html')
@app.route('/logo')
def logo():
  return render_template('profile.html')

@app.route('/home')
def home1():
  return render_template('homepage.html')
 
@app.route('/buddies')
def buddies():
  return render_template('findgroup.html')
  
@app.route('/resources')
def resources():
   return render_template('forum.html')
   
@app.route('/message')
def message():
   return render_template('message.html')
   
@app.route('/invitations')
def invitations():
   return render_template('invitation.html')

@app.route('/editprofile')
def editprofile():
   return render_template('editprofile.html')
   
@app.route('/help')
def help():
   return render_template('message.html')
@app.route('/setting')
def setting():
   return render_template('message.html')

@app.route('/calendar')
def calendar():
   return render_template('calendar.html')

@app.route('/calendar-popup')
def calendarpopup():
   return render_template('calendar-popup.html')

@app.route('/admin/dashboard')
def dashboard():
   return render_template('admin/dashboard.html')

@app.route('/admin/userManagement')
def userManagement():
   return render_template('admin/userManagement.html')

@app.route('/admin/forumManagement')
def forumManagement():
   return render_template('admin/forumManagement.html')

@app.route('/q&a/id=1')
def q1():
   return render_template('q&a/id=1.html')

if __name__ == '__main__':
  app.run(debug=True)
