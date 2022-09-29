///////////////////////////////////////////////////////////////////////
// m3pi line following and U turn on at the end of the line spot script
// JH @ Krapp Lab
// 12/09/2014
///////////////////////////////////////////////////////////////////////

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
     m3pi.printf("PID Crk");
 
     wait(1.0);
 
     float right = 0;
     float left = 0;
     float position_of_line = 0.0;
     float prev_pos_of_line = 0.0;
     float derivative,proportional;
     float integral = 0;
     float power = 0;
     m3pi.sensor_auto_calibrate();
     float speed = MAX;
     
     int dirCrook = 0;
     int robotStat = 0;
     
//     led1=1;
//     led2=1;
//     led3=1;
//     led4=1;

/*
    while (1) {   
        m3pi.cls();
        m3pi.printf("%f",m3pi.line_position());
        wait(0.1);
    }
*/
     wait(0.5);
     
     while (1) {
         
         // Get the position of the line.
         position_of_line = m3pi.line_position();
         
         //m3pi.cls();
         //m3pi.printf("%f",position_of_line);
         //wait(0.001);
    
        if (abs(position_of_line) >= 0.95 && robotStat == 0) {
                   
            if (dirCrook == 0)
            {
                robotStat = 3;
                dirCrook = 1;
            }
            else
            {
                robotStat = 4;
                dirCrook = 0;  
            }
            
            m3pi.forward((left+right)/4);
            wait(0.1); 
            m3pi.forward((left+right)/8);
            wait(0.1); 
            m3pi.stop();
            wait(0.1);   
        }
        if (abs(position_of_line) <= 0.1 ) {
            robotStat = 0;
        }
    
          
        if(robotStat == 3){
            m3pi.right(MAX);
            //m3pi.left_motor(-speed);
            //m3pi.cls();
            //m3pi.printf("Crook R");
        }  
        else if(robotStat == 4){
            m3pi.left(MAX);
            //m3pi.left_motor(-speed);
            //m3pi.cls();
            //m3pi.printf("Crook L");
        }  
        else{
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
             {right = MIN;}
         else if (right > MAX)
             {right = MAX;}
             
         if (left < MIN)
             {left = MIN;}
         else if (left > MAX)
             {left = MAX;}
     
        // set speed 
         m3pi.left_motor(left);
         m3pi.right_motor(right);
        
        //m3pi.cls();
        //m3pi.printf("PID FWD");
        }
        

        
        
/*
        if (position_of_line <= 0.2 && position_of_line >=-0.2 )
            {led1=1;dout8=1;}
        else
            {led1=0;dout8=0;}
*/     
       
     }
}
