#define Spectro 2    // Input signal from QePro for illumination sequence
#define LampEnable 3 // Input signal from Qepro for reset at line's end

int Nb_pulse = 0, iState, iStateM=LOW, iStateReset;

void setup() {
  // 

  pinMode(LampEnable, INPUT);
  pinMode(Spectro, INPUT);
  pinMode(7, OUTPUT); 
  pinMode(5, OUTPUT);    // laser 655nm logique inverse
  pinMode(9, OUTPUT);
  pinMode(11, OUTPUT);
  digitalWrite(5, HIGH);

}

void loop() {
  iState = digitalRead(Spectro);
  iStateReset = digitalRead(LampEnable);
  
  
  if((iState != iStateM) && (iState == HIGH)) // FRONT MONTANT 
  {
    Nb_pulse++;  
    if (Nb_pulse%4 == 0)
    {digitalWrite(7, HIGH);
    iStateM = iState;}
    if (Nb_pulse%4 == 1)
    {digitalWrite(5, LOW);
    iStateM = iState;}
    if (Nb_pulse%4 == 2)
    {digitalWrite(9, HIGH);
    iStateM = iState;}
    if (Nb_pulse%4 == 3)
    {digitalWrite(11, HIGH);
    iStateM = iState;}
  } 
  if((iState != iStateM) && (iState == LOW)) // FRONT DESCENDANT
  {  
    if (Nb_pulse%4 == 0)
    {digitalWrite(7, LOW);
    iStateM = iState;}
    if (Nb_pulse%4 == 1)
    {digitalWrite(5, HIGH);
    iStateM = iState;}
    if (Nb_pulse%4 == 2)
    {digitalWrite(9, LOW);
    iStateM = iState;}
    if (Nb_pulse%4 == 3)
    {digitalWrite(11, LOW);
    iStateM = iState;}
  }
  if(iStateReset == HIGH)
  {
    Nb_pulse = 0;
  }  
  
  delayMicroseconds(1000);
}
