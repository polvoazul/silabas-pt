#!/usr/bin/env python3
from lxml import etree
import pandas as pd
import glob
from markdownify import markdownify as md


files = sorted(glob.glob('./html/*'))
parser = etree.HTMLParser()

def text(el):
    return ''.join(el.itertext())

def inner_html(el):
    return etree.tostring(el, pretty_print=True)

def get_positions(word, syls):
    syls = syls.replace('_', '')
    idx_w, idx_s = 0, 0
    strong = 0
    positions = []
    while idx_w < len(word):
        char_w = word[idx_w]
        char_s = syls[idx_s]
        if char_w == "'": idx_w += 1; continue
        if char_s != char_w:
            if char_s == '*':
                strong = len(positions)
                idx_s += 2
            elif char_s == '|':
                positions.append(idx_w) # the number is the position where you would insert the separator 'abc|defg' (3)
                idx_s += 1
            elif char_s in "´'`": idx_s += 1
            else: print('!!!!!!!!!!!!!', word, syls); return [0], 0 #breakpoint() # raise Exception(char_s, word, syls)
        else:
            if char_s == '-':
                positions.append(idx_w)
            idx_w += 1
            idx_s += 1
    return positions, strong


def convert_to_markdown(element):
    html = inner_html(element)
    html = html.replace(b'\n',  b'')
    html = html.replace(b'<b>',  b'**')
    html = html.replace(b'</b>', b'**')
    html = html.replace(b'<u>',  b'__')
    html = html.replace(b'</u>', b'__')
    out = text(etree.fromstring(html))
    out = out.split('\n')[0].strip()
    out = out.replace('**·**', '|')
    out = out.replace('·', '|')
    out = out.replace('__**', '**').replace('**__', '**')
    out = out.replace(' ', '')
    return out
    

data = []
for f in files:
    print(f)
    with open(f) as _f:
        html = _f.read()
        html = html.split('<tr><th>Palavra<th>Divisão silábica')[1]
        html = html.split('</table>')[0]
        tree = etree.fromstring(html, parser)

    rows = tree.xpath('//tr')
    for row in rows:
        word = row.xpath('.//td[@title="Palavra"]/b/a/text()')[0]
        if ' ' in word: continue
        if word in {'circum-anal', 'corredator', 'êxul', 'ham-ioc-chong', 'inspetor-orientador', 'juiz-forana',
                    'marroio-negro', 'quianda-muchito', 'raimundo-silvestre', 'rainha-margarida',
                    'ratinho-lavadeiro', 'retopético', 'raiz-da-madre-de-deus', 'reformador-reitor',
                    'regenerador-liberal', 'relógio-pulseira', 'reposteiro-mor', 'reserva-ouro',
                    'residência-geral', 'residente-geral', 'rodrigo-afonso', 'rubi-topázio', 'rosário-bravio',
                    'rui-barbosense', 'sabão-vegetal', 'sacerdote-mor', 'saci-pererê', 'zuzara'
        }: continue # words with errors

        category = row.xpath('.//td[@title="Palavra"]/text()')[0].strip().strip('()')

        syl_html = row.xpath('.//td[@title="pron�ncia"]')[0]
        syl = convert_to_markdown(syl_html)
        try: positions, strong = get_positions(word, syl)
        except Exception: breakpoint()

        data.append({'word': word, 'category': category, 'syl': syl, 'syl_positions': positions, 'syl_strong': strong})

df = pd.DataFrame(data)
df.to_csv('syls.csv', index=False)
