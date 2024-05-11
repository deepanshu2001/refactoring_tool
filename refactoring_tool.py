import ast
import PySimpleGUI as si
import os
from pathlib import Path


si.theme("DarkTeal4")



LONG_METHOD_THRESHOLD=15
LONG_PARAMETER_LIST_THRESHOLD=3
SIMILARITY_THRESHOLD=0.75
class FunctionVisitor(ast.NodeVisitor):
    def __init__(self,content):
        self.content=content
        self.functions=[]
        self.long_methods_list=[]
        self.long_parameterlist=[]
       
    def calculate_lines(self,function_source):
        function_content = []
        for line in function_source:
            
            non_commented_code, *comment_code = line.split("#", 1)
            
            non_commented_code = non_commented_code.strip()
            
            if non_commented_code:
                function_content.append(non_commented_code)
        return function_content

        
    def visit_FunctionDef(self,node):
        function_source=ast.get_source_segment(self.content,node).split("\n")
        function_content=self.calculate_lines(function_source)

        if len(function_content)>LONG_METHOD_THRESHOLD:
            self.long_methods_list.append(node.name)

        count_arguments=len(node.args.args)
        if count_arguments>LONG_PARAMETER_LIST_THRESHOLD:
            self.long_parameterlist.append(node.name)

        del function_content[0]
        
        self.functions.append({
            'name':node.name,
            'content':function_content

        })
        self.generic_visit(node)


def parse_tree(content):
    return ast.parse(content)

def visit_functions(content):
    tree=parse_tree(content)
    visitor=FunctionVisitor(content)
    visitor.visit(tree)
    return visitor
        
def jaccard_similarity(set1, set2):
    # intersection of two sets
    intersection = len(set1.intersection(set2))
    # Unions of two sets
    union = len(set1.union(set2))
     
    return intersection / union


def extract_function(list,content):
    tree=parse_tree(content)
    visitor=FunctionVisitor(content)
    visitor.visit(tree)
    method=[]
    for func in list:
        for node in ast.walk(tree):
            if isinstance(node,ast.FunctionDef):
                if func ==node.name:
                    method.append(ast.get_source_segment(content,node))
    return method

def show_data(code_smell,list,str):
        layout = [
            [si.Text(f"{len(list)} {code_smell} code smell detected")],
            [si.Multiline(str, size=(80, 20), autoscroll=True, no_scrollbar=False)],
            [si.Button("Close",key="Close")]
        ]
        window=si.Window(f"{code_smell} Code Smell Detected",layout,modal=True)
        window.finalize()
        window["Close"].Widget.config(cursor="hand2")
        while True:
            event,values=window.read()
            if event == si.WIN_CLOSED or event == "Close":
                break
        window.close()
def show_window(code_smell):
    layout=[
        [si.Text(f"{code_smell} code smell Not Detected")],
        [si.Push(),si.Button("Close",key="Close"),si.Push()]
    ]
    window=si.Window("No code smell present",layout=layout,modal=True)
    window.finalize()
    window["Close"].Widget.config(cursor="hand2")
    while True:
        event,values=window.read()
        if event == si.WIN_CLOSED or event == "Close":
            break
    window.close()

def nofunction_layout():
    return [
        [si.Text("There is no function present in the file",font=("Times",14,"bold"))],
        [si.Push(),si.Button("OK",key="OK",font=("Arial Bold",10)),si.Push()]
    ]
def nofunction_window():
    window=si.Window("CodeCutter-Refactoring Tool in Python",layout=nofunction_layout(),modal=True,size=(300,140))
    
    window["OK"].Widget.config(cursor="hand2")
    while True:
        event,values=window.read()
        if event == si.WIN_CLOSED or event == "OK":
            break
    
    window.close()

def detect_long_methods(content):
    visitor=visit_functions(content)
    long_methods=visitor.long_methods_list
    long_method_content=[]
    if long_methods:
        long_method_content=extract_function(long_methods,content)
    try:
        func_str="\n\n".join(long_method_content)
        code_smell="Long Method"
        if long_methods:
            
            show_data(code_smell,long_methods,func_str)
            
        else:
            show_window(code_smell)
    except:
        nofunction_window()
        
    
def detect_long_parameterlist(content):
    visitor=visit_functions(content)
    long_parameters=visitor.long_parameterlist
    long_parameter_content=[]
    if long_parameters:
        long_parameter_content=extract_function(long_parameters,content)
    try:
        func_str="\n\n".join(long_parameter_content)
        code_smell="Long Parameter List "
        if long_parameters:
            
            show_data(code_smell,long_parameters,func_str)

        else:
            show_window(code_smell)
    except:
        nofunction_window()


def find_duplicate_functions(functions,visit_functions_,duplicate_func_dict):
    for index,current_function in enumerate(functions):
        if current_function['name'] in visit_functions_:
            continue
        duplicates=set()
        for next_function in functions[index+1:]:
            if next_function['name'] in visit_functions_:
                continue
            
            if jaccard_similarity(set(current_function['content']),set(next_function['content']))>=SIMILARITY_THRESHOLD:
                duplicates.add(next_function['name'])
                visit_functions_.add(next_function['name'])

        if duplicates:
            duplicate_func_dict[current_function['name']]=duplicates
            visit_functions_.add(current_function['name'])
    return duplicate_func_dict

def store_duplicated_code(content):
    visitor=visit_functions(content)
    functions=visitor.functions
    duplicate_func_dict={}
    visit_functions_=set()

    duplicate_func_dict=find_duplicate_functions(functions,visit_functions_,duplicate_func_dict)
    return duplicate_func_dict


def store_duplicate_functions(functions,duplicate_functions):
    for index,current_function in enumerate(functions):
        for next_function in functions[index+1:]:
            if jaccard_similarity(set(current_function['content']),set(next_function['content']))>=SIMILARITY_THRESHOLD:
                duplicate_functions.add(current_function['name'])
                duplicate_functions.add(next_function['name'])
    return duplicate_functions

def detect_duplicate_code(content):
    visitor=visit_functions(content)
    duplicate_functions=set()
    duplicate_functions=store_duplicate_functions(visitor.functions,duplicate_functions)
   
    duplicate_function_content=[]
    if duplicate_functions:
        duplicate_function_content=extract_function(duplicate_functions,content)
    try:
        func_str="\n\n".join(duplicate_function_content)
        
        if duplicate_functions:
            
            show_data("Duplicate Functions",duplicate_function_content,func_str)
        else:
            show_window("Duplicate Functions")
    except:
        nofunction_window()
def refactore_layout():
    return [
        [si.Text("Refactored Code written in refactored.py",font=("Times",14,"bold"))],
        [si.Push(),si.Button("OK",key="OK",font=("Arial Bold",10)),si.Push()]
    ]
def refactore_window():
    window=si.Window("CodeCutter-Refactoring Tool in Python",layout=refactore_layout(),modal=True,size=(400,140))
    window.finalize()
    window["OK"].Widget.config(cursor="hand2")
    while True:
        event,values=window.read()
        if event == si.WIN_CLOSED or event == "OK":
            break
    
    window.close()


def write_content(content):
    new_content="\n\n".join(content)
    filename="refactored.py"
    with open(filename,"w",encoding='utf-8') as f:
        f.write(new_content)
    
    refactore_window()


def walk_tree(tree,duplicate_function,duplicate_func_dict):
    file_content=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef):
            if node.name not in duplicate_function:
                file_content.append(ast.get_source_segment(content,node))
            else:
                if node.name in duplicate_func_dict:
                    file_content.append(ast.get_source_segment(content,node))
                    del duplicate_func_dict[node.name]

    return file_content

def refactor_duplicated_code(content):
    duplicate_func_dict=store_duplicated_code(content)
    duplicate_function=set()
    
    for dict_vals in duplicate_func_dict.values():
        duplicate_function.update(dict_vals)
    tree=parse_tree(content)
    visitor=FunctionVisitor(content)
    visitor.visit(tree)
    file_content=[]
    file_content=walk_tree(tree,duplicate_function,duplicate_func_dict)
    
    
    write_content(file_content)
    
    
def custom_layout():
    return [
        [si.Text("Select what would you like to do?",font=("Heveltica Bold",14))],
        [si.Text("Detect Long Method Code Smell",font=("Times",10,"bold")),si.Push(),si.Button("Yes",key='option-1',font=("Arial Bold",10))],
        [si.Text("")],
        [si.Text("Detect Long Parameter List Code Smell",font=("Times",10,"bold")),si.Push(),si.Button("Yes",key='option-2',font=("Arial Bold",10))],
        [si.Text("")],
        [si.Text("Detect whether Duplicate code exists?",font=("Times",10,"bold")),si.Push(),si.Button("Yes",key='option-3',font=("Arial Bold",10))],
        [si.Text("")],
        [si.Text("Refactor duplicate Code",font=("Times",10,"bold")),si.Push(),si.Button("Yes",key='option-4',font=("Arial Bold",10))],
        [si.Text("")],
        [si.Push(),si.Button("Close",key='option-5',font=("Arial Bold",10)),si.Push()]
    ]
def set_cursor(window):
    window["option-1"].Widget.config(cursor="hand2")
    window["option-2"].Widget.config(cursor="hand2")
    window["option-3"].Widget.config(cursor="hand2")
    window["option-4"].Widget.config(cursor="hand2")
    window["option-5"].Widget.config(cursor="hand2")

def choose_options(window):
    while True:
        event,values=window.read()
        if event==si.WIN_CLOSED:
            break
        elif event=='option-1':
            detect_long_methods(content)

        elif event=='option-2':
            detect_long_parameterlist(content)

        elif event=='option-3':
            detect_duplicate_code(content)
        elif event=='option-4':
            refactor_duplicated_code(content)
        elif event=='option-5':
            window.close()


def read_content(content):
    
    window=si.Window("CodeCutter-Refactoring Tool in Python",layout=custom_layout(),modal=True,size=(400,340))
    window.finalize()
    set_cursor(window)
    choose_options(window)
    
        
    
def file_layout():
    return [
    [si.Text("")],
    [si.Text("Choose a Python File",font=("Times",14,"bold"))],
    [si.In(size=(50,50),key="Input_field"),si.FileBrowse(font=("Arial Bold",10),key="Browse",enable_events='true')],
    [si.Text("")],
    [si.Push(),si.Button("Submit",key="Submit",font=("Arial Bold",10)),si.Push(),si.Button("Cancel",key='Cancel',font=("Arial Bold",10)),si.Push()]
    
    ]


window = si.Window("CodeCutter-Refactoring Tool in Python", layout=file_layout(),size=(500,200),margins=(10,10))
window.Finalize()
window["Submit"].Widget.config(cursor="hand2")
window["Browse"].Widget.config(cursor="hand2")
window["Cancel"].Widget.config(cursor="hand2")

def file_layout():
    return [
        [si.Text("Please choose a python file",font=("Arial Bold",10))],
        [si.Push(),si.Button("OK",key="OK"),si.Push()]
    ]

def file_window():
    window=si.Window("CodeCutter-Refactoring Tool in Python",layout=file_layout(),modal=True,size=(300,100))
    window.finalize()
    
    while True:
        event,values=window.read()
        if event == si.WIN_CLOSED or event == "OK":
            break
    
    window.close()

while True:
    event, values = window.read()
    if event==si.WIN_CLOSED or event=='Cancel':
        break
    elif event=='Submit' and values['Input_field']=='':
        file_window()
    elif event=='Submit':
        file_name=values['Input_field']
        if Path(file_name).is_file():
            file=open(values['Input_field'],"r",encoding='utf-8')
            file_path, file_extension = os.path.splitext(file_name)
            if(file_extension!='.py'):
                file_window()
                window['Input_field'].update('')
            else:
                content=file.read()
                read_content(content) 
            

window.close()