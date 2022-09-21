from typing import List, Optional

from luaparser.ast import ASTRecursiveVisitor, parse, SyntaxException, to_lua_source
from luaparser.astnodes import Block

from cmm import Cmm


def block_statements(node: Block):
    return '  '.join([statement.__class__.__name__ for statement in node.body])


class WrapBlock:
    def __init__(self, node: Block, parent: Optional[Block], level):
        self.node = node
        self.parent = parent
        self.level = level

    def info(self):
        d = {"level": self.level, "node": id(self.node)}
        if self.parent is not None:
            d.setdefault("parent", id(self.parent))
        return d

    def source(self):
        return ['<b>[嵌套层级 {}]</b>'.format(self.level), to_lua_source(self.node), '\n']


class NestedVisitor(ASTRecursiveVisitor):

    def __init__(self, max_nested: int = 5):
        super(NestedVisitor, self).__init__()

        self.cur_level = 0
        self.max_level = 0
        self.max_nested = max_nested
        self.block_all = dict()
        self.block_chain: List[Block] = []
        self.block_in_levels: List[List[WrapBlock]] = []

    def add_block(self, node: Block):
        at = len(self.block_chain) - 1
        last_node = None
        if at >= 0:
            last_node = self.block_chain[at]
        self.block_chain.append(node)
        self.block_all.setdefault(id(node), node)

        block = WrapBlock(node, last_node, self.cur_level)
        length = len(self.block_in_levels)
        if self.cur_level >= length:
            blocks = []
            self.block_in_levels.append(blocks)
        else:
            blocks = self.block_in_levels[self.cur_level]
        blocks.append(block)

    def enter_Block(self, node: Block):
        self.add_block(node)
        self.cur_level += 1

    def exit_Block(self, _: Block):
        self.cur_level -= 1
        self.block_chain.pop()

    def tree(self):
        tree = []
        for blocks in self.block_in_levels:
            for block in blocks:
                tree.append(block)
        return tree


class LuaSyntaxChecker:
    @staticmethod
    def check_by_source(src: str):
        try:
            tree = parse(src)
            return True, tree
        except (SyntaxException, Exception) as e:
            print({"msg": str(e), "type": e.__class__.__name__})
            return False

    @staticmethod
    def check_by_file(filepath: str):
        try:
            encoding = Cmm.get_file_encoding(filepath)
            with open(filepath, 'r', encoding=encoding) as f:
                return LuaSyntaxChecker.check_by_source(f.read())
        except (OSError, SyntaxException, UnicodeDecodeError, Exception) as e:
            print(e)
            return False

    @staticmethod
    def check_nested(filepath):
        try:
            syntax_ok, syntax_tree = LuaSyntaxChecker.check_by_file(filepath)
            if syntax_ok is True and syntax_tree is not None:
                visitor = NestedVisitor()
                visitor.visit(syntax_tree)
                return True, visitor.block_in_levels
            return syntax_ok, None
        except (SyntaxException, UnicodeDecodeError, Exception) as e:
            print(e)
            return False, None

# if __name__ == '__main__':
#     file_path = r'F:\repo\zqgame\lieyan\client\tool\lua_lexer\test.lua'
#     syntax_ok = LuaSyntaxChecker.check_by_file(file_path)
#     print('syntax: ', 'good' if syntax_ok else 'bad')
#     check_file_nested_level(file_path)
