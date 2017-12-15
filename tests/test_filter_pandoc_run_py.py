import os
import json
# from filter_pandoc_run_py import *
from filter_pandoc_run_py import *
from subprocess import call

dir_path = os.path.dirname(os.path.realpath(__file__))

"""

	Pandoc convert using the filter from markdown to html:
	pandoc ./test.md -F ../filter_pandoc_run_py/filter_pandoc_run_py.py  --to html -s -o ./tests//test.html

	Pandoc convert using the filter from markdown to markdown:
	! pandoc ./tests/test.md --to markdown -F ./filter_pandoc_run_py/filter_pandoc_run_py.py -o ./tests/test_conv.md

	Generate the intermediary json ast file:
	! pandoc ./tests/test.md -t json -o ./tests/test.json
"""

#--------------------------------------------
# 	 Low Level tests 	 
#--------------------------------------------

def test_run_pandoc_process():

	text = 'I am a **mark** *down*'
	ret = run_pandoc(text)
	d = json.loads(ret)
	assert d[1][0]['c'][6]['t'] == 'Strong'

	ret = run_pandoc(text, ['--from=markdown', '--to=html'])
	ret = ret.replace('\r', '')
	assert ret == '<p>I am a <strong>mark</strong> <em>down</em></p>\n'

	text = 'Oi sou um **mark** *down* \n\n New Line!'
	ret = run_pandoc(text)
	d = json.loads(ret)
	assert d[1][0]['c'][-1]['t'] == 'Emph'

def test_json_ast_reader():
	'''
	Json generated as: pandoc test.md -t json -o test.json
	'''
	dt = read_json(os.path.join(dir_path, 'test.json'))
	assert isinstance(dt, (dict, list))

	dt = read_json(os.path.join(dir_path, 'test.json'), 'string')
	assert isinstance(dt, (str))

def test_stdout_redirection():
	code = """
i = [0,1,2]
for j in i :
    print(j)
"""
	with stdoutIO() as s:
		exec(code)

	print("out:", s.getvalue())
	assert s.getvalue() == '0\n1\n2\n'
	pass

#--------------------------------------------
# 	 Testing code Samples run and Print
#--------------------------------------------

def test_md_sample_regular_code():
	MD_SAMPLE = '''
```{.python }
e = 'foo'
```
'''
	ast_string = run_pandoc(MD_SAMPLE)
	processed = applyJSONFilters([run_py_code_block], ast_string)
	d = json.loads(processed)
	assert d[1][0]['c'][1] == "e = 'foo'"


def test_md_sample_runnable():
	MD_SAMPLE = '''
```{.python .run}
d = 1e3
```
'''
	ast_string = run_pandoc(MD_SAMPLE)
	processed = applyJSONFilters([run_py_code_block], ast_string)
	d = json.loads(processed)
	assert d[1][0]['c'][1] == 'd = 1e3'

def test_md_sample_run_inline():
	MD_SAMPLE = '''
Water density is `foo = 1`{.run}.
'''
	ast_string = run_pandoc(MD_SAMPLE)
	processed = applyJSONFilters([run_py_code_block], ast_string)
	d = json.loads(processed)
	assert d[1][0]['c'][6]['t'] == 'Code'

def test_md_sample_print():
	MD_SAMPLE = '''
```{.python .run}
print('A={}'.format(2.0))
```
'''
	ast_string = run_pandoc(MD_SAMPLE)
	processed = applyJSONFilters([run_py_code_block], ast_string)
	d = json.loads(processed)
	assert d[1][1]['c'][1]['t'] == 'BlockQuote'

def test_md_sample_print_text():
	MD_SAMPLE = '''
```{.python .run format=text}
print('A={}'.format(2.0))
```
'''
	ast_string = run_pandoc(MD_SAMPLE)
	processed = applyJSONFilters([run_py_code_block], ast_string)
	d = json.loads(processed)
	assert d[1][1]['t'] == 'Para'
	pass

def test_md_sample_print_hiding():
	MD_SAMPLE = '''
```{.python .run hide_code=True}
print('A={}'.format(2.0))
```
'''
	ast_string = run_pandoc(MD_SAMPLE)
	processed = applyJSONFilters([run_py_code_block], ast_string)
	d = json.loads(processed)
	assert d[1][0]['c'][1]['t'] == 'BlockQuote'
	pass


def test_md_sample_print_inline():
	MD_SAMPLE = '''
`print('Hi')`{.run}.
'''
	ast_string = run_pandoc(MD_SAMPLE)
	processed = applyJSONFilters([run_py_code_block], ast_string)
	d = json.loads(processed)
	assert d[1][0]['t'] == 'Para'
	pass

#--------------------------------------------
# 	 Testing Inline Image to document 	 
#--------------------------------------------

def test_inline_plot():
	MD_SAMPLE = '''
```{.python .run caption="cap1" label="lbl1"}
import matplotlib
matplotlib.use('AGG')
from matplotlib import pyplot as plt
plt.plot([1, 2], [3, 4], 'dr-')
```
'''
	ast_string = run_pandoc(MD_SAMPLE)
	processed = applyJSONFilters([run_py_code_block], ast_string)
	d = json.loads(processed)
	assert d[1][1]['c'][0]['t'] == 'Image'


#--------------------------------------------
# 	 Testing Full Convertion 	 
#--------------------------------------------

def test_run_pandoc_like():
	"""
	Requires test.json in the file directory.
	It is generated from test.md as:
	pandoc test.md --to json -o test.json
	"""
	call(['pandoc', os.path.join(dir_path, 'test.md'), '--to',
            'json', '-o', os.path.join(dir_path, 'test.json')])
	dt = read_json(os.path.join(dir_path, 'test.json'), 'string')
	applyJSONFilters([run_py_code_block], dt)

############################################
###########################################
#
#
# 	 Regular Debugger Start
#
#
###########################################
###########################################
def insider_Debugger():
	test_run_pandoc_like()
	pass

if __name__ == '__main__':
	insider_Debugger()
	pass
