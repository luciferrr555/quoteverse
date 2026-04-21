#include <stdio.h>
#include <stdlib.h>

#define MAX 5

int queue[MAX];
int front = -1, rear = -1;
int val;

void enque(int val)
{
    if (front ==(rear+1)%MAX)
    {
        printf("FULL");
        return;
    }
    rear=(rear+1)%5;
    queue[rear]=val;
    if(front==-1)
        front=0;    
}
void deque()
{
    if(front==-1)
    {
        printf("EMPTY");
        return;
    }
    printf("%d",queue[front]);
    front=(front+1)%5;
}

int main()
{
    int choice;
    do
    {
        printf("1.ENQUEUE\n2.DEQUEUE\n3.EXIT\n");
        scanf("%d",&choice);
        switch(choice)
        {
            case 1:
                printf("ENTER THE VALUE : ");
                scanf("%d",&val);
                enque(val);
                break;
            case 2:
                deque();
                break;
            case 3:
                exit(0);
            default:
                printf("INVALID CHOICE\n");
        }
    }while(choice!=3);
}