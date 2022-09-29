/*Trying to get simple code to work, using Interrupt*/
#include "mbed.h"
#include "m3pi.h"
#include "InterruptIn.h"
m3pi m3pi;
InterruptIn input(p5);
DigitalOut led1(LED1);
DigitalOut led2(LED2);
float speed=0.3;
int RTurnflag=1;
/* ====================================================== */
void collision_avoidance()
{    
    __disable_irq();
    led2=1;
    m3pi.stop();
    m3pi.left_motor(-speed);
    m3pi.right_motor(speed);
    wait(0.2);
    led2=0;
    //m3pi.stop();
    __enable_irq();
}
                            
int main() //main function
{    
    input.rise(&collision_avoidance);
    while(1)    //robot moving oscillatory forward    
    {
        if (RTurnflag==1)        
        {            
            led1 = 1;            
            m3pi.stop();            
            m3pi.left_motor(speed);            
            m3pi.right_motor(0);            
            RTurnflag=0;            
            wait(0.36);        //this one is longer for the bias        
        }
        else        
        {            
            m3pi.stop();            
            m3pi.left_motor(0);            
            m3pi.right_motor(speed);            
            RTurnflag = 1;            
            wait(0.3);        
        }//wait(0.02);    
    }//end of while
}//end of main
