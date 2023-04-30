#pragma endian little

enum Mode : u8 {
    FM = 0x00,
    NFM = 0x01,
    AM = 0x02,
    NAM = 0x03,
    T98 = 0x04,
    T102_B54 = 0x05,
    DMR = 0x06,
    HOGEHOHE = 0x0C,
    DSTAR = 0x0D,
    C4FM = 0x0E,
    AIS = 0x0F,
    ACARS = 0x10,
    _12KIF_W = 0x12,
    _12kIF_N = 0x13
};

enum Step : u8 {
    _1k,
    _5k,
    _6k25,
    _8k33,
    _10k,
    _12k5,
    _15k,
    _20k,
    _25k,
    _30k,
    _50k,
    _100k,
    _125k,
    _200k
};

enum Att : u8 {
    OFF,
    _10db,
    _20db
};

enum Sq : u8 {
    OFF,
    CTCSS,
    DCS,
    REVERSE_CTCSS,
    REVERSE_DCS,
    JR,
    MSK
};

enum Tone : u8 {
    _670,
    _693,
    _719,
    _744,
    _770,
    _797,
    _825,
    _854,
    _885,
    _915,
    _948,
    _974,
    _1000,
    _1035,
    _1072,
    _1109,
    _1148,
    _1188,
    _1230,
    _1273,
    _1318,
    _1355,
    _1413,
    _1462,
    _1415,
    _1567,
    _1598,
    _1622,
    _1655,
    _1679,
    _1713,
    _1738,
    _1773,
    _1799,
    _1835,
    _1862,
    _1899,
    _1928,
    _1966,
    _1995,
    _2035,
    _2065,
    _2107,
    _2181,
    _2257,
    _2291,
    _2336,
    _2418,
    _2503,
    _2541
};

enum Dmr_slot : u8 {
    AUTO,
    _1,
    _2
};

bitfield U16_auto {
    value : 15;
    auto_scan : 1;
};

bitfield U16_enable {
    value : 15;
    enable : 1;
};

bitfield U32_all {
    value : 31;
    all : 1;
};

struct Header {
    u32  magic;
    u8   version;
    u32  data_size;
    char comment[64];
    char reserved[183];
};

struct Data {
    u32 freq;
    Mode mode;
    Step step;
    bool offset_step;
    bool enable_location;
    u32 latitude;
    u32 longitude;
    u8 skip;
    bool bank[26];
    char name[29];
    s32 shift;
    Att att;
    Sq sq;
    Tone tone;
    u8 dcs;
    u16 unknown_1;
    U16_auto t98_wc;
    u16 unknown_2;
    U16_auto t102_wc;
    char unknown_3[10];
    U16_auto t98_uc;
    U16_auto t102_uc;
    U16_enable t98_scramble;
    U16_enable t102_scramble;
    U32_all t98_group;
    U32_all t102_group;
    U32_all dmr_group;
    Dmr_slot  dmr_slot;
    U16_enable dmr_color;
    U16_enable dstar_sq;
    U16_enable c4fm_dgid;
    char unknown_4[3];
};

Header header @ 0x0000;
Data data[1000] @ 0x0100;
