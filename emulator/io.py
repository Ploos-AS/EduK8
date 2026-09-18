"""K8 v1 memory-mapped educational peripherals."""

KEY_DATA=0xC010; KEY_STATUS=0xC011; KEY_CONTROL=0xC012; KEY_RAW=0xC013
VIDEO_CONTROL=0xC020; VIDEO_STATUS=0xC021; CURSOR_X=0xC022; CURSOR_Y=0xC023; CURSOR_CONTROL=0xC024
VRAM_START=0x7800; VRAM_VISIBLE=1000

class IO:
    def __init__(self):
        self.keyboard=[]
        self.key_control=0
        self.key_overrun=False
        self.video_control=1
        self.cursor_x=0
        self.cursor_y=0
        self.cursor_control=0

    def inject_key(self, value):
        if len(self.keyboard) >= 16:
            self.key_overrun=True
            return
        self.keyboard.append(value & 0xFF)

    def read(self, address):
        if address == KEY_DATA:
            return self.keyboard.pop(0) if self.keyboard else 0
        if address == KEY_STATUS:
            return (1 if self.keyboard else 0) | (2 if self.key_overrun else 0)
        if address == KEY_CONTROL: return self.key_control
        if address == KEY_RAW: return 0
        if address == VIDEO_CONTROL: return self.video_control
        if address == VIDEO_STATUS: return 0
        if address == CURSOR_X: return self.cursor_x
        if address == CURSOR_Y: return self.cursor_y
        if address == CURSOR_CONTROL: return self.cursor_control
        if 0xC000 <= address <= 0xC0FF: return 0
        return None

    def write(self, address, value):
        value &= 0xFF
        if address == KEY_CONTROL: self.key_control=value; return True
        if address == VIDEO_CONTROL: self.video_control=value; return True
        if address == CURSOR_X: self.cursor_x=value % 40; return True
        if address == CURSOR_Y: self.cursor_y=value % 25; return True
        if address == CURSOR_CONTROL: self.cursor_control=value; return True
        if 0xC000 <= address <= 0xC0FF: return True
        return False

    def text(self, memory):
        cells=memory[VRAM_START:VRAM_START+VRAM_VISIBLE]
        return "\n".join(bytes(cells[y*40:(y+1)*40]).decode("latin1") for y in range(25))
