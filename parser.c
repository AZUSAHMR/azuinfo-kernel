#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <memory.h>
#include <math.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/types.h>

//#define PARSER_N 2
#define PARSER_N 1

//const char * parser[PARSER_N] = {"sdvx.py","popn.py"};
const char * parser[PARSER_N] = {"sdvx.py"};

void * thread(void * arg){
	char * cmd = (char *)arg;
	system(cmd);
	free(cmd);
}

int main(int argn,char ** argv){
	char * session = argv[1];
	char * user = argv[2];
	int flag = atoi(argv[3]);

	int n = 0;
	pthread_t tid[PARSER_N];

	for(int i=0;i<PARSER_N;i++){
		int target = pow(2,i);

		if((flag&target)==target){
			char * cmd = (char *)malloc(sizeof(char)*256);
			sprintf(cmd,"python3 %s %s %s",parser[i],session,user);
			pthread_create(&tid[n++],NULL,thread,(void *)cmd);
		}
	}

	for(int i=0;i<n;i++)
		pthread_join(tid[i],NULL);

	return 0;
}
