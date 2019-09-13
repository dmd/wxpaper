#include "epd.h"

void setup(void)
{
    epd_init();
    epd_wakeup();
    epd_set_memory(MEM_TF);
    epd_set_color(BLACK, WHITE);
    epd_set_en_font(ASCII32);
    epd_clear();
    epd_disp_string("waiting for update...", 300, 300);
    epd_update();
    Time.zone(-4);
    Particle.function("clear", clear);
    Particle.function("img", img);
    Particle.function("text", text);
    Particle.function("update", update);
}

int clear(String x)
{
    epd_clear();
}

int img(String imginfo)
{
    int x, y;
    String img;

    int c1 = imginfo.indexOf('|');
    int c2 = imginfo.indexOf('|', c1 + 1);
    img = imginfo.substring(0, c1);
    x = imginfo.substring(c1 + 1, c2).toInt();
    y = imginfo.substring(c2 + 1).toInt();
    epd_disp_bitmap(img.c_str(), x, y);
}

int text(String textinfo)
{
    int x, y;
    String text;

    int c1 = textinfo.indexOf('|');
    int c2 = textinfo.indexOf('|', c1 + 1);
    text = textinfo.substring(0, c1);
    x = textinfo.substring(c1 + 1, c2).toInt();
    y = textinfo.substring(c2 + 1).toInt();
    epd_disp_string(text, x, y);
}

int update(String x)
{
    epd_update();
}

void loop()
{
    delay(10000);
}
