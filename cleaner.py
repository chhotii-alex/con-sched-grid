#!/usr/bin/env python3

import re

tagsplit = re.compile(r'(</?[a-zA-Z0-9_-]+[^>]*>)')
tagparts = re.compile(r'<(/?)([a-zA-Z0-9_-]+)([^>]*)>')
replacements = { "<": "&lt;", ">": "&gt;" }

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def tag_parts(tag_str):
    parts = tagparts.fullmatch(tag_str)
    is_close = parts.group(1) == '/'
    attrs = parts.group(3)
    is_empty = not is_close and len(attrs) > 0  and attrs[-1] == '/'
    if is_empty:
        attrs = attrs[:-1]
    tag = parts.group(2)
    return (tag, attrs, is_close, is_empty)

'''
Note that this is severely buggy if an attribute
value contains whitespace. However, I cannot think of any
legitimate reason that an <a> tag would have an attribute
with a value containing whitespace in this context.
'''
def cleanup_anchor_attributes(attrs):
    attrs = attrs.strip()
    attrs = attrs.split()
    dict = {}
    for attr in attrs:
        keyval = attr.split("=", 1)
        if len(keyval) == 1:
            dict[attr] = None
        else:
            dict[keyval[0]] = keyval[1]
    should_target_blank = False
    if 'href' in dict:
        href_val = dict['href'].strip('"')
        if not href_val.startswith('#'):
            should_target_blank = True
    if should_target_blank:
        dict['target'] = '"_blank"'
    result = ''
    for key in dict:
        result += " "
        if dict[key] is None:
            result += key
        else:
            result += "%s=%s" % (key, dict[key])
    return result

def cleanup_tag(tag, attrs, is_close, is_empty):
    close_mark = ''
    if is_close:
        close_mark = '/'
    empty_mark = ''
    if is_empty:
        empty_mark = '/'
    if tag == 'a':
        attrs = cleanup_anchor_attributes(attrs)
    return "<%s%s%s%s>" % (close_mark, tag, attrs, empty_mark)

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
            (tag, attrs, is_close, is_empty) = tag_parts(bit)
            if tag in allowed_tags:
                result += cleanup_tag(tag, attrs, is_close, is_empty)
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

def test_anchor_cleaning(s):
    (new_str, forbidden_tag) = clean_tags(s, ['i', 'a'])
    if 'target="_blank"' not in new_str:
        raise Exception("Failed to add target=_blank")

def test_internal_anchor(s):
    (new_str, forbidden_tag) = clean_tags(s, ['i', 'a'])
    if 'target="_blank"' in new_str:
        raise Exception("Should not add target=_blank to internal anchors")

def run_unit_tests():
    test_anchor_cleaning('this text <a href="https://www.example.com">contains a yummy link</a>okay?')
    test_internal_anchor('trying <a href="#top">internal anchor link</a>')
    test_internal_anchor('this makes <a id="yo"/>an anchor on the page')
    test_string_is_unchanged('before<i>Lord of the Rings</i>after')
    test_string_is_unchanged('testing an empty <i/> tag')
    test_string_is_unchanged('not that an <i floppy="true">italic</i>can have attributes')
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
