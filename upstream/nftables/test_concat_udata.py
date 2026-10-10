#!/usr/bin/env python3
"""Exercise real libnftables concat userdata APIs without sockets or privileges.

The 256-byte buffer matches NFT_USERDATA_MAXLEN. The optional set envelope
uses the actual set_key_expression() source, which ignores build_udata errors.
An unmodified current library is expected to exit 1 with truncated metadata.
This is a component regression, not a kernel text/JSON listing test.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', required=True, type=pathlib.Path)
parser.add_argument('--build', required=True, type=pathlib.Path)
parser.add_argument('--prefix', required=True, type=pathlib.Path)
parser.add_argument('--output', type=pathlib.Path)
args = parser.parse_args()

def extract_function(text, anchor):
    start = text.index(anchor)
    end = text.index('{', start) + 1
    depth = 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

mnl_source = (args.source / 'src/mnl.c').read_text()
envelope = extract_function(mnl_source, 'static void set_key_expression(')
test = r'''
#include <nft.h>
#include <stdio.h>
#include <expression.h>
#include <datatype.h>
#include <ct.h>
#include <netlink.h>
#include <utils.h>
#include <libnftnl/udata.h>
#include <linux/netfilter/nf_tables.h>
''' + envelope + r'''
int main(void)
{
    struct location loc = {0};
    unsigned counts[] = {1, 4, 5, 6, 11};
    unsigned failures = 0;

    printf("{\"registerSizeBytes\":%u,\"registerCount\":%u,"
           "\"userdataBufferBytes\":%u,\"variants\":[",
           NFT_REG32_SIZE, NFT_REG32_COUNT, NFT_USERDATA_MAXLEN);
    for (unsigned mode = 0; mode < 2; mode++) {
        for (unsigned v = 0; v < sizeof(counts) / sizeof(counts[0]); v++) {
            struct expr *concat = concat_expr_alloc(&loc);
            uint32_t dt = 0;
            for (unsigned i = 0; i < counts[v]; i++) {
                struct expr *e = ct_expr_alloc(&loc, NFT_CT_MARK, -1);
                dt = concat_subtype_add(dt, e->dtype->type);
                concat_expr_add(concat, e);
            }
            concat->dtype = concat_type_alloc(dt);
            concat->len = 32 * counts[v];

            struct nftnl_udata_buf *buf = nftnl_udata_buf_alloc(NFT_USERDATA_MAXLEN);
            if (!buf)
                return 2;
            int ret = 0;
            unsigned decoded = 0;
            if (mode == 0) {
                struct nftnl_udata *outer = nftnl_udata_nest_start(buf, 0);
                ret = expr_ops(concat)->build_udata(buf, concat);
                nftnl_udata_nest_end(buf, outer);
                /* Inspect even a failed builder: the real caller ignores its return. */
                struct expr *parsed = expr_ops(concat)->parse_udata(outer);
                if (parsed) {
                    decoded = expr_concat(parsed)->size;
                    expr_free(parsed);
                }
            } else {
                /* Real key typeof wrapper, without the other set/map attributes. */
                set_key_expression(NULL, concat, 0, buf, NFTNL_UDATA_SET_KEY_TYPEOF);
                const struct nftnl_udata *key = nftnl_udata_buf_data(buf);
                const struct nftnl_udata *etype = nftnl_udata_get(key);
                const struct nftnl_udata *data = nftnl_udata_next(etype);
                struct expr *parsed = expr_ops(concat)->parse_udata(data);
                if (parsed) {
                    decoded = expr_concat(parsed)->size;
                    expr_free(parsed);
                }
            }
            bool passed = decoded == counts[v] && (mode != 0 || ret == 0);
            failures += !passed;
            char return_string[16];
            snprintf(return_string, sizeof(return_string), "%d", ret);
            printf("%s{\"fields\":%u,\"setKeyEnvelope\":%s,"
                   "\"buildReturnObserved\":%s,\"buildReturn\":%s,"
                   "\"userdataBytes\":%u,\"parsedFields\":%u,\"passed\":%s}",
                   mode || v ? "," : "", counts[v], mode ? "true" : "false",
                   mode ? "false" : "true", mode ? "null" : return_string, nftnl_udata_buf_len(buf),
                   decoded, passed ? "true" : "false");
            nftnl_udata_buf_free(buf);
            expr_free(concat);
        }
    }
    printf("],\"failedCases\":%u,\"passed\":%s}\n",
           failures, failures ? "false" : "true");
    return failures ? 1 : 0;
}
'''

library = args.build / 'src/.libs/libnftables.a'
with tempfile.TemporaryDirectory(prefix='nft-concat-udata-') as directory:
    source_file = pathlib.Path(directory) / 'test.c'
    executable = source_file.with_suffix('')
    source_file.write_text(test)
    subprocess.run([
        'cc', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
        '-DHAVE_CONFIG_H', '-I' + str(args.build),
        '-I' + str(args.source / 'include'), '-I' + str(args.prefix / 'include'),
        str(source_file), str(library), '-L' + str(args.prefix / 'lib'),
        '-Wl,-rpath,' + str(args.prefix / 'lib'),
        '-lnftnl', '-lmnl', '-lgmp', '-ljansson', '-o', str(executable),
    ], check=True)
    process = subprocess.run([str(executable)], text=True, capture_output=True)
    if not process.stdout:
        raise RuntimeError(process.stderr)
    result = json.loads(process.stdout)
    result.update({
        'realBuiltLibrary': True,
        'sourceCommit': subprocess.check_output(
            ['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip(),
        'mnlSourceSha256': hashlib.sha256((args.source / 'src/mnl.c').read_bytes()).hexdigest(),
        'expressionSourceSha256': hashlib.sha256((args.source / 'src/expression.c').read_bytes()).hexdigest(),
        'staticLibrarySha256': hashlib.sha256(library.read_bytes()).hexdigest(),
        'setEnvelopeUsesActualSource': True,
        'otherSetMapAttributesIncluded': False,
        'kernelNetlinkTested': False,
    })
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    raise SystemExit(process.returncode)
