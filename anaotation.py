import json
from dotenv import load_dotenv
import os
import json
import pandas as pd
import re
from bs4 import BeautifulSoup as BS
from bs4 import NavigableString
from nltk import Tree
import stanza
from stanza.models.common.doc import Document
# from PIL import ImageFont
import math
import logging


load_dotenv()
# to ignore the message besides warnings
logging.getLogger('stanza').setLevel(logging.WARNING)
report_path = os.getenv('SOURCE')
with open(report_path,'r') as file:
    report = json.load(file)

document = report.get('document')
annotation = []
var_counter = 0
formula_counter = 0
anno_counter = 0
end = report.get('tokens')[-1]['end-ref']

#with patterns to find declarations for the math node
#declarations are in spotted concepts
# TODO: opacity -> opacities
# TODO: L-function(where L is labeled as a mathnode)
# TODO: there could be some words like 'here', 'hencefor' √
# Problems: constant can be a qualifier or a declaration
declaration_set = {'optical depth', 'baryonic mass', 'energy', 'opacity', 'temperature', 'thermal energy','vector', 'relativistic expansion', 'lorenz factor','waveform','operator', 
                   'number','sigular value', 'eigenvalue','constant','measure','mapping','map','inner product','index set','Hilbert space', 'frame','cusp form','Brownian motion',
                   'integer','group','variable','probability density function','divisor function','density function','function','arithmetic function','variance','mean', 'expectation',
                   'matrix','coefficient','sequence'}
qualifiers = ['positive', 'negative','universal','usual','global','initial','natural','real','complex','irrational','imaginary','aperiodic','periodic','finite','infinite','bounded', 
              'discrete', 'continuous', 'random','identical','random','characteristic','a sequence of',
              'Hecke','Fourier','unspecified','real', '-', 'valued','non','decreasing','increasing','distinct','automorphic','normalized','unimodular', 'stochastic','identically distributed',
              '(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|\\d+)','dimensional','minimum','maximum']
# Pattern of math declarations to be matched
Concept = '(\b' + '|'.join(re.escape(concept) + '(s|es)?' for concept in declaration_set) + '\b)'
qualifiers_pattern = '((?:\b' + '|'.join(qualifiers) + '\b)\s*)*'

# Words that does not effect the meaning of declaration
ignored_words = ['here', 'there', 'henceforth','hence','therefore','respectively','also']

# group all tokens with . as an endpoint
def get_end_point(report):
    #sentence seperator
    global end 
    SentenceBlock = []
    start_point = 1
    point_pos = 1
    end_point = end
    token_list = report.get('tokens')
    for i, token_block in enumerate(token_list):
        if len(token_list) - i > 1:
            
            if token_block.get('token') == '.':
                if i + 2 < len(token_list):
                    # to solve problem: i.e...
                    if token_list[i+2].get('token') == '.' or token_block.get('start-ref') - point_pos <= 3:
                        point_pos = token_block.get('end-ref')
                    else:
                        SentenceBlock.append([start_point,token_block.get('start-ref')])
                        start_point = token_block.get('end-ref')
            elif token_block.get('token') == '!' or token_block.get('token') == '?' or token_block.get('token') == 'MathEquation':
                SentenceBlock.append([start_point,token_block.get('start-ref')])
                start_point = token_block.get('end-ref')
            # prevent the '.' is written inside the math node
            elif token_block.get('token') == 'MathNode' and token_list[i+1].get('token')[0].isupper() and token_list[i+1].get('token') != 'MathNode':
                SentenceBlock.append([start_point,token_block.get('end-ref')])
                start_point = token_block.get('end-ref')
        # in case the last sentence does not have a end sign
        else:
            if token_block.get('token') == '.' or token_block.get('token') == '!' or token_block.get('token') == '?' or token_block.get('token') == 'MathEquation':
                SentenceBlock.append([start_point,token_list[i-1].get('end-ref')])
            else:
                SentenceBlock.append([start_point, token_block.get('end-ref')])
    # 
    # if not SentenceBlock or SentenceBlock[-1][1] != end_point -1:
    #     SentenceBlock.append([start_point,end_point])

    return SentenceBlock


#add an 'id' to the math node
#see if it is a parameter or a formula

def equation_form(node, declaration):
    global formula_counter
    global anno_counter
    global annotation
    id_formula = document +'#FormulaTag.target.' + str(formula_counter)
    formula_counter += 1
    formula = {
            'type': 'FragmentTarget',
            'id': id_formula,
            'source': document,
            'selector':
                [
                    {
                    'type': 'OffsetSelector',
                    'start': node['start-ref'],
                    'end':node['end-ref']
                    # 'replaced-node':node.get('replaced-node'),
                    }
                ]
        }
    annotation.append(formula)
    id_annotation = document + '#FormulaTag.anno.' + str(anno_counter)
    annotat = {
        'type': 'Annotation',
        'id': id_annotation,
        'target': id_formula,
        'body': {
          'type': 'SimpleTagBody',
          'val': declaration
        },
        'creator':''
    }
    anno_counter += 1
    annotation.append(annotat)

# #Since the locations of letters are represented by pixels, so extract the corresponding pixels the target has
# def length_calculate(w_string,s_string,length):
#     font = ImageFont.load_default()
#     total = font.getlength(w_string)
#     taget_len = font.getlength(s_string)
#     width = length * (taget_len/total)
#     return int(width)

#TODO:  'f: R->R', 'A:R'
def parameter_form(node,declaration):
    global var_counter
    global annotation
    global anno_counter
    id_para = document +'#VariableTag.target.' + str(var_counter)
    var_counter += 1
    new_node = parameter_seperation(node)
    start = new_node['start-ref']
    end = new_node['end-ref']
    print(new_node)
    variable = {
        'type': 'FragmentTarget',
        'id': id_para,
        'source': document,
        'selector':
            [
                {
                'type': 'OffsetSelector',
                'start': start,
                'end': end,
                # 'symbol':new_node['symbol']
               # 'replaced-node':node.get('replaced-node'),
            }
            ]
        
    }
    annotation.append(variable)
    id_annotation = document + '#VariableTag.anno.' + str(anno_counter)
    annotat = {
        'type': 'Annotation',
        'id': id_annotation,
        'target': id_para,
        'body': {
          'type': 'SimpleTagBody',
          'val': declaration
        },
        'creator':''
    }
    anno_counter += 1
    annotation.append(annotat)


def parameter_seperation(node):
    symbol_refs = ''
    symbols_with_refs = []
    soup = BS(node["replaced-node"], 'html.parser')
    inside_semantics = soup.find('semantics')
    symbol_start_ref = node["start-ref"]
    symbol_end_ref = node['end-ref']
    total = len(node["replaced-node"])
    ref_span = (node['end-ref'] - node['start-ref'])/total 
    for child in inside_semantics:
        if child.name and is_not_annotation(child):
            
            # Iterate over each math symbol tag
            for symbol in child.contents:
                if symbol.name == 'mrow':
                    for s in symbol.contents:
                        if not isinstance(s, NavigableString):
                            symbol_id = s.get('id')
                            symbol_text = s.get_text()
                            if symbol_id:
                                if symbol_text == ':':
                                    symbol_end_ref = symbol_start_ref
                                    break
                                else:
                                    symbol_refs += symbol_text
                                    symbol_start_ref += (ref_span * len(str(s)))
                else:
                    if not isinstance(symbol, NavigableString): 
                        symbol_id = symbol.get('id')
                        symbol_text = symbol.get_text()
                        if symbol_id:
                            if symbol_text == ':':
                                symbol_end_ref = symbol_start_ref
                                break
                            else:
                                symbol_refs += symbol_text
                                symbol_start_ref += (ref_span * len(str(symbol)))
            # width = length_calculate(soup.text, symbol_refs, ref_span)
            # symbol_end_ref = node['start-ref'] + width
            symbols_with_refs ={
            "token": "MathNode",
            "start-ref": node['start-ref'],
            "end-ref": math.ceil(symbol_end_ref) + 1,# the empty space seems to be belonged to the representation
            "symbol": symbol_refs
        }
    return symbols_with_refs
    


def clean_surrogate_pairs(text):
    return text.encode('utf-16', 'surrogatepass').decode('utf-16', 'ignore')


#only need the content of html of math representation
def is_not_annotation(tag):
    return tag.name not in ['annotation', 'annotation-xml']
symbol1 = ['≠','≈','≥','≤','<','>', '=']
symbol2 = ['+','−','∓','±','-']


#check if they are only digits 
def only_numbers(target):
    pattern = r'\b\d+(\.\d+)?\b|\b\d+\.'
    matches = re.match(pattern, target)
    return bool(matches)


#check if there are only digits left
def only_digital_left(tagset,symbol):
    left = []
    text = ''
    for tag in tagset:
        concated_str = ''.join(str(tag))
        new_soup = BS(concated_str,'html.parser')
        left += new_soup.find_all(lambda t: t.get_text() not in symbol)
    for i in left:
        text += i.text
    return only_numbers(text)


#find if the mathnode is only a number, equation or parameter 
def number_identifier(node):
    soup = BS(node, 'html.parser')
    if_only_number = False
    if_parameter = False
    if_equation = False
    inside_semantics = soup.find('semantics')

    if inside_semantics:
        for child in inside_semantics:
            if child.name and is_not_annotation(child):
                if_approximate = child.find(lambda t: t.name == 'mo' and (t.text =='≈' or t.text == '≤' or t.text == '≥' or t.text == '>' or t.text == '<'))
                minus_plus = child.find(lambda t: t.name == 'mo' and (t.text == '∓' or t.text == '±' or t.text == '+' or t.text == '-' or t.text == '−'))
                if only_numbers(child.text):
                    if_only_number = True
                # elif 'mrow' not in child.name and 'mfrac' not in child.name and 'msub' not in child.name:
                #     print('continue')
                elif if_approximate:
                    before_sign = if_approximate.find_previous_siblings()
                    text_before = ''
                    for i in before_sign:
                        text_before += i.text
                    if not text_before:
                        if only_digital_left(if_approximate.find_next_siblings(),symbol=symbol1+symbol2):
                            if_only_number = True
                            print('onöy number')
                        else:
                            if_parameter = True
                    else:
                        sign = BS(str(if_approximate),'html.parser')
                        left_tags = child.find_all(lambda t: not( t.name == sign.name and t.get_text() == sign.text()))
                        if only_digital_left(left_tags,symbol=symbol1+symbol2):
                            if_only_number = True
                        else:
                            if_equation = True
                elif minus_plus:
                    sign = BS(str(minus_plus),'html.parser')
                    other_tags = child.find_all(lambda t: not( t.name == sign.name and t.get_text() == sign.text()))
                    left_html = BS(str(other_tags), 'html.parser')
                    if_compare = left_html.find(lambda t: t.text in symbol1)
                    if only_digital_left(other_tags, symbol=symbol2+symbol1):
                        if_only_number = True
                    elif if_compare:
                        if_equation = True
                    else:
                        if_parameter = True
                else:
                    if_parameter = True
    return if_equation, if_only_number, if_parameter

# avoiding the same node which can be matched with different patterns
def check_node_exists(start, end):
    global annotation
    for item in annotation:
        if item['type'] == 'FragmentTarget':
            selector = item.get('selector')
            # it could counts the space or not
            if any(abs(sel.get('start') - start) <= 1 and abs(sel.get('end') - end) <= 1 for sel in selector):
                return True
    return False                    

sentence_sign = ['SINV','S','SQ','SBAR','SBARQ']
phrase_set = ['NP', 'PP', 'VP','WHNP','NNP','VNP']
con_words = ['IT','IN','CC','DT',',']
# To make sure there are no more clauses
def parallel_seperator(tree, if_sepsent = False):
    new_tree_before = Tree(tree.label(),[])
    new_tree_after = Tree(tree.label(),[])
    sub_sent = Tree('ROOT', [])
    list = []
    if tree.label() == 'ROOT':
        tree = tree[0]
    for child in tree:
        # go through all subtree nodes to see if there is a node for sentence
        if isinstance(child, Tree):
            if child.label() in s:
                sub_sent = child
                list.append(sub_sent)
                if_sepsent = True
                print('it has different sentences')
            else:
                rebuilt_tree_before, rebuilt_tree_after, lis, if_sepsent = parallel_seperator(child, if_sepsent)
                if list:
                    if rebuilt_tree_after:
                        list.append(rebuilt_tree_after)
                else:
                    new_tree_after.append(rebuilt_tree_after)
                list.extend(lis)
                if rebuilt_tree_before:   
                    new_tree_before.append(rebuilt_tree_before)
                
        else:
            if if_sepsent:
                new_tree_after.append(child)
            else:
                new_tree_before.append(child)


    return new_tree_before, new_tree_after, list, if_sepsent
# to see the structure of the sentence
def extract_subtree(tree, subtree_list):
    
    if tree.label() == 'ROOT':
        tree = tree[0]
    for subtree in tree: 
        if subtree.label() in sentence_sign:
            extract_subtree(subtree,subtree_list)
        elif subtree.label() == 'VP':
            extract_subtree(subtree,subtree_list)
        else:
            subtree_list.append(subtree)
    if subtree_list:
        return subtree_list
    else:
        return tree

# constituency parse the sentence 
def constituency(text):
    # Tokenization without Sentence Segmentation, because stanza will see short terms as a sentence
    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency',tokenize_no_ssplit=True)
    doc = nlp(text)
    for sentence in doc.sentences:
        tree = sentence.constituency
        nltk_tree = Tree.fromstring(str(tree))
    return nltk_tree
# To let the parsed concept to be more precise
def check_more_precise(tree, concept):
    if tree.label() in phrase_set + sentence_sign:
        befor_sub, after_sub, l, if_subsent = parallel_seperator(tree)
        if if_subsent:
            l.append(befor_sub)
            for sub_p in l:
                if concept in " ".join(sub_p.leaves()):
                    declaration = check_more_precise(sub_p, concept)
                    return declaration
        else: 
            return tree
    else:
        return tree
# check the matched part are all considered as declarations for parameter
pattern_concept = r'(' + qualifiers_pattern + Concept + ')'
regex = re.compile(pattern_concept, re.I)
def check_in_concept(tree, be = False, end_point = False):
    text = ""
    concept = ""
    for subtree in tree:
        if not end_point:
            if isinstance(subtree, Tree):
                subtree.pretty_print()
                if subtree.label() in phrase_set + sentence_sign:
                    t, be, end_point = check_in_concept(subtree,be)
                    print(t)
                    concept += t
                    concept += " "
                    if end_point:
                        return concept, be, end_point
                elif subtree.label() in con_words:
                    if be and not end_point:
                        print('before the conjunction:', concept)
                        concept += " ".join(subtree.leaves())
                        concept += " "
                else:
                    text += " ".join(tree.leaves())
                    print('the text is: ', text)
                    match = re.search(pattern_concept, text, flags=re.I)
                    if match:
                        concept += text
                        concept += " "
                        be = True
                        print('new concept matched: ', concept)
                        return concept, be, end_point
                    else:
                        if be:
                            print('the concept is: ', concept)
                            be = True
                            end = True
                            return concept, be, end_point
                        else:
                            break
            else:
                print('it is not a tree')
                match = re.findall(pattern_concept, subtree, flags=re.I)
                if match:
                    print('matched')
                    concept += subtree
                    concept += " "
                else:
                    if be:
                        end_point = True
                    else:
                        print('still looking')
                        continue   
        else: 
            return concept, be, end_point
    if concept:       
        be = True 
        return concept, be, end_point
    else:
        return concept, be, end_point
#TODO: 'a,b', 'a and b' 
# match the sentence to see if it is a declaration
def decalration_identify(sentence, pattern):
    global annotation
    result = []
    current_index = 0
    text = ''
    indices_map = []
    # form all tokens into a string
    # attach an index for each token to trace back which token is matched
    for token in sentence:
        start_index = current_index
        text += token['token']
        current_index += len(token['token'])
        indices_map.append((start_index, current_index))
        text += ' '  
        current_index += 1  # Account for the space
    # get each match and trace back to original words
    
    # ignore some words like henceforth, here  
    for word in ignored_words:
        text_string = re.sub(r'\b' + re.escape(word) + r'\b', '', text)
    para_sen = constituency(text_string)
    regex = re.compile(pattern, re.I)
    for t in para_sen:
        for match in regex.finditer(text_string):
            if match:
                print('the matched part is:\n', match)
                subtree_list = []
                phrase = extract_subtree(t, subtree_list)
                i = 0
                start, end = match.start('m'), match.end('m')
                mathnode = re.split('\s*,\s*|\s*and\s*',match.group('m'))
                for p in phrase:
                    # find the Concept belongs to which seperated pharse 
                    if match.group('c') in " ".join(p.leaves()):
                        sub_p = check_more_precise(p, match.group('c'))
                        sub_p.pretty_print()
                        c, be, ended= check_in_concept(sub_p)
                        print('concept is: ', c)
                        declaration = re.split('\s*,\s*|\s*\band\s*\b',c)
                if not declaration:
                    declaration = re.split('\s*,\s*|\s*\band\s*\b', match.group('c'))
                print('declaration is:\n', declaration)
                if len(declaration) == len(mathnode):
                    for tokens, (s,e) in zip(sentence, indices_map):
                        if tokens['token'] == 'MathNode':
                            # see if it in the matched sentences
                            if s >= start and e <= end:
                                # see if it is matches earlier with other pattern
                                if not check_node_exists(tokens.get('start-ref'),tokens.get('end-ref')):
                                    if_equation, if_number, if_para = number_identifier(tokens['replaced-node'])
                                    if if_number: 
                                        continue
                                    elif if_equation:      
                                        equation_form(tokens, declaration[i])
                                    else:
                                        parameter_form(tokens, declaration[i])
                                    i += 1
                else:
                    for tokens, (s,e) in zip(sentence, indices_map):
                        if tokens['token'] == 'MathNode':
                            if s >= start and e <= end:
                                if not check_node_exists(tokens.get('start-ref'),tokens.get('end-ref')):
                                    if_equation, if_number, if_para = number_identifier(tokens['replaced-node'])
                                    if if_number: 
                                        continue
                                    elif if_equation:      
                                        equation_form(tokens, declaration[0])
                                    else:
                                        parameter_form(tokens, declaration[0])

    return text_string




s = get_end_point(report)
id_counter = 0
patterns = [r'(let|where|(suppose(\s*that)?))\s+(?P<m>MathNode(?:\s*,\s*MathNode)*(?:\s*and\s*MathNode)?)\s+(is|are|be)\s+(an?\s*|the\s*|some\s*)?(?P<c>' + qualifiers_pattern + Concept + r'(\s*,\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')*(\s*and\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')?)',
            r'((there\s*(is|are|exists?)(\s*an?|\s*the|\s*some)?)|(for\s*some))\s*(?P<c>' + qualifiers_pattern + Concept + r'(\s*,\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')*(\s*and\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')?)\s*(?P<m>MathNode(?:\s*,\s*MathNode)*(?:\s*and\s*MathNode)?)',
            # it is intend to detect the 'Let MathNode be constant, MathNode real number, MathNode verctors', if doesn't have pattern3, then the second and the third can not be matched, but if has pattern3 then could match 'L function' and 'given MathNode Concept'(since some , and in the MathNode)
            r'(?P<m>MathNode)\s*(be\s*)?(?:an?\s*|the\s*)?(?P<c>' + qualifiers_pattern + Concept + ')',
            r'for\s*(every|all|any)\s*(?P<c>' + qualifiers_pattern + Concept + r'(\s*,\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')*(\s*and\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')?)\s*(?P<m>(MathNode)(?:\s*,\s*MathNode)*(?:\s*and\s*MathNode)?)',
            r'(?P<c>' + qualifiers_pattern + Concept + r')\s*,\s*(?P<m>(MathNode)(?:\s*,\s*MathNode)*(?:\s*and\s*MathNode)?)\s*(\.|,|of)?',
            r'(?P<c>' + qualifiers_pattern + Concept + r'(\s*,\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')*(\s*and\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')?)\s*(is\s*|are\s*)?((denoted\s*by\s*)|(given\s*by\s*))?(?P<m>(MathNode)(?:\s*,\s*MathNode)*(?:\s*and\s*MathNode)?)',
            r'(?P<m>(MathNode)(?:\s*,\s*MathNode)*(?:\s*and\s*MathNode)?)\s*(is|are)\s*(said\s*to\s*be\s*)?(?:an?\s*|the\s*)?(?P<c>' + qualifiers_pattern + Concept + r'(\s*,\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')*(\s*and\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')?)',
            r'(?P<m>(MathNode)(?:\s*,\s*MathNode)*(?:\s*and\s*MathNode)?)\s*(denotes?|((are|is)\s*denoted\s*as))\s*(?:an?\s*|the\s*)?(?P<c>' + qualifiers_pattern + Concept + r'(\s*,\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')*(\s*and\s*(an?\s*|the\s*)?' + qualifiers_pattern + Concept + r')?)'
            #For fireballs in the energy range of MathNode , MathNode a' will be matched 
            #TODO: get concepts set √
            # and 'and the relativistic Lorentz factor , MathNode o' will also be matched          
            #TODO: 'optical depth MathNode, thermal energy MathNode, maximal relativistic expansion MathNode and a maximal baryonic load of MathNode' will be matched even MathNode is only numbers  √
            #TODO: pattern for 'the initial optical depth is MathNode' 
            
            ]


for i in range(len(s)):
    t = ""
    sentence = [t for t in report.get('tokens') if t['start-ref'] >= s[i][0] and t['end-ref'] <= s[i][1]]
    for a in sentence:
        t += a.get('token')
        t += " "
    if 'MathNode' not in t:
        continue
    else:
        for i, pattern in enumerate(patterns):
            print(i)
            text= decalration_identify(sentence, pattern)
            print('sentence is:\n', text)
            
            

annotation_data = json.dumps(annotation,indent=4)
print(annotation_data,'\n')

with open('annotation.json', 'w') as file:
    file.write(annotation_data)

    
#if it is a equation, the declaration is probably for the parameter before the equal sign
#if it is a parameter, the classify if it is sigle parameter or sth with :,-> and so on
#for the declaration_identify, should change 'put all mathnode into consideration' into 'match all elements in group m with elements in group c'

     

#Problems meet: Let MathNode be a Hilbert space and let MathNode where MathNode is some index set , be a collection of vectors in MathNode Then MathNode is said to be a frame for MathNode if there exist constants MathNode and MathNode MathNode such that for any MathNode MathEquation The constants MathNode and MathNode are called the frame bounds 



