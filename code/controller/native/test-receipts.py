#!/usr/bin/env python3
"""Compile the actual receipt module source under a small mocked transport."""
import pathlib,subprocess,tempfile
here=pathlib.Path(__file__).resolve().parent
stub='''#pragma once
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <netinet/in.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32;
typedef uint64_t u64; typedef uint32_t __be32;
#define DEFINE_SPINLOCK(x) int x
#define spin_lock_bh(x) ((void)(x))
#define spin_unlock_bh(x) ((void)(x))
#define kmalloc(n,f) malloc(n)
#define kfree(x) free(x)
#define GFP_ATOMIC 0
#define THIS_MODULE 0
#define try_module_get(x) true
#define module_put(x) ((void)(x))
#define BUILD_BUG_ON(x) _Static_assert(!(x), #x)
#define EXPORT_SYMBOL(x)
#define EXPORT_SYMBOL_GPL(x)
#define MODULE_LICENSE(x)
#define MODULE_DESCRIPTION(x)
'''
with tempfile.TemporaryDirectory(prefix='athena-receipts-test-') as d:
    root=pathlib.Path(d);(root/'linux').mkdir()
    (root/'stub.h').write_text(stub)
    for name in ['module.h','slab.h','spinlock.h','types.h','in6.h']:
        (root/'linux'/name).write_text('#include "../stub.h"\n')
    output=root/'test'
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Wno-unused-parameter',
        '-Werror','-I'+str(root),'-I'+str(here),str(here/'test-receipts.c'),'-o',str(output)],check=True)
    subprocess.run([str(output)],check=True)
