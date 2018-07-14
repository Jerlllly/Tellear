from Lexer import Lexer
# 关键字
keywords = [
    ['int', 'float', 'double', 'char', 'void'],
    ['if', 'for', 'while', 'do', 'else'], ['include', 'return'],
]

# 运算符
operators = [
    '=', '&', '<', '>', '++', '--', '+', '-', '*', '/', '>=', '<=', '!='
]

class SyntaxTreeNode(object):
    '''语法树节点'''

    def __init__(self, value=None, _type=None, extra_info=None):
        # 节点的值，为文法中的终结符或者非终结符
        self.value = value
        # 记录某些token的类型
        self.type = _type
        # 语义分析中记录关于token的其他一些信息，比如关键字是变量，该变量类型为int
        self.extra_info = extra_info
        self.father = None
        self.left = None
        self.right = None
        self.first_son = None
    # 设置value

    def set_value(self, value):
        self.value = value
    # 设置type

    def set_type(self, _type):
        self.type = _type
    # 设置extra_info

    def set_extra_info(self, extra_info):
        self.extra_info = extra_info


class SyntaxTree(object):
    '''语法树'''

    def __init__(self):
        # 树的根节点
        self.root = None
        # 现在遍历到的节点
        self.current = None

    # 添加一个子节点，必须确定father在该树中
    def add_child_node(self, new_node, father=None):
        if not father:
            father = self.current
        # 认祖归宗
        new_node.father = father
        # 如果father节点没有儿子，则将其赋值为其第一个儿子
        if not father.first_son:
            father.first_son = new_node
        else:
            current_node = father.first_son
            while current_node.right:
                current_node = current_node.right
            current_node.right = new_node
            new_node.left = current_node
        self.current = new_node

    # 交换相邻的两棵兄弟子树
    def switch(self, left, right):
        left_left = left.left
        right_right = right.right
        left.left = right
        left.right = right_right
        right.left = left_left
        right.right = left
        if left_left:
            left_left.right = right
        if right_right:
            right_right.left = left


class Parser(object):
    '''语法分析器'''

    def __init__(self,content):
        lexer = Lexer()
        lexer.main(content)
        # 要分析的tokens
        self.tokens = lexer.tokens
        # tokens下标
        self.index = 0
        # 最终生成的语法树
        self.tree = SyntaxTree()

    # 处理大括号里的部分
    def _block(self, father_tree):
        self.index += 1
        sentence_tree = SyntaxTree()
        sentence_tree.current = sentence_tree.root = SyntaxTreeNode('Sentence')
        father_tree.add_child_node(sentence_tree.root, father_tree.root)
        while True:
            # 句型
            sentence_pattern = self._judge_sentence_pattern()
            # 声明语句
            if sentence_pattern == 'STATEMENT':
                self._statement(sentence_tree.root)
            # 赋值语句
            elif sentence_pattern == 'ASSIGNMENT':
                self._assignment(sentence_tree.root)
            # 函数调用
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call(sentence_tree.root)
            # 控制流语句
            elif sentence_pattern == 'CONTROL':
                self._control(sentence_tree.root)
            # return语句
            elif sentence_pattern == 'RETURN':
                self._return(sentence_tree.root)
            # 右大括号，函数结束
            elif sentence_pattern == 'RB_BRACKET':
                break
            else:
                print ('block error!')
                exit()

    # include句型
    def _include(self, father=None):
        if not father:
            father = self.tree.root
        include_tree = SyntaxTree()
        include_tree.current = include_tree.root = SyntaxTreeNode('Include')
        self.tree.add_child_node(include_tree.root, father)
        # include语句中双引号的个数
        cnt = 0
        # include语句是否结束
        flag = True
        while flag:
            if self.tokens[self.index] == '\"':
                cnt += 1
            if self.index >= len(self.tokens) or cnt >= 2 or self.tokens[self.index].value == '>':
                flag = False
            include_tree.add_child_node(
                SyntaxTreeNode(self.tokens[self.index].value), include_tree.root)
            self.index += 1

    # 函数声明
    def _function_statement(self, father=None):
        if not father:
            father = self.tree.root
        func_statement_tree = SyntaxTree()
        func_statement_tree.current = func_statement_tree.root = SyntaxTreeNode(
            'FunctionStatement')
        self.tree.add_child_node(func_statement_tree.root, father)
        # 函数声明语句什么时候结束
        flag = True
        while flag and self.index < len(self.tokens):
            # 如果是函数返回类型
            if self.tokens[self.index].value in keywords[0]:
                return_type = SyntaxTreeNode('Type')
                func_statement_tree.add_child_node(return_type)
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
                self.index += 1
            # 如果是函数名
            elif self.tokens[self.index].type == 'IDENTIFIER':
                func_name = SyntaxTreeNode('FunctionName')
                func_statement_tree.add_child_node(
                    func_name, func_statement_tree.root)
                # extra_info
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {'type': 'FUNCTION_NAME'}))
                self.index += 1
            # 如果是参数序列
            elif self.tokens[self.index].type == 'LL_BRACKET':
                params_list = SyntaxTreeNode('StateParameterList')
                func_statement_tree.add_child_node(
                    params_list, func_statement_tree.root)
                self.index += 1
                while self.tokens[self.index].type != 'RL_BRACKET':
                    if self.tokens[self.index].value in keywords[0]:
                        param = SyntaxTreeNode('Parameter')
                        func_statement_tree.add_child_node(param, params_list)
                        # extra_info
                        func_statement_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}), param)
                        if self.tokens[self.index + 1].type == 'IDENTIFIER':
                            # extra_info
                            func_statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index + 1].value, 'IDENTIFIER', {
                                                               'type': 'VARIABLE', 'variable_type': self.tokens[self.index].value}), param)
                        else:
                            print ('函数定义参数错误！')
                            exit()
                        self.index += 1
                    self.index += 1
                self.index += 1
            # 如果是遇见了左大括号
            elif self.tokens[self.index].type == 'LB_BRACKET':
                self._block(func_statement_tree)

    # 声明语句
    def _statement(self, father=None):
        if not father:
            father = self.tree.root
        statement_tree = SyntaxTree()
        statement_tree.current = statement_tree.root = SyntaxTreeNode(
            'Statement')
        self.tree.add_child_node(statement_tree.root, father)
        # 暂时用来保存当前声明语句的类型，以便于识别多个变量的声明
        tmp_variable_type = None
        while self.tokens[self.index].type != 'SEMICOLON':
            # 变量类型
            if self.tokens[self.index].value in keywords[0]:
                tmp_variable_type = self.tokens[self.index].value
                variable_type = SyntaxTreeNode('Type')
                statement_tree.add_child_node(variable_type)
                # extra_info
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
            # 变量名
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # extra_info
                statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                              'type': 'VARIABLE', 'variable_type': tmp_variable_type}), statement_tree.root)
            # 数组大小
            elif self.tokens[self.index].type == 'DIGIT_CONSTANT':
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'DIGIT_CONSTANT'), statement_tree.root)
                statement_tree.current.left.set_extra_info(
                    {'type': 'LIST', 'list_type': tmp_variable_type})
            # 数组元素
            elif self.tokens[self.index].type == 'LB_BRACKET':
                self.index += 1
                constant_list = SyntaxTreeNode('ConstantList')
                statement_tree.add_child_node(
                    constant_list, statement_tree.root)
                while self.tokens[self.index].type != 'RB_BRACKET':
                    if self.tokens[self.index].type == 'DIGIT_CONSTANT':
                        statement_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'DIGIT_CONSTANT'), constant_list)
                    self.index += 1
            # 多个变量声明
            elif self.tokens[self.index].type == 'COMMA':
                while self.tokens[self.index].type != 'SEMICOLON':
                    if self.tokens[self.index].type == 'IDENTIFIER':
                        tree = SyntaxTree()
                        tree.current = tree.root = SyntaxTreeNode('Statement')
                        self.tree.add_child_node(tree.root, father)
                        # 类型
                        variable_type = SyntaxTreeNode('Type')
                        tree.add_child_node(variable_type)
                        # extra_info
                        # 类型
                        tree.add_child_node(
                            SyntaxTreeNode(tmp_variable_type, 'FIELD_TYPE', {'type': tmp_variable_type}))
                        # 变量名
                        tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                            'type': 'VARIABLE', 'variable_type': tmp_variable_type}), tree.root)
                    self.index += 1
                break
            self.index += 1
        self.index += 1

    # 赋值语句
    def _assignment(self, father=None):
        if not father:
            father = self.tree.root
        assign_tree = SyntaxTree()
        assign_tree.current = assign_tree.root = SyntaxTreeNode('Assignment')
        self.tree.add_child_node(assign_tree.root, father)
        while self.tokens[self.index].type != 'SEMICOLON':
            # 被赋值的变量
            if self.tokens[self.index].type == 'IDENTIFIER':
                assign_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER'))
                self.index += 1
            elif self.tokens[self.index].type == 'ASSIGN':
                self.index += 1
                self._expression(assign_tree.root)
        self.index += 1

    # while语句，没处理do-while的情况，只处理了while
    def _while(self, father=None):
        while_tree = SyntaxTree()
        while_tree.current = while_tree.root = SyntaxTreeNode(
            'Control', 'WhileControl')
        self.tree.add_child_node(while_tree.root, father)

        self.index += 1
        if self.tokens[self.index].type == 'LL_BRACKET':
            tmp_index = self.index
            while self.tokens[tmp_index].type != 'RL_BRACKET':
                tmp_index += 1
            self._expression(while_tree.root, tmp_index)

            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(while_tree)

    # for语句
    def _for(self, father=None):
        for_tree = SyntaxTree()
        for_tree.current = for_tree.root = SyntaxTreeNode(
            'Control', 'ForControl')
        self.tree.add_child_node(for_tree.root, father)
        # 标记for语句是否结束
        while True:
            token_type = self.tokens[self.index].type
            # for标记
            if token_type == 'FOR':
                self.index += 1
            # 左小括号
            elif token_type == 'LL_BRACKET':
                self.index += 1
                # 首先找到右小括号的位置
                tmp_index = self.index
                while self.tokens[tmp_index].type != 'RL_BRACKET':
                    tmp_index += 1
                # for语句中的第一个分号前的部分
                self._assignment(for_tree.root)
                # 两个分号中间的部分
                self._expression(for_tree.root)
                self.index += 1
                # 第二个分号后的部分
                self._expression(for_tree.root, tmp_index)
                self.index += 1
            # 如果为左大括号
            elif token_type == 'LB_BRACKET':
                self._block(for_tree)
                break
        # 交换for语句下第三个子节点和第四个子节点
        current_node = for_tree.root.first_son.right.right
        next_node = current_node.right
        for_tree.switch(current_node, next_node)

    # if语句
    def _if_else(self, father=None):
        if_else_tree = SyntaxTree()
        if_else_tree.current = if_else_tree.root = SyntaxTreeNode(
            'Control', 'IfElseControl')
        self.tree.add_child_node(if_else_tree.root, father)

        if_tree = SyntaxTree()
        if_tree.current = if_tree.root = SyntaxTreeNode('IfControl')
        if_else_tree.add_child_node(if_tree.root)

        # if标志
        if self.tokens[self.index].type == 'IF':
            self.index += 1
            # 左小括号
            if self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                # 右小括号位置
                tmp_index = self.index
                while self.tokens[tmp_index].type != 'RL_BRACKET':
                    tmp_index += 1
                self._expression(if_tree.root, tmp_index)
                self.index += 1
            else:
                print ('error: lack of left bracket!')
                exit()

            # 左大括号
            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(if_tree)

        # 如果是else关键字
        if self.tokens[self.index].type == 'ELSE':
            self.index += 1
            else_tree = SyntaxTree()
            else_tree.current = else_tree.root = SyntaxTreeNode('ElseControl')
            if_else_tree.add_child_node(else_tree.root, if_else_tree.root)
            # 左大括号
            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(else_tree)

    def _control(self, father=None):
        token_type = self.tokens[self.index].type
        if token_type == 'WHILE' or token_type == 'DO':
            self._while(father)
        elif token_type == 'IF':
            self._if_else(father)
        elif token_type == 'FOR':
            self._for(father)
        else:
            print ('error: control style not supported!')
            exit()

    # 表达式
    def _expression(self, father=None, index=None):
        if not father:
            father = self.tree.root
        # 运算符优先级
        operator_priority = {'>': 0, '<': 0, '>=': 0, '<=': 0,
                             '+': 1, '-': 1, '*': 2, '/': 2, '++': 3, '--': 3, '!': 3}
        # 运算符栈
        operator_stack = []
        # 转换成的逆波兰表达式结果
        reverse_polish_expression = []
        # 中缀表达式转为后缀表达式，即逆波兰表达式
        while self.tokens[self.index].type != 'SEMICOLON':
            if index and self.index >= index:
                break
            # 如果是常量
            if self.tokens[self.index].type == 'DIGIT_CONSTANT':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Expression', 'Constant')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Constant'))
                reverse_polish_expression.append(tree)
            # 如果是变量或者数组的某元素
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # 变量
                if self.tokens[self.index + 1].value in operators or self.tokens[self.index + 1].type == 'SEMICOLON':
                    tree = SyntaxTree()
                    tree.current = tree.root = SyntaxTreeNode(
                        'Expression', 'Variable')
                    tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, '_Variable'))
                    reverse_polish_expression.append(tree)
                # 数组的某一个元素ID[i]
                elif self.tokens[self.index + 1].type == 'LM_BRACKET':
                    tree = SyntaxTree()
                    tree.current = tree.root = SyntaxTreeNode(
                        'Expression', 'ArrayItem')
                    # 数组的名字
                    tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, '_ArrayName'))
                    self.index += 2
                    if self.tokens[self.index].type != 'DIGIT_CONSTANT' and self.tokens[self.index].type != 'IDENTIFIER':
                        print ('error: 数组下表必须为常量或标识符')
                        print (self.tokens[self.index].type)
                        exit()
                    else:
                        # 数组下标
                        tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, '_ArrayIndex'), tree.root)
                        reverse_polish_expression.append(tree)
            # 如果是运算符
            elif self.tokens[self.index].value in operators or self.tokens[self.index].type == 'LL_BRACKET' or self.tokens[self.index].type == 'RL_BRACKET':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Operator', 'Operator')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Operator'))
                # 如果是左括号，直接压栈
                if self.tokens[self.index].type == 'LL_BRACKET':
                    operator_stack.append(tree.root)
                # 如果是右括号，弹栈直到遇到左括号为止
                elif self.tokens[self.index].type == 'RL_BRACKET':
                    while operator_stack and operator_stack[-1].current.type != 'LL_BRACKET':
                        reverse_polish_expression.append(operator_stack.pop())
                    # 将左括号弹出来
                    if operator_stack:
                        operator_stack.pop()
                # 其他只能是运算符
                else:
                    while operator_stack and operator_priority[tree.current.value] < operator_priority[operator_stack[-1].current.value]:
                        reverse_polish_expression.append(operator_stack.pop())
                    operator_stack.append(tree)
            self.index += 1
        # 最后将符号栈清空，最终得到逆波兰表达式reverse_polish_expression
        while operator_stack:
            reverse_polish_expression.append(operator_stack.pop())
        # 打印
        # for item in reverse_polish_expression:
        #   print item.current.value,
        # print

        # 操作数栈
        operand_stack = []
        child_operators = [['!', '++', '--'], [
            '+', '-', '*', '/', '>', '<', '>=', '<=']]
        for item in reverse_polish_expression:
            if item.root.type != 'Operator':
                operand_stack.append(item)
            else:
                # 处理单目运算符
                if item.current.value in child_operators[0]:
                    a = operand_stack.pop()
                    new_tree = SyntaxTree()
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'SingleOperand')
                    # 添加操作符
                    new_tree.add_child_node(item.root)
                    # 添加操作数
                    new_tree.add_child_node(a.root, new_tree.root)
                    operand_stack.append(new_tree)
                # 双目运算符
                elif item.current.value in child_operators[1]:
                    b = operand_stack.pop()
                    a = operand_stack.pop()
                    new_tree = SyntaxTree()
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'DoubleOperand')
                    # 第一个操作数
                    new_tree.add_child_node(a.root)
                    # 操作符
                    new_tree.add_child_node(item.root, new_tree.root)
                    # 第二个操作数
                    new_tree.add_child_node(b.root, new_tree.root)
                    operand_stack.append(new_tree)
                else:
                    print ('operator %s not supported!' % item.current.value)
                    exit()
        self.tree.add_child_node(operand_stack[0].root, father)

    # 函数调用
    def _function_call(self, father=None):
        if not father:
            father = self.tree.root
        func_call_tree = SyntaxTree()
        func_call_tree.current = func_call_tree.root = SyntaxTreeNode(
            'FunctionCall')
        self.tree.add_child_node(func_call_tree.root, father)

        while self.tokens[self.index].type != 'SEMICOLON':
            # 函数名
            if self.tokens[self.index].type == 'IDENTIFIER':
                func_call_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FUNCTION_NAME'))
            # 左小括号
            elif self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                params_list = SyntaxTreeNode('CallParameterList')
                func_call_tree.add_child_node(params_list, func_call_tree.root)
                while self.tokens[self.index].type != 'RL_BRACKET':
                    if self.tokens[self.index].type == 'IDENTIFIER' or self.tokens[self.index].type == 'DIGIT_CONSTANT' or self.tokens[self.index].type == 'STRING_CONSTANT':
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                    elif self.tokens[self.index].type == 'DOUBLE_QUOTE':
                        self.index += 1
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                        self.index += 1
                    elif self.tokens[self.index].type == 'ADDRESS':
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'ADDRESS'), params_list)
                    self.index += 1
            else:
                print ('function call error!')
                exit()
            self.index += 1
        self.index += 1

    # return语句
    def _return(self, father=None):
        if not father:
            father = self.tree.root
        return_tree = SyntaxTree()
        return_tree.current = return_tree.root = SyntaxTreeNode('Return')
        self.tree.add_child_node(return_tree.root, father)
        while self.tokens[self.index].type != 'SEMICOLON':
            # 被赋值的变量
            if self.tokens[self.index].type == 'RETURN':
                return_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value))
                self.index += 1
            else:
                self._expression(return_tree.root)
        self.index += 1

    # 根据一个句型的句首判断句型
    def _judge_sentence_pattern(self):
        token_value = self.tokens[self.index].value
        token_type = self.tokens[self.index].type
        # include句型
        if token_type == 'SHARP' and self.tokens[self.index + 1].type == 'INCLUDE':
            return 'INCLUDE'
        # 控制句型
        elif token_value in keywords[1]:
            return 'CONTROL'
        # 有可能是声明语句或者函数声明语句
        elif token_value in keywords[0] and self.tokens[self.index + 1].type == 'IDENTIFIER':
            index_2_token_type = self.tokens[self.index + 2].type
            if index_2_token_type == 'LL_BRACKET':
                return 'FUNCTION_STATEMENT'
            elif index_2_token_type == 'SEMICOLON' or index_2_token_type == 'LM_BRACKET' or index_2_token_type == 'COMMA':
                return 'STATEMENT'
            else:
                return 'ERROR'
        # 可能为函数调用或者赋值语句
        elif token_type == 'IDENTIFIER':
            index_1_token_type = self.tokens[self.index + 1].type
            if index_1_token_type == 'LL_BRACKET':
                return 'FUNCTION_CALL'
            elif index_1_token_type == 'ASSIGN':
                return 'ASSIGNMENT'
            else:
                return 'ERROR'
        # return语句
        elif token_type == 'RETURN':
            return 'RETURN'
        # 右大括号，表明函数的结束
        elif token_type == 'RB_BRACKET':
            self.index += 1
            return 'RB_BRACKET'
        else:
            return 'ERROR'

    # 主程序
    def main(self):
        # 根节点
        self.tree.current = self.tree.root = SyntaxTreeNode('Sentence')
        while self.index < len(self.tokens):
            # 句型
            sentence_pattern = self._judge_sentence_pattern()
            # 如果是include句型
            if sentence_pattern == 'INCLUDE':
                self._include()
            # 函数声明语句
            elif sentence_pattern == 'FUNCTION_STATEMENT':
                self._function_statement()
                break
            # 声明语句
            elif sentence_pattern == 'STATEMENT':
                self._statement()
            # 函数调用
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call()
            else:
                print ('main error!')
                exit()

    # DFS遍历语法树
    def display(self, node):
        if not node:
            return
        #print ('( self: %s %s, father: %s, left: %s, right: %s )' % (node.value, node.type, node.father.value if node.father else None, node.left.value if node.left else None, node.right.value if node.right else None))
      #  temp=('( '+'self: '+node.value+' '+node.type+', '+'father: ')
      #   temp='( '+'self: '
      #   if node.value!=None:
      #       temp=temp+node.value+' '
      #   if node.type!=None:
      #       temp=temp+node.type+','
      #   temp=temp+' father'
      #   if  node.father.value:
      #       temp=temp+node.father+', '
      #   else:
      #       temp=temp+' '+', '
      #   temp=temp+'left: '
      #
      #   if node.left.value:
      #       temp=temp+node.left+', '
      #   else:
      #       temp=temp+' '+', '
      #
      #   temp = temp + 'right: '
      #   if node.right.value:
      #       temp = temp + node.right + ' '
      #   else:
      #       temp = temp + ' ' + ' '
      #   temp=temp+')'
      #   print (temp)
      #   buffer.append(temp)
      #   print (buffer)
        f=open('tree.txt','a')
        f.write('( self: %s %s, father: %s, left: %s, right: %s )\n' % (node.value, node.type, node.father.value if node.father else None, node.left.value if node.left else None, node.right.value if node.right else None))
        child = node.first_son
        while child:
            self.display(child)
            child = child.right