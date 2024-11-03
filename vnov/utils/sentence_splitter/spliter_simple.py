# -*- coding:utf-8 -*-
import re


SYMBOLS = {
    'quotation': re.compile('(["“”])'),
    'bracket_left': re.compile('([{\[\(（【「])'),
    'bracket_right': re.compile('([\)\]}」】）])'),
    'comma': re.compile('([,，])'),
    'end_symbols': re.compile('([?\!\.…;？！。……；．])')
}


class Simple_Spliter:

    def __init__(self):
        '''
        :param option: 决定是中文还是英文
        '''
        # self.option = option
        self.sentences = []
        self.count_quote = 0
        self.count_left_bracket = 0
        self.count_right_bracket = 0
        self.tmp_char = ''

        # -- parameter -- #

    # -- filter -- #

    # -- sentences segmentation -- #
    def cut_to_sentences(self, paragraph):
        '''
        将段落切成句子
        :param paragraph:
        :return: 切分好的list
        '''
        self.sentences = []
        self.tmp_char = []  # ''  append 比 __iadd__ 快
        if len(paragraph) == 0:
            return []
        total_len = len(paragraph)
        #s = time.time()
        for index, char in enumerate(paragraph):
            if char != '\n':
                self._do_cut(char, index, paragraph, total_len)
        #print(time.time() - s)
        self.tmp_char = ''.join(self.tmp_char)
        if self.tmp_char:
            self.sentences.append(self.tmp_char)
        return self.sentences

    def _do_cut(self, char, index, paragraph, total_len):
        '''
        切分的状态机，再封装各个情况，每个if能拆解为函数
        :param index:
        :param char:
        :param paragraph:
        '''
        self.tmp_char.append(char)
        if SYMBOLS['quotation'].match(char):  # "xx"，情况不切句 其他""情况切句
            self.count_quote += 1
            if self.count_quote % 2 == 0:
                self.count_quote = 0
                if index + 1 >= total_len or not SYMBOLS['comma'].match(paragraph[index + 1]):#双引号后面不是逗号,就切分
                    self.add_to_sntnc()
                    return
        # -- 假定所有引号和括号都完美合上了 -- #
        elif SYMBOLS['bracket_left'].match(char):  # （）不切
            self.count_left_bracket += 1
            return

        elif SYMBOLS['bracket_right'].match(char):
            self.count_right_bracket += 1
            if self.count_left_bracket == self.count_right_bracket:
                self.count_left_bracket = 0
                self.count_right_bracket = 0
            return
        elif self.is_valid_cut() and SYMBOLS['end_symbols'].match(char):  # 判断此字符是否为结束符号
            if index + 1 >= total_len or not self._demical_char(char, index, paragraph):  # 判断是否是小数(是结束字符且不是小数)
                self.add_to_sntnc()
        return

        

    def add_to_sntnc(self):
        tmp_char = ''.join(self.tmp_char)
        if tmp_char:
            if len(tmp_char) == 1 and len(self.sentences) > 0:
                self.sentences[-1] = self.sentences[-1] + tmp_char
            else:
                self.sentences.append(tmp_char)
            self.tmp_char = []

    def is_valid_cut(self):
        if self.count_left_bracket == self.count_right_bracket and \
                self.count_quote % 2 == 0:
            return True
        else:
            return False

    def _demical_char(self, char, index, paragraph):
        '''
        是否是小数
        :param char:
        :param index:
        :param paragraph:
        :return: True/False
        '''
        if char == '.' and paragraph[index - 1].isdigit() and paragraph[index + 1].isdigit():
            return True
        else:
            return False
