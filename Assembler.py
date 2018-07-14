from Parser import Parser
class AssemblerFileHandler(object):
    '''维护生成的汇编文件'''

    def __init__(self):
        self.result = ['.data', '.bss', '.lcomm bss_tmp, 4', '.text']
        self.data_pointer = 1
        self.bss_pointer = 3
        self.text_pointer = 4

    def insert(self, value, _type):
        # 插入到data域
        if _type == 'DATA':
            self.result.insert(self.data_pointer, value)
            self.data_pointer += 1
            self.bss_pointer += 1
            self.text_pointer += 1
        # 插入到bss域
        elif _type == 'BSS':
            self.result.insert(self.bss_pointer, value)
            self.bss_pointer += 1
            self.text_pointer += 1
        # 插入到代码段
        elif _type == 'TEXT':
            self.result.insert(self.text_pointer, value)
            self.text_pointer += 1
        else:
            print ('error!')
            exit()

    # 将结果保存到文件中
    def generate_ass_file(self,file_name):
        self.file = open(file_name[0:-2] + '.S', 'w+')
        self.result.insert(0,'.code32')
        self.file.write('\n'.join(self.result) + '\n')
        self.file.close()
        ftemp=open(file_name[0:-2] + '.txt', 'w+')
        str='\n'.join(self.result)+'\n'
        ftemp.write(str)
        ftemp.close()

class Assembler(object):
    '''编译成汇编语言'''

    def __init__(self,content):
        self.parser = Parser(content)
        self.parser.main()
        # 生成的语法树
        self.tree = self.parser.tree
        # 要生成的汇编文件管理器
        self.ass_file_handler = AssemblerFileHandler()
        # 符号表
        self.symbol_table = {}
        # 语法类型
        self.sentence_type = ['Sentence', 'Include', 'FunctionStatement',
                              'Statement', 'FunctionCall', 'Assignment', 'Control', 'Expression', 'Return']
        # 表达式中的符号栈
        self.operator_stack = []
        # 表达式中的操作符栈
        self.operand_stack = []
        # 已经声明了多少个label
        self.label_cnt = 0
        # ifelse中的标签
        self.labels_ifelse = {}

    # include句型
    def _include(self, node=None):
        pass

    # 函数定义句型
    def _function_statement(self, node=None):
        # 第一个儿子
        current_node = node.first_son
        while current_node:
            if current_node.value == 'FunctionName':
                if current_node.first_son.value != 'main':
                    print ('other function statement except for main is not supported!')
                    exit()
                else:
                    self.ass_file_handler.insert('.globl main', 'TEXT')
                    self.ass_file_handler.insert('main:', 'TEXT')
                    self.ass_file_handler.insert('finit', 'TEXT')
            elif current_node.value == 'Sentence':
                self.traverse(current_node.first_son)
            current_node = current_node.right

    # 简单的sizeof
    def _sizeof(self, _type):
        size = -1
        if _type == 'int' or _type == 'float' or _type == 'long':
            size = 4
        elif _type == 'char':
            size = 1
        elif _type == 'double':
            size = 8
        return str(size)

    # 声明语句
    def _statement(self, node=None):
        # 对应的汇编代码中的声明语句
        line = None
        # 1:初始化的，0:没有初始化
        flag = 0
        # 变量数据类型
        variable_field_type = None
        # 变量类型，是数组还是单个变量
        variable_type = None
        # 变量名
        variable_name = None
        current_node = node.first_son
        while current_node:
            # 类型
            if current_node.value == 'Type':
                variable_field_type = current_node.first_son.value
            # 变量名
            elif current_node.type == 'IDENTIFIER':
                variable_name = current_node.value
                variable_type = current_node.extra_info['type']
                line = '.lcomm ' + variable_name + \
                    ', ' + self._sizeof(variable_field_type)
            # 数组元素
            elif current_node.value == 'ConstantList':
                line = variable_name + ': .' + variable_field_type + ' '
                tmp_node = current_node.first_son
                # 保存该数组
                array = []
                while tmp_node:
                    array.append(tmp_node.value)
                    tmp_node = tmp_node.right
                line += ', '.join(array)
            current_node = current_node.right
        self.ass_file_handler.insert(
            line, 'BSS' if variable_type == 'VARIABLE' else 'DATA')
        # 将该变量存入符号表
        self.symbol_table[variable_name] = {
            'type': variable_type, 'field_type': variable_field_type}

    # 函数调用
    def _function_call(self, node=None):
        current_node = node.first_son
        func_name = None
        parameter_list = []
        while current_node:
            # 函数名字
            if current_node.type == 'FUNCTION_NAME':
                func_name = current_node.value
                if func_name != 'scanf' and func_name != 'printf':
                    print ('function call except scanf and printf not supported yet!')
                    exit()
            # 函数参数
            elif current_node.value == 'CallParameterList':
                tmp_node = current_node.first_son
                while tmp_node:
                    # 是常数
                    if tmp_node.type == 'DIGIT_CONSTANT' or tmp_node.type == 'STRING_CONSTANT':
                        # 汇编中该参数的名称
                        label = 'label_' + str(self.label_cnt)
                        self.label_cnt += 1
                        if tmp_node.type == 'STRING_CONSTANT':
                            # 添加数据段中该参数定义
                            line = label + ': .asciz "' + tmp_node.value + '"'
                            self.ass_file_handler.insert(line, 'DATA')
                        else:
                            print ('in functionc_call digital constant parameter is not supported yet!')
                            exit()
                        self.symbol_table[label] = {
                            'type': 'STRING_CONSTANT', 'value': tmp_node.value}
                        parameter_list.append(label)
                    # 是某个变量
                    elif tmp_node.type == 'IDENTIFIER':
                        parameter_list.append(tmp_node.value)
                    elif tmp_node.type == 'ADDRESS':
                        pass
                    else:
                        print (tmp_node.value)
                        print (tmp_node.type)
                        print ('parameter type is not supported yet!')
                        exit()
                    tmp_node = tmp_node.right
            current_node = current_node.right
        # 添加到代码段
        if func_name == 'printf':
            #%esp要+的值
            num = 0
            for parameter in parameter_list[::-1]:
                # 如果该参数的类型是字符串常量
                if self.symbol_table[parameter]['type'] == 'STRING_CONSTANT':
                    line = 'pushl $' + parameter
                    self.ass_file_handler.insert(line, 'TEXT')
                    num += 1
                elif self.symbol_table[parameter]['type'] == 'VARIABLE':
                    field_type = self.symbol_table[parameter]['field_type']
                    if field_type == 'int':
                        line = 'pushl ' + parameter
                        self.ass_file_handler.insert(line, 'TEXT')
                        num += 1
                    elif field_type == 'float':
                        line = 'flds ' + parameter
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = r'subl $8, %esp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = r'fstpl (%esp)'
                        self.ass_file_handler.insert(line, 'TEXT')
                        num += 2
                    else:
                        print ('field type except int and float is not supported yet!')
                        exit()
                else:
                    print ('parameter type not supported in printf yet!')
                    exit()
            line = 'call printf'
            self.ass_file_handler.insert(line, 'TEXT')
            line = 'add $' + str(num * 4) + ', %esp'
            self.ass_file_handler.insert(line, 'TEXT')
        elif func_name == 'scanf':
            num = 0
            for parameter in parameter_list[::-1]:
                parameter_type = self.symbol_table[parameter]['type']
                if parameter_type == 'STRING_CONSTANT' or parameter_type == 'VARIABLE':
                    num += 1
                    line = 'pushl $' + parameter
                    self.ass_file_handler.insert(line, 'TEXT')
                else:
                    print ('parameter type not supported in scanf!')
                    exit()
            line = 'call scanf'
            self.ass_file_handler.insert(line, 'TEXT')
            line = 'add $' + str(num * 4) + ', %esp'
            self.ass_file_handler.insert(line, 'TEXT')
    # 赋值语句

    def _assignment(self, node=None):
        current_node = node.first_son
        if current_node.type == 'IDENTIFIER' and current_node.right.value == 'Expression':
            expres = self._expression(current_node.right)
            # 该变量的类型
            field_type = self.symbol_table[current_node.value]['field_type']
            if field_type == 'int':
                # 常数
                if expres['type'] == 'CONSTANT':
                    line = 'movl $' + \
                        expres['value'] + ', ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                elif expres['type'] == 'VARIABLE':
                    line = 'movl ' + expres['value'] + ', ' + '%edi'
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'movl %edi, ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                else:
                    pass
            elif field_type == 'float':
                if expres['type'] == 'CONSTANT':
                    line = 'movl $' + \
                        expres['value'] + ', ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'filds ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'fstps ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                else:
                    line = 'fstps ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
            else:
                print ('field type except int and float not supported!')
                exit()
        else:
            print ('assignment wrong.')
            exit()

    # for语句
    def _control_for(self, node=None):
        current_node = node.first_son
        # 遍历的是for循环中的那个部分
        cnt = 2
        while current_node:
            # for第一部分
            if current_node.value == 'Assignment':
                self._assignment(current_node)
            # for第二、三部分
            elif current_node.value == 'Expression':
                if cnt == 2:
                    cnt += 1
                    line = 'label_' + str(self.label_cnt) + ':'
                    self.ass_file_handler.insert(line, 'TEXT')
                    self.label_cnt += 1
                    self._expression(current_node)
                else:
                    self._expression(current_node)
            # for语句部分
            elif current_node.value == 'Sentence':
                self.traverse(current_node.first_son)
            current_node = current_node.right
        line = 'jmp label_' + str(self.label_cnt - 1)
        self.ass_file_handler.insert(line, 'TEXT')
        line = 'label_' + str(self.label_cnt) + ':'
        self.ass_file_handler.insert(line, 'TEXT')
        self.label_cnt += 1

    # if else语句
    def _control_if(self, node=None):
        current_node = node.first_son
        self.labels_ifelse['label_else'] = 'label_' + str(self.label_cnt)
        self.label_cnt += 1
        self.labels_ifelse['label_end'] = 'label_' + str(self.label_cnt)
        self.label_cnt += 1
        while current_node:
            if current_node.value == 'IfControl':
                if current_node.first_son.value != 'Expression' or current_node.first_son.right.value != 'Sentence':
                    print ('control_if error!')
                    exit()
                self._expression(current_node.first_son)
                self.traverse(current_node.first_son.right.first_son)
                line = 'jmp ' + self.labels_ifelse['label_end']
                self.ass_file_handler.insert(line, 'TEXT')
                line = self.labels_ifelse['label_else'] + ':'
                self.ass_file_handler.insert(line, 'TEXT')
            elif current_node.value == 'ElseControl':
                self.traverse(current_node.first_son)
                line = self.labels_ifelse['label_end'] + ':'
                self.ass_file_handler.insert(line, 'TEXT')
            current_node = current_node.right

    # while语句
    def _control_while(self, node=None):
        print ('while not supported yet!')

    # return语句
    def _return(self, node=None):
        current_node = node.first_son
        if current_node.value != 'return' or current_node.right.value != 'Expression':
            print ('return error!')
            exit()
        else:
            current_node = current_node.right
            expres = self._expression(current_node)
            if expres['type'] == 'CONSTANT':
                line = 'pushl $' + expres['value']
                self.ass_file_handler.insert(line, 'TEXT')
                line = 'call exit'
                self.ass_file_handler.insert(line, 'TEXT')
            else:
                print ('return type not supported!')
                exit()

    # 遍历表达式
    def _traverse_expression(self, node=None):
        if not node:
            return
        if node.type == '_Variable':
            self.operand_stack.append(
                {'type': 'VARIABLE', 'operand': node.value})
        elif node.type == '_Constant':
            self.operand_stack.append(
                {'type': 'CONSTANT', 'operand': node.value})
        elif node.type == '_Operator':
            self.operator_stack.append(node.value)
        elif node.type == '_ArrayName':
            self.operand_stack.append(
                {'type': 'ARRAY_ITEM', 'operand': [node.value, node.right.value]})
            return
        current_node = node.first_son
        while current_node:
            self._traverse_expression(current_node)
            current_node = current_node.right

    # 判断一个变量是不是float类型
    def _is_float(self, operand):
        return operand['type'] == 'VARIABLE' and self.symbol_table[operand['operand']]['field_type'] == 'float'
    # 判断两个操作数中是否含有float类型的数

    def _contain_float(self, operand_a, operand_b):
        return self._is_float(operand_a) or self._is_float(operand_b)

    # 表达式
    def _expression(self, node=None):
        if node.type == 'Constant':
            return {'type': 'CONSTANT', 'value': node.first_son.value}
        # 先清空
        self.operator_priority = []
        self.operand_stack = []
        # 遍历该表达式
        self._traverse_expression(node)

        # 双目运算符
        double_operators = ['+', '-', '*', '/', '>', '<', '>=', '<=']
        # 单目运算符
        single_operators = ['++', '--']
        # 运算符对汇编指令的映射
        operator_map = {'>': 'jbe', '<': 'jae', '>=': 'jb', '<=': 'ja'}
        while self.operator_stack:
            operator = self.operator_stack.pop()
            if operator in double_operators:
                operand_b = self.operand_stack.pop()
                operand_a = self.operand_stack.pop()
                contain_float = self._contain_float(operand_a, operand_b)
                if operator == '+':
                    if contain_float:
                        line = 'flds ' if self._is_float(
                            operand_a) else 'filds '
                        line += operand_a['operand']
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'fadd ' if self._is_float(
                            operand_b) else 'fiadd '
                        line += operand_b['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        # 计算结果保存到bss_tmp中
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 计算结果压栈
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        # 记录到符号表中
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        # 第一个操作数
                        if operand_a['type'] == 'ARRAY_ITEM':
                            line = 'movl ' + \
                                operand_a['operand'][1] + r', %edi'
                            self.ass_file_handler.insert(line, 'TEXT')
                            line = 'movl ' + \
                                operand_a['operand'][0] + r'(, %edi, 4), %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_a['type'] == 'VARIABLE':
                            line = 'movl ' + operand_a['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_a['type'] == 'CONSTANT':
                            line = 'movl $' + operand_a['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        # 加上第二个操作数
                        if operand_b['type'] == 'ARRAY_ITEM':
                            line = 'movl ' + \
                                operand_b['operand'][1] + r', %edi'
                            self.ass_file_handler.insert(line, 'TEXT')
                            line = 'addl ' + \
                                operand_b['operand'][0] + r'(, %edi, 4), %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_b['type'] == 'VARIABLE':
                            line = 'addl ' + operand_b['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        elif operand_b['type'] == 'CONSTANT':
                            line = 'addl $' + operand_b['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        # 赋值给临时操作数
                        line = 'movl %eax, bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 计算结果压栈
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        # 记录到符号表中
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'int'}

                elif operator == '-':
                    if contain_float:
                        # 操作数a
                        if self._is_float(operand_a):
                            if operand_a['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_a) else 'filds '
                                line += operand_a['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        else:
                            if operand_a['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_a['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        # 操作数b
                        if self._is_float(operand_b):
                            if operand_b['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_b) else 'filds '
                                line += operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fsub ' + operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        else:
                            if operand_b['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_b['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fisub bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                        # 计算结果保存到bss_tmp中
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 计算结果压栈
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        # 记录到符号表中
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        print ('not supported yet!')
                        exit()
                # 尚未考虑浮点数，只考虑整数乘法
                elif operator == '*':
                    if operand_a['type'] == 'ARRAY_ITEM':
                        line = 'movl ' + operand_a['operand'][1] + r', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'movl ' + \
                            operand_a['operand'][0] + r'(, %edi, 4), %eax'
                        self.ass_file_handler.insert(line, 'TEXT')
                    else:
                        print ('other MUL not supported yet!')
                        exit()

                    if operand_b['type'] == 'ARRAY_ITEM':
                        line = 'movl ' + operand_b['operand'][1] + r', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 相乘
                        line = 'mull ' + \
                            operand_b['operand'][0] + '(, %edi, 4)'
                        self.ass_file_handler.insert(line, 'TEXT')
                    else:
                        print ('other MUL not supported yet!')
                        exit()
                    # 将所得结果压入栈
                    line = r'movl %eax, bss_tmp'
                    self.ass_file_handler.insert(line, 'TEXT')
                    self.operand_stack.append(
                        {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                    self.symbol_table['bss_tmp'] = {
                        'type': 'IDENTIFIER', 'field_type': 'int'}
                elif operator == '/':
                    if contain_float:
                        line = 'flds ' if self._is_float(
                            operand_a) else 'filds '
                        line += operand_a['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'fdiv ' if self._is_float(
                            operand_b) else 'fidiv '
                        line += operand_b['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        # 计算结果保存到bss_tmp中
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # 计算结果压栈
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        # 记录到符号表中
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        pass
                elif operator == '>=':
                    if contain_float:
                        if self._is_float(operand_a):
                            if operand_a['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_a) else 'filds '
                                line += operand_a['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                print ('array item not supported when >=')
                                exit()
                        else:
                            pass

                        if self._is_float(operand_b):
                            if operand_b['type'] == 'VARIABLE':
                                line = 'fcom ' + operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                print ('array item not supported when >=')
                                exit()
                        else:
                            if operand_b['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_b['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fcom bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = operator_map[
                                    '>='] + ' ' + self.labels_ifelse['label_else']
                                self.ass_file_handler.insert(line, 'TEXT')
                            else:
                                pass
                    else:
                        pass
                elif operator == '<':
                    if contain_float:
                        pass
                    else:
                        line = 'movl $' if operand_a[
                            'type'] == 'CONSTANT' else 'movl '
                        line += operand_a['operand'] + ', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'movl $' if operand_b[
                            'type'] == 'CONSTANT' else 'movl '
                        line += operand_b['operand'] + ', %esi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = r'cmpl %esi, %edi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = operator_map[
                            '<'] + ' ' + 'label_' + str(self.label_cnt)
                        self.ass_file_handler.insert(line, 'TEXT')

            elif operator in single_operators:
                operand = self.operand_stack.pop()
                if operator == '++':
                    line = 'incl ' + operand['operand']
                    self.ass_file_handler.insert(line, 'TEXT')
                elif operator == '--':
                    pass
            else:
                print ('operator not supported!')
                exit()
        result = {'type': self.operand_stack[0]['type'], 'value': self.operand_stack[
            0]['operand']} if self.operand_stack else {'type': '', 'value': ''}
        return result

    # 处理某一种句型
    def _handler_block(self, node=None):
        if not node:
            return
        # 下一个将要遍历的节点
        if node.value in self.sentence_type:
            # 如果是根节点
            if node.value == 'Sentence':
                self.traverse(node.first_son)
            # include语句
            elif node.value == 'Include':
                self._include(node)
            # 函数声明
            elif node.value == 'FunctionStatement':
                self._function_statement(node)
            # 声明语句
            elif node.value == 'Statement':
                self._statement(node)
            # 函数调用
            elif node.value == 'FunctionCall':
                self._function_call(node)
            # 赋值语句
            elif node.value == 'Assignment':
                self._assignment(node)
            # 控制语句
            elif node.value == 'Control':
                if node.type == 'IfElseControl':
                    self._control_if(node)
                elif node.type == 'ForControl':
                    self._control_for(node)
                elif node.type == 'WhileControl':
                    self._control_while()
                else:
                    print ('control type not supported!')
                    exit()
            # 表达式语句
            elif node.value == 'Expression':
                self._expression(node)
            # return语句
            elif node.value == 'Return':
                self._return(node)
            else:
                print ('sentenct type not supported yet！')
                exit()

    # 遍历节点
    def traverse(self, node=None):
        self._handler_block(node)
        next_node = node.right
        while next_node:
            self._handler_block(next_node)
            next_node = next_node.right