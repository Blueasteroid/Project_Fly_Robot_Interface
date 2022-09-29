////////////////////////////////////////////////////
// m3pi line following and U turn on spot script
// JH @ Krapp Lab
// 12/09/2014
// mod:
// 2019-03-06: line following with event triggering
////////////////////////////////////////////////////

#include "mbed.h"
#include "m3pi.h"
//#include "SerialRPCInterface.h"

DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);
DigitalOut led4(LED4);

BusOut leds(LED1,LED2,LED3,LED4);
m3pi m3pi(p23,p9,p10);

#define MAX 0.3     //<----- tuning the max speed (MAX = 1.0)
#define MIN 0
 
#define P_TERM 1
#define I_TERM 0
#define D_TERM 20

#define SEND_CALIBRATED_SENSOR_VALUES 0x87

#define SEND_SIGNATURE 0x81
#define SEND_RAW_SENSOR_VALUES 0x86
#define SEND_TRIMPOT 0xB0
#define SEND_BATTERY_MILLIVOLTS 0xB1
#define DO_PLAY 0xB3
#define PI_CALIBRATE 0xB4
#define DO_CLEAR 0xB7
#define DO_PRINT 0xB8
#define DO_LCD_GOTO_XY 0xB9
#define LINE_SENSORS_RESET_CALIBRATION 0xB5
#define SEND_LINE_POSITION 0xB6
#define AUTO_CALIBRATE 0xBA
#define SET_PID 0xBB
#define STOP_PID 0xBC
#define M1_FORWARD 0xC1
#define M1_BACKWARD 0xC2
#define M2_FORWARD 0xC5
#define M2_BACKWARD 0xC6

int sensor[5]={0};
const char tune[] PROGMEM = 
  "! T120O5L16agafaea";
  
// RN42 module defaults to 115,200 and is on p28,p27
// SerialRPCInterface Interface(p28, p27, 115200);
// m3pi m3pi(p23,p9,p10);

int readsensor (int *sensor)
{   
    m3pi.putc(SEND_CALIBRATED_SENSOR_VALUES);  
    sensor[0] = m3pi.getc();
    sensor[0] += m3pi.getc() << 8;
    sensor[1] = m3pi.getc();
    sensor[1] += m3pi.getc() << 8;
    sensor[2] = m3pi.getc();
    sensor[2] += m3pi.getc() << 8;
    sensor[3] = m3pi.getc();
    sensor[3] += m3pi.getc() << 8;
    sensor[4] = m3pi.getc();
    sensor[4] += m3pi.getc() << 8;
  
    if(sensor[1] < 100 && sensor[2] < 100 && sensor[3] < 100)
    {
        // There is no line visible ahead, and we didn't see any
        // intersection.  Must be a dead end.
        //led2=1;
        //led3=1;
        return 0;
    }
    else if(sensor[0] > 200 || sensor[4] > 200)
    {
        // Found an intersection.
        //led1=1;
        //led4=1;
        return 1;
    }
        
    return 0;
}

int playBuzzer (char* tune) {
    m3pi.putc(DO_PLAY);  
    m3pi.putc(strlen(tune));       
    for (int i = 0 ; i < strlen(tune) ; i++) {
        m3pi.putc(tune[i]); 
    }
    return(0);
}

////////////////////////////////////////////////////
////////////////////////////////////////////////////
////////////////////////////////////////////////////

int main() 
{
    m3pi.locate(0,1);
    m3pi.printf("SPD:MAX");
 
    wait(1);
 
    float right = 0;
    float left = 0;
    float position_of_line = 0.0;
    float prev_pos_of_line = 0.0;
    float derivative,proportional;
    float integral = 0;
    float power = 0;
    float speed = MAX;
     
    int dirCrook = 0;
    int robotStat = 0;

    leds = 1;
    m3pi.sensor_auto_calibrate();
    leds = 0;
    wait(0.5);
/*
    while (1) {   
        m3pi.cls();
        m3pi.printf("%f",m3pi.line_position());
        wait(0.1);
    }//...debug for ir sensors
*/
    while (1) 
    { 
        led1=0;led2=0;led3=0;led4=0;
//        if (readsensor(sensor)==1){   led1=1;  }  //...event trigger by ground marker
        
        // Get the position of the line.
        position_of_line = m3pi.line_position();
         
        //m3pi.cls();
        //m3pi.printf("%f",position_of_line);
        //wait(0.001);
    
        if (abs(position_of_line) >= 0.95 && robotStat == 0) 
        {
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
        if (abs(position_of_line) <= 0.1 ) 
        {
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
            if (readsensor(sensor)==1){   led1=1;  } //...event trigger by ground marker
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
     
            m3pi.left_motor(left);
            m3pi.right_motor(right);
        }
    }
}
