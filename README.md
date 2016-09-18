Please run "pip install -r requirements.txt"


ltpout.py:
--------------
    main python file to run the code to extract the address information
    As to load module, please refer to __init__ 
    As to get an address from one sentence, please refer to __call__
    Please refer to the main function of ltpout.py for an example

ltpout_try.py:
--------------
    The code will be deleted in the future. 
    It is the first version of main python file to run the code to extract the address information

accuracy.ipynb:
--------------
    It is used to check the performance of codes in ltpout_try.py. 
    There are some commented print that can be used to show the different between the address given and the address extract from one sentence, can be used to mofidy the model

segmentor.txt:
--------------
    Personal dictionary for word segmentation

postagger.txt:
-------------
    Personal dictionary for POS

token_address_weak.txt
-------------
    Words that seems to indicates an sentence contains the address information
    Should contains two lines. 
    The first line contains the Chinese words that can be splited into several words.
    The second line contains the Chinese words that can not be splited
    
token_address.txt
------------
    Words that indicates that an sentence contains the address information strongly
    The first line contains the Chinese words that can be splited into several words.
    The second line contains the Chinese words that can not be splited

token_address_remove.txt
-------------
    Words that are not address information but includes words in token_address_weak.txt

exception.txt:
-------------
    Some addresses not be recognized by the code of ltpout.py. 

ltp_models
---------------
    The models trained by ltp. Please download them from https://pan.baidu.com/share/link?shareid=1988562907&uk=2738088569. In this ltp_models, please include cws.model, pos.model and parser.model


