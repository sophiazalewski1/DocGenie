from bs4 import BeautifulSoup, NavigableString, Tag
import re

with open("index.html", 'r') as html_file:
    parsed_html = BeautifulSoup(html_file, 'html.parser')

def parse_table(table_elt):
    table = ""
    rows = table_elt.find_all('tr')
    for row in rows:
        # Render table header
        cols = row.find_all('th')
        if cols != []: 
            table += "|{}|\n".format('|'.join([col.text for col in cols]))
            table += "|{}|\n".format('|'.join(["--" for _ in cols]))
        # Render table data
        else:
            cols = row.find_all('td')
            table += "|{}|\n".format('|'.join([col.text for col in cols]))
    return table

def parse_body(elt, strip=True):
    markdown_text = ''
    for content in elt.contents:
        if isinstance(content, NavigableString):
            content_string = str(content)
            content_string = re.sub(r'\s+', ' ', content_string) # Remove multiple white spaces
            markdown_text += content_string
        elif content.name == 'span':
            text = content.text
            if strip: text = text.strip()
            classes = content.get('class', [])
            if 'bold' in classes:
                markdown_text += '**{}** '.format(text)
            elif 'emphasis' in classes:
                markdown_text += '*{}* '.format(text)
            elif 'note' in [c[0:4] for c in classes]:
                markdown_text += '> {}\n\n'.format(text)
        else:
            markdown_text += parse_body(content)
            # partial_markdown, _ = parse_element(content)
            # markdown_text += partial_markdown
    return markdown_text

def parse_element(elt, in_codeblock = False):
    markdown = ""

    if isinstance(elt, Tag):
        # Header elts
        classes = elt.get('class', [])
        h_prefixes = [c[0:2] for c in classes]
        code_prefixes = [c[0:4] for c in classes]

        if "code" not in code_prefixes and in_codeblock:
            markdown += "```\n"
            in_codeblock = False

        if 'h2' in h_prefixes or 'h1' in h_prefixes:
            markdown += "# {}\n".format(elt.text)
        elif 'h3' in h_prefixes:
            markdown += "## {}\n".format(elt.text)
        elif 'h4' in h_prefixes:
            markdown += "### {}\n".format(elt.text)
        elif 'h5' in h_prefixes:
            markdown += "#### {}\n".format(elt.text)

        # Body
        elif "body" in classes:
            markdown += parse_body(elt)
            markdown += "\n\n"

        # Bullet notes
        elif "list_bul" in classes or "tbl_list_bul" in classes:
            markdown += "* {}\n".format(elt.text[1:])

        # Code blocks
        elif "code" in code_prefixes:
            if in_codeblock:
                markdown += elt.text
                markdown += "\n"
            else:
                markdown += "```\n{}\n".format(elt.text)
                in_codeblock = True

        # Table
        elif elt.name == "table":
            markdown += parse_table(elt)

        else:
            for content in elt.contents:
                partial_markdown, in_codeblock = parse_element(content, in_codeblock=in_codeblock)
                markdown += partial_markdown

    return markdown, in_codeblock


markdown = ""
in_codeblock = False
for elt in parsed_html.body.find_all('div'):
    partial_markdown, in_codeblock = parse_element(elt, in_codeblock)
    markdown += partial_markdown

print(markdown)