#ifndef QUADKEN_DATA_MANAGER_H
#define QUADKEN_DATA_MANAGER_H

#include <vector>
#include <map>
#include <stdexcept>
#include <cstring>
#include <type_traits>

namespace Quadken {

template <typename T>
class DataManager {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type.");

public:
    DataManager(uint8_t identifier, size_t length)
        : identifier_(identifier), length_(length), data_(length, 0) {
        if (identifier == 0) {
            throw std::invalid_argument("Identifier must be 1-255");
        }
        getInstances()[identifier] = this;
    }

    ~DataManager() {
        getInstances().erase(identifier_);
    }

    void update(const std::vector<T>& new_data) {
        if (new_data.size() != length_) {
            throw std::invalid_argument("Size mismatch");
        }
        data_ = new_data;
    }

    const std::vector<T>& get() const {
        return data_;
    }

    std::vector<uint8_t> pack() const {
        std::vector<uint8_t> buffer(length_ * sizeof(T));
        std::memcpy(buffer.data(), data_.data(), buffer.size());
        return buffer;
    }

    void unpack(const std::vector<uint8_t>& buffer) {
        if (buffer.size() != length_ * sizeof(T)) {
            throw std::invalid_argument("Unpack size mismatch");
        }
        std::memcpy(data_.data(), buffer.data(), buffer.size());
    }

    uint8_t identifier() const {
        return identifier_;
    }

    static std::vector<T> unpack(uint8_t identifier, const std::vector<uint8_t>& buffer) {
        auto* instance = search(identifier);
        instance->unpack(buffer);
        return instance->get();
    }

private:
    const uint8_t identifier_;
    const size_t length_;
    std::vector<T> data_;

    static std::map<uint8_t, DataManager<T>*>& getInstances() {
        static std::map<uint8_t, DataManager<T>*> instances;
        return instances;
    }

    static DataManager<T>* search(uint8_t identifier) {
        auto& inst = getInstances();
        auto it = inst.find(identifier);
        if (it == inst.end()) {
            throw std::runtime_error("No instance found for identifier");
        }
        return it->second;
    }
};

} // namespace Quadken

#endif // QUADKEN_DATA_MANAGER_H
