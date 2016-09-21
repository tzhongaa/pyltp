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
        token1_address: A list. Used for store the words that suggests that the phrase contains address information strongly. Please refer to the first line of token_address.txt. It should be the subset of token1_address_weak
        token2_address: A list. Used for store the words that suggests that the phrase contains address information strongly. Please refer to the second line of token_address.txt. It should be the subset of token2_adderess_weak
        token1_address_weak: A list. Used for store the words that suggests that the phrase contains address information weakly. Please refer to the first line of token_address_weak.txt
        token2_address_weak: A list. Used for store the words that suggests that the phrase contains address information weakly. Please refer to the second line of token_address_weak.txt
        token_address_remove: A list. To remove the word that is not address information but contains words in token_address_week. Please refer to the file toaken_address_remove.txt       
    """

    def __init__(self, csw_model='ltp_models/cws.model', csw_dictionary='segmentor.txt', pos_model='ltp_models/pos.model', pos_dictionary='postagger.txt',parse_model='ltp_models/parser.model', token_address='token_address.txt', token_address_weak='token_address_weak.txt', token_address_remove='token_address_remove.txt'):
        """
        load the modeles

        Args:
        --------------
            csw_model: word segmentation models
            pos_model: part of speech models
            parse_model: syntax tree models
            csw_dictionary: personal dictionary for word segmentation
            pos_dictionary: perfonal dictionary for part of speech
            token_address: words that indicates that a phrase contains an address. It should be a subset of token_address_weak
            token_address_weak: words tha indicates that a phrase contains an address weakly. 
            token_address_remove: words that are not address information but contains words in token_address_weak

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

        import re
        regex = re.compile('\s*,\s*')
        with open(token_address,'r') as fp:
            token1_address = regex.split(fp.readline().strip('\n'))   
            token2_address = regex.split(fp.readline().strip('\n'))
        with open(token_address_weak, 'r') as fp:
            token1_address_weak = regex.split(fp.readline().strip('\n'))   
            token2_address_weak = regex.split(fp.readline().strip('\n'))
        with open(token_address_remove, 'r') as fp:
            token_address_remove = regex.split(fp.readline().strip('\n'))   

        self.segmentor = segmentor
        self.postagger = postagger
        self.parser = parser
        self.token1_address = token1_address
        self.token2_address = token2_address
        self.token1_address_weak = token1_address_weak
        self.token2_address_weak = token2_address_weak
        self.token_address_remove = token_address_remove

        
        with open('drink_dictionary.txt','r') as fp:
            drink_dictionary = regex.split(fp.readline().strip('\n'))
        with open('drink_end.txt','r') as fp:
            drink_end = regex.split(fp.readline().strip('\n'))   
        with open('drink_remove.txt','r') as fp:
            drink_remove = regex.split(fp.readline().strip('\n'))   
        with open('drink_confuse.txt','r') as fp:
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
        return self.address_extract(words, postags, arcs)

    def get_drink(self, sentence):
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
        original_words = segmentor.segment(sentence)  # 分词
        self.original_words = original_words
        
        self.sentence = sentence

        words = segmentor.segment(sentence)  # 分词
        print '\t'.join(words)
        #segmentor.release()  # 释放模型
        postags = postagger.postag(words)  # 词性标注
        print '\t'.join(postags)
        #postagger.release()  # 释放模型
        arcs = parser.parse(words, postags)  # 句法分析
        print "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs)
        #parser.release()  # 释放模型
        #print [x.relation for x in arcs]

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
                #print temp
                while len(temp) >=1 and not (words[temp[-1]] in address or self.word_in(words[temp[-1]], word_address)) and postags[temp[-1]] not in ['j', 'm', 'nd', 'ni', 'nl', 'ns', 'nz', 'ws', 'i', 'q'] and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['送'] and words[temp[0]-1] in ['到', '至']) and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['地址', '住']) and not (postags[temp[-1]] in ['n'] and temp[0] >=1 and words[temp[0]-1] in ['住']): # comment we might remove the last words in the temp in some cases
                    temp.pop()
                if len(temp) >= 1:
                    solution.append(temp) # comment we append the address to the solution

          #      print solution
            elif (arcs[i].relation == 'ATT' and postags[i] not in ['p', 'r', 'q'] and words[i] not in ['大杯','超大杯','小杯', '中杯', '杯']) or postags[i] in ['ns', 'ni', 'nl']: # comment generate an phrase via "ATT" relation but modify a little bit
                temp.append(i)
                #print temp
            elif temp != [] and (words[i] in address or self.word_in(words[i],word_address)): # comment consider the words in token_address_weak
                temp.append(i)
            elif self.word_in_first(words[i]): # comment consider the case of the first word
                temp.append(i)
            elif temp != [] and postags[i] in ['m', 'ws']: # comment consider the case of number of foreign words like 'cyt'
                temp.append(i)
            elif temp != []:   
                #print temp
                while len(temp) >=1 and not (words[temp[-1]] in address or self.word_in(words[temp[-1]], word_address)) and postags[temp[-1]] not in ['j', 'm', 'nd', 'ni', 'nl', 'ns', 'nz', 'ws', 'i', 'q'] and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['送'] and words[temp[0]-1] in ['到', '至']) and not (postags[temp[-1]] in ['n'] and temp[0] >=2 and words[temp[0]-2] in ['地址', '住']) and not (postags[temp[-1]] in ['n'] and temp[0] >=1 and words[temp[0]-1] in ['住']):# comment we might remove the last words in the temp in some cases
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
        count = 0
        mini_count = 1
        new_word = []
        new_word_list = []
        for single_word in self.sentence.decode('utf-8'):
#            print single_word
            new_word.append(single_word.encode('utf-8'))
            if single_word in [' '.decode('utf-8'), '　'.decode('utf-8')]:
                pass
            elif mini_count < len(words[count].decode('utf-8')):
                mini_count += 1
            else:
                mini_count = 1
                count += 1
                new_word_list.append(''.join(word for word in new_word))
                new_word = []
#        for temp in new_word_list:
#            print temp
        
        final_solution = []
#        for temp in temp_solution:
##            print temp
#            final_solution.append(''.join(words[i] for i in temp))# comment we transfer the temp(a list) to a string contains address information

        for temp in temp_solution:
#            print temp
            final_solution.append((''.join(new_word_list[i] for i in temp)).strip())# comment we transfer the temp(a list) to a string contains address information
        return final_solution


    def word_fix(self, word, drink_confuse):
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
#        with open('drink_dictionary.txt','r') as fp:
#            drink_dictionary = regex.split(fp.readline().strip('\n'))   
        drink_dictionary = self.drink_dictionary
        for temp in drink_dictionary:
            print temp
            if temp in sentence:
                return [temp]
        return []


    def drink_extract(self, words, postags, arcs):
#        import re
#        regex = re.compile('\s*,\s*')
#        with open('drink_end.txt','r') as fp:
#            drink_end = regex.split(fp.readline().strip('\n'))   
#        with open('drink_remove.txt','r') as fp:
#            drink_remove = regex.split(fp.readline().strip('\n'))   
#        with open('drink_confuse.txt','r') as fp:
#            drink_confuse = regex.split(fp.readline().strip('\n'))
#        for temp in drink_remove:
#            print temp
        drink_end = self.drink_end
        drink_remove = self.drink_remove
        drink_confuse = self.drink_confuse
     
        temp = []
        solution = []
        for i in range(len(arcs)):
     #       if words[i] in drink_remove:
      #          temp = []
            if words[i] in drink_end or self.word_fix(words[i], drink_confuse) in drink_end:
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
        word_solution = []
        from copy import deepcopy
        original_words = self.original_words
        for temp in original_words:
            print temp
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
            middle_solution.append(temp)


        final_solution = []
      
      
      
##        for temp in middle_solution:
##            final_solution.append(''.join(words[i] for i in temp))
#
#        final_solution = []
#        for temp in middle_solution:
#            final_solution.append(''.join(original_words[i] for i in temp))
#        
#        return final_solution
#
##        if len(final_solution) == 0:
##            final_solution = self.drink_from_dictionary(self.sentence)
                

#        count = 0
#        mini_count = 1
#        new_word = []
#        new_word_list = []
#        for single_word in self.sentence.decode('utf-8'):
##            print single_word
#            new_word.append(single_word.encode('utf-8'))
#            if single_word in [' '.decode('utf-8'), '　'.decode('utf-8')]:
#                pass
#            elif mini_count < len(original_words[count].decode('utf-8')):
#                mini_count += 1
#            else:
#                mini_count = 1
#                count += 1
#                new_word_list.append(''.join(word for word in new_word))
#                new_word = []
##        for temp in new_word_list:
##            print temp
#        
##        for temp in temp_solution:
###            print temp
##            final_solution.append(''.join(words[i] for i in temp))# comment we transfer the temp(a list) to a string contains address information
#        import re
#        for temp in middle_solution:
#            if len(temp) == 1:
#                m = re.search(original_words[temp[0]].decode('utf-8'), ''.join(new_word_list[temp[0]].decode('utf-8').split()))
#                start = m.start()
#                length = len(original_words[temp[0]].decode('utf-8'))
#                for new_word in new_word_list[temp[0]].decode('utf-8'):
#                    if new_word in [' '.decode('utf-8'), '　'.decode('utf-8')]:
#                        new_word_list[temp[0]] = new_word_list[temp[0]].decode('utf-8')[1:].encode('utf-8')
#                    elif start == 0:
#                        break
#                    else:
#                        new_word_list[temp[0]] = new_word_list[temp[0]].decode('utf-8')[1:].encode('utf-8')
#                        start -= 1
#                number = 0
#                while length > 0:
#                    if new_word_list[temp[0]].decode('utf-8')[number] in [' '.decode('utf-8'), '　'.decode('utf-8')]:
#                        pass
#                    else:
#                        length -= 1
#                    number += 1
#                new_word_list[temp[0]] = new_word_list[temp[0]].decode('utf-8')[:number].encode('utf-8')
#            else:
#                left = len(original_words[temp[0]].decode('utf-8')) - len(words[temp[0]].decode('utf-8'))
#                new_word_first = new_word_list[temp[0]].decode('utf-8')
#                for i in range(len(new_word)):
#                    if new_word in [' '.decode('utf-8'), '　'.decode('utf-8')]:
#                        new_word = new_word[1:]
#                    elif left > 0:
#                        new_word = new_word[1:]
#                        left -= 1
#                    else:
#                        new_word_list[temp[0]] = new_word.encode('utf-8')
#                        break
#                right = len(original_words[temp[-1]].decode('utf-8')) - len(words[temp[-1]].decode('utf-8'))
#                new_word_first = new_word_list[temp[-1]].decode('utf-8')
#                for i in range(len(new_word)):
#                    if new_word in [' '.decode('utf-8'), '　'.decode('utf-8')]:
#                        new_word = new_word[:-1]
#                    elif left > 0:
#                        new_word = new_word[:-1]
#                        right -= 1
#                    else:
#                        new_word_list[temp[-1]] = new_word.encode('utf-8')
#                        break
#
#
#        final_solution = []
#                
#        for temp in middle_solution:
#
#            final_solution.append((''.join(new_word_list[i] for i in temp)).strip())# comment we transfer the temp(a list) to a string contains address information
#        if len(final_solution) == 0:
#            final_solution = self.drink_from_dictionary(self.sentence)
#                      
#        return final_solution




if __name__ == '__main__':
    from time import time
    start = time()
    address_drink_parser = AddressDrinkParser()

    end = time()

    sentence = '星巴克热拿铁'
    solution = address_drink_parser.get_drink(sentence)

    end1 = time()
    for temp in solution:
        print(temp)
      
    print(end-start)
    print(end1-end)

