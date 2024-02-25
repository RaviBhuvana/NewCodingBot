import numpy as np
import pymongo
import torch
from fastapi import FastAPI

myclient = pymongo.MongoClient("mongodb://mongo-test1:27017,mongo-test2:27017,mongo-test3:27017/Unifiedring?w=0&readPreference=nearest&replicaSet=replconfig01&auto_reconnect=true")
mydb = myclient["Unifiedring"]
mycol = mydb["urr_meeting_closecaptions"]
mycol1 = mydb["MOM_CHANGES"]
from summarizer import Summarizer
model = Summarizer()
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd
from pydantic import BaseModel
# pip install yake #
import yake
kw_extractor = yake.KeywordExtractor()


class Item(BaseModel):
    uuid:str    
    text:list
    



def key(Text):
    a=[]
    language = "en"
    max_ngram_size = 3
    deduplication_threshold = 0.9
    numOfKeywords = 20
    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
    keywords = custom_kw_extractor.extract_keywords(Text)
    for kw in keywords:
        a.append(kw[0])
    return a


def MOM(document):    
    get_summary=document             
    result = model(get_summary, min_length=20)
    summary = "".join(result) 
    return summary

   
  
app = FastAPI()
################################  over all MOM API ##############################################################
@app.get("/read_root")
def read_root(uuid: str):
    try:    
        ie = mycol.find_one({"uuid": uuid})
        if ie.get("MOM") != None:
            mom= ie.get("MOM")       
            return {"MOM":mom}
        else:
            se = set()
            dic = {}
            dic1 = []
            tex = ""
            final_dic={}
                ################ we are getting speakers name ##########################
            for item in ie.get("transcripts"):
                se.add(item.get("speakerName"))
                tex += " "+item.get('text')
            se1 = list(se)
                ####################### we are collect the text ################################
            for i in se1:
                b = ""
                for item in ie.get("transcripts"):
                    if i == item.get("speakerName"):
                        b += item.get("text")
                dic.update({i: b})               
            hari=MOM(tex)
            haran=[{"name":"over_all summary","summary":hari}]
            final_dic.update({"over_all summary":haran})
            print(tex) 
            print(dic)    
            for i in dic:
                y = MOM(dic.get(i))
                dic1.append(({"name": i, "summary": y}))
            final_dic.update({"participant_mom":dic1})      
            z=key(tex)
            final_dic.update({"key_words":z}) 
            mycol.update_one({"name":uuid},{"$set": {"MOM":final_dic }})   
            return final_dic    
    except:
        return {"statusCode": 422, "message": f"No available meeting  {uuid}"}
###########################  user requirement correction text update  API #############################################################
@app.post("/write_root")
def write_root(item:Item):    
    mycol1.insert_one({"uuid":item.uuid,"text":item.text})
    return {"Response":"successful"}
########################### correction text get   API #############################################################
@app.get("/get_root")
def get_root(uuid:str):
    x = mycol1.find_one({"uuid":uuid})   
    b=x.get("text")
    return {"text":b}