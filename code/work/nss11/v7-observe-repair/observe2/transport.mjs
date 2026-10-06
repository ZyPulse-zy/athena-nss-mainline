import zlib from 'node:zlib';
import crypto from 'node:crypto';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
export const MAX_EXEC_BYTES=9000, DIRECT_BYTES=8000, MAX_RAW_BYTES=65536;
function text(source){if(typeof source!=='string'||source.includes('\0'))throw Error('Transport requires NUL-free text');if(Buffer.byteLength(source)>MAX_RAW_BYTES)throw Error('Transport raw length refused');}
// Same RAM/length/SHA-before-exec wrapper as the independently tested read-only prototype.
export function capsule(source){
 text(source);
 const sourceHash=sha(source),delim='NSS11_PAYLOAD_'+sourceHash,token='__NSS11_EXEC_RC_'+sourceHash+'__';
 if(source.split('\n').includes(delim))throw Error('Transport heredoc delimiter collision');
 const body="/bin/sh <<'"+delim+"'\n"+source+'\n'+delim+"\nnss11_rc=$?\nprintf '\\n"+token+"%s\\n' \"$nss11_rc\" >&2\nexit \"$nss11_rc\"\n";
 const bytes=Buffer.from(body),hash=sha(bytes),marker='__NSS11_DECODE_END_'+sourceHash+'__',b64=zlib.gzipSync(bytes,{level:9}).toString('base64');
 const command="set -u\nLC_ALL=C;export LC_ALL\nnss11_data=$(lua -e 'io.write(assert(require(\"nixio\").bin.b64decode([["+b64+"]])))' | /bin/gzip -dc && printf '%s' '"+marker+"') || exit 73\ncase \"$nss11_data\" in *"+marker+") ;; *) exit 74;; esac\nnss11_data=${nss11_data%"+marker+"}\ntest \"$(printf '%s' \"$nss11_data\" | wc -c)\" -eq "+bytes.length+" || exit 75\ntest \"$(printf '%s' \"$nss11_data\" | sha256sum | cut -d' ' -f1)\" = "+hash+" || exit 76\nprintf '%s' \"$nss11_data\" | /bin/sh\n";
 if(Buffer.byteLength(command)>MAX_EXEC_BYTES||bytes.length>MAX_RAW_BYTES)throw Error('Transport length refused');
 return{command,token,sourceHash,capsuleHash:hash,bytes:bytes.length,execBytes:Buffer.byteLength(command)};
}
export function encode(source){text(source);return Buffer.byteLength(source)>DIRECT_BYTES?capsule(source):{command:source,token:null,execBytes:Buffer.byteLength(source)};}
export function receipt(result,encoded){
 if(!encoded.token)return result;
 if(typeof result.stdout!=='string'||typeof result.stderr!=='string'||!Number.isInteger(result.code))throw Error('Transport missing execution result');
 const re=new RegExp('\\n'+encoded.token+'(0|[1-9][0-9]{0,2})\\n$'),m=result.stderr.match(re);
 if(!m||result.stderr.split(encoded.token).length!==2||Number(m[1])>255||Number(m[1])!==result.code)throw Error('Transport terminal receipt missing or mismatched (code '+result.code+')');
 return{...result,stderr:result.stderr.slice(0,m.index)};
}
export function capabilityProbe(){
 const known='NSS11_NATIVE_DECODE_CAPABILITY\n',b64=zlib.gzipSync(Buffer.from(known),{level:9}).toString('base64'),hash=sha(known);
 return "set -eu\nfor nss11_tool in lua gzip wc sha256sum cut sh; do command -v \"$nss11_tool\" >/dev/null; done\nlua -e 'assert(type(require(\"nixio\").bin.b64decode)==\"function\")'\nnss11_cap=$(lua -e 'io.write(assert(require(\"nixio\").bin.b64decode([["+b64+"]])))' | /bin/gzip -dc && printf '%s' '__NSS11_CAP_END__')\ncase \"$nss11_cap\" in *__NSS11_CAP_END__) ;; *) exit 74;; esac\nnss11_cap=${nss11_cap%__NSS11_CAP_END__}\ntest \"$(printf '%s' \"$nss11_cap\" | wc -c)\" -eq "+Buffer.byteLength(known)+"\ntest \"$(printf '%s' \"$nss11_cap\" | sha256sum | cut -d' ' -f1)\" = "+hash+"\nprintf '%s\\n' 'NSS11_NATIVE_TRANSPORT_CAPABILITY_PASS'\n";
}
