from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo 
import datetime

app = Flask(__name__)
app.secret_key='aufrbsaudrbs'
app.config["MONGO_URI"] = "mongodb+srv://kimddil:aufrbs12@cluster0.92bnn.mongodb.net/myweb2?retryWrites=true&w=majority"
mongo = PyMongo(app) 
db = mongo.db 


def getArticleIndex():
  index=db.articles.find().sort("article_index",-1).limit(1)
  for i in index:
        rindex = i["article_index"] + 1
  return rindex



@app.route('/', methods=['GET', 'POST'])   
def main():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
        userid = request.form.get('id')
        userpw = request.form.get('pw')

        if userid == "" or userpw == "":
            flash("ID와 PASSWORD를 입력해주세요!")
            return render_template('main.html')

        users = mongo.db.users
        data = users.find_one({"user_id": userid })

        if data is None:
            flash("등록된 회원 정보가 존재하지 않습니다!")
            return redirect(url_for('main'))
        else:
            if data.get("user_pwd") == userpw:
                session["user_id"] = data.get("user_id")
                session["user_name"] = data.get("user_name")
                session["user_email"] = data.get("user_email")
                session["user_phone"]=data.get("user_phone")
                return redirect(url_for('home')) 
            else:
                flash("비밀번호가 틀렸습니다.")
                return redirect(url_for('main')) 
        return ""
  else:
    return render_template("main.html")
        
          
          
@app.route('/home.html', methods=['GET', 'POST'])
def home():
    name=session["user_name"]
    id=session["user_id"]
    article_list=db.articles.find({"article_id":id}).sort("article_time",-1)
    session["user_id"] = id
    return render_template('home.html', article_list=article_list)



@app.route('/article/<int:article_index>/')
def article(article_index):
    id=session["user_name"]
    article = db.articles.find_one({"article_index":article_index})
    session["user_id"] = article["article_id"]
    session["context"] = article["article_context"]
    session["title"]= article["article_title"]
    session["index"]= article["article_index"]
    return render_template('article.html', article=article)

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
      id = request.form['regi_id']
      pw = request.form['regi_pw']
      rpw = request.form['regi_rpw']
      name = request.form['regi_name']
      email= request.form['regi_email']
      phone= request.form['regi_phone']
      
      userinfo = {'user_id' : id ,'user_pwd': pw, 'user_name' : name,'user_email': email,'user_phone' :phone}
      users = mongo.db.users
      data = users.find_one({"user_id": id })
      
      if not (id and pw and rpw and name):
        flash("정보를 다 입력해주세요")
        return redirect(url_for('register'))
      elif pw != rpw:
        flash("비밀번호와 재확인 비밀번호가 일치하지 않습니다.")
        return redirect(url_for('register'))
      elif data != None:
        flash("이미 존재하는 아이디입니다.")
        return redirect(url_for('register'))
      else:
         users.insert_one(userinfo)
         flash("회원가입이 완료되었습니다.")
         return redirect(url_for('main'))
      return ""                 
    else:
      return render_template('register.html')

@app.route('/edit.html', methods=("GET", "POST"))
def edit():
    id=session["user_id"]
    title=session['title']
    context=session['context']
    index=session['index']
    article = db.articles.find_one({"article_index":index})
  
    if request.method == "POST":
      title = request.form.get('title')
      context = request.form.get('context') 
      if title != "" and context != "":
        db.articles.update({'article_index':index},{'$set':{'article_title':title, 'article_context' : context}})
        if 'image' in request.files:
          image=request.files['image']
          mongo.save_file(image.filename,image)
          db.articles.update({'article_index':index},{'$set':{'image_name':image.filename}})
        session["user_id"]=id 
        return redirect(url_for("article",article_index=index))
      else:
        flash("제목과 내용을 입력해주세요")
        session["user_id"]=id 
        return redirect(url_for('edit'))
    session["user_id"]=id
    return render_template('edit.html', article=article)

@app.route('/write.html', methods=["GET", "POST"])
def write():
    id=session["user_id"]
    user = db.users.find_one({"user_id":id})
    if request.method == "POST":
      title = request.form.get('title')
      context = request.form.get('context')
      article_id = id
      article_username=user.get("user_name")
      now=datetime.datetime.now()
      time=now.today()
      if title != "" and context != "":
        index=getArticleIndex()
        db.articles.insert_one({'article_id':article_id,'article_username':article_username,'article_title':title,'article_time': time,'article_index':index,'article_context':context})
        if 'image' in request.files:
          image=request.files['image']
          mongo.save_file(image.filename,image)
          db.articles.update({'article_index':index},{'$set':{'image_name':image.filename}})
        return redirect(url_for("article",article_index=index))
      else:
        flash("제목과 내용을 입력해주세요")
        session["user_id"]=id
        return redirect(url_for('write'))
    session["user_id"]=id 
    return render_template('write.html')

@app.route('/image/<image_name>')
def image(image_name):
  return mongo.send_file(image_name)

@app.route('/delete.html', methods=("GET", "POST"))
def delete():
    id=session["user_id"]
    index=session["index"]
    db.articles.remove({"article_index":index})
    session["user_id"]=id 
    return redirect(url_for("home"))
  
 
if __name__ == '__main__':
    app.run(debug=True)

              

              