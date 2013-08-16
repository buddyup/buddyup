from flask import Flask, render_template
 
app = Flask(__name__)      
 
@app.route('/')
def intro():
  return render_template('intro.html')
@app.route('/welcome')
def welcome():
  return render_template('welcome.html')
@app.route('/home')
def home():
  return render_template('homepage.html')
@app.route('/profile')
def profile():
  return render_template('profile.html') 
@app.route('/resources')
def resources():
   return render_template('forum.html')
   
@app.route('/message')
def message():
   return render_template('message.html')
@app.route('/invite')
def invite():
   return render_template('invite.html')
   
@app.route('/invite2group')
def invite2group():
   return render_template('invite2group.html')

@app.route('/editprofile')
def editprofile():
   return render_template('editprofile.html')
   
@app.route('/help')
def help():
   return render_template('help.html')
@app.route('/setting')
def setting():
   return render_template('setting.html') 
@app.route('/note')
def note():
   return render_template('note.html')
@app.route('/findgroup')
def findgroup():
   return render_template('findgroup.html')
@app.route('/findgrouperror')
def findgrouperror():
   return render_template('findgroup_error.html')
@app.route('/creategroup')
def creategroup():
   return render_template('creategroup.html')   
@app.route('/calendar')
def calendar():
   return render_template('calendar.html') 
@app.route('/buddies')
def buddies():
   return render_template('buddies.html')   
@app.route('/404')
def error404():
   return render_template('404.html') 
@app.route('/500')
def error500():
   return render_template('500.html')
@app.route('/503')
def error503():
   return render_template('503.html')
@app.route('/400')
def error400():
   return render_template('400.html')
@app.route('/403')
def error403():
    return render_template('403.html') 
@app.route('/landing')
def landing():
    return render_template('landing.html')
@app.route('/landing2')
def landing2():
    return render_template('landing2.html')
@app.route('/group_result')
def group_result():
    return render_template('group_result.html') 
@app.route('/viewevent')
def viewevent():
    return render_template('viewevent.html') 
@app.route('/q&a/id=1')
def q1():
   return render_template('q&a/id=1.html')
@app.route('/admin/dashboard')
def dashboard():
   return render_template('admin/dashboard.html')

@app.route('/admin/userManagement')
def userManagement():
   return render_template('admin/userManagement.html')

@app.route('/admin/forumManagement')
def forumManagement():
   return render_template('admin/forumManagement.html')
@app.route('/search')
def search():
  return render_template('search.html')     
if __name__ == '__main__':
  app.run(debug=True)