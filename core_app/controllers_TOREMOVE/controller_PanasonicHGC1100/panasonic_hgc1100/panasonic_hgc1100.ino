// from https://github.com/abpydev/LouCOMAX_Controllers/blob/main/controllers/LOUCOMAX_LASER_CONTROL.ino


// Constants
const int analogPin = A0; // Pin A0 for analog input


void setup() {
  // Initialize the serial communication at a baud rate of 9600:
  Serial.begin(9600);
}

void loop() {
  // Read the analog input on pin A0:
  int sensorValue = analogRead(analogPin);
  
  // Print the sensor value to the Serial Monitor:
  Serial.println(sensorValue);
  
  // Delay in microseconds before next reading:
  delayMicroseconds(5000);
}
