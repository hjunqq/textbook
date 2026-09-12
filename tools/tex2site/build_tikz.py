#!/usr/bin/env python3
"""Compile current numbered jobs and record SVG provenance. Cross-platform."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import shutil
import subprocess
from svg_provenance import source_hash, file_hash, verified_svg

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get('TEX2SITE_REPO', HERE.parent.parent))
BUILD = Path(os.environ.get('TEX2SITE_BUILD', REPO/'temp/tex2site-build'))/'tikz'


def executable(name):
    found = shutil.which(name)
    local = Path('C:/texlive/2026/bin/windows')/(name+'.exe')
    if found:
        return found
    if local.is_file():
        return str(local)
    raise FileNotFoundError(name+' must be installed and available in PATH')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--force', action='store_true', help='Recompile all current figures')
    args = parser.parse_args()
    jobs = json.loads((BUILD/'expected-jobs.json').read_text(encoding='utf-8'))
    preamble = (HERE/'preamble.tex').read_text(encoding='utf-8')
    definitions = (REPO/'output/tikz-diagrams.tex').read_text(encoding='utf-8')
    (BUILD/'tikz-diagrams.tex').write_text(definitions, encoding='utf-8')
    xelatex, cairo = executable('xelatex'), executable('pdftocairo')

    def compile_one(job):
        name = job['file']
        stem = Path(name).stem
        snippet = (BUILD/(stem+'.tex')).read_text(encoding='utf-8')
        digest = source_hash(snippet, preamble, definitions)
        if digest != job['source_sha256']:
            raise ValueError('Source changed after convert.py: '+name)
        cached = None if args.force else verified_svg(BUILD, name, digest, require_pdf=True)
        if cached is None:
            (BUILD/('build_'+stem+'.tex')).write_text(preamble+'\n'+snippet+'\n\\end{document}\n', encoding='utf-8')
            result = subprocess.run([xelatex, '-interaction=nonstopmode', '-halt-on-error',
                                     '-jobname='+stem, 'build_'+stem+'.tex'], cwd=BUILD,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
            (BUILD/(stem+'.build.txt')).write_bytes(result.stdout)
            if result.returncode:
                raise RuntimeError('XeLaTeX failed: '+name+'; see its .build.txt')
            log=(BUILD/(stem+'.log')).read_text(encoding='utf-8', errors='replace')
            if 'Missing character:' in log or 'Overfull' in log:
                raise RuntimeError('Missing glyph or overflow: '+name)
            subprocess.run([cairo, '-svg', stem+'.pdf', name], cwd=BUILD, check=True, timeout=30)
        return name, dict(source_sha256=digest, svg_sha256=file_hash(BUILD/name),
                          pdf_sha256=file_hash(BUILD/(stem+'.pdf')), rebuilt=cached is None)

    results, errors = {}, []
    with ThreadPoolExecutor(max_workers=max(1,args.jobs)) as pool:
        futures={pool.submit(compile_one,job):job['file'] for job in jobs}
        for future in as_completed(futures):
            try:
                name, record = future.result()
                results[name] = record
                print(('BUILT ' if record['rebuilt'] else 'VERIFIED ')+name, flush=True)
            except Exception as error:
                errors.append(str(error)); print('FAIL '+str(error), flush=True)
    # Failed and removed jobs must never retain previous provenance entries.
    (BUILD/'svg-manifest.json').write_text(json.dumps(dict(version=1, figures=results), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Verified SVGs:', len(results))


if __name__ == '__main__':
    main()
