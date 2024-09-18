/*
  Hubert robot test program.

  This sketch control Hubert's servos.
  It implements command line interface via ROS, for setting the position of the servo using subscribe.
  Also, it publishes the current pwm value through rosserial. 

  Command interface:
  >> roscore
  >> rosrun rosserial_python serial_node.py _port:=/dev/ttyACM0 _baud:=57600
  Note: correct port must be selected (ttyACM0, 1 or whatever)
  Same baude rate as in Arduino sketch (below)
  >> rostopic echo robot_position
  >> rostopic pub /servo_body std_msgs/UInt16 <angle>
  >> rostopic pub /servo_neck_pan std_msgs/UInt16 <angle>
  >> rostopic pub /servo_neck_tilt std_msgs/UInt16 <angle>
  >> rostopic pub /servo_shoulder std_msgs/UInt16 <angle>
  >> rostopic pub /servo_elbow std_msgs/UInt16 <angle>
  >> rostopic pub /servo_gripper std_msgs/UInt16 <angle>

  Replace <angle> with a write.microseconds value in approx. [500,2350], mid pos.: 1350
  NOTE: Go back to NeutralPos. before terminating.
  
  created 23 Jun 2020
  by Krister Wolff
  modified 23 Jun 2020
  by Krister Wolff

  This example code is in the public domain.

  http://www.arduino.cc/en/
*/

#include <Arduino.h>
#include <Servo.h>
#include <ros.h>
#include <std_msgs/UInt16.h>


ros::NodeHandle hubert;

//Servos
Servo body;
Servo headPan;
Servo headTilt;
Servo shoulder;
Servo elbow;
Servo gripper;

//Init position of all servos
const int servo_pins[] = {3, 5, 6, 9, 10, 11};

const int pos_init[] = {1700, 1500, 2000, 2200, 1650, 1600};
int curr_pos[6];
int new_servo_val[6];

const int pos_min[] = {560, 550, 950, 750, 550, 550};
const int pos_max[] = {2330, 2340, 2400, 2200, 2400, 2150};

//Publisher
std_msgs::UInt16 Pwm;
ros::Publisher robot_position("robot_position",&Pwm);

//ROS-setup
void servo_body_ex(const std_msgs::UInt16& cmd_msg) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[0];
  CurrPwm = now;
  NewPwm = cmd_msg.data;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    body.writeMicroseconds(now);
    //Publishing data
    Pwm.data = now;//ZZZ
    robot_position.publish(&Pwm);//ZZZ
    delay(20);
  }
  curr_pos[0] = now;
  delay(10);

  hubert.loginfo("GOT DATA MOVE BODY");
}

void servo_neck_pan(const std_msgs::UInt16& cmd_msg) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[1];
  CurrPwm = now;
  NewPwm = cmd_msg.data;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    headPan.writeMicroseconds(now);
    //Publishing data
    Pwm.data = now;//ZZZ
    robot_position.publish(&Pwm);
    delay(20);
  }
  curr_pos[1] = now;
  delay(10);
  
	hubert.loginfo("GOT DATA MOVE SERVO NECK PAN");
}

void servo_neck_tilt(const std_msgs::UInt16& cmd_msg) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[2];
  CurrPwm = now;
  NewPwm = cmd_msg.data;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    headTilt.writeMicroseconds(now);
    //Publishing data
    Pwm.data = now;//ZZZ
    robot_position.publish(&Pwm);
    delay(20);
  }
  curr_pos[2] = now;
  delay(10);

	hubert.loginfo("GOT DATA MOVE SERVO NECK TILT");
}

void servo_shoulder(const std_msgs::UInt16& cmd_msg) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[3];
  CurrPwm = now;
  NewPwm = cmd_msg.data;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    shoulder.writeMicroseconds(now);
    //Publishing data
    Pwm.data = now;//ZZZ
    robot_position.publish(&Pwm);//ZZZ
    delay(20);
  }
  curr_pos[3] = now;
  delay(10);
  
	hubert.loginfo("GOT DATA MOVE SERVO SHOULDER");
}

void servo_elbow(const std_msgs::UInt16& cmd_msg) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[4];
  CurrPwm = now;
  NewPwm = cmd_msg.data;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    elbow.writeMicroseconds(now);
    //Publishing data
    Pwm.data = now;//ZZZ
    robot_position.publish(&Pwm);//ZZZ
    delay(20);
  }
  curr_pos[4] = now;
  delay(10);

  hubert.loginfo("GOT DATA MOVE SERVO ELBOW");
}

void servo_gripper_ex(const std_msgs::UInt16& cmd_msg) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[5];
  CurrPwm = now;
  NewPwm = cmd_msg.data;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    gripper.writeMicroseconds(now);
    //Publishing data
    Pwm.data = now;//ZZZ
    robot_position.publish(&Pwm);//ZZZ
    delay(20);
  }
  curr_pos[5] = now;
  delay(10);
  
  hubert.loginfo("GOT DATA MOVE SERVO GRIPPER");
}


//Subscriber
ros::Subscriber<std_msgs::UInt16> sub_body("/servo_body", servo_body_ex);
ros::Subscriber<std_msgs::UInt16> sub_pan("/servo_neck_pan", servo_neck_pan);
ros::Subscriber<std_msgs::UInt16> sub_tilt("/servo_neck_tilt", servo_neck_tilt);
ros::Subscriber<std_msgs::UInt16> sub_shoulder("/servo_shoulder", servo_shoulder);
ros::Subscriber<std_msgs::UInt16> sub_elbow("/servo_elbow", servo_elbow);
ros::Subscriber<std_msgs::UInt16> sub_gripper("/servo_gripper", servo_gripper_ex);


void setup() {

  Serial.begin(57600); // Starts the serial communication

  //Init node
	hubert.initNode();
  
  //Subscriptions
  hubert.subscribe(sub_body);
	hubert.subscribe(sub_pan);
	hubert.subscribe(sub_tilt);
	hubert.subscribe(sub_shoulder);
	hubert.subscribe(sub_elbow);	
  hubert.subscribe(sub_gripper);

  //Advertise
  hubert.advertise(robot_position);

	//Attach each joint servo
	//and write each init position
  body.attach(servo_pins[0]);
  body.writeMicroseconds(pos_init[0]);
  
  headPan.attach(servo_pins[1]);
  headPan.writeMicroseconds(pos_init[1]);
  
  headTilt.attach(servo_pins[2]);
  headTilt.writeMicroseconds(pos_init[2]);

  shoulder.attach(servo_pins[3]);
	shoulder.writeMicroseconds(pos_init[3]);

	elbow.attach(servo_pins[4]);
	elbow.writeMicroseconds(pos_init[4]);
	
	gripper.attach(servo_pins[5]);
  gripper.writeMicroseconds(pos_init[5]);

  //Initilize curr_pos and new_servo_val vectors
  byte i;
  for (i=0; i<(sizeof(pos_init)/sizeof(int)); i++){
    curr_pos[i] = pos_init[i];
    new_servo_val[i] = curr_pos[i];
  }

	delay(250);
}

void loop() {
	hubert.spinOnce();
	delay(1);
}
