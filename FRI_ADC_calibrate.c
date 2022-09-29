#include "mbed.h"
#include "m3pi.h"

m3pi m3pi(p23,p9,p10);

DigitalOut dout1(p15);
DigitalOut dout2(p16);
DigitalOut dout3(p17);
DigitalOut dout4(p18);
//AnalogOut signal(p18);
AnalogIn ainL(p19);
AnalogIn ainR(p20);
DigitalOut dout5(p21);
DigitalOut dout6(p22);
DigitalOut dout7(p23);
DigitalOut dout8(p24);
DigitalOut dout9(p25);
DigitalOut dout10(p26);
DigitalOut dout11(p27);
DigitalOut dout12(p28);
DigitalOut dout13(p29);
DigitalOut dout14(p30);


DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);
DigitalOut led4(LED4);

//m3pi m3pi(p23,p9,p10);

float maxspeedL = 0.5, maxspeedR = 0.5;
float counterL = 0, counterR = 0;

int pre_sigL,pre_sigR;
int sigL,sigR;
float deltaL,deltaR;
float threL,threR;

float speedL=0;
float speedR=0;

int main() 
{

    threL = 2.7/3.3;
    threR = 2.7/3.3;
    
    
    
    while (1)
    {
        //wait(0.00005);
        //wait_ms(0.05);
        wait_us(50);

//        led1 = (ainR > 0.2) ? 1 : 0;
//        led2 = (ainL > 0.4) ? 1 : 0;
//        led3 = (ainL > 0.6) ? 1 : 0;
//        led4 = (ainL > 0.8) ? 1 : 0;

        sigL = (ainL >= threL) ? 1 : 0;
        sigR = (ainR >= threR) ? 1 : 0;
        
        led1 = sigL;
        led4 = sigR;
        
        counterL = counterL + 1; 
        counterR = counterR + 1; 
        
        //===========================     
        //... Control law
        if (sigL == 1 && pre_sigL == 0)
        {
            if (counterL < 50){;}
            if (counterL >= 50 && counterL <= 200)
            {
                maxspeedL = 0.5; // ((1/(counterL*0.00005)-100)/300);
                deltaL = 0.001;
                led2 = 1;   //...debug
                counterL = 0;
            }
            if (counterL > 200 && counterL <= 2000)
            {
                deltaL = -0.001;
                led2 = 0;   //...debug
                counterL = 0;
            }
            if (counterL > 2000)
            {
                counterL = 0;
            }
        }
        
        if (sigR == 1 && pre_sigR == 0)
        {
            if (counterR < 50){;}
            if (counterR >= 50 && counterR <= 200)
            {
                maxspeedR = 0.5; // ((1/(counterR*0.00005)-100)/300);
                deltaR = 0.001;
                led3 = 1;   //...debug
                counterR = 0;
            }
            if (counterR > 200 && counterR <= 2000)
            {
                deltaR = -0.001;
                led3 = 0;   //...debug
                counterR = 0;
            }
            if (counterR > 2000)
            {
                counterR = 0;
            }
        }
        
        
        //... time out
        if (counterL >= 2000)
        {
            counterL = 2000;
            deltaL = -0.001;
        }
        if (counterR >= 2000)
        {
            counterR = 2000;
            deltaR = -0.001;
        }
        
        //... Speed limit
        if (speedL >= maxspeedL)
        {deltaL = -0.001;}
        if (speedR >= maxspeedR)
        {deltaR = -0.001;}  
        
        if (speedL <= 0 && deltaL<0)
        {deltaL = 0;}
        if (speedR <= 0 && deltaR<0)
        {deltaR = 0;} 
        
        //===========================
        
        speedL = speedL + deltaL;
        speedR = speedR + deltaR;
        
        m3pi.left_motor(speedL);
        m3pi.right_motor(speedR);
         
        pre_sigL = sigL;
        pre_sigR = sigR;        
              
    } 
}
