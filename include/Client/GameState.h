#pragma once

#include <cstdint>

namespace client {

struct Vec2 {
    float x{0.0f};
    float y{0.0f};
};

struct CharacterState {
    std::int32_t hp{0};
    std::int32_t maxHp{0};
    std::int32_t sp{0};
    std::int32_t maxSp{0};
    Vec2 position{};
    std::int32_t level{0};
};

struct GameState {
    CharacterState character{};
    bool valid{false};
};

}
