# coding: utf-8

def model_load(csw_model='ltp_models/cws.model', csw_dictionary='segmentor.txt', pos_model='ltp_models/pos.model', pos_dictionary='postagger.txt',parse_model='ltp_models/parser.model'):

    from pyltp import Segmentor
    segmentor = Segmentor()  # 初始化实例
    segmentor.load_with_lexicon('ltp_models/cws.model','segmentor.txt')  # 加载模型
    from pyltp import Postagger
    postagger = Postagger() # 初始化实例
    postagger.load_with_lexicon('ltp_models/pos.model','postagger.txt')  # 加载模型
    from pyltp import Parser
    parser = Parser() # 初始化实例
    parser.load('ltp_models/parser.model')  # 加载模型
    return segmentor, postagger, parser

def parse_sentence(segmentor, postagger, parser, sentence='北京市望京soho'):
    words = segmentor.segment(sentence)  # 分词
    print '\t'.join(words)
    #segmentor.release()  # 释放模型
    postags = postagger.postag(words)  # 词性标注
    print '\t'.join(postags)
    #postagger.release()  # 释放模型
    arcs = parser.parse(words, postags)  # 句法分析
   # print "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs)
    #parser.release()  # 释放模型
    print [x.relation for x in arcs]

    return words, postags, arcs


def word_in(word, address):
    word_new = word.decode('utf-8')
    w = word_new[len(word_new)-1]
    for w_ in address:
        if w == w_.decode('utf-8'):
            return True
    return False


def word_in_first(word):
    word_new = word.decode('utf-8')
    if word in ['道路', '原路'] or len(word_new) <= 1:
        return False
    w = word_new[len(word_new)-1]
    for w_ in ['路', '街']:
        if w == w_.decode('utf-8'):
            return True
    return False


def address_extract(words, postags, arcs):

    address = ['驾校', '招待所','前台', '影棚', '商场','政府','证券','大厦', '大学','中学','小学', '学校', '科技园','广场', '公园', '酒店', '花园', '中心', '单元', '公司', '研究院', '公寓', '店铺', '山庄', '影城', '胡同', '大道', '学堂', '出口', '商铺', '剧场', '专柜', '门诊', '医院','房间', '总部', '有限公司', '分行', '银行', '支行', '俱乐部', '路口','柜台', '学院']
    word_address = ['省','市','县','乡','区', '镇','街','号','路', '栋','座','层','楼','室', '弄', '店', '院', '城', '园', '馆', '厅','房','站', '门','村', '幢','期', '寺', '庙', '档', '铺', '部', '局']
    word2_address = ['省','市','县','乡','区', '镇','街','路', '栋','座','层','楼','室', '店', '院', '城', '园', '馆', '厅', '村', '幢', '寺', '庙']
#    word_remove = ['时']
    temp = []
    solution = []
    for i in range(len(arcs)):
        if (temp != [] and i == len(arcs)-1 and arcs[i].relation not in ['WP'] and (postags[i] not in ['v', 'r'] or words[i] in ['弄'])) or (i == len(arcs)-1 and postags[i] in ['ni', 'ns', 'nl']) or (i == len(arcs)-1 and word_in_first(words[i])):
            temp.append(i)
            #print temp
#            if words[len(temp)-1] in word_remove:
#                del temp[len(temp)-1]
#                if len(temp) !=0 and postags[temp[0]] not in ['nz', 'n', 'ns', 'nd', 'nh', 'ni', 'nl']:
#                    del temp[0] 
            while len(temp) >=1 and not (words[temp[-1]] in address or word_in(words[temp[-1]], word_address)) and postags[temp[-1]] not in ['j', 'm', 'nd', 'ni', 'nl', 'ns', 'nz', 'ws', 'i', 'q'] and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['送'] and words[temp[0]-1] in ['到', '至']) and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['地址', '住']) and not (postags[temp[-1]] in ['n'] and temp[0] >=1 and words[temp[0]-1] in ['住']):
                temp.pop()
            if len(temp) >= 1:
                solution.append(temp)

      #      print solution
        elif (arcs[i].relation == 'ATT' and postags[i] not in ['p', 'r', 'q'] and words[i] not in ['大杯','超大杯','小杯']) or postags[i] in ['ns', 'ni', 'nl']:
            temp.append(i)
            #print temp
        elif temp != [] and (words[i] in address or word_in(words[i],word_address)):
            temp.append(i)
        elif word_in_first(words[i]):
            temp.append(i)
        elif temp != [] and postags[i] in ['m', 'ws']:
            temp.append(i)
        elif temp != []:   
#            if words[temp[len(temp)-1]] in word_remove:
#                del temp[len(temp)-1]
#                if len(temp) !=0 and postags[temp[0]] not in ['nz', 'n', 'ns', 'nd', 'nh', 'ni', 'nl']:
#                    del temp[0]
            #print temp
            while len(temp) >=1 and not (words[temp[-1]] in address or word_in(words[temp[-1]], word_address)) and postags[temp[-1]] not in ['j', 'm', 'nd', 'ni', 'nl', 'ns', 'nz', 'ws', 'i', 'q'] and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['送'] and words[temp[0]-1] in ['到', '至']) and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['地址', '住']) and not (postags[temp[-1]] in ['n'] and temp[0] >=1 and words[temp[0]-1] in ['住']):
                temp.pop()
            if len(temp) >= 1:
                solution.append(temp)
            temp = []
        else:
            temp = []

    temp_solution = []
    for temp in solution:
        #print temp
        for idx in temp:
            if postags[idx] in ['ns', 'ni', 'nl'] or words[idx] in address or word_in(words[idx], word_address):
                if len(temp_solution) >= 1 and (temp[0] - temp_solution[-1][-1] == 2) and words[temp[0]-1] in ['的', '与', '和']:
                    last_temp = temp_solution.pop()
                    last_temp.append(temp[0]-1)
                    last_temp.extend(temp)
                    temp = last_temp
                if arcs[temp[-1]].relation == 'VOB' and arcs[temp[-1]].head == temp[0] + 1:
                    del temp[0]
                    #print temp
                for idx1 in temp:
                    if postags[idx1] in ['ns', 'ni', 'nl'] or words[idx1] in address or word_in(words[idx1], word2_address):
                        temp_solution.append(temp)
                        break
                break
    #print temp_solution           
    final_solution = []
    for temp in temp_solution:
        final_solution.append(''.join(words[i] for i in temp))

    return final_solution



def word_fix(word, drink_confuse):
    flag = False
    for temp in drink_confuse:
        if temp in word:
            flag = True
            break
    if flag:
        new_word = word.decode('utf-8')
        left = 0
        right = len(new_word)
        for i in range(len(new_word)):
            if new_word[i].encode('utf-8') in drink_confuse and i == left:
                left = i+1
            elif new_word[i].encode('utf-8') in drink_confuse:
                right = i
        word = new_word[left:right].encode('utf-8')
    return word

def drink_from_dictionary(sentence):
    with open('drink_dictionary.txt','r') as fp:
        drink_dictionary = regex.split(fp.readline().strip('\n'))   
    for temp in drink_dictionary:
        if temp in sentence:
            return [temp]
    return []


def drink_extract(words, postags, arcs):
    import re
    regex = re.compile('\s*,\s*')
    with open('drink_end.txt','r') as fp:
        drink_end = regex.split(fp.readline().strip('\n'))   
    with open('drink_remove.txt','r') as fp:
        drink_remove = regex.split(fp.readline().strip('\n'))   
    with open('drink_confuse.txt','r') as fp:
        drink_confuse = regex.split(fp.readline().strip('\n'))
    for temp in drink_remove:
        print temp
 
    temp = []
    solution = []
    for i in range(len(arcs)):
 #       if words[i] in drink_remove:
  #          temp = []
        if words[i] in drink_end or word_fix(words[i], drink_confuse) in drink_end:
            temp.append(i)
            if i < len(arcs) -1 and words[i+1] in drink_end:
                continue
            solution.append(temp)
            temp = []
        elif i < len(arcs) - 1 and words[i] in ['flat', 'Flat', 'FLAT'] and words[i+1] in ['white', 'White', 'WHITE']:
            temp.append(i)
            temp.append(i+1)
            if i < len(arcs) - 2 and words[i+2] in drink_end:
                continue
            solution.append(temp)
            temp = []
        elif arcs[i].relation == 'ATT' and postags[i] not in ['m', 'p', 'r', 'q', 'e', 'ws'] and words[i] not in drink_remove:
            print('yes')
            temp.append(i)
        else:
            temp = []

    temp_solution = []
    for temp in solution:
        if len(temp_solution) >= 1 and (temp[0] - temp_solution[-1][-1] == 1):
            last_temp = temp_solution.pop()
            last_temp.extend(temp)
            temp = last_temp
        temp_solution.append(temp)

    final_solution = []
    for temp in temp_solution:

        while words[temp[0]].decode('utf-8')[0].encode('utf-8') in drink_confuse and words[temp[0]] not in drink_end:
            if len(temp) >=2 and words[temp[0]] in ['热'] and words[temp[1]] in ['巧克力']:
                break
            if words[temp[0]] in ['冰摇', '冰搖']:
                break
            words[temp[0]] = words[temp[0]].decode('utf-8')[1:].encode('utf-8')
            if not words[temp[0]]:
                temp = temp[1:]

        while words[temp[-1]].decode('utf-8')[-1].encode('utf-8') in drink_confuse and words[temp[-1]] not in drink_end:
            words[temp[-1]] = words[temp[-1]].decode('utf-8')[:-1].encode('utf-8')
            if not words[temp[-1]]:
                temp = temp[:-1]
        if len(temp) == 1 and words[temp[0]] in ['咖啡']:
            continue
#        string = ''
#        for i in temp:
#            if words[i] in ['white', 'White']:
#                string = string + ' '+words[i]
#            else:
#                string = string + words[i]
        final_solution.append(''.join(words[i] for i in temp))
#        final_solution.append(string)

            

    return final_solution





if __name__ == '__main__':
    from time import time
    start = time()
    #import chardet
    segmentor, postagger, parser = model_load()
    end = time()
    sentence = '星巴克热卡布奇诺大杯'
    words, postags, arcs  = parse_sentence(segmentor, postagger, parser, sentence)
    end1 = time()
    solution = drink_extract(words, postags, arcs)
    end2 = time()
    for temp in solution:
        print(temp)

      
    print(end-start)
    print(end1-end)
    print(end2-end)

