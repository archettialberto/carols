"""Optical music recognition drafts for raster scans, with Audiveris 5.4 built from source.

A draft is only a starting point: check every voice against the scan (AGENTS.md).
Development only; needs Java 21 and, for `tiff`, PyMuPDF + Pillow.

  python sources/scripts/omr.py prepare-build AUDIVERIS_SRC   # write a Maven pom for the source tree
      then: cd AUDIVERIS_SRC/app && mvn -q compile dependency:copy-dependencies -DoutputDirectory=target/lib
  python sources/scripts/omr.py tiff "songs/Ding Dong.pdf" OUT.tif [--pages 1,2]
  python sources/scripts/omr.py run AUDIVERIS_SRC OUT_DIR INPUT.tif [...]   # writes OUT_DIR/<name>.mxl
  python sources/scripts/omr.py dump DRAFT.mxl                              # notes per part and measure

Build notes (Audiveris 5.4, November 2026): download the 5.4 source archive from
https://github.com/Audiveris/audiveris, use Maven 3.9 with Java 21 (its Gradle wrapper failed
offline); `prepare-build` converts the Gradle dependencies, pins slf4j-api 2.0.7, adds the
Linux leptonica/tesseract natives and writes ProgramId.java. Put Tesseract's eng.traineddata in
the folder given by --tessdata. Raster input works best as 300-dpi greyscale TIFF.
"""
import argparse
import os
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


def prepare_build(source):
    app = Path(source) / 'app'
    gradle = (app / 'build.gradle').read_text()
    section = gradle.split('dependencies {')[1].split('testImplementation')[0]
    versions = {'jcppVersion': '1.5.9', 'leptVersion': '1.83.0', 'tessVersion': '5.3.1'}
    deps = []
    for group, name, version in re.findall(r"group: '([^']+)', name: '([^']+)', version: [\"']([^\"']+)[\"']", section):
        for key, value in versions.items():
            version = version.replace('${' + key + '}', value)
        if name == 'slf4j-api':
            version = '2.0.7'  # matches the logback version Audiveris ships with
        # bsaf declares a system-scope javax.jnlp (javaws.jar), which modern JDKs no longer ship.
        exclusions = ('<exclusions><exclusion><groupId>javax.jnlp</groupId><artifactId>jnlp</artifactId></exclusion></exclusions>'
                      if name == 'bsaf' else '')
        deps.append(f'<dependency><groupId>{group}</groupId><artifactId>{name}</artifactId><version>{version}</version>{exclusions}</dependency>')
    for name, version in [('leptonica', '1.83.0-1.5.9'), ('tesseract', '5.3.1-1.5.9')]:
        deps.append(f'<dependency><groupId>org.bytedeco</groupId><artifactId>{name}</artifactId><version>{version}</version>'
                    '<classifier>linux-x86_64</classifier></dependency>')
    (app / 'pom.xml').write_text(
        '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>local</groupId>'
        '<artifactId>audiveris</artifactId><version>5.4</version><properties><maven.compiler.source>21</maven.compiler.source>'
        '<maven.compiler.target>21</maven.compiler.target><project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>'
        '</properties><repositories><repository><id>jboss</id><url>https://repository.jboss.org/nexus/content/repositories/'
        'thirdparty-releases</url></repository></repositories><dependencies>' + ''.join(deps) + '</dependencies><build><plugins>'
        '<plugin><groupId>org.apache.maven.plugins</groupId><artifactId>maven-compiler-plugin</artifactId><version>3.13.0</version>'
        '</plugin></plugins><resources><resource><directory>res</directory><targetPath>res</targetPath></resource><resource>'
        '<directory>src/main/resources</directory></resource></resources></build></project>')
    ids = {'COMPANY_NAME': 'Audiveris Ltd.', 'COMPANY_ID': 'AudiverisLtd', 'PROGRAM_NAME': 'Audiveris', 'PROGRAM_ID': 'audiveris',
           'PROGRAM_VERSION': '5.4', 'PROGRAM_BUILD': 'official-5.4', 'TESSDATA_TAG': '4.1.0'}
    (app / 'src/main/java/org/audiveris/omr/ProgramId.java').write_text(
        'package org.audiveris.omr; public abstract class ProgramId {'
        + ''.join(f'public static final String {k}="{v}";' for k, v in ids.items()) + '}')
    print(f'{app}/pom.xml: {len(deps)} dependencies')


def tiff(pdf, output, pages=None, dpi=300):
    import fitz
    from PIL import Image
    doc = fitz.open(pdf)
    images = []
    for index in pages or range(len(doc)):
        pix = doc[index].get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), colorspace=fitz.csGRAY)
        images.append(Image.frombytes('L', (pix.width, pix.height), pix.samples))
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    images[0].save(output, save_all=True, append_images=images[1:], compression='tiff_lzw', dpi=(dpi, dpi))
    print(output, len(images), 'page(s)')


def run(source, output, inputs, tessdata, memory):
    app = Path(source).resolve() / 'app'
    work = Path(output).resolve()
    work.mkdir(parents=True, exist_ok=True)
    # Keep Audiveris' caches and settings out of the user's home folder.
    env = {**os.environ, 'XDG_CACHE_HOME': str(work / '.cache'), 'XDG_CONFIG_HOME': str(work / '.config'),
           'XDG_DATA_HOME': str(work / '.data'), 'TESSDATA_PREFIX': str(Path(tessdata).resolve())}
    command = ['java', '--add-exports=java.desktop/sun.awt.image=ALL-UNNAMED', f'-Xmx{memory}', '-Djava.awt.headless=true',
               '-cp', f'{app}/target/classes:{app}/target/lib/*', 'Audiveris', '-batch', '-transcribe', '-export',
               '-output', str(work)]
    for item in inputs:
        log = work / (Path(item).stem + '.log')
        print('recognising', item, '→ log', log, flush=True)
        with open(log, 'w') as handle:
            result = subprocess.run(command + [str(Path(item).resolve())], env=env, cwd=app, stdout=handle, stderr=subprocess.STDOUT)
        print('exit', result.returncode, flush=True)


def dump(path):
    """Print each part's notes per measure as (beat, pitch, duration, voice, staff, stem, lyrics)."""
    archive = zipfile.ZipFile(path)
    name = next(n for n in archive.namelist() if n.endswith('.xml') and not n.startswith('META'))
    root = ET.fromstring(archive.read(name))
    for part in root.findall('part'):
        print('PART', part.get('id'))
        divisions = 1
        for measure in part.findall('measure'):
            divisions = int(measure.findtext('attributes/divisions', divisions))
            at = last = 0
            notes = []
            for item in measure:
                if item.tag in ('backup', 'forward'):
                    at += (-1 if item.tag == 'backup' else 1) * int(item.findtext('duration')) / divisions
                if item.tag != 'note':
                    continue
                chord = item.find('chord') is not None
                start = last if chord else at
                duration = int(item.findtext('duration', 0)) / divisions
                alter = {'1': '#', '-1': 'b'}.get(item.findtext('pitch/alter'), '')
                pitch = item.findtext('pitch/step', 'R') + alter + item.findtext('pitch/octave', '')
                lyrics = [lyric.findtext('text') for lyric in item.findall('lyric')]
                notes.append((start, pitch, duration, item.findtext('voice'), item.findtext('staff'), item.findtext('stem'), lyrics))
                if not chord:
                    at += duration
                    last = start
            print(measure.get('number'), notes)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('prepare-build').add_argument('source')
    t = sub.add_parser('tiff'); t.add_argument('pdf'); t.add_argument('output'); t.add_argument('--pages')
    r = sub.add_parser('run'); r.add_argument('source'); r.add_argument('output'); r.add_argument('inputs', nargs='+')
    r.add_argument('--tessdata', default='tessdata'); r.add_argument('--memory', default='5g')
    sub.add_parser('dump').add_argument('draft')
    args = parser.parse_args()
    if args.command == 'prepare-build':
        prepare_build(args.source)
    elif args.command == 'tiff':
        tiff(args.pdf, args.output, [int(p) - 1 for p in args.pages.split(',')] if args.pages else None)
    elif args.command == 'run':
        run(args.source, args.output, args.inputs, args.tessdata, args.memory)
    else:
        dump(args.draft)


if __name__ == '__main__':
    sys.exit(main())
