# coding: utf-8
class AddressDrinkParser(object):
    """It is used to extract address information from one sentence
    Please refer to LTP(http://www.ltp-cloud.com/intro/) for reference. We first generate one phrase from a sentence via "ATT" in Dependency Parsing. Then we check whether there is address information. If it is, we decide that the phrase contains address information. After that, we do some pattern based modifications to the phrase. 
    As for the trained model, please download from https://pan.baidu.com/share/link?shareid=1988562907&uk=2738088569. Besides, please install pyltp, which is the python interface of LTP.
   

    Attributes:
    ------------- 
        segmentor: Used for word segmentation
        postagger: Used for Part of Speech 
        parser: Used for generate syntax tree
        recognizer: Used for name entity recognition
        token1_address: A list. Used for store the words that suggests that the phrase contains address information strongly. Please refer to the first line of token_address.txt. It should be the subset of token1_address_weak
        token2_address: A list. Used for store the words that suggests that the phrase contains address information strongly. Please refer to the second line of token_address.txt. It should be the subset of token2_adderess_weak
        token1_address_weak: A list. Used for store the words that suggests that the phrase contains address information weakly. Please refer to the first line of token_address_weak.txt
        token2_address_weak: A list. Used for store the words that suggests that the phrase contains address information weakly. Please refer to the second line of token_address_weak.txt
        token3_address_weak: A list. Used for store the words that suggests that the phrase contains address information weakly. It can be some special word that can be address. Please refer to the third line of token_address_weak.txt
        token_address_remove: A list. To remove the word that is not address information but contains words in token_address_week. Please refer to the file toaken_address_remove.txt       
        token_address_exception: A list. Remove some words that are not address
    """

    def __init__(self, csw_model='ltp_models/cws.model', csw_dictionary='segmentor.txt', pos_model='ltp_models/pos.model', pos_dictionary='postagger.txt',parse_model='ltp_models/parser.model', ner_model='ltp_models/ner.model', token_address='token_address.txt', token_address_weak='token_address_weak.txt', token_address_remove='token_address_remove.txt', token_address_exception='token_address_exception.txt', drink_dictionary='drink_dictionary.txt', drink_end='drink_end.txt', drink_remove='drink_remove.txt', drink_confuse='drink_confuse.txt'):
        """
        load the modeles

        Args:
        --------------
            csw_model: word segmentation models
            pos_model: part of speech models
            ner_model: named entity recognition models
            ner_model: named entity recognition models
            csw_dictionary: personal dictionary for word segmentation
            pos_dictionary: perfonal dictionary for part of speech
            token_address: words that indicates that a phrase contains an address. It should be a subset of token_address_weak
            token_address_weak: words tha indicates that a phrase contains an address weakly. 
            token_address_remove: words that are not address information but contains words in token_address_weak
            drink_dictionary: drink from the file "sku_id.txt"
            drink_end = drink_end: the word that the drink might end with
            drink_remove = drink_remove: the word that does not belong to drink
            drink_confuse = drink_confuse: the word that might attach to the word in drink( due to the problem of segmentation of LTP)

        """
        from pyltp import Segmentor
        segmentor = Segmentor()  # 初始化实例
        segmentor.load_with_lexicon(csw_model,csw_dictionary)  # 加载模型
        from pyltp import Postagger
        postagger = Postagger() # 初始化实例
        postagger.load_with_lexicon(pos_model,pos_dictionary)  # 加载模型
        from pyltp import Parser
        parser = Parser() # 初始化实例
        parser.load(parse_model)  # 加载模型
        from pyltp import NamedEntityRecognizer
        recognizer = NamedEntityRecognizer() # 初始化实例
        recognizer.load(ner_model)  # 加载模型

        import re
        regex = re.compile('\s*,\s*')
        with open(token_address,'r') as fp:
            token1_address = regex.split(fp.readline().strip('\n'))   
            token2_address = regex.split(fp.readline().strip('\n'))
        with open(token_address_weak, 'r') as fp:
            token1_address_weak = regex.split(fp.readline().strip('\n'))   
            token2_address_weak = regex.split(fp.readline().strip('\n'))
            token3_address_weak = regex.split(fp.readline().strip('\n'))
        with open(token_address_remove, 'r') as fp:
            token_address_remove = regex.split(fp.readline().strip('\n'))   
        with open(token_address_exception, 'r') as fp:
            token_address_exception = regex.split(fp.readline().strip('\n'))   

        self.segmentor = segmentor
        self.postagger = postagger
        self.parser = parser
        self.recognizer = recognizer

        self.token1_address = token1_address
        self.token2_address = token2_address
        self.token1_address_weak = token1_address_weak
        self.token2_address_weak = token2_address_weak
        self.token3_address_weak = token3_address_weak
        self.token_address_remove = token_address_remove
        self.token_address_exception = token_address_exception

        
        with open(drink_dictionary,'r') as fp:
            drink_dictionary = regex.split(fp.readline().strip('\n'))
        with open(drink_end,'r') as fp:
            drink_end = regex.split(fp.readline().strip('\n'))   
        with open(drink_remove,'r') as fp:
            drink_remove = regex.split(fp.readline().strip('\n'))   
        with open(drink_confuse,'r') as fp:
            drink_confuse = regex.split(fp.readline().strip('\n'))


        self.drink_dictionary = drink_dictionary
        self.drink_end = drink_end
        self.drink_remove = drink_remove
        self.drink_confuse = drink_confuse

       
    def get_address(self, sentence):
        """
        To generate address information from one sentence

        Args:
        ------------
            sentence: One Chinese sentence, should be a string

        Returns:
        ------------
            A list: It contains a list of strings. Each string is an address

        """
        words, postags, arcs = self.parse_sentence(self.segmentor, self.postagger, self.parser, sentence)
        if self.flag:
            return []
        return self.address_extract(words, postags, arcs)


    def get_drink(self, sentence):
        """
        To generate drink information from one sentence

        Args:
        ------------
            sentence: One Chinese sentence, should be a string

        Returns:
        ------------
            A list: It contains a list of strings. Each string is a drink

        """
        words, postags, arcs = self.parse_sentence(self.segmentor, self.postagger, self.parser, sentence)
        if self.flag:
            return []
        return self.drink_extract(words, postags, arcs)

    def parse_sentence(self, segmentor, postagger, parser, sentence='北京市望京soho'):
        """
        Used to word segmentation, pos and syntax tree analysis

        Args:
        -------------
            segmentor: word segmentation model
            postagger: pos model
            parser: syntax tree model
            sentence: A string. One Chinese sentence

        Returns:
        -------------
            words: word segmentation
            postags: pos
            arcs: syntax tree
        """
        
        self.sentence = sentence
        self.flag = False
        words = None
        postags = None
        arcs = None

        if len(sentence) == 0:
            self.flag = True
            return words, postags, arcs
        words = segmentor.segment(sentence)  # 分词
        
#        print '\t'.join(words)
        #segmentor.release()  # 释放模型
        postags = postagger.postag(words)  # 词性标注
#        print '\t'.join(postags)
        #postagger.release()  # 释放模型
        arcs = parser.parse(words, postags)  # 句法分析
#        print "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs)
        #parser.release()  # 释放模型
#        print [x.relation for x in arcs]
        
        netags = self.recognizer.recognize(words, postags)  # 命名实体识别
#        print '\t'.join(netags)
        #recognizer.release()  # 释放模型
        self.netags = netags

        return words, postags, arcs
       

    def word_in(self, word, address):
        """
        Used to capture whether a word is in a list

        Args:
        -------------
            word: A string. A word
            address: A list. Could be self.token_address...

        Returns:
        -------------
            Whether the word contains the information of address indicated by self.token_address_weak
        """
        if word in self.token_address_remove: # comment if word in self.token_address_remove, we treat that the word does not contain address information
           return False
        word_new = word.decode('utf-8')
        w = word_new[len(word_new)-1]
        for w_ in address:
            if w == w_.decode('utf-8'):
                return True
        return False


    def word_in_first(self, word):
        """
        Check the first word in one phrase whether it contains address information
        Args:
        -------------
            word: A string. A word

        Returns:
        -------------
            Whether the word contains the information of address indicated by ['路', '街']

        """
        word_new = word.decode('utf-8')
        if len(word_new) <= 1:
            return False
        w = word_new[len(word_new)-1]
        for w_ in ['路', '街']:
            if w == w_.decode('utf-8'):
                return True
        return False


    def address_extract(self, words, postags, arcs):
        """
        It is used to generate an address via syntax tree (by ATT in LTP)

        Args:
        -------------
            words: word segmentation
            postags: pos
            arcs: syntax tree

        Returns:
        -------------
            final_solution: A list contains strings. Each string is an address
        """
        address2 = self.token1_address
        word2_address = self.token2_address
        address = self.token1_address_weak
        word_address = self.token2_address_weak
        token_address_remove = self.token_address_remove
       
        
        temp = [] # comment a list, used to store one indices of an address
        solution = [] # comment, a list used to store temps above, namely, used to store several address
        for i in range(len(arcs)):
            if (temp != [] and i == len(arcs)-1 and arcs[i].relation not in ['WP'] and (postags[i] not in ['v', 'r'] or words[i] in ['弄'])) or (i == len(arcs)-1 and postags[i] in ['ni', 'ns', 'nl']) or (i == len(arcs)-1 and self.word_in_first(words[i])): # comment consider the case when the word in the last word
                temp.append(i)
               # print temp
                while len(temp) >=1 and not (words[temp[-1]] in address or words[temp[-1]] in self.token3_address_weak or self.word_in(words[temp[-1]], word_address)) and postags[temp[-1]] not in ['m', 'nd', 'ni', 'nl', 'ns', 'ws'] and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['送'] and words[temp[0]-1] in ['到', '至']) and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['地址', '住']) and not (postags[temp[-1]] in ['n'] and temp[0] >=1 and words[temp[0]-1] in ['住']): # comment we might remove the last words in the temp in some cases
                    temp.pop()
                if len(temp) >= 1:
                    solution.append(temp) # comment we append the address to the solution

          #      print solution
            elif (arcs[i].relation == 'ATT' and postags[i] not in ['p', 'q' ,'r'] and words[i] not in ['大杯','超大杯','小杯', '中杯', '杯', '奶'] and words[i] not in self.drink_end) or postags[i] in ['ns', 'ni', 'nl']: # comment generate an phrase via "ATT" relation but modify a little bit
                temp.append(i)
                #print temp
            elif temp != [] and (words[i] in address or self.word_in(words[i],word_address)): # comment consider the words in token_address_weak
                temp.append(i)
            elif self.word_in_first(words[i]): # comment consider the case of the first word
                temp.append(i)
            elif temp != [] and postags[i] in ['m', 'ws'] and words[i] not in ['几']: # comment consider the case of number of foreign words like 'cyt'
                temp.append(i)
            elif temp != []:   
                #print temp
                while len(temp) >=1 and not (words[temp[-1]] in address or words[temp[-1]] in self.token3_address_weak or self.word_in(words[temp[-1]], word_address)) and postags[temp[-1]] not in ['m', 'nd', 'ni', 'nl', 'ns',  'ws'] and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['送'] and words[temp[0]-1] in ['到', '至']) and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['地址', '住']) and not (postags[temp[-1]] in ['n'] and temp[0] >=1 and words[temp[0]-1] in ['住']):# comment we might remove the last words in the temp in some cases
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
                if postags[idx] in ['ns', 'ni', 'nl'] or words[idx] in address or self.word_in(words[idx], word_address):
                    if len(temp_solution) >= 1 and (temp[0] - temp_solution[-1][-1] == 2) and words[temp[0]-1] in ['的', '与', '和']: #comment we might need to combine two address if there exit only one word like '的' between them
                        last_temp = temp_solution.pop()
                            
                        last_temp.append(temp[0]-1)
                        last_temp.extend(temp)
                        temp = last_temp
                    if arcs[temp[-1]].relation == 'VOB' and arcs[temp[-1]].head == temp[0] + 1:# consider we might need to remove the first word some times
                        del temp[0]
                        #print temp
                    for idx1 in temp:
                        if postags[idx1] in ['ns', 'ni'] or words[idx1] in address2 or self.word_in(words[idx1], word2_address):# comment we check whether the phrase is one sentence
                            temp_solution.append(temp)
                            break
                    break
        #print temp_solution          
        middle_solution = []
        big_temp = []
        temp_count = 0
        netags = self.netags
        for i in range(len(words)):
          #  print i
            if netags[i] in ['B-Ns', 'I-Ns', 'E-Ns']:
                big_temp.append(i)
            elif temp_count < len(temp_solution) and i in temp_solution[temp_count]:
                big_temp.append(i)
            elif temp_count + 1 < len(temp_solution) and i in temp_solution[temp_count+1]:
                big_temp.append(i)
                temp_count = temp_count + 1
            else:
                if big_temp and words[big_temp[-1]] in ['小来', '来也']:
                    big_temp.pop()
                while True:
                    if len(big_temp) >=2 and words[big_temp[0]] in ['送'] and words[big_temp[1]] in ['到', '至', '往']:
                        big_temp = big_temp[2:]
                    elif big_temp and (words[big_temp[0]] in self.drink_end or words[big_temp[0]] in ['送到', '送至', '送往', '送']): 
                        big_temp = big_temp[1:]
                    else:
                        break
                if big_temp:
                    middle_solution.append(''.join(words[i] for i in big_temp))
         #           middle_solution.append(big_temp)
                    big_temp = []
        
        if big_temp and words[big_temp[-1]] in ['小来', '来也']:
            big_temp.pop()
            
        while True:
            if big_temp and (words[big_temp[0]] in self.drink_end or words[big_temp[0]] in ['送到', '送至']): 
                big_temp = big_temp[1:]
            elif len(big_temp) >=2 and words[big_temp[0]] in ['送'] and words[big_temp[1]] in ['到', '至']:
                big_temp = big_temp[2:]
            else:
                break

        if  big_temp:
           # middle_solution.append(big_temp)
            middle_solution.append(''.join(words[i] for i in big_temp))
       # print middle_solution
       # temp_solution = middle_solution
        sentence_dict = dict()
        sentence_count = 0
        word_count = 0
        for single_word in (self.sentence).decode('utf-8'):# comment it is used to keep the ' ' in the original sentence when we generate the address. We use a dict to deal with it
            if single_word in [' '.decode('utf-8'), '　'.decode('utf-8')]:
                sentence_count += 1
            else:
                sentence_dict[word_count] = sentence_count
                sentence_count += 1
                word_count += 1

        final_solution = []
        sentence_continue = ''.join((self.sentence).decode('utf-8').split())
        import re
        sentence_length = len(sentence_continue)
        for address_result in middle_solution:
            address_result = address_result.decode('utf-8')
            pattern_length = len(address_result)
           
            if sentence_length == 0:
                break
            if pattern_length == 0:
                continue
            start = -1
            for i in range(sentence_length):
                if address_result == sentence_continue[i:i+pattern_length]:
                    start = i
                    break

            if start == -1: # fail to match
                pass
            else:
                final_solution.append(self.sentence.decode('utf-8')[sentence_dict[start]:sentence_dict[pattern_length+start-1]+1].encode('utf-8'))
        temp_solution = []
        for temp in final_solution:# comment remove some exception address
            if temp in  self.token_address_exception:
                pass
            else:
                if len(temp.decode('utf-8')) >=2 and temp.decode('utf-8')[0].encode('utf-8') in ['嗯']:
                    temp = temp.decode('utf-8')[1:].encode('utf-8')
                temp_solution.append(temp)
        final_solution = temp_solution



                      
        return final_solution


    def word_fix(self, word, drink_confuse):
        """
        Some words in drink_confuse might attach to the words in drink, due to the problem of segmentation of LTP

        Args:
        -------------
            word: The input word that contains drink information
            drink_confuse: Please refer to "drink_confuse.txt"

        Returns:
        ------------
            Mofified word that remove the word in drink_confuse
        """
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

    def drink_from_dictionary(self, sentence):
        """
        The the syntax tree fails to extract the drink, we might the string match method to extract the drink information. Please refer to "drink_dictionary.txt"

        Args:
        -----------
            sentence: A string. The sentence we want to process

        Returns:
        ----------
            A list: Contains the drink from drink_dictionary
        """
        drink_dictionary = self.drink_dictionary
        sentence = ''.join(sentence.decode('utf-8').split())
        for temp in drink_dictionary:
            if temp.decode('utf-8') in sentence:
                return [temp]
        return []


    def drink_extract(self, words, postags, arcs):
        """
        It is used to generate the drink via syntax tree (by ATT in LTP)

        Args:
        -------------
            words: word segmentation
            postags: pos
            arcs: syntax tree

        Returns:
        -------------
            final_solution: A list contains strings. Each string is a kind of drink
        """

        drink_end = self.drink_end
        drink_remove = self.drink_remove
        drink_confuse = self.drink_confuse
     
        temp = []
        solution = []
        for i in range(len(arcs)):
            if words[i] in drink_end or self.word_fix(words[i], drink_confuse) in drink_end:# comment if the phrase contains the word in drink_end, we decide it is a kind of drink
                temp.append(i)
                if i < len(arcs) -1 and words[i+1] in drink_end: # comment consider the case when the there is another word in drink_end after the current word
                    continue
                solution.append(temp)
                temp = []
            elif i < len(arcs) - 1 and words[i] in ['flat', 'Flat', 'FLAT'] and words[i+1] in ['white', 'White', 'WHITE']: # comment consider the case of Englist word in drink product
                temp.append(i)
                temp.append(i+1)
                if i < len(arcs) - 2 and words[i+2] in drink_end:
                    continue
                solution.append(temp)
                temp = []
            elif arcs[i].relation == 'ATT' and postags[i] not in ['m', 'p', 'r', 'q', 'e', 'ws', 'v'] and words[i] not in drink_remove: # comment we use ATT to generate phrase
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
            
        middle_solution = []
        for temp in temp_solution: # comment consider the case when there are some word in drink_confuse in the either side of the phrase, we might need to remove them

            while words[temp[0]].decode('utf-8')[0].encode('utf-8') in drink_confuse and words[temp[0]] not in drink_end:
                if len(temp) >=2 and words[temp[0]] in ['热'] and words[temp[1]] in ['巧克力']:
                    break
                if words[temp[0]] in ['冰摇', '冰搖']: # we should keep it 
                    break
                words[temp[0]] = words[temp[0]].decode('utf-8')[1:].encode('utf-8')
                if not words[temp[0]]:
                    temp = temp[1:]

            while words[temp[-1]].decode('utf-8')[-1].encode('utf-8') in drink_confuse and words[temp[-1]] not in drink_end:
                words[temp[-1]] = words[temp[-1]].decode('utf-8')[:-1].encode('utf-8')
                if not words[temp[-1]]:
                    temp = temp[:-1]
            if len(temp) == 1 and words[temp[0]] in ['咖啡']: # if the phrase is only 咖啡, we simply remove it
                continue
            middle_solution.append(''.join(words[i] for i in temp))

       
        if len(middle_solution) == 0:# if we fail to get the drink above, we use string match from drink_dictionary
            middle_solution = self.drink_from_dictionary(self.sentence)

        sentence_dict = dict()
        sentence_count = 0
        word_count = 0
        for single_word in (self.sentence).decode('utf-8'):# comment it is used to keep the ' ' in the original sentence when we generate the drink. We use a dict to deal with it
            if single_word in [' '.decode('utf-8'), '　'.decode('utf-8')]:
                sentence_count += 1
            else:
                sentence_dict[word_count] = sentence_count
                sentence_count += 1
                word_count += 1


        final_solution = []
        sentence_continue = ''.join((self.sentence).decode('utf-8').split())
        import re
        sentence_length = len(sentence_continue)
        for drink_result in middle_solution:
            drink_result = drink_result.decode('utf-8')
            pattern_length = len(drink_result)
           
            if sentence_length == 0:
                break
            if pattern_length == 0:
                continue
            start = -1
            for i in range(sentence_length):
                if drink_result == sentence_continue[i:i+pattern_length]:
                    start = i
                    break

            if start == -1: # comment fail to match
                pass
            else:
                final_solution.append(self.sentence.decode('utf-8')[sentence_dict[start]:sentence_dict[pattern_length+start-1]+1].encode('utf-8'))

        return final_solution


if __name__ == '__main__':
    from time import time
    start = time()
    address_drink_parser = AddressDrinkParser()

    end = time()

    sentence = '浓醇 黑 焦糖 烫1 可可  碎片星  冰乐1  摩卡  星  冰乐4  热 摩 卡 1'


    solution = address_drink_parser.get_drink(sentence)
    end1 = time()
    for temp in solution:
        print(temp)
     
    sentence = ''
    sentence = '满记 芒果西米露 满记 芒果白雪黑糯米 X 2 满记 蓝莓梦幻双皮奶 热焦糖咖啡拿铁 拿铁'
    solution = address_drink_parser.get_address(sentence)
    for temp in solution:
        print(temp)
    print(end-start)
    print(end1-end)

