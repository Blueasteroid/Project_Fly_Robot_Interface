////////////////////////////////////////////////////////////////////////////////
// Turning radius vs Spike rate (open loop tuning)
// JH@KrappLab
// 2016-12-08: recompile from Naomi's version
// 2017-01-23: re-calibrate the vR/vr formula
// 2019-03-21: rewrite code, add white line, tuning of speed & frequency
// 2019-03-28: use sign of derivative of line position for sync signal (not done)
////////////////////////////////////////////////////////////////////////////////

#include "mbed.h"
#include "m3pi.h"

#define P_TERM 1
#define I_TERM 0
#define D_TERM 20

#define SEND_CALIBRATED_SENSOR_VALUES 0x87

m3pi m3pi; 

DigitalIn button(p21); //... manually select speed or frequency of turns

DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);
DigitalOut led4(LED4);
DigitalOut sync(p5);//(p23);
//DigitalOut sync_gnd(p22);

void spin_cw(void);
void spin_ccw(void);
void osc_fwd(float,float,float);
void robot_stop(void);
void go_straight_counting(long);
void go_straight(void);

float IR_threshold = 0.1; //L... 0.1 - 0.4(frontal infrared sensor)
float VMAX =         0.2; //V... 0.2 - 0.4


float VMIN = 0; 
float VMID = 0.3; 

float Rt=15;    //... turning radius
float Rr=5;     //... robot radius
float Ratio = Rt/Rr; //... Ratio of radii: R = Rt/Rr (turning radius / robot radius)
float vR = 0;    //... velocity of the faster wheel
float vr = 0;    //... velocity of the slower wheel



float flag_white_line = 1;  //... robot on a black line or white line
//float prev_pos = 0;

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
float line_position(int flag_white_line) //... add function for white track
{
    int sensor[5]={0};
    
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
  
    //return(sensor[2]);//...<< quick debug
    ////////////

    long avg = 0;
    int sum = 0; 
    int last_value = 0;
    int value;
    char online=0;
    
    for (int i=0;i<5;i++)
    {
        value = sensor[i];  //... on black line
        if ( flag_white_line ){value = 1000-sensor[i];} //... on white line
        if (value>200){online=1;}  //... on the track
        if (value>50)   //... threshold of data processing
        {
            avg += (long)(value)*(i*1000);
            sum += value;
        }
    }
    
    if (!online)    //... when offline, remember the last line position
    {
        if(last_value< 2000){return ((float)((0-2048.0)/2048.0));}    
        else{return ((float)((4000-2048.0)/2048.0));}
    }
    last_value =  avg/sum;
    return ((float)((last_value-2048.0)/2048.0));
    
}

int playBuzzer (char* tune) {
    m3pi.putc(DO_PLAY);  
    m3pi.putc(strlen(tune));       
    for (int i = 0 ; i < strlen(tune) ; i++) {
        m3pi.putc(tune[i]); 
    }
    return(0);
}

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

int main()
{
    button.mode(PullUp);
    //sync_gnd=0;
    ///////////////////////////// Test code ///   
    float test_flag = 0;
    if (test_flag)
    {
        m3pi.sensor_auto_calibrate();
        wait(0.2);
        while(1)    
        {
            //playBuzzer(">g32>>c32");
            playBuzzer(">g32");
            wait(1);
        }
        while(1)    
        {
            //float position = m3pi.line_position(); 
            float position = line_position(flag_white_line); 
            m3pi.locate(0,0);
            m3pi.printf("%05.2f",position);
            wait(0.5);
        }
    }
    
    ///////////////////////////// configure ///
    float conf_flag = 0;
    int mode_num = 0;
    if (conf_flag)
    {
        while(conf_flag)    
        {   
            if(!button)
            {
                mode_num++;
                mode_num = mode_num % 5;    
            } 
            
            if (mode_num == 0)
            {led1=0;led2=0;led3=0;led4=0;
            //VMAX=0.3;
            IR_threshold = 0.1;
            }
            if (mode_num == 1)
            {led1=1;led2=0;led3=0;led4=0;
            //VMAX=0.4;
            IR_threshold = 0.2;
            }
            if (mode_num == 2)
            {led1=0;led2=1;led3=0;led4=0;
            //VMAX=0.5;
            IR_threshold = 0.3;
            }
            if (mode_num == 3)
            {led1=0;led2=0;led3=1;led4=0;
            //VMAX=0.6;
            IR_threshold = 0.4;
            }
            if (mode_num == 4)
            {led1=0;led2=0;led3=0;led4=1;
            //VMAX=0.7;
            IR_threshold = 0.5;
            }
            
            conf_flag--;   
            wait(0.1);
        }
    }
    ///////////////////////////////////////////
    
    if(Ratio == 1)
    {
        vR = VMAX;
        vr = 0;
    }
    else
    {
        vR = VMAX;
        float k = (Ratio+1)/(Ratio-1);  
        vr = vR/k;
    }

    
    
    m3pi.locate(0,0);
    m3pi.printf("KrappLab");
    
    m3pi.sensor_auto_calibrate(); 
    wait(0.2);
    
    
    
    while (1)
    {  

     
        go_straight();
        playBuzzer(">g32");
        //wait(0.01);
        spin_cw();
        playBuzzer(">c32");
        //wait(0.01);
        go_straight_counting(100);
        //playBuzzer(">g32");
        //wait(0.01);
        osc_fwd(vR, vr, IR_threshold);
        playBuzzer(">g32");
        //wait(0.01);
        spin_ccw();
        playBuzzer(">c32");
        //wait(0.01);
        go_straight();
        playBuzzer(">g32");
        //wait(0.01);
        robot_stop();
        //playBuzzer(">g32");      
    } 
}

////////////////////////////////////////////////////////////////////////////////

void robot_stop()
{
    while(1)
    {
        m3pi.stop();
    }    
} 

////////////////////////////////////////////////////////////////////////////////

void osc_fwd(float VR, float Vr, float th)
{    
    float steer_flag = 1;
    int done_flag=0;
    
    while(1)
    {
        float position = line_position(flag_white_line);
        /*
        if (position-prev_pos>=0)
        {
            sync=1;
            led1=1;
        }
        else
        {
            sync=0;
            led1=0;
        }
        prev_pos = position;
        */
        
        if (steer_flag == 1.0 && done_flag ==0)
        {
            m3pi.left_motor(VR);
            m3pi.right_motor(Vr);
            sync=1;
            done_flag=1;
        }
        else if(steer_flag == 0 && done_flag ==0)
        {  
            m3pi.left_motor(Vr);
            m3pi.right_motor(VR);
            sync=0;
            done_flag =1;
        }
        
        if(position < -1*th)
        {
            steer_flag = 1.0;
            done_flag=0;
        }
        
        if(position > th)
        {
            steer_flag = 0.0;
            done_flag=0;
        } 
        
        if (position <= -0.95 || position >= 0.95)
        {
            sync=0;
            //time_return1();
            m3pi.left_motor(VMID/2);
            m3pi.right_motor(VMID/2);
            wait(0.05);
            m3pi.left_motor(VMID/4);
            m3pi.right_motor(VMID/4);
            wait(0.05);
            m3pi.stop(); 
            break;  
        }
    }
} 


////////////////////////////////////////////////////////////////////////////////

void go_straight_counting(long count){
    float right;
    float left;
    float current_pos_of_line = 0.0;
    float previous_pos_of_line = 0.0;
    float derivative,proportional,integral = 0;
    float power;
    float speed = VMID;
    //long count=1; 
    //sync=0;
    
    while(count)
    {
        current_pos_of_line = line_position(flag_white_line);        
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
        count--;
    }
}

////////////////////////////////////////////////////////////////////////////////

void go_straight()
{
    float right;
    float left;
    float current_pos_of_line = 0.0;
    float previous_pos_of_line = 0.0;
    float derivative,proportional,integral = 0;
    float power;
    float speed = VMID;
//  long count; 
    //sync=0;
    
    while (1)
    {    
        current_pos_of_line = line_position(flag_white_line);        
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
            //time_return2();
            
            m3pi.left_motor(left/2);
            m3pi.right_motor(right/2);
            wait(0.05);
            m3pi.left_motor(left/4);
            m3pi.right_motor(right/4);
            wait(0.05);
            m3pi.stop(); 
            
            break;
        }
    }
}
        
////////////////////////////////////////////////////////////////////////////////

void spin_cw()
{
    m3pi.stop();   
    float speed = VMID;
    while(1)
    {
        float position = line_position(flag_white_line);
        m3pi.left_motor(-speed);
        m3pi.right_motor(speed);
        //wait(0.1);
        
        if(position >= -0.3 && position <= 0.3)
        {
            break;
        }
    } 
}

void spin_ccw()
{
    m3pi.stop();
    float speed = VMID;
    while(1)
    {
        float position = line_position(flag_white_line);
        m3pi.left_motor(speed);
        m3pi.right_motor(-speed);
        //wait(0.1);
                
        if(position >= -0.3 && position <= 0.3)
        {
            break;
        }
    }
}

///////////// End of Code //////////////////
