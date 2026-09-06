from wikitextparser import Argument, Template, parse


def test_basics():
    a = Argument('| a = b ')
    assert ' a ' == a.get_name(False)
    assert ' b ' == a.get_value(False)
    assert not a.is_positional(False)
    assert repr(a) == "Argument('| a = b ')"


def test_anonymous_parameter():
    a = Argument('| a ')
    assert '1' == a.get_name(False)
    assert ' a ' == a.get_value(False)


def test_set_name():
    a = Argument('| a = b ')
    a.set_name(' c ', False)
    assert '| c = b ' == a.string
    a.set_name(' c ', True)
    assert '| c = c = b ' == a.string


def test_set_name_at_subspan_boundary():
    a = Argument('|{{ a }}={{ b }}')
    a.set_name(' c ', False)
    assert '| c ={{ b }}' == a.string
    assert '{{ b }}' == a.get_value(False)


def test_set_name_for_positional_args():
    a = Argument('| b ')
    a.set_name(a.get_name(False), False)
    assert '|1= b ' == a.string


def test_value_setter():
    a = Argument('| a = b ')
    a.set_value(' c ', ignore_equals=False)
    assert '| a = c ' == a.string
    a.set_value(' c ', ignore_equals=True)
    assert '| c ' == a.string


def test_removing_last_arg_should_not_effect_the_others():
    a, b, c = Template('{{t|1=v|v|1=v}}').arguments
    del c[:]
    assert '|1=v' == a.string
    assert '|v' == b.string


def test_nowikied_arg():
    a = Argument('|<nowiki>1=3</nowiki>')
    assert a.is_positional(False) is True
    assert '1' == a.get_name(False)
    assert '<nowiki>1=3</nowiki>' == a.get_value(False)


def test_value_after_convertion_of_positional_to_keywordk():
    a = Argument("""|{{{a|{{{b}}}}}}""")
    a.set_name(' 1 ', False)
    assert '{{{a|{{{b}}}}}}' == a.get_value(False)


def test_name_of_positionals():
    assert ['1', '2', '3'] == [
        a.get_name(False) for a in parse('{{t|a|b|c}}').templates[0].arguments
    ]


def test_dont_confuse_subspan_equal_with_keyword_arg_equal():
    p = parse('{{text| {{text|1=first}} | b }}')
    a0, a1 = p.templates[0].arguments
    assert ' {{text|1=first}} ' == a0.get_value(False)
    assert '1' == a0.get_name(False)
    assert ' b ' == a1.get_value(False)
    assert '2' == a1.get_name(False)


def test_setting_positionality():
    a = Argument('|1=v')
    a.make_positional(True)
    assert '|1=v' == a.string
    a.make_positional(False)
    assert '|v' == a.string
    a.make_positional(False)
    assert '|v' == a.string


def test_parser_functions_at_the_end():
    pfs = Argument('| 1 ={{#ifeq:||yes}}').parser_functions
    assert 1 == len(pfs)


def test_section_not_keyword_arg():
    a = Argument('|1=foo\n== section ==\nbar')
    assert (a.get_name(False), a.get_value(False)) == ('1', 'foo\n== section ==\nbar')
    a = Argument('|\n==t==\nx')
    assert (a.get_name(False), a.get_value(False)) == ('1', '\n==t==\nx')
    # Following cases is not treated as a section headings
    a = Argument('|==1==\n')
    assert (a.get_name(False), a.get_value(False)) == ('', '=1==\n')
    # Todo: Prevents forming a template!
    # a = Argument('|\n==1==')
    # assert
    #     (a.name == a.value), ('1', '\n==1==')


def test_argument_name_not_external_link():
    # MediaWiki parses template parameters before external links,
    # so it goes with the named parameter in both cases.
    a = Argument('|[http://example.com?foo=bar]')
    assert (a.get_name(False), a.get_value(False)) == ('[http://example.com?foo', 'bar]')
    a = Argument('|http://example.com?foo=bar')
    assert (a.get_name(False), a.get_value(False)) == ('http://example.com?foo', 'bar')


def test_lists():
    assert Argument('|list=*a\n*b').get_lists()[0].items == ['a', 'b']
    assert Argument('|lst= *a\n*b').get_lists()[0].items == ['a', 'b']
    assert Argument('|*a\n*b').get_lists()[0].items == ['a', 'b']
    # the space at the beginning of a positional argument should not be
    # ignored. (?)
    assert Argument('| *a\n*b').get_lists()[0].items == ['b']


def test_equal_sign_in_val():
    a, c = Template('{{t|a==b|c}}').arguments
    assert a.get_value(False) == '=b'
    assert c.get_name(False) == '1'


def test_tag_with_equal_sign():
    assert Argument('|a<ref name="abc">R</ref>').get_name(False) == '1'


def test_section_heading_with_carriage_return_in_name():
    assert Argument('|a\r== heading ==\rb=c').get_name(False) == 'a\r== heading ==\rb'
