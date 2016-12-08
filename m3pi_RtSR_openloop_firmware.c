// Turning radius vs Spike rate (open loop tuning)
// JH@KrappLab
// 2016-12-08

#include "mbed.h"
#include "m3pi.h"

#define VMAX 0.4
#define VMIN 0

#define P_TERM 1
#define I_TERM 0
#define D_TERM 20

m3pi m3pi; 

DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);
DigitalOut led4(LED4);
DigitalOut pulse(p5);

void time_return1(void);
void time_return2(void);
void sin_move(float,float,float);
void robot_stop (void);
void go_straight_withcount(void);
void go_straight(void);
void go_straight_withoutturn();

float vR = VMAX;
float vr = 0;
      
int return_factor = 1;  //
float threshold = 0.35; //

////////////////////////////////////////////

int main(){
    
    float R = 2; 
    
    if(R == 2)
    {
        vR = VMAX;
        vr = 0;
    }
    else
    {
        float k = R/(R-2);  // k = vR/vr;
        vr = vR/k;
    }
    
    m3pi.locate(0,1);
    m3pi.printf("KrappLab");
    m3pi.sensor_auto_calibrate(); 
    wait(0.2);
    
    //int procflag=0; // process flag
    // t.start();   
    while (1)
    {  
        float position = m3pi.line_position();
     
        go_straight();

        go_straight_withcount();
             
        sin_move(vR,vr,threshold);
     
        go_straight_withoutturn();
        
        robot_stop();
                
    } 
}
   
///////////////////////////////////////////////////////

void robot_stop()
{
    while(1)
    {
        m3pi.stop();
    }    
} 

/////////////////////////////////////////////////////
    
void sin_move(float VR, float Vr, float th)
{
          
    float flag = 1;
            
    while(1)
    {
        float position = m3pi.line_position();
        
        if(-1.0<=position && position<-0.5) 
        {
            led1 = 0;led2 = 0; led3 = 0;led4 = 1;
        }
        if(-0.5<=position && position <0.0)
        {
            led1 = 0;led2 = 0;led3 = 1;led4 = 1;
        }
        if(0.0<=position && position<0.5)
        {
            led1 = 0;led2 = 1; led3 = 1;led4 = 1;
        }
        if(0.5<=position && position <1.0)
        {
            led1 = 1;led2 = 1; led3 = 1;led4 = 1;
        }
    
        if (flag == 1.0)
        {
            m3pi.left_motor(VR);
            m3pi.right_motor(Vr);
            pulse=1;
        }
        else
        {  
            m3pi.left_motor(Vr);
            m3pi.right_motor(VR);
            pulse=0;
        }
        
        if(position < -1*th)
        {
            flag = 1.0;
        }
        
        if(position > th)
        {
            flag = 0.0;
        } 
        
        if (position <= -0.95 || position >= 0.95)
        {
            pulse=0;
            time_return1();
            break;  
        }
    }
} 

////////////////////////////////////////////////////////////////////

void time_return1()
{
    led1 = 0;led2 = 0; led3 = 0;led4 = 0;
    m3pi.stop();
    
    while(1)
    {
        led1 = 0;led2 = 1; led3 = 1;led4 = 0;
        float position = m3pi.line_position();
        led1 = 1;led2 = 0;
        led3 = 0;led4 = 1;
        m3pi.left_motor(-VMAX);
        m3pi.right_motor(VMAX);
    
        if(position >= -0.3 && position <= 0.3)
        {
            break;
        }
    }
}

//////////////////////////////////////////////////////////////////////////////////////////

void go_straight_withcount(){
    float right;
    float left;
    float current_pos_of_line = 0.0;
    float previous_pos_of_line = 0.0;
    float derivative,proportional,integral = 0;
    float power;
    float speed = VMAX;
    long count=1; 
    
    while (1)
    {
        if (count > 100 )
        {
            count = 0;
            break;
        }
        else
        {
            current_pos_of_line = m3pi.line_position();        
            proportional = current_pos_of_line;
            derivative = current_pos_of_line - previous_pos_of_line;
            integral += proportional;
            previous_pos_of_line = current_pos_of_line;
            power = (proportional * (P_TERM) ) + (integral*(I_TERM)) + (derivative*(D_TERM)) ; 
            right = speed+power;
            left  = speed-power;
            if (right < VMIN)
                right = VMIN;
            else if (right > VMAX)
                right = VMAX;
                
            if (left < VMIN)
                left = VMIN;
            else if (left > VMAX)
                left = VMAX;
                
            m3pi.left_motor(left);
            m3pi.right_motor(right);
            count++;
        }
    }
}

//////////////////////////////////////////////////////////////////////

void go_straight()
{
    float right;
    float left;
    float current_pos_of_line = 0.0;
    float previous_pos_of_line = 0.0;
    float derivative,proportional,integral = 0;
    float power;
    float speed = VMAX;
//  long count; 
    
    while (1)
    {    
        current_pos_of_line = m3pi.line_position();        
        proportional = current_pos_of_line;
        derivative = current_pos_of_line - previous_pos_of_line;
        integral += proportional;
        previous_pos_of_line = current_pos_of_line;
        power = (proportional * (P_TERM) ) + (integral*(I_TERM)) + (derivative*(D_TERM)) ; 
        right = speed+power;
        left  = speed-power;
        if (right < VMIN)
            right = VMIN;
        else if (right > VMAX)
            right = VMAX;
            
        if (left < VMIN)
            left = VMIN;
        else if (left > VMAX)
            left = VMAX;
            
        m3pi.left_motor(left);
        m3pi.right_motor(right);
      
        if (current_pos_of_line <= -0.95 || current_pos_of_line >= 0.95)
        {
            time_return2();
            break;
        }
    }
}
        
////////////////////////////////////////////////////////////////////////////////////

void go_straight_withoutturn()
{   
    float right;
    float left;
    float current_pos_of_line = 0.0;
    float previous_pos_of_line = 0.0;
    float derivative,proportional,integral = 0;
    float power;
    float speed = VMAX;
//  long count; 
    
    while (1)
    {    
        current_pos_of_line = m3pi.line_position();        
        proportional = current_pos_of_line;
        derivative = current_pos_of_line - previous_pos_of_line;
        integral += proportional;
        previous_pos_of_line = current_pos_of_line;
        power = (proportional * (P_TERM) ) + (integral*(I_TERM)) + (derivative*(D_TERM)) ; 
        right = speed+power;
        left  = speed-power;
        if (right < VMIN)
            right = VMIN;
        else if (right > VMAX)
            right = VMAX;
            
        if (left < VMIN)
            left = VMIN;
        else if (left > VMAX)
            left = VMAX;
            
        m3pi.left_motor(left);
        m3pi.right_motor(right);
        
        if (current_pos_of_line <= -0.95 || current_pos_of_line >= 0.95)
        {
            break; 
        }
    }
}

////////////////////////////////////////////////

void time_return2()
{
    led1 = 0;led2 = 0; led3 = 0;led4 = 0;
    m3pi.stop();
    
    while(1)
    {
        led1 = 0;led2 = 1; led3 = 1;led4 = 0;
        float position = m3pi.line_position();
        led1 = 1;led2 = 0;
        led3 = 0;led4 = 1;
        m3pi.left_motor(VMAX);
        m3pi.right_motor(-VMAX);
        if(position >= -0.3 && position <= 0.3)
        {
            break;
        }
    } 
}

///////////// End of Code //////////////////
