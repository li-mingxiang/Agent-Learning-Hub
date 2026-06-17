import ast
import operator


ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float | int:
    """递归计算 AST 节点，只允许白名单里的算术语法。"""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    # 数字字面量是计算的叶子节点，例如 1、3.14。
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    # 二元运算只允许 +、-、*、/，不允许 **、// 等扩展语法。
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_BINARY_OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return ALLOWED_BINARY_OPERATORS[type(node.op)](left, right)

    # 支持一元正负号，例如 -3 或 +5。
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_UNARY_OPERATORS:
        operand = _eval_node(node.operand)
        return ALLOWED_UNARY_OPERATORS[type(node.op)](operand)

    # 任何函数调用、变量名、属性访问都会走到这里，被明确拒绝。
    raise ValueError("only numbers, +, -, *, /, and parentheses are allowed")


def calculator(expression: str) -> str:
    """安全计算基础四则运算表达式，并把结果或错误信息作为字符串返回。"""
    if not isinstance(expression, str) or not expression.strip():
        return "Error: expression cannot be empty."

    try:
        # mode="eval" 只解析单个表达式，不接受多行语句或赋值语句。
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree)
    except ZeroDivisionError:
        return "Error: division by zero."
    except (SyntaxError, ValueError) as exc:
        return f"Error: invalid expression ({exc})."

    return str(result)
