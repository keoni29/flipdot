
#define PANEL_NOF_COLUMNS 28
#define DISPLAY_NOF_PANELS 4
#define DISPLAY_NOF_COLUMNS PANEL_NOF_COLUMNS * DISPLAY_NOF_PANELS
#define DISPLAY_NOF_ROWS 16

#define FLIP_US 300
#define DELAY_US 500

#define PIN_PNL_A0 3
#define PIN_PNL_A1 2
#define PIN_ENA 4
#define PIN_COL_B1 A1
#define PIN_COL_B0 A0
#define PIN_DAT 15
#define PIN_COL_A2 14
#define PIN_COL_A1 16
#define PIN_COL_A0 10

#define PIN_ROW_A0 9
#define PIN_ROW_A1 8
#define PIN_ROW_A2 7
#define PIN_ROW_A3 6
#define PIN_ROW_POL 5

void flip(uint8_t x, uint8_t y, uint8_t d);
inline void selectRow(uint8_t row);
inline void selectColumn(uint8_t column);

typedef struct {
  int x;
  int y;
  int d;
} Display;

Display mDisplay;

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.

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
  int data, row, col;
  
  for(data = 0; data <= 1; data++){
    for(row = 0; row < DISPLAY_NOF_ROWS; row++){
      for(col = 0; col < DISPLAY_NOF_COLUMNS; col++){
        flip(col, row, data);
        delayMicroseconds(DELAY_US);
      }
    }
  }
}

// Private functions

/**
 * Select the display row
 * @param row[in]
 */
inline void selectRow(uint8_t row) {
  digitalWrite(PIN_ROW_A0, bitRead(row, 0));
  digitalWrite(PIN_ROW_A1, bitRead(row, 1));
  digitalWrite(PIN_ROW_A2, bitRead(row, 2));
  digitalWrite(PIN_ROW_A3, bitRead(row, 3));
}


/**
 * Select the display column.
 * @param column[in]
 */
inline void selectColumn(uint8_t column) {
  /* Each column driver has 32 outputs, but only 28 are connected. After 7 columns there is one column which is not wired up, therefore we skip all missing columns. */
  column += column / 7;

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
 * @param x[in] Dot x-coordinate or column
 * @param y[in] Dot y-coordinate or row
 * @param d[in] Data, or Dot polarity. 1=on 0=off
 */
void flip(uint8_t x, uint8_t y, uint8_t d) {

  if (x < DISPLAY_NOF_COLUMNS && y < DISPLAY_NOF_ROWS) {
    if (x != mDisplay.x) {
      mDisplay.x = x;
      selectColumn(mDisplay.x);
    }
  
    if (y != mDisplay.y) {
      mDisplay.y = y;
      selectRow(mDisplay.y);
    }
  
    if (d != mDisplay.d) {
      digitalWrite(PIN_ROW_POL, d);
      digitalWrite(PIN_DAT, d); // TODO combine pins.
    }
    
    digitalWrite(PIN_ENA, HIGH);
    delayMicroseconds(FLIP_US);
    digitalWrite(PIN_ENA, LOW);
  }
}
