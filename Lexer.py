import re
from Token import Token
# 关键字
keywords = [
    ['int', 'float', 'double', 'char', 'void'],
    ['if', 'for', 'while', 'do', 'else'], ['include', 'return'],
]
# 运算符
operators = [
    '=', '&', '<', '>', '++', '--', '+', '-', '*', '/', '>=', '<=', '!='
]
# 分隔符
delimiters = ['(', ')', '{', '}', '[', ']', ',', '\"', ';']
class Lexer(object):
    '''词法分析器'''

    def __init__(self):
        # 用来保存词法分析出来的结果
        self.tokens = []

    # 判断是否是空白字符
    def is_blank(self, index,content):
        return (
            content[index] == ' ' or
            content[index] == '\t' or
            content[index] == '\n' or
            content[index] == '\r'
        )

    # 跳过空白字符
    def skip_blank(self, index,content):
        while index < len(content) and self.is_blank(index,content):
            index += 1
        return index

    # 打印
    def print_log(self, style, value):
        print ('(%s, %s)' % (style, value))

    # 判断是否是关键字
    def is_keyword(self, value):
        for item in keywords:
            if value in item:
                return True
        return False

    # 词法分析主程序
    def main(self,content):
        i = 0
        while i < len(content):
            i = self.skip_blank(i,content)
            # 如果是引入头文件，还有一种可能是16进制数，这里先不判断
            if content[i] == '#':
                #self.print_log( '分隔符', content[ i ] )
                self.tokens.append(Token(4, content[i]))
                i = self.skip_blank(i + 1,content)
                # 分析这一引入头文件
                while i < len(content):
                    # 匹配"include"
                    if re.match('include', content[i:]):
                        # self.print_log( '关键字', 'include' )
                        self.tokens.append(Token(0, 'include'))
                        i = self.skip_blank(i + 7,content)
                    # 匹配"或者<
                    elif content[i] == '\"' or content[i] == '<':
                        # self.print_log( '分隔符', content[ i ] )
                        self.tokens.append(Token(4, content[i]))
                        i = self.skip_blank(i + 1,content)
                        close_flag = '\"' if content[i] == '\"' else '>'
                        # 找到include的头文件
                        lib = ''
                        while content[i] != close_flag:
                            lib += content[i]
                            i += 1
                        # self.print_log( '标识符', lib )
                        self.tokens.append(Token(1, lib))
                        # 跳出循环后，很显然找到close_flog
                        # self.print_log( '分隔符', close_flag )
                        self.tokens.append(Token(4, close_flag))
                        i = self.skip_blank(i + 1,content)
                        break
                    else:
                        print ('include error!')
                        exit()
            # 如果是字母或者是以下划线开头
            elif content[i].isalpha() or content[i] == '_':
                # 找到该字符串
                temp = ''
                while i < len(content) and (
                        content[i].isalpha() or
                        content[i] == '_' or
                        content[i].isdigit()):
                    temp += content[i]
                    i += 1
                # 判断该字符串
                if self.is_keyword(temp):
                    # self.print_log( '关键字', temp )
                    self.tokens.append(Token(0, temp))
                else:
                    # self.print_log( '标识符', temp )
                    self.tokens.append(Token(1, temp))
                i = self.skip_blank(i,content)
            # 如果是数字开头
            elif content[i].isdigit():
                temp = ''
                while i < len(content):
                    if content[i].isdigit() or (
                            content[i] == '.' and content[i + 1].isdigit()):
                        temp += content[i]
                        i += 1
                    elif not content[i].isdigit():
                        if content[i] == '.':
                            print ('float number error!')
                            exit()
                        else:
                            break
                # self.print_log( '常量' , temp )
                self.tokens.append(Token(2, temp))
                i = self.skip_blank(i,content)
            # 如果是分隔符
            elif content[i] in delimiters:
                # self.print_log( '分隔符', content[ i ] )
                self.tokens.append(Token(4, content[i]))
                # 如果是字符串常量
                if content[i] == '\"':
                    i += 1
                    temp = ''
                    while i < len(content):
                        if content[i] != '\"':
                            temp += content[i]
                            i += 1
                        else:
                            break
                    else:
                        print ('error:lack of \"')
                        exit()
                    # self.print_log( '常量' , temp )
                    self.tokens.append(Token(5, temp))
                    # self.print_log( '分隔符' , '\"' )
                    self.tokens.append(Token(4, '\"'))
                i = self.skip_blank(i + 1,content)
            # 如果是运算符
            elif content[i] in operators:
                # 如果是++或者--
                if (content[i] == '+' or content[i] == '-') and (
                        content[i + 1] == content[i]):
                    # self.print_log( '运算符', content[ i ] * 2 )
                    self.tokens.append(Token(3, content[i] * 2))
                    i = self.skip_blank(i + 2,content)
                # 如果是>=或者<=
                elif (content[i] == '>' or content[i] == '<') and content[i + 1] == '=':
                    # self.print_log( '运算符', content[ i ] + '=' )
                    self.tokens.append(Token(3, content[i] + '='))
                    i = self.skip_blank(i + 2,content)
                # 其他
                else:
                    # self.print_log( '运算符', content[ i ] )
                    self.tokens.append(Token(3, content[i]))
                    i = self.skip_blank(i + 1,content)