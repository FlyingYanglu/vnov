# -*- coding:utf-8 -*-
# CREATED BY: Li Wang
# CREATED ON:2020/4/30 上午11:56
# LAST MODIFIED ON:
# AIM: 对划分好的句子长短句做处理
# import vnov.utils.sentence_splitter as s_splitter
from vnov.utils.sentence_splitter.spliter_simple import Simple_Spliter
import re
from typing import List
from cerberus import Validator

class Spliter:
    def __init__(self, **options):
        schema = {'language':{'type':'string'},
                  'remove_blank':{'type':'boolean'},
                  'long_short_sent_handle':{'type':'boolean'},
                  'max_length':{'type':'integer'},
                  'min_length':{'type':'integer'},
                  'hard_max_length':{'type':'integer'}}
        v = Validator(schema)
        # params = options
        if v.validate(options):
            if options['language'].lower() == 'zh':
                self.spliter = Simple_Spliter()
                self.flag = 'zh'
            elif options['language'].lower() == 'en':
                self.spliter = Simple_Spliter()
                self.flag = 'en'
            else:
                raise Exception("option > language must be one of the following value ['zh', 'en']")
            self.remove_blank_on = options['remove_blank']
            # print(self.remove_blank_on)
            self.long_short_sent_handle = options['long_short_sent_handle']
            self.max_length = options['max_length']
            self.min_length = options['min_length']
            self.hard_max_length = options['hard_max_length']
            self.long_filter = re.compile('([.?!。？！，,])')


    def cut_to_sentences(self,text):

        if self.remove_blank_on and self.flag == 'zh':
            text = re.sub(r'\s+', '', text)  # 先不考虑中英文混合情况,去掉空格
            all_sentence = self.to_sentence(text)
        if self.flag == 'en':
            all_sentence = self.to_sentence(text)
            return all_sentence
        elif self.flag == 'zh':
            if self.long_short_sent_handle:
                return self.refine(all_sentence)
            else:
                return all_sentence

    # - step 1:划分句子
    def to_sentence(self, paragraph) -> [str]:
        sentences = self.spliter.cut_to_sentences(paragraph)
        return sentences

    def refine_single_short(self, sentence: str) -> [str]:
        pass

    def refine(self, all_sentence: List[str]) -> List[str]:
        out = []
        i = 0
        end_sntnc = ''
        while i < len(all_sentence):
            current_sent = all_sentence[i]

            # Concatenate with previous incomplete sentence if it exists
            if end_sntnc and len(end_sntnc + current_sent) <= self.max_length:
                current_sent = end_sntnc + current_sent
                if out:
                    out.pop()  # Remove the last incomplete sentence from output
                end_sntnc = ''  # Clear incomplete sentence buffer

            # Check if the sentence is valid, otherwise split it further
            if self.is_valid_sntnc(current_sent):
                out.append(current_sent)
            else:
                new_sents = self.refine_single(current_sent)
                out.extend(new_sents)

            # If the last sentence is too short, buffer it for the next loop
            if len(out[-1]) < self.min_length:
                end_sntnc = out.pop()

            i += 1

        if end_sntnc:  # Add any remaining buffered sentence
            out.append(end_sntnc)

        return out


    def is_valid_sntnc(self, sentence: str):
        '''
        判断是否满足正常句子，长度在min_length到max_length之间
        :param sentence:
        :return:
        '''
        if self.min_length < len(sentence) < self.max_length:
            return True
        else:
            return False

    def refine_single(self, sentence: str) -> List[str]:
        """
        Refines a single sentence by splitting it based on punctuation and length constraints.

        :param sentence: The sentence to refine.
        :return: A list of refined sentence parts.
        """
        pattern_w = re.compile(r'([?!…;？！。；,.，])')  # Matching punctuation that can be split on
        out = ['']  # Initialize with an empty string for accumulating parts
        pre_split_index = 0  # Index to track the last valid split point
        acc_range = 0  # Accumulated length adjustment due to splits

        for i, char in enumerate(sentence):
            # Accumulate the current character into the last part
            out[-1] += char

            # Check if the character is punctuation and marks a split point
            if pattern_w.match(char):
                if len(out[-1]) <= self.max_length:
                    pre_split_index = i + 1  # Update the split index to the next position

            # If the current part exceeds the hard max length, split it
            if len(out[-1]) > self.hard_max_length:
                if pre_split_index <= 0:  # Handle case where no valid punctuation split exists
                    pre_split_index = self.hard_max_length + acc_range

                # Determine the range for splitting
                split_range = pre_split_index - acc_range
                acc_range += split_range

                # Split the sentence into two parts
                shorter = out[-1][:split_range]  # Part 1: Up to the split point
                remainder = sentence[pre_split_index:i + 1]  # Part 2: Remainder of the sentence

                out[-1] = shorter  # Replace the last part with the shorter split
                out.append(remainder)  # Add the remainder as a new part

                pre_split_index = 0  # Reset split index for the next iteration

        return out

    def remove_blank(self, sentence: str) -> str:
        if not self.remove_blank_on:
            return sentence
        else:
            pass
    # -- 中英文混合情况 -- #
    # def is_zh(self, _char: str) -> bool:
    #     if '\u4e00' <= _char <= '\u9fa5':
    #         return True
    #     return False
    #
    # def len(self, sentence:str) -> bool:
    #     '''
    #     只考虑英语和中文情况
    #     :param sentence:
    #     :return:
    #     '''
    #     cnt = 0
    #     nzh_flag = 0
    #     for char in sentence:
    #         if self.is_zh(char):
    #             cnt += 1
    #             nzh_flag = 0
    #         else:
    #             nzh_flag
    #
    # def is_zh_sntnc(self, sentence: str) -> bool:
    #     length = len(sentence)
    #     count = None
    #     for c in sentence:
    #         pass