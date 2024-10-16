/*
  Hubert robot test program.

  This sketch control Hubert's servos.  
  A write.microseconds value in approx. [500,2350], mid pos.: 1350
  NOTE: Go back to NeutralPos. before terminating.
  
  created 20 Jul 2020
  by Krister Wolff
  modified 20 Jul 2020
  by Krister Wolff

  This example code is in the public domain.

  http://www.arduino.cc/en/
*/

#include <Arduino.h>
#include <Servo.h>

//Servos
Servo body;
Servo headPan;
Servo headTilt;
Servo shoulder;
Servo elbow;
Servo gripper;

//Init position of all servos
const int servo_pins[] = {3, 9, 12, 6, 10, 5};

const int pos_init[] = {1700, 1500, 2000, 1500, 850, 1600};
int curr_pos[6];
int new_positions[6];

const int pos_min[] = {560, 550, 950, 750, 550, 550};
const int pos_max[] = {2330, 2340, 2400, 2300, 2400, 2150};

//Servo update function
void servo_body_ex(const int new_pos) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[0];
  CurrPwm = now;
  NewPwm = new_pos;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    body.writeMicroseconds(now);
    delay(20);
  }
  curr_pos[0] = now;
  delay(10);
}

//Servo update function
void servo_neck_pan(const int new_pos) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[1];
  CurrPwm = now;
  NewPwm = new_pos;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    headPan.writeMicroseconds(now);
    delay(20);
  }
  curr_pos[1] = now;
  delay(10);
}

//Servo update function
void servo_neck_tilt(const int new_pos) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[2];
  CurrPwm = now;
  NewPwm = new_pos;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    headTilt.writeMicroseconds(now);
    delay(20);
  }
  curr_pos[2] = now;
  delay(10);
}

//Servo update function
void servo_shoulder(const int new_pos) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[3];
  CurrPwm = now;
  NewPwm = new_pos;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    shoulder.writeMicroseconds(now);
    delay(20);
  }
  curr_pos[3] = now;
  delay(10);
}

//Servo update function
void servo_elbow(const int new_pos) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[4];
  CurrPwm = now;
  NewPwm = new_pos;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    elbow.writeMicroseconds(now);
    delay(20);
  }
  curr_pos[4] = now;
  delay(10);
}

void move_shoulder_and_elbow_simultaneously(const int shoulder_pos, const int elbow_pos) {
  int shoulder_diff, shoulder_steps, shoulder_now, shoulder_CurrPwm, shoulder_NewPwm;
  int elbow_diff, elbow_steps, elbow_now, elbow_CurrPwm, elbow_NewPwm;
  int delta = 6;

  // Current servo values
  shoulder_now = curr_pos[3];
  shoulder_CurrPwm = shoulder_now;
  shoulder_NewPwm = shoulder_pos;

  elbow_now = curr_pos[4];
  elbow_CurrPwm = elbow_now;
  elbow_NewPwm = elbow_pos;

  // Determine iteration "diff" from old to new position
  shoulder_diff = (shoulder_NewPwm - shoulder_CurrPwm) / abs(shoulder_NewPwm - shoulder_CurrPwm); // +1 if NewPwm is bigger than CurrPwm, -1 otherwise
  shoulder_steps = abs(shoulder_NewPwm - shoulder_CurrPwm);

  elbow_diff = (elbow_NewPwm - elbow_CurrPwm) / abs(elbow_NewPwm - elbow_CurrPwm); // +1 if NewPwm is bigger than CurrPwm, -1 otherwise
  elbow_steps = abs(elbow_NewPwm - elbow_CurrPwm);

  // Move both servos simultaneously
  for (int i = 0; i < max(shoulder_steps, elbow_steps); i += delta) {
    if (i < shoulder_steps) {
      shoulder_now = shoulder_now + delta * shoulder_diff;
      shoulder.writeMicroseconds(shoulder_now);
    }
    if (i < elbow_steps) {
      elbow_now = elbow_now + delta * elbow_diff;
      elbow.writeMicroseconds(elbow_now);
    }
    delay(20);
  }

  // Update current positions
  curr_pos[3] = shoulder_now;
  curr_pos[4] = elbow_now;
  delay(10);
}

//Servo update function
void servo_gripper_ex(const int new_pos) {

  int diff, steps, now, CurrPwm, NewPwm, delta = 6;

  //current servo value
  now = curr_pos[5];
  CurrPwm = now;
  NewPwm = new_pos;

  /* determine interation "diff" from old to new position */
  diff = (NewPwm - CurrPwm)/abs(NewPwm - CurrPwm); // Should return +1 if NewPwm is bigger than CurrPwm, -1 otherwise.
  steps = abs(NewPwm - CurrPwm);
  delay(10);

  for (int i = 0; i < steps; i += delta) {
    now = now + delta*diff;
    gripper.writeMicroseconds(now);
    delay(20);
  }
  curr_pos[5] = now;
  delay(10);
}

void init_robot_positions(){
  body.attach(servo_pins[0]);
  body.writeMicroseconds(pos_init[0]);
  
  headPan.attach(servo_pins[1]);
  headPan.writeMicroseconds(pos_init[1]);
  
  headTilt.attach(servo_pins[2]);
  headTilt.writeMicroseconds(pos_init[2]);

	elbow.attach(servo_pins[4]);
	elbow.writeMicroseconds(pos_init[4]);
  
  shoulder.attach(servo_pins[3]);
	shoulder.writeMicroseconds(pos_init[3]);

	
	gripper.attach(servo_pins[5]);
  gripper.writeMicroseconds(pos_init[5]);

  //Initilize curr_pos and new_servo_val vectors
  byte i;
  for (i=0; i<(sizeof(pos_init)/sizeof(int)); i++){
    curr_pos[i] = pos_init[i];
    new_positions[i] = curr_pos[i];
  }

	delay(2000);
}

void setup() {

  Serial.begin(57600); // Starts the serial communication
  init_robot_positions();
  delay(1000);
  Serial.println("<Arduino is ready>");


	//Attach each joint servo
	//and write each init position
  
}
// Example 3 - Receive with start- and end-markers

const byte numChars = 40;
char receivedChars[numChars];

bool newData = false;


void loop() {
  // Serial.println(("Neck min"));
  // servo_neck_tilt(950);
  // delay(100);
  // servo_neck_tilt(2400);
  // Serial.println(("Neck max"));



  recvWithStartEndMarkers(&newData);
  if (newData == true) {
    parseCommand(receivedChars, new_positions, 6);
    servo_body_ex(new_positions[0]);
    servo_neck_pan(new_positions[1]);
    servo_neck_tilt(new_positions[2]);
    move_shoulder_and_elbow_simultaneously(new_positions[3], new_positions[4]);
    // servo_elbow(new_positions[4]);
    // servo_shoulder(new_positions[3]);
    servo_gripper_ex(new_positions[5]);
    showNewData();
    newData = false;
  }
}



void recvWithStartEndMarkers(bool *newData) {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
    while (Serial.available() > 0 && *newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                *newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}
void parseCommand(char* command, int* new_positions, int numValues) {
    char *ptr = strtok(command, ",");
    int i = 0;
    while (ptr != NULL && i < numValues) {
        new_positions[i] = atoi(ptr);  // Convert string to integer
        i++;
        ptr = strtok(NULL, ",");
    }
}

void showNewData() {
    Serial.print("<ARDUINO -- ");
    for (int i = 0; i < 6; i++) {  // Fix the loop to iterate over the correct number of elements
        Serial.print(new_positions[i]);
        if (i < 5) {
            Serial.print(',');
        }
    }
    Serial.println(">");
}