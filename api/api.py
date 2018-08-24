# import sys
# sys.path.insert(0,'bin')
# from gg import *
from flask import Flask
from flask import request
from flask import jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
import json


app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.askbox


def toJson(data):
	return json.dumps(data, default=json_util.default)

##########route binding start##########

#####user account session start#####
user_db=db.user

#create account#
@app.route('/user/register',methods=["POST"])
def acc_get():
        data=request.form.to_dict()
        print (request.form)
        print ("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        register_json = {
                "user_id": data["user_id"],
                "user_name": data["user_name"],
                "email": data["email"],
                "age": data["age"],
                "bio": data["bio"],
                "post_reputation": 0,
                "ans_reputation": 0,
                "password": data["password"]
		}
        user_db.insert(register_json)
        return toJson({"status": "ok", "data": "account registered successfully"})
        

#####user account session stop#####


#####post section start#####

post_db = db.post

#fine one post
@app.route('/post/get/<post_id>',methods=["GET"])
def get_post(post_id):
   json = []
   data = post_db.find({"_id": ObjectId(post_id)})
   for a in data:
    json.append(a)
   return toJson({"status": "ok", "data": json})


#find all post
@app.route('/post/get',methods=["GET"])
def get_post_all():
   data = post_db.find()
   json = []
   for a in data:
    json.append(a)
   return toJson({"status": "ok", "data": json})


#uploadpost
@app.route('/post/post',methods=["POST"])
def post_get():
  # print request.args.get('name')
  # print request.data
  data = request.form.to_dict()
  print (data["user_id"])
  print (data["user_name"])
  print (data["tag"])
  print (data["content"])
  post_json = {
    "title":data["title"],
    "user_id":data["user_id"],
    "user_name":data["user_name"],
    "tag":data["tag"].split(","),
    "content":data["content"],
    "upvote":[],
    "downvote":[],
    "date":data["date"],
    "request":[]
    }
  post_db.insert_one(post_json)
  return toJson({"status": "ok", "data": "post successfully created"})

#####post section end#####


#####post upvote & downvote session start######


#upvote&downpost
@app.route('/post/upvote',methods=["POST"])
def post_vote():
       data = request.form.to_dict()
       user_id = data["user_id"]
       post_id = data["post_id"]
       user_name = data["user_name"]
       vote = data["vote"]

       up_flag=0
       down_flag=0
       result = post_db.distinct("user_id",{"_id":ObjectId(data["post_id"])})
       for owner in result:
               owner_id=owner
       print(owner_id,"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@") 
       up_result =  post_db.distinct("upvote.user_id",{'_id':ObjectId(data["post_id"])})
       for up_id in up_result:
               if user_id==up_id:
                       up_flag=1
                       break
               else:
                        up_flag=0
       down_result = post_db.distinct("upvote.user_id",{'_id':ObjectId(data["post_id"])})
       for down_id in down_result:
               if user_id==down_id:
                       down_flag=1
                       break
               else:
                       down_flag=0 
       if vote == "1":
               print(up_flag,"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
               print(down_flag,"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
               if up_flag==0:
                       if down_flag==0:
                               post_db.update({"_id":ObjectId(data["post_id"])},{"$addToSet":{"upvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               db.user.update({"user_id":owner_id},{"$inc":{"post_reputation":1}})
                       elif down_flag==1:
                               post_db.update({"_id":ObjectId(data["post_id"])},{"$pull":{"downvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               post_db.update({"_id":ObjectId(data["post_id"])},{"$addToSet":{"upvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               db.user.update({"user_id":owner_id},{"$inc":{"post_reputation":1}})
               elif up_flag==1:
                       post_db.update({"_id":ObjectId(data["post_id"])},{"$pull":{"upvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                       db.user.update({"user_id":owner_id},{"$inc":{"post_reputation":-1}})
               return toJson({"status": "ok", "data": "you successfully upvoted"})
       elif vote == "0":
               if down_flag==0:
                       if up_flag==0:
                               post_db.update({"_id":ObjectId(data["post_id"])},{"$addToSet":{"downvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               db.user.update({"user_id":owner_id},{"$inc":{"post_reputation":-1}})
                       elif up_flag==1:
                               post_db.update({"_id":ObjectId(data["post_id"])},{"$pull":{"upvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               post_db.update({"_id":ObjectId(data["post_id"])},{"$addToSet":{"downvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               db.user.update({"user_id":owner_id},{"$inc":{"post_reputation":-1}})
               elif down_flag==1:
                       post_db.update({"_id":ObjectId(data["post_id"])},{"$pull":{"downvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                       db.user.update({"user_id":owner_id},{"$inc":{"post_reputation":1}})
               return toJson({"status": "ok", "data": "you successfully downvoted"})
        

#####post upvote & downvote session start######

#####tag_used_count section start#####
@app.route('/tag/<tag_name>',methods=["GET"])
def get_tag(tag_name):
        data = post_db.find({"tag":tag_name}).count()
        result = json.JSONEncoder().encode({"count":data})
        return toJson({"status": "ok", "data": result})

#####tag_used_count section stop#####

##### answer section start #####
ans_db = db.ans
#uploadanswer
@app.route('/answer/post',methods=["POST"])
def post_answer():
    data = request.form.to_dict()
    
    post_json = {
    "post_id":data["post_id"],
 	  "user_id":data["user_id"],
		"user_name":data["user_name"],
		"answer":data["answer"],
		"upvote":[],
		"downvote":[],
		"date":data["date"]
		}	
    # post_json = {
    # "name":data["name"],
    # "post_id":"595b6d6b6626a0361f6a9f21"
    # }
    ans_db.insert(post_json) 
    return toJson({"status": "ok", "data": "answer successfully uploaded"})


#get answer by post_id
@app.route('/answer/get/<post_id>',methods=["GET","POST"])
def get_answer(post_id):
   data = ans_db.find({"post_id": post_id})
   json = []
   for a in data:
    json.append(a)
   return toJson({"status": "ok", "data": json})
##### get answer section end #####

#upvote&down_answer
@app.route('/answer/upvote',methods=["POST"])
def answer_vote():
       data = request.form.to_dict()
       user_id = data["user_id"]
       post_id = data["post_id"]
       user_name = data["user_name"]
       vote = data["vote"]
       up_ans=0
       down_ans=0
       print (vote)
       result = post_db.distinct("user_id",{"_id":ObjectId(data["post_id"])})
       for owner in result:
               owner_id=owner
       up_result =  ans_db.distinct("upvote.user_id",{"post_id":data["post_id"]})
       for up_id in up_result:
               if user_id==up_id:
                       up_ans=1
                       break
               else:
                        up_ans=0
       down_result = ans_db.distinct("upvote.user_id",{"post_id":data["post_id"]})
       for down_id in down_result:
               if user_id==down_id:
                       down_ans=1
                       break
               else:
                       down_ans=0 
       if vote == "1":
               if up_ans==0:
                       if down_ans==0:
                               ans_db.update({"post_id":data["post_id"]},{"$addToSet":{"upvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               db.user.update({"user_id":owner_id},{"$inc":{"ans_reputation":1}})
                       elif down_ans==1:
                               ans_db.update({"post_id":data["post_id"]},{"$pull":{"downvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               ans_db.update({"post_id":data["post_id"]},{"$addToSet":{"upvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               db.user.update({"user_id":owner_id},{"$inc":{"ans_reputation":1}})
               elif up_ans==1:
                       ans_db.update({"post_id":data["post_id"]},{"$pull":{"upvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                       db.user.update({"user_id":owner_id},{"$inc":{"ans_reputation":-1}})
               return toJson({"status": "ok", "data": "you successfully upvoted"})
       elif vote == "0":
               if down_ans==0:
                       if up_ans==0:
                               ans_db.update({"post_id":data["post_id"]},{"$addToSet":{"downvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               db.user.update({"user_id":owner_id},{"$inc":{"ans_reputation":-1}})
                       elif up_ans==1:
                               ans_db.update({"post_id":data["post_id"]},{"$pull":{"upvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               ans_db.update({"post_id":data["post_id"]},{"$addToSet":{"downvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                               db.user.update({"user_id":owner_id},{"$inc":{"ans_reputation":-1}})
               elif down_ans==1:
                       ans_db.update({"post_id":data["post_id"]},{"$pull":{"downvote":{"user_id":data["user_id"],"user_name":data["user_name"]}}})
                       db.user.update({"user_id":owner_id},{"$inc":{"ans_reputation":1}})
               return toJson({"status": "ok", "data": "you successfully upvoted"})
        

#####answer upvote & downvote session end######'''

#####post delete######
@app.route('/post/delete/<post_id>',methods=['GET'])
def post_del(post_id):
        post_db.remove({"_id":ObjectId(post_id)})
        return toJson({"status": "ok", "data": "post successfully deleted"})

##### answer section end #####

##########route binding end##########

#Cross-origin resource sharing
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

app.run(ssl_context='adhoc',host='askbox.com', port=9999,debug=True,threaded=True)

