import os
import sys
import importlib.util
import re

def remove_comment(line):
    """Removes // comments only if they are not inside quotes."""
    in_quotes = False
    quote_char = ''
    for i, char in enumerate(line):
        if char in ('"', "'"):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
        elif char == '/' and i + 1 < len(line) and line[i+1] == '/' and not in_quotes:
            return line[:i]
    return line


def split_arguments(arg_string):
    """Splits arguments by comma while respecting quotes and nested parentheses."""
    args = []
    current = []
    in_quotes = False
    quote_char = ''
    paren_depth = 0

    for char in arg_string:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current.append(char)
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = ''
            current.append(char)
        elif char == '(' and not in_quotes:
            paren_depth += 1
            current.append(char)
        elif char == ')' and not in_quotes:
            paren_depth -= 1
            current.append(char)
        elif char == ',' and not in_quotes and paren_depth == 0:
            args.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if current:
        args.append("".join(current).strip())

    return [a for a in args if a]


def parse_code(code):
    lines = code.strip().splitlines()
    ast, _ = parse_block(lines, 0)
    return ast


def parse_block(lines, start_idx):
    ast = []
    i = start_idx

    while i < len(lines):
        line = remove_comment(lines[i].rstrip())
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "}":
            i += 1
            return ast, i

        # Imports
        if stripped.startswith("load "):
            module_name = stripped.replace("load ", "").replace(";", "").strip()
            ast.append({"type": "import", "module": module_name})
            i += 1
        
        # Variable declarations (int, float, str, bool)
        elif any(stripped.startswith(t + " ") for t in ["int", "float", "str", "bool"]):
            parts = stripped.replace(";", "").split("=", 1)
            header = parts[0].strip().split()
            var_type = header[0]
            var_name = header[1]
            var_value = parts[1].strip()
            ast.append({
                "type": "var_decl",
                "var_type": var_type,
                "name": var_name,
                "value": var_value
            })
            i += 1

        # While loop
        elif stripped.startswith("while"):
            cond_start = stripped.find("(")
            cond_end = stripped.rfind(")")
            condition = stripped[cond_start+1:cond_end].strip()
            
            i += 1
            while i < len(lines) and "{" not in lines[i]:
                i += 1
            if i < len(lines):
                i += 1
            
            body, i = parse_block(lines, i)
            ast.append({
                "type": "while_loop",
                "condition": condition,
                "body": body
            })

        # If statement
        elif stripped.startswith("if"):
            cond_start = stripped.find("(")
            cond_end = stripped.rfind(")")
            condition = stripped[cond_start+1:cond_end].strip()

            i += 1
            while i < len(lines) and "{" not in lines[i]:
                i += 1
            if i < len(lines):
                i += 1
            
            body, i = parse_block(lines, i)
            
            branches = [{"condition": condition, "body": body}]
            else_body = None

            while i < len(lines):
                next_stripped = remove_comment(lines[i]).strip()
                if next_stripped.startswith("elif"):
                    cond_start = next_stripped.find("(")
                    cond_end = next_stripped.rfind(")")
                    elif_cond = next_stripped[cond_start+1:cond_end].strip()
                    i += 1
                    while i < len(lines) and "{" not in lines[i]:
                        i += 1
                    if i < len(lines):
                        i += 1
                    elif_body, i = parse_block(lines, i)
                    branches.append({"condition": elif_cond, "body": elif_body})
                elif next_stripped.startswith("else"):
                    i += 1
                    while i < len(lines) and "{" not in lines[i]:
                        i += 1
                    if i < len(lines):
                        i += 1
                    else_body, i = parse_block(lines, i)
                    break
                else:
                    break

            ast.append({
                "type": "if_statement",
                "branches": branches,
                "else_body": else_body
            })

        # Function calls
        elif "(" in stripped:
            clean_line = stripped.rstrip(";")
            func_name = clean_line.split("(")[0].strip()
            raw_args = clean_line[clean_line.find("(")+1 : clean_line.rfind(")")]
            args = split_arguments(raw_args)
            
            ast.append({
                "type": "func_call",
                "func": func_name,
                "args": args
            })
            i += 1
        else:
            i += 1

    return ast, i


def evaluate_expression(expr_str, variables, loaded_modules, modules_dir):
    """Evaluates mathematical, logical, or string expressions."""
    expr_str = expr_str.strip()
    
    def replace_str_syntax(match):
        v_name = match.group(1)
        val = variables.get(v_name, "")
        return repr(str(val))
    
    clean_expr = re.sub(r'str\{([^}]+)\}', replace_str_syntax, expr_str)
    
    try:
        return eval(clean_expr, {"__builtins__": {}}, variables)
    except Exception:
        return evaluate_arg(expr_str, variables, loaded_modules, modules_dir)


def evaluate_arg(arg, variables, loaded_modules, modules_dir):
    """Helper to resolve variable values, constants, or nested functions."""
    arg = arg.strip()

    if "(" in arg and arg.endswith(")"):
        func_name = arg.split("(")[0].strip()
        raw_args = arg[arg.find("(")+1 : arg.rfind(")")]
        args = split_arguments(raw_args)
        return execute_function_call(func_name, args, variables, loaded_modules, modules_dir)

    elif arg.startswith("str{") and arg.endswith("}"):
        var_inside = arg[4:-1]
        return str(variables.get(var_inside, ""))
    elif arg in variables:
        return variables[arg]
    elif (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
        return arg[1:-1]
    elif arg.isdigit():
        return int(arg)
    
    return evaluate_expression(arg, variables, loaded_modules, modules_dir)


def execute_function_call(func_name, raw_args, variables, loaded_modules, modules_dir):
    """Executes a function call dynamically from imported modules."""
    evaluated_args = [evaluate_arg(a, variables, loaded_modules, modules_dir) for a in raw_args]

    if func_name in ["print", "print_"]:
        print(*(str(a) for a in evaluated_args))
        return None

    if "." in func_name:
        mod_name, func_method = func_name.split(".", 1)
        if mod_name in loaded_modules:
            module_obj = loaded_modules[mod_name]
            if hasattr(module_obj, func_method):
                func = getattr(module_obj, func_method)
                return func(*evaluated_args)
            else:
                print(f"Error: Function '{func_method}' not found in module '{mod_name}'")
        else:
            print(f"Error: Module '{mod_name}' is not loaded.")
    else:
        print(f"Error: Unknown function '{func_name}'")
    return None


def execute_ast(ast, variables=None, loaded_modules=None, modules_dir=None):
    """Executes the abstract syntax tree."""
    if variables is None:
        variables = {}
    if loaded_modules is None:
        loaded_modules = {}

    if modules_dir is None:
        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        modules_dir = os.path.join(current_dir, "modules")

    for node in ast:
        if node["type"] == "import":
            module_name = node["module"]
            py_file = os.path.join(modules_dir, f"{module_name}.py")

            if os.path.exists(py_file):
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                loaded_modules[module_name] = mod
            else:
                print(f'Error: Module "{module_name}" not found in "{modules_dir}"')

        elif node["type"] == "var_decl":
            val_str = node["value"]
            evaluated_val = evaluate_arg(val_str, variables, loaded_modules, modules_dir)
    
            if node["var_type"] == "int":
                variables[node["name"]] = int(evaluated_val)
            elif node["var_type"] == "float":
                variables[node["name"]] = float(evaluated_val)
            elif node["var_type"] == "bool":
                if isinstance(evaluated_val, str):
                    variables[node["name"]] = evaluated_val.strip().lower() in ("true", "1", "yes")
                else:
                    variables[node["name"]] = bool(evaluated_val)
            elif node["var_type"] == "str":
                variables[node["name"]] = str(evaluated_val)

        elif node["type"] == "func_call":
            execute_function_call(node["func"], node["args"], variables, loaded_modules, modules_dir)

        elif node["type"] == "if_statement":
            executed = False
            for branch in node["branches"]:
                cond_val = evaluate_expression(branch["condition"], variables, loaded_modules, modules_dir)
                if cond_val:
                    execute_ast(branch["body"], variables, loaded_modules, modules_dir)
                    executed = True
                    break
            if not executed and node["else_body"] is not None:
                execute_ast(node["else_body"], variables, loaded_modules, modules_dir)

        elif node["type"] == "while_loop":
            while True:
                cond_val = evaluate_expression(node["condition"], variables, loaded_modules, modules_dir)
                if not cond_val:
                    break
                execute_ast(node["body"], variables, loaded_modules, modules_dir)

    return variables