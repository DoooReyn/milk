from typing import Union

from luaparser.ast import *
from luaparser.astnodes import *

from cmm import Cmm


class LuaSourceWriter:
    def __init__(self):
        self._tree = []
        self._lines = []
        self._indent = 0
        self._start = False

    def last(self, index: int = -1):
        if len(self._lines) > 0:
            return self._lines[index]

    def pop_last(self):
        self._lines.pop()

    def append_value(self, v):
        self._lines.append(str(v))

    def append_line(self):
        self.append_value('\n' + '\t' * self._indent)

    def indent(self):
        self._indent += 1
        self.append_line()

    def current_index(self):
        return self._indent

    def cal_indent(self, v: int):
        self._indent += v

    def unindent(self):
        self._indent -= 1
        self.append_line()

    def content(self):
        return ''.join(self._lines)

    def tree(self):
        return '\n'.join(self._tree)

    def slice(self, v: int):
        return self._lines[v::]

    def append_ast_node(self, v: str):
        self._tree.append('\t' * self._indent + str(v))


class LuaSourceInterpreter:
    def __init__(self, bracket_table_field: bool = False, with_comments: bool = True):
        self._writer = LuaSourceWriter()
        self._errors = []
        self._with_comments = with_comments
        self._bracket_table_field = bracket_table_field

    def interpret(self, chunk: Chunk):
        self._restore_block(chunk.body, False)
        return self

    def content(self):
        return self._writer.content()

    def tree(self):
        return self._writer.tree()

    def errors(self):
        if len(self._errors) > 0:
            return "\n".join(self._errors)

    def _append_error(self, e: str):
        self._errors.append(e)

    def get_last_type(self):
        last = self._writer.last()
        if last is not None:
            if last.endswith('{'):
                return last, 1
            if last.endswith('}') or last.endswith(',') or last.endswith(';') or last.endswith('end'):
                return last, 4
            elif last.find('\n') > -1:
                return last, 2
        return last, 3

    def _restore_head_comments(self, node: Node):
        if self._with_comments is True:
            if isinstance(node.comments, list) and len(node.comments) > 0:
                prefix = None
                last, kind = self.get_last_type()
                if kind == 1:
                    self._writer.indent()
                    prefix = '\n' + '\t' * self._writer.current_index()
                elif kind == 2:
                    prefix = last
                elif kind == 3:
                    prefix = '\n' + '\t' * self._writer.current_index()
                elif kind == 4:
                    prefix = '\n' + '\t' * (self._writer.current_index() + 1)
                    self._writer.append_value(prefix)

                fmt = '【head】\n    kind    = {}\n    last    = {}\n    prefix  = {}\n    comment = {}'
                print(fmt.format(kind, repr(last), repr(prefix), [c.s for c in node.comments]))

                self._writer.append_value(prefix.join([c.s for c in node.comments]))
                if kind == 1:
                    self._writer.cal_indent(-1)
                elif kind == 2 or kind == 3:
                    self._writer.append_line()

    def _restore_tail_comments(self, node: Node):
        if self._with_comments is True:
            if isinstance(node.tail_comments, list) and len(node.tail_comments) > 0:
                prefix = None
                last, kind = self.get_last_type()
                if kind == 1:
                    self._writer.indent()
                    prefix = '\n' + '\t' * self._writer.current_index()
                elif kind == 2:
                    prefix = last
                elif kind == 3:
                    self._writer.append_line()
                    prefix = '\n' + '\t' * self._writer.current_index()
                elif kind == 4:
                    prefix = '\n' + '\t' * self._writer.current_index()
                    self._writer.append_value(prefix)

                fmt = '【tail】\n    kind    = {}\n    last    = {}\n    prefix  = {}\n    comment = {}'
                print(fmt.format(kind, repr(last), repr(prefix), [c.s for c in node.tail_comments]))

                self._writer.append_value(prefix.join([c.s for c in node.tail_comments]))
                if kind == 1:
                    self._writer.cal_indent(-1)
                elif kind == 2:
                    self._writer.append_line()

    def _restore_comment(self, comment: Union[Comment, str]):
        if self._with_comments is False:
            return
        if isinstance(comment, str):
            self._writer.append_value(comment)
        elif isinstance(comment, Comment):
            self._writer.append_value(comment.s)
        self._writer.append_line()

    def _restore_block(self, node: Block, indent: bool = True):
        if indent is True:
            self._writer.indent()
        for index, item in enumerate(node.body):
            self._restore_node(item)
            if index < len(node.body) - 1:
                self._writer.append_line()
        self._restore_tail_comments(node)
        if indent is True:
            self._writer.unindent()

    def _restore_node(self, node: Node):
        self._writer.append_ast_node(node.display_name)
        self._restore_head_comments(node)
        if isinstance(node, Expression):
            self._restore_interpreter(node)
            self._restore_tail_comments(node)
        elif isinstance(node, Statement):
            self._restore_interpreter(node)
            self._restore_tail_comments(node)
        elif isinstance(node, Block):
            self._restore_block(node)
        elif isinstance(node, Comment):
            # self._restore_comment(node)
            pass
        else:
            self._append_error("!!! [{}] Node skipped...".format(node.display_name))

    def _restore_inner_node_list(self, nodes: List[Node], split: bool = True):
        length = len(nodes)
        for index, item in enumerate(nodes):
            self._restore_node(item)
            if split and index < length - 1:
                self._writer.append_value(', ')

    def _interpret_Comment(self, node: Comment):
        # self._writer.append_value(node.s)
        # self._writer.append_line()
        pass

    def _interpret_tail_Comment(self, node: Comment):
        self._writer.append_value(node.s)

    def _restore_interpreter(self, node: Union[Statement, Expression, Op]):
        fn_name = '_interpret_{}'.format(node.display_name)
        fn = getattr(self, fn_name, None)
        if fn is not None:
            fn(node)
            return
        self._append_error("!!! [{}] Interpreter not implemented: {}".format(node.display_name, fn_name))

    def _restore_binary_operator(self, op: BinaryOp, key: str):
        self._restore_node(op.left)
        self._writer.append_value(key)
        self._restore_node(op.right)

    def _interpret_LocalAssign(self, node: LocalAssign):
        self._writer.append_value('local ')
        self._restore_inner_node_list(node.targets)
        if len(node.values) > 0:
            self._writer.append_value(' = ')
        self._restore_inner_node_list(node.values)

    def _interpret_Assign(self, node: Assign):
        self._restore_inner_node_list(node.targets)
        if len(node.values) > 0:
            self._writer.append_value(' = ')
        self._restore_inner_node_list(node.values)

    def _interpret_Name(self, node: Name):
        self._writer.append_value(node.id)

    def _interpret_While(self, node: While):
        self._writer.append_value('while ')
        self._restore_node(node.test)
        self._writer.append_value(' ')
        self._writer.append_value('do')
        self._restore_node(node.body)
        self._writer.append_value('end')

    def _interpret_Do(self, node: Do):
        self._writer.append_value('do')
        self._restore_node(node.body)
        self._writer.append_value('end')

    def _interpret_Repeat(self, node: Repeat):
        self._writer.append_value('repeat')
        self._restore_node(node.body)
        self._writer.append_value('until ')
        self._restore_node(node.test)

    def _interpret_ElseIf(self, node: ElseIf):
        self._writer.append_value('elseif ')
        self._restore_node(node.test)
        self._writer.append_value(' then')
        self._restore_node(node.body)
        if isinstance(node.orelse, Block):
            self._writer.append_value('else')
            self._restore_node(node.orelse)
        elif isinstance(node.orelse, ElseIf):
            self._restore_node(node.orelse)

    def _interpret_If(self, node: If):
        self._writer.append_value('if ')
        self._restore_node(node.test)
        self._writer.append_value(' then')
        self._restore_node(node.body)
        if isinstance(node.orelse, Block):
            self._writer.append_value('else')
            self._restore_node(node.orelse)
        elif node.orelse is not None:
            self._restore_node(node.orelse)
        self._writer.append_value('end')

    def _interpret_Label(self, node: Label):
        self._writer.append_value('::{}::'.format(node.id.id))

    def _interpret_Goto(self, node: Goto):
        self._writer.append_value('goto {}'.format(node.label.id))

    def _interpret_SemiColon(self, node: SemiColon):
        # self._writer.append_value(';')
        pass

    def _interpret_Break(self, _: Break):
        self._writer.append_value('break')

    def _interpret_Fornum(self, node: Fornum):
        self._writer.append_value('for ')
        self._writer.append_value(node.target.id)
        self._writer.append_value(' = ')
        self._restore_node(node.start)
        self._writer.append_value(', ')
        self._restore_node(node.stop)
        if isinstance(node.step, Number):
            self._writer.append_value(', ')
            self._restore_node(node.step)
        self._writer.append_value(' do')
        self._restore_node(node.body)
        self._writer.append_value('end')

    def _interpret_Forin(self, node: Forin):
        self._writer.append_value('for ')
        targets_len = len(node.targets)
        for index, item in enumerate(node.targets):
            self._restore_node(item)
            if index < targets_len - 1:
                self._writer.append_value(', ')
        self._writer.append_value(' in ')
        iter_len = len(node.iter)
        for index, item in enumerate(node.iter):
            self._restore_node(item)
            if index < iter_len - 1:
                self._writer.append_value(', ')
        self._writer.append_value(' do')
        self._restore_node(node.body)
        self._writer.append_value('end')

    def _interpret_Call(self, node: Call):
        # self._writer.append_value('')
        self._restore_node(node.func)
        self._writer.append_value('(')
        args_len = len(node.args)
        for index, arg in enumerate(node.args):
            self._restore_node(arg)
            if index < args_len - 1:
                self._writer.append_value(', ')
        self._writer.append_value(')')

    def _interpret_Invoke(self, node: Invoke):
        self._restore_node(node.source)
        self._writer.append_value(':')
        self._restore_node(node.func)
        self._writer.append_value('(')
        args_len = len(node.args)
        for index, arg in enumerate(node.args):
            self._restore_node(arg)
            if index < args_len - 1:
                self._writer.append_value(', ')
        self._writer.append_value(')')

    def _interpret_function(self, node: Union[Function, LocalFunction, Method]):
        self._restore_node(node.name)
        self._writer.append_value(' (')
        args_len = len(node.args)
        for index, arg in enumerate(node.args):
            self._restore_node(arg)
            if index < args_len - 1:
                self._writer.append_value(', ')
        self._writer.append_value(')')
        self._restore_node(node.body)
        self._writer.append_value('end')

    def _interpret_Function(self, node: Function):
        self._writer.append_value('function ')
        self._interpret_function(node)

    def _interpret_LocalFunction(self, node: LocalFunction):
        self._writer.append_value('local function ')
        self._interpret_function(node)

    def _interpret_Method(self, node: Method):
        self._writer.append_value('function ')
        self._restore_node(node.source)
        self._writer.append_value(':')
        self._interpret_function(node)

    def _interpret_Return(self, node: Return):
        self._writer.append_value('return ')
        if node.values is not None:
            if isinstance(node.values, list):
                self._restore_inner_node_list(node.values)
            elif isinstance(node.values, Node):
                self._restore_node(node.values)
            else:
                self._writer.append_value(node.values)

    def _interpret_Index(self, node: Index):
        self._restore_node(node.value)
        if node.notation == IndexNotation.DOT:
            self._writer.append_value('.')
            self._writer.append_value(node.idx.id)
        elif node.notation == IndexNotation.SQUARE:
            self._writer.append_value('[')
            self._restore_node(node.idx)
            self._writer.append_value(']')

    def _interpret_Nil(self, _: Nil):
        self._writer.append_value('nil')

    def _interpret_True(self, _: TrueExpr):
        self._writer.append_value('true')

    def _interpret_False(self, _: FalseExpr):
        self._writer.append_value('false')

    def _interpret_Number(self, node: Number):
        self._writer.append_value(node.n)

    def _interpret_Varargs(self, _: Varargs):
        self._writer.append_value('...')

    def _interpret_String(self, node: String):
        if node.delimiter == StringDelimiter.SINGLE_QUOTE:
            self._writer.append_value("'{}'".format(node.s))
        elif node.delimiter == StringDelimiter.DOUBLE_QUOTE:
            self._writer.append_value('"{}"'.format(node.s))
        elif node.delimiter == StringDelimiter.DOUBLE_SQUARE:
            self._writer.append_value('[[{}]]'.format(node.s))

    def _interpret_Field(self, node: Field):
        self._writer.indent()

        if self._bracket_table_field:
            self._writer.append_value('[')
            if isinstance(node.key, Name):
                self._writer.append_value("'{}'".format(node.key.id))
            elif isinstance(node.key, Number):
                self._writer.append_value(node.key.n)
            elif node.key is not None:
                self._restore_node(node.key)
            self._writer.append_value('] = ')
        else:
            if isinstance(node.key, Name):
                self._writer.append_value('{} = '.format(node.key.id))
            elif isinstance(node.key, Number):
                pass
            elif node.key is not None:
                self._writer.append_value('[')
                self._restore_node(node.key)
                self._writer.append_value('] = ')

        self._restore_node(node.value)

        self._writer.unindent()

    def _interpret_Table(self, node: Table):
        if self._with_comments and (len(node.comments) > 0 or len(node.tail_comments) > 0):
            self._writer.indent()
        self._writer.append_value('{')

        table_len = len(node.fields)
        for index, filed in enumerate(node.fields):
            self._restore_node(filed)
            if index < table_len - 1:
                last = self._writer.last()
                if last and last.find('\n') > -1:
                    self._writer.pop_last()
                self._writer.append_value(',')
        self._writer.append_value('}')

    def _interpret_Dots(self, _: Dots):
        self._writer.append_value('...')

    def _interpret_AnonymousFunction(self, node: AnonymousFunction):
        self._writer.append_value('function (')
        for arg in node.args:
            self._restore_node(arg)
        self._writer.append_value(')')
        self._restore_node(node.body)
        self._writer.append_value('end')

    def _interpret_UnaryOp(self, node: UnaryOp):
        self._restore_interpreter(node)

    def _interpret_AddOp(self, op: AddOp):
        self._restore_binary_operator(op, ' + ')

    def _interpret_SubOp(self, op: SubOp):
        self._restore_binary_operator(op, ' - ')

    def _interpret_MultOp(self, op: MultOp):
        self._restore_binary_operator(op, ' * ')

    def _interpret_FloatDivOp(self, op: FloatDivOp):
        self._restore_binary_operator(op, ' / ')

    def _interpret_FloorDivOp(self, op: FloorDivOp):
        self._restore_binary_operator(op, ' // ')

    def _interpret_ModOp(self, op: ModOp):
        self._restore_binary_operator(op, ' % ')

    def _interpret_ExpoOp(self, op: ExpoOp):
        self._restore_binary_operator(op, ' ^ ')

    def _interpret_BAndOp(self, op: BAndOp):
        self._restore_binary_operator(op, ' & ')

    def _interpret_BOrOp(self, op: BOrOp):
        self._restore_binary_operator(op, ' | ')

    def _interpret_BXorOp(self, op: BXorOp):
        self._restore_binary_operator(op, ' ~ ')

    def _interpret_BShiftROp(self, op: BShiftROp):
        self._restore_binary_operator(op, ' >> ')

    def _interpret_BShiftLOp(self, op: BShiftLOp):
        self._restore_binary_operator(op, ' << ')

    def _interpret_RLtOp(self, op: LessThanOp):
        self._restore_binary_operator(op, ' < ')

    def _interpret_RGtOp(self, op: GreaterThanOp):
        self._restore_binary_operator(op, ' > ')

    def _interpret_RLtEqOp(self, op: LessOrEqThanOp):
        self._restore_binary_operator(op, ' <= ')

    def _interpret_RGtEqOp(self, op: GreaterOrEqThanOp):
        self._restore_binary_operator(op, ' >= ')

    def _interpret_REqOp(self, op: EqToOp):
        self._restore_binary_operator(op, ' == ')

    def _interpret_RNotEqOp(self, op: NotEqToOp):
        self._restore_binary_operator(op, ' ~= ')

    def _interpret_LAndOp(self, op: AndLoOp):
        self._restore_binary_operator(op, ' and ')

    def _interpret_LOrOp(self, op: OrLoOp):
        self._restore_binary_operator(op, ' or ')

    def _interpret_Concat(self, op: Concat):
        self._restore_binary_operator(op, ' .. ')

    def _interpret_UMinusOp(self, op: UMinusOp):
        self._writer.append_value('-')
        self._restore_node(op.operand)

    def _interpret_UBNotOp(self, op: UBNotOp):
        self._writer.append_value('~')
        self._restore_node(op.operand)

    def _interpret_ULNotOp(self, op: ULNotOp):
        self._writer.append_value('not ')
        self._writer.append_value('(')
        self._restore_node(op.operand)
        self._writer.append_value(')')

    def _interpret_ULengthOp(self, op: ULengthOP):
        self._writer.append_value('#')
        self._restore_node(op.operand)


class LuaRestoreTree:
    def __init__(self, filepath: str):
        self.file_at = filepath

    def _encoding(self):
        return Cmm.get_file_encoding(self.file_at)

    def _content(self):
        with open(self.file_at, 'r', encoding=self._encoding()) as fp:
            return fp.read()

    def root(self):
        return parse(self._content())

    def parse(self):
        root = self.root()
        return LuaSourceInterpreter(bracket_table_field=True, ).interpret(root)

    def comment(self):
        class BlockComments:
            def __init__(self):
                self.head = []
                self.tail = []

            def clear(self):
                self.head.clear()
                self.tail.clear()

            def to_list(self):
                return self.head + self.tail

        class Visitor(ASTRecursiveVisitor):
            def __init__(self):
                self.current_id = None
                self.all_block_comments = {}
                self.all_plate_comments = []

            def enter_Block(self, node: Block):
                self.current_id = id(node)
                self.all_block_comments[self.current_id] = BlockComments()
                # print('enter Block')

            def exit_Block(self, node: Block):
                block_comment = self.all_block_comments[id(node)]
                self.all_plate_comments.extend(block_comment.to_list())
                self.current_id = None
                # print('exit Block')
                # print(block_comment.to_list())

            def enter_Comment(self, node: Comment):
                block_comment = self.all_block_comments[self.current_id]
                if node.is_tail:
                    block_comment.tail.append(node.s)
                else:
                    block_comment.head.append(node.s)
                # print('enter comment: ', node.is_tail, node.s)

        _visitor = Visitor()
        _visitor.visit(self.root())
        return _visitor.all_plate_comments


if __name__ == '__main__':
    def save_result(content: str):
        with open(r"F:\repo\zqgame\lieyan\client\tool\lua_lexer\test2.lua", 'w', encoding='utf-8') as f:
            f.write(content)


    test_at = r"F:\repo\zqgame\lieyan\client\tool\lua_lexer\test.lua"

    restore = LuaRestoreTree(test_at)

    interpreter = restore.parse()
    text = interpreter.content()
    save_result(text)
    tree = interpreter.tree()
    print('> AST tree:')
    print(tree)
    errors = interpreter.errors()
    if errors is not None:
        print('\n> Errors:')
        print(errors)

    restore.comment()

    # save_result(to_pretty_str(restore.root()))
