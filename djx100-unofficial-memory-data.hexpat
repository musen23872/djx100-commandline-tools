#pragma endian little

enum Mode : u8 {
    FM = 0x00,
    NFM = 0x01,
    AM = 0x02,
    NAM = 0x03,
    T98 = 0x04,
    T102_B54 = 0x05,
    DMR = 0x06,
    T61_typ1 = 0x07,
    T61_typ2 = 0x08,
    T61_typ3 = 0x09,
    T61_typ4 = 0x0A,
    ULT_xxx_xxxx = 0x0B,
    ULT_Ixxx = 0x0C,
    dPMR = 0x0D,
    DSTAR = 0x0E,
    C4FM = 0x0F,
    AIS = 0x10,
    ACARS = 0x11,
    POCSAG = 0x12,
    _12KIF_W = 0x13,
    _12kIF_N = 0x14
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

enum AMFM_SCRAMBLE_FREQ : u8 {
    _2500Hz,
    _2600Hz,
    _2700Hz,
    _2800Hz,
    _2900Hz,
    _3000Hz,
    _3100Hz,
    _3200Hz,
    _3300Hz,
    _3400Hz,
    _3500Hz
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

struct Section {
    u32 start_address;
    u32 size;
    u32 reserved1;
    u32 reserved2;
};

struct Header {
    u32  magic;
    u8   version;
    u32  data_size;
    char comment[64];
    char reserved1[39];
    Section section[8];
    char reserved2[12];
    u32  crc;
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
    bool amfm_scramble_enable;
    AMFM_SCRAMBLE_FREQ amfm_scramble_freq;
    U16_auto t98_wc;
    u16 unknown_1;
    U16_auto t102_wc;
    u16 t61_typ1_WC;
    u16 t61_typ2_WC;
    u16 t61_typ3_WC;
    u16 t61_typ4_WC;
    u16 t61_typX_WC;
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
    u8 t61_longitude;
    u8 t61_latitude;
    u8 unknown_2;
};

Header header @ 0x0000;
Data data[1000] @ 0x0100;
