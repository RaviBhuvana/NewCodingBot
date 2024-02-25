# subscriber.py
import redis
import torch
from functools import partial
import time
import dl_translate as dlt
from langdetect import detect
# from multiprocessing import Process, freeze_support, set_start_method
import json
import pickle
from torch.multiprocessing import Pool, set_start_method
try:
     set_start_method('spawn')
except RuntimeError:
    pass
import gc
gc.collect()
torch.cuda.empty_cache()
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '2, 3'


mt = dlt.TranslationModel.load_obj('saved_model')

r = redis.Redis(host='10.171.1.121', port=6379, db=0,decode_responses=False)#10.171.1.121

p = r.pubsub()

p.subscribe("12345")  
  
#'en': 'English', 'eng': 'English','es': 'Spanish', 'spa': 'Spanish','fr': 'French', 'fre/fra*': 'French','por': 'Portuguese','ja': 'Japanese', 'jpn': 'Japanese''ko': 'Korean', 'kor': 'Korean'
def read_root(did1,extra_arg,ba,did):                               
      all_languages_codes = {'en': 'English', 'eng': 'English','es': 'Spanish', 'spa': 'Spanish','fr': 'French', 'fre/fra*': 'French','por': 'Portuguese','ja': 'Japanese', 'jpn': 'Japanese','ko': 'Korean', 'kor': 'Korean' }
      b={'Arabic': 'ar_AR', 'Czech': 'cs_CZ', 'German': 'de_DE', 'English': 'en_XX', 'Spanish': 'es_XX', 'Estonian': 'et_EE', 'Finnish': 'fi_FI', 'French': 'fr_XX', 'Gujarati': 'gu_IN', 'Hindi': 'hi_IN', 'Italian': 'it_IT', 'Japanese': 'ja_XX', 'Kazakh': 'kk_KZ', 'Korean': 'ko_KR', 'Lithuanian': 'lt_LT', 'Latvian': 'lv_LV', 'Burmese': 'my_MM', 'Nepali': 'ne_NP', 'Dutch': 'nl_XX', 'Romanian': 'ro_RO', 'Russian': 'ru_RU', 'Sinhala': 'si_LK', 'Turkish': 'tr_TR', 'Vietnamese': 'vi_VN', 'Chinese': 'zh_CN', 'Afrikaans': 'af_ZA', 'Azerbaijani': 'az_AZ', 'Bengali': 'bn_IN', 'Persian': 'fa_IR', 'Hebrew': 'he_IL', 'Croatian': 'hr_HR', 'Indonesian': 'id_ID', 'Georgian': 'ka_GE', 'Khmer': 'km_KH', 'Macedonian': 'mk_MK', 'Malayalam': 'ml_IN', 'Mongolian': 'mn_MN', 'Marathi': 'mr_IN', 'Polish': 'pl_PL', 'Pashto': 'ps_AF', 'Portuguese': 'pt_XX', 'Swedish': 'sv_SE', 'Swahili': 'sw_KE', 'Tamil': 'ta_IN', 'Telugu': 'te_IN', 'Thai': 'th_TH', 'Tagalog': 'tl_XX', 'Ukrainian': 'uk_UA', 'Urdu': 'ur_PK', 'Xhosa': 'xh_ZA', 'Galician': 'gl_ES', 'Slovene': 'sl_SI'}    
      language_code = detect(extra_arg)       
      sentence = all_languages_codes.get(language_code) 
      try:          
         if language_code==did.get(did1):                                        
             con={"translation":{str(did1):extra_arg}}                               
             ba.update(con)
             r.publish("translate",json.dumps(ba)) 
             return con                              
         else:
                                                                                          
             la2 = all_languages_codes.get(did.get(did1))
             print(la2)
             bc= mt.translate(extra_arg, source=b.get(sentence.capitalize()),target=b.get(la2.capitalize()),generation_options=dict(num_beams=5, max_length=10000), batch_size=8)         
             con={"translation":{str(did1):bc} }
             print(bc)        
             ba.update(con)
             y=json.dumps(ba)           
             r.publish("translate",y)
             return  con
      except:          
         con={"translation":{str(did1):extra_arg}} 
         ba.update(con)
         print(ba)
         r.publish("123",json.dumps(ba) ) 
         return con
             
      
       
      
    
if __name__ == '__main__':
    while True:
        message = p.get_message()
        if message: 
            print(message)          
            a=message.get('data')                            
            if a!=1 :                
                bl=json.loads(a)           
                text1=bl.get("text")                  
                did=bl.get("Language")                
                with Pool(5) as h:
                    h.map(partial(read_root, extra_arg=text1,ba=bl,did=did), did)                        
                            
            else:
                  print("server is running")   


