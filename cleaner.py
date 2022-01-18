#!/usr/bin/env python3

import re

tagsplit = re.compile(r'(</?[a-zA-Z0-9_-]+[^>]*>)')
tagparts = re.compile(r'<(/?)([a-zA-Z0-9_-]+)([^>]*)>')
replacements = { "<": "&lt;", ">": "&gt;" }

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def test_string_impl(s, allowed_tags):
    contains_forbidden_tag = False
    result = ""
    tag_stack = []
    print(s)
    pieces = tagsplit.split(s)
    for i in range(len(pieces)):
        bit = pieces[i]
        is_tag = i%2
        if is_tag:
            parts = tagparts.fullmatch(bit)
            is_close = parts.group(1) == '/'
            tag = parts.group(2)
            attrs = parts.group(3)
            is_empty = len(attrs) > 0  and attrs[-1] == '/'
            if is_empty:
                attrs = attrs[:-1]
            if tag in allowed_tags:
                result += bit
            else:
                result += " "
                contains_forbidden_tag = True
            if not is_empty:
                if is_close:
                    if len(tag_stack) < 1 or tag_stack[-1] != tag:
                        raise Exception("Text contains unbalanced HTML tags:" + s)
                    else:
                        tag_stack.pop()
                else:
                    tag_stack.append(tag)
            print("tag: %s attrs: %s end? %s empty? %s" % (tag, attrs, is_close, is_empty))
        else:
            result += replace_all(bit, replacements)
    if len(tag_stack) > 0:
        raise Exception("Unclosed tag in:" + s)
    if contains_forbidden_tag:
        print("This string contains a forbidden tag:", s)
    print(result)
    print()

def test_string(s):
    test_string_impl(s, ['i'])

def run_unit_tests():
    test_string('before<i>Lord of the Rings</i>after')
    test_string('blah<meta charset="utf-8" />5 < 8')
    test_string('before<meta name="viewport" content="width=device-width, initial-scale=1.0" />after')
    test_string('before<link rel="canonical" href="https://docs.python.org/3/library/re.html" />after')
    test_string('before<input type="checkbox" id="menuToggler" class="toggler__input" aria-controls="navigation" aria-pressed="false" aria-expanded="false" role="button" aria-label="Menu" />after')
    test_string('before<li><a class="reference internal" href="#regular-expression-examples">Regular Expression Examples</a></li>after')
    test_string('before<b>bold stuff<i>inside nested tags</i></b>after')
    test_string('before<li class="nav-item nav-item-1"><a href="index.html" >The Python Standard Library</a> &#187;</li>after')
    test_string('before<span class="gp">&gt;&gt;&gt; </span><span class="n">pattern</span><span class="o">.</span><span class="n">search</span><span class="p">(</span><span class="s2">&quot;dog&quot;</span><span class="p">,</span> <span class="mi">1</span><span class="p">)</span>  <span class="c1"># No match; search doesn&#39;t include the &quot;d&quot;</span>after')
    test_string('before<script type="text/javascript" src="../_static/switchers.js"></script>after')
    test_string('''before
   <style>
      @media only screen {
        table.full-width-table {
            width: 100%;
        }
      }
    </style>
       after''')
    test_string('''before<script>
            if (6 < 11) {
                 Crasher.crashEntireSystem();
            }
          </script>
       after''')
    test_string("<br/>")

if __name__ == "__main__":
    run_unit_tests()
