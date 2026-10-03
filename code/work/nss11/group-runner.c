// SPDX-License-Identifier: GPL-2.0
// Bound a frozen mutation helper and its descendants while inherited locks stay held.
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <poll.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
static volatile sig_atomic_t interrupted;
static void on_signal(int n){interrupted=n;}
static long long millis(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return -1;return (long long)t.tv_sec*1000+t.tv_nsec/1000000;}
static void pause_ms(int n){struct timespec t={n/1000,(n%1000)*1000000L};while(nanosleep(&t,&t)&&errno==EINTR){} }
static int child_exited(pid_t p,siginfo_t *i){memset(i,0,sizeof(*i));int r=waitid(P_PID,(id_t)p,i,WEXITED|WNOHANG|WNOWAIT);if(r<0)return -1;return i->si_pid==p;}
int main(int argc,char **argv){
 if(argc<3){fputs("group-runner: seconds program arguments...\n",stderr);return 2;}
 char *end;long seconds=strtol(argv[1],&end,10);if(*end||seconds<1||seconds>6||argv[2][0]!='/')return 2;
 if(prctl(PR_SET_CHILD_SUBREAPER,1,0,0,0)){perror("subreaper");return 3;}
 struct sigaction a={0};a.sa_handler=on_signal;sigemptyset(&a.sa_mask);
 if(sigaction(SIGTERM,&a,0)||sigaction(SIGINT,&a,0)||sigaction(SIGHUP,&a,0))return 3;
 signal(SIGPIPE,SIG_IGN);
 int ready[2],ack[2];if(pipe2(ready,O_CLOEXEC)||pipe2(ack,O_CLOEXEC))return 3;
 pid_t child=fork();if(child<0)return 3;
 if(child==0){
  close(ready[0]);close(ack[1]);
  signal(SIGTERM,SIG_DFL);signal(SIGINT,SIG_DFL);signal(SIGHUP,SIG_DFL);signal(SIGPIPE,SIG_DFL);
  if(setsid()<0)_exit(126);
  char byte='R';if(write(ready[1],&byte,1)!=1)_exit(126);close(ready[1]);
  if(read(ack[0],&byte,1)!=1||byte!='A')_exit(125);
  close(ack[0]);
  execv(argv[2],argv+2);_exit(127);
 }
 close(ready[1]);close(ack[0]);
 int acknowledged=0,reason=0;siginfo_t status;long long boot_deadline=millis()+1000;
 while(!interrupted&&millis()<boot_deadline){
  struct pollfd p={ready[0],POLLIN,0};int r=poll(&p,1,20);if(r<0&&errno!=EINTR){reason=3;break;}
  if(r>0){char byte;if(read(ready[0],&byte,1)==1&&byte=='R'){acknowledged=1;break;}reason=3;break;}
 }
 close(ready[0]);
 if(!acknowledged||interrupted){
  // Our unreaped direct child PID cannot be reused. EOF also prevents late exec.
  close(ack[1]);kill(child,SIGKILL);while(waitpid(child,0,0)<0&&errno==EINTR){}
  return interrupted?128+interrupted:(reason?reason:124);
 }
 char byte='A';if(write(ack[1],&byte,1)!=1){close(ack[1]);kill(-child,SIGKILL);while(waitpid(child,0,0)<0&&errno==EINTR){}return 3;}close(ack[1]);
 long long deadline=millis()+seconds*1000;int complete=0;
 while(!interrupted&&millis()<deadline){
  int r=child_exited(child,&status);if(r<0){reason=3;break;}if(r){complete=1;break;}pause_ms(20);
 }
 if(interrupted)reason=128+interrupted;else if(!complete&&!reason)reason=124;
 // Keep the leader unreaped through BOTH signals: no PGID reuse window.
 if(kill(-child,SIGTERM)<0&&errno!=ESRCH)reason=3;
 pause_ms(150);
 if(kill(-child,SIGKILL)<0&&errno!=ESRCH)reason=3;
 int lead_status=0,lead_seen=0;
 for(;;){
  int st;pid_t p=waitpid(-1,&st,0);
  if(p>0){if(p==child){lead_status=st;lead_seen=1;}continue;}
  if(errno==EINTR)continue;
  if(errno==ECHILD)break;
  perror("reap");return 3;
 }
 // All descendants have exited before any inherited FD8/FD9 is released.
 if(reason)return reason;
 if(!lead_seen)return 3;
 if(WIFEXITED(lead_status))return WEXITSTATUS(lead_status);
 if(WIFSIGNALED(lead_status))return 128+WTERMSIG(lead_status);
 return 3;
}
