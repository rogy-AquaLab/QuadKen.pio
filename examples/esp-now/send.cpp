#include <esp_now.h>
#include <WiFi.h>

uint8_t loop_count = 0;

// 正方形ESP32 : 08:D1:F9:36:FF:3C
// ターゲット（フィギュアスタンド）の MAC address
uint8_t targetAddress[] = {0x08, 0xD1, 0xF9, 0x36, 0xFF, 0x3C};

// 送信データの構造体。
// ただし、ESP-Nowで送信可能なデータサイズは250バイトまでってことは覚えておいてね。
struct ControlData{
  uint8_t mode;
  uint8_t number;
};

// ピア（送信先）の情報を保持するための変数だよ。
esp_now_peer_info_t peerInfo;

// ESP-Nowでデータを送信した後に呼び出されるコールバック関数だよ。
// statusの値をチェックすることで送信が成功したかどうかが分かるよ。
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print(ESP_LOG_DEBUG);
    Serial.print(status == ESP_NOW_SEND_SUCCESS ? "ESPNow data send success" : "ESPNow data send failed");
}

// ESP-Nowでデータを送信するための関数を定義しているよ。
void sendControlData(uint8_t num=0){
    Serial.print("\tsendControlData");
  ControlData data = {
    .mode = 1,
    .number = num
  };
  esp_now_send(targetAddress, (uint8_t*)&data, sizeof(data));
}

void setup() {
    Serial.begin(115200);
  // WiFi.mode()の引数にWIFI_STAを指定することで、Wi-FiのモードをWIFI_STAにする
  WiFi.mode(WIFI_STA);
  // esp_now_init()を呼び出すことでESP-Nowを初期化している
  if(esp_now_init() != ESP_OK){
    Serial.println("ESP-NOW Init Failed");
    return;
  }

  // targetAddressにはターゲットのMAC addressが格納されていて、この値をpeerInfoにコピーしているよ。
  memcpy(peerInfo.peer_addr, targetAddress, 6);
  peerInfo.channel = 0; // Wi-Fiのチャンネル  
  peerInfo.encrypt = false; // 暗号化する or しない

  // esp_now_add_peer()を呼び出すことで、ターゲットのアドレスを登録
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.print(ESP_LOG_ERROR);
    Serial.print("Failed to add peer, error code: ");
    return;
  }

  // 送信時のコールバック関数の登録
  esp_now_register_send_cb(OnDataSent);

}

void loop() {
  // ボクはデータ送信用にsendControlData()という関数を定義したよ。
  Serial.print("loop");
  sendControlData(loop_count);

  loop_count++;
  delay(2000);
}