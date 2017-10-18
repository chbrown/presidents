import json


def read_lines(*filepaths):
    '''
    Iterate over all lines in all files listed by `filepaths`
    '''
    for filepath in filepaths:
        with open(filepath) as fp:
            for line in fp:
                yield line


def read_strings(*filepaths):
    '''
    Read each line from each file in `filepaths` as a (byte) string without a
    terminating line separator
    '''
    for line in read_lines(*filepaths):
        yield line.rstrip()


def read_ldjson(*filepaths):
    '''
    Read each line from each file in `filepaths` as a JSON object
    '''
    for line in read_lines(*filepaths):
        yield json.loads(line)
