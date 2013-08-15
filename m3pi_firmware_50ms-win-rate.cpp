/*----------------------------------------------*/
// m3pi firmware 
// Jiaqi Huang (Imperial College London)
//
// Ver_2013-08-14: ADC 5kHz, ISI rate input
// Ver_2013-08-15: ADC 5kHz, 50ms window rate input
/*----------------------------------------------*/
#include "mbed.h"
#include "m3pi.h"

m3pi m3pi(p23,p9,p10);

DigitalOut dout11(p11);
DigitalOut dout12(p12);
DigitalOut dout13(p13);
DigitalOut dout14(p14);
DigitalOut dout15(p15);
DigitalOut dout16(p16);
DigitalOut dout17(p17);
DigitalOut dout18(p18);
//AnalogOut signal(p18);
AnalogIn ainL(p19);
AnalogIn ainR(p20);
DigitalOut dout21(p21);
DigitalOut dout22(p22);
DigitalOut dout23(p23);
DigitalOut dout24(p24);
DigitalOut dout25(p25);
DigitalOut dout26(p26);
DigitalOut dout27(p27);
DigitalOut dout28(p28);
DigitalOut dout29(p29);
DigitalOut dout30(p30);

DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);
DigitalOut led4(LED4);


int pre_sigL, pre_sigR;
int sigL, sigR;

float threL, threR;
float counterL = 0, counterR = 0;
float speedL = 0, speedR = 0;

Ticker fly_robot;

float ADC_Fs = 5000; //Hz ... ADC sampling rate (Note: it will jam UART baudrate when above 5000.)

int rasterL[250]={0};
int idxL=0;
int rasterR[250]={0};
int idxR=0;

/* ====================================================== */

void fly_robot_interface() 
{
    sigL = (ainL >= threL);// ? 1 : 0;
    sigR = (ainR >= threR);// ? 1 : 0;
    
    led1 = sigL;
    led4 = sigR;
    
    rasterL[idxL] = (sigL == 1 && pre_sigL == 0);// ? 1 : 0;
    idxL = (idxL++) % 250;
    rasterR[idxR] = (sigR == 1 && pre_sigR == 0);// ? 1 : 0;
    idxR = (idxR++) % 250;    
    
    counterL=0;
    counterR=0;
    for (int i=0; i<250; i++)
    {
        //counterL += rasterL[i]; 
        if (rasterL[i]){counterL ++;}
        //counterR += rasterR[i]; 
        if (rasterR[i]){counterR ++;}
    }
    /*
    for (int i=0; i<250; i++)
    {
        
    }
    */
/*    
    //... time out
    if (counterL >= 2000)
    {
        counterL = 2000;
        led2 = 0;   //...debug
        speedL = 0;
    }
    if (counterR >= 2000)
    {
        counterR = 2000;
        led3 = 0;   //...debug
        speedR = 0;
    } 
*/
    // =========================== control law ===
    
    if ((counterL * 20.0) >= 100.0)
    {
        led2 = 1;   //...debug
        speedL = (counterL * 20.0 - 100.0)/300.0;
    }
    else
    {
        led2 = 0;   //...debug  
        speedL = 0.0;   
    }
    
    if ((counterR * 20.0) >= 100.0)
    {
        led3 = 1;   //...debug
        speedR = (counterR * 20.0 - 100.0)/300.0;
    }
    else
    {
        led3 = 0;   //...debug   
        speedR = 0.0; 
    }  
    
/*
    if (sigL == 1 && pre_sigL == 0)
    {
        if (counterL < 13)
        {
            speedL = 0;
            led2 = 0;   //...debug
        }
        if (counterL >= 13 && counterL <= 50)
        {
            //speedL = ((1/(float(counterL)*(1/ADC_Fs))-100)/300);
            speedL = ((ADC_Fs/float(counterL))-100)/300;
            led2 = 1;   //...debug
            counterL = 0;
        }
        if (counterL > 50 && counterL <= 500)
        {
            speedL = 0;
            led2 = 0;   //...debug
            counterL = 0;
        }
        if (counterL > 500)
        {
            counterL = 0;
        }
    }

    if (sigR == 1 && pre_sigR == 0)
    {
        if (counterR < 13)
        {
            speedR = 0;
            led3 = 0;   //...debug
        }
        if (counterR >= 13 && counterR <= 50)
        {
            speedR = ((ADC_Fs/float(counterR))-100)/300;
            led3 = 1;   //...debug
            counterR = 0;
        }
        if (counterR > 50 && counterR <= 500)
        {
            speedR = 0;
            led3 = 0;   //...debug
            counterR = 0;
        }
        if (counterR > 500)
        {
            counterR = 0;
        }
    }
*/
    pre_sigL = sigL;
    pre_sigR = sigR;   
}

void motor_control()
{
    m3pi.left_motor(speedL);
    //m3pi.printf(speedL);
    m3pi.right_motor(speedR);
    //m3pi.printf(speedR);
}

int main() 
{
    threL = 2.7/3.3;
    threR = 2.7/3.3;

    //fly_robot.attach_us(&fly_robot_interface, int(1/(ADC_Fs/1000000)));  //... sampling tick 200 us
    fly_robot.attach_us(&fly_robot_interface, 200); 

    while(1)
    {
        motor_control();   
        wait(0.05);
        //wait(1);
    }
}
