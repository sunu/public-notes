import json
from pathlib import Path
from pprint import pprint
from collections import defaultdict
import os

# Start anew
os.system('rm -rf docs && cp -r notes docs')


# Read Cache
with open('docs/.obsidian/cache', 'r') as fp:
    cache = json.load(fp)


# Collect backlinks
def for_each_md():
    return list(Path("docs").rglob("*.md"))


def drop_header(link):
    return link.split('#')[0]


pprint(cache['files'])

hash_to_file_map = {}
stem_to_file = {}
for f in for_each_md():
    stem_to_file[f.stem] = f
    file = cache['files'].get(str(f)[5:])
    if file is not None:
        f_hash = file['hash']
        hash_to_file_map[f_hash] = f

pprint(hash_to_file_map)
pprint(stem_to_file)

backlinks = defaultdict(list)
for hsh, mtdt in cache['metadata'].items():
    links = mtdt['links']
    for link in links:
        src = hash_to_file_map.get(hsh)
        if src:
            backlinks[drop_header(link['link'])].append({
                'text': f"{link['beforeContext']}{link['original']}(){link['afterContext']}",  # noqa
                'source': src
            })

pprint(dict(backlinks))

# Convert links to proper markdown
for stem, path in stem_to_file.items():
    path = str(path)[4:][:-3]
    os.system(f'fd -t f -e md . docs/ -X sd -s "[[{stem}]]" "[[{stem}]]({path})"')  # noqa

# Convert image embeds to markdown syntax
os.system("fd -t f -e md . docs/ -X sd '!\[\[(?P<name>\w.+)\]\]' '![${name}](/assets/${name})'")  # noqa

# Write backlinks
for stem, links in backlinks.items():
    path = str(stem_to_file[stem])[5:]
    path = Path('docs').joinpath(path)
    with open(path, 'a') as fp:
        fp.write('\n\n')
        fp.write('# Linked Mentions\n')
        per_page = defaultdict(set)
        for link in links:
            source = link['source']
            per_page[source].add(link["text"])
        for source, texts in per_page.items():
            source_path = str(source)[4:][:-3]
            fp.write(f'- [[{source.stem}]]({source_path})\n')
            for text in texts:
                fp.write(f'    - {text}\n')


# Clean up
os.system('rm -rf docs/.obsidian/')
os.system('cp CNAME docs/')
os.system('cp -r assets/ docs/')
os.system('cp -r _layouts/ docs/')
os.system('cp _config.yml docs/')
