#include <esp_now.h>
#include <WiFi.h>


// こちらは送信側で定義したものと同じ構造体だよ。
// ホントはヘッダにまとめた方が良いと思うけど、デモコードだから全く同じ定義を書いているよ。
struct ControlData{
    uint8_t mode;
    uint8_t number;
};
  
// ESP-Nowで受信したデータを格納するための変数だよ。
ControlData pixel_settings = {
.mode = 0,
.number = 5
};

// ちょっと順番が前後しちゃうけど、このOnDataRecv関数がESP-Nowでデータを受信
// したときに呼び出されるように後ろの方にあるsetup関数内で登録しているよ。
void OnDataRecv(const uint8_t *mac_addr, const uint8_t *receiveData, int data_len) {
    ControlData data;
    if(data_len == sizeof(ControlData)){
        // ESP-Nowで受信したデータの長さとControlDataの構造体の長さが一致していれば、
        // 受信したデータをpixel_settingsという変数へコピーするよ。
        memcpy(&pixel_settings, receiveData, data_len);
        Serial.print(pixel_settings.mode);
        Serial.print(" ");
        Serial.print(pixel_settings.number);
        Serial.print(ESP_LOG_DEBUG);
        Serial.print("ESPNow data received: ");
    }else{
        Serial.print(ESP_LOG_ERROR);
        Serial.print("Received data size does not match ControlData: ");
    }
}

void setup() {

    // ESP-Nowの初期化後に以下のコードを記載。
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);
    // 2. EPS-Nowを初期化
    // esp_now_init()を呼び出すことでESP-Nowを初期化しているよ。
    if(esp_now_init() != ESP_OK){
        Serial.print(ESP_LOG_ERROR);
        Serial.print("ESP-NOW Init Failed");
        return;
    }

    // 1. データ受信時に呼び出されるコールバック登録
    // ESP-Nowでデータを受信したときに呼び出されるコールバック関数を登録しているよ。
    esp_now_register_recv_cb(OnDataRecv);

}
void loop() {
    Serial.print("loop");
    delay(2000);
}