#!/usr/bin/env python3
"""Compile the actual gate selection function with explicit CT/clock mocks.

This checks one-selection semantics, not complete ECM retries or firmware.
"""
import json, pathlib, subprocess, tempfile
here=pathlib.Path(__file__).resolve().parent
source=(here/'athena_ecm_gate.c').read_text()
def function(name):
    start=source.index('static ',source.index(name)-100)
    # Locate the declaration containing this function, not an earlier helper.
    start=source.rfind('static ',0,source.index(name))
    opening=source.index('{',source.index(name));depth=1;end=opening+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[start:end]
stub=r'''
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <netinet/in.h>
typedef uint32_t u32; typedef uint64_t u64;
typedef int ecm_ae_classifier_result_t;
#define ECM_AE_CLASSIFIER_RESULT_NOT_YET 0
#define ECM_AE_CLASSIFIER_RESULT_NSS 1
#define ECM_AE_CLASSIFIER_FLOW_ROUTED 1
#define ECM_AE_CLASSIFIER_FLOW_MULTICAST 2
#define spin_lock_bh(x) ((void)(x))
#define spin_unlock_bh(x) ((void)(x))
#define CAPACITY 32
#define LIVE 1
struct nf_conntrack_tuple {struct {struct {u32 ip;}u3;union {uint16_t all;}u;}src;
 struct {struct {u32 ip;}u3;union {uint16_t all;}u;unsigned protonum;}dst;};
struct ecm_ae_classifier_info {unsigned ip_ver,flag,src_port,dst_port,protocol;
 struct {u32 v4_addr;}src,dest;};
struct entry {unsigned state,selected;u64 until;struct nf_conntrack_tuple original,reply;};
static struct entry entries[CAPACITY];static int entry_lock;static bool stopping,ct_live=true;
static u64 clock_ms=100,routed_attempts,tuple_matches,instance_rejections;
static u64 now_ms(void){return clock_ms;}
static bool instance_live(struct entry *e){(void)e;return ct_live;}
'''
test=r'''
static unsigned checks;
static void check(bool v){checks++;if(!v){fprintf(stderr,"selection check %u failed\n",checks);abort();}}
int main(void){
 struct ecm_ae_classifier_info i={.ip_ver=4,.flag=ECM_AE_CLASSIFIER_FLOW_ROUTED,
 .src={0x01020304},.dest={0x05060708},.src_port=1000,.dst_port=2000,.protocol=17};
 entries[0]=(struct entry){.state=LIVE,.until=200,.original={.src={.u3={i.src.v4_addr},.u={htons(1000)}},
 .dst={.u3={i.dest.v4_addr},.u={htons(2000)},.protonum=17}}};
 check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NSS);check(entries[0].selected==1);
 check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 entries[0].until=300;check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 entries[0].selected=0;clock_ms=300;check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 clock_ms=100;ct_live=false;check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);check(!entries[0].selected);
 ct_live=true;stopping=true;check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 stopping=false;i.ip_ver=6;check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 i.ip_ver=4;i.flag|=ECM_AE_CLASSIFIER_FLOW_MULTICAST;check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 i.flag=ECM_AE_CLASSIFIER_FLOW_ROUTED;i.src_port++;check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 i.src_port--;entries[0].state=2;check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NOT_YET);
 entries[0].state=LIVE;check(select_flow(&i)==ECM_AE_CLASSIFIER_RESULT_NSS);
 printf("{\"passed\":true,\"checks\":%u,\"oneSelectionPreserved\":true,\"mockedCT\":true,\"firmwareProof\":false}\n",checks);
}
'''
with tempfile.TemporaryDirectory(prefix='athena-selection-') as directory:
    root=pathlib.Path(directory);file=root/'test.c';output=root/'test'
    file.write_text(stub+function('ae_tuple(')+function('select_flow(')+test)
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(file),'-o',str(output)],check=True)
    subprocess.run([str(output)],check=True)
