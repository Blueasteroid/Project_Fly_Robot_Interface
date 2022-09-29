//#include "mbed.h"

#include "mbed.h"
#include "m3pi.h"
//#include "SerialRPCInterface.h"

DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);
DigitalOut led4(LED4);

//DigitalOut dout8(p8);

BusOut leds(LED1,LED2,LED3,LED4);
m3pi m3pi(p23,p9,p10);


#define MAX 0.3     //<----- tuning the max speed (MAX = 1.0)
#define MIN 0
 
 
#define P_TERM 1
#define I_TERM 0
#define D_TERM 20


// RN42 module defaults to 115,200 and is on p28,p27
//SerialRPCInterface Interface(p28, p27, 115200);

//m3pi m3pi(p23,p9,p10);

int main() 
{
     m3pi.locate(0,1);
     m3pi.printf("Line Flw");
 
     wait(2.0);
 
     float right;
     float left;
     float position_of_line = 0.0;
     float prev_pos_of_line = 0.0;
     float derivative,proportional;
     float integral = 0;
     float power;
     m3pi.sensor_auto_calibrate();
     float speed = MAX;
     
//     led1=1;
//     led2=1;
//     led3=1;
//     led4=1;
     
     while (1) {
 
         // Get the position of the line.
         position_of_line = m3pi.line_position();
         proportional = position_of_line;
         // Compute the derivative
         derivative = position_of_line - prev_pos_of_line;
         // Compute the integral
         integral += proportional;
         // Remember the last position.
         prev_pos_of_line = position_of_line;
         // Compute
         power = (proportional * (P_TERM) ) + (integral*(I_TERM)) + (derivative*(D_TERM)) ;
         
         //    Compute new speeds   
         right = speed+power;
         left  = speed-power;
         // limit checks
         if (right < MIN)
             right = MIN;
         else if (right > MAX)
             right = MAX;
             
         if (left < MIN)
             left = MIN;
         else if (left > MAX)
             left = MAX;
             
        // set speed 
         m3pi.left_motor(left);
         m3pi.right_motor(right);
 
/*
        if (position_of_line <= 0.2 && position_of_line >=-0.2 )
            {led1=1;dout8=1;}
        else
            {led1=0;dout8=0;}
*/            
     }

    
}
