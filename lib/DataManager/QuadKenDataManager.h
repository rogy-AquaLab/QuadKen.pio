#ifndef QUADKEN_DATA_MANAGER_H
#define QUADKEN_DATA_MANAGER_H

#include <vector>
#include <map>
#include <cstring>

// ESP32/Arduino環境での例外処理
#ifdef ARDUINO
    #include <Arduino.h>
    #define THROW_RUNTIME_ERROR(msg) { Serial.println(msg); abort(); }
    #define THROW_INVALID_ARGUMENT(msg) { Serial.println(msg); abort(); }
#else
    #include <stdexcept>
    #include <type_traits>
    #define THROW_RUNTIME_ERROR(msg) throw std::runtime_error(msg)
    #define THROW_INVALID_ARGUMENT(msg) throw std::invalid_argument(msg)
#endif

namespace Quadken {

// シンプルな基底クラス
class DataManagerBase {
public:
    virtual ~DataManagerBase() = default;
    virtual void unpack(const std::vector<uint8_t>& buffer) = 0;
    virtual std::vector<uint8_t> pack() const = 0;
    virtual size_t getExpectedSize() const = 0;
    virtual size_t getElementSize() const = 0;
    
    // 汎用unpack関数（型指定不要、identifierからデータを検索してデータを入れる）
    static void unpackAny(uint8_t identifier, const std::vector<uint8_t>& buffer) {
        auto& global_instances = getGlobalInstances();
        auto it = global_instances.find(identifier);
        if (it == global_instances.end()) {
            THROW_RUNTIME_ERROR("No instance found for identifier");
        }
        
        DataManagerBase* instance = it->second;
        if (buffer.size() != instance->getExpectedSize()) {
            THROW_INVALID_ARGUMENT("Buffer size mismatch for identifier");
        }
        
        // identifierで見つけたインスタンスにデータを直接設定
        instance->unpack(buffer);
    }
    
protected:
    static std::map<uint8_t, DataManagerBase*>& getGlobalInstances() {
        static std::map<uint8_t, DataManagerBase*> instances;
        return instances;
    }
};

template <typename T>
class DataManager : public DataManagerBase {
#ifndef ARDUINO
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type.");
#endif

public:
    DataManager(uint8_t identifier, size_t length)
        : identifier_(identifier), length_(length), data_(length, 0) {
        if (identifier == 0) {
            THROW_INVALID_ARGUMENT("Identifier must be 1-255");
        }
        
        // グローバルマップに登録
        auto& global_instances = getGlobalInstances();
        if (global_instances.find(identifier) != global_instances.end()) {
            THROW_INVALID_ARGUMENT("Identifier already exists");
        }
        global_instances[identifier] = this;
    }

    ~DataManager() {
        getGlobalInstances().erase(identifier_);
    }

    void update(const std::vector<T>& new_data) {
        if (new_data.size() != length_) {
            THROW_INVALID_ARGUMENT("Size mismatch");
        }
        data_ = new_data;
    }

    const std::vector<T>& get() const {
        return data_;
    }

    std::vector<uint8_t> pack() const override {
        std::vector<uint8_t> buffer(length_ * sizeof(T));
        std::memcpy(buffer.data(), data_.data(), buffer.size());
        return buffer;
    }

    void unpack(const std::vector<uint8_t>& buffer) override {
        if (buffer.size() != length_ * sizeof(T)) {
            THROW_INVALID_ARGUMENT("Unpack size mismatch");
        }
        std::memcpy(data_.data(), buffer.data(), buffer.size());
    }

    size_t getExpectedSize() const override {
        return length_ * sizeof(T);
    }

    size_t getElementSize() const override {
        return sizeof(T);
    }

    uint8_t identifier() const {
        return identifier_;
    }



    // 型安全なunpack関数（要素サイズチェック付き）
    static std::vector<T> unpack(uint8_t identifier, const std::vector<uint8_t>& buffer) {
        auto& global_instances = getGlobalInstances();
        auto it = global_instances.find(identifier);
        if (it == global_instances.end()) {
            THROW_RUNTIME_ERROR("No instance found for identifier");
        }
        
        DataManagerBase* instance = it->second;
        
        // 要素サイズチェック（簡易型チェック）
        if (instance->getElementSize() != sizeof(T)) {
            THROW_RUNTIME_ERROR("Element size mismatch - possible type mismatch");
        }
        
        if (buffer.size() != instance->getExpectedSize()) {
            THROW_INVALID_ARGUMENT("Buffer size mismatch");
        }
        
        instance->unpack(buffer);
        
        // 安全なキャスト（要素サイズチェック済み）
        DataManager<T>* typed_instance = static_cast<DataManager<T>*>(instance);
        return typed_instance->get();
    }

private:
    const uint8_t identifier_;
    const size_t length_;
    std::vector<T> data_;
};

} // namespace Quadken

#endif // QUADKEN_DATA_MANAGER_H
