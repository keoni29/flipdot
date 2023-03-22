/**
 * Flipdot display driver firmware
 * (c) 2023 Koen van Vliet <8by8mail@gmail.com>
 * 
 * Serial1 command format: Two consecutive bytes containing x,y coordinates and dot polarity (on/off.)
 * CMDH = 1CCC CCCC
 * CMDL = 0xxP RRRR
 * 
 * C = column address
 * R = row address
 * P = dot polarity (1= on/ 0=off)
 * x = reserved for future use, set to 0 for now
 */

#define BAUD_RATE 115200UL ///< Serial1 command interface data rate.
#define BAUD_RATE 74880UL ///< Serial1 command interface data rate.

// Display parameters
#define PANEL_NOF_COLUMNS 28 ///< Number of columns per panel
#define DISPLAY_NOF_PANELS 4 ///< Number of daisy chained panels that form the display.
#define DISPLAY_NOF_ROWS 16 ///< Number of rows of the display

#define DISPLAY_NOF_COLUMNS PANEL_NOF_COLUMNS * DISPLAY_NOF_PANELS ///< Total number of columns of the display

#define FLIP_DOT_ON_TIME_US 150 ///< On-time of the coil while flipping a dot.\n unit: microseconds\n typical range is 200 to 500
#define FLIP_DOT_MIN_DELAY_TIME_US 10 ///< Minimum time between flipping dots.

#define PIN_PNL_A0 3  ///< Panel select address pin 
#define PIN_PNL_A1 2  ///< Panel select address pin
#define PIN_ENA 4     ///< Column driver enable pulse pin. Used to flip a dot.
#define PIN_COL_B1 A1 ///< Column driver address pin
#define PIN_COL_B0 A0 ///< Column driver address pin
#define PIN_DAT 15    ///< Column driver data pin. Specifies the polarity of the column driver output. Set to 1 to turn a dot on, 0 to turn a dot off. //TODO check this
#define PIN_COL_A2 14 ///< Column driver address pin
#define PIN_COL_A1 16 ///< Column driver address pin
#define PIN_COL_A0 10 ///< Column driver address pin

#define PIN_ROW_A0 9  ///< Row driver address pin
#define PIN_ROW_A1 8  ///< Row driver address pin
#define PIN_ROW_A2 7  ///< Row driver address pin
#define PIN_ROW_A3 6  ///< Row driver address pin
#define PIN_ROW_POL 5 ///< Row driver polarity pin. Specifies the polarity of the row driver output. Set to 1 to turn a dot on, 0 to turn a dot off. //TODO check this

static void flip(uint8_t x, uint8_t y, uint8_t d);
static inline void selectRow(uint8_t row);
static inline void selectColumn(uint8_t column);

void setup() {
  Serial.begin(115200);
  Serial.println("Flipdot begin!");
  Serial1.begin(BAUD_RATE);

  pinMode(PIN_PNL_A0, OUTPUT);
  pinMode(PIN_PNL_A1, OUTPUT);
  pinMode(PIN_ROW_A0, OUTPUT);
  pinMode(PIN_ROW_A1, OUTPUT);
  pinMode(PIN_ROW_A2, OUTPUT);
  pinMode(PIN_ROW_A3, OUTPUT);
  pinMode(PIN_ENA, OUTPUT);
  pinMode(PIN_COL_B1, OUTPUT);
  pinMode(PIN_COL_B0, OUTPUT);
  pinMode(PIN_DAT, OUTPUT);
  pinMode(PIN_COL_A2, OUTPUT);
  pinMode(PIN_COL_A1, OUTPUT);
  pinMode(PIN_COL_A0, OUTPUT);
  pinMode(PIN_ROW_POL, OUTPUT);
}


// the loop function runs over and over again forever
void loop() {  
  uint8_t data, row, col;
  uint8_t cmdl, cmdh;
  
  #ifdef TESTPATTERN
  while(1){
   for(data = 0; data <= 1; data++){
     for(row = 0; row < DISPLAY_NOF_ROWS; row++){
       for(col = 0; col < DISPLAY_NOF_COLUMNS; col++){
         flip(col, row, data);
         delayMicroseconds(FLIP_DOT_MIN_DELAY_TIME_US);
       }
     }
   }
  }
  #endif

  cmdl = 0;

  while (1) {
    if (Serial1.available()) {
      if (cmdl & (1<<7)) {
        cmdh = cmdl;
        cmdl = Serial1.read();

        data = (cmdl >> 4) & 0x01;
        row = cmdl & 0x0F;
        col = cmdh & 0x7F;

        flip(col, row, data);
        
        cmdl = 0;      
      } else {
        cmdl = Serial1.read();
      }
    }
  }
}

// Private functions

/**
 * Select the display row
 * @param row[in]
 */
static inline void selectRow(uint8_t row) {
  digitalWrite(PIN_ROW_A0, bitRead(row, 0));
  digitalWrite(PIN_ROW_A1, bitRead(row, 1));
  digitalWrite(PIN_ROW_A2, bitRead(row, 2));
  digitalWrite(PIN_ROW_A3, bitRead(row, 3));
}


/**
 * Select the display column.
 * @param column[in]
 */
static inline void selectColumn(uint8_t column) {
  /* Each column driver has 32 outputs, but only 28 are connected. After 7 columns there is one column which is not wired up, therefore we skip all missing columns. */
  column = column + column / 7 + 1;

  digitalWrite(PIN_COL_A0, bitRead(column, 0));
  digitalWrite(PIN_COL_A1, bitRead(column, 1));
  digitalWrite(PIN_COL_A2, bitRead(column, 2));
  digitalWrite(PIN_COL_B0, bitRead(column, 3));
  digitalWrite(PIN_COL_B1, bitRead(column, 4));

  digitalWrite(PIN_PNL_A0, bitRead(column, 5));
  digitalWrite(PIN_PNL_A1, bitRead(column, 6));
}

/**
 * Flip a dot at position
 * @param x[in] Dot x-coordinate / column
 * @param y[in] Dot y-coordinate / row
 * @param p[in] Dot polarity. 1=on 0=off
 * 
 * Only updates row and column outputs if the coordinates have changed from last call.
 */
static void flip(uint8_t x, uint8_t y, uint8_t p) {
  static uint8_t xx = 0, yy = 0, pp = 0;

  if (x < DISPLAY_NOF_COLUMNS && y < DISPLAY_NOF_ROWS) {
    if (x != xx) {
      xx = x;
      selectColumn(xx);
    }
  
    if (y != yy) {
      yy = y;
      selectRow(yy);
    }
  
    if (p != pp) {
      pp = p;
      digitalWrite(PIN_ROW_POL, pp);
      digitalWrite(PIN_DAT, pp); // TODO combine pins.
    }
    
    digitalWrite(PIN_ENA, HIGH);
    delayMicroseconds(FLIP_DOT_ON_TIME_US);
    digitalWrite(PIN_ENA, LOW);
  }
}
