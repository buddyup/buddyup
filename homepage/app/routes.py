from flask import Flask, render_template
 
app = Flask(__name__)      
 
@app.route('/')
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
@app.route('/note')
def note():
   return render_template('note.html')
@app.route('/findgroup')
def findgroup():
   return render_template('findgroup.html')
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
@app.route('/group_result')
def group_result():
    return render_template('group_result.html') 
if __name__ == '__main__':
  app.run(debug=True)