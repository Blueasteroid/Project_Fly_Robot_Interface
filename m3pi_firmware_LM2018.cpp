/* Closed-loop algorithm: LM2018 */
/* JH@KrappLab */
/* 2018-09-26 V2 : modified version */

#include "mbed.h"
#include "m3pi.h"
m3pi m3pi;

AnalogIn ainL(p20);
DigitalOut led1(LED1);
DigitalOut led2(LED2);

float speed=0.3;
float Rturnduration=0.02;
//float Lturnduration=0.035;
int value=0;        //trigger flag of collision avoidance
long timecount=0;   //time period of left wheel
long timecount2=0;  //time period of right wheel
long Numspike=0;    //instantaneous mean spike rate
int RTurnflag=1;    
int Lturnflag=0;
//int SpikerateThrehold=50;
float avgspike;
int pre_sigL=0;
int sigL;
float threL;
Ticker fly_robot;
float ADC_Fs = 5000;    //Hz ... ADC sampling rate (Note: it will jam UART baudrate when above 5000.)
int SpikerateThrehold=50;

/* ====================================================== */

void fly_robot_interface() //interrupt sub-routine for spike rate updating
{   
    if(RTurnflag==1)
    {
        sigL = (ainL >= threL);
        if(sigL == 1 && pre_sigL == 0)
        {
            Numspike++;
            led1=1;
        }
        else
        {
            led1=0;
        }
        pre_sigL = sigL; 
        value=0;
        timecount++;
    } 
    else if(Lturnflag==1)
    {
        //avgspike=Numspike/(timecount*200*10^-6);
        //if(avgspike > SpikerateThrehold)
        if(Numspike>SpikerateThrehold)
        {
            value=1;
        } 
        Numspike=0;
        timecount2++;
    }
}
         
int main() //main function
{
    threL = 2.7/3.3; //voltage threshold of spike
    fly_robot.attach_us(&fly_robot_interface, 200); //call ISR
    while(1)    //robot moving oscillatory forward, and bias to one side
    {      
        if (RTurnflag==1)
        {
            m3pi.left_motor(speed);
            m3pi.right_motor(0);
            if (timecount>=1750)
            {
                m3pi.stop();timecount=0;
                RTurnflag=0;Lturnflag=1;
            }
        }
        if (Lturnflag==1)
        {
            if (value==1) // trigger of collision avoidance
            {    
                led2=1;
                m3pi.left_motor(-speed);
                m3pi.right_motor(speed);
                wait(0.02);
                m3pi.stop();
                value=0;
            } 
            else
            {
                led2=0;
            }
            m3pi.left_motor(0);
            m3pi.right_motor(speed);
            if (timecount2>=1000)
            {
                m3pi.stop();timecount2=0;
                Lturnflag=0;
                RTurnflag=1;   
            }//end of if       
        }//end of if
    }//end of while
}//end of main
