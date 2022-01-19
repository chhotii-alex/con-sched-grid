#!/usr/bin/env python3

import re

tagsplit = re.compile(r'(</?[a-zA-Z0-9_-]+[^>]*>)')
tagparts = re.compile(r'<(/?)([a-zA-Z0-9_-]+)([^>]*)>')
replacements = { "<": "&lt;", ">": "&gt;" }

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

'''
Return values: transformed string; whether original string contained forbidden tag
Throws exception if orginal string contains unmatched tags
'''
def clean_tags(s, allowed_tags):
    contains_forbidden_tag = False
    result = ""
    tag_stack = []
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
        else:
            result += replace_all(bit, replacements)
    if len(tag_stack) > 0:
        raise Exception("Unclosed tag in:" + s)
    if contains_forbidden_tag:
        print("Warning: contains a forbidden tag:", s)
    return (result, contains_forbidden_tag)

'''
Unit test functions
'''
def test_string_is_unchanged(s):
    (new_str, forbidden_tag) = clean_tags(s, ['i'])
    if forbidden_tag:
        raise Exception("Falsely claims bad tag")
    if new_str != s:
        raise Exception("Should not have changed string")

def test_contains_and_doesnt(s, include, exclude):
    (new_str, forbidden_tag) = clean_tags(s, ['i'])
    if include not in new_str:
        raise Exception("Transformed string missing something")
    if exclude in new_str:
        raise Exception("Something should have been removed")

def test_throws_exception(s):
    did_throw_exception = False
    try:
        clean_tags(s, ['i'])
    except:
        did_throw_exception = True
    if not did_throw_exception:
        raise Exception("Exception should've occurred")

def test_result_is_empty(s):
    (new_str, forbidden_tag) = clean_tags(s, ['i'])
    new_str = new_str.strip()
    if new_str:
        raise Exception("Result should be empty")

def run_unit_tests():
    test_string_is_unchanged('before<i>Lord of the Rings</i>after')
    test_contains_and_doesnt('blah<meta charset="utf-8" />5 < 8', '&lt;', 'meta')
    test_contains_and_doesnt('before<meta name="viewport" content="width=device-width, initial-scale=1.0" />after', 'after', 'viewport')
    test_contains_and_doesnt('before<link rel="canonical" href="https://docs.python.org/3/library/re.html" />after', 'after', 'https')
    test_contains_and_doesnt('before<input type="checkbox" id="menuToggler" class="toggler__input" aria-controls="navigation" aria-pressed="false" aria-expanded="false" role="button" aria-label="Menu" />after',
                             'before after', 'input')
    test_throws_exception('before<li><a class="reference internal" href="#regular-expression-examples">Regular Expression Examples</a><ul>after')
    test_contains_and_doesnt('before<b>bold stuff<i>inside nested tags</i></b>after', 'before bold', '/b')
    test_contains_and_doesnt('before<li class="nav-item nav-item-1"><a href="index.html" >The Python Standard Library</a> &#187;</li>after', 'before  The', 'li')
    test_throws_exception('before<span class="gp">&gt;&gt;&gt; </span><span class="n">pattern</span><span class="o">.</span><span class="n">search</span><span class="p">(</span><span class="s2">&quot;dog&quot;</span><span class="p">,</span> <span class="mi">1</span><span class="p">)</span>  <span class="c1">after')
    test_contains_and_doesnt('before<script type="text/javascript" src="../_static/switchers.js"></script>after', 'before  after', 'switchers')
    test_contains_and_doesnt('''before
   <style>
      @media only screen {
        table.full-width-table {
            width: 100%;
        }
      }
    </style>
       after''', 'before', 'style')
    test_contains_and_doesnt('''before<script>
            if (6 < 11) {
                 Crasher.crashEntireSystem();
            }
          </script>
       after''', '&lt;', 'script')
    test_result_is_empty("<br/>")

if __name__ == "__main__":
    run_unit_tests()
