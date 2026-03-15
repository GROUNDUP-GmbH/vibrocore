/**
 * Vibrocore — Hub Motor Control (NEMA 42 + CL86T-V4.1)
 *
 * Controls the linear hub via step/dir interface.
 * Closed-loop stepper driver handles torque regulation.
 *
 * Hardware:
 *   - CONTROLLINO MAXI or Arduino Opta (industrial PLC)
 *   - CL86T-V4.1 closed-loop stepper driver
 *   - NEMA 42 stepper motor with encoder
 *   - Neugart PLPE120-040 gearbox (40:1)
 *   - 10B-2 duplex chain + 15T sprockets
 *
 * Connections:
 *   PLC Digital Out → Driver PUL+/DIR+/ENA+
 *   PLC Digital In  ← Driver ALM (alarm/fault)
 *   PLC Digital In  ← Limit switches (upper/lower)
 *   PLC Digital Out → Brake relay (24V, active = released)
 *   PLC Analog In   ← Current sensor (stone detection)
 */

#include <AccelStepper.h>

// -- Pin definitions (adjust for your PLC) --
const int PIN_STEP      = 9;
const int PIN_DIR       = 8;
const int PIN_ENABLE    = 7;
const int PIN_BRAKE     = 6;
const int PIN_ALARM     = A0;
const int PIN_LIMIT_UP  = 2;
const int PIN_LIMIT_DN  = 3;
const int PIN_BTN_UP    = 4;
const int PIN_BTN_DN    = 5;
const int PIN_ESTOP     = 10;
const int PIN_CURRENT   = A1;

// -- Machine parameters --
const float STEPS_PER_REV   = 200.0;
const float MICROSTEPPING   = 8.0;
const float GEAR_RATIO      = 40.0;
const float SPROCKET_CIRC   = 238.0;  // mm, 15T 10B-2 sprocket

// Steps per mm of carriage travel
const float STEPS_PER_MM = (STEPS_PER_REV * MICROSTEPPING * GEAR_RATIO) / SPROCKET_CIRC;

// Speed & acceleration
const float MAX_SPEED_MMS       = 60.0;   // mm/s max
const float PENETRATION_SPEED   = 15.0;   // mm/s during sonic push-in
const float RETRACT_SPEED       = 50.0;   // mm/s pull-out
const float ACCEL_MMS2          = 30.0;   // mm/s²

// Target depth (mm from top home position)
const float TARGET_DEPTH        = 1200.0; // 1.2 m stroke

// Stone detection threshold (raw ADC 0-1023, calibrate in field)
const int CURRENT_THRESHOLD     = 700;
const unsigned long CURRENT_DEBOUNCE_MS = 200;

// -- State machine --
enum State {
  IDLE,
  HOMING_UP,
  MOVING_DOWN,
  MOVING_UP,
  ESTOP,
  FAULT
};

State currentState = IDLE;
AccelStepper stepper(AccelStepper::DRIVER, PIN_STEP, PIN_DIR);
unsigned long highCurrentStart = 0;
bool highCurrentDetected = false;

void setup() {
  Serial.begin(115200);
  Serial.println(F("Vibrocore Hub Control v0.1"));

  pinMode(PIN_ENABLE, OUTPUT);
  pinMode(PIN_BRAKE, OUTPUT);
  pinMode(PIN_ALARM, INPUT);
  pinMode(PIN_LIMIT_UP, INPUT_PULLUP);
  pinMode(PIN_LIMIT_DN, INPUT_PULLUP);
  pinMode(PIN_BTN_UP, INPUT_PULLUP);
  pinMode(PIN_BTN_DN, INPUT_PULLUP);
  pinMode(PIN_ESTOP, INPUT_PULLUP);
  pinMode(PIN_CURRENT, INPUT);

  disableMotor();
  engageBrake();

  stepper.setMaxSpeed(MAX_SPEED_MMS * STEPS_PER_MM);
  stepper.setAcceleration(ACCEL_MMS2 * STEPS_PER_MM);

  Serial.println(F("System ready. Press UP to home, DN to start cycle."));
}

void loop() {
  if (digitalRead(PIN_ESTOP) == LOW) {
    emergencyStop();
    return;
  }

  if (digitalRead(PIN_ALARM) == HIGH) {
    handleDriverFault();
    return;
  }

  switch (currentState) {
    case IDLE:
      handleIdle();
      break;

    case HOMING_UP:
      handleHomingUp();
      break;

    case MOVING_DOWN:
      handleMovingDown();
      break;

    case MOVING_UP:
      handleMovingUp();
      break;

    case ESTOP:
      if (digitalRead(PIN_ESTOP) == HIGH) {
        Serial.println(F("E-Stop released. Resetting to IDLE."));
        currentState = IDLE;
      }
      break;

    case FAULT:
      break;
  }
}

void handleIdle() {
  if (digitalRead(PIN_BTN_UP) == LOW) {
    Serial.println(F("Homing UP..."));
    enableMotor();
    releaseBrake();
    stepper.setSpeed(RETRACT_SPEED * STEPS_PER_MM);
    currentState = HOMING_UP;
  }
  else if (digitalRead(PIN_BTN_DN) == LOW) {
    Serial.println(F("Starting penetration cycle..."));
    enableMotor();
    releaseBrake();
    stepper.moveTo(TARGET_DEPTH * STEPS_PER_MM);
    stepper.setMaxSpeed(PENETRATION_SPEED * STEPS_PER_MM);
    currentState = MOVING_DOWN;
  }
}

void handleHomingUp() {
  if (digitalRead(PIN_LIMIT_UP) == LOW) {
    stepper.stop();
    stepper.setCurrentPosition(0);
    disableMotor();
    engageBrake();
    currentState = IDLE;
    Serial.println(F("Home position reached."));
    return;
  }
  stepper.setSpeed(-RETRACT_SPEED * STEPS_PER_MM);
  stepper.runSpeed();
}

void handleMovingDown() {
  if (digitalRead(PIN_LIMIT_DN) == LOW) {
    Serial.println(F("Lower limit reached!"));
    stopAndRetract();
    return;
  }

  if (checkStoneDetection()) {
    Serial.println(F("STONE DETECTED — aborting!"));
    stepper.stop();
    delay(100);
    stepper.move(-20 * STEPS_PER_MM);  // retract 20mm
    while (stepper.distanceToGo() != 0) {
      stepper.run();
    }
    disableMotor();
    engageBrake();
    currentState = IDLE;
    Serial.println(F("Retracted 20mm. Check conditions and retry."));
    return;
  }

  if (stepper.distanceToGo() == 0) {
    Serial.println(F("Target depth reached!"));
    stopAndRetract();
    return;
  }

  stepper.run();
}

void handleMovingUp() {
  if (digitalRead(PIN_LIMIT_UP) == LOW || stepper.distanceToGo() == 0) {
    stepper.stop();
    stepper.setCurrentPosition(0);
    disableMotor();
    engageBrake();
    currentState = IDLE;
    Serial.println(F("Extraction complete. Cycle done."));
    return;
  }
  stepper.run();
}

void stopAndRetract() {
  // TODO: Signal VFD to stop sonic head before extraction
  stepper.stop();
  delay(500);  // allow sonic head to spin down

  stepper.setMaxSpeed(RETRACT_SPEED * STEPS_PER_MM);
  stepper.moveTo(0);
  currentState = MOVING_UP;
  Serial.println(F("Retracting..."));
}

bool checkStoneDetection() {
  int current = analogRead(PIN_CURRENT);
  if (current > CURRENT_THRESHOLD) {
    if (!highCurrentDetected) {
      highCurrentDetected = true;
      highCurrentStart = millis();
    }
    if (millis() - highCurrentStart > CURRENT_DEBOUNCE_MS) {
      return true;
    }
  } else {
    highCurrentDetected = false;
  }
  return false;
}

void emergencyStop() {
  stepper.stop();
  disableMotor();
  engageBrake();
  currentState = ESTOP;
  Serial.println(F("*** EMERGENCY STOP ***"));
}

void handleDriverFault() {
  stepper.stop();
  disableMotor();
  engageBrake();
  currentState = FAULT;
  Serial.println(F("DRIVER FAULT — check CL86T alarm output."));
}

void enableMotor() {
  digitalWrite(PIN_ENABLE, LOW);  // active LOW for most drivers
}

void disableMotor() {
  digitalWrite(PIN_ENABLE, HIGH);
}

void releaseBrake() {
  digitalWrite(PIN_BRAKE, HIGH);  // 24V relay energised = brake released
}

void engageBrake() {
  digitalWrite(PIN_BRAKE, LOW);   // relay off = spring engages brake
}
