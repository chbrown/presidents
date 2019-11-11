from pathlib import Path
import logging
import subprocess

import altair as alt

logger = logging.getLogger(__name__)


def export_altair_chart(chart: alt.Chart, basename: str, dirpath: Path):
    '''
    Render the given chart to a PDF at {dirpath}/{basename}.pdf
    Write the raw Vega-Lite JSON to {dirpath}/{basename}.vl.json

    May need to install dependencies:
        brew install svg2pdf
        npm config set python python2.7
        npm install -g vega@2.6.5 vega-lite@1.3.1
    '''
    if not isinstance(chart, alt.Chart):
        raise RuntimeError('chart must be an altair.Chart instance')
    if basename.endswith('.pdf'):
        raise RuntimeError('basename should not end in .pdf')

    vl_json_filepath = dirpath / f'{basename}.vl.json'
    pdf_filepath = dirpath / f'{basename}.pdf'

    vl_json_string = chart.to_json()
    try:
        with open(vl_json_filepath, 'x') as vl_json_file:
            vl_json_file.write(vl_json_string)
        logger.info('Wrote Vega-Lite to %s', vl_json_filepath)
    except FileExistsError as exc:
        logger.warning('Not writing Vega-Lite: %s', exc)

    try:
        vl2svg_proc = subprocess.run(['vl2svg'], stdout=subprocess.PIPE, input=vl_json_string,
                                     universal_newlines=True, check=True)
        svg_string = vl2svg_proc.stdout
        with open(pdf_filepath, 'xb') as pdf_file:
            svg2pdf_proc = subprocess.run(['svg2pdf'], stdout=pdf_file, input=svg_string,
                                          encoding='utf-8', check=True)
        logger.info('Wrote PDF to "%s"', pdf_filepath)
    except FileExistsError as exc:
        logger.warning('Not writing PDF: %s', exc)
